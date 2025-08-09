# this_file: external/int_folders/d361/src/d361/core/interfaces.py
"""
Core interfaces and protocols for the d361 package.

This module defines the hexagonal architecture ports - the contracts that
external adapters must implement to integrate with the core domain logic.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, AsyncIterator, Protocol, runtime_checkable

from pydantic import BaseModel

from .models import Article, Category, ProjectVersion


@runtime_checkable
class DataProvider(Protocol):
    """Protocol for data providers that can fetch Document360 content.
    
    This is the primary port for data access in our hexagonal architecture.
    Concrete implementations (adapters) include API, archive, and web scraping providers.
    """

    @abstractmethod
    async def get_article(self, article_id: int, **kwargs: Any) -> Article:
        """Fetch a single article by ID.
        
        Args:
            article_id: The unique identifier of the article
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Article: The requested article
            
        Raises:
            ArticleNotFoundError: If the article doesn't exist
            ProviderError: If the provider encounters an error
        """

    @abstractmethod
    async def list_articles(
        self,
        category_id: int | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> list[Article]:
        """List articles with optional filtering.
        
        Args:
            category_id: Filter by category ID
            status: Filter by publication status
            **kwargs: Additional provider-specific parameters
            
        Returns:
            list[Article]: List of articles matching the criteria
        """

    @abstractmethod
    async def stream_articles(self, **kwargs: Any) -> AsyncIterator[Article]:
        """Stream all articles for memory-efficient processing.
        
        Args:
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Article: Individual articles as they're processed
        """

    @abstractmethod
    async def get_category(self, category_id: int, **kwargs: Any) -> Category:
        """Fetch a single category by ID.
        
        Args:
            category_id: The unique identifier of the category
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Category: The requested category
        """

    @abstractmethod
    async def list_categories(self, **kwargs: Any) -> list[Category]:
        """List all categories.
        
        Args:
            **kwargs: Additional provider-specific parameters
            
        Returns:
            list[Category]: List of all categories
        """

    @abstractmethod
    async def get_project_version(self, **kwargs: Any) -> ProjectVersion:
        """Get project version information.
        
        Args:
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ProjectVersion: Current project version details
        """


@runtime_checkable
class ContentWriter(Protocol):
    """Protocol for content writers that can output content in various formats.
    
    This port defines how processed content can be written to different destinations
    like files, databases, or external systems.
    """

    @abstractmethod
    async def write_article(self, article: Article, destination: str, **kwargs: Any) -> bool:
        """Write an article to the specified destination.
        
        Args:
            article: The article to write
            destination: Target destination (file path, database, etc.)
            **kwargs: Additional writer-specific parameters
            
        Returns:
            bool: True if write was successful
        """

    @abstractmethod
    async def write_articles_batch(
        self, articles: list[Article], destination: str, **kwargs: Any
    ) -> dict[str, bool]:
        """Write multiple articles in a batch operation.
        
        Args:
            articles: List of articles to write
            destination: Target destination
            **kwargs: Additional writer-specific parameters
            
        Returns:
            dict[str, bool]: Mapping of article IDs to success status
        """


class ConvertedContent(BaseModel):
    """Result of a content conversion operation.
    
    This model represents the output from converter plugins,
    providing both the converted content and metadata about the conversion.
    """

    content: str
    """The converted content in the target format."""
    
    format: str
    """The target format (e.g., 'markdown', 'confluence', 'notion')."""
    
    metadata: dict[str, Any] = {}
    """Additional metadata about the conversion process."""
    
    source_format: str = "html"
    """The original format of the content."""
    
    warnings: list[str] = []
    """Any warnings generated during conversion."""


@runtime_checkable
class ConverterPlugin(Protocol):
    """Protocol for converter plugins that transform content between formats.
    
    Converter plugins allow extending the system with new output formats
    without modifying the core domain logic.
    """

    @abstractmethod
    def convert(self, content: str, **options: Any) -> ConvertedContent:
        """Convert content from one format to another.
        
        Args:
            content: Source content to convert
            **options: Conversion-specific options
            
        Returns:
            ConvertedContent: The converted content with metadata
        """

    @property
    @abstractmethod
    def supported_formats(self) -> tuple[str, str]:
        """Get the supported format conversion pair.
        
        Returns:
            tuple[str, str]: (source_format, target_format)
        """

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Get the plugin name for identification.
        
        Returns:
            str: Unique plugin identifier
        """


@runtime_checkable
class CacheProvider(Protocol):
    """Protocol for cache providers that can store and retrieve cached data.
    
    This port allows different caching backends (memory, disk, Redis, etc.)
    to be used interchangeably.
    """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            The cached value or None if not found
        """

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiration)
            
        Returns:
            bool: True if successful
        """

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value from the cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            bool: True if the key existed and was deleted
        """

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cached values.
        
        Returns:
            bool: True if successful
        """


@runtime_checkable
class SecretsProvider(Protocol):
    """Protocol for secrets providers that can retrieve sensitive configuration.
    
    This port allows integration with various secrets management systems
    like HashiCorp Vault, AWS Secrets Manager, or encrypted files.
    """

    @abstractmethod
    async def get_secret(self, key: str) -> str | None:
        """Retrieve a secret value.
        
        Args:
            key: Secret key identifier
            
        Returns:
            str | None: The secret value or None if not found
        """

    @abstractmethod
    async def list_secrets(self, prefix: str = "") -> list[str]:
        """List available secret keys.
        
        Args:
            prefix: Optional prefix to filter keys
            
        Returns:
            list[str]: List of available secret keys
        """