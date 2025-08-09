# this_file: external/int_folders/d361/src/d361/http/middleware.py
"""
HTTP Middleware - Common middleware functions for UnifiedHttpClient.

This module provides ready-to-use middleware for common HTTP client needs:
- Authentication handling
- Request/response logging
- Rate limiting
- Metrics collection
- Request correlation
- Security headers
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from loguru import logger

from .client import HttpResponse, RequestMetrics


class AuthenticationMiddleware:
    """Middleware for handling various authentication methods."""
    
    def __init__(
        self,
        auth_type: str = "bearer",
        token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.auth_type = auth_type.lower()
        self.token = token
        self.api_key = api_key
        self.api_key_header = api_key_header
        self.username = username
        self.password = password
    
    async def __call__(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add authentication headers to request."""
        headers = request_data.setdefault("headers", {})
        
        if self.auth_type == "bearer" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        elif self.auth_type == "basic" and self.username and self.password:
            import base64
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
        
        elif self.auth_type == "api_key" and self.api_key:
            headers[self.api_key_header] = self.api_key
        
        logger.debug("Authentication middleware applied", auth_type=self.auth_type)
        return request_data


class RequestIdMiddleware:
    """Middleware for adding unique request IDs for correlation."""
    
    def __init__(self, header_name: str = "X-Request-ID"):
        self.header_name = header_name
    
    async def __call__(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add unique request ID to headers."""
        headers = request_data.setdefault("headers", {})
        
        if self.header_name not in headers:
            request_id = str(uuid.uuid4())
            headers[self.header_name] = request_id
            logger.debug("Request ID added", request_id=request_id)
        
        return request_data


class UserAgentMiddleware:
    """Middleware for setting consistent User-Agent headers."""
    
    def __init__(self, user_agent: str = "d361-http-client/1.0"):
        self.user_agent = user_agent
    
    async def __call__(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set User-Agent header."""
        headers = request_data.setdefault("headers", {})
        
        if "User-Agent" not in headers:
            headers["User-Agent"] = self.user_agent
        
        return request_data


class SecurityHeadersMiddleware:
    """Middleware for adding security-related headers."""
    
    def __init__(self, enable_all: bool = True):
        self.enable_all = enable_all
    
    async def __call__(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add security headers to request."""
        headers = request_data.setdefault("headers", {})
        
        if self.enable_all:
            # Add security headers if not present
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY", 
                "X-XSS-Protection": "1; mode=block",
            }
            
            for header, value in security_headers.items():
                if header not in headers:
                    headers[header] = value
        
        return request_data


class LoggingMiddleware:
    """Middleware for detailed request/response logging."""
    
    def __init__(
        self, 
        log_requests: bool = True,
        log_responses: bool = True,
        log_body: bool = False,
        max_body_size: int = 1000,
    ):
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_body = log_body
        self.max_body_size = max_body_size
    
    async def log_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log outgoing request details."""
        if not self.log_requests:
            return request_data
        
        url = request_data.get("url", "")
        method = request_data.get("method", "")
        headers = request_data.get("headers", {})
        
        log_data = {
            "method": method,
            "url": url,
            "headers_count": len(headers),
        }
        
        # Log request body if enabled
        if self.log_body:
            if "json" in request_data and request_data["json"]:
                import json
                body_str = json.dumps(request_data["json"])
                if len(body_str) <= self.max_body_size:
                    log_data["json_body"] = request_data["json"]
                else:
                    log_data["json_body"] = f"<truncated {len(body_str)} chars>"
            
            elif "data" in request_data and request_data["data"]:
                data_str = str(request_data["data"])
                if len(data_str) <= self.max_body_size:
                    log_data["data_body"] = data_str
                else:
                    log_data["data_body"] = f"<truncated {len(data_str)} chars>"
        
        logger.info("HTTP request details", **log_data)
        return request_data
    
    async def log_response(self, response: HttpResponse) -> HttpResponse:
        """Log incoming response details."""
        if not self.log_responses:
            return response
        
        log_data = {
            "status_code": response.status_code,
            "url": response.url,
            "headers_count": len(response.headers),
            "content_type": response.headers.get("content-type", ""),
            "content_length": len(response.content) if response.content else 0,
        }
        
        # Log response body if enabled
        if self.log_body and response.text:
            if len(response.text) <= self.max_body_size:
                log_data["response_text"] = response.text
            else:
                log_data["response_text"] = f"<truncated {len(response.text)} chars>"
        
        # Log metrics if available
        if response.metrics:
            log_data.update({
                "duration_ms": response.metrics.duration_ms,
                "retry_count": response.metrics.retry_count,
            })
        
        logger.info("HTTP response details", **log_data)
        return response
    
    # Make this middleware work for both request and response
    async def __call__(self, data: Any) -> Any:
        """Handle both request and response logging."""
        if isinstance(data, dict) and "method" in data:
            # This is request data
            return await self.log_request(data)
        elif isinstance(data, HttpResponse):
            # This is response data
            return await self.log_response(data)
        else:
            # Unknown data type, pass through
            return data


class MetricsMiddleware:
    """Middleware for collecting HTTP request metrics."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_duration = 0.0
        self.status_codes: Dict[int, int] = {}
    
    async def __call__(self, response: HttpResponse) -> HttpResponse:
        """Collect metrics from response."""
        self.request_count += 1
        
        # Count status codes
        status = response.status_code
        self.status_codes[status] = self.status_codes.get(status, 0) + 1
        
        # Count errors
        if not response.is_success:
            self.error_count += 1
        
        # Track duration
        if response.metrics and response.metrics.duration_ms:
            self.total_duration += response.metrics.duration_ms
        
        logger.debug(
            "Metrics collected",
            total_requests=self.request_count,
            error_count=self.error_count,
            status_code=status,
        )
        
        return response
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        avg_duration = (
            self.total_duration / self.request_count 
            if self.request_count > 0 
            else 0.0
        )
        
        error_rate = (
            self.error_count / self.request_count * 100 
            if self.request_count > 0 
            else 0.0
        )
        
        return {
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "average_duration_ms": round(avg_duration, 2),
            "status_code_distribution": dict(self.status_codes),
        }


class RateLimitMiddleware:
    """Middleware for simple rate limiting."""
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []
    
    async def __call__(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check rate limit before making request."""
        now = time.time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we're at the limit
        if len(self.requests) >= self.max_requests:
            wait_time = self.time_window - (now - self.requests[0])
            logger.warning(
                "Rate limit reached",
                max_requests=self.max_requests,
                time_window=self.time_window,
                wait_time=wait_time,
            )
            
            # Simple delay - in production you might want to raise an exception instead
            import asyncio
            await asyncio.sleep(wait_time)
            
            # Clean up again after waiting
            now = time.time()
            self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Record this request
        self.requests.append(now)
        
        return request_data


class RetryMetricsMiddleware:
    """Middleware for tracking retry statistics."""
    
    def __init__(self):
        self.retry_stats: Dict[str, int] = {}
        self.total_retries = 0
    
    async def __call__(self, response: HttpResponse) -> HttpResponse:
        """Track retry metrics from response."""
        if response.metrics and response.metrics.retry_count > 0:
            self.total_retries += response.metrics.retry_count
            
            # Track retries by URL pattern
            url_pattern = self._get_url_pattern(response.url)
            self.retry_stats[url_pattern] = self.retry_stats.get(url_pattern, 0) + response.metrics.retry_count
            
            logger.info(
                "Retry metrics updated",
                url_pattern=url_pattern,
                retry_count=response.metrics.retry_count,
                total_retries=self.total_retries,
            )
        
        return response
    
    def _get_url_pattern(self, url: str) -> str:
        """Extract URL pattern for grouping."""
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception:
            return "unknown"
    
    def get_retry_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return {
            "total_retries": self.total_retries,
            "retry_by_endpoint": dict(self.retry_stats),
        }


# Convenience functions for creating common middleware
def create_auth_middleware(
    auth_type: str = "bearer",
    token: Optional[str] = None,
    **kwargs,
) -> AuthenticationMiddleware:
    """Create authentication middleware with given configuration."""
    return AuthenticationMiddleware(auth_type=auth_type, token=token, **kwargs)


def create_logging_middleware(
    log_requests: bool = True,
    log_responses: bool = True,
    log_body: bool = False,
) -> LoggingMiddleware:
    """Create logging middleware with given configuration."""
    return LoggingMiddleware(
        log_requests=log_requests,
        log_responses=log_responses, 
        log_body=log_body,
    )


def create_metrics_middleware() -> MetricsMiddleware:
    """Create metrics collection middleware."""
    return MetricsMiddleware()


def create_security_middleware() -> SecurityHeadersMiddleware:
    """Create security headers middleware."""
    return SecurityHeadersMiddleware()