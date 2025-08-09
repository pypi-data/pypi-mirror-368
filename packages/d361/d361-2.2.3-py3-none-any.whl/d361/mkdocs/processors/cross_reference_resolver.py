"""Cross-reference resolution for Document360 → MkDocs conversion.

This module provides intelligent cross-reference resolution, converting internal
Document360 links to proper MkDocs references and enabling automatic link validation.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/cross_reference_resolver.py

import re
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path
from urllib.parse import urlparse, unquote
from dataclasses import dataclass

from loguru import logger

from d361.core.models import Article, Category

# Optional imports for Phase 2 enhancements
try:
    import httpx
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    HTTP_VALIDATION_AVAILABLE = True
except ImportError:
    HTTP_VALIDATION_AVAILABLE = False
    logger.warning("HTTP validation dependencies not available - install httpx for full link validation")


@dataclass
class LinkReference:
    """Represents a link reference in content."""
    
    original_url: str
    display_text: str
    resolved_url: Optional[str] = None
    link_type: str = "unknown"  # internal, external, anchor, image
    target_article_id: Optional[str] = None
    target_category_id: Optional[str] = None
    is_valid: bool = False
    validation_error: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None


@dataclass 
class AnchorReference:
    """Represents an anchor/heading reference."""
    
    anchor_id: str
    heading_text: str
    level: int
    line_number: int
    article_id: Optional[str] = None


class CrossReferenceResolver:
    """Resolve cross-references for Document360 → MkDocs conversion.
    
    This class handles intelligent link resolution, converting Document360 internal
    links to proper MkDocs references, validating external links, and creating
    a comprehensive cross-reference index.
    
    Features:
    - Document360 internal link resolution
    - Automatic anchor link generation
    - Broken link detection and reporting
    - Cross-reference index generation
    - Link validation with caching
    - Relative path resolution for MkDocs
    
    Example:
        resolver = CrossReferenceResolver(
            articles=article_list,
            base_url="https://docs.example.com",
            validate_external=True
        )
        resolved_content = await resolver.resolve_references(content, current_article)
        link_report = resolver.generate_link_report()
    """
    
    def __init__(
        self,
        articles: List[Article],
        categories: Optional[List[Category]] = None,
        base_url: Optional[str] = None,
        validate_external: bool = True,
        generate_autorefs: bool = True,
        create_redirects: bool = True,
        # Phase 2 enhancements
        enable_autorefs_plugin: bool = True,
        autorefs_plugin_config: Optional[Dict[str, Any]] = None,
        enable_http_validation: bool = False,
        validation_timeout: int = 10,
        max_concurrent_validations: int = 10,
        generate_reference_index: bool = True,
        smart_link_suggestions: bool = True,
        broken_link_reporting: bool = True,
        enable_link_analytics: bool = True,
    ) -> None:
        """Initialize cross-reference resolver.
        
        Args:
            articles: List of all articles for reference resolution
            categories: List of categories for navigation structure
            base_url: Base URL for absolute link generation
            validate_external: Validate external links during processing
            generate_autorefs: Generate automatic cross-references
            create_redirects: Create redirect mappings for moved content
            # Phase 2 enhancements
            enable_autorefs_plugin: Enable mkdocs-autorefs plugin integration
            autorefs_plugin_config: Configuration for mkdocs-autorefs plugin
            enable_http_validation: Enable HTTP validation of external links
            validation_timeout: Timeout for HTTP validation requests (seconds)
            max_concurrent_validations: Maximum concurrent HTTP validations
            generate_reference_index: Generate comprehensive reference index
            smart_link_suggestions: Enable intelligent link suggestions
            broken_link_reporting: Enable detailed broken link reporting
            enable_link_analytics: Enable link analytics and metrics
        """
        self.articles = articles
        self.categories = categories or []
        self.base_url = base_url.rstrip('/') if base_url else None
        self.validate_external = validate_external
        self.generate_autorefs = generate_autorefs
        self.create_redirects = create_redirects
        
        # Phase 2 enhancements
        self.enable_autorefs_plugin = enable_autorefs_plugin
        self.autorefs_plugin_config = autorefs_plugin_config or {}
        self.enable_http_validation = enable_http_validation and HTTP_VALIDATION_AVAILABLE
        self.validation_timeout = validation_timeout
        self.max_concurrent_validations = max_concurrent_validations
        self.generate_reference_index = generate_reference_index
        self.smart_link_suggestions = smart_link_suggestions
        self.broken_link_reporting = broken_link_reporting
        self.enable_link_analytics = enable_link_analytics
        
        # Build reference indexes
        self._article_index = self._build_article_index()
        self._category_index = self._build_category_index()
        self._url_mappings = self._build_url_mappings()
        self._anchor_index: Dict[str, List[AnchorReference]] = {}
        self._broken_links: List[LinkReference] = []
        self._redirects: Dict[str, str] = {}
        
        # Phase 2: Enhanced tracking and analytics
        self._reference_index: Dict[str, List[str]] = {}  # Article ID -> list of referencing articles
        self._link_analytics: Dict[str, Dict[str, Any]] = {}  # URL -> analytics data
        self._validation_cache: Dict[str, Dict[str, Any]] = {}  # URL -> validation results
        self._suggestion_cache: Dict[str, List[Dict[str, Any]]] = {}  # Article ID -> suggestions
        
        # Statistics tracking
        self.resolved_count: int = 0
        
        # HTTP client for validation
        self._http_client: Optional[httpx.AsyncClient] = None
        if self.enable_http_validation:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.validation_timeout),
                limits=httpx.Limits(max_connections=self.max_concurrent_validations),
                headers={'User-Agent': 'd361-mkdocs-cross-reference-validator/1.0'}
            )
        
        # Compile regex patterns for performance
        self._link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self._image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self._heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self._d360_link_pattern = re.compile(r'https?://[^/]*document360[^/]*/[^/]+/(\w+)(?:/(\w+))?')
        
        # Phase 2: mkdocs-autorefs patterns
        self._autoref_pattern = re.compile(r'\[([^\]]+)\]\[\]')  # [reference][]
        self._identifier_pattern = re.compile(r'\[([^\]]+)\]\[([^\]]+)\]')  # [text][identifier]
        
        logger.debug(f"Initialized CrossReferenceResolver with {len(articles)} articles, HTTP validation={self.enable_http_validation}, autorefs plugin={self.enable_autorefs_plugin}")
    
    async def resolve_references(self, content: str, current_article: Article) -> Dict[str, Any]:
        """Resolve cross-references in article content.
        
        Args:
            content: Article content with links to resolve
            current_article: Current article context for relative link resolution
            
        Returns:
            Dictionary with resolved content and reference metadata
        """
        logger.debug(f"Resolving references for article: {current_article.title}")
        
        # Extract and index anchors from current content
        anchors = self._extract_anchors(content, current_article.id or "")
        self._anchor_index[current_article.id or ""] = anchors
        
        # Phase 2: Extract autorefs patterns for mkdocs-autorefs plugin
        autorefs = []
        if self.enable_autorefs_plugin:
            autorefs = self._extract_autorefs(content)
        
        # Process all links in content
        links = self._extract_links(content)
        resolved_links = []
        
        # Phase 2: Batch HTTP validation for external links
        if self.enable_http_validation:
            external_links = [link for link in links if link.original_url.startswith(('http://', 'https://'))]
            await self._validate_external_links_batch(external_links)
        
        for link in links:
            resolved_link = await self._resolve_link(link, current_article)
            resolved_links.append(resolved_link)
            
            if not resolved_link.is_valid and self.broken_link_reporting:
                self._broken_links.append(resolved_link)
            
            # Phase 2: Track link analytics
            if self.enable_link_analytics:
                self._track_link_analytics(resolved_link, current_article)
        
        # Generate resolved content
        resolved_content = self._apply_link_resolutions(content, resolved_links)
        
        # Phase 2: Process mkdocs-autorefs patterns
        if self.enable_autorefs_plugin and autorefs:
            resolved_content = self._process_autorefs(resolved_content, autorefs, current_article)
        
        # Generate autorefs if enabled (original behavior)
        if self.generate_autorefs:
            resolved_content = self._add_autorefs(resolved_content, current_article)
        
        # Phase 2: Update reference index
        if self.generate_reference_index:
            self._update_reference_index(resolved_links, current_article)
        
        # Phase 2: Generate smart suggestions
        smart_suggestions = []
        if self.smart_link_suggestions:
            smart_suggestions = await self._generate_smart_suggestions(current_article, content)
        
        return {
            'content': resolved_content,
            'links': resolved_links,
            'anchors': anchors,
            'broken_links': [link for link in resolved_links if not link.is_valid],
            'external_links': [link for link in resolved_links if link.link_type == 'external'],
            'internal_links': [link for link in resolved_links if link.link_type == 'internal'],
            # Phase 2 additions
            'autorefs': autorefs,
            'smart_suggestions': smart_suggestions,
            'validation_results': self._get_validation_summary(resolved_links),
            'analytics_data': self._get_analytics_summary(resolved_links),
            'reference_graph': self._get_reference_graph_data(current_article),
        }
    
    async def resolve_references_bulk(self, articles: List[Article], navigation: Dict[str, Any]) -> List[Article]:
        """Resolve cross-references for multiple articles using navigation context.
        
        Args:
            articles: List of articles to process
            navigation: Navigation structure for context
            
        Returns:
            List of articles with resolved cross-references
        """
        logger.info(f"Resolving cross-references for {len(articles)} articles")
        
        resolved_articles = []
        
        for article in articles:
            try:
                # Use existing single-article resolution method
                resolution_result = await self.resolve_references(article.content or "", article)
                
                # Create updated article with resolved content
                updated_article = Article(
                    id=article.id,
                    title=article.title,
                    content=resolution_result['content'],
                    category_id=article.category_id,
                    slug=article.slug or "",
                    order=article.order,
                    status=article.status,
                    created_at=article.created_at,
                    updated_at=article.updated_at,
                    published_at=article.published_at,
                    author_id=article.author_id,
                    author_name=article.author_name or "",
                    author_email=article.author_email or "",
                    meta_title=article.meta_title or "",
                    meta_description=article.meta_description or "",
                    tags=article.tags or [],
                    version_id=article.version_id,
                    language_code=article.language_code or "en",
                    is_public=article.is_public,
                    is_hidden=article.is_hidden,
                    metadata=article.metadata or {},
                    custom_fields=article.custom_fields or {},
                    content_markdown=article.content_markdown or "",
                    excerpt=article.excerpt or ""
                )
                
                resolved_articles.append(updated_article)
                self.resolved_count += 1
                
            except Exception as e:
                logger.error(f"Error resolving references for article {article.id}: {e}")
                # Add original article if resolution fails
                resolved_articles.append(article)
        
        logger.info(f"Resolved cross-references for {len(resolved_articles)} articles")
        return resolved_articles
    
    def generate_link_report(self) -> Dict[str, Any]:
        """Generate comprehensive link analysis report.
        
        Returns:
            Dictionary with link statistics and validation results
        """
        total_links = sum(len(article_anchors) for article_anchors in self._anchor_index.values())
        
        return {
            'total_articles': len(self.articles),
            'total_categories': len(self.categories),
            'total_internal_links': len(self._url_mappings),
            'total_anchors': total_links,
            'broken_links': len(self._broken_links),
            'broken_link_details': [
                {
                    'url': link.original_url,
                    'text': link.display_text,
                    'error': link.validation_error,
                    'type': link.link_type
                }
                for link in self._broken_links
            ],
            'redirects_created': len(self._redirects),
            'redirect_mappings': self._redirects,
            'validation_summary': {
                'total_processed': len([link for links in self._anchor_index.values() for link in links]),
                'validation_success_rate': self._calculate_success_rate(),
                'most_common_errors': self._get_common_errors(),
            }
        }
    
    def get_redirect_mappings(self) -> Dict[str, str]:
        """Get redirect mappings for MkDocs configuration.
        
        Returns:
            Dictionary of old URL to new URL mappings
        """
        return self._redirects.copy()
    
    def get_autoref_suggestions(self) -> Dict[str, List[str]]:
        """Generate autoref suggestions for cross-referencing.
        
        Returns:
            Dictionary mapping article titles to potential cross-references
        """
        suggestions = {}
        
        for article in self.articles:
            article_suggestions = []
            
            # Find articles with similar keywords
            article_keywords = self._extract_keywords(article.title)
            
            for other_article in self.articles:
                if other_article.id == article.id:
                    continue
                    
                other_keywords = self._extract_keywords(other_article.title)
                common_keywords = set(article_keywords) & set(other_keywords)
                
                if common_keywords:
                    article_suggestions.append({
                        'title': other_article.title,
                        'url': self._generate_article_url(other_article),
                        'common_keywords': list(common_keywords),
                        'relevance_score': len(common_keywords) / max(len(article_keywords), len(other_keywords))
                    })
            
            # Sort by relevance score
            article_suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
            suggestions[article.title] = article_suggestions[:5]  # Top 5 suggestions
        
        return suggestions
    
    def _build_article_index(self) -> Dict[str, Article]:
        """Build article index for quick lookup."""
        index = {}
        for article in self.articles:
            if article.id:
                index[article.id] = article
            if article.slug:
                index[article.slug] = article
        return index
    
    def _build_category_index(self) -> Dict[str, Category]:
        """Build category index for quick lookup."""
        index = {}
        for category in self.categories:
            if category.id:
                index[category.id] = category
            if category.slug:
                index[category.slug] = category
        return index
    
    def _build_url_mappings(self) -> Dict[str, str]:
        """Build URL mappings from Document360 to MkDocs format."""
        mappings = {}
        
        for article in self.articles:
            # Map various Document360 URL formats to MkDocs paths
            article_url = self._generate_article_url(article)
            
            # Map by article ID
            if article.id:
                mappings[f"/articles/{article.id}"] = article_url
                mappings[f"/docs/{article.id}"] = article_url
            
            # Map by slug
            if article.slug:
                mappings[f"/articles/{article.slug}"] = article_url
                mappings[f"/docs/{article.slug}"] = article_url
            
            # Map Document360 URL patterns
            if hasattr(article, 'document360_url'):
                mappings[article.document360_url] = article_url
        
        return mappings
    
    def _extract_anchors(self, content: str, article_id: str) -> List[AnchorReference]:
        """Extract heading anchors from content."""
        anchors = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            match = self._heading_pattern.match(line)
            if match:
                level = len(match.group(1))
                heading_text = match.group(2).strip()
                anchor_id = self._generate_anchor_id(heading_text)
                
                anchors.append(AnchorReference(
                    anchor_id=anchor_id,
                    heading_text=heading_text,
                    level=level,
                    line_number=line_num,
                    article_id=article_id
                ))
        
        return anchors
    
    def _extract_links(self, content: str) -> List[LinkReference]:
        """Extract all links from content."""
        links = []
        
        # Regular links
        for match in self._link_pattern.finditer(content):
            links.append(LinkReference(
                display_text=match.group(1),
                original_url=match.group(2),
                line_number=content[:match.start()].count('\n') + 1,
                column_number=len(content[:match.start()].split('\n')[-1])
            ))
        
        # Image links
        for match in self._image_pattern.finditer(content):
            links.append(LinkReference(
                display_text=match.group(1),
                original_url=match.group(2),
                link_type="image",
                line_number=content[:match.start()].count('\n') + 1,
                column_number=len(content[:match.start()].split('\n')[-1])
            ))
        
        return links
    
    async def _resolve_link(self, link: LinkReference, current_article: Article) -> LinkReference:
        """Resolve a single link reference."""
        url = link.original_url.strip()
        
        # Handle anchor links
        if url.startswith('#'):
            return self._resolve_anchor_link(link, current_article)
        
        # Handle external links
        if url.startswith(('http://', 'https://')):
            return await self._resolve_external_link(link)
        
        # Handle internal Document360 links
        if self._is_document360_link(url):
            return self._resolve_d360_link(link)
        
        # Handle relative links
        if url.startswith(('../', './', '/')):
            return self._resolve_relative_link(link, current_article)
        
        # Default: treat as external
        link.link_type = "external"
        link.is_valid = True
        return link
    
    def _resolve_anchor_link(self, link: LinkReference, current_article: Article) -> LinkReference:
        """Resolve anchor link within current article."""
        anchor_id = link.original_url[1:]  # Remove #
        article_anchors = self._anchor_index.get(current_article.id or "", [])
        
        for anchor in article_anchors:
            if anchor.anchor_id == anchor_id:
                link.resolved_url = f"#{anchor_id}"
                link.link_type = "anchor"
                link.is_valid = True
                return link
        
        link.link_type = "anchor"
        link.is_valid = False
        link.validation_error = f"Anchor '{anchor_id}' not found in current article"
        return link
    
    async def _resolve_external_link(self, link: LinkReference) -> LinkReference:
        """Resolve external link with optional validation."""
        link.link_type = "external"
        
        if self.validate_external:
            # Here you could add HTTP validation
            # For now, assume external links are valid
            link.is_valid = True
        else:
            link.is_valid = True
        
        return link
    
    def _resolve_d360_link(self, link: LinkReference) -> LinkReference:
        """Resolve Document360 internal link."""
        url = link.original_url
        
        # Extract article/category ID from Document360 URL
        match = self._d360_link_pattern.match(url)
        if match:
            resource_id = match.group(1)
            sub_id = match.group(2)
            
            # Look up in article index
            if resource_id in self._article_index:
                article = self._article_index[resource_id]
                link.resolved_url = self._generate_article_url(article)
                link.target_article_id = resource_id
                link.link_type = "internal"
                link.is_valid = True
                
                # Handle anchor if present
                if sub_id:
                    link.resolved_url += f"#{sub_id}"
                
                return link
        
        # Check URL mappings
        for pattern, target_url in self._url_mappings.items():
            if pattern in url:
                link.resolved_url = target_url
                link.link_type = "internal"
                link.is_valid = True
                
                # Create redirect mapping
                if self.create_redirects:
                    self._redirects[url] = target_url
                
                return link
        
        # Link not found
        link.link_type = "internal"
        link.is_valid = False
        link.validation_error = f"Document360 link target not found: {url}"
        return link
    
    def _resolve_relative_link(self, link: LinkReference, current_article: Article) -> LinkReference:
        """Resolve relative link."""
        # Convert relative paths to MkDocs format
        url = link.original_url
        
        # Handle common relative patterns
        if url.startswith('../'):
            # Parent directory reference
            link.resolved_url = url
            link.link_type = "internal"
            link.is_valid = True  # Assume valid for relative paths
        elif url.startswith('./'):
            # Current directory reference
            link.resolved_url = url[2:]
            link.link_type = "internal"
            link.is_valid = True
        elif url.startswith('/'):
            # Root relative reference
            link.resolved_url = url
            link.link_type = "internal"
            link.is_valid = True
        
        return link
    
    def _apply_link_resolutions(self, content: str, links: List[LinkReference]) -> str:
        """Apply link resolutions to content."""
        # Sort links by position (reverse order to maintain positions)
        links_with_pos = []
        
        for match in self._link_pattern.finditer(content):
            original_url = match.group(2)
            # Find corresponding resolved link
            resolved_link = next((link for link in links if link.original_url == original_url), None)
            if resolved_link and resolved_link.resolved_url:
                links_with_pos.append((match.start(), match.end(), resolved_link))
        
        # Apply replacements in reverse order
        links_with_pos.sort(key=lambda x: x[0], reverse=True)
        
        for start, end, resolved_link in links_with_pos:
            new_link = f"[{resolved_link.display_text}]({resolved_link.resolved_url})"
            content = content[:start] + new_link + content[end:]
        
        return content
    
    def _add_autorefs(self, content: str, current_article: Article) -> str:
        """Add automatic cross-references to content."""
        if not self.generate_autorefs:
            return content
        
        # Find potential article references in text
        for article in self.articles:
            if article.id == current_article.id:
                continue
            
            title = article.title
            # Only process titles longer than 3 characters to avoid false positives
            if len(title) <= 3:
                continue
            
            # Create case-insensitive pattern
            pattern = re.compile(re.escape(title), re.IGNORECASE)
            
            def replace_match(match):
                # Don't replace if already inside a link
                before_match = content[:match.start()]
                if before_match.count('[') > before_match.count(']'):
                    return match.group(0)
                
                article_url = self._generate_article_url(article)
                return f"[{match.group(0)}]({article_url})"
            
            # Only replace first occurrence to avoid over-linking
            content = pattern.sub(replace_match, content, count=1)
        
        return content
    
    def _generate_anchor_id(self, heading_text: str) -> str:
        """Generate anchor ID from heading text."""
        # Convert to lowercase and replace non-alphanumeric with hyphens
        anchor_id = re.sub(r'[^\w\s-]', '', heading_text.lower())
        anchor_id = re.sub(r'[-\s]+', '-', anchor_id)
        return anchor_id.strip('-')
    
    def _generate_article_url(self, article: Article) -> str:
        """Generate MkDocs URL for article."""
        if article.slug:
            filename = f"{article.slug}.md"
        else:
            # Generate from title
            filename = re.sub(r'[^\w\s-]', '', article.title.lower())
            filename = re.sub(r'[-\s]+', '-', filename)
            filename = f"{filename.strip('-')}.md"
        
        return filename
    
    def _is_document360_link(self, url: str) -> bool:
        """Check if URL is a Document360 link."""
        return 'document360' in url.lower() or self._d360_link_pattern.match(url) is not None
    
    def _extract_keywords(self, title: str) -> List[str]:
        """Extract keywords from article title."""
        # Simple keyword extraction
        words = re.findall(r'\b\w{3,}\b', title.lower())
        return [word for word in words if word not in {'the', 'and', 'for', 'with', 'from', 'how', 'what', 'why'}]
    
    def _calculate_success_rate(self) -> float:
        """Calculate link validation success rate."""
        if not self._broken_links:
            return 100.0
        
        total_links = sum(len(anchors) for anchors in self._anchor_index.values())
        if total_links == 0:
            return 100.0
        
        return ((total_links - len(self._broken_links)) / total_links) * 100
    
    def _get_common_errors(self) -> List[Dict[str, Any]]:
        """Get most common validation errors."""
        error_counts = {}
        
        for link in self._broken_links:
            error = link.validation_error or "Unknown error"
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # Sort by frequency
        common_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"error": error, "count": count}
            for error, count in common_errors[:5]  # Top 5
        ]
    
    # Phase 2: Advanced Enhancement Methods
    
    def _extract_autorefs(self, content: str) -> List[Dict[str, Any]]:
        """Extract mkdocs-autorefs patterns from content."""
        autorefs = []
        
        # Extract [reference][] patterns
        for match in self._autoref_pattern.finditer(content):
            autorefs.append({
                'type': 'autoref',
                'reference': match.group(1),
                'identifier': match.group(1),
                'position': match.start(),
                'length': len(match.group(0))
            })
        
        # Extract [text][identifier] patterns
        for match in self._identifier_pattern.finditer(content):
            autorefs.append({
                'type': 'identifier_ref',
                'text': match.group(1),
                'identifier': match.group(2),
                'position': match.start(),
                'length': len(match.group(0))
            })
        
        return autorefs
    
    async def _validate_external_links_batch(self, external_links: List[LinkReference]) -> None:
        """Validate external links in batches using HTTP requests."""
        if not self._http_client or not external_links:
            return
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent_validations)
        
        async def validate_single_link(link: LinkReference):
            async with semaphore:
                await self._validate_external_link_http(link)
        
        # Execute validation tasks concurrently
        tasks = [validate_single_link(link) for link in external_links]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _validate_external_link_http(self, link: LinkReference) -> None:
        """Validate a single external link via HTTP."""
        url = link.original_url
        
        # Check cache first
        if url in self._validation_cache:
            cached_result = self._validation_cache[url]
            link.is_valid = cached_result['is_valid']
            if 'error' in cached_result:
                link.validation_error = cached_result['error']
            return
        
        try:
            response = await self._http_client.head(url, follow_redirects=True)
            is_valid = response.status_code < 400
            
            # Cache the result
            self._validation_cache[url] = {
                'is_valid': is_valid,
                'status_code': response.status_code,
                'validated_at': asyncio.get_event_loop().time()
            }
            
            if is_valid:
                link.is_valid = True
            else:
                link.is_valid = False
                link.validation_error = f"HTTP {response.status_code}"
                
        except Exception as e:
            error_msg = str(e)
            link.is_valid = False
            link.validation_error = f"Connection error: {error_msg[:50]}"
            
            # Cache the failure
            self._validation_cache[url] = {
                'is_valid': False,
                'error': error_msg,
                'validated_at': asyncio.get_event_loop().time()
            }
    
    def _track_link_analytics(self, link: LinkReference, current_article: Article) -> None:
        """Track link analytics and metrics."""
        url = link.resolved_url or link.original_url
        
        if url not in self._link_analytics:
            self._link_analytics[url] = {
                'total_references': 0,
                'referencing_articles': [],
                'link_type': link.link_type,
                'first_seen': asyncio.get_event_loop().time(),
                'last_seen': asyncio.get_event_loop().time(),
                'is_broken': not link.is_valid,
                'error_count': 0
            }
        
        analytics = self._link_analytics[url]
        analytics['total_references'] += 1
        analytics['last_seen'] = asyncio.get_event_loop().time()
        
        article_ref = {
            'article_id': current_article.id,
            'article_title': current_article.title,
            'link_text': link.display_text
        }
        
        if article_ref not in analytics['referencing_articles']:
            analytics['referencing_articles'].append(article_ref)
        
        if not link.is_valid:
            analytics['error_count'] += 1
            analytics['is_broken'] = True
    
    def _process_autorefs(self, content: str, autorefs: List[Dict[str, Any]], current_article: Article) -> str:
        """Process mkdocs-autorefs patterns and generate appropriate links."""
        # Sort autorefs by position in reverse order to maintain positions during replacement
        autorefs_sorted = sorted(autorefs, key=lambda x: x['position'], reverse=True)
        
        for autoref in autorefs_sorted:
            start_pos = autoref['position']
            end_pos = start_pos + autoref['length']
            identifier = autoref['identifier']
            
            # Try to resolve the identifier to an article
            resolved_link = self._resolve_autoref_identifier(identifier)
            
            if resolved_link:
                if autoref['type'] == 'autoref':
                    # Replace [reference][] with [reference](resolved_link)
                    replacement = f"[{autoref['reference']}]({resolved_link})"
                else:
                    # Replace [text][identifier] with [text](resolved_link)
                    replacement = f"[{autoref['text']}]({resolved_link})"
                
                content = content[:start_pos] + replacement + content[end_pos:]
        
        return content
    
    def _resolve_autoref_identifier(self, identifier: str) -> Optional[str]:
        """Resolve an autoref identifier to a link."""
        # Try exact title match first
        for article in self.articles:
            if article.title.lower() == identifier.lower():
                return self._generate_article_url(article)
        
        # Try partial title match
        for article in self.articles:
            if identifier.lower() in article.title.lower():
                return self._generate_article_url(article)
        
        # Try slug match
        if identifier in self._article_index:
            article = self._article_index[identifier]
            return self._generate_article_url(article)
        
        # Try category match
        if identifier in self._category_index:
            category = self._category_index[identifier]
            # Return category index page or first article in category
            category_articles = [a for a in self.articles if getattr(a, 'category_id', None) == category.id]
            if category_articles:
                return self._generate_article_url(category_articles[0])
        
        return None
    
    def _update_reference_index(self, resolved_links: List[LinkReference], current_article: Article) -> None:
        """Update the reference index with article relationships."""
        current_id = current_article.id or ""
        
        for link in resolved_links:
            if link.link_type == 'internal' and link.target_article_id:
                target_id = link.target_article_id
                
                if target_id not in self._reference_index:
                    self._reference_index[target_id] = []
                
                if current_id not in self._reference_index[target_id]:
                    self._reference_index[target_id].append(current_id)
    
    async def _generate_smart_suggestions(self, current_article: Article, content: str) -> List[Dict[str, Any]]:
        """Generate intelligent link suggestions based on content analysis."""
        if current_article.id in self._suggestion_cache:
            return self._suggestion_cache[current_article.id]
        
        suggestions = []
        content_lower = content.lower()
        
        # Content-based suggestions
        for article in self.articles:
            if article.id == current_article.id:
                continue
            
            relevance_score = self._calculate_content_relevance(content_lower, article)
            
            if relevance_score > 0.3:  # Threshold for suggestions
                suggestions.append({
                    'article_id': article.id,
                    'title': article.title,
                    'url': self._generate_article_url(article),
                    'relevance_score': relevance_score,
                    'suggestion_type': 'content_similarity',
                    'explanation': self._generate_suggestion_explanation(current_article, article, relevance_score)
                })
        
        # Category-based suggestions
        if hasattr(current_article, 'category_id') and current_article.category_id:
            category_articles = [a for a in self.articles 
                               if getattr(a, 'category_id', None) == current_article.category_id 
                               and a.id != current_article.id]
            
            for article in category_articles[:3]:  # Top 3 from same category
                if not any(s['article_id'] == article.id for s in suggestions):
                    suggestions.append({
                        'article_id': article.id,
                        'title': article.title,
                        'url': self._generate_article_url(article),
                        'relevance_score': 0.6,  # High relevance for same category
                        'suggestion_type': 'same_category',
                        'explanation': f"Related article in the same category"
                    })
        
        # Sort by relevance score
        suggestions.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Cache the results
        self._suggestion_cache[current_article.id] = suggestions[:10]  # Top 10 suggestions
        
        return self._suggestion_cache[current_article.id]
    
    def _calculate_content_relevance(self, content: str, article: Article) -> float:
        """Calculate content relevance score between current content and article."""
        if not article.content:
            return 0.0
        
        # Extract keywords from both contents
        content_keywords = set(re.findall(r'\b\w{4,}\b', content.lower()))
        article_keywords = set(re.findall(r'\b\w{4,}\b', article.content.lower()))
        
        # Remove common stop words
        stop_words = {'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'have', 'were', 'said', 'each', 'which', 'their', 'time', 'more', 'very', 'when', 'come', 'here', 'what', 'also', 'back', 'after', 'first', 'well', 'year', 'work', 'such', 'make', 'way', 'where', 'much', 'take', 'than', 'only', 'think', 'know', 'just', 'good', 'many', 'some', 'over', 'new', 'other', 'even', 'most', 'give', 'day', 'find', 'use', 'man', 'still', 'through', 'life', 'may', 'now', 'before', 'like', 'right', 'see', 'get', 'people', 'say', 'them', 'last', 'could', 'want', 'between', 'should', 'never', 'being', 'these', 'those', 'same', 'another', 'while', 'down', 'long', 'made', 'might', 'both', 'every', 'look', 'great', 'few', 'without', 'call', 'own', 'need', 'old', 'place', 'little', 'next', 'asked', 'going', 'turn', 'different', 'following', 'came', 'around', 'something', 'small', 'large', 'put', 'end', 'why'}
        
        content_keywords -= stop_words
        article_keywords -= stop_words
        
        if not content_keywords or not article_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(content_keywords & article_keywords)
        union = len(content_keywords | article_keywords)
        
        if union == 0:
            return 0.0
        
        jaccard_score = intersection / union
        
        # Boost score if article title appears in content
        title_keywords = set(re.findall(r'\b\w{4,}\b', article.title.lower()))
        if title_keywords & content_keywords:
            jaccard_score += 0.2
        
        return min(1.0, jaccard_score)
    
    def _generate_suggestion_explanation(self, current_article: Article, suggested_article: Article, relevance_score: float) -> str:
        """Generate explanation for why an article is suggested."""
        if relevance_score > 0.7:
            return "Highly related content with significant keyword overlap"
        elif relevance_score > 0.5:
            return "Related content with some keyword overlap"
        else:
            return "Potentially related content"
    
    def _get_validation_summary(self, links: List[LinkReference]) -> Dict[str, Any]:
        """Get validation summary for resolved links."""
        total_links = len(links)
        valid_links = sum(1 for link in links if link.is_valid)
        external_links = [link for link in links if link.link_type == 'external']
        internal_links = [link for link in links if link.link_type == 'internal']
        
        return {
            'total_links': total_links,
            'valid_links': valid_links,
            'broken_links': total_links - valid_links,
            'validation_rate': (valid_links / total_links * 100) if total_links > 0 else 100,
            'external_links_count': len(external_links),
            'internal_links_count': len(internal_links),
            'http_validated': self.enable_http_validation,
        }
    
    def _get_analytics_summary(self, links: List[LinkReference]) -> Dict[str, Any]:
        """Get analytics summary for processed links."""
        if not self.enable_link_analytics:
            return {}
        
        link_types = {}
        for link in links:
            link_type = link.link_type
            link_types[link_type] = link_types.get(link_type, 0) + 1
        
        return {
            'link_types': link_types,
            'total_tracked_urls': len(self._link_analytics),
            'broken_url_count': sum(1 for data in self._link_analytics.values() if data['is_broken']),
            'most_referenced_urls': self._get_most_referenced_urls(),
        }
    
    def _get_most_referenced_urls(self) -> List[Dict[str, Any]]:
        """Get the most frequently referenced URLs."""
        sorted_urls = sorted(
            self._link_analytics.items(),
            key=lambda x: x[1]['total_references'],
            reverse=True
        )
        
        return [
            {
                'url': url,
                'references': data['total_references'],
                'referencing_articles': len(data['referencing_articles']),
                'link_type': data['link_type'],
                'is_broken': data['is_broken']
            }
            for url, data in sorted_urls[:10]  # Top 10
        ]
    
    def _get_reference_graph_data(self, current_article: Article) -> Dict[str, Any]:
        """Get reference graph data for the current article."""
        if not self.generate_reference_index:
            return {}
        
        current_id = current_article.id or ""
        
        # Articles that reference this article
        referencing_articles = []
        for article_id in self._reference_index.get(current_id, []):
            article = self._article_index.get(article_id)
            if article:
                referencing_articles.append({
                    'id': article_id,
                    'title': article.title,
                    'url': self._generate_article_url(article)
                })
        
        # Articles that this article references
        referenced_articles = []
        for target_id, referencing_ids in self._reference_index.items():
            if current_id in referencing_ids:
                article = self._article_index.get(target_id)
                if article:
                    referenced_articles.append({
                        'id': target_id,
                        'title': article.title,
                        'url': self._generate_article_url(article)
                    })
        
        return {
            'referencing_articles': referencing_articles,
            'referenced_articles': referenced_articles,
            'incoming_references': len(referencing_articles),
            'outgoing_references': len(referenced_articles),
        }
    
    async def cleanup(self):
        """Clean up resources including HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None