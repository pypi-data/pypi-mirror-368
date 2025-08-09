# this_file: external/int_folders/d361/src/d361/providers/mock_provider.py
"""
Mock provider for testing and development.

This module provides a mock implementation of the DataProvider protocol
for use in testing, development, and demonstration scenarios.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, AsyncIterator

from ..core.interfaces import DataProvider
from ..core.models import Article, Category, ProjectVersion, PublishStatus


class MockProvider:
    """Mock provider for testing and development.
    
    This provider implements the DataProvider protocol with predictable,
    configurable mock data for testing and development purposes.
    """

    def __init__(
        self,
        simulate_delays: bool = False,
        delay_ms: int = 100,
        fail_probability: float = 0.0,
        **kwargs: Any,
    ) -> None:
        """Initialize the mock provider.
        
        Args:
            simulate_delays: Whether to simulate network delays
            delay_ms: Delay in milliseconds for simulated operations
            fail_probability: Probability of operations failing (0.0-1.0)
            **kwargs: Additional configuration options
        """
        self.simulate_delays = simulate_delays
        self.delay_ms = delay_ms
        self.fail_probability = fail_probability
        
        # Generate mock data
        self._mock_articles = self._generate_mock_articles()
        self._mock_categories = self._generate_mock_categories()
        self._mock_project = self._generate_mock_project()
        
    async def get_article(self, article_id: int, **kwargs: Any) -> Article:
        """Fetch a mock article by ID.
        
        Args:
            article_id: Article identifier
            **kwargs: Additional parameters
            
        Returns:
            Article: Mock article data
            
        Raises:
            ValueError: If article not found in mock data
        """
        await self._simulate_operation()
        
        for article in self._mock_articles:
            if article.id == article_id:
                return article
                
        raise ValueError(f"Article {article_id} not found in mock data")
        
    async def list_articles(
        self,
        category_id: int | None = None,
        status: str | None = None,
        **kwargs: Any,
    ) -> list[Article]:
        """List mock articles with optional filtering.
        
        Args:
            category_id: Filter by category
            status: Filter by status
            **kwargs: Additional parameters
            
        Returns:
            list[Article]: Filtered mock articles
        """
        await self._simulate_operation()
        
        articles = self._mock_articles
        
        if category_id is not None:
            articles = [a for a in articles if a.category_id == category_id]
            
        if status is not None:
            articles = [a for a in articles if a.status.value == status]
            
        return articles
        
    async def stream_articles(self, **kwargs: Any) -> AsyncIterator[Article]:
        """Stream mock articles.
        
        Args:
            **kwargs: Additional parameters
            
        Yields:
            Article: Individual mock articles
        """
        await self._simulate_operation()
        
        for article in self._mock_articles:
            if self.simulate_delays:
                await asyncio.sleep(self.delay_ms / 1000)
            yield article
            
    async def get_category(self, category_id: int, **kwargs: Any) -> Category:
        """Fetch a mock category by ID.
        
        Args:
            category_id: Category identifier
            **kwargs: Additional parameters
            
        Returns:
            Category: Mock category data
            
        Raises:
            ValueError: If category not found in mock data
        """
        await self._simulate_operation()
        
        for category in self._mock_categories:
            if category.id == category_id:
                return category
                
        raise ValueError(f"Category {category_id} not found in mock data")
        
    async def list_categories(self, **kwargs: Any) -> list[Category]:
        """List all mock categories.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            list[Category]: All mock categories
        """
        await self._simulate_operation()
        return self._mock_categories
        
    async def get_project_version(self, **kwargs: Any) -> ProjectVersion:
        """Get mock project version.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            ProjectVersion: Mock project version
        """
        await self._simulate_operation()
        return self._mock_project
        
    def _generate_mock_articles(self) -> list[Article]:
        """Generate mock article data."""
        now = datetime.now()
        
        return [
            Article(
                id=1,
                title="Getting Started Guide",
                slug="getting-started-guide",
                content="<h1>Welcome</h1><p>This is a comprehensive getting started guide...</p>",
                content_markdown="# Welcome\n\nThis is a comprehensive getting started guide...",
                excerpt="Learn the basics of Document360",
                category_id=1,
                status=PublishStatus.PUBLISHED,
                created_at=now,
                updated_at=now,
                author_name="John Doe",
                author_email="john@example.com",
                tags=["beginner", "tutorial"],
            ),
            Article(
                id=2,
                title="Advanced Configuration",
                slug="advanced-configuration", 
                content="<h1>Advanced Settings</h1><p>Configure advanced features...</p>",
                content_markdown="# Advanced Settings\n\nConfigure advanced features...",
                excerpt="Advanced configuration options",
                category_id=1,
                status=PublishStatus.PUBLISHED,
                created_at=now,
                updated_at=now,
                author_name="Jane Smith",
                author_email="jane@example.com",
                tags=["advanced", "configuration"],
            ),
            Article(
                id=3,
                title="API Reference",
                slug="api-reference",
                content="<h1>API Documentation</h1><p>Complete API reference...</p>",
                content_markdown="# API Documentation\n\nComplete API reference...",
                excerpt="Complete API documentation",
                category_id=2,
                status=PublishStatus.PUBLISHED,
                created_at=now,
                updated_at=now,
                author_name="Bob Wilson",
                author_email="bob@example.com",
                tags=["api", "reference"],
            ),
            Article(
                id=4,
                title="Draft Article",
                slug="draft-article",
                content="<h1>Work in Progress</h1><p>This article is still being written...</p>",
                content_markdown="# Work in Progress\n\nThis article is still being written...",
                excerpt="Article still in progress",
                category_id=1,
                status=PublishStatus.DRAFT,
                created_at=now,
                updated_at=now,
                author_name="Alice Brown",
                author_email="alice@example.com",
                tags=["draft"],
            ),
        ]
        
    def _generate_mock_categories(self) -> list[Category]:
        """Generate mock category data."""
        now = datetime.now()
        
        return [
            Category(
                id=1,
                name="User Guide",
                slug="user-guide",
                parent_id=None,
                order=1,
                level=0,
                path="User Guide",
                description="User documentation and guides",
                is_public=True,
                status=PublishStatus.PUBLISHED,
                created_at=now,
                updated_at=now,
                article_count=3,
                subcategory_count=0,
            ),
            Category(
                id=2,
                name="Developer Documentation",
                slug="developer-documentation",
                parent_id=None,
                order=2,
                level=0,
                path="Developer Documentation",
                description="Technical documentation for developers",
                is_public=True,
                status=PublishStatus.PUBLISHED,
                created_at=now,
                updated_at=now,
                article_count=1,
                subcategory_count=1,
            ),
            Category(
                id=3,
                name="API Reference",
                slug="api-reference",
                parent_id=2,
                order=1,
                level=1,
                path="Developer Documentation/API Reference",
                description="Complete API reference documentation",
                is_public=True,
                status=PublishStatus.PUBLISHED,
                created_at=now,
                updated_at=now,
                article_count=1,
                subcategory_count=0,
            ),
        ]
        
    def _generate_mock_project(self) -> ProjectVersion:
        """Generate mock project version data."""
        now = datetime.now()
        
        return ProjectVersion(
            id=1,
            name="Main Documentation",
            version_number="1.0.0",
            is_default=True,
            project_id=1,
            project_name="Mock Documentation Project",
            project_slug="mock-docs",
            created_at=now,
            updated_at=now,
            published_at=now,
            language_code="en",
            timezone="UTC",
            is_public=True,
            site_title="Mock Documentation",
            site_description="Mock documentation site for testing",
            total_articles=4,
            total_categories=3,
        )
        
    async def _simulate_operation(self) -> None:
        """Simulate operation delays and failures if configured."""
        # Simulate network delay
        if self.simulate_delays:
            await asyncio.sleep(self.delay_ms / 1000)
            
        # Simulate operation failures
        if self.fail_probability > 0:
            import random
            if random.random() < self.fail_probability:
                raise RuntimeError("Simulated operation failure")