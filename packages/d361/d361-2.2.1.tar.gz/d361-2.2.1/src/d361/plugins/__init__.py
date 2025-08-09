# this_file: external/int_folders/d361/src/d361/plugins/__init__.py
"""
Plugin system for the d361 library.

This package provides a plugin architecture for extending the library with
custom converters, providers, and other functionality without modifying
the core codebase.
"""

from .manager import PluginManager

__all__ = [
    "PluginManager",
]