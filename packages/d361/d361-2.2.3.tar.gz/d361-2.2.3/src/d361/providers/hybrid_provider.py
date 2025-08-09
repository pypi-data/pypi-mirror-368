# this_file: external/int_folders/d361/src/d361/providers/hybrid_provider.py
"""
Hybrid provider combining multiple data sources intelligently.

This module provides a smart provider that can source data from API, archives,
or web scraping based on data freshness requirements, availability, and performance.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field

from ..core.interfaces import DataProvider
from ..core.models import Article, Category, ProjectVersion
from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity
from .api_provider import ApiProvider
from .archive_provider import ArchiveProvider


class DataSource(str, Enum):
    """Available data sources."""
    API = "api"
    ARCHIVE = "archive"
    SCRAPER = "scraper"
    CACHE = "cache"


class FreshnessRequirement(str, Enum):
    """Data freshness requirements."""
    REALTIME = "realtime"      # Must be < 5 minutes old
    FRESH = "fresh"           # Must be < 1 hour old  
    RECENT = "recent"         # Must be < 24 hours old
    CACHED = "cached"         # Can use any cached data
    ANY = "any"              # Any available data


@dataclass
class SourceMetrics:
    """Metrics for a data source."""
    availability: float = 1.0      # 0-1, availability score
    latency_ms: float = 0.0       # Average response latency
    error_rate: float = 0.0       # 0-1, error rate
    last_success: Optional[datetime] = None
    last_error: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0


@dataclass
class DataRequest:
    """Request for data with sourcing preferences."""
    content_type: str
    identifier: Union[int, str]
    freshness: FreshnessRequirement = FreshnessRequirement.RECENT
    preferred_sources: List[DataSource] = field(default_factory=list)
    fallback_sources: List[DataSource] = field(default_factory=list)
    max_sources: int = 3
    timeout_seconds: float = 30.0


class HybridConfig(BaseModel):
    """Configuration for hybrid provider."""
    
    # Freshness settings
    max_age_hours: int = Field(default=24, ge=1, description="Maximum age for cached data")
    realtime_threshold_minutes: int = Field(default=5, ge=1, description="Threshold for realtime data")
    fresh_threshold_hours: int = Field(default=1, ge=1, description="Threshold for fresh data")
    
    # Source preferences
    default_source_priority: List[DataSource] = Field(
        default=[DataSource.API, DataSource.ARCHIVE, DataSource.SCRAPER],
        description="Default source priority order"
    )
    
    # Performance settings
    parallel_requests: bool = Field(default=True, description="Enable parallel source requests")
    max_concurrent_sources: int = Field(default=2, ge=1, le=5, description="Max concurrent source requests")
    source_timeout: float = Field(default=30.0, ge=1.0, description="Timeout per source in seconds")
    
    # Fallback behavior
    enable_fallback: bool = Field(default=True, description="Enable fallback to other sources")
    min_sources_required: int = Field(default=1, ge=1, description="Minimum sources that must succeed")
    
    # Conflict resolution
    conflict_resolution_strategy: str = Field(
        default="newest_first",
        description="Strategy for resolving data conflicts"
    )
    
    # Quality thresholds
    min_content_quality: float = Field(
        default=0.7, ge=0.0, le=1.0,
        description="Minimum quality threshold for content"
    )


class HybridProvider(DataProvider):
    """
    Intelligent hybrid data provider.
    
    Combines multiple data sources (API, archives, web scraping) with smart
    routing, fallback handling, conflict resolution, and performance optimization
    to provide reliable, fresh data with optimal performance characteristics.
    """
    
    def __init__(
        self,
        config: Optional[HybridConfig] = None,
        api_provider: Optional[ApiProvider] = None,
        archive_provider: Optional[ArchiveProvider] = None,
        scraper_provider: Optional[Any] = None,  # ScraperProvider when implemented
    ) -> None:
        """Initialize the hybrid provider.
        
        Args:
            config: Hybrid provider configuration
            api_provider: API provider instance
            archive_provider: Archive provider instance
            scraper_provider: Web scraper provider instance
        """
        self.config = config or HybridConfig()
        self.api_provider = api_provider
        self.archive_provider = archive_provider
        self.scraper_provider = scraper_provider
        
        # Source metrics tracking
        self.source_metrics: Dict[DataSource, SourceMetrics] = {
            DataSource.API: SourceMetrics(),
            DataSource.ARCHIVE: SourceMetrics(),
            DataSource.SCRAPER: SourceMetrics(),
        }
        
        # Internal cache for resolved data
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(
            "HybridProvider initialized",
            sources={
                "api": api_provider is not None,
                "archive": archive_provider is not None,
                "scraper": scraper_provider is not None
            },
            config=self.config.dict()
        )
        
    async def get_article(self, article_id: int, **kwargs: Any) -> Article:
        """Fetch article using the best available source.
        
        Args:
            article_id: Article identifier
            **kwargs: Additional parameters including freshness requirements
            
        Returns:
            Article: The requested article from the best source
            
        Raises:
            Document360Error: If no source can provide the article
        """
        freshness = kwargs.get("freshness", FreshnessRequirement.RECENT)
        
        request = DataRequest(
            content_type="article",
            identifier=article_id,
            freshness=freshness,
            preferred_sources=kwargs.get("preferred_sources", []),
            fallback_sources=kwargs.get("fallback_sources", [])
        )
        
        try:
            result = await self._fetch_with_strategy(request, self._fetch_article_from_source)
            return result
        except Exception as e:
            error_msg = f"Failed to fetch article {article_id} from any source: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.DATA_ACCESS,
                severity=ErrorSeverity.HIGH
            )
        
    async def list_articles(
        self,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Article]:
        """List articles using the best available source.
        
        Args:
            category_id: Filter by category
            status: Filter by status
            **kwargs: Additional parameters
            
        Returns:
            List[Article]: Articles from the best available source
        """
        freshness = kwargs.get("freshness", FreshnessRequirement.RECENT)
        
        request = DataRequest(
            content_type="articles",
            identifier=f"list_{category_id}_{status}",
            freshness=freshness,
            preferred_sources=kwargs.get("preferred_sources", []),
            fallback_sources=kwargs.get("fallback_sources", [])
        )
        
        try:
            result = await self._fetch_with_strategy(
                request, 
                lambda source, req: self._fetch_articles_list_from_source(
                    source, req, category_id, status, **kwargs
                )
            )
            return result
        except Exception as e:
            logger.error(f"Failed to list articles from any source: {e}")
            return []  # Return empty list on failure
        
    async def stream_articles(self, **kwargs: Any) -> AsyncIterator[Article]:
        """Stream articles from the most appropriate source.
        
        Args:
            **kwargs: Additional parameters
            
        Yields:
            Article: Individual articles
        """
        freshness = kwargs.get("freshness", FreshnessRequirement.RECENT)
        sources = self._determine_source_priority(freshness)
        
        for source in sources:
            try:
                async for article in self._stream_from_source(source, **kwargs):
                    yield article
                return  # Successfully streamed from this source
            except Exception as e:
                logger.warning(f"Failed to stream from {source}: {e}")
                continue
        
        logger.error("Failed to stream articles from any source")
            
    async def get_category(self, category_id: int, **kwargs: Any) -> Category:
        """Fetch category using the best available source.
        
        Args:
            category_id: Category identifier
            **kwargs: Additional parameters
            
        Returns:
            Category: The requested category
        """
        freshness = kwargs.get("freshness", FreshnessRequirement.RECENT)
        
        request = DataRequest(
            content_type="category",
            identifier=category_id,
            freshness=freshness,
            preferred_sources=kwargs.get("preferred_sources", []),
            fallback_sources=kwargs.get("fallback_sources", [])
        )
        
        try:
            result = await self._fetch_with_strategy(request, self._fetch_category_from_source)
            return result
        except Exception as e:
            error_msg = f"Failed to fetch category {category_id} from any source: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.DATA_ACCESS,
                severity=ErrorSeverity.HIGH
            )
        
    async def list_categories(self, **kwargs: Any) -> List[Category]:
        """List categories using the best available source.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            List[Category]: Categories from the best source
        """
        freshness = kwargs.get("freshness", FreshnessRequirement.RECENT)
        
        request = DataRequest(
            content_type="categories",
            identifier="list_all",
            freshness=freshness,
            preferred_sources=kwargs.get("preferred_sources", []),
            fallback_sources=kwargs.get("fallback_sources", [])
        )
        
        try:
            result = await self._fetch_with_strategy(request, self._fetch_categories_list_from_source)
            return result
        except Exception as e:
            logger.error(f"Failed to list categories from any source: {e}")
            return []  # Return empty list on failure
        
    async def get_project_version(self, **kwargs: Any) -> ProjectVersion:
        """Get project version using the best available source.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            ProjectVersion: Project version details
        """
        freshness = kwargs.get("freshness", FreshnessRequirement.RECENT)
        
        request = DataRequest(
            content_type="project_version",
            identifier="current",
            freshness=freshness,
            preferred_sources=kwargs.get("preferred_sources", []),
            fallback_sources=kwargs.get("fallback_sources", [])
        )
        
        try:
            result = await self._fetch_with_strategy(request, self._fetch_project_version_from_source)
            return result
        except Exception as e:
            error_msg = f"Failed to fetch project version from any source: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.DATA_ACCESS,
                severity=ErrorSeverity.HIGH
            )
    
    async def _fetch_with_strategy(
        self, 
        request: DataRequest, 
        fetch_func: Any
    ) -> Any:
        """Execute fetch with intelligent source strategy.
        
        Args:
            request: Data request with preferences
            fetch_func: Function to fetch from specific source
            
        Returns:
            The fetched data from the best available source
        """
        # Check cache first if freshness allows
        if request.freshness in [FreshnessRequirement.CACHED, FreshnessRequirement.ANY]:
            cached_data = self._get_cached_data(request)
            if cached_data is not None:
                logger.debug(f"Returning cached data for {request.identifier}")
                return cached_data
        
        # Determine source priority
        sources = self._determine_source_priority(
            request.freshness,
            request.preferred_sources,
            request.fallback_sources
        )
        
        if not sources:
            raise Document360Error(
                "No available sources for request",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
        
        # Try sources in parallel or sequence based on config
        if self.config.parallel_requests and len(sources) > 1:
            return await self._fetch_parallel(request, fetch_func, sources)
        else:
            return await self._fetch_sequential(request, fetch_func, sources)
    
    async def _fetch_parallel(
        self,
        request: DataRequest,
        fetch_func: Any,
        sources: List[DataSource]
    ) -> Any:
        """Fetch from multiple sources in parallel."""
        # Limit concurrent requests
        sources = sources[:self.config.max_concurrent_sources]
        
        # Create tasks for each source
        tasks = []
        for source in sources:
            task = asyncio.create_task(
                self._fetch_from_source_with_metrics(source, request, fetch_func)
            )
            tasks.append((source, task))
        
        # Wait for first success or all failures
        completed = []
        pending = [task for _, task in tasks]
        
        try:
            while pending:
                done, pending = await asyncio.wait(
                    pending, 
                    timeout=request.timeout_seconds,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    try:
                        result = await task
                        if result is not None:
                            # Success! Cancel remaining tasks
                            for remaining_task in pending:
                                remaining_task.cancel()
                            
                            # Cache the result
                            self._cache_data(request, result)
                            return result
                    except Exception as e:
                        logger.debug(f"Parallel fetch task failed: {e}")
                        continue
            
            # All sources failed
            raise Document360Error(
                f"All {len(sources)} sources failed for {request.content_type}",
                category=ErrorCategory.DATA_ACCESS,
                severity=ErrorSeverity.HIGH
            )
        
        finally:
            # Clean up any remaining tasks
            for _, task in tasks:
                if not task.done():
                    task.cancel()
    
    async def _fetch_sequential(
        self,
        request: DataRequest,
        fetch_func: Any,
        sources: List[DataSource]
    ) -> Any:
        """Fetch from sources sequentially."""
        last_error = None
        
        for source in sources:
            try:
                result = await self._fetch_from_source_with_metrics(source, request, fetch_func)
                if result is not None:
                    self._cache_data(request, result)
                    return result
            except Exception as e:
                logger.debug(f"Source {source} failed: {e}")
                last_error = e
                continue
        
        # All sources failed
        raise Document360Error(
            f"All sources failed for {request.content_type}: {last_error}",
            category=ErrorCategory.DATA_ACCESS,
            severity=ErrorSeverity.HIGH
        )
    
    async def _fetch_from_source_with_metrics(
        self,
        source: DataSource,
        request: DataRequest,
        fetch_func: Any
    ) -> Any:
        """Fetch from source with metrics tracking."""
        metrics = self.source_metrics[source]
        start_time = datetime.now()
        
        try:
            result = await asyncio.wait_for(
                fetch_func(source, request),
                timeout=self.config.source_timeout
            )
            
            # Update success metrics
            latency = (datetime.now() - start_time).total_seconds() * 1000
            metrics.last_success = datetime.now()
            metrics.success_count += 1
            metrics.latency_ms = (
                (metrics.latency_ms * (metrics.success_count - 1) + latency) / 
                metrics.success_count
            )
            
            return result
            
        except Exception as e:
            # Update error metrics
            metrics.last_error = datetime.now()
            metrics.error_count += 1
            metrics.error_rate = metrics.error_count / (metrics.success_count + metrics.error_count)
            
            raise e
    
    def _determine_source_priority(
        self,
        freshness: FreshnessRequirement,
        preferred: List[DataSource] = None,
        fallback: List[DataSource] = None
    ) -> List[DataSource]:
        """Determine source priority based on requirements."""
        # Start with preferred sources if specified
        if preferred:
            sources = preferred.copy()
        else:
            sources = []
        
        # Add default priority sources if not already included
        for source in self.config.default_source_priority:
            if source not in sources and self._is_source_available(source):
                sources.append(source)
        
        # Add fallback sources if enabled
        if self.config.enable_fallback and fallback:
            for source in fallback:
                if source not in sources and self._is_source_available(source):
                    sources.append(source)
        
        # Filter based on freshness requirements
        filtered_sources = []
        for source in sources:
            if self._source_meets_freshness(source, freshness):
                filtered_sources.append(source)
        
        return filtered_sources
    
    def _is_source_available(self, source: DataSource) -> bool:
        """Check if a source is available."""
        if source == DataSource.API:
            return self.api_provider is not None
        elif source == DataSource.ARCHIVE:
            return self.archive_provider is not None
        elif source == DataSource.SCRAPER:
            return self.scraper_provider is not None
        return False
    
    def _source_meets_freshness(self, source: DataSource, freshness: FreshnessRequirement) -> bool:
        """Check if source can meet freshness requirements."""
        if freshness == FreshnessRequirement.REALTIME:
            # Only API can provide realtime data
            return source == DataSource.API
        elif freshness == FreshnessRequirement.FRESH:
            # API is preferred, archive might be acceptable
            return source in [DataSource.API, DataSource.ARCHIVE]
        else:
            # Any source is acceptable for recent/cached/any
            return True
    
    def _get_cached_data(self, request: DataRequest) -> Optional[Any]:
        """Get cached data if available and fresh enough."""
        cache_key = f"{request.content_type}:{request.identifier}"
        cached = self._cache.get(cache_key)
        
        if not cached:
            return None
        
        # Check if data is fresh enough
        cached_time = cached.get("timestamp")
        if not cached_time:
            return None
        
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600
        if age_hours > self.config.max_age_hours:
            # Remove stale data
            del self._cache[cache_key]
            return None
        
        return cached.get("data")
    
    def _cache_data(self, request: DataRequest, data: Any) -> None:
        """Cache fetched data."""
        cache_key = f"{request.content_type}:{request.identifier}"
        self._cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now(),
            "source": "hybrid"
        }
    
    # Source-specific fetch methods
    async def _fetch_article_from_source(self, source: DataSource, request: DataRequest) -> Article:
        """Fetch article from specific source."""
        article_id = int(request.identifier)
        
        if source == DataSource.API and self.api_provider:
            return await self.api_provider.get_article(article_id)
        elif source == DataSource.ARCHIVE and self.archive_provider:
            return await self.archive_provider.get_article(article_id)
        elif source == DataSource.SCRAPER and self.scraper_provider:
            # This would be implemented when scraper provider is available
            raise NotImplementedError("Scraper provider not yet implemented")
        else:
            raise Document360Error(
                f"Source {source} not available for articles",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def _fetch_articles_list_from_source(
        self,
        source: DataSource,
        request: DataRequest,
        category_id: Optional[int],
        status: Optional[str],
        **kwargs: Any
    ) -> List[Article]:
        """Fetch articles list from specific source."""
        if source == DataSource.API and self.api_provider:
            return await self.api_provider.list_articles(category_id=category_id, status=status, **kwargs)
        elif source == DataSource.ARCHIVE and self.archive_provider:
            return await self.archive_provider.list_articles(category_id=category_id, status=status, **kwargs)
        elif source == DataSource.SCRAPER and self.scraper_provider:
            raise NotImplementedError("Scraper provider not yet implemented")
        else:
            raise Document360Error(
                f"Source {source} not available for article lists",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def _fetch_category_from_source(self, source: DataSource, request: DataRequest) -> Category:
        """Fetch category from specific source."""
        category_id = int(request.identifier)
        
        if source == DataSource.API and self.api_provider:
            return await self.api_provider.get_category(category_id)
        elif source == DataSource.ARCHIVE and self.archive_provider:
            return await self.archive_provider.get_category(category_id)
        elif source == DataSource.SCRAPER and self.scraper_provider:
            raise NotImplementedError("Scraper provider not yet implemented")
        else:
            raise Document360Error(
                f"Source {source} not available for categories",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def _fetch_categories_list_from_source(self, source: DataSource, request: DataRequest) -> List[Category]:
        """Fetch categories list from specific source."""
        if source == DataSource.API and self.api_provider:
            return await self.api_provider.list_categories()
        elif source == DataSource.ARCHIVE and self.archive_provider:
            return await self.archive_provider.list_categories()
        elif source == DataSource.SCRAPER and self.scraper_provider:
            raise NotImplementedError("Scraper provider not yet implemented")
        else:
            raise Document360Error(
                f"Source {source} not available for category lists",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def _fetch_project_version_from_source(self, source: DataSource, request: DataRequest) -> ProjectVersion:
        """Fetch project version from specific source."""
        if source == DataSource.API and self.api_provider:
            return await self.api_provider.get_project_version()
        elif source == DataSource.ARCHIVE and self.archive_provider:
            return await self.archive_provider.get_project_version()
        elif source == DataSource.SCRAPER and self.scraper_provider:
            raise NotImplementedError("Scraper provider not yet implemented")
        else:
            raise Document360Error(
                f"Source {source} not available for project version",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    async def _stream_from_source(self, source: DataSource, **kwargs: Any) -> AsyncIterator[Article]:
        """Stream articles from specific source."""
        if source == DataSource.API and self.api_provider:
            async for article in self.api_provider.stream_articles(**kwargs):
                yield article
        elif source == DataSource.ARCHIVE and self.archive_provider:
            async for article in self.archive_provider.stream_articles(**kwargs):
                yield article
        elif source == DataSource.SCRAPER and self.scraper_provider:
            raise NotImplementedError("Scraper provider not yet implemented")
        else:
            raise Document360Error(
                f"Source {source} not available for streaming",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    def get_source_metrics(self) -> Dict[DataSource, SourceMetrics]:
        """Get current metrics for all sources."""
        return self.source_metrics.copy()
    
    def clear_cache(self) -> None:
        """Clear internal cache."""
        self._cache.clear()
        logger.info("HybridProvider cache cleared")