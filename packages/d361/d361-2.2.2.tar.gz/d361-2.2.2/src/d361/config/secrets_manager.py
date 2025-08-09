# this_file: external/int_folders/d361/src/d361/config/secrets_manager.py
"""
Secrets manager for auto-detection and intelligent provider selection.

This module provides the SecretsManager class that automatically detects
the best available secret provider based on environment and configuration,
with fallback strategies and comprehensive error handling.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime

from loguru import logger

from .schema import SecretProvider, SecurityConfig
from .secrets import (
    SecretsProvider,
    SecretValue,
    SecretMetadata,
    SecretType,
    create_secrets_provider,
    PROVIDER_REGISTRY
)
from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class SecretsManager:
    """
    Central secrets management orchestrator with auto-detection.
    
    This class provides intelligent provider selection, fallback strategies,
    and a unified interface for secret management across different providers.
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        Initialize secrets manager.
        
        Args:
            config: Security configuration (auto-detected if None)
        """
        self.config = config or SecurityConfig()
        self._primary_provider: Optional[SecretsProvider] = None
        self._fallback_providers: List[SecretsProvider] = []
        self._provider_health: Dict[str, bool] = {}
        self._is_initialized = False
        
        logger.debug(
            "SecretsManager initialized",
            primary_provider=self.config.secrets_provider,
            config_keys=list(self.config.secrets_config.keys())
        )
    
    async def initialize(self) -> None:
        """Initialize the secrets manager and providers."""
        try:
            # Detect and initialize primary provider
            await self._initialize_primary_provider()
            
            # Initialize fallback providers
            await self._initialize_fallback_providers()
            
            self._is_initialized = True
            logger.info(
                "SecretsManager initialized successfully",
                primary_provider=self._primary_provider.__class__.__name__,
                fallback_count=len(self._fallback_providers)
            )
            
        except Exception as e:
            raise Document360Error(
                f"Failed to initialize SecretsManager: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
    
    async def _initialize_primary_provider(self) -> None:
        """Initialize the primary secrets provider."""
        provider_type = self.config.secrets_provider
        provider_config = self.config.secrets_config.copy()
        
        # Auto-detect provider if not specified
        if provider_type == SecretProvider.ENVIRONMENT:
            detected_provider = await self._detect_best_provider()
            if detected_provider != provider_type:
                logger.info(f"Auto-detected provider: {detected_provider}")
                provider_type = detected_provider
        
        # Create and initialize provider
        self._primary_provider = create_secrets_provider(provider_type, provider_config)
        await self._primary_provider.initialize()
        
        # Check provider health
        health = await self._primary_provider.health_check()
        self._provider_health[provider_type.value] = health
        
        if not health:
            logger.warning(f"Primary provider {provider_type} is not healthy")
    
    async def _initialize_fallback_providers(self) -> None:
        """Initialize fallback providers for redundancy."""
        primary_type = self.config.secrets_provider
        
        # Define fallback chain
        fallback_chain = [
            SecretProvider.ENVIRONMENT,
            SecretProvider.LOCAL_FILE,
        ]
        
        for provider_type in fallback_chain:
            if provider_type == primary_type:
                continue  # Skip primary provider
            
            try:
                # Use basic configuration for fallback providers
                fallback_config = self._get_fallback_config(provider_type)
                provider = create_secrets_provider(provider_type, fallback_config)
                await provider.initialize()
                
                # Check health
                health = await provider.health_check()
                self._provider_health[provider_type.value] = health
                
                if health:
                    self._fallback_providers.append(provider)
                    logger.debug(f"Fallback provider {provider_type} initialized successfully")
                
            except Exception as e:
                logger.debug(f"Failed to initialize fallback provider {provider_type}: {e}")
                continue
    
    def _get_fallback_config(self, provider_type: SecretProvider) -> Dict[str, Any]:
        """Get basic configuration for fallback providers."""
        if provider_type == SecretProvider.ENVIRONMENT:
            return {"prefix": "D361_SECRET_"}
        elif provider_type == SecretProvider.LOCAL_FILE:
            return {
                "secrets_dir": Path.home() / ".d361" / "secrets",
                "encryption_key_path": None
            }
        else:
            return {}
    
    async def _detect_best_provider(self) -> SecretProvider:
        """
        Auto-detect the best available secrets provider.
        
        Returns:
            Best available provider type
        """
        # Check for Vault configuration
        if self._is_vault_available():
            logger.debug("HashiCorp Vault detected")
            return SecretProvider.HASHICORP_VAULT
        
        # Check for AWS configuration
        if self._is_aws_available():
            logger.debug("AWS Secrets Manager detected")
            return SecretProvider.AWS_SECRETS_MANAGER
        
        # Check for local secrets directory
        secrets_dir = Path.home() / ".d361" / "secrets"
        if secrets_dir.exists() and any(secrets_dir.glob("*.json")):
            logger.debug("Local secrets files detected")
            return SecretProvider.LOCAL_FILE
        
        # Default to environment variables
        logger.debug("Defaulting to environment variables provider")
        return SecretProvider.ENVIRONMENT
    
    def _is_vault_available(self) -> bool:
        """Check if HashiCorp Vault is available."""
        vault_url = os.getenv("VAULT_ADDR")
        vault_token = os.getenv("VAULT_TOKEN")
        
        if not vault_url or not vault_token:
            return False
        
        try:
            # Try to import hvac
            import hvac
            return True
        except ImportError:
            return False
    
    def _is_aws_available(self) -> bool:
        """Check if AWS Secrets Manager is available."""
        # Check for AWS credentials
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_DEFAULT_REGION")
        
        if not all([aws_access_key, aws_secret_key, aws_region]):
            return False
        
        try:
            # Try to import boto3
            import boto3
            return True
        except ImportError:
            return False
    
    async def get_secret(self, secret_id: str) -> SecretValue:
        """
        Get a secret with automatic fallback.
        
        Args:
            secret_id: The secret identifier
            
        Returns:
            SecretValue with value and metadata
            
        Raises:
            Document360Error: If secret retrieval fails from all providers
        """
        if not self._is_initialized:
            raise Document360Error(
                "SecretsManager not initialized",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
        
        errors = []
        
        # Try primary provider first
        if self._primary_provider:
            try:
                secret = await self._primary_provider.get_secret(secret_id)
                logger.debug(f"Secret '{secret_id}' retrieved from primary provider")
                return secret
            except Exception as e:
                errors.append(f"Primary provider: {e}")
                logger.debug(f"Primary provider failed for secret '{secret_id}': {e}")
        
        # Try fallback providers
        for provider in self._fallback_providers:
            try:
                secret = await provider.get_secret(secret_id)
                logger.info(f"Secret '{secret_id}' retrieved from fallback provider: {provider.__class__.__name__}")
                return secret
            except Exception as e:
                errors.append(f"{provider.__class__.__name__}: {e}")
                logger.debug(f"Fallback provider {provider.__class__.__name__} failed for secret '{secret_id}': {e}")
        
        # All providers failed
        error_details = "; ".join(errors)
        raise Document360Error(
            f"Failed to retrieve secret '{secret_id}' from all providers: {error_details}",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH
        )
    
    async def set_secret(
        self,
        secret_id: str,
        value: str,
        secret_type: SecretType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecretMetadata:
        """
        Store a secret using the primary provider.
        
        Args:
            secret_id: The secret identifier
            value: The secret value
            secret_type: Type of secret
            metadata: Additional metadata
            
        Returns:
            SecretMetadata for the stored secret
            
        Raises:
            Document360Error: If secret storage fails
        """
        if not self._is_initialized or not self._primary_provider:
            raise Document360Error(
                "SecretsManager not initialized or no primary provider available",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
        
        try:
            result = await self._primary_provider.set_secret(secret_id, value, secret_type, metadata)
            logger.debug(f"Secret '{secret_id}' stored successfully")
            return result
        except Exception as e:
            raise Document360Error(
                f"Failed to store secret '{secret_id}': {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
    
    async def delete_secret(self, secret_id: str) -> bool:
        """
        Delete a secret from the primary provider.
        
        Args:
            secret_id: The secret identifier
            
        Returns:
            True if deleted successfully
        """
        if not self._is_initialized or not self._primary_provider:
            logger.warning("SecretsManager not initialized or no primary provider available")
            return False
        
        try:
            result = await self._primary_provider.delete_secret(secret_id)
            logger.debug(f"Secret '{secret_id}' deletion result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_id}': {e}")
            return False
    
    async def list_secrets(
        self,
        secret_type: Optional[SecretType] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """
        List secrets from the primary provider.
        
        Args:
            secret_type: Optional filter by secret type
            tags: Optional filter by tags
            
        Returns:
            List of secret metadata
        """
        if not self._is_initialized or not self._primary_provider:
            return []
        
        try:
            secrets = await self._primary_provider.list_secrets(secret_type, tags)
            logger.debug(f"Listed {len(secrets)} secrets from primary provider")
            return secrets
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []
    
    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all providers.
        
        Returns:
            Dictionary mapping provider names to health status
        """
        health_status = {}
        
        if self._primary_provider:
            try:
                health = await self._primary_provider.health_check()
                provider_name = self._primary_provider.__class__.__name__
                health_status[f"primary_{provider_name}"] = health
            except Exception as e:
                health_status[f"primary_{self._primary_provider.__class__.__name__}"] = False
        
        for provider in self._fallback_providers:
            try:
                health = await provider.health_check()
                provider_name = provider.__class__.__name__
                health_status[f"fallback_{provider_name}"] = health
            except Exception as e:
                health_status[f"fallback_{provider.__class__.__name__}"] = False
        
        return health_status
    
    async def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about configured providers.
        
        Returns:
            Provider information dictionary
        """
        info = {
            "primary_provider": self._primary_provider.__class__.__name__ if self._primary_provider else None,
            "fallback_providers": [p.__class__.__name__ for p in self._fallback_providers],
            "provider_health": await self.health_check(),
            "total_providers": 1 + len(self._fallback_providers) if self._primary_provider else len(self._fallback_providers),
            "initialization_time": datetime.now().isoformat()
        }
        
        return info
    
    async def rotate_secrets(
        self,
        secret_ids: Optional[List[str]] = None,
        secret_types: Optional[List[SecretType]] = None
    ) -> Dict[str, bool]:
        """
        Rotate secrets based on IDs or types.
        
        Args:
            secret_ids: Optional list of specific secrets to rotate
            secret_types: Optional list of secret types to rotate
            
        Returns:
            Dictionary mapping secret IDs to rotation success status
        """
        if not self._is_initialized:
            return {}
        
        rotation_results = {}
        
        # Get list of secrets to rotate
        if secret_ids:
            secrets_to_rotate = secret_ids
        else:
            # Get all secrets of specified types
            all_secrets = await self.list_secrets()
            secrets_to_rotate = [
                s.secret_id for s in all_secrets 
                if not secret_types or s.secret_type in secret_types
            ]
        
        for secret_id in secrets_to_rotate:
            try:
                # For now, just check if secret exists and is expired
                secret = await self.get_secret(secret_id)
                
                if secret.metadata.expires_soon(threshold_hours=48):
                    logger.info(f"Secret '{secret_id}' needs rotation (expires soon)")
                    # TODO: Implement actual rotation logic based on secret type
                    rotation_results[secret_id] = True
                else:
                    rotation_results[secret_id] = False
                    
            except Exception as e:
                logger.error(f"Failed to rotate secret '{secret_id}': {e}")
                rotation_results[secret_id] = False
        
        return rotation_results
    
    async def cleanup(self) -> None:
        """Cleanup all providers."""
        if self._primary_provider:
            await self._primary_provider.cleanup()
        
        for provider in self._fallback_providers:
            await provider.cleanup()
        
        self._is_initialized = False
        logger.debug("SecretsManager cleaned up")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager(config: Optional[SecurityConfig] = None) -> SecretsManager:
    """
    Get the global secrets manager instance.
    
    Args:
        config: Security configuration (used only for first initialization)
        
    Returns:
        Global SecretsManager instance
    """
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager(config)
    return _secrets_manager


def set_secrets_manager(manager: SecretsManager) -> None:
    """
    Set the global secrets manager instance.
    
    Args:
        manager: SecretsManager instance to set as global
    """
    global _secrets_manager
    _secrets_manager = manager


def reset_secrets_manager() -> None:
    """Reset the global secrets manager instance."""
    global _secrets_manager
    _secrets_manager = None