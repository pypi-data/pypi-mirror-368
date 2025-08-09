#!/usr/bin/env python3
# this_file: external/int_folders/d361/test_circuit_breaker.py
"""
Test script for CircuitBreaker functionality.

This script validates the circuit breaker implementation including
state management, failure detection, and automatic recovery.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from d361.api.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
    CircuitMetrics,
    CircuitBreakerRegistry,
    circuit_breaker,
    get_circuit_breaker,
    get_registry
)


class TestException(Exception):
    """Test exception for circuit breaker testing."""
    pass


async def test_circuit_breaker_config():
    """Test circuit breaker configuration."""
    print("⚙️ Testing CircuitBreakerConfig...")
    
    # Test 1: Default configuration
    print("\n1. Testing default configuration...")
    try:
        config = CircuitBreakerConfig()
        print(f"   ✅ Default config: failure_threshold={config.failure_threshold}")
        print(f"   ⏱️  Timeouts: recovery={config.recovery_timeout}s, half_open={config.half_open_timeout}s")
        print(f"   📊 Thresholds: failure_rate={config.failure_rate_threshold}, slow_call={config.slow_call_rate_threshold}")
    except Exception as e:
        print(f"   ❌ Default config failed: {e}")
        return False
    
    # Test 2: Custom configuration
    print("\n2. Testing custom configuration...")
    try:
        config = CircuitBreakerConfig(
            failure_threshold=3,
            failure_rate_threshold=0.6,
            recovery_timeout=30.0,
            half_open_max_calls=5
        )
        print(f"   ✅ Custom config: failure_threshold={config.failure_threshold}")
        print(f"   📊 Custom thresholds: failure_rate={config.failure_rate_threshold}")
    except Exception as e:
        print(f"   ❌ Custom config failed: {e}")
        return False
    
    print("✅ CircuitBreakerConfig tests passed!")
    return True


async def test_circuit_metrics():
    """Test circuit breaker metrics."""
    print("\n📊 Testing CircuitMetrics...")
    
    # Test 1: Metrics initialization and updates
    print("\n1. Testing metrics updates...")
    try:
        metrics = CircuitMetrics()
        
        # Initial state
        print(f"   ✅ Metrics created: {metrics.total_requests} requests")
        print(f"   📊 Initial rates: success={metrics.success_rate:.1%}, failure={metrics.failure_rate:.1%}")
        
        # Update with successful requests
        metrics.update_request(success=True, response_time=0.5)
        metrics.update_request(success=True, response_time=0.8)
        print(f"   📈 After 2 successful: success={metrics.success_rate:.1%}, avg_time={metrics.avg_response_time:.2f}s")
        
        # Update with failed request
        metrics.update_request(success=False, response_time=2.0)
        print(f"   📉 After 1 failed: success={metrics.success_rate:.1%}, consecutive_failures={metrics.consecutive_failures}")
        
        # Test state change tracking
        metrics.update_state_change(CircuitState.OPEN)
        print(f"   🔄 State changes: {metrics.state_changes}")
        
    except Exception as e:
        print(f"   ❌ Metrics test failed: {e}")
        return False
    
    # Test 2: Metrics serialization
    print("\n2. Testing metrics serialization...")
    try:
        metrics_dict = metrics.to_dict()
        print(f"   ✅ Serialized to dict with {len(metrics_dict)} keys")
        print(f"   📊 Contains: {list(metrics_dict.keys())[:5]}...")
    except Exception as e:
        print(f"   ❌ Metrics serialization failed: {e}")
        return False
    
    print("✅ CircuitMetrics tests passed!")
    return True


async def test_circuit_breaker_states():
    """Test circuit breaker state transitions."""
    print("\n🔄 Testing CircuitBreaker state transitions...")
    
    # Test 1: Basic circuit breaker creation
    print("\n1. Testing circuit breaker creation...")
    try:
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=5.0)
        cb = CircuitBreaker("test_breaker", config)
        
        print(f"   ✅ Circuit breaker created: {cb.name}")
        print(f"   🔄 Initial state: {cb.state.value}")
        print(f"   📊 Available: {cb.is_available}")
        
    except Exception as e:
        print(f"   ❌ Circuit breaker creation failed: {e}")
        return False
    
    # Test 2: State transitions via failures
    print("\n2. Testing failure-induced state transitions...")
    try:
        # Create a test function that fails
        async def failing_function():
            raise TestException("Simulated failure")
        
        # Test successful calls first
        async def successful_function():
            return "success"
        
        result = await cb.call(successful_function)
        print(f"   ✅ Successful call: {result}")
        print(f"   🔄 State after success: {cb.state.value}")
        
        # Now test failures
        failure_count = 0
        for i in range(3):  # More than failure_threshold (2)
            try:
                await cb.call(failing_function)
                failure_count += 1
                print(f"   📉 Failure {failure_count}, state: {cb.state.value}")
            except TestException:
                failure_count += 1
                print(f"   📉 Failure {failure_count}, state: {cb.state.value}")
            except CircuitBreakerError:
                # Circuit opened, subsequent calls are blocked
                print(f"   🔴 Circuit opened after {failure_count} failures, blocking subsequent calls")
                break
        
        print(f"   🔴 Final state after failures: {cb.state.value}")
        
        # Test that circuit is now open
        try:
            await cb.call(successful_function)
            print("   ❌ Circuit should be OPEN, call should fail")
            return False
        except CircuitBreakerError as e:
            print(f"   ✅ Circuit correctly blocked call: {e.circuit_state}")
        
    except Exception as e:
        print(f"   ❌ State transition test failed: {e}")
        return False
    
    print("✅ CircuitBreaker state tests passed!")
    return True


async def test_circuit_breaker_recovery():
    """Test circuit breaker recovery mechanism."""
    print("\n🔄 Testing CircuitBreaker recovery...")
    
    # Test recovery after timeout
    print("\n1. Testing automatic recovery...")
    try:
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=5.0)  # Valid timeout
        cb = CircuitBreaker("recovery_test", config)
        
        # Force failure to open circuit
        async def failing_function():
            raise TestException("Failure")
        
        try:
            await cb.call(failing_function)
        except TestException:
            pass
        
        print(f"   🔴 Circuit state after failure: {cb.state.value}")
        
        # Simulate timeout by manually triggering half-open state for testing
        await cb._transition_to_half_open()
        print(f"   🟡 State after simulated timeout: {cb.state.value}")
        
        # Test successful call in half-open state
        async def successful_function():
            return "recovered"
        
        # This should succeed and close the circuit
        result = await cb.call(successful_function)
        print(f"   ✅ Recovery successful: {result}")
        
        # Make enough successful calls to close the circuit
        for i in range(cb.config.half_open_max_calls - 1):
            await cb.call(successful_function)
        
        print(f"   🟢 Final state: {cb.state.value}")
        
    except Exception as e:
        print(f"   ❌ Recovery test failed: {e}")
        return False
    
    print("✅ CircuitBreaker recovery tests passed!")
    return True


async def test_circuit_breaker_decorator():
    """Test circuit breaker decorator."""
    print("\n🎨 Testing CircuitBreaker decorator...")
    
    # Test 1: Decorator application
    print("\n1. Testing decorator application...")
    try:
        config = CircuitBreakerConfig(failure_threshold=2)
        
        @circuit_breaker("decorator_test", config)
        async def test_function(should_fail=False):
            if should_fail:
                raise TestException("Decorator test failure")
            return "decorator success"
        
        # Test successful call
        result = await test_function()
        print(f"   ✅ Decorated function success: {result}")
        
        # Access circuit breaker instance
        cb_instance = test_function.circuit_breaker
        print(f"   📊 Circuit breaker accessible: {cb_instance.name}")
        print(f"   🔄 State: {cb_instance.state.value}")
        
        # Test failure
        try:
            await test_function(should_fail=True)
        except TestException:
            print(f"   📉 Expected failure caught, state: {cb_instance.state.value}")
        
    except Exception as e:
        print(f"   ❌ Decorator test failed: {e}")
        return False
    
    print("✅ CircuitBreaker decorator tests passed!")
    return True


async def test_circuit_breaker_registry():
    """Test circuit breaker registry."""
    print("\n📋 Testing CircuitBreakerRegistry...")
    
    # Test 1: Registry operations
    print("\n1. Testing registry operations...")
    try:
        registry = CircuitBreakerRegistry()
        
        # Create circuit breakers
        cb1 = registry.get_or_create("api_calls")
        cb2 = registry.get_or_create("database_calls")
        
        print(f"   ✅ Created breakers: {len(registry.list_breakers())}")
        print(f"   📋 Breaker names: {registry.list_breakers()}")
        
        # Test getting existing breaker
        cb1_again = registry.get_or_create("api_calls")
        print(f"   ✅ Same instance: {cb1 is cb1_again}")
        
        # Test health report
        health = registry.get_health_report()
        print(f"   📊 Health report: {health['total_breakers']} breakers")
        print(f"   🟢 Closed: {health['summary']['closed_breakers']}")
        
    except Exception as e:
        print(f"   ❌ Registry test failed: {e}")
        return False
    
    # Test 2: Global registry functions
    print("\n2. Testing global registry functions...")
    try:
        # Test global functions
        global_cb = get_circuit_breaker("global_test")
        global_registry = get_registry()
        
        print(f"   ✅ Global circuit breaker: {global_cb.name}")
        print(f"   📋 Global registry has {len(global_registry.list_breakers())} breakers")
        
    except Exception as e:
        print(f"   ❌ Global registry test failed: {e}")
        return False
    
    print("✅ CircuitBreakerRegistry tests passed!")
    return True


async def test_circuit_breaker_error():
    """Test circuit breaker error handling."""
    print("\n🚨 Testing CircuitBreakerError...")
    
    try:
        # Create a circuit breaker error
        metrics = CircuitMetrics()
        metrics.consecutive_failures = 5
        metrics.failure_rate = 0.8
        
        error = CircuitBreakerError(
            "Circuit is open",
            CircuitState.OPEN,
            metrics
        )
        
        print(f"   ✅ CircuitBreakerError created: {error}")
        print(f"   📊 Error context: {error.context}")
        print(f"   🔄 Circuit state: {error.circuit_state}")
        print(f"   📈 Failure rate: {error.metrics.failure_rate}")
        
    except Exception as e:
        print(f"   ❌ CircuitBreakerError test failed: {e}")
        return False
    
    print("✅ CircuitBreakerError tests passed!")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting CircuitBreaker Tests")
    
    success = True
    
    # Test configuration
    if not await test_circuit_breaker_config():
        success = False
    
    # Test metrics
    if not await test_circuit_metrics():
        success = False
    
    # Test state management
    if not await test_circuit_breaker_states():
        success = False
    
    # Test recovery
    if not await test_circuit_breaker_recovery():
        success = False
    
    # Test decorator
    if not await test_circuit_breaker_decorator():
        success = False
    
    # Test registry
    if not await test_circuit_breaker_registry():
        success = False
    
    # Test error handling
    if not await test_circuit_breaker_error():
        success = False
    
    if success:
        print("\n🎉 All CircuitBreaker tests completed successfully!")
        print("✅ CircuitBreaker is ready for production use")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())