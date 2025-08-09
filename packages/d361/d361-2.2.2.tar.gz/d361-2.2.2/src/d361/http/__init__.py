# this_file: external/int_folders/d361/src/d361/http/__init__.py
"""
HTTP Client Module - Enterprise-grade HTTP handling for d361.

This module provides a unified HTTP client built on httpx with enterprise features:
- Automatic retries with exponential backoff
- Comprehensive logging and metrics
- Request/response middleware support  
- Legacy aiohttp compatibility layer
- Robust error handling and classification

Examples:
    Basic usage:
    >>> from d361.http import create_http_client
    >>> async with create_http_client() as client:
    ...     response = await client.get('https://api.example.com')
    ...     print(response.status_code, response.json_data)
    
    With configuration:
    >>> from d361.http import UnifiedHttpClient, RetryConfig
    >>> retry_config = RetryConfig(max_attempts=5, wait_min=2.0)
    >>> client = UnifiedHttpClient(
    ...     base_url='https://api.example.com',
    ...     timeout=60.0,
    ...     retry_config=retry_config,
    ... )
    
    Legacy compatibility:
    >>> from d361.http import AiohttpSession  # Deprecated
    >>> async with AiohttpSession() as session:
    ...     async with session.get('https://api.example.com') as response:
    ...         data = await response.json()
"""

# Core client classes
from .client import (
    HttpMethod,
    HttpResponse, 
    RetryConfig,
    RequestMetrics,
    UnifiedHttpClient,
    create_http_client,
)

# Error classes
from .client import (
    HttpError,
    HttpClientError,
    HttpServerError,
    HttpTimeoutError,
    HttpNetworkError,
)

# Compatibility layer (deprecated)
from .compatibility import (
    AiohttpResponse,
    AiohttpSession,
    ClientSession,
    MigrationHelper,
    session,
)

__all__ = [
    # Core client
    "UnifiedHttpClient",
    "create_http_client",
    
    # Configuration
    "HttpMethod",
    "RetryConfig", 
    "RequestMetrics",
    
    # Response handling
    "HttpResponse",
    
    # Error handling
    "HttpError",
    "HttpClientError",
    "HttpServerError", 
    "HttpTimeoutError",
    "HttpNetworkError",
    
    # Compatibility layer (deprecated)
    "AiohttpResponse",
    "AiohttpSession",
    "ClientSession", 
    "session",
    "MigrationHelper",
]

# Module-level convenience functions
async def get(url: str, **kwargs) -> HttpResponse:
    """
    Convenience function for making GET requests.
    
    Creates a temporary client instance for one-off requests.
    For multiple requests, use create_http_client() or UnifiedHttpClient.
    """
    async with create_http_client() as client:
        return await client.get(url, **kwargs)


async def post(url: str, **kwargs) -> HttpResponse:
    """
    Convenience function for making POST requests.
    
    Creates a temporary client instance for one-off requests.
    For multiple requests, use create_http_client() or UnifiedHttpClient.
    """
    async with create_http_client() as client:
        return await client.post(url, **kwargs)


async def put(url: str, **kwargs) -> HttpResponse:
    """
    Convenience function for making PUT requests.
    
    Creates a temporary client instance for one-off requests.
    For multiple requests, use create_http_client() or UnifiedHttpClient.
    """
    async with create_http_client() as client:
        return await client.put(url, **kwargs)


async def delete(url: str, **kwargs) -> HttpResponse:
    """
    Convenience function for making DELETE requests.
    
    Creates a temporary client instance for one-off requests.
    For multiple requests, use create_http_client() or UnifiedHttpClient.
    """
    async with create_http_client() as client:
        return await client.delete(url, **kwargs)


# Add convenience functions to __all__
__all__.extend([
    "get",
    "post", 
    "put",
    "delete",
])