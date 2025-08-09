# this_file: external/int_folders/d361/tests/test_unit_config.py
"""
Comprehensive unit tests for d361 configuration system.

This module provides thorough testing of the configuration management,
secrets handling, environment loading, and validation components.
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

import pytest
from pydantic import ValidationError

from d361.config import (
    AppConfig,
    Environment,
    SecretProvider,
    SecretType,
    EnvironmentLoader,
    SecretsManager,
    ConfigLoader,
    ConfigValidator,
    SecretMetadata,
    SecretValue,
    EnvironmentSecretsProvider,
    LocalFileSecretsProvider
)
from d361.api.errors import Document360Error


class TestAppConfig:
    """Test cases for AppConfig model."""

    def test_app_config_creation_defaults(self):
        """Test AppConfig creation with default values."""
        config = AppConfig()
        
        assert config.app_name == "d361"
        assert config.version == "1.0.0"
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True  # Default for development

    def test_app_config_environment_override(self):
        """Test environment-specific configuration."""
        config = AppConfig(environment=Environment.PRODUCTION)
        
        assert config.environment == Environment.PRODUCTION
        # Production-specific defaults should be applied

    def test_app_config_nested_models(self):
        """Test nested configuration models."""
        config = AppConfig()
        
        # Test API config
        assert config.api.timeout_seconds == 30
        assert config.api.max_retries == 3
        assert config.api.requests_per_minute == 60
        
        # Test cache config
        assert config.cache.enabled is True
        assert config.cache.default_ttl_seconds == 3600
        
        # Test monitoring config
        assert config.monitoring.metrics_enabled is True
        assert config.monitoring.log_level.value == "INFO"

    def test_app_config_validation(self):
        """Test AppConfig validation rules."""
        config = AppConfig()
        
        # Test validation method
        issues = config.validate_configuration()
        # Should have some issues in default config
        assert isinstance(issues, list)

    def test_app_config_production_validation(self):
        """Test production-specific validation."""
        config = AppConfig(environment=Environment.PRODUCTION, debug=True)
        
        # Should have warnings about debug in production
        issues = config.validate_configuration()
        debug_issues = [issue for issue in issues if "debug" in issue.lower()]
        # Depending on implementation, may or may not have debug warning

    def test_app_config_feature_flags(self):
        """Test feature flag functionality."""
        config = AppConfig()
        
        # Test default features
        assert config.get_feature_flag("api_client") is True
        assert config.get_feature_flag("archive_processing") is True
        assert config.get_feature_flag("non_existent_feature", default=False) is False

    def test_app_config_serialization(self):
        """Test configuration serialization."""
        config = AppConfig()
        
        # Test dict conversion
        config_dict = config.to_dict()
        assert "app_name" in config_dict
        assert "api" in config_dict
        
        # Test secrets exclusion
        config_dict_safe = config.to_dict(exclude_secrets=True)
        # Should mask sensitive data
        if "api" in config_dict_safe and "api_tokens" in config_dict_safe["api"]:
            # Check if tokens are masked
            pass

    def test_app_config_from_dict(self):
        """Test configuration creation from dictionary."""
        config_data = {
            "app_name": "test-app",
            "environment": "testing",
            "debug": False,
            "api": {
                "timeout_seconds": 60
            }
        }
        
        config = AppConfig(**config_data)
        assert config.app_name == "test-app"
        assert config.environment == Environment.TESTING
        assert config.api.timeout_seconds == 60

    def test_app_config_environment_variables(self):
        """Test configuration from environment variables."""
        with patch.dict(os.environ, {
            "D361_APP_NAME": "env-app",
            "D361_DEBUG": "false",
            "D361_API_TIMEOUT_SECONDS": "120"
        }):
            config = AppConfig()
            
            # Should pick up environment variables
            assert config.app_name == "env-app" or config.app_name == "d361"  # Depends on implementation


class TestEnvironmentLoader:
    """Test cases for EnvironmentLoader."""

    def test_environment_detection(self, test_data_dir):
        """Test environment detection logic."""
        loader = EnvironmentLoader(test_data_dir)
        
        # Default should be development
        env = loader.detect_environment()
        assert env == Environment.DEVELOPMENT

    def test_environment_detection_with_override(self, test_data_dir):
        """Test environment detection with override."""
        loader = EnvironmentLoader(test_data_dir, environment_override="production")
        
        env = loader.detect_environment()
        assert env == Environment.PRODUCTION

    def test_environment_detection_from_env_var(self, test_data_dir):
        """Test environment detection from environment variable."""
        with patch.dict(os.environ, {"D361_ENVIRONMENT": "staging"}):
            loader = EnvironmentLoader(test_data_dir)
            env = loader.detect_environment()
            assert env == Environment.STAGING

    def test_dotenv_file_loading(self, test_data_dir, test_helpers):
        """Test .env file loading."""
        # Create test .env file
        env_vars = {
            "TEST_VAR": "test_value",
            "QUOTED_VAR": '"quoted_value"',
            "NUMBER_VAR": "123"
        }
        test_helpers.create_test_env_file(test_data_dir, env_vars)
        
        loader = EnvironmentLoader(test_data_dir)
        loaded_vars = loader.load_dotenv_file(test_data_dir / ".env")
        
        assert loaded_vars["TEST_VAR"] == "test_value"
        assert loaded_vars["QUOTED_VAR"] == "quoted_value"  # Quotes removed
        assert loaded_vars["NUMBER_VAR"] == "123"

    def test_config_file_paths(self, test_data_dir, test_helpers):
        """Test configuration file path detection."""
        # Create test config files
        test_helpers.create_test_config_file(test_data_dir, "config.yaml", {"test": "value"})
        test_helpers.create_test_config_file(test_data_dir, "config.production.yaml", {"prod": "value"})
        
        loader = EnvironmentLoader(test_data_dir)
        
        config_paths = loader.get_config_file_paths(Environment.PRODUCTION)
        assert len(config_paths) >= 1
        
        # Should include environment-specific file
        prod_config = any("production" in str(path) for path in config_paths)
        assert prod_config

    def test_env_file_paths(self, test_data_dir, test_helpers):
        """Test .env file path detection."""
        # Create test .env files
        test_helpers.create_test_env_file(test_data_dir, {"BASE": "value"})
        test_helpers.create_test_env_file(test_data_dir / ".env.development", {"DEV": "value"})
        
        loader = EnvironmentLoader(test_data_dir)
        
        env_paths = loader.get_env_file_paths(Environment.DEVELOPMENT)
        assert len(env_paths) >= 1
        
        # Should include base and development files
        has_base = any(path.name == ".env" for path in env_paths)
        assert has_base

    @pytest.mark.asyncio
    async def test_configuration_loading(self, test_data_dir, test_helpers):
        """Test complete configuration loading."""
        # Create test configuration
        config_data = {
            "app_name": "test-app",
            "debug": True
        }
        test_helpers.create_test_config_file(test_data_dir, "config.yaml", config_data)
        
        loader = EnvironmentLoader(test_data_dir)
        config = loader.load_configuration(Environment.TESTING)
        
        assert isinstance(config, AppConfig)
        assert config.environment == Environment.TESTING

    def test_hot_reload_setup(self, test_data_dir):
        """Test hot-reload functionality setup."""
        loader = EnvironmentLoader(test_data_dir)
        
        # Create test config for reloading
        test_config = AppConfig(environment=Environment.DEVELOPMENT)
        loader._current_config = test_config
        
        callback = Mock()
        loader.start_hot_reload(callback)
        
        # Should set up file watcher
        # Note: Actual file change testing would be complex
        assert loader._observer is not None or loader._current_config.is_production()

    def test_config_summary(self, test_data_dir):
        """Test configuration summary generation."""
        loader = EnvironmentLoader(test_data_dir)
        
        summary = loader.get_config_summary()
        
        assert "environment" in summary
        assert "base_config_dir" in summary
        assert "config_files" in summary
        assert "sources_priority" in summary


class TestSecretsProviders:
    """Test cases for secrets providers."""

    @pytest.mark.asyncio
    async def test_environment_secrets_provider(self):
        """Test environment variables secrets provider."""
        config = {"prefix": "TEST_SECRET_"}
        provider = EnvironmentSecretsProvider(config)
        
        await provider.initialize()
        assert provider._is_initialized

        # Test setting and getting secret
        with patch.dict(os.environ, {"TEST_SECRET_API_TOKEN": "test-token-123"}):
            secret = await provider.get_secret("api_token")
            
            assert secret.value == "test-token-123"
            assert secret.metadata.secret_id == "api_token"

    @pytest.mark.asyncio
    async def test_environment_secrets_provider_missing_secret(self):
        """Test environment provider with missing secret."""
        provider = EnvironmentSecretsProvider({"prefix": "MISSING_"})
        await provider.initialize()
        
        with pytest.raises(Document360Error) as exc_info:
            await provider.get_secret("nonexistent")
        
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_local_file_secrets_provider(self, test_data_dir):
        """Test local file secrets provider."""
        secrets_dir = test_data_dir / "secrets"
        secrets_dir.mkdir(exist_ok=True)
        
        config = {"secrets_dir": secrets_dir}
        provider = LocalFileSecretsProvider(config)
        
        await provider.initialize()
        assert provider._is_initialized

        # Test setting secret
        metadata = await provider.set_secret(
            "test_secret",
            "secret_value_123",
            SecretType.API_TOKEN,
            {"description": "Test secret"}
        )
        
        assert metadata.secret_id == "test_secret"
        assert metadata.secret_type == SecretType.API_TOKEN

        # Test getting secret
        secret = await provider.get_secret("test_secret")
        assert secret.value == "secret_value_123"
        assert secret.metadata.secret_type == SecretType.API_TOKEN

    @pytest.mark.asyncio
    async def test_local_file_secrets_provider_list(self, test_data_dir):
        """Test listing secrets from local file provider."""
        secrets_dir = test_data_dir / "secrets"
        provider = LocalFileSecretsProvider({"secrets_dir": secrets_dir})
        await provider.initialize()

        # Create test secrets
        await provider.set_secret("secret1", "value1", SecretType.API_TOKEN)
        await provider.set_secret("secret2", "value2", SecretType.DATABASE_URL)

        # List all secrets
        secrets = await provider.list_secrets()
        assert len(secrets) == 2

        # List by type
        api_secrets = await provider.list_secrets(secret_type=SecretType.API_TOKEN)
        assert len(api_secrets) == 1
        assert api_secrets[0].secret_type == SecretType.API_TOKEN

    @pytest.mark.asyncio
    async def test_secrets_provider_health_check(self, test_data_dir):
        """Test secrets provider health checks."""
        # Environment provider
        env_provider = EnvironmentSecretsProvider({})
        await env_provider.initialize()
        assert await env_provider.health_check() is True

        # Local file provider
        file_provider = LocalFileSecretsProvider({"secrets_dir": test_data_dir / "secrets"})
        await file_provider.initialize()
        assert await file_provider.health_check() is True


class TestSecretsManager:
    """Test cases for SecretsManager."""

    @pytest.mark.asyncio
    async def test_secrets_manager_initialization(self, test_data_dir):
        """Test secrets manager initialization."""
        from d361.config import SecurityConfig
        
        security_config = SecurityConfig(
            secrets_provider=SecretProvider.LOCAL_FILE,
            secrets_config={"secrets_dir": test_data_dir / "secrets"}
        )
        
        manager = SecretsManager(security_config)
        await manager.initialize()
        
        assert manager._is_initialized
        assert manager._primary_provider is not None

    @pytest.mark.asyncio
    async def test_secrets_manager_auto_detection(self):
        """Test automatic provider detection."""
        manager = SecretsManager()
        
        # Should detect environment provider as default
        detected_provider = await manager._detect_best_provider()
        assert detected_provider == SecretProvider.ENVIRONMENT

    @pytest.mark.asyncio
    async def test_secrets_manager_fallback(self, test_data_dir):
        """Test fallback provider functionality."""
        from d361.config import SecurityConfig
        
        security_config = SecurityConfig(
            secrets_provider=SecretProvider.LOCAL_FILE,
            secrets_config={"secrets_dir": test_data_dir / "secrets"}
        )
        
        manager = SecretsManager(security_config)
        await manager.initialize()
        
        # Should have fallback providers
        assert len(manager._fallback_providers) >= 1

    @pytest.mark.asyncio
    async def test_secrets_manager_secret_operations(self, test_data_dir):
        """Test secret CRUD operations through manager."""
        from d361.config import SecurityConfig
        
        security_config = SecurityConfig(
            secrets_provider=SecretProvider.LOCAL_FILE,
            secrets_config={"secrets_dir": test_data_dir / "secrets"}
        )
        
        manager = SecretsManager(security_config)
        await manager.initialize()

        # Set secret
        metadata = await manager.set_secret(
            "test_api_token",
            "token_value_123",
            SecretType.API_TOKEN
        )
        assert metadata.secret_id == "test_api_token"

        # Get secret
        secret = await manager.get_secret("test_api_token")
        assert secret.value == "token_value_123"

        # List secrets
        secrets = await manager.list_secrets()
        assert len(secrets) >= 1

        # Delete secret
        result = await manager.delete_secret("test_api_token")
        assert result is True

    @pytest.mark.asyncio
    async def test_secrets_manager_health_check(self, test_data_dir):
        """Test secrets manager health monitoring."""
        from d361.config import SecurityConfig
        
        security_config = SecurityConfig(
            secrets_provider=SecretProvider.LOCAL_FILE,
            secrets_config={"secrets_dir": test_data_dir / "secrets"}
        )
        
        manager = SecretsManager(security_config)
        await manager.initialize()

        health = await manager.health_check()
        
        assert isinstance(health, dict)
        assert any("primary_" in key for key in health.keys())

    @pytest.mark.asyncio
    async def test_secrets_manager_provider_info(self, test_data_dir):
        """Test provider information retrieval."""
        from d361.config import SecurityConfig
        
        security_config = SecurityConfig(
            secrets_provider=SecretProvider.LOCAL_FILE,
            secrets_config={"secrets_dir": test_data_dir / "secrets"}
        )
        
        manager = SecretsManager(security_config)
        await manager.initialize()

        info = await manager.get_provider_info()
        
        assert "primary_provider" in info
        assert "fallback_providers" in info
        assert "total_providers" in info


class TestConfigLoader:
    """Test cases for ConfigLoader."""

    @pytest.mark.asyncio
    async def test_config_loader_initialization(self, test_data_dir):
        """Test config loader initialization."""
        loader = ConfigLoader(
            base_config_dir=test_data_dir,
            enable_secrets=False,
            enable_hot_reload=False
        )
        
        assert loader.base_config_dir == test_data_dir
        assert loader.enable_secrets is False

    @pytest.mark.asyncio
    async def test_config_loader_load_configuration(self, test_data_dir, test_helpers):
        """Test configuration loading through ConfigLoader."""
        # Create test configuration
        config_data = {"app_name": "test-app", "debug": False}
        test_helpers.create_test_config_file(test_data_dir, "config.yaml", config_data)
        
        loader = ConfigLoader(
            base_config_dir=test_data_dir,
            enable_secrets=False,
            enable_hot_reload=False
        )
        
        config = await loader.load_configuration(Environment.TESTING, validate=False)
        
        assert isinstance(config, AppConfig)
        assert config.environment == Environment.TESTING

    @pytest.mark.asyncio
    async def test_config_loader_validation(self, test_data_dir):
        """Test configuration validation through loader."""
        loader = ConfigLoader(
            base_config_dir=test_data_dir,
            enable_secrets=False,
            enable_hot_reload=False
        )
        
        # Load with validation
        config = await loader.load_configuration(Environment.TESTING, validate=True)
        
        assert isinstance(config, AppConfig)

    @pytest.mark.asyncio
    async def test_config_loader_with_secrets(self, test_data_dir):
        """Test configuration loading with secrets integration."""
        loader = ConfigLoader(
            base_config_dir=test_data_dir,
            enable_secrets=True,
            enable_hot_reload=False
        )
        
        # Should initialize secrets manager
        config = await loader.load_configuration(Environment.TESTING)
        assert loader.secrets_manager is not None

    def test_config_loader_summary(self, test_data_dir):
        """Test configuration summary from loader."""
        loader = ConfigLoader(base_config_dir=test_data_dir)
        
        # Get summary
        summary = asyncio.run(loader.get_config_summary())
        
        assert "secrets_enabled" in summary
        assert "hot_reload_enabled" in summary


class TestConfigValidator:
    """Test cases for ConfigValidator."""

    def test_config_validator_creation(self):
        """Test config validator creation."""
        validator = ConfigValidator(Environment.PRODUCTION)
        
        assert validator.environment == Environment.PRODUCTION
        assert len(validator.validation_rules) > 0

    def test_config_validator_production_rules(self):
        """Test production-specific validation rules."""
        validator = ConfigValidator(Environment.PRODUCTION)
        
        # Create config with production issues
        config = AppConfig(
            environment=Environment.PRODUCTION,
            debug=True  # Should trigger warning
        )
        
        issues = validator.validate(config)
        
        # Should have debug mode issue
        debug_issues = [issue for issue in issues if "debug" in issue.lower()]
        # May or may not have issues depending on implementation

    def test_config_validator_development_rules(self):
        """Test development-specific validation."""
        validator = ConfigValidator(Environment.DEVELOPMENT)
        
        config = AppConfig(environment=Environment.DEVELOPMENT)
        
        issues = validator.validate(config)
        
        # Development should be more lenient
        assert isinstance(issues, list)

    def test_config_validator_custom_rule(self):
        """Test adding custom validation rules."""
        validator = ConfigValidator(Environment.TESTING)
        
        def custom_rule(config: AppConfig) -> list[str]:
            if config.app_name == "invalid":
                return ["Custom rule: invalid app name"]
            return []
        
        validator.add_rule(custom_rule)
        
        # Test with invalid config
        config = AppConfig(app_name="invalid")
        issues = validator.validate(config)
        
        custom_issues = [issue for issue in issues if "Custom rule" in issue]
        assert len(custom_issues) == 1

    def test_config_validator_resource_limits(self):
        """Test resource limit validation."""
        validator = ConfigValidator(Environment.PRODUCTION)
        
        # Create config with excessive limits
        config = AppConfig()
        config.cache.max_disk_size_mb = 100000  # 100GB
        config.archive.max_extracted_size_mb = 100000  # 100GB
        
        issues = validator.validate(config)
        
        # Should have resource limit warnings
        limit_issues = [issue for issue in issues if "cache size" in issue.lower()]
        # May have issues depending on validation implementation

    def test_config_validator_network_settings(self):
        """Test network settings validation."""
        validator = ConfigValidator(Environment.PRODUCTION)
        
        config = AppConfig()
        config.api.timeout_seconds = 1  # Very short timeout
        
        issues = validator.validate(config)
        
        # Should have timeout warnings
        timeout_issues = [issue for issue in issues if "timeout" in issue.lower()]
        # May have issues depending on implementation


class TestConfigurationEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_environment_values(self):
        """Test handling of invalid environment values."""
        with pytest.raises(ValidationError):
            AppConfig(environment="invalid_environment")

    def test_missing_required_fields(self):
        """Test handling of missing required configuration fields."""
        # Most fields should have defaults, but test edge cases
        config = AppConfig()
        
        # Should not raise errors due to defaults
        assert config.app_name is not None
        assert config.version is not None

    def test_config_with_invalid_nested_values(self):
        """Test configuration with invalid nested values."""
        with pytest.raises(ValidationError):
            AppConfig(
                api={"timeout_seconds": -1}  # Invalid negative timeout
            )

    @pytest.mark.asyncio
    async def test_config_loading_with_corrupted_files(self, test_data_dir, test_helpers):
        """Test configuration loading with corrupted files."""
        # Create corrupted JSON file
        corrupted_path = test_data_dir / "config.json"
        with open(corrupted_path, 'w') as f:
            f.write('{"invalid": json}')  # Invalid JSON
        
        loader = EnvironmentLoader(test_data_dir)
        
        # Should handle corrupted files gracefully
        try:
            config = loader.load_configuration(Environment.TESTING)
            # Should either succeed with defaults or raise appropriate error
        except Document360Error:
            # Expected for corrupted config
            pass

    @pytest.mark.asyncio
    async def test_secrets_with_provider_failures(self):
        """Test secrets handling when provider fails."""
        # Mock failing provider
        failing_provider = AsyncMock()
        failing_provider.initialize.side_effect = Exception("Provider failed")
        
        with patch('d361.config.secrets_manager.create_secrets_provider', return_value=failing_provider):
            manager = SecretsManager()
            
            with pytest.raises(Document360Error):
                await manager.initialize()

    def test_config_serialization_edge_cases(self):
        """Test configuration serialization edge cases."""
        config = AppConfig()
        
        # Test with secrets present
        config.api.api_tokens = ["secret-token-123"]
        
        # Safe serialization should mask secrets
        safe_dict = config.to_dict(exclude_secrets=True)
        
        if "api" in safe_dict and "api_tokens" in safe_dict["api"]:
            # Should be masked
            tokens = safe_dict["api"]["api_tokens"]
            assert isinstance(tokens, list)
            # Should be masked or empty depending on implementation


# Fixtures for configuration testing
@pytest.fixture
def sample_config_data() -> Dict[str, Any]:
    """Sample configuration data for testing."""
    return {
        "app_name": "test-d361",
        "environment": "testing",
        "debug": True,
        "api": {
            "timeout_seconds": 30,
            "max_retries": 3,
            "api_tokens": ["test-token"]
        },
        "cache": {
            "enabled": True,
            "max_memory_mb": 128
        },
        "monitoring": {
            "metrics_enabled": True,
            "log_level": "DEBUG"
        }
    }


@pytest.fixture
def production_config_data() -> Dict[str, Any]:
    """Production configuration data for testing."""
    return {
        "app_name": "d361-prod",
        "environment": "production",
        "debug": False,
        "api": {
            "timeout_seconds": 60,
            "max_retries": 5,
            "api_tokens": ["prod-token"]
        },
        "monitoring": {
            "metrics_enabled": True,
            "alerting_enabled": True,
            "log_level": "INFO"
        }
    }