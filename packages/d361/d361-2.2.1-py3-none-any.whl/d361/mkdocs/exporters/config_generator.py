"""MkDocs configuration generator for Document360 exports.

This module generates optimized MkDocs YAML configurations with support for
Material theme, popular plugins, and modern MkDocs features.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/exporters/config_generator.py

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from jinja2 import Environment, PackageLoader, select_autoescape, Template, TemplateError, TemplateSyntaxError

from loguru import logger

from d361.api.errors import Document360Error, ErrorCategory, ErrorSeverity


class ConfigGenerator:
    """Generate MkDocs configuration files with theme and plugin support.
    
    This class creates optimized MkDocs configurations for different themes
    and use cases, with built-in support for popular plugins and extensions.
    
    Features:
    - Material theme integration with all features
    - Popular plugin configurations (autorefs, section-index, redirects)
    - Python Markdown extensions (SuperFences, tabbed, admonitions)
    - Performance optimizations (minify, search)
    - SEO and accessibility features
    - Template-based customization
    
    Example:
        generator = ConfigGenerator(theme="material", enable_plugins=True)
        config_yaml = await generator.generate_config(
            site_name="My Documentation",
            navigation=navigation_structure
        )
    """
    
    def __init__(
        self,
        theme: str = "material",
        enable_plugins: bool = True,
        template_dir: Optional[Path] = None,
    ) -> None:
        """Initialize configuration generator.
        
        Args:
            theme: MkDocs theme to use ('material', 'readthedocs', etc.)
            enable_plugins: Enable popular MkDocs plugins
            template_dir: Custom template directory (uses built-in if None)
        """
        self.theme = theme
        self.enable_plugins = enable_plugins
        self.template_dir = template_dir
        
        # Initialize Jinja2 environment
        if template_dir:
            self.jinja_env = Environment(
                loader=PackageLoader("d361.mkdocs", "templates"),
                autoescape=select_autoescape(["html", "xml", "yml", "yaml"])
            )
        else:
            # Use built-in templates
            self.jinja_env = Environment(
                loader=PackageLoader("d361.mkdocs", "templates"),
                autoescape=select_autoescape(["html", "xml", "yml", "yaml"])
            )
        
        # Add custom filters
        self.jinja_env.filters["to_yaml"] = self._yaml_filter
        
        logger.info(f"Initialized ConfigGenerator for {theme} theme")
    
    def _yaml_filter(self, obj: Any) -> str:
        """Convert object to YAML string for templates."""
        return yaml.dump(obj, default_flow_style=False, sort_keys=False).strip()
    
    async def generate_config(
        self,
        site_name: str,
        navigation: List[Dict[str, Any]],
        output_path: Path,
        site_url: Optional[str] = None,
        site_description: Optional[str] = None,
        repo_url: Optional[str] = None,
        edit_uri: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate MkDocs configuration YAML.
        
        Args:
            site_name: Site name for MkDocs
            navigation: Navigation structure
            output_path: Output directory path
            site_url: Site URL for deployment
            site_description: Site description for SEO
            repo_url: Repository URL for source links
            edit_uri: Edit URI for page editing
            custom_config: Additional custom configuration
            
        Returns:
            Generated MkDocs configuration as YAML string
        """
        logger.info(f"Generating MkDocs config for {site_name}")
        
        # Build base configuration
        config = self._build_base_config(
            site_name=site_name,
            site_url=site_url,
            site_description=site_description,
            repo_url=repo_url,
            edit_uri=edit_uri,
        )
        
        # Add theme configuration
        config["theme"] = self._build_theme_config()
        
        # Add plugins
        if self.enable_plugins:
            config["plugins"] = self._build_plugins_config()
        
        # Add Markdown extensions
        config["markdown_extensions"] = self._build_markdown_extensions()
        
        # Add navigation
        config["nav"] = navigation
        
        # Add extra configuration
        config["extra"] = self._build_extra_config()
        
        # Merge custom configuration
        if custom_config:
            config = self._merge_configs(config, custom_config)
        
        # Convert to YAML
        yaml_config = yaml.dump(config, default_flow_style=False, sort_keys=False)
        
        logger.info("Generated MkDocs configuration successfully")
        return yaml_config
    
    def _build_base_config(
        self,
        site_name: str,
        site_url: Optional[str] = None,
        site_description: Optional[str] = None,
        repo_url: Optional[str] = None,
        edit_uri: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build base MkDocs configuration."""
        config = {
            "site_name": site_name,
            "docs_dir": "docs",
            "site_dir": "site",
        }
        
        if site_url:
            config["site_url"] = site_url
        
        if site_description:
            config["site_description"] = site_description
        
        if repo_url:
            config["repo_url"] = repo_url
            
        if edit_uri:
            config["edit_uri"] = edit_uri
        
        return config
    
    def _build_theme_config(self) -> Dict[str, Any]:
        """Build theme configuration."""
        if self.theme == "material":
            return self._build_material_theme_config()
        elif self.theme == "readthedocs":
            return self._build_readthedocs_theme_config()
        else:
            return {"name": self.theme}
    
    def _build_material_theme_config(self) -> Dict[str, Any]:
        """Build Material theme configuration with all features."""
        return {
            "name": "material",
            "features": [
                "navigation.instant",
                "navigation.instant.prefetch",
                "navigation.tracking",
                "navigation.tabs",
                "navigation.tabs.sticky",
                "navigation.sections",
                "navigation.expand",
                "navigation.indexes",
                "navigation.top",
                "search.highlight",
                "search.share",
                "search.suggest",
                "toc.follow",
                "toc.integrate",
                "content.action.edit",
                "content.action.view",
                "content.code.copy",
                "content.code.annotate",
                "content.tabs.link",
                "content.tooltips",
            ],
            "palette": [
                {
                    "media": "(prefers-color-scheme)",
                    "toggle": {
                        "icon": "material/brightness-auto",
                        "name": "Switch to light mode",
                    },
                },
                {
                    "media": "(prefers-color-scheme: light)",
                    "scheme": "default",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Switch to dark mode",
                    },
                },
                {
                    "media": "(prefers-color-scheme: dark)",
                    "scheme": "slate",
                    "primary": "black",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Switch to system preference",
                    },
                },
            ],
            "font": {
                "text": "Roboto",
                "code": "Roboto Mono",
            },
            "icon": {
                "logo": "material/library",
                "repo": "fontawesome/brands/github",
            },
        }
    
    def _build_readthedocs_theme_config(self) -> Dict[str, Any]:
        """Build Read the Docs theme configuration."""
        return {
            "name": "readthedocs",
            "highlightjs": True,
            "hljs_languages": ["yaml", "python", "javascript", "bash"],
        }
    
    def _build_plugins_config(self) -> List[Dict[str, Any]]:
        """Build plugins configuration."""
        plugins = [
            "search",
        ]
        
        if self.enable_plugins:
            plugins.extend([
                {
                    "autorefs": {
                        # Automatic cross-referencing
                    }
                },
                {
                    "section-index": {
                        # Clickable sections
                    }
                },
                {
                    "redirects": {
                        "redirect_maps": {}  # Will be populated with actual redirects
                    }
                },
                {
                    "minify": {
                        "minify_html": True,
                        "minify_js": True,
                        "minify_css": True,
                        "htmlmin_opts": {
                            "remove_comments": True
                        },
                        "cache_safe": True,
                    }
                },
            ])
            
            if self.theme == "material":
                plugins.extend([
                    {
                        "social": {
                            "cards": True,
                            "cards_layout_options": {
                                "background_color": "#1976d2",
                            },
                        }
                    },
                    {
                        "offline": {
                            "enabled": False,  # Enable for offline builds
                        }
                    },
                ])
        
        return plugins
    
    def _build_markdown_extensions(self) -> List[Dict[str, Any] | str]:
        """Build Markdown extensions configuration."""
        extensions = [
            "meta",
            "attr_list",
            "md_in_html",
            "def_list",
            "footnotes",
            "tables",
            "abbr",
            {
                "toc": {
                    "permalink": True,
                    "permalink_title": "Anchor link to this section for reference",
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
                        }
                    ]
                }
            },
            {
                "pymdownx.tabbed": {
                    "alternate_style": True,
                    "combine_header_slug": True,
                }
            },
            {
                "pymdownx.highlight": {
                    "anchor_linenums": True,
                    "line_spans": "__span",
                    "pygments_lang_class": True,
                }
            },
            {
                "pymdownx.inlinehilite": {}
            },
            {
                "pymdownx.snippets": {
                    "auto_append": ["includes/abbreviations.md"],
                }
            },
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
                "pymdownx.tasklist": {
                    "custom_checkbox": True,
                }
            },
            {
                "pymdownx.emoji": {
                    "emoji_index": "!!python/name:material.extensions.emoji.twemoji",
                    "emoji_generator": "!!python/name:material.extensions.emoji.to_svg",
                }
            },
        ]
        
        return extensions
    
    def _build_extra_config(self) -> Dict[str, Any]:
        """Build extra configuration."""
        extra = {
            "generator": "d361",
            "version": {
                "provider": "mike",
            },
            "social": [
                {
                    "icon": "fontawesome/brands/github",
                    "link": "https://github.com/",
                    "name": "GitHub"
                },
            ],
        }
        
        if self.theme == "material":
            extra.update({
                "status": {
                    "new": "Recently added",
                    "deprecated": "Deprecated",
                },
                "analytics": {
                    "feedback": {
                        "title": "Was this page helpful?",
                        "ratings": [
                            {
                                "icon": "material/emoticon-happy-outline",
                                "name": "This page was helpful",
                                "data": 1,
                                "note": "Thanks for your feedback!"
                            },
                            {
                                "icon": "material/emoticon-sad-outline", 
                                "name": "This page could be improved",
                                "data": 0,
                                "note": "Thanks for your feedback! Help us improve by letting us know what you're looking for."
                            }
                        ]
                    }
                }
            })
        
        return extra
    
    def _merge_configs(
        self, 
        base_config: Dict[str, Any], 
        custom_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge custom configuration with base configuration."""
        def deep_merge(base: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
            """Recursively merge dictionaries."""
            result = base.copy()
            for key, value in custom.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(base_config, custom_config)
    
    async def generate_config_from_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        validate_output: bool = True,
    ) -> str:
        """Generate configuration from Jinja2 template with validation.
        
        Args:
            template_name: Name of template file
            context: Template context variables
            validate_output: Validate generated YAML configuration
            
        Returns:
            Generated configuration as string
            
        Raises:
            Document360Error: If template generation or validation fails
        """
        try:
            # Validate template exists
            self._validate_template_exists(template_name)
            
            # Validate context for template
            self._validate_template_context(template_name, context)
            
            # Get and render template
            template = self.jinja_env.get_template(template_name)
            config_content = template.render(context)
            
            # Validate generated configuration
            if validate_output:
                self._validate_generated_config(config_content, template_name)
            
            logger.info(f"Successfully generated config from template: {template_name}")
            return config_content
            
        except TemplateSyntaxError as e:
            error_msg = f"Template syntax error in {template_name}: {e}"
            logger.error(error_msg)
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH,
                context={"template": template_name, "line": e.lineno}
            )
        except TemplateError as e:
            error_msg = f"Template rendering error in {template_name}: {e}"
            logger.error(error_msg)
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.PROCESSING_ERROR,
                severity=ErrorSeverity.HIGH,
                context={"template": template_name}
            )
        except Exception as e:
            error_msg = f"Unexpected error generating config from template {template_name}: {e}"
            logger.error(error_msg)
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.CRITICAL,
                context={"template": template_name}
            )
    
    def _validate_template_exists(self, template_name: str) -> None:
        """Validate that template file exists.
        
        Args:
            template_name: Name of template to check
            
        Raises:
            Document360Error: If template doesn't exist
        """
        try:
            self.jinja_env.get_template(template_name)
        except Exception:
            available_templates = self._get_available_templates()
            error_msg = f"Template '{template_name}' not found"
            
            logger.error(f"{error_msg}. Available templates: {available_templates}")
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH,
                context={
                    "template": template_name,
                    "available_templates": available_templates
                }
            )
    
    def _validate_template_context(self, template_name: str, context: Dict[str, Any]) -> None:
        """Validate template context variables.
        
        Args:
            template_name: Name of template
            context: Context variables to validate
            
        Raises:
            Document360Error: If required context variables are missing
        """
        # Define required context variables for each template
        required_contexts = {
            "mkdocs_base.yml.j2": ["site_name"],
            "material_theme.yml.j2": ["site_name"],
            "plugin_configs.yml.j2": []
        }
        
        required_vars = required_contexts.get(template_name, [])
        missing_vars = [var for var in required_vars if var not in context]
        
        if missing_vars:
            error_msg = f"Missing required context variables for template '{template_name}': {missing_vars}"
            logger.error(error_msg)
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH,
                context={
                    "template": template_name,
                    "missing_variables": missing_vars,
                    "required_variables": required_vars
                }
            )
    
    def _validate_generated_config(self, config_content: str, template_name: str) -> None:
        """Validate generated YAML configuration.
        
        Args:
            config_content: Generated YAML content
            template_name: Template used to generate config
            
        Raises:
            Document360Error: If configuration is invalid
        """
        try:
            # Parse YAML to ensure it's valid
            parsed_config = yaml.safe_load(config_content)
            
            # Validate required MkDocs fields
            self._validate_mkdocs_structure(parsed_config, template_name)
            
            # Validate theme-specific requirements
            if "theme" in parsed_config:
                self._validate_theme_config(parsed_config["theme"], template_name)
            
            # Validate plugin configurations
            if "plugins" in parsed_config:
                self._validate_plugin_configs(parsed_config["plugins"], template_name)
                
            logger.debug(f"Configuration validation passed for template: {template_name}")
            
        except yaml.YAMLError as e:
            error_msg = f"Invalid YAML syntax in generated config from template '{template_name}': {e}"
            logger.error(error_msg)
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH,
                context={"template": template_name, "yaml_error": str(e)}
            )
    
    def _validate_mkdocs_structure(self, config: Dict[str, Any], template_name: str) -> None:
        """Validate basic MkDocs configuration structure.
        
        Args:
            config: Parsed configuration dictionary
            template_name: Template used to generate config
            
        Raises:
            Document360Error: If structure is invalid
        """
        required_fields = ["site_name"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            error_msg = f"Missing required MkDocs fields in template '{template_name}': {missing_fields}"
            logger.error(error_msg)
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH,
                context={
                    "template": template_name,
                    "missing_fields": missing_fields,
                    "required_fields": required_fields
                }
            )
        
        # Validate field types
        if not isinstance(config["site_name"], str):
            error_msg = f"Invalid site_name type in template '{template_name}': expected string"
            logger.error(error_msg)
            raise Document360Error(
                message=error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    def _validate_theme_config(self, theme_config: Union[str, Dict[str, Any]], template_name: str) -> None:
        """Validate theme configuration.
        
        Args:
            theme_config: Theme configuration (string or dict)
            template_name: Template used to generate config
            
        Raises:
            Document360Error: If theme config is invalid
        """
        if isinstance(theme_config, dict):
            if "name" not in theme_config:
                error_msg = f"Theme configuration missing 'name' field in template '{template_name}'"
                logger.error(error_msg)
                raise Document360Error(
                    message=error_msg,
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.HIGH,
                    context={"template": template_name}
                )
            
            theme_name = theme_config["name"]
        else:
            theme_name = theme_config
        
        # Validate known theme names
        known_themes = ["material", "readthedocs", "mkdocs"]
        if theme_name not in known_themes:
            logger.warning(f"Unknown theme '{theme_name}' in template '{template_name}'. Known themes: {known_themes}")
    
    def _validate_plugin_configs(self, plugins: List[Any], template_name: str) -> None:
        """Validate plugin configurations.
        
        Args:
            plugins: List of plugin configurations
            template_name: Template used to generate config
            
        Raises:
            Document360Error: If plugin config is invalid
        """
        for i, plugin in enumerate(plugins):
            if isinstance(plugin, dict):
                # Validate each plugin configuration
                for plugin_name, plugin_config in plugin.items():
                    if not isinstance(plugin_config, (dict, type(None))):
                        error_msg = f"Invalid plugin config for '{plugin_name}' in template '{template_name}'"
                        logger.error(error_msg)
                        raise Document360Error(
                            message=error_msg,
                            category=ErrorCategory.VALIDATION,
                            severity=ErrorSeverity.MEDIUM,
                            context={"template": template_name, "plugin": plugin_name}
                        )
    
    def _get_available_templates(self) -> List[str]:
        """Get list of available template names.
        
        Returns:
            List of available template file names
        """
        try:
            # Get templates from the Jinja2 environment
            return list(self.jinja_env.list_templates(filter_func=lambda name: name.endswith('.j2')))
        except Exception as e:
            logger.warning(f"Could not list available templates: {e}")
            return ["mkdocs_base.yml.j2", "material_theme.yml.j2", "plugin_configs.yml.j2"]
    
    def validate_final_config(self, config_yaml: str) -> Dict[str, Any]:
        """Validate a final MkDocs configuration and return validation results.
        
        Args:
            config_yaml: Complete MkDocs configuration as YAML string
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Parse YAML
            config = yaml.safe_load(config_yaml)
            
            # Check required fields
            if "site_name" not in config:
                results["valid"] = False
                results["errors"].append("Missing required field: site_name")
            
            # Check theme configuration
            if "theme" in config:
                theme = config["theme"]
                if isinstance(theme, dict) and "name" not in theme:
                    results["warnings"].append("Theme configuration should include 'name' field")
                elif isinstance(theme, str) and theme not in ["material", "readthedocs", "mkdocs"]:
                    results["warnings"].append(f"Unknown theme: {theme}")
            
            # Check navigation
            if "nav" not in config:
                results["suggestions"].append("Consider adding navigation structure for better user experience")
            
            # Check for SEO fields
            if "site_description" not in config:
                results["suggestions"].append("Consider adding site_description for better SEO")
            
            # Check for performance optimizations
            plugins = config.get("plugins", [])
            plugin_names = []
            for plugin in plugins:
                if isinstance(plugin, str):
                    plugin_names.append(plugin)
                elif isinstance(plugin, dict):
                    plugin_names.extend(plugin.keys())
            
            if "search" not in plugin_names:
                results["warnings"].append("Search plugin not found - users won't be able to search content")
            
            if "minify" not in plugin_names and config.get("theme", {}).get("name") == "material":
                results["suggestions"].append("Consider adding minify plugin for better performance")
            
            logger.info(f"Configuration validation completed. Valid: {results['valid']}, Errors: {len(results['errors'])}, Warnings: {len(results['warnings'])}")
            
        except yaml.YAMLError as e:
            results["valid"] = False
            results["errors"].append(f"YAML syntax error: {e}")
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Validation error: {e}")
        
        return results