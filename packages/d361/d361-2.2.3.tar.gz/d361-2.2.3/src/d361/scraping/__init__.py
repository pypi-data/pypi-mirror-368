# this_file: external/int_folders/d361/src/d361/scraping/__init__.py
"""
Scraping package - Document360 web scraping and content extraction.

This package provides comprehensive web scraping capabilities including
browser automation, content extraction, HTML-to-Markdown conversion,
and intelligent deduplication for Document360 websites.
"""

from .scraper import (
    Document360Scraper, ScrapingConfig, ScrapedPage, ScrapingSession,
    BrowserType, ScrapingMode, UserAgent
)
from .extractor import (
    ContentExtractor, ExtractionConfig, ExtractedContent, ContentBlock,
    ContentType, ExtractionQuality
)
from .converter import (
    MarkdownConverter, ConversionConfig, ConversionResult, ConversionStats,
    MarkdownStyle, LinkHandling, Document360MarkdownConverter
)
from .deduplicator import (
    ContentDeduplicator, DeduplicationConfig, DuplicateStatus, SimilarityScore,
    SimilarityAlgorithm, DuplicateGroup
)
from .content_processor import ContentProcessor, Document360ContentProcessor

__all__ = [
    # Web scraping
    "Document360Scraper",
    "ScrapingConfig",
    "ScrapedPage", 
    "ScrapingSession",
    "BrowserType",
    "ScrapingMode", 
    "UserAgent",
    
    # Content extraction
    "ContentExtractor",
    "ExtractionConfig",
    "ExtractedContent",
    "ContentBlock",
    "ContentType",
    "ExtractionQuality",
    
    # Markdown conversion
    "MarkdownConverter",
    "ConversionConfig", 
    "ConversionResult",
    "ConversionStats",
    "MarkdownStyle",
    "LinkHandling",
    "Document360MarkdownConverter",
    
    # Deduplication
    "ContentDeduplicator",
    "DeduplicationConfig",
    "DuplicateStatus",
    "SimilarityScore",
    "SimilarityAlgorithm",
    "DuplicateGroup",
    
    # Content processing
    "ContentProcessor",
    "Document360ContentProcessor",
]