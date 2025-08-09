# this_file: external/int_folders/d361/src/d361/utils/performance.py
"""
Performance Optimization Layer - Caching and batch processing utilities.

This module provides comprehensive performance optimization utilities including
async caching with diskcache, batch processing decorators, and performance
monitoring tools for the d361 library.
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import inspect
import json
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union
from weakref import WeakKeyDictionary

import diskcache
from loguru import logger
from pydantic import BaseModel, Field

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class CacheStrategy(str, Enum):
    """Cache eviction strategies."""
    LRU = "lru"          # Least Recently Used
    LFU = "lfu"          # Least Frequently Used  
    FIFO = "fifo"        # First In First Out
    NONE = "none"        # No eviction


class BatchStrategy(str, Enum):
    """Batch processing strategies."""
    SIZE_BASED = "size_based"      # Trigger on batch size
    TIME_BASED = "time_based"      # Trigger on time interval
    HYBRID = "hybrid"              # Both size and time triggers


@dataclass
class CacheConfig:
    """Configuration for cache behavior."""
    directory: Optional[Path] = None
    size_limit: int = 100_000_000  # 100MB default
    timeout: float = 86400.0       # 24 hours default
    eviction_policy: CacheStrategy = CacheStrategy.LRU
    statistics: bool = True
    disk_sync: bool = True
    
    def __post_init__(self):
        """Ensure directory is Path object."""
        if self.directory and not isinstance(self.directory, Path):
            self.directory = Path(self.directory)


@dataclass
class BatchConfig:
    """Configuration for batch processing."""
    max_size: int = 100
    max_wait: float = 1.0          # seconds
    strategy: BatchStrategy = BatchStrategy.HYBRID
    max_concurrency: int = 10
    timeout: float = 30.0          # seconds per batch
    retry_attempts: int = 3
    retry_delay: float = 1.0       # seconds


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""
    cache_hits: int = 0
    cache_misses: int = 0
    cache_size: int = 0
    batch_count: int = 0
    batch_total_items: int = 0
    avg_batch_size: float = 0.0
    avg_processing_time: float = 0.0
    processing_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    def add_processing_time(self, duration: float) -> None:
        """Add a processing time measurement."""
        self.processing_times.append(duration)
        self.avg_processing_time = sum(self.processing_times) / len(self.processing_times)


class AsyncCache:
    """High-performance async cache with disk persistence."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self._memory_cache: Dict[str, Any] = {}
        self._disk_cache: Optional[diskcache.Cache] = None
        self._access_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = defaultdict(int)
        
        # Initialize disk cache if directory provided
        if config.directory:
            config.directory.mkdir(parents=True, exist_ok=True)
            self._disk_cache = diskcache.Cache(
                directory=str(config.directory),
                size_limit=config.size_limit,
                eviction_policy=config.eviction_policy.value,
                disk=diskcache.JSONDisk if config.disk_sync else None,
                statistics=config.statistics,
            )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Try memory cache first
        if key in self._memory_cache:
            self._update_access_stats(key)
            self.metrics.cache_hits += 1
            return self._memory_cache[key]
        
        # Try disk cache
        if self._disk_cache and key in self._disk_cache:
            value = self._disk_cache[key]
            self._memory_cache[key] = value  # Promote to memory
            self._update_access_stats(key)
            self.metrics.cache_hits += 1
            return value
        
        self.metrics.cache_misses += 1
        return None
    
    async def set(self, key: str, value: Any, timeout: Optional[float] = None) -> None:
        """Set value in cache."""
        timeout = timeout or self.config.timeout
        
        # Store in memory cache
        self._memory_cache[key] = value
        self._update_access_stats(key)
        
        # Store in disk cache if available
        if self._disk_cache:
            self._disk_cache.set(key, value, expire=timeout)
        
        self.metrics.cache_size = len(self._memory_cache)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        deleted = False
        
        # Remove from memory cache
        if key in self._memory_cache:
            del self._memory_cache[key]
            deleted = True
        
        # Remove from disk cache
        if self._disk_cache and key in self._disk_cache:
            del self._disk_cache[key]
            deleted = True
        
        # Clean up access stats
        self._access_times.pop(key, None)
        self._access_counts.pop(key, None)
        
        self.metrics.cache_size = len(self._memory_cache)
        return deleted
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        self._memory_cache.clear()
        self._access_times.clear()
        self._access_counts.clear()
        
        if self._disk_cache:
            self._disk_cache.clear()
        
        self.metrics.cache_size = 0
    
    def _update_access_stats(self, key: str) -> None:
        """Update access statistics for cache key."""
        self._access_times[key] = time.time()
        self._access_counts[key] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "memory_size": len(self._memory_cache),
            "hit_rate": self.metrics.hit_rate,
            "hits": self.metrics.cache_hits,
            "misses": self.metrics.cache_misses,
        }
        
        if self._disk_cache and self.config.statistics:
            disk_stats = dict(self._disk_cache.stats())
            stats.update({"disk_" + k: v for k, v in disk_stats.items()})
        
        return stats


class BatchProcessor:
    """Async batch processor with configurable strategies."""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self._pending_items: List[Any] = []
        self._pending_futures: List[asyncio.Future] = []
        self._batch_timer: Optional[asyncio.Task] = None
        self._processing_lock = asyncio.Lock()
        self._executor = ThreadPoolExecutor(max_workers=config.max_concurrency)
        
    async def add_item(self, item: Any, processor: Callable[[List[Any]], Any]) -> Any:
        """Add item to batch for processing."""
        future = asyncio.Future()
        
        async with self._processing_lock:
            self._pending_items.append(item)
            self._pending_futures.append(future)
            
            # Check if we should trigger batch processing
            should_process = self._should_trigger_batch()
            
            if should_process:
                await self._process_batch(processor)
            elif self._batch_timer is None:
                # Start timer for time-based triggering
                self._batch_timer = asyncio.create_task(
                    self._wait_for_timeout(processor)
                )
        
        return await future
    
    def _should_trigger_batch(self) -> bool:
        """Determine if batch should be triggered."""
        if self.config.strategy == BatchStrategy.SIZE_BASED:
            return len(self._pending_items) >= self.config.max_size
        elif self.config.strategy == BatchStrategy.TIME_BASED:
            return False  # Only trigger on timeout
        else:  # HYBRID
            return len(self._pending_items) >= self.config.max_size
    
    async def _wait_for_timeout(self, processor: Callable[[List[Any]], Any]) -> None:
        """Wait for timeout and trigger batch processing."""
        try:
            await asyncio.sleep(self.config.max_wait)
            async with self._processing_lock:
                if self._pending_items:  # Still have items to process
                    await self._process_batch(processor)
        except asyncio.CancelledError:
            pass  # Timer was cancelled, batch was processed
    
    async def _process_batch(self, processor: Callable[[List[Any]], Any]) -> None:
        """Process current batch of items."""
        if not self._pending_items:
            return
        
        items = self._pending_items[:]
        futures = self._pending_futures[:]
        self._pending_items.clear()
        self._pending_futures.clear()
        
        # Cancel timer if running
        if self._batch_timer:
            self._batch_timer.cancel()
            self._batch_timer = None
        
        # Update metrics
        self.metrics.batch_count += 1
        self.metrics.batch_total_items += len(items)
        self.metrics.avg_batch_size = self.metrics.batch_total_items / self.metrics.batch_count
        
        start_time = time.time()
        
        try:
            # Process batch
            if asyncio.iscoroutinefunction(processor):
                result = await processor(items)
            else:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self._executor, processor, items)
            
            # Set results for all futures
            if isinstance(result, list) and len(result) == len(futures):
                # Individual results for each item
                for future, item_result in zip(futures, result):
                    future.set_result(item_result)
            else:
                # Same result for all items
                for future in futures:
                    future.set_result(result)
                    
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            # Set exception for all futures
            for future in futures:
                future.set_exception(e)
        
        # Update timing metrics
        duration = time.time() - start_time
        self.metrics.add_processing_time(duration)
    
    async def flush(self, processor: Callable[[List[Any]], Any]) -> None:
        """Force process any pending items."""
        async with self._processing_lock:
            if self._pending_items:
                await self._process_batch(processor)
    
    async def shutdown(self) -> None:
        """Shutdown the batch processor."""
        if self._batch_timer:
            self._batch_timer.cancel()
        
        self._executor.shutdown(wait=True)


class PerformanceOptimizer:
    """
    Main performance optimization utility class.
    
    Provides centralized access to caching, batch processing, and 
    performance monitoring capabilities.
    """
    
    def __init__(
        self,
        cache_config: Optional[CacheConfig] = None,
        batch_config: Optional[BatchConfig] = None,
    ):
        self.cache_config = cache_config or CacheConfig()
        self.batch_config = batch_config or BatchConfig()
        
        self._caches: Dict[str, AsyncCache] = {}
        self._batch_processors: WeakKeyDictionary = WeakKeyDictionary()
        self._metrics = PerformanceMetrics()
    
    def get_cache(self, name: str = "default") -> AsyncCache:
        """Get or create named cache instance."""
        if name not in self._caches:
            config = CacheConfig(
                directory=self.cache_config.directory / name if self.cache_config.directory else None,
                size_limit=self.cache_config.size_limit,
                timeout=self.cache_config.timeout,
                eviction_policy=self.cache_config.eviction_policy,
                statistics=self.cache_config.statistics,
                disk_sync=self.cache_config.disk_sync,
            )
            self._caches[name] = AsyncCache(config)
        
        return self._caches[name]
    
    def get_batch_processor(self, func: Callable) -> BatchProcessor:
        """Get or create batch processor for function."""
        if func not in self._batch_processors:
            self._batch_processors[func] = BatchProcessor(self.batch_config)
        
        return self._batch_processors[func]
    
    async def clear_all_caches(self) -> None:
        """Clear all cache instances."""
        for cache in self._caches.values():
            await cache.clear()
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get combined metrics from all components."""
        metrics = {"global": self._metrics}
        
        # Add cache metrics
        for name, cache in self._caches.items():
            metrics[f"cache_{name}"] = cache.get_stats()
        
        # Add batch processor metrics
        batch_metrics = {}
        for func, processor in self._batch_processors.items():
            func_name = getattr(func, '__name__', str(func))
            batch_metrics[func_name] = {
                "batch_count": processor.metrics.batch_count,
                "total_items": processor.metrics.batch_total_items,
                "avg_batch_size": processor.metrics.avg_batch_size,
                "avg_processing_time": processor.metrics.avg_processing_time,
            }
        
        if batch_metrics:
            metrics["batch_processors"] = batch_metrics
        
        return metrics


# Global optimizer instance
_optimizer: Optional[PerformanceOptimizer] = None


def get_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = PerformanceOptimizer()
    return _optimizer


def set_optimizer(optimizer: PerformanceOptimizer) -> None:
    """Set global performance optimizer instance."""
    global _optimizer
    _optimizer = optimizer


# Decorators for performance optimization

def async_cache(
    cache_name: str = "default",
    timeout: Optional[float] = None,
    key_func: Optional[Callable[..., str]] = None,
    optimizer: Optional[PerformanceOptimizer] = None,
) -> Callable[[F], F]:
    """
    Decorator for async function caching.
    
    Args:
        cache_name: Name of cache to use
        timeout: Cache timeout in seconds
        key_func: Function to generate cache key from arguments
        optimizer: Performance optimizer instance
        
    Returns:
        Decorated function with caching
        
    Example:
        @async_cache(cache_name="api_cache", timeout=3600)
        async def fetch_data(url: str) -> dict:
            # Expensive API call
            return await http_client.get(url)
    """
    def decorator(func: F) -> F:
        target_optimizer = optimizer or get_optimizer()
        cache = target_optimizer.get_cache(cache_name)
        
        def default_key_func(*args, **kwargs) -> str:
            """Default key generation from function arguments."""
            # Create a stable key from function name and arguments
            func_name = f"{func.__module__}.{func.__qualname__}"
            args_str = json.dumps([str(arg) for arg in args], sort_keys=True)
            kwargs_str = json.dumps({k: str(v) for k, v in kwargs.items()}, sort_keys=True)
            key_data = f"{func_name}:{args_str}:{kwargs_str}"
            return hashlib.md5(key_data.encode()).hexdigest()
        
        key_generator = key_func or default_key_func
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = key_generator(*args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}", key=cache_key)
                return cached_result
            
            # Call original function
            logger.debug(f"Cache miss for {func.__name__}", key=cache_key)
            result = await func(*args, **kwargs)
            
            # Store result in cache
            await cache.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    
    return decorator


def batch_processor(
    max_size: int = 100,
    max_wait: float = 1.0,
    strategy: BatchStrategy = BatchStrategy.HYBRID,
    optimizer: Optional[PerformanceOptimizer] = None,
) -> Callable[[F], F]:
    """
    Decorator for batch processing of function calls.
    
    Args:
        max_size: Maximum batch size before triggering processing
        max_wait: Maximum wait time in seconds before triggering
        strategy: Batch processing strategy
        optimizer: Performance optimizer instance
        
    Returns:
        Decorated function with batch processing
        
    Example:
        @batch_processor(max_size=50, max_wait=2.0)
        async def process_items(items: List[str]) -> List[str]:
            # Process batch of items together
            return [item.upper() for item in items]
    """
    def decorator(func: F) -> F:
        target_optimizer = optimizer or get_optimizer()
        
        # Update batch config for this decorator
        config = BatchConfig(
            max_size=max_size,
            max_wait=max_wait,
            strategy=strategy,
            max_concurrency=target_optimizer.batch_config.max_concurrency,
            timeout=target_optimizer.batch_config.timeout,
            retry_attempts=target_optimizer.batch_config.retry_attempts,
            retry_delay=target_optimizer.batch_config.retry_delay,
        )
        
        processor = BatchProcessor(config)
        
        @functools.wraps(func)
        async def wrapper(item):
            # Add single item to batch processor
            return await processor.add_item(item, func)
        
        # Add flush method to wrapper
        wrapper.flush = lambda: processor.flush(func)  # type: ignore
        wrapper.shutdown = processor.shutdown  # type: ignore
        
        return wrapper
    
    return decorator


def performance_monitor(
    track_timing: bool = True,
    track_memory: bool = False,
    log_slow_calls: bool = True,
    slow_threshold: float = 1.0,
) -> Callable[[F], F]:
    """
    Decorator for monitoring function performance.
    
    Args:
        track_timing: Track execution time
        track_memory: Track memory usage (requires psutil)
        log_slow_calls: Log calls that exceed slow_threshold
        slow_threshold: Threshold in seconds for slow call logging
        
    Returns:
        Decorated function with performance monitoring
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = None
            
            if track_memory:
                try:
                    import psutil
                    process = psutil.Process()
                    start_memory = process.memory_info().rss
                except ImportError:
                    logger.warning("psutil not available for memory tracking")
            
            try:
                result = await func(*args, **kwargs)
                
                # Track metrics
                duration = time.time() - start_time
                
                if track_timing:
                    optimizer = get_optimizer()
                    optimizer._metrics.add_processing_time(duration)
                
                if log_slow_calls and duration > slow_threshold:
                    logger.warning(
                        f"Slow function call detected",
                        function=func.__name__,
                        duration=duration,
                        threshold=slow_threshold,
                    )
                
                if track_memory and start_memory:
                    try:
                        import psutil
                        process = psutil.Process()
                        end_memory = process.memory_info().rss
                        memory_delta = end_memory - start_memory
                        
                        logger.debug(
                            f"Function memory usage",
                            function=func.__name__,
                            memory_delta_mb=memory_delta / 1024 / 1024,
                            duration=duration,
                        )
                    except ImportError:
                        pass
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function failed after {duration:.3f}s",
                    function=func.__name__,
                    error=str(e),
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if log_slow_calls and duration > slow_threshold:
                    logger.warning(
                        f"Slow function call detected",
                        function=func.__name__,
                        duration=duration,
                        threshold=slow_threshold,
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function failed after {duration:.3f}s",
                    function=func.__name__,
                    error=str(e),
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator