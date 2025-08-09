# this_file: external/int_folders/d361/src/d361/config/schema.py
"""
Configuration schema definitions with comprehensive validation.

This module provides the main AppConfig class and nested configuration models
for all d361 components, with environment-specific settings, validation rules,
and secure defaults for production deployment.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from enum import Enum

from loguru import logger
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, field_validator, model_validator
except ImportError:
    # Fallback for Pydantic v1
    from pydantic import BaseSettings, Field
    from pydantic import validator as field_validator, root_validator as model_validator

from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class Environment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"  
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Logging levels."""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CacheEvictionPolicy(str, Enum):
    """Cache eviction policies."""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"
    SIZE = "size"


class SecretProvider(str, Enum):
    """Secret management providers."""
    LOCAL_FILE = "local_file"
    ENVIRONMENT = "environment"
    HASHICORP_VAULT = "vault"
    AWS_SECRETS_MANAGER = "aws_secrets"
    AZURE_KEY_VAULT = "azure_keyvault"


class ApiConfig(BaseSettings):
    """Configuration for API client operations."""
    
    # Connection settings
    base_url: str = Field(
        default="https://apidocs.document360.com",
        description="Base URL for Document360 API"
    )
    
    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts"
    )
    
    # Authentication
    api_tokens: List[str] = Field(
        default_factory=list,
        description="API tokens for authentication"
    )
    
    token_rotation_enabled: bool = Field(
        default=True,
        description="Enable automatic token rotation"
    )
    
    # Rate limiting
    requests_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Requests per minute limit"
    )
    
    burst_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Burst request limit"
    )
    
    # Circuit breaker
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker pattern"
    )
    
    failure_threshold: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Circuit breaker failure threshold"
    )
    
    recovery_timeout: int = Field(
        default=60,
        ge=10,
        le=600,
        description="Circuit breaker recovery timeout in seconds"
    )
    
    # Bulk operations
    bulk_batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Default batch size for bulk operations"
    )
    
    bulk_concurrency: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Concurrent bulk operations limit"
    )

    class Config:
        env_prefix = "D361_API_"
        case_sensitive = False


class ArchiveConfig(BaseSettings):
    """Configuration for archive processing operations."""
    
    # Storage paths
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".d361" / "cache" / "archives",
        description="Directory for archive cache"
    )
    
    temp_dir: Path = Field(
        default_factory=lambda: Path("/tmp") / "d361_archives",
        description="Temporary directory for archive extraction"
    )
    
    # Processing settings
    max_archive_size_mb: int = Field(
        default=500,
        ge=1,
        le=5000,
        description="Maximum archive size in MB"
    )
    
    max_extracted_size_mb: int = Field(
        default=2000,
        ge=10,
        le=10000,
        description="Maximum extracted content size in MB"
    )
    
    batch_size: int = Field(
        default=1000,
        ge=10,
        le=10000,
        description="Batch size for archive processing"
    )
    
    # Database settings
    db_path: Optional[Path] = Field(
        None,
        description="SQLite database path (auto-generated if None)"
    )
    
    enable_fts: bool = Field(
        default=True,
        description="Enable full-text search indexing"
    )
    
    vacuum_interval_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Database vacuum interval in hours"
    )
    
    # Performance settings
    connection_pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    
    cache_eviction_policy: CacheEvictionPolicy = Field(
        default=CacheEvictionPolicy.LRU,
        description="Cache eviction policy"
    )

    class Config:
        env_prefix = "D361_ARCHIVE_"
        case_sensitive = False

    @field_validator("cache_dir", "temp_dir", mode="before")
    def validate_paths(cls, v):
        """Validate and create directories if needed."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v


class ScrapingConfig(BaseSettings):
    """Configuration for web scraping operations."""
    
    # Browser settings
    browser_type: str = Field(
        default="chromium",
        description="Browser type (chromium, firefox, webkit)"
    )
    
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode"
    )
    
    user_data_dir: Optional[Path] = Field(
        None,
        description="Browser user data directory"
    )
    
    # Request settings
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Page load timeout in seconds"
    )
    
    delay_min_seconds: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Minimum delay between requests"
    )
    
    delay_max_seconds: float = Field(
        default=3.0,
        ge=0.5,
        le=20.0,
        description="Maximum delay between requests"
    )
    
    # Concurrency settings
    concurrent_pages: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Maximum concurrent pages"
    )
    
    max_requests_per_domain: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum requests per domain"
    )
    
    # Content settings
    max_content_length_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum content length in MB"
    )
    
    save_screenshots: bool = Field(
        default=False,
        description="Save page screenshots"
    )
    
    screenshot_dir: Optional[Path] = Field(
        None,
        description="Screenshot storage directory"
    )
    
    # Anti-detection settings
    randomize_user_agent: bool = Field(
        default=True,
        description="Randomize user agents"
    )
    
    dismiss_cookie_banners: bool = Field(
        default=True,
        description="Attempt to dismiss cookie banners"
    )
    
    respect_robots_txt: bool = Field(
        default=True,
        description="Respect robots.txt files"
    )

    class Config:
        env_prefix = "D361_SCRAPING_"
        case_sensitive = False


class CacheConfig(BaseSettings):
    """Configuration for caching operations."""
    
    # General cache settings
    enabled: bool = Field(
        default=True,
        description="Enable caching globally"
    )
    
    default_ttl_seconds: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Default TTL in seconds"
    )
    
    max_memory_mb: int = Field(
        default=256,
        ge=10,
        le=2048,
        description="Maximum memory cache size in MB"
    )
    
    # Disk cache settings
    disk_cache_enabled: bool = Field(
        default=True,
        description="Enable disk-based caching"
    )
    
    disk_cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".d361" / "cache" / "disk",
        description="Disk cache directory"
    )
    
    max_disk_size_mb: int = Field(
        default=1024,
        ge=50,
        le=10240,
        description="Maximum disk cache size in MB"
    )
    
    # Eviction policies
    eviction_policy: CacheEvictionPolicy = Field(
        default=CacheEvictionPolicy.LRU,
        description="Cache eviction policy"
    )
    
    cleanup_interval_seconds: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Cache cleanup interval in seconds"
    )
    
    # Performance settings
    compression_enabled: bool = Field(
        default=True,
        description="Enable cache data compression"
    )
    
    async_writes: bool = Field(
        default=True,
        description="Enable asynchronous cache writes"
    )

    class Config:
        env_prefix = "D361_CACHE_"
        case_sensitive = False

    @field_validator("disk_cache_dir", mode="before")
    def validate_disk_cache_dir(cls, v):
        """Validate and create cache directory."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v


class MonitoringConfig(BaseSettings):
    """Configuration for monitoring and observability."""
    
    # Logging settings
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Global log level"
    )
    
    log_format: str = Field(
        default="json",
        description="Log format (json, console, structured)"
    )
    
    log_file_path: Optional[Path] = Field(
        None,
        description="Log file path (stdout if None)"
    )
    
    log_rotation_size_mb: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Log file rotation size in MB"
    )
    
    log_retention_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Log retention period in days"
    )
    
    # Metrics settings
    metrics_enabled: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    
    metrics_port: int = Field(
        default=9090,
        ge=1024,
        le=65535,
        description="Metrics server port"
    )
    
    metrics_path: str = Field(
        default="/metrics",
        description="Metrics endpoint path"
    )
    
    # Health check settings
    health_check_enabled: bool = Field(
        default=True,
        description="Enable health check endpoint"
    )
    
    health_check_port: int = Field(
        default=8080,
        ge=1024,
        le=65535,
        description="Health check server port"
    )
    
    health_check_path: str = Field(
        default="/health",
        description="Health check endpoint path"
    )
    
    # Alerting settings
    alerting_enabled: bool = Field(
        default=False,
        description="Enable alerting (production only)"
    )
    
    alert_webhook_url: Optional[str] = Field(
        None,
        description="Webhook URL for alerts"
    )
    
    alert_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "error_rate": 0.05,
            "response_time_p95": 5000.0,
            "memory_usage": 0.8,
            "disk_usage": 0.9
        },
        description="Alert thresholds for various metrics"
    )

    class Config:
        env_prefix = "D361_MONITORING_"
        case_sensitive = False


class SecurityConfig(BaseSettings):
    """Configuration for security settings."""
    
    # Secrets management
    secrets_provider: SecretProvider = Field(
        default=SecretProvider.ENVIRONMENT,
        description="Secret management provider"
    )
    
    secrets_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific secret configuration"
    )
    
    # Encryption settings
    encryption_key_path: Optional[Path] = Field(
        None,
        description="Path to encryption key file"
    )
    
    encryption_algorithm: str = Field(
        default="AES-256-GCM",
        description="Encryption algorithm"
    )
    
    # Security headers
    security_headers_enabled: bool = Field(
        default=True,
        description="Enable security headers"
    )
    
    cors_enabled: bool = Field(
        default=False,
        description="Enable CORS headers"
    )
    
    cors_origins: List[str] = Field(
        default_factory=list,
        description="Allowed CORS origins"
    )
    
    # Rate limiting
    rate_limiting_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    
    rate_limit_requests_per_hour: int = Field(
        default=1000,
        ge=10,
        le=100000,
        description="Rate limit requests per hour"
    )
    
    # Input validation
    max_request_size_mb: int = Field(
        default=16,
        ge=1,
        le=100,
        description="Maximum request size in MB"
    )
    
    sanitize_inputs: bool = Field(
        default=True,
        description="Enable input sanitization"
    )

    class Config:
        env_prefix = "D361_SECURITY_"
        case_sensitive = False


class AppConfig(BaseSettings):
    """
    Main application configuration with comprehensive settings.
    
    This is the root configuration class that encompasses all d361 components
    with environment-specific settings, validation rules, and secure defaults
    for development, staging, and production deployments.
    """
    
    # Application metadata
    app_name: str = Field(
        default="d361",
        description="Application name"
    )
    
    version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Deployment environment"
    )
    
    debug: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    
    # Core directories
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".d361",
        description="Main data directory"
    )
    
    config_dir: Path = Field(
        default_factory=lambda: Path.home() / ".d361" / "config",
        description="Configuration files directory"
    )
    
    logs_dir: Path = Field(
        default_factory=lambda: Path.home() / ".d361" / "logs",
        description="Log files directory"
    )
    
    # Component configurations
    api: ApiConfig = Field(default_factory=ApiConfig)
    archive: ArchiveConfig = Field(default_factory=ArchiveConfig)
    scraping: ScrapingConfig = Field(default_factory=ScrapingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Feature flags
    features: Dict[str, bool] = Field(
        default_factory=lambda: {
            "api_client": True,
            "archive_processing": True,
            "web_scraping": True,
            "hybrid_provider": True,
            "metrics_collection": True,
            "health_checks": True
        },
        description="Feature toggle flags"
    )

    class Config:
        env_prefix = "D361_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        secrets_dir = None  # Will be set dynamically

    @field_validator("data_dir", "config_dir", "logs_dir", mode="before")
    def validate_and_create_directories(cls, v):
        """Validate and create application directories."""
        if isinstance(v, str):
            v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    @model_validator(mode="after")
    def validate_production_settings(self):
        """Validate production-specific settings."""
        if self.environment == Environment.PRODUCTION:
            # Production validation rules
            if self.debug:
                logger.warning("Debug mode is enabled in production - this is not recommended")
            
            # Ensure security settings are appropriate
            if self.security and self.security.secrets_provider == SecretProvider.ENVIRONMENT:
                logger.warning("Using environment variables for secrets in production - consider a dedicated secret manager")
            
            # Validate monitoring is enabled
            if self.monitoring:
                if not self.monitoring.metrics_enabled:
                    logger.warning("Metrics collection is disabled in production")
                if not self.monitoring.health_check_enabled:
                    logger.warning("Health checks are disabled in production")
        
        return self

    @model_validator(mode="after")  
    def validate_component_consistency(self):
        """Validate consistency across component configurations."""
        # Ensure cache directories are consistent
        if self.archive and self.cache:
            # Ensure archive cache is under main cache directory
            if not str(self.archive.cache_dir).startswith(str(self.cache.disk_cache_dir.parent)):
                logger.info("Archive cache directory is not under main cache directory")
        
        return self

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING

    def get_feature_flag(self, feature_name: str, default: bool = False) -> bool:
        """Get feature flag value with default fallback."""
        return self.features.get(feature_name, default)

    def validate_configuration(self) -> List[str]:
        """
        Validate the entire configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check required API tokens in production
        if self.is_production() and not self.api.api_tokens:
            issues.append("API tokens are required in production environment")
        
        # Check disk space requirements
        total_cache_mb = self.cache.max_disk_size_mb + self.archive.max_extracted_size_mb
        if total_cache_mb > 10000:  # 10GB
            issues.append(f"Total cache size ({total_cache_mb}MB) may be too large")
        
        # Check port conflicts
        ports_used = set()
        if self.monitoring.metrics_enabled:
            if self.monitoring.metrics_port in ports_used:
                issues.append(f"Port conflict: metrics port {self.monitoring.metrics_port} already used")
            ports_used.add(self.monitoring.metrics_port)
        
        if self.monitoring.health_check_enabled:
            if self.monitoring.health_check_port in ports_used:
                issues.append(f"Port conflict: health check port {self.monitoring.health_check_port} already used")
            ports_used.add(self.monitoring.health_check_port)
        
        # Validate scraping settings
        if self.scraping.delay_min_seconds > self.scraping.delay_max_seconds:
            issues.append("Scraping minimum delay cannot be greater than maximum delay")
        
        return issues

    def to_dict(self, exclude_secrets: bool = True) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Args:
            exclude_secrets: Whether to exclude sensitive information
            
        Returns:
            Configuration dictionary
        """
        config_dict = self.dict()
        
        if exclude_secrets:
            # Remove sensitive fields
            if "api" in config_dict and "api_tokens" in config_dict["api"]:
                config_dict["api"]["api_tokens"] = ["***"] * len(self.api.api_tokens)
            
            if "security" in config_dict:
                config_dict["security"].pop("secrets_config", None)
                config_dict["security"].pop("encryption_key_path", None)
        
        return config_dict

    @classmethod
    def load_from_file(cls, config_path: Path) -> AppConfig:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded configuration instance
            
        Raises:
            Document360Error: If configuration loading fails
        """
        try:
            if config_path.suffix.lower() == ".json":
                import json
                with open(config_path, "r") as f:
                    config_data = json.load(f)
                return cls(**config_data)
            elif config_path.suffix.lower() in [".yml", ".yaml"]:
                try:
                    import yaml
                    with open(config_path, "r") as f:
                        config_data = yaml.safe_load(f)
                    return cls(**config_data)
                except ImportError:
                    raise Document360Error(
                        "PyYAML is required to load YAML configuration files",
                        category=ErrorCategory.CONFIGURATION,
                        severity=ErrorSeverity.HIGH
                    )
            else:
                raise Document360Error(
                    f"Unsupported configuration file format: {config_path.suffix}",
                    category=ErrorCategory.CONFIGURATION,
                    severity=ErrorSeverity.HIGH
                )
        except Exception as e:
            raise Document360Error(
                f"Failed to load configuration from {config_path}: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )

    def save_to_file(self, config_path: Path, exclude_secrets: bool = True) -> None:
        """
        Save configuration to file.
        
        Args:
            config_path: Path where to save configuration
            exclude_secrets: Whether to exclude sensitive information
            
        Raises:
            Document360Error: If saving fails
        """
        try:
            config_dict = self.to_dict(exclude_secrets=exclude_secrets)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.suffix.lower() == ".json":
                import json
                with open(config_path, "w") as f:
                    json.dump(config_dict, f, indent=2, default=str)
            elif config_path.suffix.lower() in [".yml", ".yaml"]:
                try:
                    import yaml
                    with open(config_path, "w") as f:
                        yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                except ImportError:
                    raise Document360Error(
                        "PyYAML is required to save YAML configuration files",
                        category=ErrorCategory.CONFIGURATION,
                        severity=ErrorSeverity.HIGH
                    )
            else:
                raise Document360Error(
                    f"Unsupported configuration file format: {config_path.suffix}",
                    category=ErrorCategory.CONFIGURATION,
                    severity=ErrorSeverity.HIGH
                )
                
            logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            raise Document360Error(
                f"Failed to save configuration to {config_path}: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )


# Global configuration instance
_app_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Get the global configuration instance.
    
    Returns:
        Global AppConfig instance
    """
    global _app_config
    if _app_config is None:
        _app_config = AppConfig()
    return _app_config


def set_config(config: AppConfig) -> None:
    """
    Set the global configuration instance.
    
    Args:
        config: AppConfig instance to set as global
    """
    global _app_config
    _app_config = config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _app_config
    _app_config = None