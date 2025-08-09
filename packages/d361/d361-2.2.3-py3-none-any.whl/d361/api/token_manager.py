# this_file: external/int_folders/d361/src/d361/api/token_manager.py
"""
Token Management System for Document360 API.

This module provides comprehensive token management including usage tracking,
rate limiting (60 calls/minute per token), intelligent rotation, and health
monitoring for multiple API tokens.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field


class TokenHealth(str, Enum):
    """Token health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class TokenStats:
    """
    Statistics and tracking for a single API token.
    
    Tracks usage, rate limits, health status, and performance metrics
    for intelligent token rotation and management.
    """
    
    token: str
    calls_made: int = 0
    calls_remaining: int = 60  # Document360 default: 60 calls/minute
    reset_time: Optional[datetime] = None
    health: TokenHealth = TokenHealth.HEALTHY
    last_used: Optional[datetime] = None
    total_calls: int = 0
    error_count: int = 0
    consecutive_errors: int = 0
    avg_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize tracking fields."""
        if self.last_used is None:
            self.last_used = datetime.now()
        if self.reset_time is None:
            self.reset_time = datetime.now() + timedelta(minutes=1)
    
    def record_call(self, response_time: float, success: bool = True) -> None:
        """
        Record a successful API call.
        
        Args:
            response_time: Response time in seconds
            success: Whether the call was successful
        """
        self.calls_made += 1
        self.total_calls += 1
        self.last_used = datetime.now()
        
        # Update response time tracking
        self.response_times.append(response_time)
        if len(self.response_times) > 100:  # Keep last 100 response times
            self.response_times.pop(0)
        self.avg_response_time = sum(self.response_times) / len(self.response_times)
        
        if success:
            self.consecutive_errors = 0
            if self.health == TokenHealth.ERROR and self.error_count > 0:
                self.health = TokenHealth.HEALTHY
        else:
            self.error_count += 1
            self.consecutive_errors += 1
            
            # Mark as degraded/error based on consecutive errors
            if self.consecutive_errors >= 5:
                self.health = TokenHealth.ERROR
            elif self.consecutive_errors >= 3:
                self.health = TokenHealth.DEGRADED
        
        # Update calls remaining (decremented by API responses)
        if self.calls_remaining > 0:
            self.calls_remaining -= 1
        
        logger.debug(
            "Token call recorded",
            token_hash=self.token_hash,
            calls_made=self.calls_made,
            calls_remaining=self.calls_remaining,
            health=self.health.value,
            response_time=response_time,
            success=success,
        )
    
    def update_rate_limit(self, calls_remaining: int, reset_time: Optional[datetime] = None) -> None:
        """
        Update rate limit information from API response headers.
        
        Args:
            calls_remaining: Number of calls remaining in current window
            reset_time: When the rate limit window resets
        """
        self.calls_remaining = calls_remaining
        if reset_time:
            self.reset_time = reset_time
        
        # Update health based on rate limit status
        if calls_remaining <= 0:
            self.health = TokenHealth.RATE_LIMITED
        elif calls_remaining <= 5:  # Low remaining calls
            self.health = TokenHealth.DEGRADED
        elif self.health == TokenHealth.RATE_LIMITED and calls_remaining > 10:
            self.health = TokenHealth.HEALTHY
    
    def is_rate_limited(self) -> bool:
        """Check if token is currently rate limited."""
        if self.calls_remaining <= 0:
            return True
        
        # Check if reset time has passed
        if self.reset_time and datetime.now() > self.reset_time:
            # Reset window has passed, reset counters
            self.calls_made = 0
            self.calls_remaining = 60
            self.reset_time = datetime.now() + timedelta(minutes=1)
            if self.health == TokenHealth.RATE_LIMITED:
                self.health = TokenHealth.HEALTHY
            return False
            
        return self.health == TokenHealth.RATE_LIMITED
    
    def can_make_call(self) -> bool:
        """Check if token can make another API call."""
        return (
            self.health not in [TokenHealth.EXPIRED, TokenHealth.ERROR] and
            not self.is_rate_limited()
        )
    
    @property
    def token_hash(self) -> str:
        """Get a hash of the token for safe logging."""
        return f"***{self.token[-4:] if len(self.token) > 4 else '****'}"
    
    @property
    def utilization_rate(self) -> float:
        """Calculate token utilization rate (0-1)."""
        if self.calls_remaining + self.calls_made == 0:
            return 0.0
        return self.calls_made / (self.calls_remaining + self.calls_made)
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate (0-1)."""
        return self.error_count / max(self.total_calls, 1)
    
    def to_dict(self) -> Dict[str, any]:
        """Convert stats to dictionary for monitoring/logging."""
        return {
            "token_hash": self.token_hash,
            "calls_made": self.calls_made,
            "calls_remaining": self.calls_remaining,
            "health": self.health.value,
            "total_calls": self.total_calls,
            "error_count": self.error_count,
            "consecutive_errors": self.consecutive_errors,
            "utilization_rate": self.utilization_rate,
            "error_rate": self.error_rate,
            "avg_response_time": self.avg_response_time,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "reset_time": self.reset_time.isoformat() if self.reset_time else None,
        }


class RateLimiter:
    """
    Rate limiter for Document360 API (60 calls/minute per token).
    
    Provides proactive rate limiting with sliding window tracking,
    backoff strategies, and intelligent call distribution.
    """
    
    def __init__(self, calls_per_minute: int = 60, safety_margin: int = 5):
        """
        Initialize rate limiter.
        
        Args:
            calls_per_minute: API rate limit (default 60 for Document360)
            safety_margin: Safety margin to leave for other operations
        """
        self.calls_per_minute = calls_per_minute
        self.safety_margin = safety_margin
        self.effective_limit = calls_per_minute - safety_margin
        self.call_timestamps: List[datetime] = []
    
    async def wait_if_needed(self) -> float:
        """
        Wait if necessary to respect rate limits.
        
        Returns:
            Number of seconds waited (0 if no wait needed)
        """
        now = datetime.now()
        
        # Remove calls older than 1 minute
        cutoff = now - timedelta(minutes=1)
        self.call_timestamps = [ts for ts in self.call_timestamps if ts > cutoff]
        
        # Check if we've exceeded our effective limit
        if len(self.call_timestamps) >= self.effective_limit:
            # Calculate wait time until oldest call is 1 minute old
            oldest_call = min(self.call_timestamps)
            wait_until = oldest_call + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            
            if wait_seconds > 0:
                logger.info(
                    f"Rate limit approaching, waiting {wait_seconds:.2f}s",
                    calls_made=len(self.call_timestamps),
                    effective_limit=self.effective_limit,
                )
                await asyncio.sleep(wait_seconds)
                return wait_seconds
        
        return 0.0
    
    def record_call(self) -> None:
        """Record that a call was made."""
        self.call_timestamps.append(datetime.now())
        
        # Keep only last minute of calls for efficiency
        if len(self.call_timestamps) > self.calls_per_minute * 2:
            cutoff = datetime.now() - timedelta(minutes=1)
            self.call_timestamps = [ts for ts in self.call_timestamps if ts > cutoff]
    
    def calls_available(self) -> int:
        """Get number of calls available in current window."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        recent_calls = [ts for ts in self.call_timestamps if ts > cutoff]
        return max(0, self.effective_limit - len(recent_calls))
    
    def time_until_reset(self) -> float:
        """Get seconds until rate limit window resets."""
        if not self.call_timestamps:
            return 0.0
        
        now = datetime.now()
        oldest_call = min(self.call_timestamps)
        reset_time = oldest_call + timedelta(minutes=1)
        return max(0.0, (reset_time - now).total_seconds())


class TokenManager:
    """
    Intelligent API token pool manager with rotation and health monitoring.
    
    Manages multiple API tokens with intelligent rotation based on:
    - Rate limit status and utilization
    - Token health and error rates
    - Response time performance
    - Load balancing across tokens
    
    Enhanced with patterns from legacy vexy360 utilities for environment
    variable loading, request statistics, and concurrency control.
    """
    
    def __init__(self, tokens: List[str], calls_per_minute: int = 60):
        """
        Initialize token manager.
        
        Args:
            tokens: List of API tokens to manage
            calls_per_minute: Rate limit per token (default 60)
        """
        if not tokens:
            raise ValueError("At least one API token must be provided")
        
        self.tokens = {token: TokenStats(token) for token in tokens}
        self.rate_limiters = {token: RateLimiter(calls_per_minute) for token in tokens}
        self.calls_per_minute = calls_per_minute
        self._round_robin_index = 0
        
        # Enhanced statistics tracking (from vexy360_02.py patterns)
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._start_time = time.time()
        
        logger.info(
            f"TokenManager initialized with {len(tokens)} tokens",
            token_hashes=[stats.token_hash for stats in self.tokens.values()],
        )
    
    @classmethod
    def from_environment(
        cls,
        prefix: str = "DOCUMENT360_API_TOKEN",
        max_tokens: int = 10,
        calls_per_minute: int = 60
    ) -> 'TokenManager':
        """
        Create TokenManager by loading tokens from environment variables.
        
        Loads tokens from environment variables with pattern:
        DOCUMENT360_API_TOKEN_01, DOCUMENT360_API_TOKEN_02, etc.
        
        This pattern is extracted from vexy360_01.py and vexy360_02.py
        which demonstrated excellent multi-token environment loading.
        
        Args:
            prefix: Environment variable prefix
            max_tokens: Maximum number of tokens to look for
            calls_per_minute: Rate limit per token
            
        Returns:
            TokenManager instance with loaded tokens
            
        Raises:
            ValueError: If no tokens found in environment
        """
        import os
        
        tokens = []
        for i in range(1, max_tokens + 1):
            env_var = f"{prefix}_{i:02d}"
            token = os.getenv(env_var)
            if token and token.strip():
                tokens.append(token.strip())
                logger.debug(f"Loaded token from {env_var}")
        
        if not tokens:
            raise ValueError(
                f"No API tokens found in environment variables {prefix}_01 through {prefix}_{max_tokens:02d}"
            )
        
        logger.info(f"Loaded {len(tokens)} tokens from environment variables")
        return cls(tokens, calls_per_minute)
    
    async def get_best_token(self) -> Optional[str]:
        """
        Get the best available token for making an API call.
        
        Selection criteria (in order):
        1. Healthy tokens that can make calls
        2. Lowest utilization rate
        3. Best response time performance
        4. Round-robin for load balancing
        
        Returns:
            Best available token, or None if all tokens are rate limited/unhealthy
        """
        available_tokens = [
            token for token, stats in self.tokens.items()
            if stats.can_make_call()
        ]
        
        if not available_tokens:
            logger.warning("No tokens available for API calls")
            return None
        
        # Sort by selection criteria
        def token_score(token: str) -> tuple:
            stats = self.tokens[token]
            return (
                # Primary: Health status (lower is better)
                0 if stats.health == TokenHealth.HEALTHY else
                1 if stats.health == TokenHealth.DEGRADED else 2,
                
                # Secondary: Utilization rate (lower is better)
                stats.utilization_rate,
                
                # Tertiary: Error rate (lower is better)  
                stats.error_rate,
                
                # Quaternary: Response time (lower is better)
                stats.avg_response_time,
            )
        
        # Get best token
        best_token = min(available_tokens, key=token_score)
        
        logger.debug(
            "Selected token for API call",
            token_hash=self.tokens[best_token].token_hash,
            health=self.tokens[best_token].health.value,
            utilization=self.tokens[best_token].utilization_rate,
            calls_remaining=self.tokens[best_token].calls_remaining,
        )
        
        return best_token
    
    async def execute_with_token(self, operation: callable, max_retries: int = 3) -> any:
        """
        Execute an operation with automatic token selection and retry logic.
        
        Enhanced with request statistics tracking from vexy360 utilities.
        
        Args:
            operation: Async callable that takes a token parameter
            max_retries: Maximum number of retries across different tokens
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        self._total_requests += 1
        
        for attempt in range(max_retries):
            token = await self.get_best_token()
            if not token:
                # Wait for tokens to become available
                wait_time = min(self.get_min_reset_time(), 60)
                logger.info(f"All tokens exhausted, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
                continue
            
            rate_limiter = self.rate_limiters[token]
            
            try:
                # Wait for rate limiting if needed
                await rate_limiter.wait_if_needed()
                
                # Record call attempt
                rate_limiter.record_call()
                start_time = time.time()
                
                # Execute operation
                result = await operation(token)
                
                # Record successful call
                response_time = time.time() - start_time
                self.tokens[token].record_call(response_time, success=True)
                self._successful_requests += 1
                
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                self.tokens[token].record_call(response_time, success=False)
                self._failed_requests += 1
                
                logger.warning(
                    f"API call failed with token {self.tokens[token].token_hash}",
                    error=str(e),
                    attempt=attempt + 1,
                    max_retries=max_retries,
                )
                
                last_exception = e
                
                # Don't retry on certain errors
                if "401" in str(e) or "403" in str(e):
                    self.tokens[token].health = TokenHealth.EXPIRED
                    
                # Short delay before retry
                await asyncio.sleep(min(2 ** attempt, 10))
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("All API tokens are exhausted and max retries reached")
    
    def update_token_rate_limit(self, token: str, calls_remaining: int, reset_time: Optional[datetime] = None) -> None:
        """
        Update token rate limit info from API response headers.
        
        Args:
            token: Token to update
            calls_remaining: Calls remaining from API header
            reset_time: Reset time from API header
        """
        if token in self.tokens:
            self.tokens[token].update_rate_limit(calls_remaining, reset_time)
    
    def get_min_reset_time(self) -> float:
        """Get minimum time until any token's rate limit resets."""
        reset_times = []
        for token, stats in self.tokens.items():
            if stats.reset_time:
                now = datetime.now()
                reset_seconds = (stats.reset_time - now).total_seconds()
                reset_times.append(max(0, reset_seconds))
        
        return min(reset_times) if reset_times else 60.0
    
    def get_health_report(self) -> Dict[str, any]:
        """
        Get comprehensive health report for all tokens.
        
        Enhanced with additional statistics from vexy360 utility patterns.
        """
        uptime = time.time() - self._start_time
        
        report = {
            "total_tokens": len(self.tokens),
            "healthy_tokens": 0,
            "rate_limited_tokens": 0,
            "error_tokens": 0,
            "total_calls": 0,
            "total_errors": 0,
            "tokens": [],
            
            # Enhanced statistics from vexy360 patterns
            "manager_stats": {
                "uptime_seconds": uptime,
                "total_requests": self._total_requests,
                "successful_requests": self._successful_requests,
                "failed_requests": self._failed_requests,
                "success_rate": self._successful_requests / max(self._total_requests, 1),
                "requests_per_second": self._total_requests / max(uptime, 1),
            }
        }
        
        for token, stats in self.tokens.items():
            token_data = stats.to_dict()
            report["tokens"].append(token_data)
            
            # Aggregate stats
            report["total_calls"] += stats.total_calls
            report["total_errors"] += stats.error_count
            
            if stats.health == TokenHealth.HEALTHY:
                report["healthy_tokens"] += 1
            elif stats.health == TokenHealth.RATE_LIMITED:
                report["rate_limited_tokens"] += 1
            elif stats.health in [TokenHealth.ERROR, TokenHealth.EXPIRED]:
                report["error_tokens"] += 1
        
        report["overall_error_rate"] = (
            report["total_errors"] / max(report["total_calls"], 1)
        )
        
        return report
    
    def reset_token_stats(self, token: str) -> None:
        """Reset statistics for a specific token."""
        if token in self.tokens:
            self.tokens[token] = TokenStats(token)
            logger.info(f"Reset statistics for token {self.tokens[token].token_hash}")
    
    def add_token(self, token: str) -> None:
        """Add a new token to the pool."""
        if token not in self.tokens:
            self.tokens[token] = TokenStats(token)
            self.rate_limiters[token] = RateLimiter(self.calls_per_minute)
            logger.info(f"Added new token to pool: {self.tokens[token].token_hash}")
    
    def remove_token(self, token: str) -> None:
        """Remove a token from the pool."""
        if token in self.tokens:
            token_hash = self.tokens[token].token_hash
            del self.tokens[token]
            del self.rate_limiters[token]
            logger.info(f"Removed token from pool: {token_hash}")
    
    @property
    def available_tokens_count(self) -> int:
        """Get count of tokens that can currently make API calls."""
        return sum(1 for stats in self.tokens.values() if stats.can_make_call())
    
    def create_concurrency_limiter(self, max_concurrent: int = 10) -> any:
        """
        Create a semaphore for limiting concurrent API operations.
        
        This pattern is extracted from vexy360_02.py which used:
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        Args:
            max_concurrent: Maximum number of concurrent operations
            
        Returns:
            asyncio.Semaphore instance for use with context manager
        """
        return asyncio.Semaphore(max_concurrent)
    
    async def execute_batch_with_concurrency(
        self,
        operations: List[callable],
        max_concurrent: int = 10,
        max_retries: int = 3
    ) -> List[any]:
        """
        Execute multiple operations with concurrency control.
        
        This method incorporates concurrency patterns from vexy360_02.py
        which demonstrated excellent batch processing with semaphore control.
        
        Args:
            operations: List of async callables that take a token parameter
            max_concurrent: Maximum concurrent operations
            max_retries: Maximum retries per operation
            
        Returns:
            List of operation results
        """
        semaphore = self.create_concurrency_limiter(max_concurrent)
        
        async def bounded_operation(operation: callable):
            async with semaphore:
                return await self.execute_with_token(operation, max_retries)
        
        # Execute all operations with concurrency control
        results = await asyncio.gather(*[
            bounded_operation(op) for op in operations
        ], return_exceptions=True)
        
        # Log batch statistics
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = len(results) - success_count
        
        logger.info(
            f"Batch execution completed",
            total_operations=len(operations),
            successful_operations=success_count,
            failed_operations=error_count,
            max_concurrent=max_concurrent,
        )
        
        return results
    
    def reset_manager_statistics(self) -> None:
        """Reset manager-level statistics (from vexy360 patterns)."""
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._start_time = time.time()
        
        logger.info("TokenManager statistics reset")
    
    @property
    def manager_statistics(self) -> Dict[str, any]:
        """Get manager-level statistics (from vexy360 patterns)."""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self._total_requests,
            "successful_requests": self._successful_requests,
            "failed_requests": self._failed_requests,
            "success_rate": self._successful_requests / max(self._total_requests, 1),
            "requests_per_second": self._total_requests / max(uptime, 1),
        }