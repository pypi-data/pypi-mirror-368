"""Advanced MkDocs plugin management and integration.

This module provides comprehensive plugin management capabilities for MkDocs
with specialized support for popular plugins and advanced configurations.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/plugin_manager.py

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from loguru import logger

from d361.api.errors import Document360Error, ErrorCategory, ErrorSeverity


@dataclass
class PluginConfig:
    """Configuration for a specific MkDocs plugin."""
    
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    required_dependencies: List[str] = field(default_factory=list)
    theme_compatibility: List[str] = field(default_factory=lambda: ["material", "readthedocs", "mkdocs"])
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plugin config to MkDocs format."""
        if self.config:
            return {self.name: self.config}
        return self.name


@dataclass
class PluginSet:
    """A collection of related plugins."""
    
    name: str
    description: str
    plugins: List[PluginConfig] = field(default_factory=list)
    required_for_theme: Optional[str] = None
    priority: int = 0  # Higher priority sets are loaded first


class PluginManager:
    """Advanced MkDocs plugin management system.
    
    This class provides comprehensive plugin management with:
    - Theme-specific plugin configurations
    - Plugin dependency management
    - Advanced plugin configurations for popular plugins
    - Plugin conflict resolution
    - Performance optimization settings
    
    Example:
        plugin_manager = PluginManager(theme="material")
        plugins = await plugin_manager.get_optimal_plugins(
            enable_seo=True,
            enable_performance=True,
            enable_accessibility=True
        )
    """
    
    def __init__(
        self,
        theme: str = "material",
        site_url: Optional[str] = None,
        enable_offline: bool = False,
    ) -> None:
        """Initialize plugin manager.
        
        Args:
            theme: MkDocs theme to optimize for
            site_url: Site URL for deployment-specific optimizations
            enable_offline: Enable offline functionality
        """
        self.theme = theme
        self.site_url = site_url
        self.enable_offline = enable_offline
        
        # Initialize plugin sets
        self._core_plugins = self._init_core_plugins()
        self._seo_plugins = self._init_seo_plugins()
        self._performance_plugins = self._init_performance_plugins()
        self._accessibility_plugins = self._init_accessibility_plugins()
        self._advanced_plugins = self._init_advanced_plugins()
        
        logger.info(f"Initialized PluginManager for {theme} theme")
    
    def _init_core_plugins(self) -> PluginSet:
        """Initialize core essential plugins."""
        return PluginSet(
            name="core",
            description="Essential plugins for basic functionality",
            priority=100,
            plugins=[
                PluginConfig(
                    name="search",
                    config={
                        "separator": r'[\s\-\.]+'
                    },
                    description="Built-in search functionality"
                ),
                PluginConfig(
                    name="autorefs",
                    config={},
                    required_dependencies=["mkdocs-autorefs"],
                    description="Automatic cross-referencing between pages"
                ),
                PluginConfig(
                    name="section-index",
                    config={},
                    required_dependencies=["mkdocs-section-index"],
                    description="Clickable section headers with index pages"
                ),
            ]
        )
    
    def _init_seo_plugins(self) -> PluginSet:
        """Initialize SEO and social media plugins."""
        plugins = [
            PluginConfig(
                name="redirects",
                config={
                    "redirect_maps": {}  # Will be populated with actual redirects
                },
                required_dependencies=["mkdocs-redirects"],
                description="Handle URL redirects for moved content"
            ),
        ]
        
        if self.theme == "material":
            plugins.extend([
                PluginConfig(
                    name="social",
                    config={
                        "cards": True,
                        "cards_layout_options": {
                            "background_color": "#1976d2",
                            "color": "#ffffff",
                        },
                        "cards_dir": "assets/images/social",
                    },
                    theme_compatibility=["material"],
                    required_dependencies=["pillow", "cairosvg"],
                    description="Generate social media cards for sharing"
                ),
            ])
        
        return PluginSet(
            name="seo",
            description="SEO and social media optimization plugins",
            priority=80,
            plugins=plugins
        )
    
    def _init_performance_plugins(self) -> PluginSet:
        """Initialize performance optimization plugins."""
        plugins = [
            PluginConfig(
                name="minify",
                config={
                    "minify_html": True,
                    "minify_js": True,
                    "minify_css": True,
                    "htmlmin_opts": {
                        "remove_comments": True,
                        "remove_empty_space": True,
                        "remove_all_empty_space": False,
                        "strip_whitespace": True,
                        "reduce_boolean_attributes": True,
                    },
                    "cache_safe": True,
                    "js_files": [
                        "assets/javascripts/bundle.*.min.js"
                    ],
                    "css_files": [
                        "assets/stylesheets/*.min.css"
                    ]
                },
                required_dependencies=["mkdocs-minify-plugin"],
                description="Minify HTML, CSS, and JS for production"
            ),
        ]
        
        if self.enable_offline:
            plugins.append(
                PluginConfig(
                    name="offline",
                    config={
                        "enabled": True,
                    },
                    theme_compatibility=["material"],
                    required_dependencies=[],
                    description="Enable offline functionality"
                )
            )
        
        return PluginSet(
            name="performance",
            description="Performance optimization plugins",
            priority=60,
            plugins=plugins
        )
    
    def _init_accessibility_plugins(self) -> PluginSet:
        """Initialize accessibility enhancement plugins."""
        return PluginSet(
            name="accessibility",
            description="Accessibility enhancement plugins",
            priority=70,
            plugins=[
                # Future accessibility plugins can be added here
            ]
        )
    
    def _init_advanced_plugins(self) -> PluginSet:
        """Initialize advanced feature plugins."""
        plugins = []
        
        # Add advanced plugins based on needs
        if self.site_url and "github" in self.site_url.lower():
            plugins.append(
                PluginConfig(
                    name="git-revision-date-localized",
                    config={
                        "enable_creation_date": True,
                        "type": "date",
                        "fallback_to_build_date": True,
                    },
                    required_dependencies=["mkdocs-git-revision-date-localized-plugin"],
                    description="Add git-based page modification dates"
                )
            )
        
        return PluginSet(
            name="advanced",
            description="Advanced feature plugins",
            priority=40,
            plugins=plugins
        )
    
    async def get_optimal_plugins(
        self,
        enable_seo: bool = True,
        enable_performance: bool = True,
        enable_accessibility: bool = True,
        enable_advanced: bool = False,
        custom_plugins: Optional[List[PluginConfig]] = None,
    ) -> List[Dict[str, Any]]:
        """Get optimal plugin configuration for the current setup.
        
        Args:
            enable_seo: Include SEO optimization plugins
            enable_performance: Include performance optimization plugins
            enable_accessibility: Include accessibility plugins
            enable_advanced: Include advanced feature plugins
            custom_plugins: Additional custom plugins to include
            
        Returns:
            List of plugin configurations in MkDocs format
        """
        logger.info("Building optimal plugin configuration")
        
        plugin_sets = [self._core_plugins]  # Always include core plugins
        
        if enable_seo:
            plugin_sets.append(self._seo_plugins)
        
        if enable_performance:
            plugin_sets.append(self._performance_plugins)
        
        if enable_accessibility:
            plugin_sets.append(self._accessibility_plugins)
        
        if enable_advanced:
            plugin_sets.append(self._advanced_plugins)
        
        # Sort by priority (highest first)
        plugin_sets.sort(key=lambda x: x.priority, reverse=True)
        
        # Collect all plugins
        all_plugins = []
        plugin_names = set()
        
        for plugin_set in plugin_sets:
            for plugin_config in plugin_set.plugins:
                if plugin_config.enabled and plugin_config.name not in plugin_names:
                    # Check theme compatibility
                    if self.theme in plugin_config.theme_compatibility:
                        all_plugins.append(plugin_config.to_dict())
                        plugin_names.add(plugin_config.name)
                        logger.debug(f"Added plugin: {plugin_config.name}")
                    else:
                        logger.debug(f"Skipping plugin {plugin_config.name} (incompatible with {self.theme})")
        
        # Add custom plugins
        if custom_plugins:
            for custom_plugin in custom_plugins:
                if custom_plugin.name not in plugin_names:
                    all_plugins.append(custom_plugin.to_dict())
                    logger.debug(f"Added custom plugin: {custom_plugin.name}")
        
        logger.info(f"Built plugin configuration with {len(all_plugins)} plugins")
        return all_plugins
    
    async def get_plugin_dependencies(
        self,
        enable_seo: bool = True,
        enable_performance: bool = True,
        enable_accessibility: bool = True,
        enable_advanced: bool = False,
    ) -> Dict[str, List[str]]:
        """Get all plugin dependencies for installation.
        
        Args:
            enable_seo: Include SEO optimization plugins
            enable_performance: Include performance optimization plugins
            enable_accessibility: Include accessibility plugins
            enable_advanced: Include advanced feature plugins
            
        Returns:
            Dictionary mapping plugin names to their dependencies
        """
        plugin_sets = [self._core_plugins]
        
        if enable_seo:
            plugin_sets.append(self._seo_plugins)
        if enable_performance:
            plugin_sets.append(self._performance_plugins)
        if enable_accessibility:
            plugin_sets.append(self._accessibility_plugins)
        if enable_advanced:
            plugin_sets.append(self._advanced_plugins)
        
        dependencies = {}
        
        for plugin_set in plugin_sets:
            for plugin_config in plugin_set.plugins:
                if plugin_config.enabled and plugin_config.required_dependencies:
                    dependencies[plugin_config.name] = plugin_config.required_dependencies
        
        logger.info(f"Collected dependencies for {len(dependencies)} plugins")
        return dependencies
    
    def get_installation_guide(
        self,
        enable_seo: bool = True,
        enable_performance: bool = True,
        enable_accessibility: bool = True,
        enable_advanced: bool = False,
    ) -> Dict[str, Any]:
        """Get installation guide for required dependencies.
        
        Returns:
            Dictionary with installation instructions and commands
        """
        # Get dependencies synchronously (we'll convert to async later if needed)
        import asyncio
        dependencies = asyncio.run(self.get_plugin_dependencies(
            enable_seo=enable_seo,
            enable_performance=enable_performance,
            enable_accessibility=enable_accessibility,
            enable_advanced=enable_advanced
        ))
        
        # Collect all unique dependencies
        all_deps = set()
        for deps in dependencies.values():
            all_deps.update(deps)
        
        pip_command = f"pip install {' '.join(sorted(all_deps))}"
        
        return {
            "dependencies_by_plugin": dependencies,
            "all_dependencies": sorted(all_deps),
            "pip_install_command": pip_command,
            "installation_notes": {
                "pillow": "Required for social card generation (Material theme)",
                "cairosvg": "Required for SVG to PNG conversion in social cards",
                "mkdocs-autorefs": "Enables automatic cross-references between pages",
                "mkdocs-section-index": "Enables clickable section headers",
                "mkdocs-redirects": "Handles URL redirects for moved content",
                "mkdocs-minify-plugin": "Minifies HTML, CSS, and JS for production",
                "mkdocs-git-revision-date-localized-plugin": "Adds git-based modification dates"
            }
        }
    
    def validate_plugin_configuration(self, plugins_config: List[Any]) -> Dict[str, Any]:
        """Validate plugin configuration for common issues.
        
        Args:
            plugins_config: Plugin configuration to validate
            
        Returns:
            Validation results with errors, warnings, and suggestions
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        plugin_names = set()
        
        for plugin in plugins_config:
            if isinstance(plugin, str):
                plugin_names.add(plugin)
            elif isinstance(plugin, dict):
                for name in plugin.keys():
                    plugin_names.add(name)
        
        # Check for essential plugins
        if "search" not in plugin_names:
            results["warnings"].append("Search plugin missing - users won't be able to search content")
        
        # Check for theme-specific recommendations
        if self.theme == "material":
            if "social" not in plugin_names:
                results["suggestions"].append("Consider adding social plugin for Material theme social cards")
            
            if "offline" not in plugin_names and self.enable_offline:
                results["suggestions"].append("Consider adding offline plugin for offline functionality")
        
        # Check for performance optimizations
        if "minify" not in plugin_names:
            results["suggestions"].append("Consider adding minify plugin for better performance")
        
        # Check for SEO optimizations
        if "redirects" not in plugin_names:
            results["suggestions"].append("Consider adding redirects plugin for URL management")
        
        logger.info(f"Plugin validation completed. Valid: {results['valid']}")
        return results


class MarkdownExtensionManager:
    """Advanced Markdown extension management for MkDocs.
    
    This class provides comprehensive management of Python Markdown extensions
    with optimized configurations for different use cases.
    """
    
    def __init__(self, theme: str = "material") -> None:
        """Initialize Markdown extension manager.
        
        Args:
            theme: MkDocs theme to optimize for
        """
        self.theme = theme
        logger.info(f"Initialized MarkdownExtensionManager for {theme} theme")
    
    def get_core_extensions(self) -> List[Dict[str, Any] | str]:
        """Get core Markdown extensions."""
        return [
            "meta",
            "attr_list",
            "md_in_html",
            "def_list",
            "footnotes",
            "tables",
            "abbr",
        ]
    
    def get_enhanced_extensions(self) -> List[Dict[str, Any] | str]:
        """Get enhanced Markdown extensions with advanced configurations."""
        extensions = [
            {
                "toc": {
                    "permalink": "⚓",
                    "permalink_title": "Anchor link to this section for reference",
                    "slugify": "!!python/name:pymdownx.slugs.uslugify",
                    "toc_depth": 3,
                }
            },
            {
                "admonition": {}
            },
            {
                "pymdownx.details": {}
            },
            {
                "pymdownx.superfences": {
                    "custom_fences": [
                        {
                            "name": "mermaid",
                            "class": "mermaid",
                            "format": "!!python/name:pymdownx.superfences.fence_code_format"
                        },
                        {
                            "name": "math",
                            "class": "arithmatex",
                            "format": "!!python/name:pymdownx.arithmatex.fence_mathjax_format"
                        }
                    ],
                    "preserve_tabs": True,
                }
            },
            {
                "pymdownx.tabbed": {
                    "alternate_style": True,
                    "combine_header_slug": True,
                    "slugify": "!!python/name:pymdownx.slugs.uslugify",
                }
            },
            {
                "pymdownx.highlight": {
                    "anchor_linenums": True,
                    "line_spans": "__span",
                    "pygments_lang_class": True,
                    "auto_title": True,
                    "linenums": False,
                }
            },
            {
                "pymdownx.inlinehilite": {
                    "style_plain_text": True,
                }
            },
            {
                "pymdownx.snippets": {
                    "auto_append": ["includes/abbreviations.md"],
                    "check_paths": True,
                }
            },
            {
                "pymdownx.tasklist": {
                    "custom_checkbox": True,
                    "clickable_checkbox": True,
                }
            },
        ]
        
        return extensions
    
    def get_advanced_extensions(self) -> List[Dict[str, Any] | str]:
        """Get advanced Markdown extensions for specialized content."""
        extensions = [
            {
                "pymdownx.arithmatex": {
                    "generic": True,
                }
            },
            {
                "pymdownx.betterem": {
                    "smart_enable": "all",
                }
            },
            {
                "pymdownx.caret": {}
            },
            {
                "pymdownx.mark": {}
            },
            {
                "pymdownx.tilde": {}
            },
            {
                "pymdownx.keys": {}
            },
            {
                "pymdownx.smartsymbols": {}
            },
        ]
        
        if self.theme == "material":
            extensions.append({
                "pymdownx.emoji": {
                    "emoji_index": "!!python/name:material.extensions.emoji.twemoji",
                    "emoji_generator": "!!python/name:material.extensions.emoji.to_svg",
                    "options": {
                        "custom_icons": [
                            "material/extensions/emoji.json"
                        ]
                    }
                }
            })
        
        return extensions
    
    def get_optimal_extensions(
        self,
        include_advanced: bool = True,
        include_math: bool = True,
        include_diagrams: bool = True,
    ) -> List[Dict[str, Any] | str]:
        """Get optimal Markdown extensions configuration.
        
        Args:
            include_advanced: Include advanced typography extensions
            include_math: Include math rendering extensions
            include_diagrams: Include diagram rendering extensions
            
        Returns:
            List of optimized Markdown extensions
        """
        extensions = []
        extensions.extend(self.get_core_extensions())
        extensions.extend(self.get_enhanced_extensions())
        
        if include_advanced:
            extensions.extend(self.get_advanced_extensions())
        
        if not include_math:
            # Remove math-related extensions
            extensions = [ext for ext in extensions 
                         if not (isinstance(ext, dict) and 'pymdownx.arithmatex' in ext)]
        
        if not include_diagrams:
            # Remove diagram-related custom fences
            for ext in extensions:
                if isinstance(ext, dict) and 'pymdownx.superfences' in ext:
                    fences = ext['pymdownx.superfences'].get('custom_fences', [])
                    ext['pymdownx.superfences']['custom_fences'] = [
                        fence for fence in fences if fence.get('name') not in ['mermaid']
                    ]
        
        logger.info(f"Built Markdown extensions configuration with {len(extensions)} extensions")
        return extensions