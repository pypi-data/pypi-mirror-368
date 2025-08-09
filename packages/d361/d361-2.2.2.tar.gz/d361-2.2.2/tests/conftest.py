# this_file: external/int_folders/d361/tests/conftest.py
"""
Comprehensive pytest configuration and global fixtures.

This module provides global pytest fixtures for testing the d361 package,
including database setup, configuration management, mock services, and
test utilities for comprehensive test coverage.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, Generator, Optional, Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from loguru import logger

# Import d361 components for testing
from d361.core.models import Article, Category, ProjectVersion
from d361.core.transformers import ModelTransformer
from d361.config import AppConfig, Environment, ConfigLoader, SecretsManager
from d361.providers import MockProvider
from d361.archive import SqliteCache, ArchiveParser
from d361.api import Document360ApiClient, TokenManager
from d361.utils import ServiceContainer, LoggingManager, PerformanceOptimizer
from d361.plugins import PluginManager


# Test configuration constants
TEST_DB_NAME = "test_d361.db"
TEST_CONFIG_DIR = "test_config"
TEST_CACHE_SIZE = 100  # MB
TEST_API_TIMEOUT = 5  # seconds


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_data_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory(prefix="d361_test_") as temp_dir:
        test_dir = Path(temp_dir)
        
        # Create subdirectories
        (test_dir / "config").mkdir()
        (test_dir / "cache").mkdir()
        (test_dir / "logs").mkdir()
        (test_dir / "archives").mkdir()
        (test_dir / "secrets").mkdir()
        
        yield test_dir


@pytest.fixture(scope="session")  
def test_config(test_data_dir: Path) -> AppConfig:
    """Create test configuration with isolated paths."""
    config = AppConfig(
        app_name="d361-test",
        version="1.0.0-test",
        environment=Environment.TESTING,
        debug=True,
        data_dir=test_data_dir,
        config_dir=test_data_dir / "config",
        logs_dir=test_data_dir / "logs"
    )
    
    # Configure for testing
    config.api.timeout_seconds = TEST_API_TIMEOUT
    config.api.max_retries = 1
    config.cache.max_memory_mb = TEST_CACHE_SIZE
    config.cache.disk_cache_dir = test_data_dir / "cache"
    config.archive.cache_dir = test_data_dir / "archives"
    config.archive.temp_dir = test_data_dir / "temp"
    config.monitoring.log_level = "DEBUG"
    
    return config


@pytest.fixture
async def test_database(test_data_dir: Path) -> AsyncGenerator[Path, None]:
    """Create isolated test database."""
    db_path = test_data_dir / TEST_DB_NAME
    
    # Initialize database with test schema
    from d361.archive.schema import create_archive_schema
    await create_archive_schema(db_path)
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
async def sqlite_cache(test_database: Path, test_config: AppConfig) -> AsyncGenerator[SqliteCache, None]:
    """Create SQLite cache for testing."""
    cache = SqliteCache(
        db_path=test_database,
        max_size_mb=TEST_CACHE_SIZE,
        ttl_seconds=300
    )
    
    await cache.initialize()
    yield cache
    await cache.cleanup()


@pytest.fixture
def mock_api_client() -> Mock:
    """Create mock API client for testing."""
    client = Mock(spec=Document360ApiClient)
    
    # Configure common mock responses
    client.get_article.return_value = {
        "id": "test-article-1",
        "title": "Test Article",
        "content": "Test content",
        "status": "published"
    }
    
    client.list_articles.return_value = [
        {"id": "test-article-1", "title": "Test Article 1"},
        {"id": "test-article-2", "title": "Test Article 2"}
    ]
    
    client.health_check.return_value = True
    
    return client


@pytest.fixture
def mock_token_manager() -> Mock:
    """Create mock token manager for testing."""
    manager = Mock(spec=TokenManager)
    manager.get_token.return_value = "test-token-123"
    manager.get_health.return_value = {"healthy": True, "available_tokens": 1}
    return manager


@pytest.fixture
def mock_secrets_manager() -> AsyncMock:
    """Create mock secrets manager for testing."""
    manager = AsyncMock(spec=SecretsManager)
    
    async def mock_get_secret(secret_id: str):
        mock_secret = AsyncMock()
        mock_secret.value = f"test-secret-{secret_id}"
        mock_secret.is_valid.return_value = True
        return mock_secret
    
    manager.get_secret.side_effect = mock_get_secret
    manager.health_check.return_value = {"primary_provider": True}
    
    return manager


@pytest.fixture
async def config_loader(test_data_dir: Path) -> AsyncGenerator[ConfigLoader, None]:
    """Create configuration loader for testing."""
    loader = ConfigLoader(
        base_config_dir=test_data_dir / "config",
        environment_override="testing",
        enable_secrets=False,
        enable_hot_reload=False
    )
    
    yield loader
    await loader.cleanup()


@pytest.fixture
def mock_provider() -> MockProvider:
    """Create mock provider with test data."""
    provider = MockProvider(
        num_articles=5,
        num_categories=3,
        include_content=True
    )
    return provider


@pytest.fixture
def model_transformer() -> ModelTransformer:
    """Create model transformer for testing."""
    return ModelTransformer()


@pytest.fixture
def plugin_manager() -> PluginManager:
    """Create plugin manager for testing."""
    return PluginManager()


@pytest.fixture
def service_container() -> Generator[ServiceContainer, None, None]:
    """Create service container for dependency injection testing."""
    container = ServiceContainer()
    yield container
    container.clear()


@pytest.fixture
def performance_optimizer(test_data_dir: Path) -> PerformanceOptimizer:
    """Create performance optimizer for testing."""
    return PerformanceOptimizer(
        cache_dir=test_data_dir / "cache",
        max_cache_size_mb=TEST_CACHE_SIZE
    )


@pytest.fixture
def logging_manager(test_data_dir: Path) -> Generator[LoggingManager, None, None]:
    """Create logging manager for testing."""
    manager = LoggingManager()
    manager.setup_logging(
        level="DEBUG",
        format_type="console",
        log_file=test_data_dir / "logs" / "test.log"
    )
    
    yield manager
    
    # Cleanup
    logger.remove()


@pytest.fixture
def sample_article() -> Article:
    """Create sample article for testing."""
    return Article(
        id="test-article-1",
        title="Test Article",
        slug="test-article",
        content="This is test article content with **markdown** formatting.",
        category_id="test-category-1",
        status="published",
        author="Test Author",
        created_at="2025-01-01T00:00:00Z",
        updated_at="2025-01-01T00:00:00Z"
    )


@pytest.fixture
def sample_category() -> Category:
    """Create sample category for testing."""
    return Category(
        id="test-category-1",
        name="Test Category",
        slug="test-category",
        description="Test category description",
        parent_id=None,
        order=1
    )


@pytest.fixture
def sample_articles() -> list[Article]:
    """Create list of sample articles for testing."""
    return [
        Article(
            id=f"test-article-{i}",
            title=f"Test Article {i}",
            slug=f"test-article-{i}",
            content=f"Content for test article {i}",
            category_id="test-category-1",
            status="published"
        )
        for i in range(1, 6)
    ]


@pytest.fixture
def test_environment_vars() -> Generator[Dict[str, str], None, None]:
    """Set up test environment variables."""
    test_vars = {
        "D361_ENVIRONMENT": "testing",
        "D361_DEBUG": "true",
        "D361_API_TIMEOUT_SECONDS": str(TEST_API_TIMEOUT),
        "D361_SECRET_API_TOKEN": "test-token-123",
        "D361_SECRET_DATABASE_URL": "sqlite:///:memory:"
    }
    
    # Set environment variables
    original_vars = {}
    for key, value in test_vars.items():
        original_vars[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original environment
    for key in test_vars:
        if original_vars[key] is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_vars[key]


@pytest.fixture
def mock_archive_file(test_data_dir: Path) -> Path:
    """Create mock archive file for testing."""
    import zipfile
    import json
    
    archive_path = test_data_dir / "test_archive.zip"
    
    # Create test content
    test_content = {
        "articles": [
            {
                "id": "test-1",
                "title": "Test Article 1",
                "content": "Content 1",
                "category_id": "cat-1"
            },
            {
                "id": "test-2", 
                "title": "Test Article 2",
                "content": "Content 2",
                "category_id": "cat-1"
            }
        ],
        "categories": [
            {
                "id": "cat-1",
                "name": "Test Category",
                "slug": "test-category"
            }
        ]
    }
    
    # Create ZIP file
    with zipfile.ZipFile(archive_path, 'w') as zf:
        zf.writestr("articles.json", json.dumps(test_content["articles"], indent=2))
        zf.writestr("categories.json", json.dumps(test_content["categories"], indent=2))
        zf.writestr("metadata.json", json.dumps({"version": "1.0", "created": "2025-01-01"}))
    
    return archive_path


@pytest.fixture
async def archive_parser(test_data_dir: Path) -> ArchiveParser:
    """Create archive parser for testing."""
    parser = ArchiveParser(
        cache_dir=test_data_dir / "archives",
        temp_dir=test_data_dir / "temp"
    )
    await parser.initialize()
    return parser


# Test utilities
class TestHelpers:
    """Helper utilities for testing."""
    
    @staticmethod
    def create_test_config_file(config_dir: Path, filename: str, config_data: Dict[str, Any]) -> Path:
        """Create test configuration file."""
        config_path = config_dir / filename
        
        if filename.endswith('.json'):
            import json
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        elif filename.endswith(('.yml', '.yaml')):
            try:
                import yaml
                with open(config_path, 'w') as f:
                    yaml.dump(config_data, f, indent=2)
            except ImportError:
                pytest.skip("PyYAML not available for YAML config test")
        
        return config_path
    
    @staticmethod
    def create_test_env_file(config_dir: Path, env_vars: Dict[str, str]) -> Path:
        """Create test .env file."""
        env_path = config_dir / ".env"
        
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        return env_path
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1):
        """Wait for a condition to become true."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False


@pytest.fixture
def test_helpers() -> TestHelpers:
    """Provide test helper utilities."""
    return TestHelpers()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "api: marks tests that require API access")
    config.addinivalue_line("markers", "database: marks tests that require database")
    config.addinivalue_line("markers", "performance: marks performance/benchmark tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on test file location
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "test_unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "test_performance" in str(item.fspath) or "benchmark" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "test_database" in str(item.fspath) or "sql" in str(item.fspath):
            item.add_marker(pytest.mark.database)


# Async test support
@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for async testing."""
    return "asyncio"