# this_file: external/int_folders/d361/src/d361/archive/cache.py
"""
SQLite-based caching system for Document360 archives.

This module provides enterprise-grade SQLite caching with performance
optimizations including WAL mode, prepared statements, connection pooling,
and intelligent cache eviction policies.
"""

from __future__ import annotations

import asyncio
import sqlite3
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from dataclasses import dataclass
from enum import Enum
from queue import Queue

from loguru import logger
from pydantic import BaseModel, Field

from .schema import create_archive_schema, ArchiveSchema
from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class EvictionPolicy(str, Enum):
    """Cache eviction policies."""
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    FIFO = "fifo"         # First In, First Out
    TTL_BASED = "ttl"     # Time To Live based
    SIZE_BASED = "size"   # Size-based eviction


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    @property
    def miss_rate(self) -> float:
        """Calculate cache miss rate."""
        return 1.0 - self.hit_rate


class CacheEntry(BaseModel):
    """Cache entry with metadata."""
    
    key: str = Field(..., description="Cache key")
    value: Any = Field(..., description="Cached value")
    size: int = Field(..., description="Entry size in bytes")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation time")
    accessed_at: datetime = Field(default_factory=datetime.now, description="Last access time")
    access_count: int = Field(default=0, description="Number of accesses")
    ttl_seconds: Optional[int] = Field(None, description="Time to live in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl_seconds is None:
            return False
        
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Get entry age in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


class CacheConfig(BaseModel):
    """Configuration for SQLite cache."""
    
    # Database settings
    db_path: Path = Field(
        default_factory=lambda: Path.home() / ".d361" / "cache" / "archive_cache.db",
        description="Path to SQLite cache database"
    )
    
    schema_config: ArchiveSchema = Field(
        default_factory=ArchiveSchema,
        description="Database schema configuration"
    )
    
    # Connection pooling
    max_connections: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of database connections"
    )
    
    connection_timeout: float = Field(
        default=30.0,
        ge=1.0,
        description="Connection timeout in seconds"
    )
    
    # Cache policies
    max_size_mb: int = Field(
        default=500,
        ge=1,
        description="Maximum cache size in megabytes"
    )
    
    max_entries: int = Field(
        default=10000,
        ge=1,
        description="Maximum number of cache entries"
    )
    
    default_ttl_seconds: int = Field(
        default=3600,  # 1 hour
        ge=60,
        description="Default TTL for cache entries"
    )
    
    eviction_policy: EvictionPolicy = Field(
        default=EvictionPolicy.LRU,
        description="Cache eviction policy"
    )
    
    # Maintenance
    cleanup_interval_seconds: int = Field(
        default=300,  # 5 minutes
        ge=60,
        description="Cleanup interval in seconds"
    )
    
    enable_compression: bool = Field(
        default=True,
        description="Enable data compression"
    )
    
    enable_background_cleanup: bool = Field(
        default=True,
        description="Enable background cleanup task"
    )


class ConnectionPool:
    """SQLite connection pool for concurrent access."""
    
    def __init__(self, db_path: Path, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._pool: Queue = Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._created_connections = 0
        
        logger.debug(f"ConnectionPool initialized with {max_connections} max connections")
    
    def get_connection(self, timeout: float = 30.0) -> sqlite3.Connection:
        """Get a connection from the pool."""
        try:
            # Try to get existing connection
            conn = self._pool.get(timeout=timeout)
            return conn
        except:
            # Create new connection if pool is empty and under limit
            with self._lock:
                if self._created_connections < self.max_connections:
                    conn = self._create_connection()
                    self._created_connections += 1
                    return conn
            
            # Pool is full, wait for available connection
            return self._pool.get(timeout=timeout)
    
    def return_connection(self, conn: sqlite3.Connection) -> None:
        """Return a connection to the pool."""
        try:
            self._pool.put(conn, block=False)
        except:
            # Pool is full, close the connection
            conn.close()
            with self._lock:
                self._created_connections -= 1
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0
        )
        
        # Configure connection
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA cache_size = 10000")
        
        return conn
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get(block=False)
                conn.close()
            except:
                break
        
        with self._lock:
            self._created_connections = 0


class SqliteCache:
    """
    Enterprise-grade SQLite cache implementation.
    
    Provides high-performance caching with WAL mode, prepared statements,
    connection pooling, and configurable eviction policies.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize SQLite cache.
        
        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self.connection_pool = ConnectionPool(
            self.config.db_path,
            self.config.max_connections
        )
        self.stats = CacheStats()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info(
            f"SqliteCache initialized",
            db_path=str(self.config.db_path),
            max_size=f"{self.config.max_size_mb}MB",
            eviction_policy=self.config.eviction_policy
        )
    
    async def start(self) -> None:
        """Start the cache and initialize database."""
        if self._running:
            return
        
        logger.info("Starting SqliteCache")
        
        # Create database schema if needed
        await self._ensure_cache_schema()
        
        # Start background cleanup if enabled
        if self.config.enable_background_cleanup:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
        
        self._running = True
        logger.info("SqliteCache started successfully")
    
    async def stop(self) -> None:
        """Stop the cache and cleanup resources."""
        if not self._running:
            return
        
        logger.info("Stopping SqliteCache")
        
        self._running = False
        
        # Stop background cleanup
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close connection pool
        self.connection_pool.close_all()
        
        logger.info("SqliteCache stopped")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        try:
            conn = self.connection_pool.get_connection(self.config.connection_timeout)
            cursor = conn.cursor()
            
            try:
                # Get cache entry
                cursor.execute("""
                    SELECT value, created_at, ttl_seconds, access_count
                    FROM cache_entries
                    WHERE key = ? AND (ttl_seconds IS NULL OR 
                                     (julianday('now') - julianday(created_at)) * 86400 <= ttl_seconds)
                """, (key,))
                
                result = cursor.fetchone()
                
                if result is None:
                    self.stats.misses += 1
                    return None
                
                # Update access statistics
                cursor.execute("""
                    UPDATE cache_entries
                    SET accessed_at = CURRENT_TIMESTAMP, access_count = access_count + 1
                    WHERE key = ?
                """, (key,))
                
                conn.commit()
                
                self.stats.hits += 1
                
                # Deserialize value
                return self._deserialize_value(result[0])
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to get cache entry '{key}': {e}")
            self.stats.misses += 1
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            # Use default TTL if not specified
            if ttl_seconds is None:
                ttl_seconds = self.config.default_ttl_seconds
            
            # Serialize value and calculate size
            serialized_value = self._serialize_value(value)
            value_size = len(serialized_value) if isinstance(serialized_value, (str, bytes)) else 0
            
            conn = self.connection_pool.get_connection(self.config.connection_timeout)
            cursor = conn.cursor()
            
            try:
                # Check if we need to evict entries
                await self._ensure_cache_capacity(cursor, value_size)
                
                # Insert or update cache entry
                cursor.execute("""
                    INSERT OR REPLACE INTO cache_entries
                    (key, value, size, ttl_seconds, created_at, accessed_at, access_count)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                """, (key, serialized_value, value_size, ttl_seconds))
                
                conn.commit()
                
                # Update stats
                self.stats.entry_count += 1
                self.stats.total_size += value_size
                
                return True
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to set cache entry '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was deleted
        """
        try:
            conn = self.connection_pool.get_connection(self.config.connection_timeout)
            cursor = conn.cursor()
            
            try:
                # Get entry size before deletion
                cursor.execute("SELECT size FROM cache_entries WHERE key = ?", (key,))
                result = cursor.fetchone()
                
                if result is None:
                    return False
                
                entry_size = result[0]
                
                # Delete entry
                cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
                
                # Update stats
                if cursor.rowcount > 0:
                    self.stats.entry_count -= 1
                    self.stats.total_size -= entry_size
                    return True
                
                return False
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to delete cache entry '{key}': {e}")
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        try:
            conn = self.connection_pool.get_connection(self.config.connection_timeout)
            cursor = conn.cursor()
            
            try:
                cursor.execute("DELETE FROM cache_entries")
                conn.commit()
                
                # Reset stats
                self.stats = CacheStats()
                
                logger.info("Cache cleared successfully")
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    async def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            Number of entries cleaned up
        """
        try:
            conn = self.connection_pool.get_connection(self.config.connection_timeout)
            cursor = conn.cursor()
            
            try:
                # Delete expired entries
                cursor.execute("""
                    DELETE FROM cache_entries
                    WHERE ttl_seconds IS NOT NULL 
                    AND (julianday('now') - julianday(created_at)) * 86400 > ttl_seconds
                """)
                
                cleaned_count = cursor.rowcount
                conn.commit()
                
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} expired cache entries")
                    self.stats.evictions += cleaned_count
                
                # Update stats
                await self._update_stats(cursor)
                
                return cleaned_count
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired entries: {e}")
            return 0
    
    async def get_stats(self) -> CacheStats:
        """Get current cache statistics."""
        try:
            conn = self.connection_pool.get_connection(self.config.connection_timeout)
            cursor = conn.cursor()
            
            try:
                await self._update_stats(cursor)
                return self.stats
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return self.stats
    
    async def _ensure_cache_schema(self) -> None:
        """Ensure cache database schema exists."""
        try:
            # Create directory if needed
            self.config.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = self.connection_pool.get_connection()
            cursor = conn.cursor()
            
            try:
                # Create cache entries table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key TEXT PRIMARY KEY,
                        value BLOB NOT NULL,
                        size INTEGER NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        ttl_seconds INTEGER,
                        access_count INTEGER DEFAULT 0,
                        metadata TEXT
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_accessed_at ON cache_entries (accessed_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_access_count ON cache_entries (access_count)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_created_at ON cache_entries (created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_ttl ON cache_entries (ttl_seconds)")
                
                conn.commit()
                
            finally:
                self.connection_pool.return_connection(conn)
                
        except Exception as e:
            error_msg = f"Failed to create cache schema: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH
            )
    
    async def _ensure_cache_capacity(self, cursor: sqlite3.Cursor, new_entry_size: int) -> None:
        """Ensure cache has capacity for new entry."""
        # Check current stats
        await self._update_stats(cursor)
        
        # Check if eviction is needed
        needs_eviction = (
            self.stats.total_size + new_entry_size > self.config.max_size_mb * 1024 * 1024 or
            self.stats.entry_count >= self.config.max_entries
        )
        
        if not needs_eviction:
            return
        
        # Perform eviction based on policy
        evicted_count = await self._evict_entries(cursor)
        self.stats.evictions += evicted_count
    
    async def _evict_entries(self, cursor: sqlite3.Cursor) -> int:
        """Evict entries based on configured policy."""
        # Calculate how many entries to evict (10% of max entries)
        entries_to_evict = max(1, self.config.max_entries // 10)
        
        if self.config.eviction_policy == EvictionPolicy.LRU:
            # Least Recently Used
            cursor.execute("""
                DELETE FROM cache_entries
                WHERE key IN (
                    SELECT key FROM cache_entries
                    ORDER BY accessed_at ASC
                    LIMIT ?
                )
            """, (entries_to_evict,))
            
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            # Least Frequently Used
            cursor.execute("""
                DELETE FROM cache_entries
                WHERE key IN (
                    SELECT key FROM cache_entries
                    ORDER BY access_count ASC, accessed_at ASC
                    LIMIT ?
                )
            """, (entries_to_evict,))
            
        elif self.config.eviction_policy == EvictionPolicy.FIFO:
            # First In, First Out
            cursor.execute("""
                DELETE FROM cache_entries
                WHERE key IN (
                    SELECT key FROM cache_entries
                    ORDER BY created_at ASC
                    LIMIT ?
                )
            """, (entries_to_evict,))
            
        elif self.config.eviction_policy == EvictionPolicy.SIZE_BASED:
            # Largest entries first
            cursor.execute("""
                DELETE FROM cache_entries
                WHERE key IN (
                    SELECT key FROM cache_entries
                    ORDER BY size DESC
                    LIMIT ?
                )
            """, (entries_to_evict,))
        
        return cursor.rowcount
    
    async def _update_stats(self, cursor: sqlite3.Cursor) -> None:
        """Update cache statistics from database."""
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(size), 0)
            FROM cache_entries
        """)
        
        result = cursor.fetchone()
        if result:
            self.stats.entry_count = result[0]
            self.stats.total_size = result[1]
    
    def _serialize_value(self, value: Any) -> Union[str, bytes]:
        """Serialize value for storage."""
        if self.config.enable_compression:
            import pickle
            import gzip
            pickled = pickle.dumps(value)
            return gzip.compress(pickled)
        else:
            import pickle
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: Union[str, bytes]) -> Any:
        """Deserialize value from storage."""
        if self.config.enable_compression:
            import pickle
            import gzip
            decompressed = gzip.decompress(data)
            return pickle.loads(decompressed)
        else:
            import pickle
            return pickle.loads(data)
    
    async def _background_cleanup(self) -> None:
        """Background task for periodic cleanup."""
        logger.info("Started background cache cleanup task")
        
        while self._running:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                
                if self._running:
                    await self.cleanup_expired()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background cleanup: {e}")
        
        logger.info("Background cache cleanup task stopped")


# Convenience functions for easy cache usage

_default_cache: Optional[SqliteCache] = None


async def get_default_cache() -> SqliteCache:
    """Get the default cache instance."""
    global _default_cache
    
    if _default_cache is None:
        _default_cache = SqliteCache()
        await _default_cache.start()
    
    return _default_cache


async def cache_get(key: str) -> Optional[Any]:
    """Get value from default cache."""
    cache = await get_default_cache()
    return await cache.get(key)


async def cache_set(key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
    """Set value in default cache."""
    cache = await get_default_cache()
    return await cache.set(key, value, ttl_seconds)


async def cache_delete(key: str) -> bool:
    """Delete value from default cache."""
    cache = await get_default_cache()
    return await cache.delete(key)