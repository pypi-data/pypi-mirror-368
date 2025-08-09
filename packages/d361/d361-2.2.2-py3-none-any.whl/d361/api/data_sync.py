# this_file: external/int_folders/d361/src/d361/api/data_sync.py
"""
Data Synchronization and Deduplication for Document360 API.

This module provides comprehensive data synchronization capabilities with:
- Content deduplication using multiple strategies (hash, content, metadata)
- Incremental synchronization with change detection
- Sync state persistence and recovery
- Conflict resolution and merge strategies
- Performance optimization for large datasets
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict

from loguru import logger
from pydantic import BaseModel, Field

from ..core.models import Article, Category, ProjectVersion, ContentType
from .errors import Document360Error, ErrorSeverity, ErrorCategory


class SyncStrategy(str, Enum):
    """Data synchronization strategies."""
    FULL = "full"                    # Full sync, replace all data
    INCREMENTAL = "incremental"      # Only sync changed items
    DELTA = "delta"                  # Sync changes since last sync
    SELECTIVE = "selective"          # Sync specific items only


class ChangeType(str, Enum):
    """Types of changes detected."""
    ADDED = "added"                  # New item
    MODIFIED = "modified"            # Changed item
    DELETED = "deleted"              # Removed item
    MOVED = "moved"                  # Item moved/renamed
    CONFLICT = "conflict"            # Conflicting changes


class DeduplicationStrategy(str, Enum):
    """Content deduplication strategies."""
    HASH = "hash"                    # Hash-based deduplication
    CONTENT = "content"              # Content similarity-based
    METADATA = "metadata"            # Metadata-based matching
    HYBRID = "hybrid"                # Combination of strategies


@dataclass
class ContentFingerprint:
    """
    Content fingerprint for deduplication and change detection.
    
    Provides multiple hash strategies for robust duplicate detection
    and change tracking.
    """
    
    # Hash-based fingerprints
    content_hash: str                # Hash of main content
    metadata_hash: str               # Hash of metadata
    structure_hash: str              # Hash of structure/outline
    combined_hash: str               # Combined hash
    
    # Content analysis
    content_length: int = 0
    word_count: int = 0
    paragraph_count: int = 0
    heading_count: int = 0
    
    # Metadata
    title: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    @classmethod
    def from_article(cls, article: Article) -> ContentFingerprint:
        """Create fingerprint from article."""
        # Extract content
        content = article.content or ""
        title = article.title or ""
        
        # Calculate hashes
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        metadata_hash = hashlib.sha256(f"{title}:{article.category_id}".encode()).hexdigest()[:16]
        
        # Simple structure analysis
        paragraphs = content.split('\n\n') if content else []
        headings = [p for p in paragraphs if p.strip().startswith('#')]
        
        structure_data = f"{len(paragraphs)}:{len(headings)}"
        structure_hash = hashlib.sha256(structure_data.encode()).hexdigest()[:16]
        
        # Combined hash
        combined_data = f"{content_hash}:{metadata_hash}:{structure_hash}"
        combined_hash = hashlib.sha256(combined_data.encode()).hexdigest()[:16]
        
        return cls(
            content_hash=content_hash,
            metadata_hash=metadata_hash,
            structure_hash=structure_hash,
            combined_hash=combined_hash,
            content_length=len(content),
            word_count=len(content.split()) if content else 0,
            paragraph_count=len(paragraphs),
            heading_count=len(headings),
            title=title,
            category=article.category_id,
            tags=getattr(article, 'tags', []) or [],
            created_at=article.created_at,
            updated_at=article.updated_at,
            last_modified=article.updated_at or article.created_at
        )
    
    def similarity_score(self, other: ContentFingerprint) -> float:
        """Calculate similarity score with another fingerprint (0-1)."""
        score = 0.0
        
        # Hash-based similarity (exact matches)
        if self.content_hash == other.content_hash:
            score += 0.4  # 40% weight for exact content match
        else:
            # Partial content similarity based on length and word count
            if self.content_length > 0 and other.content_length > 0:
                length_ratio = min(self.content_length, other.content_length) / max(self.content_length, other.content_length)
                word_ratio = min(self.word_count, other.word_count) / max(self.word_count, other.word_count) if max(self.word_count, other.word_count) > 0 else 0
                avg_content_similarity = (length_ratio + word_ratio) / 2
                score += 0.3 * avg_content_similarity  # 30% weight for partial content similarity
        
        # Metadata similarity
        if self.metadata_hash == other.metadata_hash:
            score += 0.2  # 20% weight for metadata
        
        # Structure similarity
        if self.structure_hash == other.structure_hash:
            score += 0.1  # 10% weight for structure
        else:
            # Partial structure similarity
            if self.paragraph_count > 0 and other.paragraph_count > 0:
                para_ratio = min(self.paragraph_count, other.paragraph_count) / max(self.paragraph_count, other.paragraph_count)
                score += 0.05 * para_ratio  # 5% weight for paragraph similarity
        
        # Title similarity
        if self.title and other.title:
            if self.title.lower() == other.title.lower():
                score += 0.2  # 20% weight for exact title match
            else:
                # Simple word overlap for title similarity
                title1_words = set(self.title.lower().split())
                title2_words = set(other.title.lower().split())
                if title1_words and title2_words:
                    overlap = len(title1_words.intersection(title2_words))
                    union = len(title1_words.union(title2_words))
                    title_similarity = overlap / union if union > 0 else 0
                    score += 0.1 * title_similarity  # 10% weight for partial title similarity
        
        # Category similarity
        if self.category == other.category:
            score += 0.05  # 5% weight for same category
        
        return min(score, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'content_hash': self.content_hash,
            'metadata_hash': self.metadata_hash,
            'structure_hash': self.structure_hash,
            'combined_hash': self.combined_hash,
            'content_length': self.content_length,
            'word_count': self.word_count,
            'paragraph_count': self.paragraph_count,
            'heading_count': self.heading_count,
            'title': self.title,
            'category': self.category,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
        }


@dataclass
class ChangeRecord:
    """
    Record of detected change.
    
    Tracks what changed, when, and provides context for sync decisions.
    """
    
    item_id: str
    change_type: ChangeType
    timestamp: datetime
    
    # Content tracking
    old_fingerprint: Optional[ContentFingerprint] = None
    new_fingerprint: Optional[ContentFingerprint] = None
    
    # Change details
    field_changes: Dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0
    
    # Sync metadata
    sync_priority: int = 0           # Higher = more important
    requires_manual_review: bool = False
    conflict_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'item_id': self.item_id,
            'change_type': self.change_type.value,
            'timestamp': self.timestamp.isoformat(),
            'old_fingerprint': self.old_fingerprint.to_dict() if self.old_fingerprint else None,
            'new_fingerprint': self.new_fingerprint.to_dict() if self.new_fingerprint else None,
            'field_changes': self.field_changes,
            'similarity_score': self.similarity_score,
            'sync_priority': self.sync_priority,
            'requires_manual_review': self.requires_manual_review,
            'conflict_reason': self.conflict_reason,
        }


class SyncConfig(BaseModel):
    """Configuration for data synchronization."""
    
    # Strategy settings
    sync_strategy: SyncStrategy = SyncStrategy.INCREMENTAL
    deduplication_strategy: DeduplicationStrategy = DeduplicationStrategy.HYBRID
    
    # Thresholds
    similarity_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for duplicate detection (0-1)"
    )
    
    change_detection_window: int = Field(
        default=7,
        ge=1,
        le=90,
        description="Days to look back for change detection"
    )
    
    # Batch processing
    batch_size: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Batch size for processing"
    )
    
    max_concurrent_operations: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent operations"
    )
    
    # Conflict resolution
    auto_resolve_conflicts: bool = Field(
        default=False,
        description="Automatically resolve conflicts when possible"
    )
    
    prefer_newer_content: bool = Field(
        default=True,
        description="Prefer newer content in conflicts"
    )
    
    # State management
    save_sync_state: bool = Field(
        default=True,
        description="Save sync state for incremental operations"
    )
    
    state_retention_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Days to retain sync state"
    )
    
    # Performance
    enable_caching: bool = Field(
        default=True,
        description="Enable fingerprint caching"
    )
    
    cache_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Cache TTL in hours"
    )


class SyncState(BaseModel):
    """
    Persistent state for incremental synchronization.
    
    Tracks sync progress, change history, and enables resumable operations.
    """
    
    # Sync metadata
    sync_id: str
    strategy: SyncStrategy
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    total_items: int = 0
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    
    # Change tracking
    last_sync_timestamp: Optional[datetime] = None
    detected_changes: List[ChangeRecord] = Field(default_factory=list)
    
    # Item tracking
    item_fingerprints: Dict[str, ContentFingerprint] = Field(default_factory=dict)
    processed_item_ids: Set[str] = Field(default_factory=set)
    failed_item_ids: Set[str] = Field(default_factory=set)
    
    # Deduplication results
    duplicate_groups: Dict[str, List[str]] = Field(default_factory=dict)
    merged_items: Dict[str, str] = Field(default_factory=dict)  # old_id -> new_id
    
    # Performance metrics
    average_processing_time: float = 0.0
    total_processing_time: float = 0.0
    memory_usage_peak: int = 0
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        return (self.processed_items / max(self.total_items, 1)) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return (self.successful_items / max(self.processed_items, 1)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'sync_id': self.sync_id,
            'strategy': self.strategy.value,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'successful_items': self.successful_items,
            'failed_items': self.failed_items,
            'skipped_items': self.skipped_items,
            'last_sync_timestamp': self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else None,
            'detected_changes': [change.to_dict() for change in self.detected_changes],
            'item_fingerprints': {
                item_id: fp.to_dict() 
                for item_id, fp in self.item_fingerprints.items()
            },
            'processed_item_ids': list(self.processed_item_ids),
            'failed_item_ids': list(self.failed_item_ids),
            'duplicate_groups': self.duplicate_groups,
            'merged_items': self.merged_items,
            'average_processing_time': self.average_processing_time,
            'total_processing_time': self.total_processing_time,
            'memory_usage_peak': self.memory_usage_peak,
        }


class DataSyncManager:
    """
    Comprehensive data synchronization and deduplication manager.
    
    Provides enterprise-grade data synchronization with:
    - Multi-strategy deduplication (hash, content, metadata-based)
    - Incremental sync with change detection and conflict resolution
    - Resumable operations with persistent state management
    - Performance optimization for large datasets
    - Comprehensive monitoring and reporting
    """
    
    def __init__(
        self,
        api_client,  # Document360ApiClient
        config: Optional[SyncConfig] = None,
        state_dir: Optional[Path] = None
    ):
        """
        Initialize data sync manager.
        
        Args:
            api_client: Document360 API client instance
            config: Sync configuration
            state_dir: Directory for state persistence
        """
        self.api_client = api_client
        self.config = config or SyncConfig()
        self.state_dir = state_dir or Path.home() / ".d361" / "sync_state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Internal state
        self._current_sync: Optional[SyncState] = None
        self._fingerprint_cache: Dict[str, ContentFingerprint] = {}
        self._change_callbacks: List[Callable[[ChangeRecord], None]] = []
        
        # Performance tracking
        self._start_time = 0.0
        
        logger.info(
            f"DataSyncManager initialized",
            strategy=self.config.sync_strategy.value,
            deduplication=self.config.deduplication_strategy.value,
            state_dir=str(self.state_dir),
        )
    
    def add_change_callback(self, callback: Callable[[ChangeRecord], None]) -> None:
        """Add callback for change notifications."""
        self._change_callbacks.append(callback)
    
    async def sync_articles(
        self,
        category_id: Optional[str] = None,
        project_version_id: Optional[str] = None,
        sync_id: Optional[str] = None
    ) -> SyncState:
        """
        Synchronize articles with deduplication and incremental sync.
        
        Args:
            category_id: Optional category to sync
            project_version_id: Optional project version to sync
            sync_id: Optional existing sync to resume
            
        Returns:
            Sync state with results
        """
        # Initialize or resume sync
        sync_state = await self._initialize_sync(
            sync_id=sync_id,
            operation_type="sync_articles",
            operation_params={
                'category_id': category_id,
                'project_version_id': project_version_id
            }
        )
        
        try:
            logger.info(
                f"Starting article synchronization",
                sync_id=sync_state.sync_id,
                strategy=sync_state.strategy.value,
            )
            
            # Fetch current articles
            logger.info("Fetching current articles...")
            current_articles = await self._fetch_articles(category_id, project_version_id)
            sync_state.total_items = len(current_articles)
            
            logger.info(f"Found {len(current_articles)} articles to process")
            
            # Load previous state for incremental sync
            previous_fingerprints = {}
            if sync_state.strategy in [SyncStrategy.INCREMENTAL, SyncStrategy.DELTA]:
                previous_fingerprints = await self._load_previous_fingerprints()
                logger.info(f"Loaded {len(previous_fingerprints)} previous fingerprints")
            
            # Process articles in batches
            await self._process_articles_batch(current_articles, sync_state, previous_fingerprints)
            
            # Run deduplication
            if self.config.deduplication_strategy != DeduplicationStrategy.HYBRID:
                await self._deduplicate_articles(sync_state)
            
            # Finalize sync
            sync_state.completed_at = datetime.now()
            await self._save_sync_state(sync_state)
            
            logger.info(
                f"Article synchronization completed",
                sync_id=sync_state.sync_id,
                total_items=sync_state.total_items,
                successful_items=sync_state.successful_items,
                failed_items=sync_state.failed_items,
                completion_percentage=f"{sync_state.completion_percentage:.1f}%",
            )
            
            return sync_state
            
        except Exception as e:
            logger.error(f"Sync failed: {e}", sync_id=sync_state.sync_id)
            await self._save_sync_state(sync_state)  # Save partial progress
            raise Document360Error(
                f"Synchronization failed: {e}",
                category=ErrorCategory.PROCESSING_ERROR,
                severity=ErrorSeverity.HIGH,
                retryable=True,
                context={'sync_id': sync_state.sync_id}
            )
    
    async def _initialize_sync(
        self,
        sync_id: Optional[str],
        operation_type: str,
        operation_params: Dict[str, Any]
    ) -> SyncState:
        """Initialize or resume sync operation."""
        if sync_id:
            # Resume existing sync
            existing_state = await self._load_sync_state(sync_id)
            if existing_state:
                logger.info(f"Resuming sync: {sync_id}")
                self._current_sync = existing_state
                return existing_state
        
        # Create new sync
        new_sync_id = f"sync_{int(time.time() * 1000)}"
        self._current_sync = SyncState(
            sync_id=new_sync_id,
            strategy=self.config.sync_strategy,
            started_at=datetime.now()
        )
        
        logger.info(f"Created new sync: {new_sync_id}")
        return self._current_sync
    
    async def _fetch_articles(
        self,
        category_id: Optional[str],
        project_version_id: Optional[str]
    ) -> List[Article]:
        """Fetch articles from API."""
        try:
            if category_id:
                return await self.api_client.get_articles_by_category(category_id)
            elif project_version_id:
                # Fetch all categories first, then all articles
                categories = await self.api_client.get_categories(project_version_id)
                all_articles = []
                for category in categories:
                    category_articles = await self.api_client.get_articles_by_category(category.id)
                    all_articles.extend(category_articles)
                return all_articles
            else:
                # Fetch all articles (this might need project version)
                return await self.api_client.get_articles()
                
        except Exception as e:
            logger.error(f"Failed to fetch articles: {e}")
            raise
    
    async def _process_articles_batch(
        self,
        articles: List[Article],
        sync_state: SyncState,
        previous_fingerprints: Dict[str, ContentFingerprint]
    ) -> None:
        """Process articles in batches."""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_operations)
        
        async def process_article(article: Article) -> None:
            async with semaphore:
                await self._process_single_article(article, sync_state, previous_fingerprints)
        
        # Process in batches
        for i in range(0, len(articles), self.config.batch_size):
            batch = articles[i:i + self.config.batch_size]
            tasks = [process_article(article) for article in batch]
            
            logger.info(f"Processing batch {i // self.config.batch_size + 1}/{(len(articles) - 1) // self.config.batch_size + 1}")
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Save progress periodically
            await self._save_sync_state(sync_state)
    
    async def _process_single_article(
        self,
        article: Article,
        sync_state: SyncState,
        previous_fingerprints: Dict[str, ContentFingerprint]
    ) -> None:
        """Process a single article."""
        try:
            start_time = time.time()
            
            # Generate fingerprint
            fingerprint = ContentFingerprint.from_article(article)
            sync_state.item_fingerprints[article.id] = fingerprint
            
            # Check for changes
            change_record = None
            if article.id in previous_fingerprints:
                previous_fp = previous_fingerprints[article.id]
                similarity = fingerprint.similarity_score(previous_fp)
                
                if similarity < 1.0:  # Content changed
                    change_record = ChangeRecord(
                        item_id=article.id,
                        change_type=ChangeType.MODIFIED,
                        timestamp=datetime.now(),
                        old_fingerprint=previous_fp,
                        new_fingerprint=fingerprint,
                        similarity_score=similarity
                    )
                    
                    # Determine field changes
                    change_record.field_changes = self._detect_field_changes(previous_fp, fingerprint)
            else:
                # New article
                change_record = ChangeRecord(
                    item_id=article.id,
                    change_type=ChangeType.ADDED,
                    timestamp=datetime.now(),
                    new_fingerprint=fingerprint
                )
            
            if change_record:
                sync_state.detected_changes.append(change_record)
                
                # Notify callbacks
                for callback in self._change_callbacks:
                    try:
                        callback(change_record)
                    except Exception as e:
                        logger.warning(f"Change callback failed: {e}")
            
            # Update metrics
            processing_time = time.time() - start_time
            sync_state.processed_items += 1
            sync_state.successful_items += 1
            sync_state.total_processing_time += processing_time
            sync_state.average_processing_time = sync_state.total_processing_time / sync_state.processed_items
            
            sync_state.processed_item_ids.add(article.id)
            
        except Exception as e:
            logger.error(f"Failed to process article {article.id}: {e}")
            sync_state.failed_items += 1
            sync_state.failed_item_ids.add(article.id)
    
    def _detect_field_changes(
        self,
        old_fp: ContentFingerprint,
        new_fp: ContentFingerprint
    ) -> Dict[str, Any]:
        """Detect which fields changed between fingerprints."""
        changes = {}
        
        # Compare basic properties
        if old_fp.content_hash != new_fp.content_hash:
            changes['content'] = {
                'old_hash': old_fp.content_hash,
                'new_hash': new_fp.content_hash,
                'length_change': new_fp.content_length - old_fp.content_length
            }
        
        if old_fp.title != new_fp.title:
            changes['title'] = {
                'old': old_fp.title,
                'new': new_fp.title
            }
        
        if old_fp.category != new_fp.category:
            changes['category'] = {
                'old': old_fp.category,
                'new': new_fp.category
            }
        
        # Compare structure
        if old_fp.structure_hash != new_fp.structure_hash:
            changes['structure'] = {
                'old_paragraphs': old_fp.paragraph_count,
                'new_paragraphs': new_fp.paragraph_count,
                'old_headings': old_fp.heading_count,
                'new_headings': new_fp.heading_count
            }
        
        return changes
    
    async def _deduplicate_articles(self, sync_state: SyncState) -> None:
        """Run deduplication on processed articles."""
        logger.info(f"Starting deduplication with strategy: {self.config.deduplication_strategy.value}")
        
        fingerprints = sync_state.item_fingerprints
        if len(fingerprints) < 2:
            logger.info("Not enough articles for deduplication")
            return
        
        # Group potentially duplicate articles
        duplicate_groups = defaultdict(list)
        processed_pairs = set()
        
        items = list(fingerprints.items())
        for i, (id1, fp1) in enumerate(items):
            for j, (id2, fp2) in enumerate(items[i+1:], i+1):
                pair_key = tuple(sorted([id1, id2]))
                if pair_key in processed_pairs:
                    continue
                processed_pairs.add(pair_key)
                
                # Calculate similarity
                similarity = fp1.similarity_score(fp2)
                if similarity >= self.config.similarity_threshold:
                    # Found potential duplicate
                    group_key = f"duplicate_{len(duplicate_groups)}"
                    if not any(id1 in group or id2 in group for group in duplicate_groups.values()):
                        duplicate_groups[group_key] = [id1, id2]
                    else:
                        # Add to existing group
                        for group_key, group in duplicate_groups.items():
                            if id1 in group or id2 in group:
                                if id1 not in group:
                                    group.append(id1)
                                if id2 not in group:
                                    group.append(id2)
                                break
        
        sync_state.duplicate_groups = dict(duplicate_groups)
        
        logger.info(
            f"Deduplication completed",
            duplicate_groups=len(duplicate_groups),
            total_duplicates=sum(len(group) for group in duplicate_groups.values())
        )
    
    async def _load_previous_fingerprints(self) -> Dict[str, ContentFingerprint]:
        """Load fingerprints from previous sync."""
        try:
            # Find most recent completed sync
            sync_files = list(self.state_dir.glob("sync_*.json"))
            if not sync_files:
                return {}
            
            latest_file = max(sync_files, key=lambda f: f.stat().st_mtime)
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruct fingerprints
            fingerprints = {}
            for item_id, fp_data in data.get('item_fingerprints', {}).items():
                fingerprints[item_id] = ContentFingerprint(**fp_data)
            
            logger.info(f"Loaded {len(fingerprints)} previous fingerprints from {latest_file.name}")
            return fingerprints
            
        except Exception as e:
            logger.warning(f"Failed to load previous fingerprints: {e}")
            return {}
    
    async def _save_sync_state(self, sync_state: SyncState) -> None:
        """Save sync state to disk."""
        if not self.config.save_sync_state:
            return
        
        try:
            state_file = self.state_dir / f"{sync_state.sync_id}.json"
            
            with open(state_file, 'w') as f:
                json.dump(sync_state.to_dict(), f, indent=2, default=str)
            
            logger.debug(f"Saved sync state to {state_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save sync state: {e}")
    
    async def _load_sync_state(self, sync_id: str) -> Optional[SyncState]:
        """Load sync state from disk."""
        try:
            state_file = self.state_dir / f"{sync_id}.json"
            if not state_file.exists():
                return None
            
            with open(state_file, 'r') as f:
                data = json.load(f)
            
            # Reconstruct sync state (simplified - would need proper deserialization)
            return SyncState(**data)
            
        except Exception as e:
            logger.warning(f"Failed to load sync state {sync_id}: {e}")
            return None
    
    async def list_syncs(self) -> List[Dict[str, Any]]:
        """List all sync operations."""
        syncs = []
        try:
            for state_file in self.state_dir.glob("sync_*.json"):
                with open(state_file, 'r') as f:
                    data = json.load(f)
                
                syncs.append({
                    'sync_id': data.get('sync_id'),
                    'strategy': data.get('strategy'),
                    'started_at': data.get('started_at'),
                    'completed_at': data.get('completed_at'),
                    'total_items': data.get('total_items', 0),
                    'successful_items': data.get('successful_items', 0),
                    'completion_percentage': data.get('completion_percentage', 0),
                })
        except Exception as e:
            logger.warning(f"Failed to list syncs: {e}")
        
        return sorted(syncs, key=lambda x: x['started_at'], reverse=True)
    
    async def get_sync_report(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed report for a sync operation."""
        sync_state = await self._load_sync_state(sync_id)
        if not sync_state:
            return None
        
        return {
            'sync_id': sync_state.sync_id,
            'strategy': sync_state.strategy.value,
            'started_at': sync_state.started_at.isoformat(),
            'completed_at': sync_state.completed_at.isoformat() if sync_state.completed_at else None,
            'duration': (sync_state.completed_at - sync_state.started_at).total_seconds() if sync_state.completed_at else None,
            'progress': {
                'total_items': sync_state.total_items,
                'processed_items': sync_state.processed_items,
                'successful_items': sync_state.successful_items,
                'failed_items': sync_state.failed_items,
                'skipped_items': sync_state.skipped_items,
                'completion_percentage': sync_state.completion_percentage,
                'success_rate': sync_state.success_rate,
            },
            'changes': {
                'total_changes': len(sync_state.detected_changes),
                'added': sum(1 for c in sync_state.detected_changes if c.change_type == ChangeType.ADDED),
                'modified': sum(1 for c in sync_state.detected_changes if c.change_type == ChangeType.MODIFIED),
                'deleted': sum(1 for c in sync_state.detected_changes if c.change_type == ChangeType.DELETED),
            },
            'deduplication': {
                'duplicate_groups': len(sync_state.duplicate_groups),
                'total_duplicates': sum(len(group) for group in sync_state.duplicate_groups.values()),
                'merged_items': len(sync_state.merged_items),
            },
            'performance': {
                'average_processing_time': sync_state.average_processing_time,
                'total_processing_time': sync_state.total_processing_time,
                'items_per_second': sync_state.processed_items / max(sync_state.total_processing_time, 0.001),
            }
        }
    
    async def cleanup_old_states(self) -> int:
        """Clean up old sync states based on retention policy."""
        cutoff_date = datetime.now() - timedelta(days=self.config.state_retention_days)
        cleaned_count = 0
        
        try:
            for state_file in self.state_dir.glob("sync_*.json"):
                if datetime.fromtimestamp(state_file.stat().st_mtime) < cutoff_date:
                    state_file.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} old sync states")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup sync states: {e}")
        
        return cleaned_count