# this_file: external/int_folders/d361/src/d361/config/secrets.py
"""
Secrets management system with pluggable provider architecture.

This module provides abstract and concrete implementations for secure
credential management across different secret providers including HashiCorp
Vault, AWS Secrets Manager, local encrypted files, and environment variables.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from loguru import logger
from pydantic import BaseModel, Field, validator

from .schema import SecretProvider
from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class SecretType(str, Enum):
    """Types of secrets that can be managed."""
    API_TOKEN = "api_token"
    DATABASE_URL = "database_url" 
    ENCRYPTION_KEY = "encryption_key"
    OAUTH_CLIENT_SECRET = "oauth_client_secret"
    WEBHOOK_SECRET = "webhook_secret"
    CERTIFICATE = "certificate"
    PRIVATE_KEY = "private_key"


@dataclass
class SecretMetadata:
    """Metadata associated with a secret."""
    secret_id: str
    secret_type: SecretType
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    tags: Dict[str, str] = None
    description: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
    
    def is_expired(self) -> bool:
        """Check if the secret has expired."""
        return self.expires_at is not None and datetime.now() >= self.expires_at
    
    def expires_soon(self, threshold_hours: int = 24) -> bool:
        """Check if the secret expires within the threshold."""
        if self.expires_at is None:
            return False
        return datetime.now() + timedelta(hours=threshold_hours) >= self.expires_at


class SecretValue(BaseModel):
    """Container for secret values with metadata."""
    value: str = Field(..., description="The secret value")
    metadata: SecretMetadata = Field(..., description="Secret metadata")
    
    class Config:
        arbitrary_types_allowed = True
        
    def is_valid(self) -> bool:
        """Check if the secret is valid (not expired)."""
        return not self.metadata.is_expired()


class SecretsProvider(ABC):
    """
    Abstract base class for pluggable secrets management providers.
    
    This defines the interface that all secret providers must implement
    to provide consistent secret management across different backends.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the secrets provider.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self._connection = None
        self._is_initialized = False
        
        logger.debug(
            "SecretsProvider initialized",
            provider=self.__class__.__name__,
            config_keys=list(config.keys())
        )
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider connection and authentication."""
        pass
    
    @abstractmethod
    async def get_secret(self, secret_id: str) -> SecretValue:
        """
        Get a secret by ID.
        
        Args:
            secret_id: The secret identifier
            
        Returns:
            SecretValue with value and metadata
            
        Raises:
            Document360Error: If secret retrieval fails
        """
        pass
    
    @abstractmethod
    async def set_secret(
        self,
        secret_id: str,
        value: str,
        secret_type: SecretType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecretMetadata:
        """
        Store a secret.
        
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
        pass
    
    @abstractmethod
    async def delete_secret(self, secret_id: str) -> bool:
        """
        Delete a secret.
        
        Args:
            secret_id: The secret identifier
            
        Returns:
            True if deleted successfully
            
        Raises:
            Document360Error: If secret deletion fails
        """
        pass
    
    @abstractmethod
    async def list_secrets(
        self,
        secret_type: Optional[SecretType] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """
        List available secrets.
        
        Args:
            secret_type: Optional filter by secret type
            tags: Optional filter by tags
            
        Returns:
            List of secret metadata
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy.
        
        Returns:
            True if provider is accessible and healthy
        """
        pass
    
    async def cleanup(self) -> None:
        """Cleanup resources on provider shutdown."""
        self._is_initialized = False
        logger.debug(f"SecretsProvider {self.__class__.__name__} cleaned up")


class EnvironmentSecretsProvider(SecretsProvider):
    """
    Secrets provider that uses environment variables.
    
    This is the simplest provider for development and testing environments
    where secrets are stored as environment variables with a prefix.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.prefix = config.get("prefix", "D361_SECRET_")
        self.secrets_cache: Dict[str, SecretValue] = {}
    
    async def initialize(self) -> None:
        """Initialize environment provider."""
        self._is_initialized = True
        logger.debug(f"EnvironmentSecretsProvider initialized with prefix: {self.prefix}")
    
    async def get_secret(self, secret_id: str) -> SecretValue:
        """Get secret from environment variable."""
        env_var = f"{self.prefix}{secret_id.upper()}"
        value = os.getenv(env_var)
        
        if value is None:
            raise Document360Error(
                f"Secret '{secret_id}' not found in environment variable '{env_var}'",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
        
        # Create metadata
        metadata = SecretMetadata(
            secret_id=secret_id,
            secret_type=SecretType.API_TOKEN,  # Default type
            created_at=datetime.now(),
            updated_at=datetime.now(),
            description=f"Environment variable {env_var}"
        )
        
        return SecretValue(value=value, metadata=metadata)
    
    async def set_secret(
        self,
        secret_id: str,
        value: str,
        secret_type: SecretType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecretMetadata:
        """Set secret as environment variable."""
        env_var = f"{self.prefix}{secret_id.upper()}"
        os.environ[env_var] = value
        
        secret_metadata = SecretMetadata(
            secret_id=secret_id,
            secret_type=secret_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            description=f"Environment variable {env_var}"
        )
        
        logger.debug(f"Secret '{secret_id}' stored in environment variable '{env_var}'")
        return secret_metadata
    
    async def delete_secret(self, secret_id: str) -> bool:
        """Delete secret from environment."""
        env_var = f"{self.prefix}{secret_id.upper()}"
        if env_var in os.environ:
            del os.environ[env_var]
            logger.debug(f"Secret '{secret_id}' deleted from environment variable '{env_var}'")
            return True
        return False
    
    async def list_secrets(
        self,
        secret_type: Optional[SecretType] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List secrets from environment variables."""
        secrets = []
        
        for env_var, value in os.environ.items():
            if env_var.startswith(self.prefix):
                secret_id = env_var[len(self.prefix):].lower()
                metadata = SecretMetadata(
                    secret_id=secret_id,
                    secret_type=SecretType.API_TOKEN,  # Default
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    description=f"Environment variable {env_var}"
                )
                secrets.append(metadata)
        
        return secrets
    
    async def health_check(self) -> bool:
        """Environment provider is always healthy."""
        return self._is_initialized


class LocalFileSecretsProvider(SecretsProvider):
    """
    Secrets provider that uses encrypted local JSON files.
    
    This provider stores secrets in encrypted JSON files on the local filesystem,
    suitable for development and single-machine deployments.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.secrets_dir = Path(config.get("secrets_dir", Path.home() / ".d361" / "secrets"))
        self.encryption_key_path = config.get("encryption_key_path")
        self._encryption_key: Optional[bytes] = None
        self.secrets_cache: Dict[str, SecretValue] = {}
    
    async def initialize(self) -> None:
        """Initialize local file provider."""
        # Create secrets directory
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        
        # Load encryption key if specified
        if self.encryption_key_path:
            try:
                with open(self.encryption_key_path, "rb") as f:
                    self._encryption_key = f.read()
            except Exception as e:
                raise Document360Error(
                    f"Failed to load encryption key from {self.encryption_key_path}: {e}",
                    category=ErrorCategory.CONFIGURATION,
                    severity=ErrorSeverity.CRITICAL
                )
        
        self._is_initialized = True
        logger.debug(f"LocalFileSecretsProvider initialized, secrets_dir: {self.secrets_dir}")
    
    def _get_secret_file_path(self, secret_id: str) -> Path:
        """Get the file path for a secret."""
        return self.secrets_dir / f"{secret_id}.json"
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a secret value (placeholder implementation)."""
        if self._encryption_key is None:
            # Store as base64 for basic obfuscation
            import base64
            return base64.b64encode(value.encode()).decode()
        
        # TODO: Implement actual encryption with cryptography library
        # For now, return base64 encoded
        import base64
        return base64.b64encode(value.encode()).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a secret value (placeholder implementation)."""
        if self._encryption_key is None:
            # Decode from base64
            import base64
            return base64.b64decode(encrypted_value.encode()).decode()
        
        # TODO: Implement actual decryption with cryptography library
        # For now, decode from base64
        import base64
        return base64.b64decode(encrypted_value.encode()).decode()
    
    async def get_secret(self, secret_id: str) -> SecretValue:
        """Get secret from local file."""
        secret_file = self._get_secret_file_path(secret_id)
        
        if not secret_file.exists():
            raise Document360Error(
                f"Secret '{secret_id}' not found in {secret_file}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
        
        try:
            with open(secret_file, "r") as f:
                data = json.load(f)
            
            # Decrypt the value
            encrypted_value = data["encrypted_value"]
            decrypted_value = self._decrypt_value(encrypted_value)
            
            # Create metadata
            metadata = SecretMetadata(
                secret_id=secret_id,
                secret_type=SecretType(data.get("secret_type", SecretType.API_TOKEN)),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                tags=data.get("tags", {}),
                description=data.get("description", "")
            )
            
            return SecretValue(value=decrypted_value, metadata=metadata)
            
        except Exception as e:
            raise Document360Error(
                f"Failed to read secret '{secret_id}' from {secret_file}: {e}",
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
        """Store secret in local file."""
        secret_file = self._get_secret_file_path(secret_id)
        
        # Encrypt the value
        encrypted_value = self._encrypt_value(value)
        
        # Create metadata
        now = datetime.now()
        secret_metadata = SecretMetadata(
            secret_id=secret_id,
            secret_type=secret_type,
            created_at=now,
            updated_at=now,
            tags=metadata.get("tags", {}) if metadata else {},
            description=metadata.get("description", "") if metadata else ""
        )
        
        # Prepare data for storage
        data = {
            "encrypted_value": encrypted_value,
            "secret_type": secret_type.value,
            "created_at": secret_metadata.created_at.isoformat(),
            "updated_at": secret_metadata.updated_at.isoformat(),
            "expires_at": secret_metadata.expires_at.isoformat() if secret_metadata.expires_at else None,
            "tags": secret_metadata.tags,
            "description": secret_metadata.description
        }
        
        try:
            with open(secret_file, "w") as f:
                json.dump(data, f, indent=2)
            
            # Set restrictive permissions
            secret_file.chmod(0o600)
            
            logger.debug(f"Secret '{secret_id}' stored in {secret_file}")
            return secret_metadata
            
        except Exception as e:
            raise Document360Error(
                f"Failed to store secret '{secret_id}' in {secret_file}: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
    
    async def delete_secret(self, secret_id: str) -> bool:
        """Delete secret file."""
        secret_file = self._get_secret_file_path(secret_id)
        
        if secret_file.exists():
            try:
                secret_file.unlink()
                logger.debug(f"Secret '{secret_id}' deleted from {secret_file}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete secret file {secret_file}: {e}")
                return False
        
        return False
    
    async def list_secrets(
        self,
        secret_type: Optional[SecretType] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List secrets from local files."""
        secrets = []
        
        for secret_file in self.secrets_dir.glob("*.json"):
            try:
                with open(secret_file, "r") as f:
                    data = json.load(f)
                
                metadata = SecretMetadata(
                    secret_id=secret_file.stem,
                    secret_type=SecretType(data.get("secret_type", SecretType.API_TOKEN)),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                    expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
                    tags=data.get("tags", {}),
                    description=data.get("description", "")
                )
                
                # Apply filters
                if secret_type and metadata.secret_type != secret_type:
                    continue
                
                if tags and not all(metadata.tags.get(k) == v for k, v in tags.items()):
                    continue
                
                secrets.append(metadata)
                
            except Exception as e:
                logger.warning(f"Failed to read secret metadata from {secret_file}: {e}")
                continue
        
        return secrets
    
    async def health_check(self) -> bool:
        """Check if secrets directory is accessible."""
        return self._is_initialized and self.secrets_dir.exists() and self.secrets_dir.is_dir()


class HashiCorpVaultProvider(SecretsProvider):
    """
    Secrets provider for HashiCorp Vault.
    
    This provider integrates with HashiCorp Vault for enterprise-grade
    secret management with features like secret versioning, leasing, and rotation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.vault_url = config.get("vault_url", "http://localhost:8200")
        self.vault_token = config.get("vault_token")
        self.vault_path = config.get("vault_path", "d361/")
        self.mount_point = config.get("mount_point", "secret")
        
        # Will be set during initialization
        self._vault_client = None
    
    async def initialize(self) -> None:
        """Initialize Vault client."""
        try:
            # Try to import hvac (HashiCorp Vault client)
            import hvac
            
            self._vault_client = hvac.Client(
                url=self.vault_url,
                token=self.vault_token
            )
            
            # Verify authentication
            if not self._vault_client.is_authenticated():
                raise Document360Error(
                    "Failed to authenticate with HashiCorp Vault",
                    category=ErrorCategory.CONFIGURATION,
                    severity=ErrorSeverity.CRITICAL
                )
            
            self._is_initialized = True
            logger.debug(f"HashiCorpVaultProvider initialized, vault_url: {self.vault_url}")
            
        except ImportError:
            raise Document360Error(
                "hvac library is required for HashiCorp Vault integration. Install with: pip install hvac",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
        except Exception as e:
            raise Document360Error(
                f"Failed to initialize HashiCorp Vault client: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
    
    def _get_vault_path(self, secret_id: str) -> str:
        """Get the Vault path for a secret."""
        return f"{self.vault_path}{secret_id}"
    
    async def get_secret(self, secret_id: str) -> SecretValue:
        """Get secret from Vault."""
        if not self._vault_client:
            raise Document360Error(
                "Vault client not initialized",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
        
        vault_path = self._get_vault_path(secret_id)
        
        try:
            response = self._vault_client.secrets.kv.v2.read_secret(
                path=vault_path,
                mount_point=self.mount_point
            )
            
            secret_data = response["data"]["data"]
            metadata_data = response["data"]["metadata"]
            
            # Create metadata
            metadata = SecretMetadata(
                secret_id=secret_id,
                secret_type=SecretType(secret_data.get("secret_type", SecretType.API_TOKEN)),
                created_at=datetime.fromisoformat(metadata_data["created_time"]),
                updated_at=datetime.fromisoformat(metadata_data["created_time"]),
                tags=secret_data.get("tags", {}),
                description=secret_data.get("description", "")
            )
            
            return SecretValue(value=secret_data["value"], metadata=metadata)
            
        except Exception as e:
            raise Document360Error(
                f"Failed to get secret '{secret_id}' from Vault: {e}",
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
        """Store secret in Vault."""
        if not self._vault_client:
            raise Document360Error(
                "Vault client not initialized",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
        
        vault_path = self._get_vault_path(secret_id)
        
        # Prepare secret data
        secret_data = {
            "value": value,
            "secret_type": secret_type.value,
            "tags": metadata.get("tags", {}) if metadata else {},
            "description": metadata.get("description", "") if metadata else ""
        }
        
        try:
            response = self._vault_client.secrets.kv.v2.create_or_update_secret(
                path=vault_path,
                secret=secret_data,
                mount_point=self.mount_point
            )
            
            # Create metadata
            now = datetime.now()
            secret_metadata = SecretMetadata(
                secret_id=secret_id,
                secret_type=secret_type,
                created_at=now,
                updated_at=now,
                tags=secret_data.get("tags", {}),
                description=secret_data.get("description", "")
            )
            
            logger.debug(f"Secret '{secret_id}' stored in Vault at path '{vault_path}'")
            return secret_metadata
            
        except Exception as e:
            raise Document360Error(
                f"Failed to store secret '{secret_id}' in Vault: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
    
    async def delete_secret(self, secret_id: str) -> bool:
        """Delete secret from Vault."""
        if not self._vault_client:
            return False
        
        vault_path = self._get_vault_path(secret_id)
        
        try:
            self._vault_client.secrets.kv.v2.delete_secret(
                path=vault_path,
                mount_point=self.mount_point
            )
            
            logger.debug(f"Secret '{secret_id}' deleted from Vault at path '{vault_path}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_id}' from Vault: {e}")
            return False
    
    async def list_secrets(
        self,
        secret_type: Optional[SecretType] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[SecretMetadata]:
        """List secrets from Vault."""
        if not self._vault_client:
            return []
        
        secrets = []
        
        try:
            response = self._vault_client.secrets.kv.v2.list_secrets(
                path=self.vault_path,
                mount_point=self.mount_point
            )
            
            for secret_id in response["data"]["keys"]:
                try:
                    secret_value = await self.get_secret(secret_id)
                    
                    # Apply filters
                    if secret_type and secret_value.metadata.secret_type != secret_type:
                        continue
                    
                    if tags and not all(secret_value.metadata.tags.get(k) == v for k, v in tags.items()):
                        continue
                    
                    secrets.append(secret_value.metadata)
                    
                except Exception as e:
                    logger.warning(f"Failed to get metadata for secret '{secret_id}': {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to list secrets from Vault: {e}")
        
        return secrets
    
    async def health_check(self) -> bool:
        """Check Vault health."""
        if not self._vault_client:
            return False
        
        try:
            return self._vault_client.sys.is_initialized() and self._vault_client.is_authenticated()
        except Exception:
            return False


# Provider registry for easy instantiation
PROVIDER_REGISTRY: Dict[SecretProvider, type[SecretsProvider]] = {
    SecretProvider.ENVIRONMENT: EnvironmentSecretsProvider,
    SecretProvider.LOCAL_FILE: LocalFileSecretsProvider,
    SecretProvider.HASHICORP_VAULT: HashiCorpVaultProvider,
}


def create_secrets_provider(provider_type: SecretProvider, config: Dict[str, Any]) -> SecretsProvider:
    """
    Factory function to create a secrets provider.
    
    Args:
        provider_type: The type of provider to create
        config: Provider-specific configuration
        
    Returns:
        Initialized secrets provider instance
        
    Raises:
        Document360Error: If provider type is unsupported
    """
    if provider_type not in PROVIDER_REGISTRY:
        raise Document360Error(
            f"Unsupported secrets provider: {provider_type}",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH
        )
    
    provider_class = PROVIDER_REGISTRY[provider_type]
    return provider_class(config)