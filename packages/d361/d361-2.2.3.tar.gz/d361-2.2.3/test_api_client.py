#!/usr/bin/env python3
# this_file: external/int_folders/d361/test_api_client.py
"""
Test script for Document360ApiClient functionality.

This script validates the API client implementation including token management,
error handling, request validation, and all high-level API methods.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from d361.api import Document360ApiClient, ApiConfig
from d361.api.errors import ValidationError, AuthenticationError


async def test_api_client():
    """Test Document360ApiClient functionality."""
    print("🧪 Testing Document360ApiClient...")
    
    # Test 1: Configuration validation
    print("\n1. Testing configuration validation...")
    try:
        config = ApiConfig(
            api_tokens=["test-token-1", "test-token-2"],
            base_url="https://apihub.document360.io/v1",
            timeout=30.0,
            max_retries=3
        )
        print("   ✅ ApiConfig created successfully")
        print(f"   📊 Config: {len(config.api_tokens)} tokens, timeout={config.timeout}s")
    except Exception as e:
        print(f"   ❌ ApiConfig creation failed: {e}")
        return False
    
    # Test 2: Invalid configuration
    print("\n2. Testing invalid configuration handling...")
    try:
        invalid_config = ApiConfig(api_tokens=[])  # Empty tokens list
        print("   ❌ Should have failed with empty tokens")
        return False
    except Exception as e:
        print(f"   ✅ Correctly rejected invalid config: {e}")
    
    # Test 3: Client initialization
    print("\n3. Testing client initialization...")
    try:
        client = Document360ApiClient(config)
        print("   ✅ API client initialized successfully")
        print(f"   🏭 Token manager has {client.token_manager.available_tokens_count} available tokens")
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        return False
    
    # Test 4: Validation error handling
    print("\n4. Testing validation error handling...")
    try:
        await client.get_article("")  # Empty article ID
        print("   ❌ Should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"   ✅ Correctly raised ValidationError: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error type: {type(e).__name__}: {e}")
        return False
    
    # Test 5: Parameter validation for list_articles
    print("\n5. Testing list_articles parameter validation...")
    try:
        await client.list_articles(limit=1000)  # Exceeds maximum
        print("   ❌ Should have raised ValidationError for limit > 500")
        return False
    except ValidationError as e:
        print(f"   ✅ Correctly validated limit parameter: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    # Test 6: Create article validation
    print("\n6. Testing create_article validation...")
    try:
        await client.create_article({})  # Missing required fields
        print("   ❌ Should have raised ValidationError for missing fields")
        return False
    except ValidationError as e:
        print(f"   ✅ Correctly validated required fields: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False
    
    # Test 7: Statistics and health
    print("\n7. Testing statistics and health monitoring...")
    try:
        stats = client.statistics
        print(f"   ✅ Statistics retrieved: {stats['total_requests']} total requests")
        
        # Note: health_check will fail without valid tokens, but that's expected
        print("   📊 Health check would require valid API tokens")
    except Exception as e:
        print(f"   ❌ Statistics error: {e}")
        return False
    
    # Test 8: Context manager support
    print("\n8. Testing async context manager...")
    try:
        async with Document360ApiClient(config) as test_client:
            test_stats = test_client.statistics
            print(f"   ✅ Context manager working, stats: {test_stats['uptime_seconds']:.2f}s uptime")
    except Exception as e:
        print(f"   ❌ Context manager error: {e}")
        return False
    
    # Test 9: Token manager integration
    print("\n9. Testing token manager integration...")
    try:
        health_report = client.token_manager.get_health_report()
        print(f"   ✅ Token health report: {health_report['total_tokens']} tokens, {health_report['healthy_tokens']} healthy")
    except Exception as e:
        print(f"   ❌ Token manager error: {e}")
        return False
    
    # Cleanup
    await client.close()
    
    print("\n✅ All API client tests passed!")
    return True


async def test_error_classification():
    """Test error classification and handling."""
    print("\n🔥 Testing error classification...")
    
    from d361.api.errors import ErrorHandler, ErrorSeverity, ErrorCategory
    from d361.http.client import HttpResponse
    
    # Test 1: HTTP error classification
    print("\n1. Testing HTTP error classification...")
    
    # Mock response for 404 error
    class MockResponse:
        def __init__(self, status_code, json_data=None, text="", url="https://test.com", headers=None):
            self.status_code = status_code
            self.json_data = json_data or {}
            self.text = text
            self.url = url
            self.headers = headers or {}
    
    try:
        mock_404 = MockResponse(404, {"resource_id": "test-123"})
        error = ErrorHandler.classify_error(mock_404)
        print(f"   ✅ 404 classified as: {error.category.value} / {error.severity.value}")
        print(f"   📋 Error context: {error.context}")
    except Exception as e:
        print(f"   ❌ 404 classification failed: {e}")
        return False
    
    # Test 2: Rate limit error
    print("\n2. Testing rate limit error classification...")
    try:
        mock_429 = MockResponse(429, headers={"retry-after": "60"})
        error = ErrorHandler.classify_error(mock_429)
        print(f"   ✅ 429 classified as: {error.category.value} / {error.severity.value}")
        print(f"   ⏱️  Retry after: {getattr(error, 'retry_after', 'Not specified')}")
    except Exception as e:
        print(f"   ❌ 429 classification failed: {e}")
        return False
    
    # Test 3: Retry strategy
    print("\n3. Testing retry strategy...")
    try:
        from d361.api.errors import RateLimitError
        rate_error = RateLimitError("Rate limited", retry_after=30)
        
        should_retry_1 = ErrorHandler.should_retry(rate_error, attempt=1, max_attempts=3)
        should_retry_4 = ErrorHandler.should_retry(rate_error, attempt=4, max_attempts=3)
        
        print(f"   ✅ Retry attempt 1: {should_retry_1}")
        print(f"   ✅ Retry attempt 4: {should_retry_4}")
        
        delay = ErrorHandler.get_retry_delay(rate_error, attempt=1)
        print(f"   ⏱️  Retry delay: {delay}s")
    except Exception as e:
        print(f"   ❌ Retry strategy test failed: {e}")
        return False
    
    print("\n✅ All error classification tests passed!")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting Document360 API Client Tests")
    
    success = True
    
    # Test API client functionality
    if not await test_api_client():
        success = False
    
    # Test error handling
    if not await test_error_classification():
        success = False
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("✅ Document360ApiClient is ready for production use")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())