# this_file: external/int_folders/d361/src/d361/__init__.py
"""
d361 - Document360 Unified Toolkit

A comprehensive Python library for interacting with Document360 documentation platforms.
Built on hexagonal architecture principles with support for API integration, offline 
archive processing, web scraping, and plugin-based content conversion.

Key Features:
- Multi-provider data access (API, archives, web scraping)
- Enterprise-grade API client with token rotation and rate limiting
- Plugin-based content conversion system
- Modern CLI with rich terminal output
- Comprehensive testing and observability

Examples:
    >>> from d361 import MockProvider
    >>> provider = MockProvider()
    >>> articles = await provider.list_articles()
    
    >>> from d361 import PluginManager
    >>> pm = PluginManager()
    >>> converted = pm.convert(content, "html", "markdown")
"""

from importlib.metadata import PackageNotFoundError, version

# Version information
try:
    __version__ = version("d361")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

# Core models and interfaces
from .core.models import Article, Category, ProjectVersion, PublishStatus, ContentType
from .core.interfaces import DataProvider, ConverterPlugin, ConvertedContent
from .core.transformers import ModelTransformer

# HTTP client
from .http import UnifiedHttpClient, create_http_client, HttpResponse, RetryConfig

# API client
from .api import (
    Document360ApiClient,
    ApiConfig,
    TokenManager,
    TokenStats,
    RateLimiter,
    BulkOperationManager,
    BulkOperationConfig,
    SmartBulkProcessor,
    OperationType,
    OperationRequest,
    BulkOperationResult,
    ChunkedDownloader,
    DownloadConfig,
    DownloadStatus,
    ChunkStatus,
    DownloadChunk,
    DownloadProgress,
    DownloadState,
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitState,
    CircuitMetrics,
    CircuitBreakerRegistry,
    circuit_breaker,
    get_circuit_breaker,
    get_registry,
    DataSyncManager,
    SyncConfig,
    SyncStrategy,
    DeduplicationStrategy,
    ContentFingerprint,
    ChangeRecord,
    ChangeType,
    SyncState,
    ApiMetrics,
    MetricsConfig,
    MetricType,
    MetricPoint,
    MetricSeries,
    TimeWindow,
    get_metrics,
    configure_metrics,
    Document360Error,
    ApiError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError as ApiValidationError,
    ServerError,
    ErrorHandler,
    OpenApiIntegration,
    OpenApiConfig,
    OpenApiSpec,
    ModelGenerator,
    ModelGenerationConfig,
    GenerationResult,
    generate_models_cli,
    ApiUpdater,
    ApiUpdaterConfig,
    UpdateEvent,
    UpdateTrigger,
    UpdateStatus,
    create_updater,
    run_one_time_update,
)

# Archive processing
from .archive import (
    ArchiveParser,
    ArchiveParserConfig,
    ArchiveMetadata,
    ParsedArchive,
    SqliteCache,
    CacheConfig,
    CacheEntry,
    CacheStats,
    ArchiveSchema,
    create_archive_schema,
    migrate_archive_schema,
)

# Web scraping and content processing
from .scraping import (
    Document360Scraper,
    ScrapingConfig,
    ScrapedPage,
    ScrapingSession,
    BrowserType,
    ScrapingMode,
    UserAgent,
    ContentExtractor,
    ExtractionConfig,
    ExtractedContent,
    ContentBlock,
    ContentType as ScrapingContentType,
    ExtractionQuality,
    MarkdownConverter,
    ConversionConfig,
    ConversionResult,
    ConversionStats,
    MarkdownStyle,
    LinkHandling,
    Document360MarkdownConverter,
    ContentDeduplicator,
    DeduplicationConfig,
    DuplicateStatus,
    SimilarityScore,
    SimilarityAlgorithm,
    DuplicateGroup,
)

# Providers
from .providers import ApiProvider, ArchiveProvider, HybridProvider, MockProvider

# Plugin system
from .plugins import PluginManager

# Configuration and secrets management
from .config import (
    Environment,
    LogLevel as ConfigLogLevel,
    CacheEvictionPolicy,
    SecretProvider,
    SecretType,
    AppConfig,
    ApiConfig as ConfigApiConfig,
    ArchiveConfig as ConfigArchiveConfig,
    ScrapingConfig as ConfigScrapingConfig,
    CacheConfig as ConfigCacheConfig,
    MonitoringConfig,
    SecurityConfig,
    EnvironmentLoader,
    ConfigFileHandler,
    SecretMetadata,
    SecretValue,
    SecretsProvider,
    EnvironmentSecretsProvider,
    LocalFileSecretsProvider,
    HashiCorpVaultProvider,
    SecretsManager,
    PROVIDER_REGISTRY,
    create_secrets_provider,
    ConfigLoader,
    ConfigValidator,
    get_config,
    set_config,
    reset_config,
    get_secrets_manager,
    set_secrets_manager,
    reset_secrets_manager,
    get_config_loader,
    set_config_loader,
    reset_config_loader,
)

# MkDocs export functionality
from .mkdocs import (
    MkDocsExporter,
    ConfigGenerator,
    NavigationBuilder,
    ThemeOptimizer,
    MarkdownProcessor,
    ContentEnhancer,
    CrossReferenceResolver,
    LinkReference,
    AnchorReference,
    AssetManager,
    AssetReference,
    OptimizationResult,
)

# Utilities and infrastructure
from .utils import (
    LoggingManager,
    LogLevel,
    LogFormat,
    LogContext,
    get_logging_manager,
    get_logger,
    setup_logging,
    setup_development_logging,
    setup_production_logging,
    ServiceLifecycle,
    ServiceContainer,
    injectable,
    get_container,
    resolve,
    register_singleton,
    register_transient,
    register_scoped,
    PerformanceOptimizer,
    async_cache,
    batch_processor,
    performance_monitor,
    get_optimizer,
    ValidationHelper,
    ValidatedBaseModel,
    validate_function_inputs,
)

__all__ = [
    # Version
    "__version__",
    
    # Core models
    "Article",
    "Category", 
    "ProjectVersion",
    "PublishStatus",
    "ContentType",
    
    # Core interfaces
    "DataProvider",
    "ConverterPlugin", 
    "ConvertedContent",
    
    # Transformers
    "ModelTransformer",
    
    # HTTP client
    "UnifiedHttpClient",
    "create_http_client",
    "HttpResponse",
    "RetryConfig",
    
    # API client
    "Document360ApiClient",
    "ApiConfig", 
    "TokenManager",
    "TokenStats",
    "RateLimiter",
    "BulkOperationManager",
    "BulkOperationConfig",
    "SmartBulkProcessor", 
    "OperationType",
    "OperationRequest",
    "BulkOperationResult",
    "ChunkedDownloader",
    "DownloadConfig",
    "DownloadStatus",
    "ChunkStatus", 
    "DownloadChunk",
    "DownloadProgress",
    "DownloadState",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerError",
    "CircuitState",
    "CircuitMetrics",
    "CircuitBreakerRegistry",
    "circuit_breaker",
    "get_circuit_breaker",
    "get_registry",
    "DataSyncManager",
    "SyncConfig",
    "SyncStrategy",
    "DeduplicationStrategy",
    "ContentFingerprint",
    "ChangeRecord",
    "ChangeType",
    "SyncState",
    "ApiMetrics",
    "MetricsConfig",
    "MetricType",
    "MetricPoint",
    "MetricSeries",
    "TimeWindow",
    "get_metrics",
    "configure_metrics",
    "Document360Error",
    "ApiError",
    "AuthenticationError", 
    "RateLimitError",
    "NotFoundError",
    "ApiValidationError",
    "ServerError",
    "ErrorHandler",
    "OpenApiIntegration",
    "OpenApiConfig", 
    "OpenApiSpec",
    "ModelGenerator",
    "ModelGenerationConfig",
    "GenerationResult", 
    "generate_models_cli",
    "ApiUpdater",
    "ApiUpdaterConfig",
    "UpdateEvent",
    "UpdateTrigger", 
    "UpdateStatus",
    "create_updater",
    "run_one_time_update",
    
    # Archive processing
    "ArchiveParser",
    "ArchiveParserConfig",
    "ArchiveMetadata", 
    "ParsedArchive",
    "SqliteCache",
    "CacheConfig",
    "CacheEntry",
    "CacheStats",
    "ArchiveSchema",
    "create_archive_schema",
    "migrate_archive_schema",
    
    # Web scraping and content processing
    "Document360Scraper",
    "ScrapingConfig",
    "ScrapedPage",
    "ScrapingSession",
    "BrowserType",
    "ScrapingMode",
    "UserAgent",
    "ContentExtractor",
    "ExtractionConfig",
    "ExtractedContent",
    "ContentBlock",
    "ScrapingContentType",
    "ExtractionQuality",
    "MarkdownConverter",
    "ConversionConfig",
    "ConversionResult",
    "ConversionStats",
    "MarkdownStyle",
    "LinkHandling",
    "Document360MarkdownConverter",
    "ContentDeduplicator",
    "DeduplicationConfig",
    "DuplicateStatus",
    "SimilarityScore",
    "SimilarityAlgorithm",
    "DuplicateGroup",
    
    # Providers
    "ApiProvider",
    "ArchiveProvider",
    "HybridProvider", 
    "MockProvider",
    
    # Plugin system
    "PluginManager",
    
    # Configuration and secrets management
    "Environment",
    "ConfigLogLevel",
    "CacheEvictionPolicy",
    "SecretProvider",
    "SecretType",
    "AppConfig",
    "ConfigApiConfig",
    "ConfigArchiveConfig",
    "ConfigScrapingConfig",
    "ConfigCacheConfig",
    "MonitoringConfig",
    "SecurityConfig",
    "EnvironmentLoader",
    "ConfigFileHandler",
    "SecretMetadata",
    "SecretValue",
    "SecretsProvider",
    "EnvironmentSecretsProvider",
    "LocalFileSecretsProvider",
    "HashiCorpVaultProvider",
    "SecretsManager",
    "PROVIDER_REGISTRY",
    "create_secrets_provider",
    "ConfigLoader",
    "ConfigValidator",
    "get_config",
    "set_config",
    "reset_config",
    "get_secrets_manager",
    "set_secrets_manager",
    "reset_secrets_manager",
    "get_config_loader",
    "set_config_loader",
    "reset_config_loader",
    
    # Logging and utilities
    "LoggingManager",
    "LogLevel",
    "LogFormat", 
    "LogContext",
    "get_logging_manager",
    "get_logger",
    "setup_logging",
    "setup_development_logging",
    "setup_production_logging",
    
    # Dependency injection
    "ServiceLifecycle",
    "ServiceContainer", 
    "injectable",
    "get_container",
    "resolve",
    "register_singleton",
    "register_transient",
    "register_scoped",
    
    # Performance optimization
    "PerformanceOptimizer",
    "async_cache",
    "batch_processor", 
    "performance_monitor",
    "get_optimizer",
    
    # Validation and migration
    "ValidationHelper",
    "ValidatedBaseModel",
    "validate_function_inputs",
    
    # MkDocs export functionality
    "MkDocsExporter",
    "ConfigGenerator", 
    "NavigationBuilder",
    "ThemeOptimizer",
    "MarkdownProcessor",
    "ContentEnhancer",
    "CrossReferenceResolver",
    "LinkReference",
    "AnchorReference", 
    "AssetManager",
    "AssetReference",
    "OptimizationResult",
]
