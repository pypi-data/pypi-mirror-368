# this_file: external/int_folders/d361/src/d361/api/circuit_breaker.py
"""
Circuit Breaker Pattern Implementation for Document360 API.

This module provides a comprehensive circuit breaker implementation to improve
API client resilience during service degradation with state management,
failure tracking, and automatic recovery.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps

from loguru import logger
from pydantic import BaseModel, Field

from .errors import Document360Error, ErrorSeverity, ErrorCategory


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests allowed
    OPEN = "open"          # Service degraded, requests blocked
    HALF_OPEN = "half_open" # Testing service recovery, limited requests allowed


@dataclass
class CircuitMetrics:
    """
    Circuit breaker metrics and statistics.
    
    Tracks failure rates, response times, and state transitions
    for monitoring and alerting.
    """
    
    # Request counts
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # State tracking
    state_changes: int = 0
    last_state_change: Optional[datetime] = None
    time_in_current_state: float = 0.0
    
    # Failure tracking
    consecutive_failures: int = 0
    failure_rate: float = 0.0
    
    # Response time tracking
    response_times: List[float] = field(default_factory=list)
    avg_response_time: float = 0.0
    slow_requests: int = 0
    
    # Recovery tracking
    recovery_attempts: int = 0
    last_recovery_attempt: Optional[datetime] = None
    
    def update_request(self, success: bool, response_time: float) -> None:
        """Update metrics with request result."""
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
            self.consecutive_failures = 0
        else:
            self.failed_requests += 1
            self.consecutive_failures += 1
        
        # Update response times (keep last 100)
        self.response_times.append(response_time)
        if len(self.response_times) > 100:
            self.response_times.pop(0)
        
        self.avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # Update failure rate
        if self.total_requests > 0:
            self.failure_rate = self.failed_requests / self.total_requests
    
    def update_state_change(self, new_state: CircuitState) -> None:
        """Update metrics for state change."""
        self.state_changes += 1
        self.last_state_change = datetime.now()
        
        logger.info(
            f"Circuit breaker state changed to {new_state.value}",
            total_requests=self.total_requests,
            failure_rate=f"{self.failure_rate:.1%}",
            consecutive_failures=self.consecutive_failures,
        )
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0-1)."""
        return self.successful_requests / max(self.total_requests, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.success_rate,
            'failure_rate': self.failure_rate,
            'consecutive_failures': self.consecutive_failures,
            'avg_response_time': self.avg_response_time,
            'state_changes': self.state_changes,
            'recovery_attempts': self.recovery_attempts,
            'last_state_change': self.last_state_change.isoformat() if self.last_state_change else None,
        }


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker behavior."""
    
    # Failure thresholds
    failure_threshold: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of consecutive failures to open circuit"
    )
    
    failure_rate_threshold: float = Field(
        default=0.5,
        ge=0.1,
        le=1.0,
        description="Failure rate threshold to open circuit (0-1)"
    )
    
    # Time windows
    recovery_timeout: float = Field(
        default=60.0,
        ge=5.0,
        le=600.0,
        description="Time to wait before attempting recovery (seconds)"
    )
    
    half_open_timeout: float = Field(
        default=30.0,
        ge=5.0,
        le=300.0,
        description="Timeout for half-open state (seconds)"
    )
    
    # Request limits
    half_open_max_calls: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum requests allowed in half-open state"
    )
    
    minimum_request_threshold: int = Field(
        default=10,
        ge=5,
        le=50,
        description="Minimum requests before circuit can open"
    )
    
    # Response time thresholds
    slow_call_duration_threshold: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Duration threshold for slow calls (seconds)"
    )
    
    slow_call_rate_threshold: float = Field(
        default=0.8,
        ge=0.1,
        le=1.0,
        description="Slow call rate threshold (0-1)"
    )
    
    # Error classification
    should_record_error: Callable[[Exception], bool] = Field(
        default=lambda e: True,
        description="Function to determine if error should be recorded"
    )
    
    class Config:
        arbitrary_types_allowed = True


class CircuitBreakerError(Document360Error):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, message: str, circuit_state: CircuitState, metrics: CircuitMetrics):
        super().__init__(
            message,
            category=ErrorCategory.SERVER_ERROR,
            severity=ErrorSeverity.HIGH,
            retryable=False,
            context={
                'circuit_state': circuit_state.value,
                'consecutive_failures': metrics.consecutive_failures,
                'failure_rate': metrics.failure_rate,
                'last_state_change': metrics.last_state_change.isoformat() if metrics.last_state_change else None,
            }
        )
        self.circuit_state = circuit_state
        self.metrics = metrics


class CircuitBreaker:
    """
    Circuit breaker implementation for API resilience.
    
    Provides automatic failure detection and recovery with:
    - State management (CLOSED, OPEN, HALF_OPEN)
    - Configurable failure thresholds and timeouts
    - Comprehensive metrics and monitoring
    - Automatic recovery testing
    - Integration with existing error handling
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Circuit breaker name for logging and metrics
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # State management
        self.state = CircuitState.CLOSED
        self.state_start_time = time.time()
        
        # Metrics
        self.metrics = CircuitMetrics()
        
        # Half-open state tracking
        self.half_open_calls = 0
        
        logger.info(
            f"CircuitBreaker '{name}' initialized",
            failure_threshold=self.config.failure_threshold,
            recovery_timeout=self.config.recovery_timeout,
        )
    
    async def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute a function call through the circuit breaker.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original function exceptions
        """
        # Check if call is allowed
        await self._check_state()
        
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN - requests blocked",
                self.state,
                self.metrics
            )
        
        # Execute the call
        start_time = time.time()
        success = False
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            success = True
            return result
            
        except Exception as e:
            # Determine if this error should be recorded
            if self.config.should_record_error(e):
                success = False
            else:
                success = True  # Don't count certain errors as failures
            raise
            
        finally:
            # Update metrics and state
            response_time = time.time() - start_time
            self.metrics.update_request(success, response_time)
            
            # Update half-open tracking
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
            
            # Check for state transitions
            await self._update_state(success)
    
    async def _check_state(self) -> None:
        """Check and potentially update circuit breaker state."""
        current_time = time.time()
        time_in_state = current_time - self.state_start_time
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time_in_state >= self.config.recovery_timeout:
                await self._transition_to_half_open()
                
        elif self.state == CircuitState.HALF_OPEN:
            # Check if half-open timeout has elapsed
            if time_in_state >= self.config.half_open_timeout:
                # If we've had some requests and they were successful, close circuit
                if self.half_open_calls > 0 and self.metrics.consecutive_failures == 0:
                    await self._transition_to_closed()
                else:
                    # Timeout reached without successful requests, go back to open
                    await self._transition_to_open()
    
    async def _update_state(self, request_success: bool) -> None:
        """Update circuit breaker state based on request result."""
        if self.state == CircuitState.CLOSED:
            # Check if we should open the circuit
            should_open = False
            
            # Check consecutive failures
            if self.metrics.consecutive_failures >= self.config.failure_threshold:
                should_open = True
                logger.warning(
                    f"Circuit breaker '{self.name}': consecutive failure threshold reached",
                    consecutive_failures=self.metrics.consecutive_failures,
                    threshold=self.config.failure_threshold,
                )
            
            # Check failure rate (only if we have minimum requests)
            elif (self.metrics.total_requests >= self.config.minimum_request_threshold and 
                  self.metrics.failure_rate >= self.config.failure_rate_threshold):
                should_open = True
                logger.warning(
                    f"Circuit breaker '{self.name}': failure rate threshold reached",
                    failure_rate=f"{self.metrics.failure_rate:.1%}",
                    threshold=f"{self.config.failure_rate_threshold:.1%}",
                )
            
            # Check slow call rate
            elif self._is_slow_call_rate_exceeded():
                should_open = True
                logger.warning(
                    f"Circuit breaker '{self.name}': slow call rate threshold reached",
                    avg_response_time=f"{self.metrics.avg_response_time:.2f}s",
                )
            
            if should_open:
                await self._transition_to_open()
                
        elif self.state == CircuitState.HALF_OPEN:
            if request_success:
                # Successful request in half-open state
                if self.half_open_calls >= self.config.half_open_max_calls:
                    # Enough successful requests, close the circuit
                    await self._transition_to_closed()
            else:
                # Failed request in half-open state, go back to open
                await self._transition_to_open()
    
    def _is_slow_call_rate_exceeded(self) -> bool:
        """Check if slow call rate threshold is exceeded."""
        if len(self.metrics.response_times) < self.config.minimum_request_threshold:
            return False
        
        slow_calls = sum(
            1 for rt in self.metrics.response_times 
            if rt >= self.config.slow_call_duration_threshold
        )
        
        slow_call_rate = slow_calls / len(self.metrics.response_times)
        return slow_call_rate >= self.config.slow_call_rate_threshold
    
    async def _transition_to_open(self) -> None:
        """Transition circuit breaker to OPEN state."""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.state_start_time = time.time()
            self.metrics.update_state_change(self.state)
    
    async def _transition_to_half_open(self) -> None:
        """Transition circuit breaker to HALF_OPEN state."""
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.state_start_time = time.time()
            self.half_open_calls = 0
            self.metrics.recovery_attempts += 1
            self.metrics.last_recovery_attempt = datetime.now()
            self.metrics.update_state_change(self.state)
    
    async def _transition_to_closed(self) -> None:
        """Transition circuit breaker to CLOSED state."""
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.state_start_time = time.time()
            self.half_open_calls = 0
            # Reset consecutive failures on successful recovery
            self.metrics.consecutive_failures = 0
            self.metrics.update_state_change(self.state)
    
    def force_open(self) -> None:
        """Manually force circuit breaker to OPEN state."""
        logger.warning(f"Circuit breaker '{self.name}' manually forced OPEN")
        self.state = CircuitState.OPEN
        self.state_start_time = time.time()
        self.metrics.update_state_change(self.state)
    
    def force_close(self) -> None:
        """Manually force circuit breaker to CLOSED state."""
        logger.info(f"Circuit breaker '{self.name}' manually forced CLOSED")
        self.state = CircuitState.CLOSED
        self.state_start_time = time.time()
        self.half_open_calls = 0
        self.metrics.consecutive_failures = 0
        self.metrics.update_state_change(self.state)
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        logger.info(f"Circuit breaker '{self.name}' metrics reset")
        self.metrics = CircuitMetrics()
    
    @property
    def is_available(self) -> bool:
        """Check if circuit breaker allows requests."""
        return self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]
    
    @property
    def health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        return {
            'name': self.name,
            'state': self.state.value,
            'is_available': self.is_available,
            'time_in_state': time.time() - self.state_start_time,
            'metrics': self.metrics.to_dict(),
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'failure_rate_threshold': self.config.failure_rate_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'half_open_max_calls': self.config.half_open_max_calls,
            }
        }


def circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None,
    breaker_instance: Optional[CircuitBreaker] = None
):
    """
    Decorator for applying circuit breaker pattern to functions.
    
    Args:
        name: Circuit breaker name
        config: Optional configuration
        breaker_instance: Optional existing circuit breaker instance
        
    Example:
        @circuit_breaker("api_calls", config=CircuitBreakerConfig(failure_threshold=3))
        async def make_api_call():
            # API call implementation
            pass
    """
    # Use provided instance or create new one
    cb = breaker_instance or CircuitBreaker(name, config)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)
        
        # Attach circuit breaker instance for access
        wrapper.circuit_breaker = cb
        return wrapper
    
    return decorator


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.
    
    Provides centralized management and monitoring of circuit breakers
    across the application.
    """
    
    def __init__(self):
        """Initialize circuit breaker registry."""
        self.breakers: Dict[str, CircuitBreaker] = {}
        logger.info("CircuitBreakerRegistry initialized")
    
    def get_or_create(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get existing circuit breaker or create new one."""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(name, config)
            logger.info(f"Created new circuit breaker: {name}")
        
        return self.breakers[name]
    
    def get_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self.breakers.get(name)
    
    def list_breakers(self) -> List[str]:
        """List all circuit breaker names."""
        return list(self.breakers.keys())
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report for all circuit breakers."""
        return {
            'total_breakers': len(self.breakers),
            'breakers': {
                name: breaker.health_status
                for name, breaker in self.breakers.items()
            },
            'summary': {
                'open_breakers': sum(
                    1 for b in self.breakers.values() 
                    if b.state == CircuitState.OPEN
                ),
                'half_open_breakers': sum(
                    1 for b in self.breakers.values() 
                    if b.state == CircuitState.HALF_OPEN
                ),
                'closed_breakers': sum(
                    1 for b in self.breakers.values() 
                    if b.state == CircuitState.CLOSED
                ),
            }
        }
    
    def force_open_all(self) -> None:
        """Force all circuit breakers to OPEN state."""
        for breaker in self.breakers.values():
            breaker.force_open()
        logger.warning("All circuit breakers forced OPEN")
    
    def force_close_all(self) -> None:
        """Force all circuit breakers to CLOSED state."""
        for breaker in self.breakers.values():
            breaker.force_close()
        logger.info("All circuit breakers forced CLOSED")
    
    def reset_all_metrics(self) -> None:
        """Reset metrics for all circuit breakers."""
        for breaker in self.breakers.values():
            breaker.reset_metrics()
        logger.info("All circuit breaker metrics reset")


# Global registry instance
_global_registry = CircuitBreakerRegistry()

def get_circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
    """Get or create a circuit breaker from global registry."""
    return _global_registry.get_or_create(name, config)

def get_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    return _global_registry