"""Content processors for MkDocs export functionality."""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/__init__.py

from d361.mkdocs.processors.markdown_processor import MarkdownProcessor
from d361.mkdocs.processors.content_enhancer import ContentEnhancer
from d361.mkdocs.processors.asset_manager import AssetManager
from d361.mkdocs.processors.cross_reference_resolver import CrossReferenceResolver

# Phase 3: Plugin Ecosystem Integration components
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
    # Phase 1 & 2 components
    "MarkdownProcessor",
    "ContentEnhancer", 
    "AssetManager",
    "CrossReferenceResolver",
    
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