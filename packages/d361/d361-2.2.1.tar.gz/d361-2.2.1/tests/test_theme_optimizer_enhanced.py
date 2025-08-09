# this_file: external/int_folders/d361/tests/test_theme_optimizer_enhanced.py
"""
Enhanced comprehensive tests for ThemeOptimizer.

This module provides complete unit tests for the ThemeOptimizer component,
testing all theme-specific functionality, asset generation, and configuration
integration that was previously incomplete.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

from d361.core.models import Article, Category
from d361.mkdocs.exporters.theme_optimizer import ThemeOptimizer
from d361.api.errors import Document360Error


@pytest.fixture
def sample_articles() -> List[Article]:
    """Create sample articles for theme optimization testing."""
    from datetime import datetime
    now = datetime.now()
    return [
        Article(
            id=1,
            title="Getting Started Guide",
            slug="getting-started",
            content="""# Getting Started

This is a comprehensive guide with various content types.

!!! note "Important Information"
    This is a callout box that should be optimized for the theme.

## Code Example

```python
def hello_world():
    print("Hello, world!")
```

## Image Example

![Architecture Diagram](images/architecture.png)

## Table Example

| Feature | Supported |
|---------|-----------|
| Tables  | Yes       |
| Images  | Yes       |

""",
            category_id=1,
            created_at=now,
            updated_at=now
        ),
        Article(
            id=2, 
            title="API Reference",
            slug="api-reference",
            content="""# API Reference

Complete API documentation.

!!! warning "Deprecated"
    This endpoint will be removed in v2.0.

```json
{
  "status": "success",
  "data": {
    "message": "Hello World"
  }
}
```
""",
            category_id=2,
            created_at=now,
            updated_at=now
        )
    ]


@pytest.fixture
def sample_categories() -> List[Category]:
    """Create sample categories for theme optimization testing."""
    from datetime import datetime
    now = datetime.now()
    return [
        Category(
            id=1,
            name="User Guides",
            slug="guides",
            description="Step-by-step guides",
            order=1,
            created_at=now,
            updated_at=now
        ),
        Category(
            id=2,
            name="API Reference", 
            slug="reference",
            description="Complete API documentation",
            order=2,
            created_at=now,
            updated_at=now
        )
    ]


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestThemeOptimizerInitialization:
    """Test ThemeOptimizer initialization and configuration."""
    
    def test_init_default_settings(self):
        """Test initialization with default settings."""
        optimizer = ThemeOptimizer()
        
        assert optimizer.theme == "material"
        assert optimizer.custom_css == []
        assert optimizer.custom_js == []
        assert optimizer.enable_customizations is True
        assert optimizer.theme_settings["supports_social_cards"] is True
    
    def test_init_material_theme(self):
        """Test initialization with Material theme."""
        optimizer = ThemeOptimizer(theme="material")
        
        assert optimizer.theme == "material"
        settings = optimizer.theme_settings
        assert settings["supports_social_cards"] is True
        assert settings["supports_instant_loading"] is True
        assert settings["supports_tabs"] is True
        assert settings["supports_sections"] is True
        assert settings["requires_custom_css"] is True
    
    def test_init_readthedocs_theme(self):
        """Test initialization with Read the Docs theme."""
        optimizer = ThemeOptimizer(theme="readthedocs")
        
        assert optimizer.theme == "readthedocs"
        settings = optimizer.theme_settings
        assert settings["supports_social_cards"] is False
        assert settings["supports_instant_loading"] is False
        assert settings["supports_tabs"] is False
        assert settings["supports_sections"] is True
        assert settings["requires_custom_css"] is True
    
    def test_init_custom_theme(self):
        """Test initialization with custom theme."""
        optimizer = ThemeOptimizer(theme="custom-theme")
        
        assert optimizer.theme == "custom-theme"
        settings = optimizer.theme_settings
        assert settings["supports_social_cards"] is False
        assert settings["supports_instant_loading"] is False
        assert settings["requires_custom_css"] is False
    
    def test_init_with_custom_assets(self):
        """Test initialization with custom CSS and JS."""
        custom_css = ["/path/to/custom.css", "/path/to/another.css"]
        custom_js = ["/path/to/custom.js"]
        
        optimizer = ThemeOptimizer(
            theme="material",
            custom_css=custom_css,
            custom_js=custom_js,
            enable_customizations=False
        )
        
        assert optimizer.custom_css == custom_css
        assert optimizer.custom_js == custom_js
        assert optimizer.enable_customizations is False


class TestMaterialThemeOptimization:
    """Test Material theme specific optimizations."""
    
    @pytest.mark.asyncio
    async def test_material_theme_optimization(
        self, 
        sample_articles: List[Article],
        sample_categories: List[Category],
        temp_output_dir: Path
    ):
        """Test complete Material theme optimization."""
        optimizer = ThemeOptimizer(theme="material")
        
        results = await optimizer.optimize(sample_articles, sample_categories, temp_output_dir)
        
        # Verify optimization results
        assert results["theme"] == "material"
        assert len(results["optimizations_applied"]) > 0
        assert "material_css_customization" in results["optimizations_applied"]
        assert "material_social_cards" in results["optimizations_applied"]
        assert "material_content_optimization" in results["optimizations_applied"]
        assert "common_optimizations" in results["optimizations_applied"]
        
        # Verify files were created
        assert len(results["files_created"]) > 0
        
        # Verify CSS file was created
        css_path = temp_output_dir / "docs" / "stylesheets" / "extra.css"
        assert css_path.exists()
        css_content = css_path.read_text()
        assert "Material theme customizations" in css_content
        assert "--md-primary-fg-color" in css_content
        assert ".d360-callout" in css_content
        
        # Verify JS file was created
        js_path = temp_output_dir / "docs" / "javascripts" / "extra.js"
        assert js_path.exists()
        js_content = js_path.read_text()
        assert "Material theme enhancements" in js_content
        assert "document$" in js_content  # Material theme instant loading integration
        assert "MathJax" in js_content
    
    @pytest.mark.asyncio
    async def test_material_css_generation(self, temp_output_dir: Path):
        """Test Material theme CSS generation."""
        optimizer = ThemeOptimizer(theme="material")
        results = {"files_created": []}
        
        await optimizer._create_material_css(temp_output_dir, results)
        
        css_path = temp_output_dir / "docs" / "stylesheets" / "extra.css"
        assert css_path.exists()
        assert str(css_path) in results["files_created"]
        
        css_content = css_path.read_text()
        
        # Verify CSS variables
        assert ":root" in css_content
        assert "--md-primary-fg-color" in css_content
        assert "--d360-callout-note" in css_content
        
        # Verify component styles
        assert ".d360-callout" in css_content
        assert ".d360-image" in css_content
        assert ".d360-table" in css_content
        assert ".d360-code-block" in css_content
        
        # Verify responsive styles
        assert "@media screen and (max-width: 768px)" in css_content
        assert "@media print" in css_content
    
    @pytest.mark.asyncio
    async def test_material_js_generation(self, temp_output_dir: Path):
        """Test Material theme JavaScript generation."""
        optimizer = ThemeOptimizer(theme="material")
        results = {"files_created": []}
        
        await optimizer._create_material_js(temp_output_dir, results)
        
        js_path = temp_output_dir / "docs" / "javascripts" / "extra.js"
        assert js_path.exists()
        assert str(js_path) in results["files_created"]
        
        js_content = js_path.read_text()
        
        # Verify JavaScript functionality
        assert "DOMContentLoaded" in js_content
        assert "d360-image" in js_content
        assert "d360-code-block" in js_content
        assert "d360-table" in js_content
        
        # Verify MathJax configuration
        assert "window.MathJax" in js_content
        assert "tex" in js_content
        assert "processEscapes" in js_content
        
        # Verify Material instant loading integration
        assert "document$" in js_content
        assert "subscribe" in js_content
    
    @pytest.mark.asyncio
    async def test_material_social_cards_setup(self, temp_output_dir: Path):
        """Test Material theme social cards setup."""
        optimizer = ThemeOptimizer(theme="material")
        results = {"files_created": []}
        
        await optimizer._setup_material_social_cards(temp_output_dir, results)
        
        # Verify assets directory was created
        assets_dir = temp_output_dir / "docs" / "assets"
        assert assets_dir.exists()
        assert assets_dir.is_dir()
    
    def test_material_config_updates(self):
        """Test Material theme configuration updates."""
        optimizer = ThemeOptimizer(theme="material")
        
        config_updates = optimizer.get_theme_config_updates()
        
        assert "extra_css" in config_updates
        assert "extra_javascript" in config_updates
        assert "stylesheets/extra.css" in config_updates["extra_css"]
        assert "javascripts/extra.js" in config_updates["extra_javascript"]
        assert "mathjax" in str(config_updates["extra_javascript"])


class TestReadTheDocsThemeOptimization:
    """Test Read the Docs theme specific optimizations."""
    
    @pytest.mark.asyncio
    async def test_readthedocs_theme_optimization(
        self,
        sample_articles: List[Article],
        sample_categories: List[Category], 
        temp_output_dir: Path
    ):
        """Test Read the Docs theme optimization."""
        optimizer = ThemeOptimizer(theme="readthedocs")
        
        results = await optimizer.optimize(sample_articles, sample_categories, temp_output_dir)
        
        assert results["theme"] == "readthedocs"
        assert "readthedocs_css_customization" in results["optimizations_applied"]
        assert "common_optimizations" in results["optimizations_applied"]
        
        # Verify CSS was created
        css_path = temp_output_dir / "docs" / "stylesheets" / "extra.css"
        assert css_path.exists()
        
        css_content = css_path.read_text()
        assert "Read the Docs theme customizations" in css_content
        assert ".rst-content" in css_content
        assert ".d360-callout" in css_content
    
    def test_readthedocs_config_updates(self):
        """Test Read the Docs theme configuration updates."""
        optimizer = ThemeOptimizer(theme="readthedocs")
        
        config_updates = optimizer.get_theme_config_updates()
        
        assert "extra_css" in config_updates
        assert "stylesheets/extra.css" in config_updates["extra_css"]
        # RTD theme doesn't need JavaScript by default
        assert "javascripts/extra.js" not in str(config_updates)


class TestGenericThemeOptimization:
    """Test generic theme optimizations."""
    
    @pytest.mark.asyncio
    async def test_generic_theme_optimization(
        self,
        sample_articles: List[Article],
        sample_categories: List[Category],
        temp_output_dir: Path
    ):
        """Test generic theme optimization."""
        optimizer = ThemeOptimizer(theme="mkdocs")
        
        results = await optimizer.optimize(sample_articles, sample_categories, temp_output_dir)
        
        assert results["theme"] == "mkdocs"
        assert "generic_theme_css" in results["optimizations_applied"]
        assert "common_optimizations" in results["optimizations_applied"]
        
        # Verify CSS was created
        css_path = temp_output_dir / "docs" / "stylesheets" / "extra.css"
        assert css_path.exists()
        
        css_content = css_path.read_text()
        assert "Generic theme customizations" in css_content
        assert ".d360-callout" in css_content
        assert ".d360-image" in css_content
        assert ".d360-table" in css_content
    
    def test_generic_config_updates(self):
        """Test generic theme configuration updates."""
        optimizer = ThemeOptimizer(theme="mkdocs")
        
        config_updates = optimizer.get_theme_config_updates()
        
        assert "extra_css" in config_updates
        assert "stylesheets/extra.css" in config_updates["extra_css"]


class TestCustomAssetsHandling:
    """Test custom CSS and JavaScript handling."""
    
    @pytest.mark.asyncio
    async def test_custom_css_handling(self, temp_output_dir: Path):
        """Test custom CSS file handling."""
        # Create temporary custom CSS file
        custom_css_file = temp_output_dir / "custom.css"
        custom_css_file.write_text("/* Custom styles */")
        
        optimizer = ThemeOptimizer(
            theme="material",
            custom_css=[str(custom_css_file)]
        )
        
        results = await optimizer.optimize([], [], temp_output_dir)
        
        # Verify custom CSS was copied
        copied_css = temp_output_dir / "docs" / "stylesheets" / "custom.css"
        assert copied_css.exists()
        assert str(copied_css) in results["files_created"]
        
        # Verify config includes custom CSS
        config_updates = optimizer.get_theme_config_updates()
        assert "stylesheets/custom.css" in config_updates["extra_css"]
    
    @pytest.mark.asyncio
    async def test_custom_js_handling(self, temp_output_dir: Path):
        """Test custom JavaScript file handling."""
        # Create temporary custom JS file
        custom_js_file = temp_output_dir / "custom.js"
        custom_js_file.write_text("// Custom JavaScript")
        
        optimizer = ThemeOptimizer(
            theme="material",
            custom_js=[str(custom_js_file)]
        )
        
        results = await optimizer.optimize([], [], temp_output_dir)
        
        # Verify custom JS was copied
        copied_js = temp_output_dir / "docs" / "javascripts" / "custom.js"
        assert copied_js.exists()
        assert str(copied_js) in results["files_created"]
        
        # Verify config includes custom JS
        config_updates = optimizer.get_theme_config_updates()
        assert "javascripts/custom.js" in config_updates["extra_javascript"]
    
    @pytest.mark.asyncio
    async def test_missing_custom_files_warning(self, temp_output_dir: Path):
        """Test handling of missing custom asset files."""
        optimizer = ThemeOptimizer(
            theme="material",
            custom_css=["/nonexistent/custom.css"],
            custom_js=["/nonexistent/custom.js"]
        )
        
        results = await optimizer.optimize([], [], temp_output_dir)
        
        # Verify warnings were generated
        assert len(results["warnings"]) >= 2
        assert any("Custom CSS file not found" in warning for warning in results["warnings"])
        assert any("Custom JS file not found" in warning for warning in results["warnings"])


class TestOptimizationControl:
    """Test optimization control and configuration."""
    
    @pytest.mark.asyncio
    async def test_optimizations_disabled(
        self,
        sample_articles: List[Article],
        sample_categories: List[Category],
        temp_output_dir: Path
    ):
        """Test optimization when customizations are disabled."""
        optimizer = ThemeOptimizer(theme="material", enable_customizations=False)
        
        results = await optimizer.optimize(sample_articles, sample_categories, temp_output_dir)
        
        assert results["theme"] == "material"
        assert len(results["optimizations_applied"]) == 0
        assert len(results["files_created"]) == 0
        assert len(results["files_modified"]) == 0
    
    def test_theme_settings_retrieval(self):
        """Test theme settings for different themes."""
        # Test Material theme
        material_optimizer = ThemeOptimizer(theme="material")
        material_settings = material_optimizer.theme_settings
        assert material_settings["supports_social_cards"] is True
        assert material_settings["supports_instant_loading"] is True
        
        # Test RTD theme
        rtd_optimizer = ThemeOptimizer(theme="readthedocs")
        rtd_settings = rtd_optimizer.theme_settings
        assert rtd_settings["supports_social_cards"] is False
        assert rtd_settings["supports_instant_loading"] is False
        
        # Test generic theme
        generic_optimizer = ThemeOptimizer(theme="custom")
        generic_settings = generic_optimizer.theme_settings
        assert generic_settings["supports_social_cards"] is False
        assert generic_settings["requires_custom_css"] is False


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""
    
    @pytest.mark.asyncio
    async def test_empty_content_optimization(self, temp_output_dir: Path):
        """Test optimization with empty content."""
        optimizer = ThemeOptimizer(theme="material")
        
        results = await optimizer.optimize([], [], temp_output_dir)
        
        # Should still apply optimizations even with empty content
        assert results["theme"] == "material"
        assert len(results["optimizations_applied"]) > 0
        assert len(results["files_created"]) > 0
    
    @pytest.mark.asyncio
    async def test_large_content_optimization(self, temp_output_dir: Path):
        """Test optimization with large content sets."""
        from datetime import datetime
        now = datetime.now()
        # Create many articles
        large_articles = []
        for i in range(100):
            article = Article(
                id=i + 1,  # Use integer IDs starting from 1
                title=f"Article {i}",
                slug=f"article-{i}",
                content=f"Content for article {i}" * 100,
                category_id=1,  # Use integer category ID
                created_at=now,
                updated_at=now
            )
            large_articles.append(article)
        
        optimizer = ThemeOptimizer(theme="material")
        
        results = await optimizer.optimize(large_articles, [], temp_output_dir)
        
        assert results["theme"] == "material"
        assert len(results["optimizations_applied"]) > 0
        # Should handle large content without issues
    
    @pytest.mark.asyncio
    async def test_directory_creation_edge_cases(self, temp_output_dir: Path):
        """Test directory creation in various scenarios."""
        optimizer = ThemeOptimizer(theme="material")
        
        # Test with read-only parent directory (if possible to simulate)
        results = await optimizer.optimize([], [], temp_output_dir)
        
        # Verify directories were created successfully
        assert (temp_output_dir / "docs" / "stylesheets").exists()
        assert (temp_output_dir / "docs" / "javascripts").exists()
        assert (temp_output_dir / "docs" / "assets").exists()
    
    def test_config_updates_merging(self):
        """Test configuration updates with multiple custom files."""
        optimizer = ThemeOptimizer(
            theme="material",
            custom_css=["custom1.css", "custom2.css"],
            custom_js=["custom1.js", "custom2.js"]
        )
        
        config_updates = optimizer.get_theme_config_updates()
        
        # Verify all files are included
        assert len(config_updates["extra_css"]) >= 3  # extra.css + 2 custom
        assert len(config_updates["extra_javascript"]) >= 3  # extra.js + mathjax + 2 custom
        assert "stylesheets/custom1.css" in config_updates["extra_css"]
        assert "stylesheets/custom2.css" in config_updates["extra_css"]
        assert "javascripts/custom1.js" in config_updates["extra_javascript"]
        assert "javascripts/custom2.js" in config_updates["extra_javascript"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])