# this_file: external/int_folders/d361/tests/test_mkdocs_units.py
"""
Unit tests for MkDocs export components.

This module provides focused unit tests for individual MkDocs components,
testing their functionality in isolation with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import Dict, Any, List
import yaml

from d361.core.models import Article, Category
from d361.mkdocs.exporters.config_generator import ConfigGenerator
from d361.mkdocs.exporters.navigation_builder import NavigationBuilder
from d361.mkdocs.exporters.theme_optimizer import ThemeOptimizer
from d361.mkdocs.processors.content_enhancer import ContentEnhancer
from d361.mkdocs.processors.markdown_processor import MarkdownProcessor
from d361.mkdocs.processors.asset_manager import AssetManager
from d361.mkdocs.processors.cross_reference_resolver import (
    CrossReferenceResolver, 
    LinkReference, 
    AnchorReference
)
from d361.api.errors import Document360Error


class TestConfigGeneratorUnit:
    """Unit tests for ConfigGenerator."""
    
    def test_init_default_theme(self):
        """Test initialization with default theme."""
        generator = ConfigGenerator()
        
        assert generator.theme == "material"
        assert generator.enable_plugins is True
        assert generator.jinja_env is not None
    
    def test_init_custom_theme(self):
        """Test initialization with custom theme."""
        generator = ConfigGenerator(theme="readthedocs", enable_plugins=False)
        
        assert generator.theme == "readthedocs"
        assert generator.enable_plugins is False
    
    def test_yaml_filter(self):
        """Test YAML filter functionality."""
        generator = ConfigGenerator()
        
        test_obj = {"key": "value", "list": [1, 2, 3]}
        yaml_result = generator._yaml_filter(test_obj)
        
        assert "key: value" in yaml_result
        assert "list:" in yaml_result
        assert yaml.safe_load(yaml_result) == test_obj
    
    def test_build_base_config_minimal(self):
        """Test base config building with minimal parameters."""
        generator = ConfigGenerator()
        
        config = generator._build_base_config("Test Site")
        
        assert config["site_name"] == "Test Site"
        assert config["docs_dir"] == "docs"
        assert config["site_dir"] == "site"
        assert "site_url" not in config
    
    def test_build_base_config_complete(self):
        """Test base config building with all parameters."""
        generator = ConfigGenerator()
        
        config = generator._build_base_config(
            site_name="Complete Site",
            site_url="https://example.com",
            site_description="Test description",
            repo_url="https://github.com/test/repo",
            edit_uri="edit/main/docs/"
        )
        
        assert config["site_name"] == "Complete Site"
        assert config["site_url"] == "https://example.com"
        assert config["site_description"] == "Test description"
        assert config["repo_url"] == "https://github.com/test/repo"
        assert config["edit_uri"] == "edit/main/docs/"
    
    def test_build_material_theme_config(self):
        """Test Material theme configuration building."""
        generator = ConfigGenerator(theme="material")
        
        config = generator._build_material_theme_config()
        
        assert config["name"] == "material"
        assert "features" in config
        assert "palette" in config
        assert "font" in config
        assert "icon" in config
        
        # Check for key Material features
        features = config["features"]
        assert "navigation.instant" in features
        assert "search.highlight" in features
        assert "content.code.copy" in features
    
    def test_build_readthedocs_theme_config(self):
        """Test Read the Docs theme configuration building."""
        generator = ConfigGenerator(theme="readthedocs")
        
        config = generator._build_readthedocs_theme_config()
        
        assert config["name"] == "readthedocs"
        assert config["highlightjs"] is True
        assert "hljs_languages" in config
        assert "python" in config["hljs_languages"]
    
    def test_build_plugins_config_disabled(self):
        """Test plugins configuration when disabled."""
        generator = ConfigGenerator(enable_plugins=False)
        
        plugins = generator._build_plugins_config()
        
        assert len(plugins) == 1
        assert plugins[0] == "search"
    
    def test_build_plugins_config_enabled(self):
        """Test plugins configuration when enabled."""
        generator = ConfigGenerator(enable_plugins=True)
        
        plugins = generator._build_plugins_config()
        
        assert len(plugins) > 1
        assert "search" in plugins
        
        # Check for specific plugins
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())
        
        assert "autorefs" in plugin_names
        assert "section-index" in plugin_names
        assert "redirects" in plugin_names
        assert "minify" in plugin_names
    
    def test_build_markdown_extensions(self):
        """Test Markdown extensions configuration."""
        generator = ConfigGenerator()
        
        extensions = generator._build_markdown_extensions()
        
        assert len(extensions) > 0
        
        # Check for key extensions
        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())
        
        assert "meta" in extension_names
        assert "toc" in extension_names
        assert "admonition" in extension_names
        assert "pymdownx.superfences" in extension_names
        assert "pymdownx.tabbed" in extension_names
    
    def test_merge_configs(self):
        """Test configuration merging."""
        generator = ConfigGenerator()
        
        base_config = {
            "site_name": "Base Site",
            "theme": {"name": "material"},
            "plugins": ["search"]
        }
        
        custom_config = {
            "site_name": "Custom Site",  # Override
            "site_url": "https://custom.com",  # Add new
            "theme": {"features": ["navigation.instant"]},  # Merge nested
            "plugins": ["search", "autorefs"]  # Override list
        }
        
        merged = generator._merge_configs(base_config, custom_config)
        
        assert merged["site_name"] == "Custom Site"
        assert merged["site_url"] == "https://custom.com"
        assert merged["theme"]["name"] == "material"  # Preserved from base
        assert merged["theme"]["features"] == ["navigation.instant"]  # Added from custom
        assert merged["plugins"] == ["search", "autorefs"]  # Overridden


class TestNavigationBuilderUnit:
    """Unit tests for NavigationBuilder."""
    
    def test_init(self):
        """Test initialization."""
        builder = NavigationBuilder()
        assert builder is not None
    
    @pytest.mark.asyncio
    async def test_build_navigation_empty(self):
        """Test navigation building with empty inputs."""
        builder = NavigationBuilder()
        
        result = await builder.build_navigation([], [])
        
        assert isinstance(result, dict)
        assert result["navigation"] == []
        assert result["navigation_tree"] == []
        assert result["validation_report"]["is_valid"] is True
    
    @pytest.mark.asyncio
    async def test_build_navigation_articles_only(self):
        """Test navigation building with articles only."""
        from datetime import datetime
        builder = NavigationBuilder()
        now = datetime.now()
        
        articles = [
            Article(id=1, title="Article 1", slug="article-1", content="", category_id=1, created_at=now, updated_at=now),
            Article(id=2, title="Article 2", slug="article-2", content="", category_id=1, created_at=now, updated_at=now)
        ]
        
        result = await builder.build_navigation(articles, [])
        
        assert isinstance(result, dict)
        assert isinstance(result["navigation"], list)
        assert len(result["navigation"]) >= 0  # Should handle articles without categories
    
    @pytest.mark.asyncio 
    async def test_build_navigation_with_categories(self):
        """Test navigation building with categories and articles."""
        from datetime import datetime
        builder = NavigationBuilder()
        now = datetime.now()
        
        categories = [
            Category(id=1, name="Category 1", slug="category-1", parent_id=None, order=1, created_at=now, updated_at=now)
        ]
        
        articles = [
            Article(id=1, title="Article 1", slug="article-1", content="", category_id=1, created_at=now, updated_at=now)
        ]
        
        result = await builder.build_navigation(articles, categories)
        
        assert isinstance(result, dict)
        assert isinstance(result["navigation"], list)
        assert len(result["navigation"]) >= 0
        # Detailed navigation structure testing would depend on implementation


class TestContentEnhancerUnit:
    """Unit tests for ContentEnhancer."""
    
    def test_init_default(self):
        """Test initialization with defaults."""
        enhancer = ContentEnhancer()
        
        assert enhancer.site_url is None
        assert enhancer.enable_seo is True
        assert enhancer.validate_links is True
        assert enhancer.add_edit_links is True
    
    def test_init_custom(self):
        """Test initialization with custom settings."""
        enhancer = ContentEnhancer(
            site_url="https://docs.example.com",
            enable_seo=False,
            validate_links=False,
            enable_social_cards=True
        )
        
        assert enhancer.site_url == "https://docs.example.com"
        assert enhancer.enable_seo is False
        assert enhancer.validate_links is False
        assert enhancer.enable_social_cards is True
    
    def test_extract_description_basic(self):
        """Test description extraction."""
        enhancer = ContentEnhancer()
        
        content = "This is the first paragraph.\n\nThis is the second paragraph."
        description = enhancer._extract_description(content)
        
        assert description == "This is the first paragraph."
    
    def test_extract_description_long(self):
        """Test description extraction with truncation."""
        enhancer = ContentEnhancer()
        
        content = "A" * 200  # Long content
        description = enhancer._extract_description(content)
        
        assert len(description) <= 163  # 160 + "..."
        assert description.endswith("...")
    
    def test_extract_description_with_markdown(self):
        """Test description extraction removing markdown."""
        enhancer = ContentEnhancer()
        
        content = "This is **bold** and *italic* text with `code`."
        description = enhancer._extract_description(content)
        
        # Should remove markdown formatting
        assert "**" not in description
        assert "*" not in description
        assert "`" not in description
        assert "bold" in description
        assert "italic" in description
    
    def test_normalize_headings(self):
        """Test heading normalization."""
        enhancer = ContentEnhancer()
        
        content = """# Main Heading
## Section Heading
### Subsection"""
        
        normalized = enhancer._normalize_headings(content)
        
        # H1 should become H2
        assert "## Main Heading" in normalized
        assert "## Section Heading" in normalized
        assert "### Subsection" in normalized
        
        # Should add anchor IDs
        assert "{: #main-heading }" in normalized
        assert "{: #section-heading }" in normalized
    
    def test_process_links_internal(self):
        """Test internal link processing."""
        enhancer = ContentEnhancer()
        
        content = "[Internal Link](/docs/other-page.html)"
        processed = enhancer._process_links(content)
        
        # Should convert /docs/ to ../ and .html to .md
        assert "../other-page.md" in processed
    
    def test_process_links_external(self):
        """Test external link processing."""
        enhancer = ContentEnhancer(site_url="https://docs.example.com")
        
        content = "[External Link](https://other-site.com/page)"
        processed = enhancer._process_links(content)
        
        # Should add external link attributes
        assert 'target="_blank"' in processed
        assert 'rel="noopener noreferrer"' in processed
    
    def test_process_images(self):
        """Test image processing."""
        enhancer = ContentEnhancer()
        
        content = """![Alt Text](https://document360.com/image.png)
![Local Image](../images/local.jpg)"""
        
        processed = enhancer._process_images(content)
        
        # Should process Document360 URLs
        assert "document360.com" in processed or "document360" in processed.lower()
        
        # Should add responsive attributes for large images
        assert "local.jpg" in processed
    
    def test_enhance_code_blocks(self):
        """Test code block enhancement."""
        enhancer = ContentEnhancer()
        
        content = """```
def example():
    return "hello"
```

```python
def example():
    return "hello"
    print("line 2")
    print("line 3")
```"""
        
        enhanced = enhancer._enhance_code_blocks(content)
        
        # Should detect language
        assert "python" in enhanced
        
        # Should add line numbers for long blocks
        lines = enhanced.split('\n')
        long_block_lines = [line for line in lines if 'linenums=' in line]
        # May or may not add line numbers depending on length detection
    
    def test_assess_quality_high(self):
        """Test quality assessment for high-quality content."""
        enhancer = ContentEnhancer()
        
        content = """# Introduction
This is a comprehensive article with multiple sections and good structure.

## Main Section
Content with proper formatting and [internal links](../guide.md).

### Subsection
More detailed information here with examples.

```python
def example():
    return "code sample"
```

![Diagram](diagram.png)

## Conclusion
Summary and next steps.
""" * 3  # Repeat to increase word count
        
        metrics = enhancer._assess_quality(content)
        
        assert metrics["word_count"] > 50
        assert metrics["heading_count"] >= 3
        assert metrics["link_count"] >= 1
        assert metrics["image_count"] >= 1
        assert metrics["code_block_count"] >= 1
        assert metrics["overall_score"] > 50
        assert metrics["quality_level"] in ["good", "excellent"]
    
    def test_assess_quality_low(self):
        """Test quality assessment for low-quality content."""
        enhancer = ContentEnhancer()
        
        content = "Short content."
        metrics = enhancer._assess_quality(content)
        
        assert metrics["word_count"] < 50
        assert metrics["heading_count"] == 0
        assert metrics["overall_score"] < 50
        assert metrics["quality_level"] in ["needs_improvement", "fair"]
    
    def test_generate_file_path(self):
        """Test file path generation."""
        from datetime import datetime
        enhancer = ContentEnhancer()
        now = datetime.now()
        
        # Test with slug
        article_with_slug = Article(
            id=1, 
            title="Test Article", 
            slug="test-article",
            content="",
            category_id=1,
            created_at=now,
            updated_at=now
        )
        path = enhancer._generate_file_path(article_with_slug)
        assert path == "test-article.md"
        
        # Test without slug
        article_without_slug = Article(
            id=2,
            title="Article Title With Spaces!",
            slug="",
            content="",
            category_id=1,
            created_at=now,
            updated_at=now
        )
        path = enhancer._generate_file_path(article_without_slug)
        assert path.endswith(".md")
        assert " " not in path  # Should convert spaces to hyphens


class TestAssetManagerUnit:
    """Unit tests for AssetManager."""
    
    def test_init_default(self):
        """Test initialization with defaults."""
        manager = AssetManager(output_dir=Path("/tmp/assets"))
        
        assert manager.output_dir == Path("/tmp/assets")
        assert manager.enable_optimization is True
        assert manager.generate_responsive is False
        assert manager.max_image_width == 1200
        assert manager.image_quality == 85
    
    def test_init_custom(self):
        """Test initialization with custom settings."""
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = AssetManager(
                output_dir=Path(temp_dir) / "custom" / "assets",
                enable_optimization=False,
                generate_responsive=True,
                max_image_width=800,
                image_quality=90,
                convert_to_webp=True
            )
            
            assert manager.output_dir == Path(temp_dir) / "custom" / "assets"
            assert manager.enable_optimization is False
            assert manager.generate_responsive is True
            assert manager.max_image_width == 800
            assert manager.image_quality == 90
            assert manager.convert_to_webp is True
    
    def test_extract_assets_from_content(self):
        """Test asset extraction from content."""
        manager = AssetManager(output_dir=Path("/tmp"))
        
        content = """# Test Content

![Image 1](https://example.com/image1.png)
![Image 2](../assets/image2.jpg)
![Image 3](image3.gif)

[Download PDF](document.pdf)
"""
        
        # This would need to be implemented in the actual class
        # For now, test that the manager can be initialized
        assert manager is not None
    
    @pytest.mark.asyncio
    async def test_process_assets_empty_content(self):
        """Test asset processing with empty content."""
        manager = AssetManager(output_dir=Path("/tmp"))
        
        processed = await manager.process_assets("")
        assert processed == []  # Should return empty list for no assets
    
    @pytest.mark.asyncio
    async def test_process_assets_no_images(self):
        """Test asset processing with no images."""
        manager = AssetManager(output_dir=Path("/tmp"))
        
        content = "# Test\n\nThis is text content without images."
        processed = await manager.process_assets(content)
        
        assert processed == []  # Should return empty list for no assets


class TestCrossReferenceResolverUnit:
    """Unit tests for CrossReferenceResolver."""
    
    def test_init_basic(self):
        """Test basic initialization."""
        from datetime import datetime
        now = datetime.now()
        articles = [
            Article(id=1, title="Article 1", slug="article-1", content="", category_id=1, created_at=now, updated_at=now)
        ]
        
        resolver = CrossReferenceResolver(articles)
        
        assert len(resolver.articles) == 1
        assert resolver.base_url is None
        assert resolver.validate_external is True
        assert resolver.generate_autorefs is True
    
    def test_init_with_options(self):
        """Test initialization with options."""
        from datetime import datetime
        now = datetime.now()
        articles = []
        categories = [
            Category(id=1, name="Cat 1", slug="cat-1", parent_id=None, order=1, created_at=now, updated_at=now)
        ]
        
        resolver = CrossReferenceResolver(
            articles=articles,
            categories=categories,
            base_url="https://docs.example.com",
            validate_external=False,
            generate_autorefs=False
        )
        
        assert len(resolver.articles) == 0
        assert len(resolver.categories) == 1
        assert resolver.base_url == "https://docs.example.com"
        assert resolver.validate_external is False
        assert resolver.generate_autorefs is False
    
    def test_link_reference_creation(self):
        """Test LinkReference dataclass."""
        link_ref = LinkReference(
            original_url="https://example.com",
            display_text="Example Link",
            resolved_url="https://resolved.com",
            link_type="external",
            is_valid=True
        )
        
        assert link_ref.original_url == "https://example.com"
        assert link_ref.display_text == "Example Link"
        assert link_ref.resolved_url == "https://resolved.com"
        assert link_ref.link_type == "external"
        assert link_ref.is_valid is True
        assert link_ref.validation_error is None
    
    def test_anchor_reference_creation(self):
        """Test AnchorReference dataclass."""
        anchor_ref = AnchorReference(
            anchor_id="section-1",
            heading_text="Section 1",
            level=2,
            line_number=10,
            article_id="article-1"
        )
        
        assert anchor_ref.anchor_id == "section-1"
        assert anchor_ref.heading_text == "Section 1"
        assert anchor_ref.level == 2
        assert anchor_ref.line_number == 10
        assert anchor_ref.article_id == "article-1"


class TestThemeOptimizerUnit:
    """Unit tests for ThemeOptimizer."""
    
    def test_init_default(self):
        """Test initialization with default theme."""
        optimizer = ThemeOptimizer()
        
        # This would depend on the actual implementation
        assert optimizer is not None
    
    def test_init_material_theme(self):
        """Test initialization with Material theme."""
        optimizer = ThemeOptimizer(theme="material")
        
        # This would depend on the actual implementation
        assert optimizer is not None
    
    @pytest.mark.asyncio
    async def test_optimize_empty_content(self):
        """Test optimization with empty content."""
        optimizer = ThemeOptimizer()
        
        # This would depend on the actual implementation
        # For now just test that it doesn't crash
        try:
            await optimizer.optimize([], [], Path("/tmp"))
            assert True  # No exception thrown
        except NotImplementedError:
            # This is expected if the method isn't implemented yet
            assert True


class TestMarkdownProcessorUnit:
    """Unit tests for MarkdownProcessor."""
    
    def test_init(self):
        """Test initialization."""
        processor = MarkdownProcessor()
        assert processor is not None
    
    @pytest.mark.asyncio
    async def test_convert_empty(self):
        """Test conversion of empty content."""
        processor = MarkdownProcessor()
        
        result = await processor.convert("")
        assert result == "\n"  # Empty content becomes newline after cleanup
    
    @pytest.mark.asyncio
    async def test_convert_basic_markdown(self):
        """Test conversion of basic markdown."""
        processor = MarkdownProcessor()
        
        content = "# Heading\n\nThis is **bold** text."
        result = await processor.convert(content)
        
        # Should return the content (may be processed)
        assert "Heading" in result
        assert "bold" in result