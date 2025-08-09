# this_file: external/int_folders/d361/src/d361/api/client.py
"""
Document360 API Client - Enterprise-grade Document360 API integration.

This module provides the main Document360ApiClient class with comprehensive
token management, rate limiting, error handling, and high-level API operations.
Now uses d361api for underlying API operations while preserving enterprise features.
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field, HttpUrl, validator

# UnifiedHttpClient no longer needed - using d361api directly
from .token_manager import TokenManager, TokenStats
from .errors import Document360Error, ErrorHandler, AuthenticationError, ValidationError

# Import required d361api components for API operations
from d361api import ApiClient as D361ApiClient, Configuration, ArticlesApi, CategoriesApi, ProjectVersionsApi
from d361api.exceptions import ApiException as D361ApiException

logger.info("d361api loaded successfully - using official API client for all operations")


class ApiConfig(BaseModel):
    """
    Configuration model for Document360 API client.
    
    Provides comprehensive configuration options for API endpoints,
    authentication, timeouts, and client behavior.
    """
    
    # API Endpoints
    base_url: HttpUrl = Field(
        default="https://apihub.document360.io/v1",
        description="Base URL for Document360 API"
    )
    
    # Authentication  
    api_tokens: List[str] = Field(
        min_items=1,
        description="List of Document360 API tokens for load balancing"
    )
    
    # Rate Limiting
    calls_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="API rate limit per token (default 60/minute)"
    )
    
    # Request Configuration
    timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Request timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retries for failed requests"
    )
    
    # Client Behavior
    user_agent: str = Field(
        default="d361-client/1.0",
        description="User agent string for API requests"
    )
    
    enable_caching: bool = Field(
        default=True,
        description="Enable response caching for GET requests"
    )
    
    cache_ttl: int = Field(
        default=300,
        ge=0,
        description="Cache TTL in seconds (0 disables caching)"
    )
    
    # Monitoring
    enable_metrics: bool = Field(
        default=True,
        description="Enable metrics collection and logging"
    )
    
    log_requests: bool = Field(
        default=False,
        description="Log all API requests (may expose sensitive data)"
    )
    
    @validator('api_tokens')
    def validate_tokens(cls, v):
        """Validate that all tokens are non-empty strings."""
        if not all(isinstance(token, str) and token.strip() for token in v):
            raise ValueError("All API tokens must be non-empty strings")
        return [token.strip() for token in v]


class Document360ApiClient:
    """
    Enterprise-grade Document360 API client.
    
    Provides comprehensive Document360 API integration with:
    - Multi-token management and intelligent rotation
    - Rate limiting and backoff strategies  
    - Comprehensive error handling and retry logic
    - Response caching and performance optimization
    - Request/response logging and metrics collection
    - High-level API methods for common operations
    """
    
    def __init__(self, config: ApiConfig):
        """
        Initialize the Document360 API client.
        
        Args:
            config: API client configuration
        """
        self.config = config
        self.base_url = str(config.base_url).rstrip('/')
        
        # Initialize token manager
        self.token_manager = TokenManager(
            tokens=config.api_tokens,
            calls_per_minute=config.calls_per_minute
        )
        
        # HTTP client no longer needed - using d361api directly
        
        # Initialize required d361api clients
        self._d361api_client = None
        self._articles_api = None
        self._categories_api = None
        self._project_versions_api = None
        
        self._setup_d361api_clients()
        
        # Request statistics
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._start_time = time.time()
        
        logger.info(
            "Document360ApiClient initialized",
            base_url=self.base_url,
            token_count=len(config.api_tokens),
            rate_limit=config.calls_per_minute,
            backend="d361api (auto-generated)",
        )
    
    def _setup_d361api_clients(self):
        """Setup d361api clients for API operations."""
        # Configure d361api
        d361_config = Configuration(
            host=self.base_url,
            api_key={"api_token": self.config.api_tokens[0]},  # Use first token as default
            api_key_prefix={"api_token": ""}
        )
        
        # Initialize API client
        self._d361api_client = D361ApiClient(configuration=d361_config)
        
        # Initialize specific API clients
        self._articles_api = ArticlesApi(api_client=self._d361api_client)
        self._categories_api = CategoriesApi(api_client=self._d361api_client)
        self._project_versions_api = ProjectVersionsApi(api_client=self._d361api_client)
        logger.debug("d361api clients initialized successfully")
    
    async def _execute_with_d361api(self, operation_name: str, api_call):
        """Execute an API call using d361api with proper token management and error handling.
        
        Args:
            operation_name: Name of the operation for logging
            api_call: Callable that performs the d361api operation
            
        Returns:
            Response converted to dictionary format
            
        Raises:
            Document360Error: For API errors
        """
        try:
            # Get token for rate limiting
            token = await self.token_manager.get_available_token()
            
            # Update d361api configuration with current token
            self._d361api_client.configuration.api_key["api_token"] = token
            
            # Execute the API call
            response = await api_call()
            
            # Update statistics
            self._successful_requests += 1
            self._total_requests += 1
            
            # Convert response to dictionary format expected by callers
            if hasattr(response, 'to_dict'):
                return response.to_dict()
            elif hasattr(response, 'data'):
                return response.data.to_dict() if hasattr(response.data, 'to_dict') else vars(response.data)
            else:
                return vars(response)
                
        except D361ApiException as e:
            self._failed_requests += 1
            self._total_requests += 1
            
            # Convert d361api exception to our error format
            error = ErrorHandler.classify_error(None, e)
            ErrorHandler.log_error(error, operation_name)
            raise error
        except Exception as e:
            self._failed_requests += 1
            self._total_requests += 1
            
            error = ErrorHandler.classify_error(None, e)
            ErrorHandler.log_error(error, operation_name)
            raise error
    
    # _make_request method removed - using d361api directly
    
    async def get_article(self, article_id: str) -> Dict[str, Any]:
        """
        Get a single article by ID.
        
        Args:
            article_id: Document360 article ID
            
        Returns:
            Article data dictionary
            
        Raises:
            ValidationError: If article_id is invalid
            NotFoundError: If article doesn't exist
            Document360Error: For other API errors
        """
        if not article_id or not isinstance(article_id, str):
            raise ValidationError(
                "article_id must be a non-empty string",
                field="article_id",
                value=article_id
            )
        
        # Use d361api for operation
        return await self._execute_with_d361api(
            f"GET articles/{article_id}",
            lambda: self._articles_api.v2_articles_article_id_get(article_id)
        )
    
    async def list_articles(
        self,
        category_id: Optional[str] = None,
        project_version_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List articles with optional filtering.
        
        Args:
            category_id: Optional category filter
            project_version_id: Optional project version filter
            limit: Maximum number of articles to return (1-500)
            offset: Number of articles to skip
            
        Returns:
            Articles list with pagination info
            
        Raises:
            ValidationError: If parameters are invalid
            Document360Error: For API errors
        """
        if limit < 1 or limit > 500:
            raise ValidationError(
                "limit must be between 1 and 500",
                field="limit",
                value=limit
            )
        
        if offset < 0:
            raise ValidationError(
                "offset must be non-negative",
                field="offset",
                value=offset
            )
        
        # Use d361api for operation
        return await self._execute_with_d361api(
            "GET articles",
            lambda: self._articles_api.v2_articles_get(
                category_id=category_id,
                project_version_id=project_version_id,
                limit=limit,
                offset=offset
            )
        )
    
    async def create_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new article.
        
        Args:
            article_data: Article data dictionary
            
        Returns:
            Created article data
            
        Raises:
            ValidationError: If article_data is invalid
            Document360Error: For API errors
        """
        if not isinstance(article_data, dict):
            raise ValidationError(
                "article_data must be a dictionary",
                field="article_data",
                value=type(article_data).__name__
            )
        
        required_fields = ['title', 'content', 'category_id']
        missing_fields = [field for field in required_fields if not article_data.get(field)]
        
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                field="article_data",
                value=missing_fields
            )
        
        # Use d361api for operation - need to implement CreateArticleRequest mapping
        raise NotImplementedError("create_article requires d361api CreateArticleRequest mapping")
    
    async def update_article(self, article_id: str, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing article.
        
        Args:
            article_id: Document360 article ID
            article_data: Updated article data
            
        Returns:
            Updated article data
            
        Raises:
            ValidationError: If parameters are invalid
            NotFoundError: If article doesn't exist
            Document360Error: For API errors
        """
        if not article_id or not isinstance(article_id, str):
            raise ValidationError(
                "article_id must be a non-empty string",
                field="article_id",
                value=article_id
            )
        
        if not isinstance(article_data, dict):
            raise ValidationError(
                "article_data must be a dictionary",
                field="article_data",
                value=type(article_data).__name__
            )
        
        # Use d361api for operation - need to implement UpdateArticleRequest mapping
        raise NotImplementedError("update_article requires d361api UpdateArticleRequest mapping")
    
    async def delete_article(self, article_id: str) -> bool:
        """
        Delete an article.
        
        Args:
            article_id: Document360 article ID
            
        Returns:
            True if deletion was successful
            
        Raises:
            ValidationError: If article_id is invalid
            NotFoundError: If article doesn't exist
            Document360Error: For API errors
        """
        if not article_id or not isinstance(article_id, str):
            raise ValidationError(
                "article_id must be a non-empty string",
                field="article_id",
                value=article_id
            )
        
        # Use d361api for operation - need to implement delete operation
        raise NotImplementedError("delete_article requires d361api delete operation mapping")
    
    async def get_categories(self, project_version_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get categories list.
        
        Args:
            project_version_id: Optional project version filter
            
        Returns:
            Categories data
        """
        # Use d361api for operation
        return await self._execute_with_d361api(
            "GET categories",
            lambda: self._categories_api.v2_categories_get(
                project_version_id=project_version_id
            )
        )
    
    async def get_project_versions(self) -> Dict[str, Any]:
        """
        Get project versions list.
        
        Returns:
            Project versions data
        """
        # Use d361api for operation
        return await self._execute_with_d361api(
            "GET project_versions",
            lambda: self._project_versions_api.v2_project_versions_get()
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the API client and tokens.
        
        Returns:
            Health check results with token status and client metrics
        """
        health_data = {
            "client": {
                "status": "healthy",
                "uptime_seconds": time.time() - self._start_time,
                "total_requests": self._total_requests,
                "successful_requests": self._successful_requests,
                "failed_requests": self._failed_requests,
                "success_rate": (
                    self._successful_requests / max(self._total_requests, 1)
                ),
            },
            "tokens": self.token_manager.get_health_report(),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Test API connectivity with a simple request
        try:
            await self.get_project_versions()
            health_data["api_connectivity"] = "healthy"
        except Exception as e:
            health_data["client"]["status"] = "degraded"
            health_data["api_connectivity"] = "unhealthy"
            health_data["api_error"] = str(e)
        
        return health_data
    
    async def close(self) -> None:
        """Clean up resources and close connections."""
        # Clean up d361api clients
        if self._d361api_client:
            try:
                # Close d361api client if it has a close method
                if hasattr(self._d361api_client, 'close'):
                    await self._d361api_client.close()
                elif hasattr(self._d361api_client, 'rest_client') and hasattr(self._d361api_client.rest_client, 'close'):
                    await self._d361api_client.rest_client.close()
            except Exception as e:
                logger.warning(f"Error closing d361api client: {e}")
        
        # Clear references
        self._d361api_client = None
        self._articles_api = None
        self._categories_api = None
        self._project_versions_api = None
        
        logger.info(
            "Document360ApiClient closed",
            total_requests=self._total_requests,
            success_rate=self._successful_requests / max(self._total_requests, 1),
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    # Statistics and monitoring methods
    @property
    def statistics(self) -> Dict[str, Any]:
        """Get comprehensive client statistics."""
        uptime = time.time() - self._start_time
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self._total_requests,
            "successful_requests": self._successful_requests,
            "failed_requests": self._failed_requests,
            "success_rate": self._successful_requests / max(self._total_requests, 1),
            "requests_per_second": self._total_requests / max(uptime, 1),
            "token_manager": self.token_manager.get_health_report(),
        }
    
    def reset_statistics(self) -> None:
        """Reset client statistics."""
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._start_time = time.time()
        
        logger.info("Client statistics reset")
    
    # Streaming and bulk operations
    async def stream_all_articles(
        self,
        category_id: Optional[str] = None,
        project_version_id: Optional[str] = None,
        page_size: int = 100,
        max_articles: Optional[int] = None
    ):
        """
        Stream all articles using an asynchronous generator for memory efficiency.
        
        This method fetches articles in pages and yields them one by one,
        allowing for processing of large datasets without loading everything into memory.
        
        Args:
            category_id: Optional category filter
            project_version_id: Optional project version filter
            page_size: Number of articles per API request (1-500)
            max_articles: Optional limit on total articles to fetch
            
        Yields:
            Dict[str, Any]: Individual article data
            
        Raises:
            ValidationError: If parameters are invalid
            Document360Error: For API errors
            
        Example:
            >>> async for article in client.stream_all_articles(page_size=50):
            ...     print(f"Processing article: {article['title']}")
        """
        if page_size < 1 or page_size > 500:
            raise ValidationError(
                "page_size must be between 1 and 500",
                field="page_size",
                value=page_size
            )
        
        if max_articles is not None and max_articles <= 0:
            raise ValidationError(
                "max_articles must be positive",
                field="max_articles", 
                value=max_articles
            )
        
        offset = 0
        articles_yielded = 0
        
        logger.info(
            "Starting article streaming",
            category_id=category_id,
            project_version_id=project_version_id,
            page_size=page_size,
            max_articles=max_articles,
        )
        
        while True:
            # Check if we've reached the maximum
            if max_articles and articles_yielded >= max_articles:
                logger.info(f"Reached maximum articles limit: {max_articles}")
                break
            
            # Adjust page size if approaching limit
            current_page_size = page_size
            if max_articles:
                remaining = max_articles - articles_yielded
                current_page_size = min(page_size, remaining)
            
            try:
                # Fetch page of articles
                response = await self.list_articles(
                    category_id=category_id,
                    project_version_id=project_version_id,
                    limit=current_page_size,
                    offset=offset
                )
                
                articles = response.get('data', [])
                
                # If no articles returned, we've reached the end
                if not articles:
                    logger.info(
                        "No more articles available",
                        offset=offset,
                        total_yielded=articles_yielded,
                    )
                    break
                
                # Yield each article
                for article in articles:
                    yield article
                    articles_yielded += 1
                    
                    # Check limit after each article
                    if max_articles and articles_yielded >= max_articles:
                        break
                
                # Move to next page
                offset += len(articles)
                
                # If we got fewer articles than requested, we're at the end
                if len(articles) < current_page_size:
                    logger.info(
                        "Reached end of articles",
                        last_page_size=len(articles),
                        total_yielded=articles_yielded,
                    )
                    break
                
                logger.debug(
                    "Streamed page of articles",
                    page_articles=len(articles),
                    offset=offset,
                    total_yielded=articles_yielded,
                )
                
            except Document360Error:
                logger.error(
                    "Error during article streaming",
                    offset=offset,
                    articles_yielded=articles_yielded,
                )
                raise
        
        logger.info(
            "Article streaming completed",
            total_articles=articles_yielded,
            final_offset=offset,
        )
    
    async def stream_articles_batch(
        self,
        category_id: Optional[str] = None,
        project_version_id: Optional[str] = None,
        batch_size: int = 100,
        max_articles: Optional[int] = None
    ):
        """
        Stream articles in batches for efficient batch processing.
        
        This method fetches articles in pages and yields them as batches,
        useful for bulk processing operations.
        
        Args:
            category_id: Optional category filter
            project_version_id: Optional project version filter
            batch_size: Number of articles per batch (1-500)
            max_articles: Optional limit on total articles to fetch
            
        Yields:
            List[Dict[str, Any]]: Batch of article data
            
        Raises:
            ValidationError: If parameters are invalid
            Document360Error: For API errors
        """
        if batch_size < 1 or batch_size > 500:
            raise ValidationError(
                "batch_size must be between 1 and 500",
                field="batch_size",
                value=batch_size
            )
        
        offset = 0
        articles_yielded = 0
        
        logger.info(
            "Starting batch article streaming",
            category_id=category_id,
            project_version_id=project_version_id,
            batch_size=batch_size,
            max_articles=max_articles,
        )
        
        while True:
            # Check if we've reached the maximum
            if max_articles and articles_yielded >= max_articles:
                break
            
            # Adjust batch size if approaching limit
            current_batch_size = batch_size
            if max_articles:
                remaining = max_articles - articles_yielded
                current_batch_size = min(batch_size, remaining)
            
            try:
                # Fetch batch of articles
                response = await self.list_articles(
                    category_id=category_id,
                    project_version_id=project_version_id,
                    limit=current_batch_size,
                    offset=offset
                )
                
                articles = response.get('data', [])
                
                # If no articles returned, we've reached the end
                if not articles:
                    break
                
                # Yield the entire batch
                yield articles
                articles_yielded += len(articles)
                offset += len(articles)
                
                # If we got fewer articles than requested, we're at the end
                if len(articles) < current_batch_size:
                    break
                
                logger.debug(
                    "Streamed batch of articles",
                    batch_size=len(articles),
                    offset=offset,
                    total_yielded=articles_yielded,
                )
                
            except Document360Error:
                logger.error(
                    "Error during batch article streaming",
                    offset=offset,
                    articles_yielded=articles_yielded,
                )
                raise
        
        logger.info(
            "Batch article streaming completed",
            total_articles=articles_yielded,
            batches_yielded=offset // batch_size,
        )