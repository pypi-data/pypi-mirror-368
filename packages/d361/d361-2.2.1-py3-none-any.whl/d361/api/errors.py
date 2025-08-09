# this_file: external/int_folders/d361/src/d361/api/errors.py
"""
Error handling for Document360 API operations.

This module provides comprehensive error classification, handling strategies,
and resilience patterns for robust API interactions.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from ..http.client import HttpResponse


class ErrorSeverity(str, Enum):
    """Error severity levels for classification."""
    LOW = "low"           # Temporary, retryable errors
    MEDIUM = "medium"     # Degraded service, may retry with backoff
    HIGH = "high"         # Service errors, limited retries
    CRITICAL = "critical" # Authentication/authorization errors, no retry


class ErrorCategory(str, Enum):
    """Error categories for classification and handling."""
    NETWORK = "network"               # Network connectivity issues
    RATE_LIMIT = "rate_limit"        # API rate limiting
    AUTHENTICATION = "authentication" # Auth/authorization errors
    VALIDATION = "validation"        # Input validation errors
    NOT_FOUND = "not_found"          # Resource not found
    SERVER_ERROR = "server_error"    # Server-side errors
    CLIENT_ERROR = "client_error"    # Client-side errors
    UNKNOWN = "unknown"              # Unclassified errors


class Document360Error(Exception):
    """
    Base exception for all Document360 API operations.
    
    Provides comprehensive error context, classification, and
    handling strategies for robust error management.
    """
    
    def __init__(
        self,
        message: str,
        response: Optional[HttpResponse] = None,
        error_code: Optional[str] = None,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        retryable: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.response = response
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.retryable = retryable
        self.context = context or {}
        
        # Extract additional context from response
        if response:
            self.context.update({
                "status_code": response.status_code,
                "url": response.url,
                "response_headers": dict(response.headers),
            })
    
    @property
    def status_code(self) -> Optional[int]:
        """Get HTTP status code if available."""
        return self.response.status_code if self.response else None
    
    @property
    def response_text(self) -> Optional[str]:
        """Get response text if available."""
        return self.response.text if self.response else None
    
    @property
    def response_json(self) -> Optional[Dict[str, Any]]:
        """Get response JSON if available."""
        return self.response.json_data if self.response else None
    
    def __str__(self) -> str:
        """Enhanced string representation with context."""
        parts = [super().__str__()]
        
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        
        if self.response:
            parts.append(f"Status: {self.response.status_code}")
        
        parts.append(f"Category: {self.category.value}")
        parts.append(f"Severity: {self.severity.value}")
        parts.append(f"Retryable: {self.retryable}")
        
        return " | ".join(parts)


class ApiError(Document360Error):
    """General API error for unclassified API issues."""
    
    def __init__(self, message: str, response: Optional[HttpResponse] = None, **kwargs):
        super().__init__(
            message,
            response=response,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            retryable=True,
            **kwargs
        )


class AuthenticationError(Document360Error):
    """Authentication and authorization errors."""
    
    def __init__(self, message: str, response: Optional[HttpResponse] = None, **kwargs):
        super().__init__(
            message,
            response=response,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.CRITICAL,
            retryable=False,
            **kwargs
        )


class RateLimitError(Document360Error):
    """Rate limiting errors."""
    
    def __init__(
        self,
        message: str,
        response: Optional[HttpResponse] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            message,
            response=response,
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.LOW,
            retryable=True,
            **kwargs
        )
        self.retry_after = retry_after


class NotFoundError(Document360Error):
    """Resource not found errors."""
    
    def __init__(self, message: str, resource_id: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.MEDIUM,
            retryable=False,
            context={"resource_id": resource_id} if resource_id else None,
            **kwargs
        )


class ValidationError(Document360Error):
    """Input validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            retryable=False,
            context={"field": field, "value": value} if field else None,
            **kwargs
        )


class ServerError(Document360Error):
    """Server-side errors (5xx)."""
    
    def __init__(self, message: str, response: Optional[HttpResponse] = None, **kwargs):
        super().__init__(
            message,
            response=response,
            category=ErrorCategory.SERVER_ERROR,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            **kwargs
        )


class NetworkError(Document360Error):
    """Network connectivity errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.LOW,
            retryable=True,
            **kwargs
        )


class ErrorHandler:
    """
    Centralized error handler for API operations.
    
    Provides error classification, retry strategy determination,
    and comprehensive error analysis for robust error handling.
    """
    
    @staticmethod
    def classify_error(response: Optional[HttpResponse], exception: Optional[Exception] = None) -> Document360Error:
        """
        Classify an error based on response and exception.
        
        Args:
            response: HTTP response if available
            exception: Exception that occurred
            
        Returns:
            Classified Document360Error
        """
        if not response and not exception:
            return ApiError("Unknown API error")
        
        # Handle network/connection errors
        if exception and not response:
            error_str = str(exception).lower()
            if any(keyword in error_str for keyword in ["timeout", "connection", "network"]):
                return NetworkError(f"Network error: {exception}")
            return ApiError(f"Request failed: {exception}")
        
        # Handle HTTP response errors
        if response:
            status_code = response.status_code
            error_message = f"API request failed with status {status_code}"
            
            # Add response body context if available
            if response.json_data and isinstance(response.json_data, dict):
                error_detail = response.json_data.get("error", response.json_data.get("message"))
                if error_detail:
                    error_message = f"{error_message}: {error_detail}"
            elif response.text:
                error_message = f"{error_message}: {response.text[:200]}"
            
            # Classify by status code
            if status_code == 401:
                return AuthenticationError("Invalid or expired API token", response)
            elif status_code == 403:
                return AuthenticationError("Insufficient permissions", response)
            elif status_code == 404:
                resource_id = None
                if response.json_data and isinstance(response.json_data, dict):
                    resource_id = response.json_data.get("resource_id")
                return NotFoundError("Resource not found", resource_id=resource_id, response=response)
            elif status_code == 422:
                field = None
                value = None
                if response.json_data and isinstance(response.json_data, dict):
                    field = response.json_data.get("field")
                    value = response.json_data.get("value")
                return ValidationError("Validation failed", field=field, value=value, response=response)
            elif status_code == 429:
                retry_after = None
                if "retry-after" in response.headers:
                    try:
                        retry_after = int(response.headers["retry-after"])
                    except (ValueError, KeyError):
                        pass
                return RateLimitError("Rate limit exceeded", response=response, retry_after=retry_after)
            elif 500 <= status_code < 600:
                return ServerError(error_message, response)
            elif 400 <= status_code < 500:
                return ApiError(error_message, response)
            else:
                return ApiError(error_message, response)
        
        # Fallback for unknown errors
        return ApiError(f"Unexpected error: {exception}")
    
    @staticmethod
    def should_retry(error: Document360Error, attempt: int, max_attempts: int) -> bool:
        """
        Determine if an operation should be retried.
        
        Args:
            error: The error that occurred
            attempt: Current attempt number (1-based)
            max_attempts: Maximum number of attempts
            
        Returns:
            Whether to retry the operation
        """
        if attempt >= max_attempts:
            return False
        
        if not error.retryable:
            return False
        
        # Different retry strategies based on error category
        if error.category == ErrorCategory.RATE_LIMIT:
            return attempt <= 3  # Retry rate limits up to 3 times
        elif error.category == ErrorCategory.SERVER_ERROR:
            return attempt <= 2  # Retry server errors up to 2 times
        elif error.category == ErrorCategory.NETWORK:
            return attempt <= 3  # Retry network errors up to 3 times
        elif error.severity == ErrorSeverity.LOW:
            return attempt <= 3  # Retry low severity errors
        elif error.severity == ErrorSeverity.MEDIUM:
            return attempt <= 2  # Limited retries for medium severity
        else:
            return False  # No retries for high/critical severity
    
    @staticmethod
    def get_retry_delay(error: Document360Error, attempt: int) -> float:
        """
        Calculate retry delay based on error type and attempt.
        
        Args:
            error: The error that occurred
            attempt: Current attempt number (1-based)
            
        Returns:
            Delay in seconds before retry
        """
        if error.category == ErrorCategory.RATE_LIMIT:
            if isinstance(error, RateLimitError) and error.retry_after:
                return float(error.retry_after)
            # Exponential backoff for rate limits
            return min(60, 2 ** attempt)
        elif error.category == ErrorCategory.SERVER_ERROR:
            # Exponential backoff for server errors
            return min(30, 1.5 ** attempt)
        elif error.category == ErrorCategory.NETWORK:
            # Linear backoff for network errors
            return min(10, attempt * 2)
        else:
            # Default exponential backoff
            return min(20, 2 ** (attempt - 1))
    
    @staticmethod
    def log_error(error: Document360Error, operation: str, attempt: int = 1) -> None:
        """
        Log error with appropriate level and context.
        
        Args:
            error: The error that occurred
            operation: Description of the operation that failed
            attempt: Current attempt number
        """
        from loguru import logger
        
        log_context = {
            "operation": operation,
            "error_category": error.category.value,
            "error_severity": error.severity.value,
            "retryable": error.retryable,
            "attempt": attempt,
        }
        
        # Add response context if available
        if error.response:
            log_context.update({
                "status_code": error.response.status_code,
                "url": error.response.url,
            })
        
        # Add custom context
        log_context.update(error.context)
        
        # Log at appropriate level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logger.error(f"Critical error in {operation}: {error}", **log_context)
        elif error.severity == ErrorSeverity.HIGH:
            logger.warning(f"High severity error in {operation}: {error}", **log_context)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"Medium severity error in {operation}: {error}", **log_context)
        else:
            logger.info(f"Low severity error in {operation}: {error}", **log_context)