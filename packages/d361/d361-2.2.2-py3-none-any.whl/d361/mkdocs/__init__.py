"""MkDocs export functionality for d361.

This module provides comprehensive Document360 → MkDocs conversion capabilities,
including support for Material theme, popular plugins, and modern MkDocs features.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/__init__.py

# Exporters
from d361.mkdocs.exporters.mkdocs_exporter import MkDocsExporter
from d361.mkdocs.exporters.config_generator import ConfigGenerator
from d361.mkdocs.exporters.navigation_builder import NavigationBuilder
from d361.mkdocs.exporters.theme_optimizer import ThemeOptimizer

# Processors  
from d361.mkdocs.processors.markdown_processor import MarkdownProcessor
from d361.mkdocs.processors.content_enhancer import ContentEnhancer
from d361.mkdocs.processors.cross_reference_resolver import CrossReferenceResolver, LinkReference, AnchorReference
from d361.mkdocs.processors.asset_manager import AssetManager, AssetReference, OptimizationResult

# Phase 3: Plugin Ecosystem Integration
from d361.mkdocs.processors.plugin_manager import (
    PluginManager,
    PluginConfig,
    PluginSet,
    MarkdownExtensionManager,
)
from d361.mkdocs.processors.seo_optimizer import (
    SEOOptimizer,
    SEOMetadata,
    StructuredData,
)
from d361.mkdocs.processors.accessibility_optimizer import (
    AccessibilityOptimizer,
    AccessibilityReport,
    AccessibilityIssue,
    WCAGLevel,
    ContrastRatio,
)

__all__ = [
    # Exporters
    "MkDocsExporter",
    "ConfigGenerator", 
    "NavigationBuilder",
    "ThemeOptimizer",
    
    # Core Processors (Phase 1 & 2)
    "MarkdownProcessor",
    "ContentEnhancer",
    "CrossReferenceResolver",
    "LinkReference", 
    "AnchorReference",
    "AssetManager",
    "AssetReference",
    "OptimizationResult",
    
    # Phase 3: Plugin Management
    "PluginManager",
    "PluginConfig",
    "PluginSet",
    "MarkdownExtensionManager",
    
    # Phase 3: SEO Optimization
    "SEOOptimizer", 
    "SEOMetadata",
    "StructuredData",
    
    # Phase 3: Accessibility Enhancement
    "AccessibilityOptimizer",
    "AccessibilityReport",
    "AccessibilityIssue",
    "WCAGLevel",
    "ContrastRatio",
]