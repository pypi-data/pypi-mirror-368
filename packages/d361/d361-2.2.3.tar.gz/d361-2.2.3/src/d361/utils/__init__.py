# this_file: external/int_folders/d361/src/d361/utils/__init__.py
"""
Utils package - Common utilities and infrastructure components.

This package contains shared utilities used across the d361 library,
including logging, performance optimization, and helper functions.
"""

from .logging import (
    LogLevel,
    LogFormat,
    LogContext,
    LoggingManager,
    LoggingConfig,
    LogHandlerConfig,
    get_logging_manager,
    get_logger,
    setup_logging,
    setup_development_logging,
    setup_production_logging,
    set_correlation_id,
    set_user_id,
    set_request_id,
    clear_log_context,
)

from .dependency_injection import (
    ServiceLifecycle,
    ServiceContainer,
    ServiceDescriptor,
    ServiceScope,
    ServiceError,
    ServiceNotFoundError,
    CircularDependencyError,
    ServiceRegistrationError,
    injectable,
    get_container,
    set_container,
    resolve,
    register_singleton,
    register_transient,
    register_scoped,
)

from .performance import (
    CacheStrategy,
    BatchStrategy,
    CacheConfig,
    BatchConfig,
    PerformanceMetrics,
    AsyncCache,
    BatchProcessor,
    PerformanceOptimizer,
    get_optimizer,
    set_optimizer,
    async_cache,
    batch_processor,
    performance_monitor,
)

from .validation import (
    ValidationException,
    ValidationHelper,
    MigrationHelper,
    ValidatedBaseModel,
    validate_url_field,
    validate_email_field,
    validate_slug_field,
    validate_api_token_field,
    validate_function_inputs,
)

__all__ = [
    # Logging system
    "LogLevel",
    "LogFormat", 
    "LogContext",
    "LoggingManager",
    "LoggingConfig",
    "LogHandlerConfig",
    "get_logging_manager",
    "get_logger",
    "setup_logging",
    "setup_development_logging",
    "setup_production_logging",
    "set_correlation_id",
    "set_user_id",
    "set_request_id",
    "clear_log_context",
    
    # Dependency injection system
    "ServiceLifecycle",
    "ServiceContainer",
    "ServiceDescriptor",
    "ServiceScope",
    "ServiceError",
    "ServiceNotFoundError", 
    "CircularDependencyError",
    "ServiceRegistrationError",
    "injectable",
    "get_container",
    "set_container",
    "resolve",
    "register_singleton",
    "register_transient",
    "register_scoped",
    
    # Performance optimization
    "CacheStrategy",
    "BatchStrategy",
    "CacheConfig", 
    "BatchConfig",
    "PerformanceMetrics",
    "AsyncCache",
    "BatchProcessor",
    "PerformanceOptimizer",
    "get_optimizer",
    "set_optimizer",
    "async_cache",
    "batch_processor",
    "performance_monitor",
    
    # Validation and migration
    "ValidationException",
    "ValidationHelper",
    "MigrationHelper",
    "ValidatedBaseModel",
    "validate_url_field",
    "validate_email_field", 
    "validate_slug_field",
    "validate_api_token_field",
    "validate_function_inputs",
]