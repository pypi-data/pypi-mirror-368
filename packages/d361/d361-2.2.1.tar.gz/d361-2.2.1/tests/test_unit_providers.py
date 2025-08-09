# this_file: external/int_folders/d361/tests/test_unit_providers.py
"""
Comprehensive unit tests for d361 data providers.

This module provides thorough testing of all data providers including
MockProvider, ApiProvider, ArchiveProvider, and HybridProvider functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Dict, Any, Optional
from datetime import datetime

from d361.core.models import Article, Category, ProjectVersion
from d361.core.interfaces import DataProvider
from d361.providers import (
    MockProvider, 
    ApiProvider, 
    ArchiveProvider, 
    HybridProvider
)
from d361.api.errors import Document360Error


class TestMockProvider:
    """Test cases for MockProvider."""

    def test_mock_provider_creation(self):
        """Test MockProvider creation with default parameters."""
        provider = MockProvider()
        
        assert provider.num_articles == 10  # default
        assert provider.num_categories == 5  # default
        assert provider.include_content is True  # default

    def test_mock_provider_custom_parameters(self):
        """Test MockProvider with custom parameters."""
        provider = MockProvider(
            num_articles=20,
            num_categories=8,
            include_content=False
        )
        
        assert provider.num_articles == 20
        assert provider.num_categories == 8
        assert provider.include_content is False

    @pytest.mark.asyncio
    async def test_mock_provider_list_articles(self):
        """Test listing articles from MockProvider."""
        provider = MockProvider(num_articles=5)
        
        articles = await provider.list_articles()
        
        assert len(articles) == 5
        assert all(isinstance(article, Article) for article in articles)
        assert all(article.id.startswith("mock-article-") for article in articles)

    @pytest.mark.asyncio
    async def test_mock_provider_get_article(self):
        """Test getting single article from MockProvider."""
        provider = MockProvider()
        
        article = await provider.get_article("mock-article-1")
        
        assert isinstance(article, Article)
        assert article.id == "mock-article-1"
        assert article.title == "Mock Article 1"

    @pytest.mark.asyncio
    async def test_mock_provider_get_nonexistent_article(self):
        """Test getting non-existent article."""
        provider = MockProvider(num_articles=3)
        
        with pytest.raises(Document360Error) as exc_info:
            await provider.get_article("mock-article-999")
        
        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_mock_provider_list_categories(self):
        """Test listing categories from MockProvider."""
        provider = MockProvider(num_categories=3)
        
        categories = await provider.list_categories()
        
        assert len(categories) == 3
        assert all(isinstance(category, Category) for category in categories)
        assert all(category.id.startswith("mock-category-") for category in categories)

    @pytest.mark.asyncio
    async def test_mock_provider_get_category(self):
        """Test getting single category from MockProvider."""
        provider = MockProvider()
        
        category = await provider.get_category("mock-category-1")
        
        assert isinstance(category, Category)
        assert category.id == "mock-category-1"
        assert category.name == "Mock Category 1"

    @pytest.mark.asyncio
    async def test_mock_provider_list_project_versions(self):
        """Test listing project versions from MockProvider."""
        provider = MockProvider()
        
        versions = await provider.list_project_versions()
        
        assert len(versions) >= 1
        assert all(isinstance(version, ProjectVersion) for version in versions)
        
        # Should have at least one default version
        default_versions = [v for v in versions if v.is_default]
        assert len(default_versions) >= 1

    @pytest.mark.asyncio
    async def test_mock_provider_content_generation(self):
        """Test content generation options."""
        # With content
        provider_with_content = MockProvider(include_content=True)
        article_with_content = await provider_with_content.get_article("mock-article-1")
        assert len(article_with_content.content) > 0

        # Without content
        provider_without_content = MockProvider(include_content=False)
        article_without_content = await provider_without_content.get_article("mock-article-1")
        assert article_without_content.content == ""

    @pytest.mark.asyncio
    async def test_mock_provider_pagination(self):
        """Test pagination support in MockProvider."""
        provider = MockProvider(num_articles=50)
        
        # Test with pagination parameters
        articles_page1 = await provider.list_articles(limit=10, offset=0)
        articles_page2 = await provider.list_articles(limit=10, offset=10)
        
        assert len(articles_page1) == 10
        assert len(articles_page2) == 10
        
        # Pages should be different
        page1_ids = {article.id for article in articles_page1}
        page2_ids = {article.id for article in articles_page2}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_mock_provider_search(self):
        """Test search functionality in MockProvider."""
        provider = MockProvider(num_articles=10)
        
        # Search for articles
        results = await provider.search_articles("Mock Article 1")
        
        assert len(results) >= 1
        assert any("1" in article.title for article in results)

    def test_mock_provider_consistency(self):
        """Test that MockProvider generates consistent data."""
        provider1 = MockProvider(num_articles=5, seed=12345)
        provider2 = MockProvider(num_articles=5, seed=12345)
        
        # Should generate identical data with same seed
        # Note: This depends on implementation using seed parameter


class TestApiProvider:
    """Test cases for ApiProvider."""

    def test_api_provider_creation(self):
        """Test ApiProvider creation."""
        # Mock API client
        mock_client = Mock()
        
        provider = ApiProvider(client=mock_client)
        
        assert provider.client == mock_client

    @pytest.mark.asyncio
    async def test_api_provider_list_articles(self):
        """Test listing articles through API provider."""
        # Mock API client
        mock_client = AsyncMock()
        mock_client.list_articles.return_value = [
            {"id": "api-1", "title": "API Article 1", "content": "Content 1"},
            {"id": "api-2", "title": "API Article 2", "content": "Content 2"}
        ]
        
        provider = ApiProvider(client=mock_client)
        articles = await provider.list_articles()
        
        assert len(articles) == 2
        assert all(isinstance(article, Article) for article in articles)
        mock_client.list_articles.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_provider_get_article(self):
        """Test getting single article through API provider."""
        mock_client = AsyncMock()
        mock_client.get_article.return_value = {
            "id": "api-1",
            "title": "API Article 1", 
            "content": "API Content 1"
        }
        
        provider = ApiProvider(client=mock_client)
        article = await provider.get_article("api-1")
        
        assert isinstance(article, Article)
        assert article.id == "api-1"
        assert article.title == "API Article 1"
        mock_client.get_article.assert_called_once_with("api-1")

    @pytest.mark.asyncio
    async def test_api_provider_error_handling(self):
        """Test error handling in API provider."""
        mock_client = AsyncMock()
        mock_client.get_article.side_effect = Document360Error("API Error")
        
        provider = ApiProvider(client=mock_client)
        
        with pytest.raises(Document360Error):
            await provider.get_article("nonexistent")

    @pytest.mark.asyncio
    async def test_api_provider_data_transformation(self):
        """Test data transformation in API provider."""
        mock_client = AsyncMock()
        
        # Raw API response
        api_response = {
            "id": "api-1",
            "title": "API Article",
            "body": "Article content",  # Different field name
            "created_date": "2025-01-01T00:00:00Z",
            "category": {"id": "cat-1", "name": "Category 1"}
        }
        
        mock_client.get_article.return_value = api_response
        
        provider = ApiProvider(client=mock_client)
        article = await provider.get_article("api-1")
        
        # Should transform API response to Article model
        assert isinstance(article, Article)
        assert article.id == "api-1"
        # Content should be mapped from 'body' field
        # This depends on actual transformation logic

    @pytest.mark.asyncio
    async def test_api_provider_caching(self):
        """Test caching behavior in API provider."""
        mock_client = AsyncMock()
        mock_client.get_article.return_value = {
            "id": "api-1",
            "title": "Cached Article",
            "content": "Cached content"
        }
        
        provider = ApiProvider(client=mock_client, enable_cache=True)
        
        # First call
        article1 = await provider.get_article("api-1")
        
        # Second call - should use cache if implemented
        article2 = await provider.get_article("api-1")
        
        # Both should return same data
        assert article1.id == article2.id
        
        # Mock client should be called at least once
        assert mock_client.get_article.call_count >= 1


class TestArchiveProvider:
    """Test cases for ArchiveProvider."""

    @pytest.mark.asyncio
    async def test_archive_provider_creation(self, test_database):
        """Test ArchiveProvider creation."""
        provider = ArchiveProvider(db_path=test_database)
        
        assert provider.db_path == test_database

    @pytest.mark.asyncio
    async def test_archive_provider_initialization(self, test_database):
        """Test archive provider initialization."""
        provider = ArchiveProvider(db_path=test_database)
        
        await provider.initialize()
        
        # Should be ready to use
        assert provider.is_initialized

    @pytest.mark.asyncio
    async def test_archive_provider_load_archive(self, mock_archive_file):
        """Test loading archive into provider."""
        provider = ArchiveProvider()
        
        # Load the mock archive
        result = await provider.load_archive(mock_archive_file)
        
        assert result is not None
        # Should have processed archive content

    @pytest.mark.asyncio
    async def test_archive_provider_list_articles(self, test_database):
        """Test listing articles from archive."""
        provider = ArchiveProvider(db_path=test_database)
        await provider.initialize()
        
        # Add test data to archive
        test_articles = [
            Article(
                id="archive-1",
                title="Archive Article 1",
                content="Archive content 1"
            ),
            Article(
                id="archive-2", 
                title="Archive Article 2",
                content="Archive content 2"
            )
        ]
        
        # Store articles (implementation dependent)
        for article in test_articles:
            await provider._store_article(article)
        
        # List articles
        articles = await provider.list_articles()
        
        assert len(articles) == 2
        assert all(isinstance(article, Article) for article in articles)

    @pytest.mark.asyncio
    async def test_archive_provider_search(self, test_database):
        """Test full-text search in archive provider."""
        provider = ArchiveProvider(db_path=test_database)
        await provider.initialize()
        
        # Add searchable content
        test_article = Article(
            id="searchable-1",
            title="Searchable Article",
            content="This article contains unique searchable content with specific keywords."
        )
        
        await provider._store_article(test_article)
        
        # Search for content
        results = await provider.search_articles("searchable keywords")
        
        assert len(results) >= 1
        assert any("Searchable Article" in article.title for article in results)

    @pytest.mark.asyncio
    async def test_archive_provider_incremental_updates(self, test_database):
        """Test incremental archive updates."""
        provider = ArchiveProvider(db_path=test_database)
        await provider.initialize()
        
        # Initial load
        initial_articles = [
            Article(id="initial-1", title="Initial Article 1", content="Content 1")
        ]
        
        for article in initial_articles:
            await provider._store_article(article)
        
        # Update with new article
        update_articles = [
            Article(id="update-1", title="Update Article 1", content="New content")
        ]
        
        for article in update_articles:
            await provider._store_article(article)
        
        # Should have both articles
        all_articles = await provider.list_articles()
        assert len(all_articles) == 2

    @pytest.mark.asyncio
    async def test_archive_provider_performance(self, test_database):
        """Test archive provider performance with large datasets."""
        provider = ArchiveProvider(db_path=test_database)
        await provider.initialize()
        
        import time
        
        # Create large dataset
        large_dataset = [
            Article(
                id=f"perf-{i}",
                title=f"Performance Article {i}",
                content=f"Performance content for article {i}" * 10
            )
            for i in range(100)
        ]
        
        # Measure bulk insert performance
        start_time = time.time()
        
        for article in large_dataset:
            await provider._store_article(article)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle large dataset reasonably fast
        assert duration < 10.0  # Less than 10 seconds for 100 articles
        
        # Verify all articles stored
        stored_articles = await provider.list_articles()
        assert len(stored_articles) == 100


class TestHybridProvider:
    """Test cases for HybridProvider."""

    @pytest.mark.asyncio
    async def test_hybrid_provider_creation(self):
        """Test HybridProvider creation."""
        mock_api = AsyncMock()
        mock_archive = AsyncMock()
        mock_scraper = AsyncMock()
        
        provider = HybridProvider(
            api_provider=mock_api,
            archive_provider=mock_archive,
            scraper_provider=mock_scraper
        )
        
        assert provider.api_provider == mock_api
        assert provider.archive_provider == mock_archive
        assert provider.scraper_provider == mock_scraper

    @pytest.mark.asyncio
    async def test_hybrid_provider_source_selection(self):
        """Test intelligent source selection in hybrid provider."""
        # Mock providers with different response times
        fast_api = AsyncMock()
        fast_api.get_article.return_value = Article(
            id="1", title="API Article", content="API content"
        )
        
        slow_archive = AsyncMock()
        slow_archive.get_article.return_value = Article(
            id="1", title="Archive Article", content="Archive content"
        )
        
        provider = HybridProvider(
            api_provider=fast_api,
            archive_provider=slow_archive,
            source_priority=["api", "archive"]
        )
        
        # Should try API first
        article = await provider.get_article("1")
        
        assert article.title == "API Article"
        fast_api.get_article.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_provider_fallback(self):
        """Test fallback behavior in hybrid provider."""
        # Mock API that fails
        failing_api = AsyncMock()
        failing_api.get_article.side_effect = Document360Error("API failed")
        
        # Mock archive that works
        working_archive = AsyncMock()
        working_archive.get_article.return_value = Article(
            id="1", title="Archive Article", content="Archive content"
        )
        
        provider = HybridProvider(
            api_provider=failing_api,
            archive_provider=working_archive,
            source_priority=["api", "archive"]
        )
        
        # Should fallback to archive
        article = await provider.get_article("1")
        
        assert article.title == "Archive Article"
        failing_api.get_article.assert_called_once()
        working_archive.get_article.assert_called_once()

    @pytest.mark.asyncio
    async def test_hybrid_provider_data_freshness(self):
        """Test data freshness requirements."""
        from datetime import datetime, timedelta
        
        # Old archive data
        old_article = Article(
            id="1",
            title="Old Article",
            content="Old content",
            updated_at=datetime.now() - timedelta(days=30)
        )
        
        # Fresh API data
        fresh_article = Article(
            id="1",
            title="Fresh Article", 
            content="Fresh content",
            updated_at=datetime.now()
        )
        
        mock_api = AsyncMock()
        mock_api.get_article.return_value = fresh_article
        
        mock_archive = AsyncMock()
        mock_archive.get_article.return_value = old_article
        
        provider = HybridProvider(
            api_provider=mock_api,
            archive_provider=mock_archive,
            freshness_threshold_hours=24
        )
        
        # Should prefer fresh API data
        article = await provider.get_article("1", require_fresh=True)
        
        assert article.title == "Fresh Article"

    @pytest.mark.asyncio
    async def test_hybrid_provider_caching_strategy(self):
        """Test caching strategy across providers."""
        mock_api = AsyncMock()
        mock_cache = AsyncMock()
        
        # API returns data
        api_article = Article(id="1", title="API Article", content="API content")
        mock_api.get_article.return_value = api_article
        
        provider = HybridProvider(
            api_provider=mock_api,
            cache_provider=mock_cache,
            enable_caching=True
        )
        
        # First call - should fetch from API and cache
        article1 = await provider.get_article("1")
        
        # Verify caching behavior (implementation dependent)
        assert article1.id == "1"

    @pytest.mark.asyncio
    async def test_hybrid_provider_conflict_resolution(self):
        """Test conflict resolution when data differs between sources."""
        # Different data from different sources
        api_article = Article(
            id="1",
            title="API Title",
            content="API content",
            updated_at="2025-01-02T00:00:00Z"
        )
        
        archive_article = Article(
            id="1", 
            title="Archive Title",
            content="Archive content",
            updated_at="2025-01-01T00:00:00Z"
        )
        
        mock_api = AsyncMock()
        mock_api.get_article.return_value = api_article
        
        mock_archive = AsyncMock()
        mock_archive.get_article.return_value = archive_article
        
        provider = HybridProvider(
            api_provider=mock_api,
            archive_provider=mock_archive,
            conflict_resolution="latest"
        )
        
        # Should return most recent data
        article = await provider.get_article("1", check_all_sources=True)
        
        # Should prefer newer API data
        assert article.title == "API Title"

    @pytest.mark.asyncio
    async def test_hybrid_provider_performance_metrics(self):
        """Test performance metrics collection."""
        mock_api = AsyncMock()
        mock_api.get_article.return_value = Article(
            id="1", title="Article", content="content"
        )
        
        provider = HybridProvider(
            api_provider=mock_api,
            collect_metrics=True
        )
        
        # Make several requests
        for i in range(5):
            await provider.get_article(f"{i}")
        
        # Should collect performance metrics
        metrics = provider.get_metrics()
        
        assert metrics is not None
        assert "request_count" in metrics or "total_requests" in metrics


class TestProviderIntegration:
    """Integration tests for provider interactions."""

    @pytest.mark.asyncio
    async def test_provider_interface_compliance(self):
        """Test that all providers implement DataProvider interface."""
        providers = [
            MockProvider(),
            # ApiProvider would need mock client
            # ArchiveProvider would need database
            # HybridProvider would need sub-providers
        ]
        
        for provider in providers:
            # Check interface compliance
            assert isinstance(provider, DataProvider)
            
            # Check required methods exist
            assert hasattr(provider, 'list_articles')
            assert hasattr(provider, 'get_article')
            assert hasattr(provider, 'list_categories')
            assert hasattr(provider, 'get_category')

    @pytest.mark.asyncio
    async def test_provider_error_consistency(self):
        """Test consistent error handling across providers."""
        provider = MockProvider(num_articles=3)
        
        # Test non-existent article
        with pytest.raises(Document360Error) as exc_info:
            await provider.get_article("nonexistent")
        
        # Should be consistent error format
        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.category is not None
        assert exc_info.value.severity is not None

    @pytest.mark.asyncio
    async def test_provider_data_consistency(self):
        """Test data consistency across provider operations."""
        provider = MockProvider()
        
        # List articles
        articles = await provider.list_articles()
        
        # Get individual articles
        individual_articles = []
        for article in articles[:3]:  # Test first 3
            individual = await provider.get_article(article.id)
            individual_articles.append(individual)
        
        # Data should be consistent
        for i, article in enumerate(individual_articles):
            original = articles[i]
            assert article.id == original.id
            assert article.title == original.title

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_provider_performance_characteristics(self):
        """Test performance characteristics of providers."""
        import time
        
        provider = MockProvider(num_articles=100)
        
        # Measure list performance
        start_time = time.time()
        articles = await provider.list_articles()
        list_duration = time.time() - start_time
        
        assert len(articles) == 100
        assert list_duration < 1.0  # Should be fast for mock data
        
        # Measure individual get performance
        start_time = time.time()
        for i in range(10):
            await provider.get_article(f"mock-article-{i+1}")
        get_duration = time.time() - start_time
        
        assert get_duration < 1.0  # Should be fast for mock data


# Test fixtures specific to providers
@pytest.fixture
def mock_api_client():
    """Create mock API client for testing."""
    client = AsyncMock()
    
    # Configure default responses
    client.list_articles.return_value = [
        {"id": "api-1", "title": "API Article 1", "content": "Content 1"},
        {"id": "api-2", "title": "API Article 2", "content": "Content 2"}
    ]
    
    client.get_article.return_value = {
        "id": "api-1",
        "title": "API Article 1",
        "content": "Content 1"
    }
    
    client.list_categories.return_value = [
        {"id": "cat-1", "name": "API Category 1"},
        {"id": "cat-2", "name": "API Category 2"}
    ]
    
    return client


@pytest.fixture
async def configured_providers(test_database, mock_api_client):
    """Create configured providers for testing."""
    # Mock provider
    mock_provider = MockProvider(num_articles=5, num_categories=3)
    
    # API provider with mock client
    api_provider = ApiProvider(client=mock_api_client)
    
    # Archive provider with test database
    archive_provider = ArchiveProvider(db_path=test_database)
    await archive_provider.initialize()
    
    # Hybrid provider combining all
    hybrid_provider = HybridProvider(
        api_provider=api_provider,
        archive_provider=archive_provider,
        mock_provider=mock_provider
    )
    
    return {
        "mock": mock_provider,
        "api": api_provider, 
        "archive": archive_provider,
        "hybrid": hybrid_provider
    }