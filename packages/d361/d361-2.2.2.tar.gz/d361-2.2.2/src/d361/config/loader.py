# this_file: external/int_folders/d361/src/d361/config/loader.py
"""
Configuration orchestration with hierarchical loading and validation.

This module provides the ConfigLoader class that coordinates configuration
loading from files, environment variables, and secrets with comprehensive
validation and helpful error reporting.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from datetime import datetime

from loguru import logger
from pydantic import ValidationError

from .schema import AppConfig, Environment
from .environment import EnvironmentLoader
from .secrets_manager import SecretsManager
from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class ConfigValidator:
    """
    Configuration validator for production-specific rules.
    
    This class enforces production-ready configuration settings and provides
    helpful error messages for common misconfigurations.
    """
    
    def __init__(self, environment: Environment):
        """
        Initialize configuration validator.
        
        Args:
            environment: Target environment for validation
        """
        self.environment = environment
        self.validation_rules: List[Callable[[AppConfig], List[str]]] = []
        
        # Add default validation rules
        self._add_default_rules()
    
    def _add_default_rules(self) -> None:
        """Add default validation rules."""
        self.validation_rules.extend([
            self._validate_production_debug,
            self._validate_production_secrets,
            self._validate_production_monitoring,
            self._validate_production_security,
            self._validate_resource_limits,
            self._validate_network_settings,
            self._validate_database_settings
        ])
    
    def _validate_production_debug(self, config: AppConfig) -> List[str]:
        """Validate debug settings for production."""
        issues = []
        
        if self.environment == Environment.PRODUCTION:
            if config.debug:
                issues.append("Debug mode should be disabled in production environment")
            
            if config.monitoring.log_level.value in ["TRACE", "DEBUG"]:
                issues.append(f"Log level '{config.monitoring.log_level}' too verbose for production")
        
        return issues
    
    def _validate_production_secrets(self, config: AppConfig) -> List[str]:
        """Validate secrets configuration for production."""
        issues = []
        
        if self.environment == Environment.PRODUCTION:
            # Check API tokens
            if not config.api.api_tokens:
                issues.append("API tokens are required in production environment")
            
            # Check secrets provider
            if config.security.secrets_provider.value == "environment":
                issues.append("Consider using a dedicated secret manager (Vault, AWS Secrets Manager) in production instead of environment variables")
            
            # Check encryption settings
            if not config.security.encryption_key_path:
                issues.append("Encryption key path should be configured in production")
        
        return issues
    
    def _validate_production_monitoring(self, config: AppConfig) -> List[str]:
        """Validate monitoring settings for production."""
        issues = []
        
        if self.environment == Environment.PRODUCTION:
            if not config.monitoring.metrics_enabled:
                issues.append("Metrics collection should be enabled in production")
            
            if not config.monitoring.health_check_enabled:
                issues.append("Health checks should be enabled in production")
            
            if not config.monitoring.alerting_enabled:
                issues.append("Alerting should be enabled in production")
            
            if config.monitoring.alerting_enabled and not config.monitoring.alert_webhook_url:
                issues.append("Alert webhook URL is required when alerting is enabled")
        
        return issues
    
    def _validate_production_security(self, config: AppConfig) -> List[str]:
        """Validate security settings for production."""
        issues = []
        
        if self.environment == Environment.PRODUCTION:
            if not config.security.security_headers_enabled:
                issues.append("Security headers should be enabled in production")
            
            if not config.security.rate_limiting_enabled:
                issues.append("Rate limiting should be enabled in production")
            
            if config.security.cors_enabled and not config.security.cors_origins:
                issues.append("CORS origins must be specified when CORS is enabled")
        
        return issues
    
    def _validate_resource_limits(self, config: AppConfig) -> List[str]:
        """Validate resource limit settings."""
        issues = []
        
        # Check cache size limits
        total_cache_mb = config.cache.max_disk_size_mb + config.archive.max_extracted_size_mb
        if total_cache_mb > 50000:  # 50GB
            issues.append(f"Total cache size ({total_cache_mb}MB) may be excessive and cause disk space issues")
        
        # Check memory limits
        if config.cache.max_memory_mb > 4096:  # 4GB
            issues.append(f"Memory cache size ({config.cache.max_memory_mb}MB) may be too large")
        
        # Check concurrent operations
        if config.scraping.concurrent_pages > 20:
            issues.append(f"Concurrent pages limit ({config.scraping.concurrent_pages}) may overwhelm target servers")
        
        if config.api.bulk_concurrency > 50:
            issues.append(f"API bulk concurrency ({config.api.bulk_concurrency}) may exceed rate limits")
        
        return issues
    
    def _validate_network_settings(self, config: AppConfig) -> List[str]:
        """Validate network and timeout settings."""
        issues = []
        
        # Check timeout settings
        if config.api.timeout_seconds < 5:
            issues.append(f"API timeout ({config.api.timeout_seconds}s) may be too short for reliable operations")
        
        if config.scraping.timeout_seconds > 300:  # 5 minutes
            issues.append(f"Scraping timeout ({config.scraping.timeout_seconds}s) may be excessive")
        
        # Check port conflicts
        ports_used = set()
        if config.monitoring.metrics_enabled:
            if config.monitoring.metrics_port in ports_used:
                issues.append(f"Port conflict: metrics port {config.monitoring.metrics_port}")
            ports_used.add(config.monitoring.metrics_port)
        
        if config.monitoring.health_check_enabled:
            if config.monitoring.health_check_port in ports_used:
                issues.append(f"Port conflict: health check port {config.monitoring.health_check_port}")
            ports_used.add(config.monitoring.health_check_port)
        
        return issues
    
    def _validate_database_settings(self, config: AppConfig) -> List[str]:
        """Validate database and storage settings."""
        issues = []
        
        # Check database settings
        if config.archive.connection_pool_size < 1:
            issues.append("Database connection pool size must be at least 1")
        
        if config.archive.vacuum_interval_hours > 168:  # 1 week
            issues.append(f"Database vacuum interval ({config.archive.vacuum_interval_hours}h) may be too long")
        
        # Check directory permissions and existence
        critical_dirs = [config.data_dir, config.logs_dir, config.cache.disk_cache_dir]
        for dir_path in critical_dirs:
            if not dir_path.exists():
                issues.append(f"Critical directory does not exist: {dir_path}")
            elif not os.access(dir_path, os.W_OK):
                issues.append(f"No write permission for critical directory: {dir_path}")
        
        return issues
    
    def validate(self, config: AppConfig) -> List[str]:
        """
        Validate configuration against all rules.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation issue messages
        """
        all_issues = []
        
        for rule in self.validation_rules:
            try:
                issues = rule(config)
                all_issues.extend(issues)
            except Exception as e:
                logger.warning(f"Validation rule {rule.__name__} failed: {e}")
                all_issues.append(f"Validation rule error in {rule.__name__}: {e}")
        
        # Add built-in AppConfig validation
        builtin_issues = config.validate_configuration()
        all_issues.extend(builtin_issues)
        
        return all_issues
    
    def add_rule(self, rule: Callable[[AppConfig], List[str]]) -> None:
        """
        Add a custom validation rule.
        
        Args:
            rule: Function that takes AppConfig and returns list of issue messages
        """
        self.validation_rules.append(rule)
        logger.debug(f"Added custom validation rule: {rule.__name__}")


class ConfigLoader:
    """
    Configuration orchestrator with hierarchical loading and validation.
    
    This class coordinates configuration loading from multiple sources with
    intelligent fallbacks, comprehensive validation, and helpful error reporting.
    """
    
    def __init__(
        self,
        base_config_dir: Optional[Path] = None,
        environment_override: Optional[str] = None,
        enable_secrets: bool = True,
        enable_hot_reload: bool = True
    ):
        """
        Initialize configuration loader.
        
        Args:
            base_config_dir: Base directory for configuration files
            environment_override: Override environment detection
            enable_secrets: Enable secrets management integration
            enable_hot_reload: Enable configuration hot-reloading
        """
        self.base_config_dir = base_config_dir or Path.cwd()
        self.environment_override = environment_override
        self.enable_secrets = enable_secrets
        self.enable_hot_reload = enable_hot_reload
        
        # Initialize components
        self.env_loader = EnvironmentLoader(base_config_dir, environment_override)
        self.secrets_manager: Optional[SecretsManager] = None
        self.validator: Optional[ConfigValidator] = None
        
        # State tracking
        self._current_config: Optional[AppConfig] = None
        self._loading_started_at: Optional[datetime] = None
        self._validation_cache: Dict[str, Tuple[datetime, List[str]]] = {}
        
        logger.debug(
            "ConfigLoader initialized",
            base_config_dir=str(self.base_config_dir),
            enable_secrets=enable_secrets,
            enable_hot_reload=enable_hot_reload
        )
    
    async def load_configuration(
        self,
        environment: Optional[Environment] = None,
        validate: bool = True,
        fail_on_validation_errors: bool = None
    ) -> AppConfig:
        """
        Load complete configuration with validation.
        
        Args:
            environment: Target environment (auto-detected if None)
            validate: Whether to run validation
            fail_on_validation_errors: Whether to fail on validation errors (defaults to True for production)
            
        Returns:
            Loaded and validated configuration
            
        Raises:
            Document360Error: If configuration loading or validation fails
        """
        self._loading_started_at = datetime.now()
        
        try:
            # Detect environment if not provided
            if environment is None:
                environment = self.env_loader.detect_environment()
            
            # Set default for fail_on_validation_errors
            if fail_on_validation_errors is None:
                fail_on_validation_errors = (environment == Environment.PRODUCTION)
            
            logger.info(f"Loading configuration for environment: {environment.value}")
            
            # Load base configuration from files and environment
            config = self.env_loader.load_configuration(environment)
            
            # Initialize secrets manager if enabled
            if self.enable_secrets:
                await self._initialize_secrets_manager(config.security)
                
                # Load secrets into configuration
                config = await self._inject_secrets(config)
            
            # Validate configuration
            if validate:
                validation_issues = await self._validate_configuration(config, fail_on_validation_errors)
                if validation_issues and fail_on_validation_errors:
                    raise Document360Error(
                        f"Configuration validation failed: {'; '.join(validation_issues)}",
                        category=ErrorCategory.CONFIGURATION,
                        severity=ErrorSeverity.CRITICAL
                    )
            
            # Start hot-reloading if enabled
            if self.enable_hot_reload and environment != Environment.PRODUCTION:
                await self._start_hot_reload(config)
            
            self._current_config = config
            
            loading_time = (datetime.now() - self._loading_started_at).total_seconds()
            logger.info(
                f"Configuration loaded successfully in {loading_time:.2f}s",
                environment=environment.value,
                validation_issues=len(validation_issues) if validate else 0
            )
            
            return config
            
        except Exception as e:
            if isinstance(e, Document360Error):
                raise
            
            raise Document360Error(
                f"Failed to load configuration: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
    
    async def _initialize_secrets_manager(self, security_config) -> None:
        """Initialize secrets manager."""
        if self.secrets_manager is None:
            self.secrets_manager = SecretsManager(security_config)
            await self.secrets_manager.initialize()
            logger.debug("Secrets manager initialized")
    
    async def _inject_secrets(self, config: AppConfig) -> AppConfig:
        """Inject secrets into configuration."""
        if not self.secrets_manager:
            return config
        
        # Dictionary to track secret injections
        config_dict = config.dict()
        
        # Try to load API tokens from secrets
        try:
            api_token_secret = await self.secrets_manager.get_secret("api_token")
            if api_token_secret.is_valid():
                config_dict["api"]["api_tokens"] = [api_token_secret.value]
                logger.debug("API token loaded from secrets manager")
        except Exception as e:
            logger.debug(f"No API token in secrets manager: {e}")
        
        # Try to load database URL from secrets
        try:
            db_secret = await self.secrets_manager.get_secret("database_url")
            if db_secret.is_valid():
                config_dict["archive"]["db_path"] = Path(db_secret.value)
                logger.debug("Database URL loaded from secrets manager")
        except Exception as e:
            logger.debug(f"No database URL in secrets manager: {e}")
        
        # Try to load encryption key from secrets
        try:
            encryption_secret = await self.secrets_manager.get_secret("encryption_key")
            if encryption_secret.is_valid():
                config_dict["security"]["encryption_key_path"] = Path(encryption_secret.value)
                logger.debug("Encryption key loaded from secrets manager")
        except Exception as e:
            logger.debug(f"No encryption key in secrets manager: {e}")
        
        # Recreate config with injected secrets
        return AppConfig(**config_dict)
    
    async def _validate_configuration(
        self,
        config: AppConfig,
        fail_on_errors: bool
    ) -> List[str]:
        """Validate configuration."""
        # Initialize validator if needed
        if self.validator is None:
            self.validator = ConfigValidator(config.environment)
        
        # Check cache for recent validation
        config_hash = hash(str(config.dict()))
        cache_key = f"{config_hash}_{config.environment.value}"
        
        now = datetime.now()
        if cache_key in self._validation_cache:
            cached_time, cached_issues = self._validation_cache[cache_key]
            if (now - cached_time).total_seconds() < 300:  # 5 minutes
                logger.debug("Using cached validation results")
                return cached_issues
        
        # Run validation
        validation_issues = self.validator.validate(config)
        
        # Cache results
        self._validation_cache[cache_key] = (now, validation_issues)
        
        # Log validation results
        if validation_issues:
            log_level = "error" if fail_on_errors else "warning"
            getattr(logger, log_level)(
                f"Configuration validation issues ({len(validation_issues)}): {'; '.join(validation_issues)}"
            )
        else:
            logger.debug("Configuration validation passed")
        
        return validation_issues
    
    async def _start_hot_reload(self, config: AppConfig) -> None:
        """Start configuration hot-reloading."""
        if not self.enable_hot_reload:
            return
        
        try:
            self.env_loader.start_hot_reload(self._handle_config_reload)
            logger.debug("Configuration hot-reload started")
        except Exception as e:
            logger.warning(f"Failed to start configuration hot-reload: {e}")
    
    async def _handle_config_reload(self, new_config: AppConfig) -> None:
        """Handle configuration reload."""
        try:
            # Validate new configuration
            validation_issues = await self._validate_configuration(new_config, False)
            
            if validation_issues:
                logger.warning(f"New configuration has validation issues, keeping current config: {'; '.join(validation_issues)}")
                return
            
            # Update current configuration
            self._current_config = new_config
            logger.info("Configuration reloaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to handle configuration reload: {e}")
    
    async def get_current_config(self) -> Optional[AppConfig]:
        """Get the current configuration."""
        return self._current_config
    
    async def reload_configuration(
        self,
        validate: bool = True,
        fail_on_validation_errors: bool = None
    ) -> AppConfig:
        """
        Manually reload configuration.
        
        Args:
            validate: Whether to run validation
            fail_on_validation_errors: Whether to fail on validation errors
            
        Returns:
            Reloaded configuration
        """
        environment = self._current_config.environment if self._current_config else None
        return await self.load_configuration(environment, validate, fail_on_validation_errors)
    
    async def get_config_summary(self) -> Dict[str, Any]:
        """
        Get summary of configuration loading.
        
        Returns:
            Configuration summary information
        """
        base_summary = self.env_loader.get_config_summary()
        
        secrets_info = {}
        if self.secrets_manager:
            try:
                secrets_info = await self.secrets_manager.get_provider_info()
            except Exception as e:
                secrets_info = {"error": str(e)}
        
        return {
            **base_summary,
            "secrets_enabled": self.enable_secrets,
            "secrets_manager": secrets_info,
            "hot_reload_enabled": self.enable_hot_reload,
            "current_config_loaded": self._current_config is not None,
            "loading_started_at": self._loading_started_at.isoformat() if self._loading_started_at else None,
            "validation_cache_entries": len(self._validation_cache)
        }
    
    async def cleanup(self) -> None:
        """Cleanup configuration loader resources."""
        # Stop hot reload
        self.env_loader.stop_hot_reload()
        
        # Cleanup secrets manager
        if self.secrets_manager:
            await self.secrets_manager.cleanup()
        
        # Clear caches
        self._validation_cache.clear()
        self._current_config = None
        
        logger.debug("ConfigLoader cleaned up")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(
    base_config_dir: Optional[Path] = None,
    environment_override: Optional[str] = None
) -> ConfigLoader:
    """
    Get the global configuration loader instance.
    
    Args:
        base_config_dir: Base directory for configuration files (used only for first initialization)
        environment_override: Override environment detection (used only for first initialization)
        
    Returns:
        Global ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(base_config_dir, environment_override)
    return _config_loader


def set_config_loader(loader: ConfigLoader) -> None:
    """
    Set the global configuration loader instance.
    
    Args:
        loader: ConfigLoader instance to set as global
    """
    global _config_loader
    _config_loader = loader


def reset_config_loader() -> None:
    """Reset the global configuration loader instance."""
    global _config_loader
    _config_loader = None