# this_file: external/int_folders/d361/src/d361/archive/parser.py
"""
Archive Parser for Document360 offline archives.

This module provides comprehensive parsing capabilities for Document360
offline documentation archives, including ZIP and tar.gz support,
metadata extraction, content analysis, and integration with the
SQLite indexing system.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, Iterator, BinaryIO
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field, validator

from ..core.models import Article, Category, ProjectVersion
from ..core.transformers import ModelTransformer
from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class ArchiveFormat(str, Enum):
    """Supported archive formats."""
    ZIP = "zip"
    TAR_GZ = "tar.gz"
    TAR = "tar"
    UNKNOWN = "unknown"


class ContentType(str, Enum):
    """Types of content found in archives."""
    ARTICLE = "article"
    CATEGORY = "category"
    PROJECT = "project"
    ASSET = "asset"
    METADATA = "metadata"
    UNKNOWN = "unknown"


@dataclass
class ArchiveEntry:
    """Represents a single entry in an archive."""
    path: str
    size: int
    modified_time: Optional[datetime] = None
    content_type: ContentType = ContentType.UNKNOWN
    mime_type: Optional[str] = None
    content: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ArchiveParserConfig(BaseModel):
    """Configuration for archive parsing operations."""
    
    # Archive processing
    supported_formats: Set[str] = Field(
        default_factory=lambda: {"zip", "tar.gz", "tar"},
        description="Supported archive formats"
    )
    
    max_archive_size: int = Field(
        default=500 * 1024 * 1024,  # 500MB
        ge=1024,
        description="Maximum archive size in bytes"
    )
    
    max_file_size: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        ge=1024,
        description="Maximum individual file size in bytes"
    )
    
    # Content extraction
    extract_text_content: bool = Field(
        default=True,
        description="Extract text content from files"
    )
    
    extract_metadata: bool = Field(
        default=True,
        description="Extract metadata from files"
    )
    
    content_encodings: List[str] = Field(
        default_factory=lambda: ["utf-8", "utf-16", "latin-1"],
        description="Encodings to try when decoding text content"
    )
    
    # File filtering
    include_patterns: List[str] = Field(
        default_factory=lambda: ["*.md", "*.html", "*.json", "*.txt"],
        description="File patterns to include"
    )
    
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [".*", "__*", "*.tmp", "*.log"],
        description="File patterns to exclude"
    )
    
    # Performance settings
    enable_compression: bool = Field(
        default=True,
        description="Enable content compression for storage"
    )
    
    batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Batch size for processing entries"
    )
    
    # Validation settings
    validate_json: bool = Field(
        default=True,
        description="Validate JSON content structure"
    )
    
    strict_validation: bool = Field(
        default=False,
        description="Enable strict validation of content structure"
    )


class ArchiveMetadata(BaseModel):
    """Metadata about a parsed archive."""
    
    # Basic information
    archive_path: Path = Field(..., description="Path to the archive file")
    archive_format: ArchiveFormat = Field(..., description="Archive format")
    file_size: int = Field(..., description="Archive file size in bytes")
    file_hash: str = Field(..., description="SHA256 hash of archive file")
    
    # Content statistics
    total_entries: int = Field(default=0, description="Total number of entries")
    processed_entries: int = Field(default=0, description="Successfully processed entries")
    failed_entries: int = Field(default=0, description="Failed to process entries")
    
    # Content breakdown
    articles_count: int = Field(default=0, description="Number of articles found")
    categories_count: int = Field(default=0, description="Number of categories found")
    assets_count: int = Field(default=0, description="Number of asset files found")
    
    # Processing metadata
    parsed_at: datetime = Field(default_factory=datetime.now, description="When archive was parsed")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time in seconds")
    
    # Archive structure
    root_directories: List[str] = Field(default_factory=list, description="Root level directories")
    file_extensions: Dict[str, int] = Field(default_factory=dict, description="File extensions and counts")
    
    # Validation results
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors encountered")
    validation_warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class ParsedArchive(BaseModel):
    """Complete parsed archive with metadata and content."""
    
    metadata: ArchiveMetadata = Field(..., description="Archive metadata")
    entries: List[ArchiveEntry] = Field(default_factory=list, description="Parsed archive entries")
    articles: List[Article] = Field(default_factory=list, description="Extracted articles")
    categories: List[Category] = Field(default_factory=list, description="Extracted categories") 
    projects: List[ProjectVersion] = Field(default_factory=list, description="Extracted projects")
    
    @property
    def total_content_size(self) -> int:
        """Calculate total size of all content."""
        return sum(len(entry.content or b"") for entry in self.entries)
    
    @property
    def success_rate(self) -> float:
        """Calculate processing success rate."""
        if self.metadata.total_entries == 0:
            return 1.0
        return self.metadata.processed_entries / self.metadata.total_entries


class ArchiveParser:
    """
    Parser for Document360 offline archives.
    
    Provides comprehensive parsing capabilities for ZIP and tar.gz archives
    containing Document360 documentation, with intelligent content extraction,
    metadata analysis, and integration with the d361 architecture.
    """
    
    def __init__(self, config: Optional[ArchiveParserConfig] = None):
        """
        Initialize the archive parser.
        
        Args:
            config: Parser configuration
        """
        self.config = config or ArchiveParserConfig()
        self.transformer = ModelTransformer()
        
        logger.info(
            f"ArchiveParser initialized",
            supported_formats=list(self.config.supported_formats),
            max_size=self.config.max_archive_size
        )
    
    async def parse_archive(self, archive_path: Union[str, Path]) -> ParsedArchive:
        """
        Parse a Document360 archive file.
        
        Args:
            archive_path: Path to the archive file
            
        Returns:
            Parsed archive with content and metadata
            
        Raises:
            Document360Error: If parsing fails
        """
        archive_path = Path(archive_path)
        start_time = datetime.now()
        
        logger.info(f"Starting archive parsing: {archive_path}")
        
        # Validate archive file
        await self._validate_archive_file(archive_path)
        
        # Determine archive format
        archive_format = self._detect_archive_format(archive_path)
        
        # Calculate file hash
        file_hash = await self._calculate_file_hash(archive_path)
        
        # Initialize metadata
        metadata = ArchiveMetadata(
            archive_path=archive_path,
            archive_format=archive_format,
            file_size=archive_path.stat().st_size,
            file_hash=file_hash
        )
        
        try:
            # Parse archive contents
            entries = await self._parse_archive_contents(archive_path, archive_format, metadata)
            
            # Extract structured data
            articles, categories, projects = await self._extract_structured_data(entries)
            
            # Update metadata
            processing_time = (datetime.now() - start_time).total_seconds()
            metadata.processing_time_seconds = processing_time
            metadata.processed_entries = len(entries)
            metadata.articles_count = len(articles)
            metadata.categories_count = len(categories)
            
            parsed_archive = ParsedArchive(
                metadata=metadata,
                entries=entries,
                articles=articles,
                categories=categories,
                projects=projects
            )
            
            logger.info(
                f"Archive parsing completed successfully",
                entries=len(entries),
                articles=len(articles),
                categories=len(categories),
                processing_time=processing_time
            )
            
            return parsed_archive
            
        except Exception as e:
            error_msg = f"Failed to parse archive {archive_path}: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH,
                context={'archive_path': str(archive_path), 'format': archive_format}
            )
    
    async def _validate_archive_file(self, archive_path: Path) -> None:
        """Validate archive file before processing."""
        if not archive_path.exists():
            raise Document360Error(
                f"Archive file not found: {archive_path}",
                category=ErrorCategory.NOT_FOUND,
                severity=ErrorSeverity.HIGH
            )
        
        if not archive_path.is_file():
            raise Document360Error(
                f"Archive path is not a file: {archive_path}",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH
            )
        
        file_size = archive_path.stat().st_size
        if file_size > self.config.max_archive_size:
            raise Document360Error(
                f"Archive file too large: {file_size} bytes (max: {self.config.max_archive_size})",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH,
                context={'file_size': file_size, 'max_size': self.config.max_archive_size}
            )
    
    def _detect_archive_format(self, archive_path: Path) -> ArchiveFormat:
        """Detect archive format from file extension and content."""
        suffix = archive_path.suffix.lower()
        
        if suffix == ".zip":
            return ArchiveFormat.ZIP
        elif archive_path.name.endswith(".tar.gz"):
            return ArchiveFormat.TAR_GZ
        elif suffix == ".tar":
            return ArchiveFormat.TAR
        
        # Try to detect by content
        try:
            if zipfile.is_zipfile(archive_path):
                return ArchiveFormat.ZIP
            elif tarfile.is_tarfile(archive_path):
                return ArchiveFormat.TAR_GZ if archive_path.name.endswith(".gz") else ArchiveFormat.TAR
        except Exception:
            pass
        
        return ArchiveFormat.UNKNOWN
    
    async def _calculate_file_hash(self, archive_path: Path) -> str:
        """Calculate SHA256 hash of archive file."""
        hash_sha256 = hashlib.sha256()
        
        with open(archive_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _parse_archive_contents(
        self, 
        archive_path: Path, 
        archive_format: ArchiveFormat,
        metadata: ArchiveMetadata
    ) -> List[ArchiveEntry]:
        """Parse contents of archive file."""
        entries = []
        
        if archive_format == ArchiveFormat.ZIP:
            entries = await self._parse_zip_archive(archive_path, metadata)
        elif archive_format in [ArchiveFormat.TAR, ArchiveFormat.TAR_GZ]:
            entries = await self._parse_tar_archive(archive_path, metadata)
        else:
            raise Document360Error(
                f"Unsupported archive format: {archive_format}",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH
            )
        
        return entries
    
    async def _parse_zip_archive(self, archive_path: Path, metadata: ArchiveMetadata) -> List[ArchiveEntry]:
        """Parse ZIP archive contents."""
        entries = []
        
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_file:
                file_list = zip_file.filelist
                metadata.total_entries = len(file_list)
                
                for zip_info in file_list:
                    # Skip directories
                    if zip_info.is_dir():
                        continue
                    
                    # Check file size
                    if zip_info.file_size > self.config.max_file_size:
                        logger.warning(f"Skipping large file: {zip_info.filename} ({zip_info.file_size} bytes)")
                        continue
                    
                    # Apply filters
                    if not self._should_include_file(zip_info.filename):
                        continue
                    
                    try:
                        # Extract file content
                        content = zip_file.read(zip_info.filename)
                        
                        # Create archive entry
                        entry = ArchiveEntry(
                            path=zip_info.filename,
                            size=zip_info.file_size,
                            modified_time=datetime(*zip_info.date_time),
                            content=content,
                            mime_type=mimetypes.guess_type(zip_info.filename)[0]
                        )
                        
                        # Analyze content
                        await self._analyze_entry_content(entry)
                        
                        entries.append(entry)
                        
                    except Exception as e:
                        logger.warning(f"Failed to process {zip_info.filename}: {e}")
                        metadata.failed_entries += 1
                        
        except Exception as e:
            raise Document360Error(
                f"Failed to parse ZIP archive: {e}",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH
            )
        
        return entries
    
    async def _parse_tar_archive(self, archive_path: Path, metadata: ArchiveMetadata) -> List[ArchiveEntry]:
        """Parse TAR/TAR.GZ archive contents."""
        entries = []
        
        try:
            with tarfile.open(archive_path, 'r:*') as tar_file:
                members = tar_file.getmembers()
                metadata.total_entries = len(members)
                
                for tar_info in members:
                    # Skip directories and special files
                    if not tar_info.isfile():
                        continue
                    
                    # Check file size
                    if tar_info.size > self.config.max_file_size:
                        logger.warning(f"Skipping large file: {tar_info.name} ({tar_info.size} bytes)")
                        continue
                    
                    # Apply filters
                    if not self._should_include_file(tar_info.name):
                        continue
                    
                    try:
                        # Extract file content
                        extracted_file = tar_file.extractfile(tar_info)
                        if extracted_file is None:
                            continue
                            
                        content = extracted_file.read()
                        
                        # Create archive entry
                        entry = ArchiveEntry(
                            path=tar_info.name,
                            size=tar_info.size,
                            modified_time=datetime.fromtimestamp(tar_info.mtime),
                            content=content,
                            mime_type=mimetypes.guess_type(tar_info.name)[0]
                        )
                        
                        # Analyze content
                        await self._analyze_entry_content(entry)
                        
                        entries.append(entry)
                        
                    except Exception as e:
                        logger.warning(f"Failed to process {tar_info.name}: {e}")
                        metadata.failed_entries += 1
                        
        except Exception as e:
            raise Document360Error(
                f"Failed to parse TAR archive: {e}",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH
            )
        
        return entries
    
    def _should_include_file(self, filename: str) -> bool:
        """Check if file should be included based on patterns."""
        import fnmatch
        
        # Check exclude patterns first
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return False
        
        # Check include patterns
        if not self.config.include_patterns:
            return True
            
        for pattern in self.config.include_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        
        return False
    
    async def _analyze_entry_content(self, entry: ArchiveEntry) -> None:
        """Analyze entry content to determine type and extract metadata."""
        if not entry.content:
            return
        
        # Try to decode text content
        text_content = None
        if self.config.extract_text_content:
            text_content = await self._decode_content(entry.content)
            entry.metadata['text_content'] = text_content
        
        # Determine content type
        entry.content_type = self._determine_content_type(entry.path, text_content)
        
        # Extract specific metadata based on content type
        if entry.content_type == ContentType.ARTICLE and text_content:
            await self._extract_article_metadata(entry, text_content)
        elif entry.content_type == ContentType.METADATA and text_content:
            await self._extract_json_metadata(entry, text_content)
    
    async def _decode_content(self, content: bytes) -> Optional[str]:
        """Decode binary content to text."""
        for encoding in self.config.content_encodings:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        logger.warning("Failed to decode content with any supported encoding")
        return None
    
    def _determine_content_type(self, path: str, text_content: Optional[str]) -> ContentType:
        """Determine content type based on path and content."""
        path_lower = path.lower()
        
        if path_lower.endswith(('.md', '.markdown')):
            return ContentType.ARTICLE
        elif path_lower.endswith('.json'):
            return ContentType.METADATA
        elif 'category' in path_lower:
            return ContentType.CATEGORY
        elif 'project' in path_lower:
            return ContentType.PROJECT
        elif path_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.js')):
            return ContentType.ASSET
        
        return ContentType.UNKNOWN
    
    async def _extract_article_metadata(self, entry: ArchiveEntry, content: str) -> None:
        """Extract metadata from article content."""
        # Look for frontmatter or metadata sections
        lines = content.split('\n')
        metadata = {}
        
        # Simple frontmatter extraction (YAML-like)
        if lines and lines[0].strip() == '---':
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break
            
            if frontmatter_end > 0:
                try:
                    frontmatter = '\n'.join(lines[1:frontmatter_end])
                    # Simple key-value parsing (could be enhanced with proper YAML)
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()
                except Exception as e:
                    logger.warning(f"Failed to parse frontmatter: {e}")
        
        entry.metadata.update(metadata)
    
    async def _extract_json_metadata(self, entry: ArchiveEntry, content: str) -> None:
        """Extract metadata from JSON content."""
        try:
            json_data = json.loads(content)
            entry.metadata['json_data'] = json_data
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON in {entry.path}: {e}")
    
    async def _extract_structured_data(
        self, 
        entries: List[ArchiveEntry]
    ) -> tuple[List[Article], List[Category], List[ProjectVersion]]:
        """Extract structured data objects from parsed entries."""
        articles = []
        categories = []
        projects = []
        
        for entry in entries:
            try:
                if entry.content_type == ContentType.ARTICLE:
                    article = await self._create_article_from_entry(entry)
                    if article:
                        articles.append(article)
                        
                elif entry.content_type == ContentType.CATEGORY:
                    category = await self._create_category_from_entry(entry) 
                    if category:
                        categories.append(category)
                        
                elif entry.content_type == ContentType.PROJECT:
                    project = await self._create_project_from_entry(entry)
                    if project:
                        projects.append(project)
                        
            except Exception as e:
                logger.warning(f"Failed to create structured data from {entry.path}: {e}")
        
        return articles, categories, projects
    
    async def _create_article_from_entry(self, entry: ArchiveEntry) -> Optional[Article]:
        """Create Article object from archive entry."""
        if not entry.metadata.get('text_content'):
            return None
        
        try:
            # Extract basic information
            title = entry.metadata.get('title', Path(entry.path).stem)
            content = entry.metadata['text_content']
            
            # Create article using transformer
            article_data = {
                'id': entry.metadata.get('id', hash(entry.path) % (10**10)),
                'title': title,
                'content': content,
                'slug': entry.metadata.get('slug', title.lower().replace(' ', '-')),
                'category_id': entry.metadata.get('category_id'),
                'status': entry.metadata.get('status', 'published'),
                'created_at': entry.modified_time or datetime.now(),
                'updated_at': entry.modified_time or datetime.now()
            }
            
            return self.transformer.from_archive_metadata(article_data, Article)
            
        except Exception as e:
            logger.warning(f"Failed to create article from {entry.path}: {e}")
            return None
    
    async def _create_category_from_entry(self, entry: ArchiveEntry) -> Optional[Category]:
        """Create Category object from archive entry."""
        # Implementation for category extraction
        # This would be enhanced based on actual Document360 archive structure
        return None
    
    async def _create_project_from_entry(self, entry: ArchiveEntry) -> Optional[ProjectVersion]:
        """Create ProjectVersion object from archive entry."""
        # Implementation for project extraction
        # This would be enhanced based on actual Document360 archive structure
        return None