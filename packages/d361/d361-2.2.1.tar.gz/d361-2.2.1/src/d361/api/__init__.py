# this_file: external/int_folders/d361/src/d361/api/__init__.py
"""
API package - Document360 API client and related utilities.

This package contains the enterprise-grade Document360 API client with
token management, rate limiting, and advanced features for robust
API interactions.
"""

from .client import Document360ApiClient, ApiConfig
from .errors import ErrorHandler
from .token_manager import TokenManager, TokenStats, RateLimiter
from .bulk_operations import (
    BulkOperationManager,
    BulkOperationConfig,
    SmartBulkProcessor,
    OperationType,
    OperationRequest,
    BulkOperationResult,
)
from .chunked_download import (
    ChunkedDownloader,
    DownloadConfig,
    DownloadStatus,
    ChunkStatus,
    DownloadChunk,
    DownloadProgress,
    DownloadState,
)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
    CircuitMetrics,
    CircuitBreakerRegistry,
    circuit_breaker,
    get_circuit_breaker,
    get_registry,
)
from .data_sync import (
    DataSyncManager,
    SyncConfig,
    SyncStrategy,
    DeduplicationStrategy,
    ContentFingerprint,
    ChangeRecord,
    ChangeType,
    SyncState,
)
from .metrics import (
    ApiMetrics,
    MetricsConfig,
    MetricType,
    MetricPoint,
    MetricSeries,
    TimeWindow,
    get_metrics,
    configure_metrics,
)
from .errors import (
    Document360Error,
    ApiError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)
from .openapi_integration import (
    OpenApiIntegration,
    OpenApiConfig,
    OpenApiSpec,
)
from .generate_models import (
    ModelGenerator,
    ModelGenerationConfig,
    GenerationResult,
    generate_models_cli,
)
from .api_updater import (
    ApiUpdater,
    ApiUpdaterConfig,
    UpdateEvent,
    UpdateTrigger,
    UpdateStatus,
    create_updater,
    run_one_time_update,
)

__all__ = [
    # Main API client
    "Document360ApiClient",
    "ApiConfig",
    
    # Token management
    "TokenManager",
    "TokenStats", 
    "RateLimiter",
    
    # Bulk operations
    "BulkOperationManager",
    "BulkOperationConfig",
    "SmartBulkProcessor",
    "OperationType",
    "OperationRequest", 
    "BulkOperationResult",
    
    # Chunked downloads
    "ChunkedDownloader",
    "DownloadConfig",
    "DownloadStatus",
    "ChunkStatus",
    "DownloadChunk",
    "DownloadProgress",
    "DownloadState",
    
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerError",
    "CircuitState",
    "CircuitMetrics",
    "CircuitBreakerRegistry",
    "circuit_breaker",
    "get_circuit_breaker",
    "get_registry",
    
    # Data synchronization
    "DataSyncManager",
    "SyncConfig",
    "SyncStrategy",
    "DeduplicationStrategy",
    "ContentFingerprint",
    "ChangeRecord",
    "ChangeType",
    "SyncState",
    
    # Metrics and observability
    "ApiMetrics",
    "MetricsConfig",
    "MetricType",
    "MetricPoint",
    "MetricSeries",
    "TimeWindow",
    "get_metrics",
    "configure_metrics",
    
    # Error handling
    "Document360Error",
    "ApiError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "ErrorHandler",
    
    # OpenAPI integration
    "OpenApiIntegration",
    "OpenApiConfig",
    "OpenApiSpec",
    
    # Model generation
    "ModelGenerator",
    "ModelGenerationConfig", 
    "GenerationResult",
    "generate_models_cli",
    
    # API updater
    "ApiUpdater",
    "ApiUpdaterConfig",
    "UpdateEvent",
    "UpdateTrigger",
    "UpdateStatus",
    "create_updater",
    "run_one_time_update",
]