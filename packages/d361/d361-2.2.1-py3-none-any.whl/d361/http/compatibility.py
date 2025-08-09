# this_file: external/int_folders/d361/src/d361/http/compatibility.py
"""
Aiohttp Compatibility Layer for smooth migration from legacy code.

This module provides adapters and compatibility functions to ease the transition
from aiohttp-based code to the new UnifiedHttpClient, minimizing breaking changes
during the migration process.
"""

from __future__ import annotations

import asyncio
import warnings
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from urllib.parse import urljoin

from loguru import logger

from .client import HttpResponse, UnifiedHttpClient, create_http_client


class AiohttpResponse:
    """
    Compatibility wrapper that mimics aiohttp.ClientResponse interface.
    
    This class wraps our HttpResponse to provide the same interface as
    aiohttp.ClientResponse, allowing legacy code to work with minimal changes.
    """
    
    def __init__(self, http_response: HttpResponse):
        self._response = http_response
        self._closed = False
    
    @property
    def status(self) -> int:
        """HTTP status code."""
        return self._response.status_code
    
    @property
    def headers(self) -> Dict[str, str]:
        """Response headers."""
        return self._response.headers
    
    @property
    def url(self) -> str:
        """Response URL."""
        return self._response.url
    
    @property
    def content_type(self) -> str:
        """Content type from headers."""
        return self._response.headers.get('content-type', '')
    
    @property
    def charset(self) -> Optional[str]:
        """Character encoding from content type."""
        content_type = self.content_type
        if 'charset=' in content_type:
            return content_type.split('charset=')[1].split(';')[0].strip()
        return None
    
    @property
    def content_length(self) -> Optional[int]:
        """Content length from headers."""
        length_str = self._response.headers.get('content-length')
        return int(length_str) if length_str else None
    
    @property
    def closed(self) -> bool:
        """Whether response is closed."""
        return self._closed
    
    def ok(self) -> bool:
        """Check if response is successful."""
        return self._response.is_success
    
    async def text(self, encoding: Optional[str] = None) -> str:
        """Get response text."""
        return self._response.text
    
    async def json(self, **kwargs) -> Any:
        """Get response JSON."""
        if self._response.json_data is not None:
            return self._response.json_data
        
        # Try to parse JSON if not already parsed
        import json
        try:
            return json.loads(self._response.text, **kwargs)
        except json.JSONDecodeError as e:
            raise ValueError(f"Cannot parse JSON: {e}")
    
    async def read(self) -> bytes:
        """Get response content as bytes."""
        return self._response.content
    
    def raise_for_status(self) -> None:
        """Raise exception for HTTP error status."""
        if self._response.is_client_error:
            from .client import HttpClientError
            raise HttpClientError(
                f"Client error {self._response.status_code}: {self._response.text[:200]}", 
                self._response
            )
        elif self._response.is_server_error:
            from .client import HttpServerError
            raise HttpServerError(
                f"Server error {self._response.status_code}: {self._response.text[:200]}", 
                self._response
            )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the response."""
        self._closed = True


class AiohttpSession:
    """
    Compatibility wrapper that mimics aiohttp.ClientSession interface.
    
    This class wraps UnifiedHttpClient to provide the same interface as
    aiohttp.ClientSession, enabling legacy code to work without modification.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[Union[float, Dict[str, float]]] = None,
        headers: Optional[Dict[str, str]] = None,
        trust_env: bool = True,
        connector: Optional[Any] = None,
        **kwargs,
    ):
        # Issue deprecation warning
        warnings.warn(
            "AiohttpSession is deprecated. Please migrate to UnifiedHttpClient for better performance and features.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Convert aiohttp timeout format to our format
        if isinstance(timeout, dict):
            # aiohttp uses total, connect, sock_read, etc.
            timeout_value = timeout.get('total', 30.0)
        else:
            timeout_value = timeout or 30.0
        
        self._client = UnifiedHttpClient(
            base_url=base_url,
            timeout=timeout_value,
            default_headers=headers,
            **kwargs
        )
        self._closed = False
        
        logger.debug(
            "AiohttpSession created (compatibility mode)",
            base_url=base_url,
            timeout=timeout_value,
        )
    
    @property
    def closed(self) -> bool:
        """Whether session is closed."""
        return self._closed
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the session."""
        if not self._closed:
            await self._client.close()
            self._closed = True
            logger.debug("AiohttpSession closed")
    
    def _ensure_not_closed(self):
        """Ensure session is not closed."""
        if self._closed:
            raise RuntimeError("Session is closed")
    
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> AiohttpResponse:
        """Make request and wrap response in compatibility layer."""
        self._ensure_not_closed()
        
        # Convert aiohttp parameters to our format
        request_kwargs = {}
        
        # Handle common aiohttp parameters
        if 'params' in kwargs:
            request_kwargs['params'] = kwargs['params']
        
        if 'headers' in kwargs:
            request_kwargs['headers'] = kwargs['headers']
        
        if 'json' in kwargs:
            request_kwargs['json_data'] = kwargs['json']
        
        if 'data' in kwargs:
            request_kwargs['data'] = kwargs['data']
        
        # Handle timeout (aiohttp specific)
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
            if hasattr(timeout, 'total'):
                # aiohttp.ClientTimeout object
                request_kwargs['timeout'] = timeout.total
            elif isinstance(timeout, (int, float)):
                request_kwargs['timeout'] = timeout
        
        # Make request using our client
        from .client import HttpMethod
        
        try:
            method_enum = HttpMethod(method.upper())
        except ValueError:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response = await self._client._make_request(method_enum, url, **request_kwargs)
        
        return AiohttpResponse(response)
    
    async def get(self, url: str, **kwargs) -> AiohttpResponse:
        """Make GET request."""
        return await self._make_request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> AiohttpResponse:
        """Make POST request."""
        return await self._make_request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> AiohttpResponse:
        """Make PUT request."""
        return await self._make_request('PUT', url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> AiohttpResponse:
        """Make PATCH request."""
        return await self._make_request('PATCH', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> AiohttpResponse:
        """Make DELETE request."""
        return await self._make_request('DELETE', url, **kwargs)
    
    async def head(self, url: str, **kwargs) -> AiohttpResponse:
        """Make HEAD request."""
        return await self._make_request('HEAD', url, **kwargs)
    
    async def options(self, url: str, **kwargs) -> AiohttpResponse:
        """Make OPTIONS request."""
        return await self._make_request('OPTIONS', url, **kwargs)
    
    async def request(self, method: str, url: str, **kwargs) -> AiohttpResponse:
        """Make request with specified method."""
        return await self._make_request(method, url, **kwargs)


# Legacy function aliases for backward compatibility
async def ClientSession(*args, **kwargs) -> AiohttpSession:
    """
    Create AiohttpSession for backward compatibility.
    
    Note: This is deprecated. Use UnifiedHttpClient instead.
    """
    warnings.warn(
        "ClientSession function is deprecated. Use create_http_client() or UnifiedHttpClient directly.",
        DeprecationWarning,
        stacklevel=2
    )
    return AiohttpSession(*args, **kwargs)


@asynccontextmanager
async def session(*args, **kwargs) -> AsyncGenerator[AiohttpSession, None]:
    """
    Context manager for creating aiohttp-compatible session.
    
    Note: This is deprecated. Use UnifiedHttpClient context manager instead.
    """
    warnings.warn(
        "session() function is deprecated. Use UnifiedHttpClient context manager instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    client_session = AiohttpSession(*args, **kwargs)
    try:
        yield client_session
    finally:
        await client_session.close()


# Migration utilities
class MigrationHelper:
    """Helper class for migrating from aiohttp to UnifiedHttpClient."""
    
    @staticmethod
    def convert_aiohttp_timeout(aiohttp_timeout: Any) -> float:
        """Convert aiohttp timeout to simple timeout value."""
        if hasattr(aiohttp_timeout, 'total'):
            return aiohttp_timeout.total
        elif isinstance(aiohttp_timeout, (int, float)):
            return float(aiohttp_timeout)
        elif isinstance(aiohttp_timeout, dict):
            return aiohttp_timeout.get('total', 30.0)
        else:
            return 30.0
    
    @staticmethod
    def get_migration_guide() -> str:
        """Get migration guide text."""
        return """
        Migration Guide: aiohttp to UnifiedHttpClient
        =============================================
        
        1. Replace aiohttp.ClientSession with UnifiedHttpClient:
        
        Before (aiohttp):
        ```python
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.example.com') as response:
                data = await response.json()
        ```
        
        After (UnifiedHttpClient):
        ```python
        from d361.http import create_http_client
        
        async with create_http_client() as client:
            response = await client.get('https://api.example.com')
            data = response.json_data
        ```
        
        2. Key differences:
        - Response data is immediately available (no need to await .json())
        - Better error handling with specific exception types
        - Built-in retries and logging
        - More detailed metrics and request tracking
        
        3. Compatibility layer available for gradual migration:
        ```python
        from d361.http.compatibility import AiohttpSession
        
        # Drop-in replacement for aiohttp.ClientSession
        async with AiohttpSession() as session:
            async with session.get('https://api.example.com') as response:
                data = await response.json()
        ```
        """
    
    @staticmethod
    def log_migration_suggestion(context: str):
        """Log suggestion to migrate from compatibility layer."""
        logger.info(
            "Migration suggestion: Consider upgrading to UnifiedHttpClient",
            context=context,
            guide_available=True,
        )