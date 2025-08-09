# this_file: external/int_folders/d361/tests/test_seo_optimizer_enhanced.py
"""
Enhanced comprehensive tests for SEOOptimizer.

This module provides complete unit tests for the SEOOptimizer component,
testing all SEO functionality, structured data generation, and configuration
validation that was previously incomplete.
"""

import pytest
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

from d361.mkdocs.processors.seo_optimizer import (
    SEOOptimizer,
    SEOMetadata,
    StructuredData
)
from d361.api.errors import Document360Error


@pytest.fixture
def sample_seo_optimizer():
    """Create sample SEOOptimizer for testing."""
    return SEOOptimizer(
        site_url="https://docs.example.com",
        site_name="Example Documentation",
        site_description="Comprehensive documentation for Example project",
        default_author="Documentation Team",
        default_og_image="https://docs.example.com/images/og-default.png",
        organization_name="Example Organization",
        organization_logo="https://docs.example.com/images/logo.png"
    )


@pytest.fixture
def sample_content():
    """Create sample content for testing."""
    return """# Getting Started Guide

This comprehensive guide will help you get started with our platform quickly and efficiently.

## Overview

Our platform provides powerful tools for developers to build amazing applications. 
You'll learn the fundamentals and advanced concepts needed to be productive.

### Prerequisites

- Python 3.8 or higher
- Basic understanding of web development
- A text editor or IDE

## Installation

Follow these steps to install the platform:

```bash
pip install our-platform
```

## Next Steps

After installation, check out our [API Reference](../api/) and [Tutorials](../tutorials/).

![Architecture Overview](images/architecture.png)
"""


class TestSEOMetadata:
    """Test SEOMetadata dataclass functionality."""
    
    def test_seo_metadata_creation(self):
        """Test SEOMetadata creation with various parameters."""
        published_date = datetime(2025, 1, 8, 12, 0, 0, tzinfo=timezone.utc)
        modified_date = datetime(2025, 1, 10, 15, 30, 0, tzinfo=timezone.utc)
        
        metadata = SEOMetadata(
            title="Getting Started Guide",
            description="Learn how to get started with our platform",
            canonical_url="https://docs.example.com/getting-started/",
            og_image="https://docs.example.com/images/getting-started.png",
            author="Documentation Team",
            published_date=published_date,
            modified_date=modified_date,
            tags=["guide", "tutorial", "getting-started"],
            schema_type="Article",
            lang="en"
        )
        
        assert metadata.title == "Getting Started Guide"
        assert metadata.description == "Learn how to get started with our platform"
        assert metadata.canonical_url == "https://docs.example.com/getting-started/"
        assert metadata.author == "Documentation Team"
        assert metadata.published_date == published_date
        assert metadata.modified_date == modified_date
        assert metadata.tags == ["guide", "tutorial", "getting-started"]
        assert metadata.schema_type == "Article"
    
    def test_seo_metadata_to_frontmatter(self):
        """Test conversion to MkDocs frontmatter format."""
        published_date = datetime(2025, 1, 8, 12, 0, 0, tzinfo=timezone.utc)
        modified_date = datetime(2025, 1, 10, 15, 30, 0, tzinfo=timezone.utc)
        
        metadata = SEOMetadata(
            title="API Reference",
            description="Complete API documentation",
            canonical_url="https://docs.example.com/api/",
            author="API Team",
            published_date=published_date,
            modified_date=modified_date,
            tags=["api", "reference"]
        )
        
        frontmatter = metadata.to_frontmatter()
        
        assert frontmatter["title"] == "API Reference"
        assert frontmatter["description"] == "Complete API documentation"
        assert frontmatter["canonical_url"] == "https://docs.example.com/api/"
        assert frontmatter["author"] == "API Team"
        assert frontmatter["date"] == published_date.isoformat()
        assert frontmatter["last_modified"] == modified_date.isoformat()
        assert frontmatter["tags"] == ["api", "reference"]
    
    def test_seo_metadata_defaults(self):
        """Test SEOMetadata with minimal parameters."""
        metadata = SEOMetadata(
            title="Simple Page",
            description="A simple page"
        )
        
        frontmatter = metadata.to_frontmatter()
        
        assert frontmatter["title"] == "Simple Page"
        assert frontmatter["description"] == "A simple page"
        assert "canonical_url" not in frontmatter
        assert "author" not in frontmatter
        assert "tags" not in frontmatter


class TestStructuredData:
    """Test StructuredData functionality."""
    
    def test_structured_data_creation(self):
        """Test StructuredData creation."""
        author_data = {
            "@type": "Person",
            "name": "John Doe"
        }
        
        publisher_data = {
            "@type": "Organization", 
            "name": "Example Org",
            "logo": {
                "@type": "ImageObject",
                "url": "https://example.com/logo.png"
            }
        }
        
        structured_data = StructuredData(
            type="Article",
            headline="Test Article",
            description="This is a test article",
            author=author_data,
            publisher=publisher_data,
            date_published="2025-01-08T12:00:00Z",
            date_modified="2025-01-10T15:30:00Z",
            url="https://docs.example.com/test/",
            image="https://docs.example.com/images/test.png",
            keywords=["test", "article"],
            word_count=150
        )
        
        assert structured_data.type == "Article"
        assert structured_data.headline == "Test Article"
        assert structured_data.author == author_data
        assert structured_data.publisher == publisher_data
        assert structured_data.word_count == 150
    
    def test_structured_data_to_json_ld(self):
        """Test JSON-LD generation."""
        structured_data = StructuredData(
            type="Article",
            headline="Sample Article",
            description="This is a sample article for testing",
            url="https://docs.example.com/sample/",
            keywords=["sample", "test"],
            word_count=100
        )
        
        json_ld = structured_data.to_json_ld()
        parsed_data = json.loads(json_ld)
        
        assert parsed_data["@context"] == "https://schema.org"
        assert parsed_data["@type"] == "Article"
        assert parsed_data["headline"] == "Sample Article"
        assert parsed_data["description"] == "This is a sample article for testing"
        assert parsed_data["url"] == "https://docs.example.com/sample/"
        assert parsed_data["keywords"] == ["sample", "test"]
        assert parsed_data["wordCount"] == 100
    
    def test_structured_data_minimal(self):
        """Test structured data with minimal information."""
        structured_data = StructuredData(
            type="WebPage",
            headline="Simple Page"
        )
        
        json_ld = structured_data.to_json_ld()
        parsed_data = json.loads(json_ld)
        
        assert parsed_data["@context"] == "https://schema.org"
        assert parsed_data["@type"] == "WebPage"
        assert parsed_data["headline"] == "Simple Page"
        assert "description" not in parsed_data
        assert "author" not in parsed_data


class TestSEOOptimizerInitialization:
    """Test SEOOptimizer initialization and configuration."""
    
    def test_init_minimal(self):
        """Test initialization with minimal parameters."""
        optimizer = SEOOptimizer(
            site_url="https://docs.test.com",
            site_name="Test Docs"
        )
        
        assert optimizer.site_url == "https://docs.test.com"
        assert optimizer.site_name == "Test Docs"
        assert optimizer.organization_name == "Test Docs"  # Defaults to site_name
        assert optimizer.domain == "docs.test.com"
        assert optimizer.site_description is None
        assert optimizer.default_author is None
    
    def test_init_complete(self, sample_seo_optimizer):
        """Test initialization with all parameters."""
        assert sample_seo_optimizer.site_url == "https://docs.example.com"
        assert sample_seo_optimizer.site_name == "Example Documentation"
        assert sample_seo_optimizer.site_description == "Comprehensive documentation for Example project"
        assert sample_seo_optimizer.default_author == "Documentation Team"
        assert sample_seo_optimizer.default_og_image == "https://docs.example.com/images/og-default.png"
        assert sample_seo_optimizer.organization_name == "Example Organization"
        assert sample_seo_optimizer.organization_logo == "https://docs.example.com/images/logo.png"
        assert sample_seo_optimizer.domain == "docs.example.com"
    
    def test_url_parsing(self):
        """Test URL parsing functionality."""
        optimizer = SEOOptimizer(
            site_url="https://subdomain.example.com:8080/path/",
            site_name="Test Site"
        )
        
        assert optimizer.site_url == "https://subdomain.example.com:8080/path"  # Stripped trailing slash
        assert optimizer.domain == "subdomain.example.com:8080"
        assert optimizer.parsed_url.scheme == "https"
        assert optimizer.parsed_url.path == "/path"


class TestMetadataGeneration:
    """Test SEO metadata generation."""
    
    @pytest.mark.asyncio
    async def test_generate_page_metadata_basic(self, sample_seo_optimizer, sample_content):
        """Test basic page metadata generation."""
        metadata = await sample_seo_optimizer.generate_page_metadata(
            title="Getting Started Guide",
            content=sample_content,
            url_path="/getting-started/"
        )
        
        assert metadata.title == "Getting Started Guide"
        assert len(metadata.description) > 0
        assert len(metadata.description) <= 158  # SEO optimal length + "..."
        assert metadata.canonical_url == "https://docs.example.com/getting-started/"
        assert metadata.author == "Documentation Team"  # From default
        assert metadata.og_image == "https://docs.example.com/images/og-default.png"  # From default
    
    @pytest.mark.asyncio
    async def test_generate_page_metadata_with_overrides(self, sample_seo_optimizer, sample_content):
        """Test metadata generation with parameter overrides."""
        published_date = datetime(2025, 1, 8, 12, 0, 0, tzinfo=timezone.utc)
        modified_date = datetime(2025, 1, 10, 15, 30, 0, tzinfo=timezone.utc)
        
        metadata = await sample_seo_optimizer.generate_page_metadata(
            title="Custom Guide",
            content=sample_content,
            url_path="/custom/",
            author="Custom Author",
            tags=["custom", "guide"],
            published_date=published_date,
            modified_date=modified_date,
            og_image="https://docs.example.com/images/custom.png",
            schema_type="Tutorial"
        )
        
        assert metadata.title == "Custom Guide"
        assert metadata.author == "Custom Author"  # Override default
        assert metadata.tags == ["custom", "guide"]
        assert metadata.published_date == published_date
        assert metadata.modified_date == modified_date
        assert metadata.og_image == "https://docs.example.com/images/custom.png"  # Override default
        assert metadata.schema_type == "Tutorial"
    
    @pytest.mark.asyncio
    async def test_generate_page_metadata_empty_content(self, sample_seo_optimizer):
        """Test metadata generation with empty content."""
        metadata = await sample_seo_optimizer.generate_page_metadata(
            title="Empty Page",
            content="",
            url_path="/empty/"
        )
        
        assert metadata.title == "Empty Page"
        assert metadata.description == "Learn about Empty Page in our comprehensive documentation."
        assert metadata.canonical_url == "https://docs.example.com/empty/"
    
    def test_generate_description_from_content(self, sample_seo_optimizer, sample_content):
        """Test description generation from content."""
        description = sample_seo_optimizer._generate_description(sample_content, "Test Title")
        
        assert len(description) <= 155
        assert "comprehensive guide" in description.lower()
        assert "quickly and efficiently" in description.lower()
        # Should not contain markdown symbols
        assert "#" not in description
        assert "[" not in description
    
    def test_generate_description_truncation(self, sample_seo_optimizer):
        """Test description truncation for long content."""
        long_content = "This is a very long description that exceeds the maximum length limit for SEO descriptions and should be properly truncated at the appropriate word boundary to maintain readability and SEO effectiveness."
        
        description = sample_seo_optimizer._generate_description(long_content, "Long Content")
        
        assert len(description) <= 158  # 155 + "..."
        assert description.endswith("...")
        assert " " not in description[-4:]  # Should not truncate mid-word
    
    def test_generate_description_markdown_cleaning(self, sample_seo_optimizer):
        """Test markdown and HTML cleaning in description generation."""
        markdown_content = """
        # This is a heading
        
        This is **bold** text with *italic* and `code` elements. 
        [This is a link](https://example.com) and here's an image ![alt](image.png).
        
        Visit https://example.com for more info.
        """
        
        description = sample_seo_optimizer._generate_description(markdown_content, "Markdown Test")
        
        # Should remove markdown formatting
        assert "#" not in description
        assert "**" not in description
        assert "*" not in description
        assert "`" not in description
        assert "[" not in description
        assert "]" not in description
        assert "![" not in description
        assert "https://" not in description


class TestStructuredDataGeneration:
    """Test structured data generation."""
    
    @pytest.mark.asyncio
    async def test_generate_structured_data_complete(self, sample_seo_optimizer, sample_content):
        """Test complete structured data generation."""
        # First generate metadata
        metadata = await sample_seo_optimizer.generate_page_metadata(
            title="API Guide",
            content=sample_content,
            url_path="/api-guide/",
            author="API Team",
            tags=["api", "guide"]
        )
        
        # Then generate structured data
        structured_data = await sample_seo_optimizer.generate_structured_data(
            metadata=metadata,
            content=sample_content
        )
        
        assert structured_data.type == "Article"  # Default schema type
        assert structured_data.headline == "API Guide"
        assert structured_data.description == metadata.description
        assert structured_data.url == "https://docs.example.com/api-guide/"
        assert structured_data.keywords == ["api", "guide"]
        assert structured_data.word_count > 0
        
        # Check author structure
        assert structured_data.author is not None
        assert structured_data.author["@type"] == "Person"
        assert structured_data.author["name"] == "API Team"
        
        # Check publisher structure
        assert structured_data.publisher is not None
        assert structured_data.publisher["@type"] == "Organization"
        assert structured_data.publisher["name"] == "Example Organization"
        assert "logo" in structured_data.publisher
    
    @pytest.mark.asyncio
    async def test_generate_structured_data_minimal(self, sample_seo_optimizer):
        """Test structured data generation with minimal metadata."""
        metadata = SEOMetadata(
            title="Simple Page",
            description="A simple page"
        )
        
        structured_data = await sample_seo_optimizer.generate_structured_data(
            metadata=metadata,
            content="Simple content"
        )
        
        assert structured_data.headline == "Simple Page"
        assert structured_data.description == "A simple page"
        assert structured_data.author is None  # No author in metadata
        assert structured_data.publisher is not None  # Always included
        assert structured_data.word_count == 2  # "Simple content"
    
    @pytest.mark.asyncio
    async def test_generate_structured_data_with_dates(self, sample_seo_optimizer):
        """Test structured data generation with publication dates."""
        published_date = datetime(2025, 1, 8, 12, 0, 0, tzinfo=timezone.utc)
        modified_date = datetime(2025, 1, 10, 15, 30, 0, tzinfo=timezone.utc)
        
        metadata = SEOMetadata(
            title="Dated Article",
            description="Article with dates",
            published_date=published_date,
            modified_date=modified_date
        )
        
        structured_data = await sample_seo_optimizer.generate_structured_data(
            metadata=metadata,
            content="Content with dates"
        )
        
        assert structured_data.date_published == published_date.isoformat()
        assert structured_data.date_modified == modified_date.isoformat()
    
    @pytest.mark.asyncio
    async def test_structured_data_json_ld_output(self, sample_seo_optimizer):
        """Test JSON-LD output from structured data."""
        metadata = await sample_seo_optimizer.generate_page_metadata(
            title="Test Article",
            content="Test content for structured data",
            url_path="/test/",
            author="Test Author",
            tags=["test"]
        )
        
        structured_data = await sample_seo_optimizer.generate_structured_data(
            metadata=metadata,
            content="Test content for structured data"
        )
        
        json_ld = structured_data.to_json_ld()
        parsed_data = json.loads(json_ld)
        
        # Validate JSON-LD structure
        assert parsed_data["@context"] == "https://schema.org"
        assert parsed_data["@type"] == "Article"
        assert parsed_data["headline"] == "Test Article"
        assert parsed_data["url"] == "https://docs.example.com/test/"
        assert parsed_data["keywords"] == ["test"]
        
        # Validate author structure
        assert parsed_data["author"]["@type"] == "Person"
        assert parsed_data["author"]["name"] == "Test Author"
        
        # Validate publisher structure
        assert parsed_data["publisher"]["@type"] == "Organization"
        assert parsed_data["publisher"]["name"] == "Example Organization"


class TestConfigurationGeneration:
    """Test configuration generation methods."""
    
    def test_generate_social_media_config(self, sample_seo_optimizer):
        """Test social media configuration generation."""
        config = sample_seo_optimizer.generate_social_media_config()
        
        assert "social" in config
        assert len(config["social"]) >= 3  # GitHub, Twitter, LinkedIn
        
        # Check structure of social links
        for social_link in config["social"]:
            assert "icon" in social_link
            assert "link" in social_link
            assert "name" in social_link
    
    def test_generate_analytics_config_basic(self, sample_seo_optimizer):
        """Test basic analytics configuration generation."""
        config = sample_seo_optimizer.generate_analytics_config()
        
        # Should have feedback enabled by default
        assert "feedback" in config
        assert config["feedback"]["title"] == "Was this page helpful?"
        assert len(config["feedback"]["ratings"]) == 2  # Helpful and Not Helpful
    
    def test_generate_analytics_config_with_google(self, sample_seo_optimizer):
        """Test analytics configuration with Google Analytics."""
        config = sample_seo_optimizer.generate_analytics_config(
            google_analytics="G-XXXXXXXXXX",
            google_tag_manager="GTM-XXXXXXX",
            enable_feedback=True
        )
        
        assert config["provider"] == "google"
        assert config["property"] == "G-XXXXXXXXXX"
        assert "feedback" in config
    
    def test_generate_analytics_config_no_feedback(self, sample_seo_optimizer):
        """Test analytics configuration without feedback."""
        config = sample_seo_optimizer.generate_analytics_config(
            google_analytics="G-XXXXXXXXXX",
            enable_feedback=False
        )
        
        assert config["provider"] == "google"
        assert config["property"] == "G-XXXXXXXXXX"
        assert "feedback" not in config
    
    def test_generate_performance_config(self, sample_seo_optimizer):
        """Test performance configuration generation."""
        config = sample_seo_optimizer.generate_performance_config()
        
        # Check all performance sections exist
        assert "cache" in config
        assert "compression" in config
        assert "images" in config
        assert "assets" in config
        
        # Validate cache settings
        assert config["cache"]["enabled"] is True
        assert config["cache"]["timeout"] == 3600
        
        # Validate compression settings
        assert config["compression"]["enabled"] is True
        assert "text/html" in config["compression"]["types"]
        
        # Validate image settings
        assert config["images"]["lazy_loading"] is True
        assert config["images"]["responsive"] is True
        assert "webp" in config["images"]["formats"]
        
        # Validate asset settings
        assert config["assets"]["minify"] is True
        assert config["assets"]["combine"] is True
    
    def test_generate_accessibility_config(self, sample_seo_optimizer):
        """Test accessibility configuration generation."""
        config = sample_seo_optimizer.generate_accessibility_config()
        
        assert "accessibility" in config
        assert "content" in config
        
        # Check accessibility settings
        accessibility = config["accessibility"]
        assert accessibility["skip_links"] is True
        assert accessibility["focus_indicators"] is True
        assert accessibility["contrast_compliance"] == "AA"
        assert accessibility["keyboard_navigation"] is True
        
        # Check content settings
        content = config["content"]
        assert content["alt_text_required"] is True
        assert content["heading_hierarchy"] is True
        assert content["link_descriptions"] is True
        assert content["language_declarations"] is True


class TestSEOValidation:
    """Test SEO configuration validation."""
    
    def test_validate_seo_config_valid(self, sample_seo_optimizer):
        """Test validation of valid SEO configuration."""
        config = {
            "site_name": "Test Docs",
            "site_url": "https://docs.test.com",
            "site_description": "Test documentation",
            "theme": {
                "name": "material"
            },
            "plugins": ["search", "social", "redirects"],
            "markdown_extensions": ["meta", "toc", "admonition"],
            "extra": {
                "social": [],
                "analytics": {"provider": "google"}
            }
        }
        
        results = sample_seo_optimizer.validate_seo_config(config)
        
        assert results["valid"] is True
        assert len(results["errors"]) == 0
    
    def test_validate_seo_config_missing_required(self, sample_seo_optimizer):
        """Test validation with missing required fields."""
        config = {
            "site_name": "Test Docs",
            # Missing site_url
            "theme": {"name": "material"}
        }
        
        results = sample_seo_optimizer.validate_seo_config(config)
        
        assert results["valid"] is False
        assert len(results["errors"]) > 0
        assert any("site_url" in error for error in results["errors"])
    
    def test_validate_seo_config_warnings(self, sample_seo_optimizer):
        """Test validation warnings for optional but recommended fields."""
        config = {
            "site_name": "Test Docs",
            "site_url": "https://docs.test.com",
            # Missing site_description
            "theme": {"name": "material"},
            "markdown_extensions": ["toc"]  # Missing meta extension
        }
        
        results = sample_seo_optimizer.validate_seo_config(config)
        
        assert results["valid"] is True
        assert len(results["warnings"]) > 0
        warnings_text = " ".join(results["warnings"])
        assert "site_description" in warnings_text
        assert "meta" in warnings_text
    
    def test_validate_seo_config_suggestions(self, sample_seo_optimizer):
        """Test validation suggestions for optimization."""
        config = {
            "site_name": "Test Docs",
            "site_url": "https://docs.test.com",
            "site_description": "Test docs",
            "theme": {"name": "material"},
            "plugins": ["search"],  # Missing social and redirects
            "markdown_extensions": ["meta"],
            "extra": {}  # Missing social and analytics
        }
        
        results = sample_seo_optimizer.validate_seo_config(config)
        
        assert results["valid"] is True
        assert len(results["suggestions"]) > 0
        suggestions_text = " ".join(results["suggestions"])
        assert "social" in suggestions_text or "analytics" in suggestions_text


class TestSitemapGeneration:
    """Test sitemap generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_sitemap_urls_basic(self, sample_seo_optimizer):
        """Test basic sitemap URL generation."""
        pages = [
            {"url": "/", "title": "Home", "modified_date": "2025-01-08T12:00:00Z"},
            {"url": "/getting-started/", "title": "Getting Started", "modified_date": "2025-01-10T15:30:00Z"},
            {"url": "/api/", "title": "API Reference", "modified_date": "2025-01-05T10:00:00Z"},
        ]
        
        sitemap_urls = await sample_seo_optimizer.generate_sitemap_urls(pages)
        
        assert len(sitemap_urls) == 3
        
        # Check home page (should have highest priority)
        home_url = next(url for url in sitemap_urls if url["loc"].endswith("/"))
        assert home_url["priority"] == 1.0
        assert home_url["changefreq"] == "weekly"
        
        # Check API page
        api_url = next(url for url in sitemap_urls if "/api" in url["loc"])
        assert api_url["priority"] == 0.8
        assert api_url["changefreq"] == "monthly"
    
    @pytest.mark.asyncio
    async def test_generate_sitemap_urls_with_custom_maps(self, sample_seo_optimizer):
        """Test sitemap generation with custom priority and frequency maps."""
        pages = [
            {"url": "/custom/", "title": "Custom Page", "modified_date": "2025-01-08T12:00:00Z"},
            {"url": "/other/", "title": "Other Page", "modified_date": "2025-01-08T12:00:00Z"}
        ]
        
        priority_map = {"/custom/": 0.9}
        changefreq_map = {"/custom/": "daily"}
        
        sitemap_urls = await sample_seo_optimizer.generate_sitemap_urls(
            pages=pages,
            priority_map=priority_map,
            changefreq_map=changefreq_map
        )
        
        custom_url = next(url for url in sitemap_urls if "/custom" in url["loc"])
        assert custom_url["priority"] == 0.9
        assert custom_url["changefreq"] == "daily"
        
        other_url = next(url for url in sitemap_urls if "/other" in url["loc"])
        assert other_url["priority"] == 0.5  # Default
        assert other_url["changefreq"] == "monthly"  # Default
    
    @pytest.mark.asyncio
    async def test_generate_sitemap_urls_date_handling(self, sample_seo_optimizer):
        """Test different date formats in sitemap generation."""
        now = datetime.now(timezone.utc)
        
        pages = [
            {"url": "/with-string-date/", "modified_date": "2025-01-08T12:00:00Z"},
            {"url": "/with-datetime/", "modified_date": now},
            {"url": "/without-date/"},  # Should use current time
        ]
        
        sitemap_urls = await sample_seo_optimizer.generate_sitemap_urls(pages)
        
        # All URLs should have lastmod field
        for url in sitemap_urls:
            assert "lastmod" in url
            assert url["lastmod"].endswith("Z") or "+" in url["lastmod"]  # Valid ISO format


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""
    
    @pytest.mark.asyncio
    async def test_complete_seo_workflow(self, sample_seo_optimizer, sample_content):
        """Test complete SEO optimization workflow."""
        # Generate metadata
        metadata = await sample_seo_optimizer.generate_page_metadata(
            title="Complete Guide",
            content=sample_content,
            url_path="/complete-guide/",
            author="Guide Team",
            tags=["guide", "complete"]
        )
        
        # Generate structured data
        structured_data = await sample_seo_optimizer.generate_structured_data(
            metadata=metadata,
            content=sample_content
        )
        
        # Generate configurations
        social_config = sample_seo_optimizer.generate_social_media_config()
        analytics_config = sample_seo_optimizer.generate_analytics_config(
            google_analytics="G-TEST123",
            enable_feedback=True
        )
        performance_config = sample_seo_optimizer.generate_performance_config()
        accessibility_config = sample_seo_optimizer.generate_accessibility_config()
        
        # Validate everything completed successfully
        assert metadata.title == "Complete Guide"
        assert len(metadata.description) > 0
        assert structured_data.headline == "Complete Guide"
        assert "social" in social_config
        assert analytics_config["provider"] == "google"
        assert performance_config["cache"]["enabled"] is True
        assert accessibility_config["accessibility"]["skip_links"] is True
    
    @pytest.mark.asyncio
    async def test_multilingual_support(self):
        """Test SEO optimization for different languages."""
        optimizer = SEOOptimizer(
            site_url="https://docs.example.com/es",
            site_name="Documentación de Ejemplo"
        )
        
        metadata = await optimizer.generate_page_metadata(
            title="Guía de Inicio",
            content="Esta es una guía completa para comenzar con nuestra plataforma.",
            url_path="/es/guia-inicio/"
        )
        
        assert metadata.title == "Guía de Inicio"
        assert "completa" in metadata.description
        assert metadata.canonical_url == "https://docs.example.com/es/guia-inicio/"
    
    def test_edge_case_empty_inputs(self, sample_seo_optimizer):
        """Test handling of edge cases with empty inputs."""
        # Test empty description generation
        description = sample_seo_optimizer._generate_description("", "Empty Content")
        assert description == "Learn about Empty Content in our comprehensive documentation."
        
        # Test validation with empty config
        results = sample_seo_optimizer.validate_seo_config({})
        assert not results["valid"]
        assert len(results["errors"]) > 0
    
    def test_url_handling_edge_cases(self):
        """Test URL handling with various edge cases."""
        # Test with trailing slash
        optimizer1 = SEOOptimizer(
            site_url="https://docs.example.com/",
            site_name="Test"
        )
        assert optimizer1.site_url == "https://docs.example.com"
        
        # Test with path
        optimizer2 = SEOOptimizer(
            site_url="https://example.com/docs/",
            site_name="Test"
        )
        assert optimizer2.site_url == "https://example.com/docs"
        
        # Test with port
        optimizer3 = SEOOptimizer(
            site_url="https://localhost:8000/",
            site_name="Test"
        )
        assert optimizer3.domain == "localhost:8000"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])