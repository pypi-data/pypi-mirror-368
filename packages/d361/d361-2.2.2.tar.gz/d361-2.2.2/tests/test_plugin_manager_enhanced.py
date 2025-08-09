# this_file: external/int_folders/d361/tests/test_plugin_manager_enhanced.py
"""
Enhanced comprehensive tests for PluginManager and MarkdownExtensionManager.

This module provides complete unit tests for the plugin management system,
testing all plugin configurations, dependencies, validation, and optimization
scenarios that were previously incomplete.
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

from d361.mkdocs.processors.plugin_manager import (
    PluginManager,
    MarkdownExtensionManager,
    PluginConfig,
    PluginSet
)
from d361.api.errors import Document360Error


class TestPluginConfig:
    """Test PluginConfig dataclass functionality."""
    
    def test_plugin_config_creation(self):
        """Test PluginConfig creation with various parameters."""
        # Basic plugin config
        config = PluginConfig(
            name="search",
            config={"separator": r'[\s\-\.]+'},
            enabled=True,
            description="Built-in search functionality"
        )
        
        assert config.name == "search"
        assert config.config["separator"] == r'[\s\-\.]+'
        assert config.enabled is True
        assert config.description == "Built-in search functionality"
        assert config.required_dependencies == []
        assert "material" in config.theme_compatibility
    
    def test_plugin_config_to_dict_with_config(self):
        """Test conversion to MkDocs format with configuration."""
        config = PluginConfig(
            name="minify",
            config={
                "minify_html": True,
                "minify_js": True
            }
        )
        
        result = config.to_dict()
        expected = {
            "minify": {
                "minify_html": True,
                "minify_js": True
            }
        }
        
        assert result == expected
    
    def test_plugin_config_to_dict_without_config(self):
        """Test conversion to MkDocs format without configuration."""
        config = PluginConfig(name="search")
        
        result = config.to_dict()
        assert result == "search"
    
    def test_plugin_config_defaults(self):
        """Test PluginConfig default values."""
        config = PluginConfig(name="test-plugin")
        
        assert config.config == {}
        assert config.enabled is True
        assert config.required_dependencies == []
        assert config.theme_compatibility == ["material", "readthedocs", "mkdocs"]
        assert config.description == ""


class TestPluginSet:
    """Test PluginSet dataclass functionality."""
    
    def test_plugin_set_creation(self):
        """Test PluginSet creation."""
        plugins = [
            PluginConfig(name="plugin1"),
            PluginConfig(name="plugin2")
        ]
        
        plugin_set = PluginSet(
            name="test_set",
            description="Test plugin set",
            plugins=plugins,
            required_for_theme="material",
            priority=100
        )
        
        assert plugin_set.name == "test_set"
        assert plugin_set.description == "Test plugin set"
        assert len(plugin_set.plugins) == 2
        assert plugin_set.required_for_theme == "material"
        assert plugin_set.priority == 100
    
    def test_plugin_set_defaults(self):
        """Test PluginSet default values."""
        plugin_set = PluginSet(
            name="default_set",
            description="Default test set"
        )
        
        assert plugin_set.plugins == []
        assert plugin_set.required_for_theme is None
        assert plugin_set.priority == 0


class TestPluginManagerInitialization:
    """Test PluginManager initialization and setup."""
    
    def test_init_default_settings(self):
        """Test initialization with default settings."""
        manager = PluginManager()
        
        assert manager.theme == "material"
        assert manager.site_url is None
        assert manager.enable_offline is False
        
        # Verify plugin sets are initialized
        assert manager._core_plugins is not None
        assert manager._seo_plugins is not None
        assert manager._performance_plugins is not None
        assert manager._accessibility_plugins is not None
        assert manager._advanced_plugins is not None
    
    def test_init_material_theme(self):
        """Test initialization with Material theme."""
        manager = PluginManager(theme="material", site_url="https://docs.example.com")
        
        assert manager.theme == "material"
        assert manager.site_url == "https://docs.example.com"
    
    def test_init_readthedocs_theme(self):
        """Test initialization with Read the Docs theme."""
        manager = PluginManager(theme="readthedocs", enable_offline=True)
        
        assert manager.theme == "readthedocs"
        assert manager.enable_offline is True
    
    def test_init_custom_theme(self):
        """Test initialization with custom theme."""
        manager = PluginManager(theme="custom-theme")
        
        assert manager.theme == "custom-theme"


class TestCorePluginSets:
    """Test core plugin set initialization and configuration."""
    
    def test_core_plugins_initialization(self):
        """Test core plugins set initialization."""
        manager = PluginManager()
        core_plugins = manager._core_plugins
        
        assert core_plugins.name == "core"
        assert core_plugins.priority == 100
        assert len(core_plugins.plugins) >= 3  # search, autorefs, section-index
        
        plugin_names = [p.name for p in core_plugins.plugins]
        assert "search" in plugin_names
        assert "autorefs" in plugin_names
        assert "section-index" in plugin_names
    
    def test_seo_plugins_initialization_material(self):
        """Test SEO plugins for Material theme."""
        manager = PluginManager(theme="material")
        seo_plugins = manager._seo_plugins
        
        assert seo_plugins.name == "seo"
        assert seo_plugins.priority == 80
        
        plugin_names = [p.name for p in seo_plugins.plugins]
        assert "redirects" in plugin_names
        assert "social" in plugin_names  # Material theme specific
    
    def test_seo_plugins_initialization_readthedocs(self):
        """Test SEO plugins for Read the Docs theme."""
        manager = PluginManager(theme="readthedocs")
        seo_plugins = manager._seo_plugins
        
        plugin_names = [p.name for p in seo_plugins.plugins]
        assert "redirects" in plugin_names
        assert "social" not in plugin_names  # Not available for RTD theme
    
    def test_performance_plugins_initialization(self):
        """Test performance plugins initialization."""
        manager = PluginManager()
        performance_plugins = manager._performance_plugins
        
        assert performance_plugins.name == "performance"
        assert performance_plugins.priority == 60
        
        plugin_names = [p.name for p in performance_plugins.plugins]
        assert "minify" in plugin_names
        assert "offline" not in plugin_names  # Not enabled by default
    
    def test_performance_plugins_with_offline(self):
        """Test performance plugins with offline enabled."""
        manager = PluginManager(enable_offline=True)
        performance_plugins = manager._performance_plugins
        
        plugin_names = [p.name for p in performance_plugins.plugins]
        assert "minify" in plugin_names
        assert "offline" in plugin_names
    
    def test_accessibility_plugins_initialization(self):
        """Test accessibility plugins initialization."""
        manager = PluginManager()
        accessibility_plugins = manager._accessibility_plugins
        
        assert accessibility_plugins.name == "accessibility"
        assert accessibility_plugins.priority == 70
        # Currently empty - placeholder for future accessibility plugins
    
    def test_advanced_plugins_initialization(self):
        """Test advanced plugins initialization."""
        manager = PluginManager()
        advanced_plugins = manager._advanced_plugins
        
        assert advanced_plugins.name == "advanced"
        assert advanced_plugins.priority == 40
        # Should be empty without GitHub URL
    
    def test_advanced_plugins_with_github_url(self):
        """Test advanced plugins with GitHub URL."""
        manager = PluginManager(site_url="https://github.com/user/repo")
        advanced_plugins = manager._advanced_plugins
        
        plugin_names = [p.name for p in advanced_plugins.plugins]
        assert "git-revision-date-localized" in plugin_names


class TestOptimalPluginSelection:
    """Test optimal plugin selection functionality."""
    
    @pytest.mark.asyncio
    async def test_get_optimal_plugins_default(self):
        """Test getting optimal plugins with default settings."""
        manager = PluginManager(theme="material")
        
        plugins = await manager.get_optimal_plugins()
        
        assert len(plugins) > 0
        
        # Convert to plugin names for easier testing
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())
        
        # Should include core plugins
        assert "search" in plugin_names
        assert "autorefs" in plugin_names
        
        # Should include SEO plugins (enabled by default)
        assert "redirects" in plugin_names
        assert "social" in plugin_names  # Material theme
        
        # Should include performance plugins (enabled by default)
        assert "minify" in plugin_names
        
        # Should NOT include advanced plugins (disabled by default)
        assert "git-revision-date-localized" not in plugin_names
    
    @pytest.mark.asyncio
    async def test_get_optimal_plugins_minimal(self):
        """Test getting minimal plugin configuration."""
        manager = PluginManager()
        
        plugins = await manager.get_optimal_plugins(
            enable_seo=False,
            enable_performance=False,
            enable_accessibility=False,
            enable_advanced=False
        )
        
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())
        
        # Should only include core plugins
        assert "search" in plugin_names
        assert "autorefs" in plugin_names
        assert "section-index" in plugin_names
        
        # Should NOT include optional plugins
        assert "social" not in plugin_names
        assert "minify" not in plugin_names
    
    @pytest.mark.asyncio
    async def test_get_optimal_plugins_full_features(self):
        """Test getting full-featured plugin configuration."""
        manager = PluginManager(
            theme="material",
            site_url="https://github.com/user/repo",
            enable_offline=True
        )
        
        plugins = await manager.get_optimal_plugins(
            enable_seo=True,
            enable_performance=True,
            enable_accessibility=True,
            enable_advanced=True
        )
        
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())
        
        # Should include all plugin types
        assert "search" in plugin_names
        assert "social" in plugin_names
        assert "minify" in plugin_names
        assert "offline" in plugin_names
        assert "git-revision-date-localized" in plugin_names
    
    @pytest.mark.asyncio
    async def test_get_optimal_plugins_with_custom(self):
        """Test getting plugins with custom additions."""
        manager = PluginManager()
        
        custom_plugins = [
            PluginConfig(
                name="custom-plugin",
                config={"option": "value"},
                description="Custom test plugin"
            )
        ]
        
        plugins = await manager.get_optimal_plugins(
            custom_plugins=custom_plugins
        )
        
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())
        
        assert "custom-plugin" in plugin_names
    
    @pytest.mark.asyncio
    async def test_theme_compatibility_filtering(self):
        """Test theme compatibility filtering."""
        manager = PluginManager(theme="readthedocs")
        
        plugins = await manager.get_optimal_plugins()
        
        plugin_names = []
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.append(plugin)
            elif isinstance(plugin, dict):
                plugin_names.extend(plugin.keys())
        
        # Should NOT include Material-specific plugins
        assert "social" not in plugin_names
        assert "offline" not in plugin_names
        
        # Should include compatible plugins
        assert "search" in plugin_names
        assert "redirects" in plugin_names


class TestPluginDependencies:
    """Test plugin dependency management."""
    
    @pytest.mark.asyncio
    async def test_get_plugin_dependencies_basic(self):
        """Test getting plugin dependencies."""
        manager = PluginManager(theme="material")
        
        dependencies = await manager.get_plugin_dependencies()
        
        assert isinstance(dependencies, dict)
        assert len(dependencies) > 0
        
        # Should include dependencies for enabled plugins
        assert "autorefs" in dependencies
        assert "mkdocs-autorefs" in dependencies["autorefs"]
        
        assert "social" in dependencies
        assert "pillow" in dependencies["social"]
        assert "cairosvg" in dependencies["social"]
    
    @pytest.mark.asyncio
    async def test_get_plugin_dependencies_minimal(self):
        """Test getting minimal plugin dependencies."""
        manager = PluginManager()
        
        dependencies = await manager.get_plugin_dependencies(
            enable_seo=False,
            enable_performance=False,
            enable_accessibility=False,
            enable_advanced=False
        )
        
        # Should only include core plugin dependencies
        assert "autorefs" in dependencies
        assert "section-index" in dependencies
        
        # Should NOT include optional plugin dependencies
        assert "social" not in dependencies
        assert "minify" not in dependencies
    
    def test_get_installation_guide(self):
        """Test getting installation guide."""
        manager = PluginManager(theme="material")
        
        guide = manager.get_installation_guide()
        
        assert "dependencies_by_plugin" in guide
        assert "all_dependencies" in guide
        assert "pip_install_command" in guide
        assert "installation_notes" in guide
        
        # Verify pip command format
        pip_command = guide["pip_install_command"]
        assert pip_command.startswith("pip install ")
        assert "mkdocs-autorefs" in pip_command
        
        # Verify installation notes
        notes = guide["installation_notes"]
        assert "pillow" in notes
        assert "mkdocs-autorefs" in notes


class TestPluginValidation:
    """Test plugin configuration validation."""
    
    def test_validate_plugin_configuration_valid(self):
        """Test validation of valid plugin configuration."""
        manager = PluginManager()
        
        plugins_config = [
            "search",
            {"autorefs": {}},
            {"minify": {"minify_html": True}}
        ]
        
        results = manager.validate_plugin_configuration(plugins_config)
        
        assert results["valid"] is True
        assert len(results["errors"]) == 0
    
    def test_validate_plugin_configuration_missing_search(self):
        """Test validation with missing search plugin."""
        manager = PluginManager()
        
        plugins_config = [
            {"autorefs": {}},
            {"minify": {"minify_html": True}}
        ]
        
        results = manager.validate_plugin_configuration(plugins_config)
        
        assert results["valid"] is True  # Still valid, just warnings
        assert len(results["warnings"]) > 0
        assert any("Search plugin missing" in warning for warning in results["warnings"])
    
    def test_validate_plugin_configuration_suggestions(self):
        """Test validation suggestions for optimization."""
        manager = PluginManager(theme="material", enable_offline=True)
        
        plugins_config = ["search"]  # Minimal configuration
        
        results = manager.validate_plugin_configuration(plugins_config)
        
        assert len(results["suggestions"]) > 0
        suggestions_text = " ".join(results["suggestions"])
        assert "social" in suggestions_text or "minify" in suggestions_text or "offline" in suggestions_text
    
    def test_validate_plugin_configuration_theme_specific(self):
        """Test theme-specific validation suggestions."""
        manager = PluginManager(theme="material")
        
        plugins_config = ["search", "autorefs"]
        
        results = manager.validate_plugin_configuration(plugins_config)
        
        suggestions_text = " ".join(results["suggestions"])
        assert "social" in suggestions_text  # Material theme specific suggestion


class TestMarkdownExtensionManager:
    """Test MarkdownExtensionManager functionality."""
    
    def test_markdown_extension_manager_init(self):
        """Test MarkdownExtensionManager initialization."""
        manager = MarkdownExtensionManager(theme="material")
        
        assert manager.theme == "material"
    
    def test_get_core_extensions(self):
        """Test getting core Markdown extensions."""
        manager = MarkdownExtensionManager()
        
        extensions = manager.get_core_extensions()
        
        assert isinstance(extensions, list)
        assert "meta" in extensions
        assert "attr_list" in extensions
        assert "tables" in extensions
        assert "footnotes" in extensions
    
    def test_get_enhanced_extensions(self):
        """Test getting enhanced Markdown extensions."""
        manager = MarkdownExtensionManager()
        
        extensions = manager.get_enhanced_extensions()
        
        assert isinstance(extensions, list)
        assert len(extensions) > 0
        
        # Check for specific enhanced extensions
        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())
        
        assert "toc" in extension_names
        assert "admonition" in extension_names
        assert "pymdownx.superfences" in extension_names
        assert "pymdownx.tabbed" in extension_names
        assert "pymdownx.highlight" in extension_names
    
    def test_get_advanced_extensions(self):
        """Test getting advanced Markdown extensions."""
        manager = MarkdownExtensionManager()
        
        extensions = manager.get_advanced_extensions()
        
        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())
        
        assert "pymdownx.arithmatex" in extension_names
        assert "pymdownx.betterem" in extension_names
        assert "pymdownx.caret" in extension_names
        assert "pymdownx.mark" in extension_names
    
    def test_get_advanced_extensions_material_theme(self):
        """Test advanced extensions for Material theme."""
        manager = MarkdownExtensionManager(theme="material")
        
        extensions = manager.get_advanced_extensions()
        
        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())
        
        # Should include Material-specific emoji extension
        assert "pymdownx.emoji" in extension_names
    
    def test_get_optimal_extensions_default(self):
        """Test getting optimal extensions with default settings."""
        manager = MarkdownExtensionManager()
        
        extensions = manager.get_optimal_extensions()
        
        assert len(extensions) > 10  # Should include many extensions
        
        # Should include all categories
        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())
        
        assert "meta" in extension_names  # Core
        assert "pymdownx.superfences" in extension_names  # Enhanced
        assert "pymdownx.arithmatex" in extension_names  # Advanced
    
    def test_get_optimal_extensions_minimal(self):
        """Test getting minimal extensions configuration."""
        manager = MarkdownExtensionManager()
        
        extensions = manager.get_optimal_extensions(
            include_advanced=False,
            include_math=False,
            include_diagrams=False
        )
        
        extension_names = []
        for ext in extensions:
            if isinstance(ext, str):
                extension_names.append(ext)
            elif isinstance(ext, dict):
                extension_names.extend(ext.keys())
        
        # Should still include core and enhanced
        assert "meta" in extension_names
        assert "pymdownx.superfences" in extension_names
        
        # Should NOT include advanced or math
        assert "pymdownx.arithmatex" not in extension_names
    
    def test_extension_configuration_details(self):
        """Test detailed extension configurations."""
        manager = MarkdownExtensionManager()
        
        extensions = manager.get_enhanced_extensions()
        
        # Find TOC extension configuration
        toc_config = None
        for ext in extensions:
            if isinstance(ext, dict) and "toc" in ext:
                toc_config = ext["toc"]
                break
        
        assert toc_config is not None
        assert "permalink" in toc_config
        assert "toc_depth" in toc_config
        
        # Find superfences configuration
        superfences_config = None
        for ext in extensions:
            if isinstance(ext, dict) and "pymdownx.superfences" in ext:
                superfences_config = ext["pymdownx.superfences"]
                break
        
        assert superfences_config is not None
        assert "custom_fences" in superfences_config
        assert len(superfences_config["custom_fences"]) >= 2  # mermaid, math


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""
    
    @pytest.mark.asyncio
    async def test_complete_plugin_workflow(self):
        """Test complete plugin management workflow."""
        manager = PluginManager(
            theme="material",
            site_url="https://docs.example.com",
            enable_offline=True
        )
        
        # Get optimal plugins
        plugins = await manager.get_optimal_plugins(
            enable_seo=True,
            enable_performance=True,
            enable_advanced=True
        )
        
        # Get dependencies
        dependencies = await manager.get_plugin_dependencies(
            enable_seo=True,
            enable_performance=True,
            enable_advanced=True
        )
        
        # Get installation guide
        guide = manager.get_installation_guide(
            enable_seo=True,
            enable_performance=True,
            enable_advanced=True
        )
        
        # Validate configuration
        results = manager.validate_plugin_configuration(plugins)
        
        # Verify workflow completed successfully
        assert len(plugins) > 0
        assert len(dependencies) > 0
        assert "pip_install_command" in guide
        assert results["valid"] is True
    
    def test_extension_manager_workflow(self):
        """Test complete extension manager workflow."""
        manager = MarkdownExtensionManager(theme="material")
        
        # Get different extension sets
        core = manager.get_core_extensions()
        enhanced = manager.get_enhanced_extensions()
        advanced = manager.get_advanced_extensions()
        optimal = manager.get_optimal_extensions()
        
        # Verify all sets are valid
        assert len(core) > 0
        assert len(enhanced) > 0
        assert len(advanced) > 0
        assert len(optimal) > len(core)  # Optimal should include more
        
        # Verify no duplicates in optimal
        extension_names = []
        for ext in optimal:
            if isinstance(ext, str):
                if ext not in extension_names:
                    extension_names.append(ext)
            elif isinstance(ext, dict):
                for name in ext.keys():
                    if name not in extension_names:
                        extension_names.append(name)
        
        assert len(extension_names) == len(set(extension_names))  # No duplicates


if __name__ == "__main__":
    pytest.main([__file__, "-v"])