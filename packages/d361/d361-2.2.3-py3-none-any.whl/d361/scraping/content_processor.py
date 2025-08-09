"""Generic Document360 content processing utilities."""
# this_file: external/int_folders/d361/src/d361/scraping/content_processor.py

import asyncio
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import unquote, urlparse

from loguru import logger

from ..core.models import Article, Category
from ..core.interfaces import DataProvider


class ContentProcessor:
    """Generic content processing utilities for Document360 content.
    
    This class contains generic content processing methods that were migrated
    from vexy_help to eliminate duplication. These methods are format-agnostic
    and can be used by any output converter.
    """

    def __init__(self, image_base_url: str | None = None) -> None:
        """Initialize content processor.
        
        Args:
            image_base_url: Base URL for image references
        """
        self.image_base_url = image_base_url

    def clean_content(self, content: str) -> str:
        """Clean and normalize Document360 content.
        
        Args:
            content: Raw content to clean
            
        Returns:
            Cleaned content
        """
        if not content:
            return ""

        # Remove Document360-specific artifacts
        content = self._remove_d360_artifacts(content)
        
        # Normalize whitespace
        content = self._normalize_whitespace(content)
        
        # Clean up markdown formatting
        content = self._clean_markdown_formatting(content)
        
        # Process image URLs if base URL provided
        if self.image_base_url:
            content = self.convert_image_urls(content)

        return content

    def convert_image_urls(self, content: str) -> str:
        """Convert Document360 image URLs to use base URL.
        
        Args:
            content: Content with image URLs
            
        Returns:
            Content with converted image URLs
        """
        if not self.image_base_url:
            return content

        # Pattern to match markdown images and HTML img tags
        def replace_image_url(match):
            url = match.group(1)
            
            # Skip if already absolute URL
            if url.startswith(('http://', 'https://')):
                return match.group(0)
            
            # Skip data URLs
            if url.startswith('data:'):
                return match.group(0)
                
            # Convert relative URL
            if url.startswith('/'):
                url = url[1:]  # Remove leading slash
                
            new_url = f"{self.image_base_url.rstrip('/')}/{url}"
            return match.group(0).replace(match.group(1), new_url)

        # Replace markdown image URLs: ![alt](url)
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image_url, content)
        
        # Replace HTML img src URLs: <img src="url"
        content = re.sub(r'<img([^>]*)\s+src="([^"]+)"', replace_image_url, content)

        return content

    def clean_slug(self, slug: str) -> str:
        """Clean and normalize slug for use in URLs.
        
        Args:
            slug: Raw slug to clean
            
        Returns:
            Cleaned slug
        """
        if not slug:
            return ""

        # Strip numeric prefixes (e.g., "001-article-name" -> "article-name")
        slug = self.strip_numeric_prefix(slug)
        
        # Convert to lowercase
        slug = slug.lower()
        
        # Replace spaces and underscores with hyphens
        slug = re.sub(r'[_\s]+', '-', slug)
        
        # Remove special characters except hyphens
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Strip leading/trailing hyphens
        slug = slug.strip('-')

        return slug

    def strip_numeric_prefix(self, text: str) -> str:
        """Strip numeric prefixes from text.
        
        Args:
            text: Text with potential numeric prefix
            
        Returns:
            Text without numeric prefix
        """
        return re.sub(r'^\d+-', '', text)

    def extract_metadata_from_content(self, content: str) -> dict[str, Any]:
        """Extract metadata from Document360 content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        # Count words
        word_count = len(content.split()) if content else 0
        metadata['word_count'] = word_count
        
        # Estimate reading time (200 words per minute)
        metadata['reading_time_minutes'] = max(1, word_count // 200)
        
        # Find headings
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        metadata['headings'] = headings
        metadata['heading_count'] = len(headings)
        
        # Find images
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        metadata['images'] = [{'alt': alt, 'url': url} for alt, url in images]
        metadata['image_count'] = len(images)
        
        # Find links
        links = re.findall(r'(?<!!)\[([^\]]*)\]\(([^)]+)\)', content)
        metadata['links'] = [{'text': text, 'url': url} for text, url in links]
        metadata['link_count'] = len(links)
        
        # Find code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        metadata['code_blocks'] = code_blocks
        metadata['code_block_count'] = len(code_blocks)

        return metadata

    def _remove_d360_artifacts(self, content: str) -> str:
        """Remove Document360-specific artifacts from content.
        
        Args:
            content: Content to clean
            
        Returns:
            Content without Document360 artifacts
        """
        # Remove Document360 internal references
        content = re.sub(r'<a[^>]*data-d360[^>]*>(.*?)</a>', r'\1', content, flags=re.DOTALL)
        
        # Remove Document360 widgets/embeds
        content = re.sub(r'<div[^>]*class="[^"]*d360[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
        
        # Remove Document360 metadata comments
        content = re.sub(r'<!-- d360:[^>]*-->', '', content)
        
        # Remove empty href attributes that Document360 sometimes generates
        content = re.sub(r'href=""', '', content)

        return content

    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in content.
        
        Args:
            content: Content to normalize
            
        Returns:
            Content with normalized whitespace
        """
        # Replace multiple spaces with single space
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Replace multiple newlines with maximum of two newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove trailing whitespace from lines
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        
        # Remove leading/trailing whitespace
        content = content.strip()

        return content

    def _clean_markdown_formatting(self, content: str) -> str:
        """Clean up common markdown formatting issues.
        
        Args:
            content: Content to clean
            
        Returns:
            Content with cleaned markdown
        """
        # Fix spacing around headers
        content = re.sub(r'^(#{1,6})\s*(.+)$', r'\1 \2', content, flags=re.MULTILINE)
        
        # Fix spacing around lists
        content = re.sub(r'\n(\s*[-*+]\s)', r'\n\n\1', content)
        content = re.sub(r'\n(\s*\d+\.\s)', r'\n\n\1', content)
        
        # Fix spacing around code blocks
        content = re.sub(r'\n(```)', r'\n\n\1', content)
        content = re.sub(r'(```)\n', r'\1\n\n', content)
        
        # Fix spacing around blockquotes
        content = re.sub(r'\n(>\s)', r'\n\n\1', content)

        return content

    def analyze_content_quality(self, content: str) -> dict[str, Any]:
        """Analyze content quality metrics.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary with quality metrics
        """
        if not content:
            return {'quality_score': 0, 'issues': ['empty_content']}

        issues = []
        score = 100  # Start with perfect score

        # Check for minimum word count
        word_count = len(content.split())
        if word_count < 50:
            issues.append('short_content')
            score -= 20

        # Check for headings structure
        headings = re.findall(r'^(#{1,6})', content, re.MULTILINE)
        if not headings:
            issues.append('no_headings')
            score -= 10

        # Check for images
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        if not images and word_count > 200:
            issues.append('no_images')
            score -= 5

        # Check for broken links
        links = re.findall(r'(?<!!)\[([^\]]*)\]\(([^)]+)\)', content)
        for text, url in links:
            if not url or url == '#':
                issues.append('broken_links')
                score -= 10
                break

        # Check for code blocks formatting
        if '```' in content:
            if content.count('```') % 2 != 0:
                issues.append('malformed_code_blocks')
                score -= 15

        # Check for excessive whitespace
        if re.search(r'\n{4,}', content):
            issues.append('excessive_whitespace')
            score -= 5

        return {
            'quality_score': max(0, score),
            'word_count': word_count,
            'heading_count': len(headings),
            'image_count': len(images),
            'link_count': len(links),
            'issues': issues
        }


class Document360ContentProcessor(ContentProcessor):
    """Advanced Document360 content processor for cross-platform functionality.
    
    Extends ContentProcessor with advanced functionality for merging, deduplication,
    and intelligent content processing using d361's advanced features.
    """

    def __init__(self, image_base_url: str | None = None, max_workers: int = 4):
        """Initialize the advanced content processor.
        
        Args:
            image_base_url: Base URL for image references
            max_workers: Maximum number of parallel workers for processing
        """
        super().__init__(image_base_url)
        self.max_workers = max_workers
        self.stats = {
            "articles_processed": 0,
            "content_enhanced": 0,
            "duplicates_resolved": 0,
            "merge_operations": 0,
        }

    async def load_and_merge_content(
        self,
        archive_provider: Optional[DataProvider] = None,
        api_provider: Optional[DataProvider] = None,
        data_source: str = "hybrid"
    ) -> tuple[list[Article], list[Category]]:
        """Load and intelligently merge content from multiple data sources.
        
        Args:
            archive_provider: Provider for archive data
            api_provider: Provider for API data  
            data_source: Data source mode - 'archive', 'api', or 'hybrid'
            
        Returns:
            Tuple of (articles, categories) with merged content
        """
        if data_source == "archive" and archive_provider:
            logger.info("Loading content from archive only")
            articles = await archive_provider.list_articles()
            categories = await archive_provider.list_categories()
            return articles, categories
            
        elif data_source == "api" and api_provider:
            logger.info("Loading content from API only")
            articles = await api_provider.list_articles()
            categories = await api_provider.list_categories()
            return articles, categories
            
        elif data_source == "hybrid" and archive_provider and api_provider:
            logger.info("Loading content from both archive and API with intelligent merging")
            return await self._merge_content_intelligently(archive_provider, api_provider)
            
        else:
            raise ValueError(f"Invalid data source configuration: {data_source}")

    async def _merge_content_intelligently(
        self, 
        archive_provider: DataProvider, 
        api_provider: DataProvider
    ) -> tuple[list[Article], list[Category]]:
        """Merge content from archive and API providers using intelligent conflict resolution.
        
        Args:
            archive_provider: Archive data provider
            api_provider: API data provider
            
        Returns:
            Tuple of (merged_articles, merged_categories) with resolved conflicts
        """
        logger.info("Starting intelligent content merging...")
        
        # Load data from both sources concurrently
        archive_articles, api_articles = await asyncio.gather(
            archive_provider.list_articles(),
            api_provider.list_articles()
        )
        
        archive_categories, api_categories = await asyncio.gather(
            archive_provider.list_categories(),
            api_provider.list_categories()
        )
        
        # Merge articles with conflict resolution
        merged_articles = self._merge_articles_with_conflict_resolution(
            archive_articles, api_articles
        )
        
        # Merge categories with conflict resolution
        merged_categories = self._merge_categories_with_conflict_resolution(
            archive_categories, api_categories
        )
        
        merge_stats = {
            "archive_articles": len(archive_articles),
            "api_articles": len(api_articles), 
            "merged_articles": len(merged_articles),
            "archive_categories": len(archive_categories),
            "api_categories": len(api_categories),
            "merged_categories": len(merged_categories)
        }
        
        logger.info(f"Content merging completed: {merge_stats}")
        self.stats["merge_operations"] += 1
        
        return merged_articles, merged_categories

    def _merge_articles_with_conflict_resolution(
        self, 
        archive_articles: list[Article], 
        api_articles: list[Article]
    ) -> list[Article]:
        """Merge articles using intelligent conflict resolution.
        
        Args:
            archive_articles: Articles from archive
            api_articles: Articles from API
            
        Returns:
            List of merged articles with resolved conflicts
        """
        # Create lookups by ID
        archive_by_id = {str(article.id): article for article in archive_articles}
        api_by_id = {str(article.id): article for article in api_articles}
        
        merged_articles = []
        processed_ids = set()
        
        # Process articles that exist in both sources
        for article_id, archive_article in archive_by_id.items():
            if article_id in api_by_id:
                api_article = api_by_id[article_id]
                merged_article = self._merge_single_article(archive_article, api_article)
                merged_articles.append(merged_article)
                processed_ids.add(article_id)
            else:
                # Archive-only article
                merged_articles.append(archive_article)
                processed_ids.add(article_id)
        
        # Add API-only articles
        for article_id, api_article in api_by_id.items():
            if article_id not in processed_ids:
                merged_articles.append(api_article)
        
        return merged_articles

    def _merge_categories_with_conflict_resolution(
        self,
        archive_categories: list[Category],
        api_categories: list[Category]
    ) -> list[Category]:
        """Merge categories using intelligent conflict resolution.
        
        Args:
            archive_categories: Categories from archive
            api_categories: Categories from API
            
        Returns:
            List of merged categories with resolved conflicts
        """
        # Create lookups by ID
        archive_by_id = {str(category.id): category for category in archive_categories}
        api_by_id = {str(category.id): category for category in api_categories}
        
        merged_categories = []
        processed_ids = set()
        
        # Process categories that exist in both sources
        for category_id, archive_category in archive_by_id.items():
            if category_id in api_by_id:
                api_category = api_by_id[category_id]
                merged_category = self._merge_single_category(archive_category, api_category)
                merged_categories.append(merged_category)
                processed_ids.add(category_id)
            else:
                # Archive-only category
                merged_categories.append(archive_category)
                processed_ids.add(category_id)
        
        # Add API-only categories
        for category_id, api_category in api_by_id.items():
            if category_id not in processed_ids:
                merged_categories.append(api_category)
        
        return merged_categories

    def _merge_single_article(self, archive_article: Article, api_article: Article) -> Article:
        """Merge two articles using intelligent conflict resolution.
        
        Args:
            archive_article: Article from archive
            api_article: Article from API
            
        Returns:
            Merged article with resolved conflicts
        """
        # Determine which article is newer based on updated_at timestamp
        if (api_article.updated_at and archive_article.updated_at and 
            api_article.updated_at > archive_article.updated_at):
            base_article = api_article
            other_article = archive_article
            logger.debug(f"Using API version as base for article {base_article.id} (newer)")
        else:
            base_article = archive_article
            other_article = api_article
            logger.debug(f"Using archive version as base for article {base_article.id}")
        
        # Create merged article starting with the base
        merged = Article(
            id=base_article.id,
            title=base_article.title,
            slug=base_article.slug,
            content=base_article.content,
            category_id=base_article.category_id,
            status=base_article.status,
            order=base_article.order,
            updated_at=base_article.updated_at,
            created_at=base_article.created_at,
            language=base_article.language,
            published_at=base_article.published_at
        )
        
        # Intelligent content merging
        if not merged.content and other_article.content:
            # Base has no content, use other's content
            merged.content = other_article.content
            logger.debug(f"Using content from other source for article {merged.id} (base had no content)")
            
        elif merged.content and other_article.content:
            # Both have content, use the richer one if significantly different
            if len(other_article.content) > len(merged.content) * 1.5:
                logger.debug(f"Using content from other source for article {merged.id} (richer content)")
                merged.content = other_article.content
        
        return merged

    def _merge_single_category(self, archive_category: Category, api_category: Category) -> Category:
        """Merge two categories using intelligent conflict resolution.
        
        Args:
            archive_category: Category from archive
            api_category: Category from API
            
        Returns:
            Merged category with resolved conflicts
        """
        # Use newer category based on updated_at timestamp
        if (api_category.updated_at and archive_category.updated_at and 
            api_category.updated_at > archive_category.updated_at):
            return api_category
        else:
            return archive_category

    async def enhance_content_with_advanced_processing(
        self, 
        articles: list[Article],
        use_parallel: bool = True
    ) -> list[Article]:
        """Enhance article content using d361's advanced processing capabilities.
        
        Args:
            articles: Articles to enhance
            use_parallel: Whether to use parallel processing
            
        Returns:
            Articles with enhanced content
        """
        logger.info(f"Starting content enhancement for {len(articles)} articles")
        
        if use_parallel and self.max_workers > 1:
            enhanced_articles = await self._enhance_content_parallel(articles)
        else:
            enhanced_articles = await self._enhance_content_sequential(articles)
        
        logger.info(f"Content enhancement completed: {len(enhanced_articles)} articles processed")
        self.stats["articles_processed"] += len(enhanced_articles)
        
        return enhanced_articles

    async def _enhance_content_sequential(self, articles: list[Article]) -> list[Article]:
        """Enhance article content sequentially.
        
        Args:
            articles: Articles to enhance
            
        Returns:
            Enhanced articles
        """
        enhanced_articles = []
        
        for article in articles:
            try:
                enhanced_article = await self._enhance_single_article_content(article)
                enhanced_articles.append(enhanced_article)
                
                if len(enhanced_articles) % 50 == 0:
                    logger.info(f"Enhanced {len(enhanced_articles)}/{len(articles)} articles")
                    
            except Exception as e:
                logger.error(f"Failed to enhance article {article.id}: {e}")
                enhanced_articles.append(article)  # Use original article
        
        return enhanced_articles

    async def _enhance_content_parallel(self, articles: list[Article]) -> list[Article]:
        """Enhance article content in parallel.
        
        Args:
            articles: Articles to enhance
            
        Returns:
            Enhanced articles
        """
        enhanced_articles = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all enhancement tasks
            future_to_article = {
                executor.submit(self._enhance_single_article_sync, article): article
                for article in articles
            }
            
            # Process completed futures
            for future in as_completed(future_to_article):
                article = future_to_article[future]
                try:
                    enhanced_article = future.result()
                    enhanced_articles.append(enhanced_article)
                    
                    if len(enhanced_articles) % 50 == 0:
                        logger.info(f"Enhanced {len(enhanced_articles)}/{len(articles)} articles")
                        
                except Exception as e:
                    logger.error(f"Failed to enhance article {article.id}: {e}")
                    enhanced_articles.append(article)  # Use original article
        
        return enhanced_articles

    def _enhance_single_article_sync(self, article: Article) -> Article:
        """Synchronous wrapper for single article enhancement (for ThreadPoolExecutor).
        
        Args:
            article: Article to enhance
            
        Returns:
            Enhanced article
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._enhance_single_article_content(article))
        finally:
            loop.close()

    async def _enhance_single_article_content(self, article: Article) -> Article:
        """Enhance a single article's content using d361's advanced processing.
        
        Args:
            article: Article to enhance
            
        Returns:
            Enhanced article
        """
        if not article.content or not self._content_needs_advanced_processing(article.content):
            return article
        
        try:
            from .converter import Document360MarkdownConverter, ConversionConfig
            
            # Configure the converter for Document360 content
            config = ConversionConfig(
                style="document360",
                code_language_detection=True,
                convert_tables=True,
                fence_code_blocks=True,
                validate_markdown=True,
                link_handling="preserve",
                strip_tags=["script", "style", "meta", "link"]
            )
            
            # Initialize converter with Document360 optimizations
            converter = Document360MarkdownConverter(
                heading_style='atx',
                bullets='-',
                emphasis_mark='*',
                strong_mark='**',
                strip=['script', 'style', 'meta', 'link'],
                convert=['b', 'strong', 'i', 'em', 'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'hr', 'br',
                        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img', 'div', 'span']
            )
            
            # Create enhanced article with converted content
            enhanced_article = Article(
                id=article.id,
                title=article.title,
                slug=article.slug,
                content=converter.convert(article.content),
                category_id=article.category_id,
                status=article.status,
                order=article.order,
                updated_at=article.updated_at,
                created_at=article.created_at,
                language=article.language,
                published_at=article.published_at
            )
            
            # Track enhancement
            self.stats["content_enhanced"] += 1
            logger.debug(f"Enhanced content for article {article.id}")
            
            return enhanced_article
            
        except ImportError:
            logger.debug(f"d361 MarkdownConverter not available for article {article.id}")
            return article
        except Exception as e:
            logger.warning(f"Content enhancement failed for article {article.id}: {e}")
            return article

    def _content_needs_advanced_processing(self, content: str) -> bool:
        """Check if content would benefit from d361's advanced processing.
        
        Args:
            content: Content to analyze
            
        Returns:
            True if content should be processed with advanced converter
        """
        if not content:
            return False
            
        # Check for HTML tags that benefit from advanced processing
        html_indicators = [
            '<table',           # Tables benefit from advanced table processing
            '<code',            # Code blocks can benefit from language detection
            '<pre',             # Preformatted code blocks
            '```',              # Already good markdown, but may need validation
            '<div',             # Structural divs that might contain important content
            '<blockquote',      # Quote blocks
            'class=',           # CSS classes that might indicate special formatting
            'style=',           # Inline styles that might need processing
            '<img',             # Images that might need enhanced processing
            '<a href',          # Links that might need advanced link handling
        ]
        
        content_lower = content.lower()
        html_count = sum(1 for indicator in html_indicators if indicator in content_lower)
        
        # Use advanced processing if content has multiple HTML elements
        # or if it's a substantial piece of content with some HTML
        return html_count >= 2 or (html_count >= 1 and len(content) > 500)

    async def resolve_duplicates_with_advanced_detection(
        self, 
        articles: list[Article]
    ) -> list[Article]:
        """Resolve duplicates using d361's advanced ContentDeduplicator.
        
        Args:
            articles: Articles to process for duplicates
            
        Returns:
            Articles with duplicates resolved
        """
        try:
            from .deduplicator import ContentDeduplicator, DeduplicationConfig
            
            logger.info(f"Using d361 ContentDeduplicator for advanced duplicate detection on {len(articles)} articles")
            
            # Configure the deduplicator for Document360 content
            config = DeduplicationConfig(
                exact_threshold=0.98,           # Very high threshold for exact matches
                near_duplicate_threshold=0.85,  # High similarity threshold
                similar_threshold=0.7,          # Moderate similarity threshold
                related_threshold=0.5,          # Low similarity threshold
                primary_algorithm="content_hash",  # Use content hash as primary
                enable_fuzzy_matching=True,     # Enable fuzzy matching for better detection
                max_content_length=50000,       # Process content up to 50KB
                normalize_whitespace=True,      # Normalize whitespace for better matching
                remove_html_tags=True,          # Remove HTML for content comparison
                min_content_length=50           # Ignore very short content
            )
            
            # Initialize the advanced deduplicator
            deduplicator = ContentDeduplicator(config)
            
            # Convert articles to the format expected by d361 deduplicator
            content_items = []
            article_map = {}  # Map deduplicator IDs to original articles
            
            for article in articles:
                content_item = {
                    "id": str(article.id),
                    "title": article.title,
                    "content": article.content or "",
                    "url": f"/article/{article.id}",
                    "category": str(article.category_id),
                    "created_at": article.created_at,
                    "updated_at": article.updated_at
                }
                content_items.append(content_item)
                article_map[str(article.id)] = article
            
            # Run advanced duplicate detection
            duplicate_groups = deduplicator.find_duplicates(content_items)
            
            # Process the results
            resolved_articles = self._process_duplicate_detection_results(
                articles, duplicate_groups, article_map
            )
            
            # Log advanced deduplication stats
            total_groups = len(duplicate_groups)
            exact_dupes = sum(1 for group in duplicate_groups if group.status.value == "exact")
            near_dupes = sum(1 for group in duplicate_groups if group.status.value == "near")
            similar = sum(1 for group in duplicate_groups if group.status.value == "similar")
            
            logger.info(
                f"Advanced deduplication completed: {total_groups} groups, "
                f"{exact_dupes} exact, {near_dupes} near-duplicate, {similar} similar"
            )
            
            self.stats["duplicates_resolved"] = len(articles) - len(resolved_articles)
            
            return resolved_articles
            
        except ImportError:
            logger.debug("d361 ContentDeduplicator not available, returning articles unchanged")
            return articles
        except Exception as e:
            logger.warning(f"d361 ContentDeduplicator failed: {e}, returning articles unchanged")
            return articles

    def _process_duplicate_detection_results(
        self, 
        original_articles: list[Article],
        duplicate_groups: list, 
        article_map: dict
    ) -> list[Article]:
        """Process results from d361 ContentDeduplicator.
        
        Args:
            original_articles: Original article list
            duplicate_groups: Duplicate groups from d361
            article_map: Mapping from IDs to articles
            
        Returns:
            Articles with duplicates resolved
        """
        articles_to_remove = set()
        articles_to_update = {}
        
        for group in duplicate_groups:
            if group.size <= 1:
                continue  # No duplicates in this group
                
            # Choose the representative article (usually the first/best one)
            representative_id = group.representative_id
            duplicate_ids = [id for id in group.item_ids if id != representative_id]
            
            representative_article = article_map.get(representative_id)
            if not representative_article:
                continue
                
            # Handle duplicates based on status
            if group.status.value in ["exact", "near"]:
                # For exact and near duplicates, remove the duplicates entirely
                for dup_id in duplicate_ids:
                    if dup_id in article_map:
                        articles_to_remove.add(dup_id)
                        logger.debug(f"Removing {group.status.value} duplicate article {dup_id}")
                        
            elif group.status.value == "similar":
                # For similar content, merge metadata and keep the representative
                enhanced_article = self._merge_similar_article_metadata(
                    representative_article,
                    [article_map[id] for id in duplicate_ids if id in article_map],
                    group.average_similarity
                )
                articles_to_update[representative_id] = enhanced_article
                
                # Remove the similar articles that were merged
                for dup_id in duplicate_ids:
                    if dup_id in article_map:
                        articles_to_remove.add(dup_id)
                        logger.debug(f"Merging similar article {dup_id} into {representative_id}")
        
        # Build the final article list
        resolved_articles = []
        for article in original_articles:
            article_id = str(article.id)
            
            if article_id in articles_to_remove:
                continue  # Skip removed articles
            elif article_id in articles_to_update:
                resolved_articles.append(articles_to_update[article_id])
            else:
                resolved_articles.append(article)
        
        logger.info(f"Resolved {len(articles_to_remove)} duplicate articles using advanced detection")
        return resolved_articles

    def _merge_similar_article_metadata(
        self, 
        primary_article: Article, 
        similar_articles: list[Article], 
        similarity_score: float
    ) -> Article:
        """Merge similar articles' metadata into a primary article.
        
        Args:
            primary_article: The main article to keep
            similar_articles: Similar articles to merge
            similarity_score: Average similarity score
            
        Returns:
            Enhanced primary article with merged metadata
        """
        enhanced = Article(
            id=primary_article.id,
            title=primary_article.title,
            slug=primary_article.slug,
            content=primary_article.content,
            category_id=primary_article.category_id,
            status=primary_article.status,
            order=primary_article.order,
            updated_at=primary_article.updated_at,
            created_at=primary_article.created_at,
            language=primary_article.language,
            published_at=primary_article.published_at
        )
        
        # If similar articles have richer content, consider using it
        for similar in similar_articles:
            if (similar.content and len(similar.content) > len(enhanced.content or "") * 1.2 and
                similarity_score > 0.8):
                logger.debug(f"Using richer content from similar article for {enhanced.id}")
                enhanced.content = similar.content
                break
        
        return enhanced

    def get_processing_statistics(self) -> dict[str, Any]:
        """Get processing statistics.
        
        Returns:
            Dictionary of processing statistics
        """
        return self.stats.copy()

    def reset_statistics(self) -> None:
        """Reset processing statistics."""
        self.stats = {
            "articles_processed": 0,
            "content_enhanced": 0,
            "duplicates_resolved": 0,
            "merge_operations": 0,
        }