# this_file: external/int_folders/d361/src/d361/http/client.py
"""
UnifiedHttpClient - Enterprise-grade HTTP client built on httpx.

This module provides a comprehensive HTTP client with automatic retries, 
logging, error handling, and middleware support. Designed to replace 
fragmented HTTP handling across the codebase with a single, robust solution.
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import httpx
from loguru import logger
from pydantic import BaseModel, Field
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# Context variable for request correlation
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class HttpMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""
    max_attempts: int = Field(default=3, ge=1, le=10)
    wait_min: float = Field(default=1.0, ge=0.1)
    wait_max: float = Field(default=60.0, ge=1.0)
    multiplier: float = Field(default=2.0, ge=1.0)
    retry_on_status: List[int] = Field(default_factory=lambda: [429, 502, 503, 504])
    retry_on_exceptions: List[str] = Field(
        default_factory=lambda: [
            "httpx.ConnectError",
            "httpx.TimeoutException", 
            "httpx.NetworkError"
        ]
    )


class RequestMetrics(BaseModel):
    """Metrics captured for each HTTP request."""
    method: str
    url: str
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    retry_count: int = 0
    error: Optional[str] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None


@dataclass
class HttpResponse:
    """Enhanced response wrapper with additional metadata."""
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    json_data: Optional[Dict[str, Any]] = None
    metrics: Optional[RequestMetrics] = None
    url: str = ""
    
    @property
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return 200 <= self.status_code < 300
    
    @property
    def is_client_error(self) -> bool:
        """Check if response indicates client error."""
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        """Check if response indicates server error."""
        return 500 <= self.status_code < 600


class HttpError(Exception):
    """Base exception for HTTP operations."""
    def __init__(self, message: str, response: Optional[HttpResponse] = None):
        super().__init__(message)
        self.response = response


class HttpClientError(HttpError):
    """Exception for 4xx client errors."""
    pass


class HttpServerError(HttpError):  
    """Exception for 5xx server errors."""
    pass


class HttpTimeoutError(HttpError):
    """Exception for timeout errors."""
    pass


class HttpNetworkError(HttpError):
    """Exception for network connectivity errors."""
    pass


class UnifiedHttpClient:
    """
    Enterprise-grade HTTP client with retries, logging, and middleware.
    
    Features:
    - Automatic retries with exponential backoff
    - Comprehensive request/response logging
    - Error classification and handling
    - Request correlation tracking
    - Metrics collection
    - Middleware support
    - Connection pooling and reuse
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
        default_headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self.default_headers = default_headers or {}
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        
        # Create httpx client with optimal settings
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections
        )
        
        # Build client kwargs, only including base_url if it's not None
        client_kwargs = {
            "timeout": httpx.Timeout(timeout),
            "headers": default_headers,
            "verify": verify_ssl,
            "follow_redirects": follow_redirects,
            "limits": limits,
        }
        
        if base_url is not None:
            client_kwargs["base_url"] = base_url
        
        self._client = httpx.AsyncClient(**client_kwargs)
        
        # Middleware and hooks
        self._request_middleware: List[callable] = []
        self._response_middleware: List[callable] = []
        
        logger.info(
            "UnifiedHttpClient initialized",
            base_url=base_url,
            timeout=timeout,
            verify_ssl=verify_ssl,
            max_connections=max_connections,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the underlying HTTP client."""
        await self._client.aclose()
        logger.debug("UnifiedHttpClient closed")

    def add_request_middleware(self, middleware: callable):
        """Add middleware that processes requests before sending."""
        self._request_middleware.append(middleware)
        middleware_name = getattr(middleware, '__name__', middleware.__class__.__name__)
        logger.debug("Request middleware added", middleware=middleware_name)

    def add_response_middleware(self, middleware: callable):
        """Add middleware that processes responses after receiving."""
        self._response_middleware.append(middleware)
        middleware_name = getattr(middleware, '__name__', middleware.__class__.__name__)
        logger.debug("Response middleware added", middleware=middleware_name)

    async def _apply_request_middleware(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all request middleware in order."""
        for middleware in self._request_middleware:
            request_data = await self._call_middleware(middleware, request_data)
        return request_data

    async def _apply_response_middleware(self, response: HttpResponse) -> HttpResponse:
        """Apply all response middleware in order."""
        for middleware in self._response_middleware:
            response = await self._call_middleware(middleware, response)
        return response

    async def _call_middleware(self, middleware: callable, data: Any) -> Any:
        """Call middleware function, handling both sync and async."""
        if asyncio.iscoroutinefunction(middleware):
            return await middleware(data)
        else:
            return middleware(data)

    def _should_retry(self, exception: Exception, response: Optional[HttpResponse] = None) -> bool:
        """Determine if request should be retried based on config."""
        # Check HTTP status codes
        if response and response.status_code in self.retry_config.retry_on_status:
            return True
            
        # Check exception types
        exception_name = f"{exception.__class__.__module__}.{exception.__class__.__name__}"
        return exception_name in self.retry_config.retry_on_exceptions

    async def _make_request(
        self,
        method: HttpMethod,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> HttpResponse:
        """
        Make HTTP request with retries, logging, and error handling.
        """
        request_id = f"req_{int(time.time() * 1000000)}"
        request_id_ctx.set(request_id)
        
        # Prepare request data
        request_data = {
            "method": method.value,
            "url": url,
            "headers": {**self.default_headers, **(headers or {})},
            "params": params,
            "json": json_data,
            "data": data,
            "files": files,
            **kwargs
        }
        
        # Apply request middleware
        request_data = await self._apply_request_middleware(request_data)
        
        # Initialize metrics
        full_url = url
        if not url.startswith("http") and self._client.base_url:
            full_url = str(self._client.base_url).rstrip("/") + "/" + url.lstrip("/")
        
        metrics = RequestMetrics(
            method=method.value,
            url=full_url
        )
        
        # Calculate request size
        if json_data:
            import json
            metrics.request_size = len(json.dumps(json_data).encode())
        elif data:
            metrics.request_size = len(str(data).encode()) if isinstance(data, str) else len(data) if isinstance(data, bytes) else None
        
        logger.info(
            "HTTP request starting",
            request_id=request_id,
            method=method.value,
            url=full_url,
            headers_count=len(request_data["headers"]),
            has_params=bool(params),
            has_json=bool(json_data),
            has_data=bool(data),
            has_files=bool(files),
        )
        
        start_time = time.time()
        
        # Execute request with retries
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self.retry_config.max_attempts),
            wait=wait_exponential(
                multiplier=self.retry_config.multiplier,
                min=self.retry_config.wait_min,
                max=self.retry_config.wait_max,
            ),
            retry=retry_if_exception_type((
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.NetworkError,
            )),
            reraise=True,
        ):
            with attempt:
                try:
                    # Build request arguments, filtering out None values
                    request_args = {
                        "method": request_data["method"],
                        "url": request_data["url"],
                    }
                    
                    # Add optional parameters only if they're not None
                    if request_data["headers"]:
                        request_args["headers"] = request_data["headers"]
                    if request_data["params"]:
                        request_args["params"] = request_data["params"]
                    if request_data["json"]:
                        request_args["json"] = request_data["json"]
                    if request_data["data"]:
                        request_args["data"] = request_data["data"]
                    if request_data["files"]:
                        request_args["files"] = request_data["files"]
                    
                    # Make the actual HTTP request
                    raw_response = await self._client.request(**request_args)
                    
                    # Calculate metrics
                    duration = time.time() - start_time
                    metrics.duration_ms = duration * 1000
                    metrics.status_code = raw_response.status_code
                    metrics.response_size = len(raw_response.content)
                    metrics.retry_count = attempt.retry_state.attempt_number - 1
                    
                    # Create response object
                    json_content = None
                    try:
                        if raw_response.headers.get("content-type", "").startswith("application/json"):
                            json_content = raw_response.json()
                    except Exception:
                        pass  # Not JSON or invalid JSON
                    
                    response = HttpResponse(
                        status_code=raw_response.status_code,
                        headers=dict(raw_response.headers),
                        content=raw_response.content,
                        text=raw_response.text,
                        json_data=json_content,
                        url=str(raw_response.url),
                        metrics=metrics,
                    )
                    
                    # Check for HTTP errors that should trigger retries
                    if raw_response.status_code in self.retry_config.retry_on_status:
                        error_msg = f"HTTP {raw_response.status_code}: {raw_response.text[:100]}"
                        logger.warning(
                            "HTTP error, will retry",
                            request_id=request_id,
                            status_code=raw_response.status_code,
                            error=error_msg,
                            attempt=attempt.retry_state.attempt_number,
                        )
                        raise httpx.HTTPStatusError(error_msg, request=raw_response.request, response=raw_response)
                    
                    # Apply response middleware
                    response = await self._apply_response_middleware(response)
                    
                    # Log successful response
                    logger.info(
                        "HTTP request completed",
                        request_id=request_id,
                        status_code=response.status_code,
                        duration_ms=metrics.duration_ms,
                        response_size=metrics.response_size,
                        retry_count=metrics.retry_count,
                    )
                    
                    # Check for client/server errors after retries exhausted
                    if response.is_client_error:
                        raise HttpClientError(
                            f"Client error {response.status_code}: {response.text[:200]}", 
                            response
                        )
                    elif response.is_server_error:
                        raise HttpServerError(
                            f"Server error {response.status_code}: {response.text[:200]}", 
                            response
                        )
                    
                    return response
                    
                except httpx.TimeoutException as e:
                    metrics.error = str(e)
                    logger.error(
                        "HTTP request timeout",
                        request_id=request_id,
                        error=str(e),
                        attempt=attempt.retry_state.attempt_number,
                    )
                    if attempt.retry_state.attempt_number >= self.retry_config.max_attempts:
                        raise HttpTimeoutError(f"Request timeout after {self.retry_config.max_attempts} attempts", None)
                    raise
                    
                except (httpx.ConnectError, httpx.NetworkError) as e:
                    metrics.error = str(e)
                    logger.error(
                        "HTTP network error",
                        request_id=request_id,
                        error=str(e),
                        attempt=attempt.retry_state.attempt_number,
                    )
                    if attempt.retry_state.attempt_number >= self.retry_config.max_attempts:
                        raise HttpNetworkError(f"Network error after {self.retry_config.max_attempts} attempts: {e}", None)
                    raise
                    
                except Exception as e:
                    metrics.error = str(e)
                    metrics.duration_ms = (time.time() - start_time) * 1000
                    logger.error(
                        "HTTP request failed",
                        request_id=request_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        duration_ms=metrics.duration_ms,
                    )
                    raise

    # Convenience methods for common HTTP operations
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Make GET request."""
        return await self._make_request(HttpMethod.GET, url, headers=headers, params=params, **kwargs)

    async def post(
        self,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Make POST request."""
        return await self._make_request(HttpMethod.POST, url, headers=headers, json_data=json_data, data=data, **kwargs)

    async def put(
        self,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Make PUT request."""
        return await self._make_request(HttpMethod.PUT, url, headers=headers, json_data=json_data, data=data, **kwargs)

    async def patch(
        self,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Make PATCH request."""
        return await self._make_request(HttpMethod.PATCH, url, headers=headers, json_data=json_data, data=data, **kwargs)

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Make DELETE request."""
        return await self._make_request(HttpMethod.DELETE, url, headers=headers, **kwargs)

    async def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> HttpResponse:
        """Make HEAD request."""
        return await self._make_request(HttpMethod.HEAD, url, headers=headers, **kwargs)

    # Context manager for multiple requests
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[UnifiedHttpClient, None]:
        """Create a session context for multiple requests."""
        try:
            yield self
        finally:
            # Session cleanup if needed
            pass


# Factory function for easy client creation
def create_http_client(
    base_url: Optional[str] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    verify_ssl: bool = True,
    retry_config: Optional[RetryConfig] = None,
    **kwargs,
) -> UnifiedHttpClient:
    """
    Factory function to create configured HTTP client.
    
    Args:
        base_url: Base URL for requests
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts (ignored if retry_config provided)
        verify_ssl: Whether to verify SSL certificates
        retry_config: Custom retry configuration (overrides max_retries)
        **kwargs: Additional client configuration
    
    Returns:
        Configured UnifiedHttpClient instance
    """
    # Use provided retry_config or create one from max_retries
    if retry_config is None:
        retry_config = RetryConfig(max_attempts=max_retries)
    
    return UnifiedHttpClient(
        base_url=base_url,
        timeout=timeout,
        retry_config=retry_config,
        verify_ssl=verify_ssl,
        **kwargs,
    )