# this_file: external/int_folders/d361/src/d361/config/__init__.py
"""
Configuration and secrets management package.

This package provides comprehensive configuration management with support for
multiple environments, secrets management, and security hardening for the d361 system.
"""

from .schema import (
    # Enums
    Environment,
    LogLevel,
    CacheEvictionPolicy,
    SecretProvider,
    
    # Configuration Models
    AppConfig,
    ApiConfig,
    ArchiveConfig,
    ScrapingConfig,
    CacheConfig,
    MonitoringConfig,
    SecurityConfig,
    
    # Global Configuration Functions
    get_config,
    set_config,
    reset_config,
)

from .environment import (
    # Environment Loading
    EnvironmentLoader,
    ConfigFileHandler,
)

from .secrets import (
    # Secret Types and Models
    SecretType,
    SecretMetadata,
    SecretValue,
    
    # Provider Base Class
    SecretsProvider,
    
    # Concrete Providers
    EnvironmentSecretsProvider,
    LocalFileSecretsProvider,
    HashiCorpVaultProvider,
    
    # Provider Registry
    PROVIDER_REGISTRY,
    create_secrets_provider,
)

from .secrets_manager import (
    # Secrets Management
    SecretsManager,
    
    # Global Functions
    get_secrets_manager,
    set_secrets_manager,
    reset_secrets_manager,
)

from .loader import (
    # Configuration Loading
    ConfigLoader,
    ConfigValidator,
    
    # Global Functions
    get_config_loader,
    set_config_loader,
    reset_config_loader,
)

# Public API
__all__ = [
    # Enums
    "Environment",
    "LogLevel", 
    "CacheEvictionPolicy",
    "SecretProvider",
    "SecretType",
    
    # Configuration Models
    "AppConfig",
    "ApiConfig", 
    "ArchiveConfig",
    "ScrapingConfig",
    "CacheConfig",
    "MonitoringConfig",
    "SecurityConfig",
    
    # Environment Loading
    "EnvironmentLoader",
    "ConfigFileHandler",
    
    # Secrets Management
    "SecretMetadata",
    "SecretValue",
    "SecretsProvider",
    "EnvironmentSecretsProvider",
    "LocalFileSecretsProvider", 
    "HashiCorpVaultProvider",
    "SecretsManager",
    "PROVIDER_REGISTRY",
    "create_secrets_provider",
    
    # Configuration Loading & Validation
    "ConfigLoader",
    "ConfigValidator",
    
    # Global Functions
    "get_config",
    "set_config",
    "reset_config",
    "get_secrets_manager",
    "set_secrets_manager", 
    "reset_secrets_manager",
    "get_config_loader",
    "set_config_loader",
    "reset_config_loader",
]