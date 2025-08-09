# this_file: external/int_folders/d361/src/d361/plugins/manager.py
"""
Plugin manager for automatic plugin discovery and loading.

This module provides the core plugin system infrastructure, including automatic
discovery of plugins via entry points, validation, and lifecycle management.
"""

from __future__ import annotations

import importlib
import importlib.metadata
from typing import Any, Dict, List, Type

from loguru import logger

from ..core.interfaces import ConvertedContent, ConverterPlugin


class PluginManager:
    """Manager for plugin discovery, loading, and execution.
    
    This class handles the complete plugin lifecycle:
    - Automatic discovery via entry points
    - Plugin validation and loading
    - Error isolation and recovery
    - Plugin registry management
    """

    def __init__(self) -> None:
        """Initialize the plugin manager."""
        self._converter_plugins: Dict[str, Type[ConverterPlugin]] = {}
        self._provider_plugins: Dict[str, Type[Any]] = {}  # Will be DataProvider when implemented
        self._loaded_plugins: Dict[str, Any] = {}
        
        # Auto-discover plugins on initialization
        self._discover_plugins()
        
    def _discover_plugins(self) -> None:
        """Discover and register plugins via entry points.
        
        This method scans for plugins registered in pyproject.toml entry points
        and validates them before registration.
        """
        logger.info("Discovering plugins...")
        
        # Discover converter plugins
        try:
            converter_eps = importlib.metadata.entry_points(group="d361.converters")
            for ep in converter_eps:
                try:
                    plugin_class = ep.load()
                    if self._validate_converter_plugin(plugin_class):
                        self._converter_plugins[ep.name] = plugin_class
                        logger.info(f"Registered converter plugin: {ep.name}")
                    else:
                        logger.warning(f"Invalid converter plugin: {ep.name}")
                except Exception as e:
                    logger.error(f"Failed to load converter plugin {ep.name}: {e}")
        except importlib.metadata.PackageNotFoundError:
            logger.debug("No converter plugins entry point group found")
            
        # Discover provider plugins
        try:
            provider_eps = importlib.metadata.entry_points(group="d361.providers")
            for ep in provider_eps:
                try:
                    plugin_class = ep.load()
                    # TODO: Add provider plugin validation
                    self._provider_plugins[ep.name] = plugin_class
                    logger.info(f"Registered provider plugin: {ep.name}")
                except Exception as e:
                    logger.error(f"Failed to load provider plugin {ep.name}: {e}")
        except importlib.metadata.PackageNotFoundError:
            logger.debug("No provider plugins entry point group found")
            
        logger.info(
            f"Plugin discovery complete: "
            f"{len(self._converter_plugins)} converters, "
            f"{len(self._provider_plugins)} providers"
        )
        
    def _validate_converter_plugin(self, plugin_class: Type[Any]) -> bool:
        """Validate that a class implements the ConverterPlugin protocol.
        
        Args:
            plugin_class: Class to validate
            
        Returns:
            bool: True if valid plugin
        """
        try:
            # Check if class implements required protocol methods
            required_methods = ["convert", "supported_formats", "plugin_name"]
            
            for method_name in required_methods:
                if not hasattr(plugin_class, method_name):
                    logger.error(f"Plugin {plugin_class} missing required method: {method_name}")
                    return False
                    
            # Try to instantiate the plugin (if it has a no-args constructor)
            try:
                instance = plugin_class()
                
                # Validate supported_formats returns tuple
                formats = instance.supported_formats
                if not isinstance(formats, tuple) or len(formats) != 2:
                    logger.error(f"Plugin {plugin_class} supported_formats must return tuple of length 2")
                    return False
                    
                # Validate plugin_name returns string
                name = instance.plugin_name
                if not isinstance(name, str) or not name:
                    logger.error(f"Plugin {plugin_class} plugin_name must return non-empty string")
                    return False
                    
                return True
                
            except TypeError:
                # Plugin may require constructor args, which is okay
                logger.debug(f"Plugin {plugin_class} requires constructor arguments")
                return True
                
        except Exception as e:
            logger.error(f"Error validating plugin {plugin_class}: {e}")
            return False
        
    def get_converter_plugin(self, plugin_name: str) -> Type[ConverterPlugin] | None:
        """Get a converter plugin by name.
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Plugin class or None if not found
        """
        return self._converter_plugins.get(plugin_name)
        
    def list_converter_plugins(self) -> List[str]:
        """List all registered converter plugin names.
        
        Returns:
            List of plugin names
        """
        return list(self._converter_plugins.keys())
        
    def get_plugins_for_format(self, source_format: str, target_format: str) -> List[str]:
        """Find plugins that can convert between specified formats.
        
        Args:
            source_format: Source format (e.g., "html")
            target_format: Target format (e.g., "markdown")
            
        Returns:
            List of plugin names that support the conversion
        """
        matching_plugins = []
        
        for name, plugin_class in self._converter_plugins.items():
            try:
                instance = plugin_class()
                src, tgt = instance.supported_formats
                if src == source_format and tgt == target_format:
                    matching_plugins.append(name)
            except Exception as e:
                logger.warning(f"Error checking formats for plugin {name}: {e}")
                
        return matching_plugins
        
    def convert(
        self,
        content: str,
        from_format: str,
        to_format: str,
        plugin_name: str | None = None,
        **options: Any,
    ) -> ConvertedContent:
        """Convert content using appropriate plugin.
        
        Args:
            content: Source content to convert
            from_format: Source format
            to_format: Target format
            plugin_name: Specific plugin to use (auto-select if None)
            **options: Conversion options passed to plugin
            
        Returns:
            ConvertedContent: Converted content with metadata
            
        Raises:
            ValueError: If no suitable plugin found or conversion fails
        """
        if plugin_name:
            # Use specific plugin
            plugin_class = self._converter_plugins.get(plugin_name)
            if not plugin_class:
                raise ValueError(f"Plugin '{plugin_name}' not found")
                
            try:
                plugin = plugin_class()
                return plugin.convert(content, **options)
            except Exception as e:
                logger.error(f"Plugin {plugin_name} conversion failed: {e}")
                raise ValueError(f"Conversion failed: {e}") from e
        else:
            # Auto-select plugin
            matching_plugins = self.get_plugins_for_format(from_format, to_format)
            
            if not matching_plugins:
                raise ValueError(f"No plugin found for {from_format} -> {to_format} conversion")
                
            # Try plugins in order until one succeeds
            errors = []
            for name in matching_plugins:
                try:
                    plugin_class = self._converter_plugins[name]
                    plugin = plugin_class()
                    result = plugin.convert(content, **options)
                    logger.debug(f"Successfully converted using plugin: {name}")
                    return result
                except Exception as e:
                    logger.warning(f"Plugin {name} failed: {e}")
                    errors.append(f"{name}: {e}")
                    
            raise ValueError(f"All plugins failed. Errors: {'; '.join(errors)}")
            
    def reload_plugins(self) -> None:
        """Reload all plugins from entry points.
        
        This method clears the current plugin registry and rediscovers
        all plugins, useful for development and testing.
        """
        logger.info("Reloading plugins...")
        
        self._converter_plugins.clear()
        self._provider_plugins.clear()
        self._loaded_plugins.clear()
        
        self._discover_plugins()
        
    def register_converter_plugin(
        self, 
        name: str, 
        plugin_class: Type[ConverterPlugin]
    ) -> None:
        """Manually register a converter plugin.
        
        Args:
            name: Plugin name
            plugin_class: Plugin class implementing ConverterPlugin protocol
            
        Raises:
            ValueError: If plugin is invalid
        """
        if not self._validate_converter_plugin(plugin_class):
            raise ValueError(f"Invalid plugin class: {plugin_class}")
            
        self._converter_plugins[name] = plugin_class
        logger.info(f"Manually registered converter plugin: {name}")
        
    def unregister_plugin(self, name: str) -> bool:
        """Unregister a plugin by name.
        
        Args:
            name: Plugin name to unregister
            
        Returns:
            bool: True if plugin was found and removed
        """
        removed = False
        
        if name in self._converter_plugins:
            del self._converter_plugins[name]
            removed = True
            
        if name in self._provider_plugins:
            del self._provider_plugins[name]
            removed = True
            
        if name in self._loaded_plugins:
            del self._loaded_plugins[name]
            
        if removed:
            logger.info(f"Unregistered plugin: {name}")
            
        return removed