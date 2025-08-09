# this_file: external/int_folders/d361/tests/test_integration_api.py
"""
Integration tests for d361 API client and related components.

This module provides integration testing of the API client with mock servers,
token management, error handling, and performance characteristics.
"""

import asyncio
import json
import pytest
from unittest.mock import patch, AsyncMock, Mock
from typing import Dict, List, Any
from datetime import datetime, timedelta

import httpx

from d361.api import (
    Document360ApiClient,
    TokenManager,
    TokenStats,
    RateLimiter,
    BulkOperationManager,
    SmartBulkProcessor,
    ChunkedDownloader,
    CircuitBreaker,
    DataSyncManager,
    ApiMetrics
)
from d361.api.errors import (
    Document360Error,
    AuthenticationError,
    RateLimitError,
    NotFoundError
)
from d361.core.models import Article, Category


class MockHttpServer:
    """Mock HTTP server for API testing."""
    
    def __init__(self):
        self.responses = {}
        self.request_count = 0
        self.request_log = []
        
    def add_response(self, method: str, path: str, response: Dict[str, Any], status_code: int = 200):
        """Add mock response for specific endpoint."""
        key = f"{method.upper()}:{path}"
        self.responses[key] = {
            "response": response,
            "status_code": status_code
        }
    
    def get_response(self, method: str, path: str) -> tuple:
        """Get mock response for request."""
        self.request_count += 1
        self.request_log.append(f"{method.upper()} {path}")
        
        key = f"{method.upper()}:{path}"
        if key in self.responses:
            mock_resp = self.responses[key]
            return mock_resp["response"], mock_resp["status_code"]
        
        # Default 404 response
        return {"error": "Not Found"}, 404


@pytest.fixture
def mock_server():
    """Create mock HTTP server for testing."""
    server = MockHttpServer()
    
    # Add common responses
    server.add_response("GET", "/api/v1/articles", {
        "data": [
            {
                "id": "article-1",
                "title": "Test Article 1",
                "content": "Content for article 1",
                "category_id": "cat-1",
                "status": "published",
                "created_at": "2025-01-01T00:00:00Z"
            },
            {
                "id": "article-2", 
                "title": "Test Article 2",
                "content": "Content for article 2",
                "category_id": "cat-1",
                "status": "published",
                "created_at": "2025-01-01T01:00:00Z"
            }
        ],
        "pagination": {
            "total": 2,
            "page": 1,
            "per_page": 10
        }
    })
    
    server.add_response("GET", "/api/v1/articles/article-1", {
        "data": {
            "id": "article-1",
            "title": "Test Article 1", 
            "content": "Content for article 1",
            "category_id": "cat-1",
            "status": "published",
            "created_at": "2025-01-01T00:00:00Z"
        }
    })
    
    server.add_response("GET", "/api/v1/categories", {
        "data": [
            {
                "id": "cat-1",
                "name": "Test Category 1",
                "slug": "test-category-1",
                "parent_id": None
            }
        ]
    })
    
    return server


class TestDocument360ApiClientIntegration:
    """Integration tests for Document360ApiClient."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_client_initialization(self):
        """Test API client initialization with real configuration."""
        from d361.config import ApiConfig
        
        config = ApiConfig(
            base_url="https://test-api.document360.com",
            api_tokens=["test-token-123"],
            timeout_seconds=30,
            max_retries=3
        )
        
        client = Document360ApiClient(config)
        
        assert client.config == config
        assert client.token_manager is not None
        assert client.rate_limiter is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_client_with_mock_server(self, mock_server):
        """Test API client with mock HTTP server."""
        from d361.config import ApiConfig
        
        config = ApiConfig(
            base_url="http://mock-server",
            api_tokens=["mock-token"],
            timeout_seconds=5
        )
        
        # Mock httpx client
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_server.get_response("GET", "/api/v1/articles")[0]
            mock_response.headers = {"x-ratelimit-remaining": "59"}
            
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            
            client = Document360ApiClient(config)
            
            # Test list articles
            articles = await client.list_articles()
            
            assert len(articles) == 2
            assert all(isinstance(article, Article) for article in articles)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_client_error_handling(self, mock_server):
        """Test API client error handling integration."""
        from d361.config import ApiConfig
        
        # Add error responses to mock server
        mock_server.add_response("GET", "/api/v1/articles/nonexistent", 
                                {"error": "Article not found"}, 404)
        
        config = ApiConfig(
            base_url="http://mock-server",
            api_tokens=["mock-token"]
        )
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Article not found"}
            
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            
            client = Document360ApiClient(config)
            
            with pytest.raises(NotFoundError):
                await client.get_article("nonexistent")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_client_authentication_flow(self):
        """Test authentication flow with token rotation."""
        from d361.config import ApiConfig
        
        config = ApiConfig(
            base_url="http://test-server",
            api_tokens=["token1", "token2", "token3"],
            token_rotation_enabled=True
        )
        
        client = Document360ApiClient(config)
        
        # Test token manager
        token1 = await client.token_manager.get_token()
        token2 = await client.token_manager.get_token()
        
        # Should rotate tokens
        assert isinstance(token1, str)
        assert isinstance(token2, str)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_client_rate_limiting(self):
        """Test rate limiting integration."""
        from d361.config import ApiConfig
        
        config = ApiConfig(
            base_url="http://test-server",
            api_tokens=["test-token"],
            requests_per_minute=5  # Very low for testing
        )
        
        client = Document360ApiClient(config)
        
        # Test rate limiter
        rate_limiter = client.rate_limiter
        
        # Should allow first few requests
        for i in range(3):
            allowed = await rate_limiter.can_proceed("test-token")
            assert allowed is True
            await rate_limiter.record_request("test-token")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_client_bulk_operations(self, mock_server):
        """Test bulk operations integration."""
        from d361.config import ApiConfig
        
        config = ApiConfig(
            base_url="http://mock-server",
            api_tokens=["bulk-token"],
            bulk_batch_size=5,
            bulk_concurrency=2
        )
        
        # Mock bulk responses
        for i in range(10):
            mock_server.add_response("GET", f"/api/v1/articles/bulk-{i}", {
                "data": {
                    "id": f"bulk-{i}",
                    "title": f"Bulk Article {i}",
                    "content": f"Bulk content {i}"
                }
            })
        
        client = Document360ApiClient(config)
        bulk_manager = BulkOperationManager(client)
        
        # Test bulk operation
        article_ids = [f"bulk-{i}" for i in range(5)]
        
        with patch.object(client, 'get_article') as mock_get:
            mock_get.side_effect = [
                Article(id=f"bulk-{i}", title=f"Bulk Article {i}", content=f"Content {i}")
                for i in range(5)
            ]
            
            results = await bulk_manager.bulk_fetch_articles(article_ids)
            
            assert len(results.successful) == 5
            assert len(results.failed) == 0


class TestTokenManagerIntegration:
    """Integration tests for TokenManager."""

    @pytest.mark.integration
    def test_token_manager_with_multiple_tokens(self):
        """Test token manager with multiple tokens."""
        tokens = ["token1", "token2", "token3"]
        
        manager = TokenManager(tokens)
        
        # Should have tokens loaded
        assert len(manager.tokens) == 3
        assert all(isinstance(stats, TokenStats) for stats in manager.tokens.values())

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_token_manager_load_balancing(self):
        """Test token manager load balancing."""
        tokens = ["token1", "token2", "token3"]
        manager = TokenManager(tokens)
        
        # Get tokens multiple times
        used_tokens = []
        for _ in range(9):  # 3 times more than tokens
            token = await manager.get_token()
            used_tokens.append(token)
        
        # Should distribute across all tokens
        unique_tokens = set(used_tokens)
        assert len(unique_tokens) == 3

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_token_manager_health_monitoring(self):
        """Test token health monitoring."""
        manager = TokenManager(["healthy-token", "unhealthy-token"])
        
        # Simulate successful request for healthy token
        await manager.record_success("healthy-token", response_time=0.1)
        
        # Simulate failed request for unhealthy token
        await manager.record_failure("unhealthy-token", Exception("API Error"))
        
        # Get health status
        health = manager.get_health()
        
        assert "healthy_tokens" in health
        assert "total_requests" in health

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_token_manager_stats_tracking(self):
        """Test token statistics tracking."""
        manager = TokenManager(["stats-token"])
        
        # Record various metrics
        await manager.record_success("stats-token", response_time=0.2)
        await manager.record_success("stats-token", response_time=0.3)
        await manager.record_failure("stats-token", Exception("Test error"))
        
        # Get token stats
        stats = manager.get_token_stats("stats-token")
        
        assert stats.total_requests == 3
        assert stats.successful_requests == 2
        assert stats.failed_requests == 1
        assert stats.average_response_time > 0


class TestCircuitBreakerIntegration:
    """Integration tests for CircuitBreaker."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_circuit_breaker_state_transitions(self):
        """Test circuit breaker state transitions."""
        from d361.api.circuit_breaker import CircuitBreakerConfig
        
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout_seconds=1,
            success_threshold=2
        )
        
        breaker = CircuitBreaker("test-service", config)
        
        # Initially closed
        assert breaker.state.name == "CLOSED"
        
        # Simulate failures
        for _ in range(3):
            await breaker.record_failure(Exception("Test failure"))
        
        # Should be open now
        assert breaker.state.name == "OPEN"
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Should be half-open
        assert breaker.state.name == "HALF_OPEN"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_circuit_breaker_with_api_client(self, mock_server):
        """Test circuit breaker integration with API client."""
        from d361.config import ApiConfig
        from d361.api.circuit_breaker import CircuitBreakerConfig
        
        # Configure circuit breaker with low thresholds
        breaker_config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout_seconds=1
        )
        
        config = ApiConfig(
            base_url="http://failing-server",
            api_tokens=["test-token"],
            circuit_breaker_enabled=True
        )
        
        client = Document360ApiClient(config)
        
        # Mock failing responses
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Server Error"}
            
            mock_httpx.return_value.__aenter__.return_value.get.side_effect = Exception("Connection failed")
            
            # Trigger circuit breaker
            for _ in range(3):
                try:
                    await client.get_article("test")
                except:
                    pass
            
            # Circuit should be open
            # Subsequent requests should fail fast


class TestDataSyncManagerIntegration:
    """Integration tests for DataSyncManager."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_sync_manager_deduplication(self):
        """Test data sync manager deduplication."""
        from d361.api.data_sync import SyncConfig
        
        config = SyncConfig(
            deduplication_strategy="content_hash",
            similarity_threshold=0.9
        )
        
        sync_manager = DataSyncManager(config)
        
        # Test articles with similar content
        articles = [
            Article(id="1", title="Article 1", content="This is test content"),
            Article(id="2", title="Article 2", content="This is test content"),  # Duplicate
            Article(id="3", title="Article 3", content="Different content")
        ]
        
        deduplicated = await sync_manager.deduplicate_articles(articles)
        
        # Should remove duplicate
        assert len(deduplicated) == 2
        
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_sync_manager_incremental_sync(self):
        """Test incremental synchronization."""
        from d361.api.data_sync import SyncConfig
        
        config = SyncConfig(
            incremental_sync=True,
            change_detection="timestamp"
        )
        
        sync_manager = DataSyncManager(config)
        
        # Initial dataset
        initial_articles = [
            Article(
                id="1",
                title="Article 1", 
                content="Content 1",
                updated_at=datetime(2025, 1, 1)
            )
        ]
        
        # Updated dataset
        updated_articles = [
            Article(
                id="1",
                title="Updated Article 1",
                content="Updated content 1", 
                updated_at=datetime(2025, 1, 2)
            ),
            Article(
                id="2",
                title="New Article 2",
                content="Content 2",
                updated_at=datetime(2025, 1, 2)
            )
        ]
        
        # Detect changes
        changes = await sync_manager.detect_changes(initial_articles, updated_articles)
        
        assert len(changes.updated) == 1  # Article 1 updated
        assert len(changes.added) == 1    # Article 2 added
        assert len(changes.deleted) == 0  # Nothing deleted


class TestApiMetricsIntegration:
    """Integration tests for ApiMetrics."""

    @pytest.mark.integration
    def test_api_metrics_collection(self):
        """Test API metrics collection integration."""
        from d361.api.metrics import MetricsConfig
        
        config = MetricsConfig(
            collection_enabled=True,
            buffer_size=100,
            flush_interval_seconds=1
        )
        
        metrics = ApiMetrics(config)
        
        # Record some metrics
        metrics.record_request("GET", "/articles", 200, 0.1, "test-token")
        metrics.record_request("GET", "/articles/1", 200, 0.2, "test-token")
        metrics.record_request("POST", "/articles", 201, 0.3, "test-token")
        
        # Get metrics summary
        summary = metrics.get_summary()
        
        assert summary["total_requests"] == 3
        assert summary["success_rate"] == 1.0
        assert "average_response_time" in summary

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_metrics_with_client(self, mock_server):
        """Test metrics collection with API client."""
        from d361.config import ApiConfig
        from d361.api.metrics import MetricsConfig
        
        metrics_config = MetricsConfig(collection_enabled=True)
        
        config = ApiConfig(
            base_url="http://mock-server",
            api_tokens=["metrics-token"]
        )
        
        client = Document360ApiClient(config)
        client.metrics = ApiMetrics(metrics_config)
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": {"id": "1", "title": "Test"}}
            mock_response.headers = {"x-ratelimit-remaining": "59"}
            
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Make requests
            await client.get_article("1")
            await client.get_article("2")
            
            # Check metrics
            summary = client.metrics.get_summary()
            assert summary["total_requests"] >= 2


class TestIntegrationEndToEnd:
    """End-to-end integration tests."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_api_workflow(self, mock_server):
        """Test complete API workflow integration."""
        from d361.config import ApiConfig
        
        # Configure realistic API client
        config = ApiConfig(
            base_url="http://mock-server",
            api_tokens=["workflow-token"],
            timeout_seconds=30,
            max_retries=3,
            requests_per_minute=60,
            circuit_breaker_enabled=True
        )
        
        client = Document360ApiClient(config)
        
        with patch("httpx.AsyncClient") as mock_httpx:
            # Mock successful responses
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"x-ratelimit-remaining": "59"}
            
            # Mock list articles response
            list_response = mock_server.get_response("GET", "/api/v1/articles")[0]
            mock_response.json.return_value = list_response
            
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Test workflow
            # 1. List articles
            articles = await client.list_articles()
            assert len(articles) > 0
            
            # 2. Get individual article
            first_article = articles[0]
            detailed_article = await client.get_article(first_article.id)
            assert detailed_article.id == first_article.id
            
            # 3. Check health
            health = await client.health_check()
            assert health is True
            
            # 4. Get statistics
            stats = client.get_statistics()
            assert "total_requests" in stats

    @pytest.mark.integration
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_high_load_integration(self):
        """Test API client under high load conditions."""
        from d361.config import ApiConfig
        
        config = ApiConfig(
            api_tokens=["load-test-token"],
            requests_per_minute=1000,  # High throughput
            bulk_concurrency=10
        )
        
        client = Document360ApiClient(config)
        
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": {"id": "test", "title": "Load Test"}}
            mock_response.headers = {"x-ratelimit-remaining": "59"}
            
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Simulate high load
            tasks = []
            for i in range(50):  # 50 concurrent requests
                task = asyncio.create_task(client.get_article(f"article-{i}"))
                tasks.append(task)
            
            # Wait for all requests
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Most should succeed
            successful = sum(1 for r in results if not isinstance(r, Exception))
            assert successful >= 45  # Allow for some failures

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self):
        """Test error recovery and resilience."""
        from d361.config import ApiConfig
        
        config = ApiConfig(
            api_tokens=["recovery-token"],
            max_retries=3,
            circuit_breaker_enabled=True
        )
        
        client = Document360ApiClient(config)
        
        with patch("httpx.AsyncClient") as mock_httpx:
            # Mock intermittent failures
            call_count = 0
            
            def mock_request(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                mock_response = Mock()
                
                if call_count <= 2:
                    # First two calls fail
                    mock_response.status_code = 500
                    mock_response.json.return_value = {"error": "Server Error"}
                else:
                    # Third call succeeds
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"data": {"id": "recovery", "title": "Recovered"}}
                    mock_response.headers = {"x-ratelimit-remaining": "59"}
                
                return mock_response
            
            mock_httpx.return_value.__aenter__.return_value.get.side_effect = mock_request
            
            # Should recover after retries
            article = await client.get_article("recovery")
            assert article.title == "Recovered"
            assert call_count == 3  # Took 3 attempts