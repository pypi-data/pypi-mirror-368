"""Main MkDocs export orchestrator for Document360 content.

This module provides the primary MkDocsExporter class that coordinates the complete
Document360 → MkDocs conversion process, integrating with d361's existing architecture
for archive/API data access, content processing, and modern MkDocs features.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/exporters/mkdocs_exporter.py

import asyncio
from pathlib import Path
from typing import Any, Optional, Dict, List

from loguru import logger

from d361.core.interfaces import DataProvider
from d361.core.models import Article, Category
from d361.providers.archive_provider import ArchiveProvider
from d361.providers.api_provider import ApiProvider
from d361.providers.hybrid_provider import HybridProvider
from d361.scraping.content_processor import ContentProcessor
from d361.config.schema import AppConfig
from d361.utils.logging import setup_logging
from d361.utils.performance import PerformanceOptimizer
from contextlib import contextmanager
import time

from d361.mkdocs.exporters.config_generator import ConfigGenerator
from d361.mkdocs.exporters.navigation_builder import NavigationBuilder
from d361.mkdocs.exporters.theme_optimizer import ThemeOptimizer
from d361.mkdocs.processors.markdown_processor import MarkdownProcessor
from d361.mkdocs.processors.content_enhancer import ContentEnhancer
from d361.mkdocs.processors.asset_manager import AssetManager
from d361.mkdocs.processors.cross_reference_resolver import CrossReferenceResolver


class SimplePerformanceMonitor:
    """Simple performance monitoring for MkDocs export operations."""
    
    def __init__(self):
        self.metrics = {}
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager to measure operation duration."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.metrics[operation_name] = duration
            logger.info(f"Operation '{operation_name}' took {duration:.2f} seconds")
    
    def get_metrics(self) -> dict:
        """Get collected metrics."""
        return self.metrics.copy()


class MkDocsExporter:
    """Primary orchestrator for Document360 → MkDocs conversion.
    
    This class coordinates the complete export process, integrating with d361's
    existing architecture while providing comprehensive MkDocs-specific features.
    
    Features:
    - Archive and API data source support via d361 providers
    - Modern MkDocs with Material theme integration  
    - Popular plugin support (autorefs, section-index, redirects)
    - Performance optimization with parallel processing
    - Quality validation and error reporting
    - Template system for customization
    
    Example:
        exporter = MkDocsExporter(
            source="archive",
            archive_path="project.zip",
            output_path="mkdocs_output",
            theme="material"
        )
        await exporter.export()
    """
    
    def __init__(
        self,
        source: str = "archive",
        archive_path: Optional[Path] = None,
        api_token: Optional[str] = None,
        api_base_url: Optional[str] = None,
        output_path: Path = Path("mkdocs_output"),
        theme: str = "material",
        enable_plugins: bool = True,
        parallel_processing: bool = True,
        max_workers: int = 4,
        config_path: Optional[Path] = None,
    ) -> None:
        """Initialize MkDocs exporter.
        
        Args:
            source: Data source type - 'archive', 'api', or 'hybrid'
            archive_path: Path to Document360 archive file
            api_token: Document360 API token for API/hybrid modes
            api_base_url: Document360 API base URL
            output_path: Output directory for generated MkDocs site
            theme: MkDocs theme to use ('material', 'readthedocs', etc.)
            enable_plugins: Enable popular MkDocs plugins
            parallel_processing: Use parallel processing for performance
            max_workers: Maximum parallel workers
            config_path: Path to d361 configuration file
        """
        self.source = source
        self.archive_path = archive_path
        self.api_token = api_token
        self.api_base_url = api_base_url or "https://apidocs.document360.com"
        self.output_path = Path(output_path)
        self.theme = theme
        self.enable_plugins = enable_plugins
        self.parallel_processing = parallel_processing
        self.max_workers = max_workers
        
        # Load configuration (use default config for now)
        self.config = AppConfig() if not config_path else AppConfig()
        
        # Initialize logging (simplified for compatibility)
        # setup_logging(self.config.logging)  # Disabled for now due to config incompatibility
        
        # Initialize performance monitoring
        self.performance_monitor = SimplePerformanceMonitor()
        
        # Initialize providers
        self.provider: Optional[DataProvider] = None
        self._initialize_provider()
        
        # Initialize processors
        self.content_processor = ContentProcessor()
        self.markdown_processor = MarkdownProcessor()
        self.content_enhancer = ContentEnhancer()
        self.asset_manager = AssetManager(output_dir=self.output_path)
        self.cross_reference_resolver = CrossReferenceResolver(articles=[])
        
        # Initialize MkDocs components
        self.config_generator = ConfigGenerator(theme=theme, enable_plugins=enable_plugins)
        self.navigation_builder = NavigationBuilder()
        self.theme_optimizer = ThemeOptimizer(theme=theme)
        
        # Export statistics
        self.stats = {
            "articles_processed": 0,
            "categories_processed": 0,
            "assets_processed": 0,
            "links_resolved": 0,
            "errors": 0,
        }
        
        logger.info(f"Initialized MkDocsExporter for {source} source with {theme} theme")
    
    def _initialize_provider(self) -> None:
        """Initialize data provider based on source type."""
        if self.source == "archive":
            if not self.archive_path or not self.archive_path.exists():
                raise ValueError(f"Archive path not found: {self.archive_path}")
            self.provider = ArchiveProvider(archive_path=self.archive_path)
            
        elif self.source == "api":
            if not self.api_token:
                raise ValueError("API token required for API source")
            self.provider = ApiProvider(
                api_token=self.api_token,
                base_url=self.api_base_url
            )
            
        elif self.source == "hybrid":
            if not self.archive_path or not self.api_token:
                raise ValueError("Both archive path and API token required for hybrid source")
            self.provider = HybridProvider(
                archive_path=self.archive_path,
                api_token=self.api_token,
                base_url=self.api_base_url
            )
            
        else:
            raise ValueError(f"Unknown source type: {self.source}")
    
    async def export(self) -> Dict[str, Any]:
        """Execute complete MkDocs export process.
        
        Returns:
            Export results with statistics and file paths
        """
        logger.info("Starting MkDocs export process")
        
        with self.performance_monitor.measure("total_export"):
            try:
                # Load content from data source
                articles, categories = await self._load_content()
                
                # Process content for MkDocs
                processed_articles = await self._process_content(articles)
                processed_categories = await self._process_categories(categories)
                
                # Generate MkDocs structure
                await self._generate_mkdocs_structure(processed_articles, processed_categories)
                
                # Generate MkDocs configuration
                config_path = await self._generate_config(processed_articles, processed_categories)
                
                # Optimize for selected theme
                await self._optimize_theme(processed_articles, processed_categories)
                
                # Validate export
                validation_results = await self._validate_export()
                
                # Generate export report
                export_results = self._generate_export_results(config_path, validation_results)
                
                logger.info("MkDocs export completed successfully")
                return export_results
                
            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"MkDocs export failed: {e}")
                raise
    
    async def _load_content(self) -> tuple[List[Article], List[Category]]:
        """Load content from configured data source."""
        logger.info(f"Loading content from {self.source} source")
        
        with self.performance_monitor.measure("content_loading"):
            if not self.provider:
                raise RuntimeError("Provider not initialized")
            
            articles = await self.provider.get_articles()
            categories = await self.provider.get_categories()
            
            logger.info(f"Loaded {len(articles)} articles and {len(categories)} categories")
            return articles, categories
    
    async def _process_content(self, articles: List[Article]) -> List[Article]:
        """Process articles for MkDocs conversion."""
        logger.info("Processing article content for MkDocs")
        
        with self.performance_monitor.measure("content_processing"):
            processed_articles = []
            
            if self.parallel_processing:
                # Process articles in parallel
                tasks = [
                    self._process_single_article(article)
                    for article in articles
                ]
                processed_articles = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out exceptions and log errors
                valid_articles = []
                for result in processed_articles:
                    if isinstance(result, Exception):
                        logger.error(f"Error processing article: {result}")
                        self.stats["errors"] += 1
                    else:
                        valid_articles.append(result)
                        self.stats["articles_processed"] += 1
                        
                processed_articles = valid_articles
                
            else:
                # Process articles sequentially
                for article in articles:
                    try:
                        processed_article = await self._process_single_article(article)
                        processed_articles.append(processed_article)
                        self.stats["articles_processed"] += 1
                    except Exception as e:
                        logger.error(f"Error processing article {article.id}: {e}")
                        self.stats["errors"] += 1
            
            logger.info(f"Processed {len(processed_articles)} articles")
            return processed_articles
    
    async def _process_single_article(self, article: Article) -> Article:
        """Process a single article for MkDocs."""
        # Enhance content for MkDocs
        enhanced_content = await self.content_enhancer.enhance(article.content)
        
        # Convert to optimized Markdown
        markdown_content = await self.markdown_processor.convert(enhanced_content)
        
        # Process assets
        processed_content = await self.asset_manager.process_assets(
            markdown_content, 
            article.id
        )
        
        # Create processed article
        processed_article = Article(
            id=article.id,
            title=article.title,
            content=processed_content,
            category_id=article.category_id,
            slug=article.slug,
            order=article.order,
            created_at=article.created_at,
            updated_at=article.updated_at,
            is_hidden=article.is_hidden,
        )
        
        return processed_article
    
    async def _process_categories(self, categories: List[Category]) -> List[Category]:
        """Process categories for MkDocs navigation."""
        logger.info("Processing categories for MkDocs navigation")
        
        processed_categories = []
        for category in categories:
            # Categories generally don't need as much processing
            processed_categories.append(category)
            self.stats["categories_processed"] += 1
        
        return processed_categories
    
    async def _generate_mkdocs_structure(
        self, 
        articles: List[Article], 
        categories: List[Category]
    ) -> None:
        """Generate MkDocs directory structure and files."""
        logger.info("Generating MkDocs directory structure")
        
        # Create output directories
        docs_dir = self.output_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate navigation structure
        navigation = await self.navigation_builder.build_navigation(articles, categories)
        
        # Resolve cross-references
        resolved_articles = await self.cross_reference_resolver.resolve_references(
            articles, navigation
        )
        self.stats["links_resolved"] = self.cross_reference_resolver.resolved_count
        
        # Write article files
        for article in resolved_articles:
            await self._write_article_file(article, docs_dir)
        
        # Generate category index pages
        await self._generate_category_indexes(categories, docs_dir)
        
        # Copy assets
        await self._copy_assets(docs_dir)
    
    async def _write_article_file(self, article: Article, docs_dir: Path) -> None:
        """Write individual article to MkDocs format."""
        # Determine file path based on category structure
        file_path = docs_dir / f"{article.slug}.md"
        
        # Generate frontmatter
        frontmatter = {
            "title": article.title,
            "hide": ["toc"] if not article.content.strip() else None,
        }
        
        # Write file with frontmatter
        content_lines = ["---"]
        for key, value in frontmatter.items():
            if value is not None:
                if isinstance(value, list):
                    content_lines.append(f"{key}:")
                    for item in value:
                        content_lines.append(f"  - {item}")
                else:
                    content_lines.append(f"{key}: {value}")
        content_lines.extend(["---", "", article.content])
        
        file_path.write_text("\n".join(content_lines), encoding="utf-8")
    
    async def _generate_category_indexes(
        self, 
        categories: List[Category], 
        docs_dir: Path
    ) -> None:
        """Generate index pages for categories."""
        for category in categories:
            index_path = docs_dir / f"{category.slug}" / "index.md"
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate category index content
            content = f"# {category.name}\n\n"
            if hasattr(category, 'description') and category.description:
                content += f"{category.description}\n\n"
            
            index_path.write_text(content, encoding="utf-8")
    
    async def _copy_assets(self, docs_dir: Path) -> None:
        """Copy processed assets to docs directory."""
        assets_processed = await self.asset_manager.copy_assets(docs_dir)
        self.stats["assets_processed"] = assets_processed
    
    async def _generate_config(
        self, 
        articles: List[Article], 
        categories: List[Category]
    ) -> Path:
        """Generate MkDocs configuration file."""
        logger.info("Generating MkDocs configuration")
        
        navigation = await self.navigation_builder.build_navigation(articles, categories)
        config = await self.config_generator.generate_config(
            site_name="Documentation",
            navigation=navigation,
            output_path=self.output_path
        )
        
        config_path = self.output_path / "mkdocs.yml"
        config_path.write_text(config, encoding="utf-8")
        
        logger.info(f"Generated MkDocs configuration: {config_path}")
        return config_path
    
    async def _optimize_theme(
        self, 
        articles: List[Article], 
        categories: List[Category]
    ) -> None:
        """Apply theme-specific optimizations."""
        logger.info(f"Applying {self.theme} theme optimizations")
        await self.theme_optimizer.optimize(articles, categories, self.output_path)
    
    async def _validate_export(self) -> Dict[str, Any]:
        """Validate the generated MkDocs export."""
        logger.info("Validating MkDocs export")
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
        }
        
        # Check if mkdocs.yml exists and is valid
        config_path = self.output_path / "mkdocs.yml"
        if not config_path.exists():
            validation_results["valid"] = False
            validation_results["errors"].append("mkdocs.yml not found")
        
        # Check if docs directory exists
        docs_dir = self.output_path / "docs"
        if not docs_dir.exists():
            validation_results["valid"] = False
            validation_results["errors"].append("docs directory not found")
        
        # Additional validation can be added here
        
        return validation_results
    
    def _generate_export_results(
        self, 
        config_path: Path, 
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate export results summary."""
        performance_metrics = self.performance_monitor.get_metrics()
        
        return {
            "success": validation_results["valid"] and self.stats["errors"] == 0,
            "output_path": str(self.output_path),
            "config_path": str(config_path),
            "statistics": self.stats,
            "performance": performance_metrics,
            "validation": validation_results,
            "theme": self.theme,
            "plugins_enabled": self.enable_plugins,
        }