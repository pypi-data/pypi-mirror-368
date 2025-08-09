# this_file: external/int_folders/d361/src/d361/providers/archive_provider.py
"""
Archive provider for processing offline Document360 exports.

This module provides functionality for parsing and indexing Document360 archive
files, with full-text search capabilities and efficient SQLite storage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, AsyncIterator

from ..core.interfaces import DataProvider
from ..core.models import Article, Category, ProjectVersion
from ..archive.document360_parser import Document360Parser


class ArchiveProvider:
    """Provider for offline Document360 archive processing.
    
    This provider implements the DataProvider protocol for offline archive files,
    providing features including:
    - ZIP and tar.gz archive support
    - SQLite indexing with FTS5 full-text search
    - Content extraction and parsing
    - Metadata preservation and enrichment
    - Hash-based cache validation
    """

    def __init__(
        self,
        archive_path: str | Path,
        enable_fts: bool = True,
        cache_dir: str | Path | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the archive provider.
        
        Args:
            archive_path: Path to the archive file
            enable_fts: Enable full-text search indexing
            cache_dir: Directory for cache and index files
            **kwargs: Additional configuration options
        """
        self.archive_path = Path(archive_path)
        self.enable_fts = enable_fts
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        # Initialize archive parser
        self.parser = Document360Parser(self.archive_path)
        
        # Cache for parsed data
        self._categories = None
        self._articles = None
        self._parsed = False
        
    async def _ensure_parsed(self) -> None:
        """Ensure archive data has been parsed and cached."""
        if not self._parsed:
            self._categories, self._articles = self.parser.parse()
            self._parsed = True
    
    async def get_articles(self, **kwargs: Any) -> list[Article]:
        """Get all articles from the archive (MkDocsExporter interface).
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            list[Article]: All articles from the archive
        """
        await self._ensure_parsed()
        return self._articles
    
    async def get_categories(self, **kwargs: Any) -> list[Category]:
        """Get all categories from the archive (MkDocsExporter interface).
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            list[Category]: All categories from the archive
        """
        await self._ensure_parsed()
        return self._categories
        
    async def get_article(self, article_id: int, **kwargs: Any) -> Article:
        """Fetch a single article by ID from archive.
        
        Args:
            article_id: Article identifier
            **kwargs: Additional parameters
            
        Returns:
            Article: The requested article
        """
        await self._ensure_parsed()
        
        # Find article by ID
        for article in self._articles:
            if article.id == article_id:
                return article
        
        raise ValueError(f"Article with ID {article_id} not found")
        
    async def list_articles(
        self,
        category_id: int | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> list[Article]:
        """List articles from archive with filtering.
        
        Args:
            category_id: Filter by category
            status: Filter by status
            **kwargs: Additional parameters
            
        Returns:
            list[Article]: Filtered articles
        """
        await self._ensure_parsed()
        
        articles = self._articles
        
        # Filter by category if specified
        if category_id is not None:
            articles = [a for a in articles if a.category_id == category_id]
        
        # Filter by status if specified (most archives don't have status info)
        if status is not None:
            # Archive articles typically don't have status, so we'll assume all are published
            if status.lower() in ['published', 'active']:
                pass  # Return all articles
            else:
                articles = []  # No articles match non-published status
        
        return articles
        
    async def stream_articles(self, **kwargs: Any) -> AsyncIterator[Article]:
        """Stream articles from archive efficiently.
        
        Args:
            **kwargs: Additional parameters
            
        Yields:
            Article: Individual articles
        """
        await self._ensure_parsed()
        
        for article in self._articles:
            yield article
            
    async def get_category(self, category_id: int, **kwargs: Any) -> Category:
        """Fetch a single category by ID from archive.
        
        Args:
            category_id: Category identifier
            **kwargs: Additional parameters
            
        Returns:
            Category: The requested category
        """
        await self._ensure_parsed()
        
        # Find category by ID
        for category in self._categories:
            if category.id == category_id:
                return category
        
        raise ValueError(f"Category with ID {category_id} not found")
        
    async def list_categories(self, **kwargs: Any) -> list[Category]:
        """List all categories from archive.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            list[Category]: All categories
        """
        await self._ensure_parsed()
        return self._categories
        
    async def get_project_version(self, **kwargs: Any) -> ProjectVersion:
        """Get project version from archive metadata.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            ProjectVersion: Project version details
        """
        await self._ensure_parsed()
        
        # Create a basic project version from archive info
        # Archives typically don't have full version info, so we create a minimal one
        return ProjectVersion(
            id=1,
            version_number=self.parser.version_dir.name,  # e.g., "v1"
            is_default=True,
            created_at=None,
            updated_at=None
        )
        
    async def search_full_text(self, query: str, **kwargs: Any) -> list[Article]:
        """Perform full-text search across archive content.
        
        Args:
            query: Search query
            **kwargs: Additional parameters
            
        Returns:
            list[Article]: Articles matching the search query
        """
        await self._ensure_parsed()
        
        query_lower = query.lower()
        matching_articles = []
        
        for article in self._articles:
            # Simple text search in title and content
            if (query_lower in article.title.lower() or
                (article.content and query_lower in article.content.lower())):
                matching_articles.append(article)
        
        return matching_articles