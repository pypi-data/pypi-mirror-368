# this_file: external/int_folders/d361/src/d361/archive/schema.py
"""
Database schema for Document360 archive indexing.

This module provides comprehensive SQLite schema design optimized for
archive content indexing with full-text search (FTS5), efficient
metadata queries, and performance optimization.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from loguru import logger
from pydantic import BaseModel, Field

from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class ArchiveSchema(BaseModel):
    """Schema configuration for archive database."""
    
    version: int = Field(default=1, description="Schema version")
    enable_fts: bool = Field(default=True, description="Enable full-text search")
    enable_wal: bool = Field(default=True, description="Enable WAL mode")
    enable_foreign_keys: bool = Field(default=True, description="Enable foreign keys")
    
    # Performance settings
    cache_size: int = Field(default=10000, description="SQLite cache size")
    page_size: int = Field(default=4096, description="SQLite page size")
    synchronous: str = Field(default="NORMAL", description="Synchronous mode")
    
    # Index settings
    create_indexes: bool = Field(default=True, description="Create performance indexes")
    fts_tokenizer: str = Field(default="unicode61", description="FTS tokenizer")


# SQL Schema Definitions

SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
"""

ARCHIVES_TABLE = """
CREATE TABLE IF NOT EXISTS archives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash TEXT UNIQUE NOT NULL,
    archive_format TEXT NOT NULL,
    
    -- Processing metadata
    parsed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processing_time_seconds REAL,
    
    -- Content statistics
    total_entries INTEGER DEFAULT 0,
    processed_entries INTEGER DEFAULT 0,
    failed_entries INTEGER DEFAULT 0,
    articles_count INTEGER DEFAULT 0,
    categories_count INTEGER DEFAULT 0,
    assets_count INTEGER DEFAULT 0,
    
    -- Archive structure
    root_directories TEXT, -- JSON array
    file_extensions TEXT, -- JSON object
    
    -- Validation
    validation_errors TEXT, -- JSON array
    validation_warnings TEXT, -- JSON array
    
    -- Status
    status TEXT DEFAULT 'processed', -- processed, failed, partial
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

ARCHIVE_ENTRIES_TABLE = """
CREATE TABLE IF NOT EXISTS archive_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archive_id INTEGER NOT NULL,
    
    -- Entry metadata
    path TEXT NOT NULL,
    size INTEGER NOT NULL,
    modified_time DATETIME,
    content_type TEXT,
    mime_type TEXT,
    
    -- Content
    content BLOB,
    text_content TEXT,
    content_hash TEXT,
    
    -- Extracted metadata
    metadata TEXT, -- JSON object
    
    -- Processing info
    processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processing_status TEXT DEFAULT 'success', -- success, failed, skipped
    error_message TEXT,
    
    FOREIGN KEY (archive_id) REFERENCES archives (id) ON DELETE CASCADE
);
"""

ARTICLES_TABLE = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    archive_id INTEGER NOT NULL,
    entry_id INTEGER,
    
    -- Article data
    title TEXT NOT NULL,
    slug TEXT,
    content TEXT,
    content_type TEXT DEFAULT 'markdown',
    
    -- Metadata
    category_id INTEGER,
    status TEXT DEFAULT 'published',
    author TEXT,
    tags TEXT, -- JSON array
    
    -- Timestamps
    created_at DATETIME,
    updated_at DATETIME,
    published_at DATETIME,
    
    -- Processing
    extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (archive_id) REFERENCES archives (id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id) REFERENCES archive_entries (id) ON DELETE SET NULL
);
"""

CATEGORIES_TABLE = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    archive_id INTEGER NOT NULL,
    entry_id INTEGER,
    
    -- Category data
    name TEXT NOT NULL,
    slug TEXT,
    description TEXT,
    parent_id INTEGER,
    
    -- Hierarchy
    level INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at DATETIME,
    updated_at DATETIME,
    
    -- Processing
    extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (archive_id) REFERENCES archives (id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id) REFERENCES archive_entries (id) ON DELETE SET NULL,
    FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE SET NULL
);
"""

PROJECTS_TABLE = """
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    archive_id INTEGER NOT NULL,
    entry_id INTEGER,
    
    -- Project data
    name TEXT NOT NULL,
    version TEXT,
    description TEXT,
    
    -- Metadata
    language TEXT,
    settings TEXT, -- JSON object
    
    -- Timestamps
    created_at DATETIME,
    updated_at DATETIME,
    
    -- Processing
    extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (archive_id) REFERENCES archives (id) ON DELETE CASCADE,
    FOREIGN KEY (entry_id) REFERENCES archive_entries (id) ON DELETE SET NULL
);
"""

# Full-Text Search Tables

ARTICLES_FTS_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
    title,
    content,
    tags,
    content='articles',
    content_rowid='id',
    tokenize='unicode61 remove_diacritics 1'
);
"""

ARCHIVE_ENTRIES_FTS_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS archive_entries_fts USING fts5(
    path,
    text_content,
    metadata,
    content='archive_entries',
    content_rowid='id', 
    tokenize='unicode61 remove_diacritics 1'
);
"""

# FTS Triggers for synchronization

ARTICLES_FTS_TRIGGERS = """
-- Articles FTS triggers
CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, title, content, tags) 
    VALUES (new.id, new.title, new.content, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, title, content, tags) 
    VALUES('delete', old.id, old.title, old.content, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, title, content, tags) 
    VALUES('delete', old.id, old.title, old.content, old.tags);
    INSERT INTO articles_fts(rowid, title, content, tags) 
    VALUES (new.id, new.title, new.content, new.tags);
END;
"""

ARCHIVE_ENTRIES_FTS_TRIGGERS = """
-- Archive entries FTS triggers
CREATE TRIGGER IF NOT EXISTS archive_entries_ai AFTER INSERT ON archive_entries BEGIN
    INSERT INTO archive_entries_fts(rowid, path, text_content, metadata) 
    VALUES (new.id, new.path, new.text_content, new.metadata);
END;

CREATE TRIGGER IF NOT EXISTS archive_entries_ad AFTER DELETE ON archive_entries BEGIN
    INSERT INTO archive_entries_fts(archive_entries_fts, rowid, path, text_content, metadata) 
    VALUES('delete', old.id, old.path, old.text_content, old.metadata);
END;

CREATE TRIGGER IF NOT EXISTS archive_entries_au AFTER UPDATE ON archive_entries BEGIN
    INSERT INTO archive_entries_fts(archive_entries_fts, rowid, path, text_content, metadata) 
    VALUES('delete', old.id, old.path, old.text_content, old.metadata);
    INSERT INTO archive_entries_fts(rowid, path, text_content, metadata) 
    VALUES (new.id, new.path, new.text_content, new.metadata);
END;
"""

# Performance Indexes

PERFORMANCE_INDEXES = """
-- Archives indexes
CREATE INDEX IF NOT EXISTS idx_archives_file_hash ON archives (file_hash);
CREATE INDEX IF NOT EXISTS idx_archives_file_path ON archives (file_path);
CREATE INDEX IF NOT EXISTS idx_archives_parsed_at ON archives (parsed_at);
CREATE INDEX IF NOT EXISTS idx_archives_status ON archives (status);

-- Archive entries indexes  
CREATE INDEX IF NOT EXISTS idx_archive_entries_archive_id ON archive_entries (archive_id);
CREATE INDEX IF NOT EXISTS idx_archive_entries_path ON archive_entries (path);
CREATE INDEX IF NOT EXISTS idx_archive_entries_content_type ON archive_entries (content_type);
CREATE INDEX IF NOT EXISTS idx_archive_entries_content_hash ON archive_entries (content_hash);

-- Articles indexes
CREATE INDEX IF NOT EXISTS idx_articles_archive_id ON articles (archive_id);
CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles (slug);
CREATE INDEX IF NOT EXISTS idx_articles_category_id ON articles (category_id);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles (status);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles (created_at);

-- Categories indexes
CREATE INDEX IF NOT EXISTS idx_categories_archive_id ON categories (archive_id);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories (slug);
CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories (parent_id);

-- Projects indexes
CREATE INDEX IF NOT EXISTS idx_projects_archive_id ON projects (archive_id);
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects (name);
"""

# Database configuration

DATABASE_PRAGMAS = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;
PRAGMA mmap_size = 268435456; -- 256MB
"""


@dataclass
class SchemaVersion:
    """Database schema version information."""
    version: int
    applied_at: datetime
    description: str


async def create_archive_schema(db_path: Path, config: Optional[ArchiveSchema] = None) -> None:
    """
    Create complete archive database schema.
    
    Args:
        db_path: Path to SQLite database file
        config: Schema configuration
        
    Raises:
        Document360Error: If schema creation fails
    """
    config = config or ArchiveSchema()
    
    logger.info(f"Creating archive schema at {db_path}")
    
    try:
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Configure database
            await _configure_database(cursor, config)
            
            # Create tables
            await _create_tables(cursor, config)
            
            # Create indexes
            if config.create_indexes:
                await _create_indexes(cursor)
            
            # Create FTS tables and triggers
            if config.enable_fts:
                await _create_fts_tables(cursor, config)
            
            # Record schema version
            await _record_schema_version(cursor, config.version)
            
            conn.commit()
            
        logger.info(f"Archive schema created successfully (version {config.version})")
        
    except Exception as e:
        error_msg = f"Failed to create archive schema: {e}"
        logger.error(error_msg)
        raise Document360Error(
            error_msg,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            context={'db_path': str(db_path)}
        )


async def _configure_database(cursor: sqlite3.Cursor, config: ArchiveSchema) -> None:
    """Configure database settings."""
    if config.enable_foreign_keys:
        cursor.execute("PRAGMA foreign_keys = ON")
    
    if config.enable_wal:
        cursor.execute("PRAGMA journal_mode = WAL")
    
    cursor.execute(f"PRAGMA synchronous = {config.synchronous}")
    cursor.execute(f"PRAGMA cache_size = {config.cache_size}")
    cursor.execute(f"PRAGMA page_size = {config.page_size}")
    cursor.execute("PRAGMA temp_store = memory")


async def _create_tables(cursor: sqlite3.Cursor, config: ArchiveSchema) -> None:
    """Create database tables."""
    tables = [
        SCHEMA_VERSION_TABLE,
        ARCHIVES_TABLE,
        ARCHIVE_ENTRIES_TABLE,
        ARTICLES_TABLE,
        CATEGORIES_TABLE,
        PROJECTS_TABLE
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)


async def _create_indexes(cursor: sqlite3.Cursor) -> None:
    """Create performance indexes."""
    cursor.executescript(PERFORMANCE_INDEXES)


async def _create_fts_tables(cursor: sqlite3.Cursor, config: ArchiveSchema) -> None:
    """Create FTS tables and triggers."""
    # Modify FTS table creation to use configured tokenizer
    fts_tables = [
        ARTICLES_FTS_TABLE.replace('unicode61', config.fts_tokenizer),
        ARCHIVE_ENTRIES_FTS_TABLE.replace('unicode61', config.fts_tokenizer)
    ]
    
    for fts_table in fts_tables:
        cursor.execute(fts_table)
    
    # Create FTS triggers
    cursor.executescript(ARTICLES_FTS_TRIGGERS)
    cursor.executescript(ARCHIVE_ENTRIES_FTS_TRIGGERS)


async def _record_schema_version(cursor: sqlite3.Cursor, version: int) -> None:
    """Record schema version in database."""
    cursor.execute(
        "INSERT OR REPLACE INTO schema_version (version, description) VALUES (?, ?)",
        (version, f"Archive schema version {version}")
    )


async def migrate_archive_schema(db_path: Path, target_version: int = 1) -> None:
    """
    Migrate archive database schema to target version.
    
    Args:
        db_path: Path to SQLite database file
        target_version: Target schema version
        
    Raises:
        Document360Error: If migration fails
    """
    logger.info(f"Migrating archive schema to version {target_version}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check current version
            current_version = await _get_current_schema_version(cursor)
            
            if current_version >= target_version:
                logger.info(f"Schema already at version {current_version}, no migration needed")
                return
            
            # Perform migration steps
            for version in range(current_version + 1, target_version + 1):
                await _migrate_to_version(cursor, version)
                await _record_schema_version(cursor, version)
            
            conn.commit()
            
        logger.info(f"Schema migration completed to version {target_version}")
        
    except Exception as e:
        error_msg = f"Schema migration failed: {e}"
        logger.error(error_msg)
        raise Document360Error(
            error_msg,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            context={'db_path': str(db_path), 'target_version': target_version}
        )


async def _get_current_schema_version(cursor: sqlite3.Cursor) -> int:
    """Get current schema version from database."""
    try:
        cursor.execute("SELECT MAX(version) FROM schema_version")
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except sqlite3.OperationalError:
        # Table doesn't exist, assume version 0
        return 0


async def _migrate_to_version(cursor: sqlite3.Cursor, version: int) -> None:
    """Migrate to specific schema version."""
    logger.info(f"Migrating to schema version {version}")
    
    # Add migration logic for different versions here
    if version == 1:
        # Version 1 is the initial schema, no migration needed
        pass
    else:
        logger.warning(f"No migration logic defined for version {version}")


async def get_schema_info(db_path: Path) -> Dict[str, Any]:
    """
    Get information about the database schema.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Dictionary with schema information
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get schema version
            version = await _get_current_schema_version(cursor)
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get FTS table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_fts' ORDER BY name")
            fts_tables = [row[0] for row in cursor.fetchall()]
            
            # Get index information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
            indexes = [row[0] for row in cursor.fetchall()]
            
            return {
                'version': version,
                'tables': tables,
                'fts_tables': fts_tables,
                'indexes': indexes,
                'db_path': str(db_path),
                'db_size': db_path.stat().st_size if db_path.exists() else 0
            }
            
    except Exception as e:
        logger.error(f"Failed to get schema info: {e}")
        return {'error': str(e)}