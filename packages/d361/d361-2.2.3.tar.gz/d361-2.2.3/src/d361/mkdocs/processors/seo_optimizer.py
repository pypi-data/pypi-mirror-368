"""SEO optimization and structured data generation for MkDocs sites.

This module provides comprehensive SEO optimization capabilities including
structured data generation, meta tag optimization, and social media integration.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/seo_optimizer.py

import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

from loguru import logger

from d361.api.errors import Document360Error, ErrorCategory, ErrorSeverity


@dataclass
class SEOMetadata:
    """SEO metadata for a page or site."""
    
    title: str
    description: str
    canonical_url: Optional[str] = None
    og_image: Optional[str] = None
    og_type: str = "article"
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    schema_type: str = "Article"
    lang: str = "en"
    
    def to_frontmatter(self) -> Dict[str, Any]:
        """Convert to MkDocs frontmatter format."""
        frontmatter = {
            "title": self.title,
            "description": self.description,
        }
        
        if self.canonical_url:
            frontmatter["canonical_url"] = self.canonical_url
        
        if self.tags:
            frontmatter["tags"] = self.tags
        
        if self.author:
            frontmatter["author"] = self.author
        
        if self.published_date:
            frontmatter["date"] = self.published_date.isoformat()
        
        if self.modified_date:
            frontmatter["last_modified"] = self.modified_date.isoformat()
        
        return frontmatter


@dataclass
class StructuredData:
    """Structured data for JSON-LD generation."""
    
    context: str = "https://schema.org"
    type: str = "Article"
    headline: Optional[str] = None
    description: Optional[str] = None
    author: Optional[Dict[str, Any]] = None
    publisher: Optional[Dict[str, Any]] = None
    date_published: Optional[str] = None
    date_modified: Optional[str] = None
    url: Optional[str] = None
    image: Optional[Union[str, List[str]]] = None
    keywords: List[str] = field(default_factory=list)
    article_section: Optional[str] = None
    word_count: Optional[int] = None
    
    def to_json_ld(self) -> str:
        """Generate JSON-LD structured data."""
        data = {
            "@context": self.context,
            "@type": self.type
        }
        
        if self.headline:
            data["headline"] = self.headline
        
        if self.description:
            data["description"] = self.description
        
        if self.author:
            data["author"] = self.author
        
        if self.publisher:
            data["publisher"] = self.publisher
        
        if self.date_published:
            data["datePublished"] = self.date_published
        
        if self.date_modified:
            data["dateModified"] = self.date_modified
        
        if self.url:
            data["url"] = self.url
        
        if self.image:
            data["image"] = self.image
        
        if self.keywords:
            data["keywords"] = self.keywords
        
        if self.article_section:
            data["articleSection"] = self.article_section
        
        if self.word_count:
            data["wordCount"] = self.word_count
        
        return json.dumps(data, indent=2, ensure_ascii=False)


class SEOOptimizer:
    """Comprehensive SEO optimization for MkDocs sites.
    
    This class provides advanced SEO optimization including:
    - Meta tag generation and optimization
    - Structured data (JSON-LD) generation
    - Social media optimization (Open Graph, Twitter Cards)
    - Sitemap generation support
    - Performance optimization recommendations
    - Accessibility enhancements
    
    Example:
        seo = SEOOptimizer(
            site_url="https://docs.example.com",
            site_name="Example Documentation",
            default_author="Example Team"
        )
        
        metadata = await seo.generate_page_metadata(
            title="API Reference",
            content="Complete API documentation...",
            url_path="/api/reference/"
        )
    """
    
    def __init__(
        self,
        site_url: str,
        site_name: str,
        site_description: Optional[str] = None,
        default_author: Optional[str] = None,
        default_og_image: Optional[str] = None,
        organization_name: Optional[str] = None,
        organization_logo: Optional[str] = None,
    ) -> None:
        """Initialize SEO optimizer.
        
        Args:
            site_url: Base URL of the site
            site_name: Name of the site
            site_description: Default site description
            default_author: Default author for pages
            default_og_image: Default Open Graph image
            organization_name: Name of the organization
            organization_logo: URL to organization logo
        """
        self.site_url = site_url.rstrip('/')
        self.site_name = site_name
        self.site_description = site_description
        self.default_author = default_author
        self.default_og_image = default_og_image
        self.organization_name = organization_name or site_name
        self.organization_logo = organization_logo
        
        # Parse site URL for domain info
        self.parsed_url = urlparse(site_url)
        self.domain = self.parsed_url.netloc
        
        logger.info(f"Initialized SEOOptimizer for {site_name} at {site_url}")
    
    async def generate_page_metadata(
        self,
        title: str,
        content: str,
        url_path: str,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        published_date: Optional[datetime] = None,
        modified_date: Optional[datetime] = None,
        og_image: Optional[str] = None,
        schema_type: str = "Article",
    ) -> SEOMetadata:
        """Generate comprehensive SEO metadata for a page.
        
        Args:
            title: Page title
            content: Page content for analysis
            url_path: URL path of the page
            author: Page author
            tags: Page tags/categories
            published_date: Publication date
            modified_date: Last modification date
            og_image: Open Graph image URL
            schema_type: Schema.org type
            
        Returns:
            Complete SEO metadata
        """
        logger.debug(f"Generating SEO metadata for: {title}")
        
        # Generate description from content
        description = self._generate_description(content, title)
        
        # Build canonical URL
        canonical_url = urljoin(self.site_url, url_path)
        
        # Use defaults where not provided
        final_author = author or self.default_author
        final_og_image = og_image or self.default_og_image
        final_tags = tags or []
        
        # Create metadata
        metadata = SEOMetadata(
            title=title,
            description=description,
            canonical_url=canonical_url,
            og_image=final_og_image,
            author=final_author,
            published_date=published_date,
            modified_date=modified_date,
            tags=final_tags,
            schema_type=schema_type,
        )
        
        logger.info(f"Generated SEO metadata for: {title}")
        return metadata
    
    def _generate_description(self, content: str, title: str, max_length: int = 155) -> str:
        """Generate SEO-optimized description from content.
        
        Args:
            content: Page content
            title: Page title
            max_length: Maximum description length
            
        Returns:
            Optimized description
        """
        # Clean content - remove markdown and HTML
        import re
        clean_content = re.sub(r'[#*`\[\]()]+', '', content)
        clean_content = re.sub(r'https?://\S+', '', clean_content)  # Remove URLs
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Try to find first paragraph or sentence
        paragraphs = [p.strip() for p in clean_content.split('\n') if p.strip()]
        
        if paragraphs:
            description = paragraphs[0]
        else:
            description = f"Learn about {title} in our comprehensive documentation."
        
        # Ensure proper length
        if len(description) > max_length:
            # Find last complete word within limit
            truncated = description[:max_length]
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:  # Don't truncate too much
                description = truncated[:last_space] + "..."
            else:
                description = truncated + "..."
        
        return description
    
    async def generate_structured_data(
        self,
        metadata: SEOMetadata,
        content: str,
        breadcrumbs: Optional[List[Dict[str, str]]] = None,
    ) -> StructuredData:
        """Generate structured data for a page.
        
        Args:
            metadata: SEO metadata for the page
            content: Page content
            breadcrumbs: Navigation breadcrumbs
            
        Returns:
            Structured data object
        """
        logger.debug(f"Generating structured data for: {metadata.title}")
        
        # Build author object
        author = None
        if metadata.author:
            author = {
                "@type": "Person",
                "name": metadata.author
            }
        
        # Build publisher object
        publisher = {
            "@type": "Organization",
            "name": self.organization_name
        }
        
        if self.organization_logo:
            publisher["logo"] = {
                "@type": "ImageObject",
                "url": self.organization_logo
            }
        
        # Calculate word count
        word_count = len(content.split())
        
        # Build structured data
        structured_data = StructuredData(
            type=metadata.schema_type,
            headline=metadata.title,
            description=metadata.description,
            author=author,
            publisher=publisher,
            url=metadata.canonical_url,
            image=metadata.og_image,
            keywords=metadata.tags,
            word_count=word_count,
        )
        
        if metadata.published_date:
            structured_data.date_published = metadata.published_date.isoformat()
        
        if metadata.modified_date:
            structured_data.date_modified = metadata.modified_date.isoformat()
        
        logger.info(f"Generated structured data for: {metadata.title}")
        return structured_data
    
    def generate_social_media_config(self) -> Dict[str, Any]:
        """Generate social media optimization configuration.
        
        Returns:
            Social media configuration for MkDocs
        """
        config = {
            "social": [
                {
                    "icon": "fontawesome/brands/github", 
                    "link": "https://github.com/",
                    "name": "GitHub"
                },
                {
                    "icon": "fontawesome/brands/twitter",
                    "link": "https://twitter.com/",
                    "name": "Twitter"
                },
                {
                    "icon": "fontawesome/brands/linkedin",
                    "link": "https://linkedin.com/",
                    "name": "LinkedIn"
                },
            ]
        }
        
        return config
    
    def generate_analytics_config(
        self,
        google_analytics: Optional[str] = None,
        google_tag_manager: Optional[str] = None,
        enable_feedback: bool = True,
    ) -> Dict[str, Any]:
        """Generate analytics and feedback configuration.
        
        Args:
            google_analytics: Google Analytics tracking ID
            google_tag_manager: Google Tag Manager ID
            enable_feedback: Enable page feedback system
            
        Returns:
            Analytics configuration
        """
        config = {}
        
        if google_analytics:
            config["provider"] = "google"
            config["property"] = google_analytics
        
        if enable_feedback:
            config["feedback"] = {
                "title": "Was this page helpful?",
                "ratings": [
                    {
                        "icon": "material/emoticon-happy-outline",
                        "name": "This page was helpful",
                        "data": 1,
                        "note": "Thanks for your feedback! It helps us improve our documentation."
                    },
                    {
                        "icon": "material/emoticon-sad-outline",
                        "name": "This page could be improved", 
                        "data": 0,
                        "note": "Thanks for your feedback! Help us improve by telling us what you were looking for."
                    }
                ]
            }
        
        return config
    
    def generate_performance_config(self) -> Dict[str, Any]:
        """Generate performance optimization configuration.
        
        Returns:
            Performance optimization settings
        """
        return {
            # Cache settings
            "cache": {
                "enabled": True,
                "timeout": 3600,  # 1 hour
            },
            
            # Compression settings
            "compression": {
                "enabled": True,
                "types": ["text/html", "text/css", "text/javascript", "application/javascript"],
            },
            
            # Image optimization
            "images": {
                "lazy_loading": True,
                "responsive": True,
                "formats": ["webp", "avif"],
            },
            
            # CSS/JS optimization
            "assets": {
                "minify": True,
                "combine": True,
                "inline_critical": True,
            }
        }
    
    def generate_accessibility_config(self) -> Dict[str, Any]:
        """Generate accessibility enhancement configuration.
        
        Returns:
            Accessibility configuration
        """
        return {
            "accessibility": {
                "skip_links": True,
                "focus_indicators": True,
                "aria_labels": True,
                "contrast_compliance": "AA",  # WCAG 2.1 AA
                "keyboard_navigation": True,
                "screen_reader_support": True,
            },
            
            "content": {
                "alt_text_required": True,
                "heading_hierarchy": True,
                "link_descriptions": True,
                "language_declarations": True,
            }
        }
    
    def validate_seo_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SEO configuration and provide recommendations.
        
        Args:
            config: MkDocs configuration to validate
            
        Returns:
            Validation results with recommendations
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check required SEO fields
        if "site_description" not in config:
            results["warnings"].append("Missing site_description - important for SEO")
        
        if "site_url" not in config:
            results["errors"].append("Missing site_url - required for proper canonical URLs")
            results["valid"] = False
        
        # Check theme configuration
        theme = config.get("theme", {})
        if isinstance(theme, dict):
            # Check for social media integration
            if "social" not in config.get("extra", {}):
                results["suggestions"].append("Consider adding social media links for better engagement")
            
            # Check for analytics
            if "analytics" not in config.get("extra", {}):
                results["suggestions"].append("Consider adding analytics tracking for insights")
        
        # Check plugins for SEO
        plugins = config.get("plugins", [])
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())
        
        if "social" not in plugin_names and theme.get("name") == "material":
            results["suggestions"].append("Consider enabling social cards plugin for better sharing")
        
        if "redirects" not in plugin_names:
            results["suggestions"].append("Consider adding redirects plugin for URL management")
        
        # Check Markdown extensions
        extensions = config.get("markdown_extensions", [])
        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())
        
        if "meta" not in extension_names:
            results["warnings"].append("Missing 'meta' extension - needed for page-specific SEO metadata")
        
        logger.info(f"SEO validation completed. Valid: {results['valid']}")
        return results
    
    async def generate_sitemap_urls(
        self,
        pages: List[Dict[str, Any]],
        priority_map: Optional[Dict[str, float]] = None,
        changefreq_map: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate sitemap URL entries.
        
        Args:
            pages: List of page information
            priority_map: Custom priority mapping by URL pattern
            changefreq_map: Custom change frequency mapping
            
        Returns:
            List of sitemap URL entries
        """
        sitemap_urls = []
        
        default_priority_map = {
            "/": 1.0,
            "/index": 1.0,
            "/getting-started": 0.9,
            "/api": 0.8,
            "/tutorials": 0.7,
        }
        
        default_changefreq_map = {
            "/": "weekly",
            "/api": "monthly", 
            "/tutorials": "monthly",
        }
        
        final_priority_map = {**(priority_map or {}), **default_priority_map}
        final_changefreq_map = {**(changefreq_map or {}), **default_changefreq_map}
        
        for page in pages:
            url_path = page.get("url", "")
            full_url = urljoin(self.site_url, url_path)
            
            # Determine priority
            priority = 0.5  # default
            for pattern, p in final_priority_map.items():
                if url_path.startswith(pattern):
                    priority = p
                    break
            
            # Determine change frequency
            changefreq = "monthly"  # default
            for pattern, freq in final_changefreq_map.items():
                if url_path.startswith(pattern):
                    changefreq = freq
                    break
            
            # Get last modification date
            lastmod = page.get("modified_date")
            if isinstance(lastmod, str):
                lastmod = datetime.fromisoformat(lastmod.replace('Z', '+00:00'))
            elif not isinstance(lastmod, datetime):
                lastmod = datetime.now(timezone.utc)
            
            sitemap_urls.append({
                "loc": full_url,
                "lastmod": lastmod.isoformat(),
                "changefreq": changefreq,
                "priority": priority,
            })
        
        logger.info(f"Generated {len(sitemap_urls)} sitemap entries")
        return sitemap_urls