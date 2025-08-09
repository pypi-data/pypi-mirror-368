# this_file: external/int_folders/d361/src/d361/archive/__init__.py
"""
Archive package - Document360 offline archive processing.

This package provides comprehensive offline archive processing capabilities
including parsing, indexing, and intelligent caching for Document360
documentation archives.
"""

from .parser import ArchiveParser, ArchiveParserConfig, ArchiveMetadata, ParsedArchive
from .cache import SqliteCache, CacheConfig, CacheEntry, CacheStats
from .schema import ArchiveSchema, create_archive_schema, migrate_archive_schema
from .document360_parser import Document360Parser

__all__ = [
    # Archive parsing
    "ArchiveParser",
    "ArchiveParserConfig", 
    "ArchiveMetadata",
    "ParsedArchive",
    
    # Document360-specific parsing
    "Document360Parser",
    
    # Caching
    "SqliteCache",
    "CacheConfig",
    "CacheEntry",
    "CacheStats",
    
    # Database schema
    "ArchiveSchema", 
    "create_archive_schema",
    "migrate_archive_schema",
]