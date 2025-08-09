# this_file: external/int_folders/d361/src/d361/scraping/deduplicator.py
"""
Content deduplication and similarity detection for scraped content.

This module provides comprehensive content deduplication capabilities with
multiple similarity detection algorithms, hash-based exact matching, and
intelligent duplicate identification optimized for Document360 content.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field, validator

from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class DuplicateStatus(str, Enum):
    """Status of duplicate detection."""
    UNIQUE = "unique"                # No duplicates found
    EXACT_DUPLICATE = "exact"        # Exact content match
    NEAR_DUPLICATE = "near"          # High similarity (>90%)
    SIMILAR = "similar"              # Moderate similarity (70-90%)
    RELATED = "related"              # Low similarity (50-70%)


class SimilarityAlgorithm(str, Enum):
    """Similarity detection algorithms."""
    EXACT_HASH = "exact_hash"        # Exact content hash matching
    CONTENT_HASH = "content_hash"    # Normalized content hash
    FUZZY_HASH = "fuzzy_hash"        # Fuzzy/ssdeep hashing
    JACCARD = "jaccard"              # Jaccard similarity
    COSINE = "cosine"                # Cosine similarity
    LEVENSHTEIN = "levenshtein"      # Edit distance
    SHINGLE = "shingle"              # N-gram shingles


@dataclass
class SimilarityScore:
    """Similarity score between two pieces of content."""
    algorithm: SimilarityAlgorithm
    score: float  # 0.0 to 1.0
    confidence: float  # Confidence in the score
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_duplicate(self) -> bool:
        """Check if score indicates duplicate content."""
        return self.score >= 0.9
    
    @property
    def is_similar(self) -> bool:
        """Check if score indicates similar content."""
        return self.score >= 0.7


@dataclass
class DuplicateGroup:
    """Group of duplicate or similar content items."""
    representative_id: str  # ID of the representative item
    item_ids: List[str]     # All items in the group
    similarity_scores: List[float]  # Similarity scores
    status: DuplicateStatus = DuplicateStatus.SIMILAR
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def size(self) -> int:
        """Number of items in the group."""
        return len(self.item_ids)
    
    @property
    def average_similarity(self) -> float:
        """Average similarity score in the group."""
        return sum(self.similarity_scores) / len(self.similarity_scores) if self.similarity_scores else 0.0


class DeduplicationConfig(BaseModel):
    """Configuration for content deduplication."""
    
    # Similarity thresholds
    exact_threshold: float = Field(
        default=1.0,
        ge=0.95,
        le=1.0,
        description="Threshold for exact duplicates"
    )
    
    near_duplicate_threshold: float = Field(
        default=0.9,
        ge=0.8,
        le=0.99,
        description="Threshold for near duplicates"
    )
    
    similar_threshold: float = Field(
        default=0.7,
        ge=0.5,
        le=0.89,
        description="Threshold for similar content"
    )
    
    related_threshold: float = Field(
        default=0.5,
        ge=0.3,
        le=0.69,
        description="Threshold for related content"
    )
    
    # Algorithm selection
    primary_algorithm: SimilarityAlgorithm = Field(
        default=SimilarityAlgorithm.CONTENT_HASH,
        description="Primary similarity algorithm"
    )
    
    secondary_algorithms: List[SimilarityAlgorithm] = Field(
        default=[SimilarityAlgorithm.JACCARD, SimilarityAlgorithm.SHINGLE],
        description="Additional algorithms for verification"
    )
    
    # Content processing
    normalize_content: bool = Field(
        default=True,
        description="Normalize content before comparison"
    )
    
    ignore_case: bool = Field(
        default=True,
        description="Ignore case when comparing"
    )
    
    ignore_whitespace: bool = Field(
        default=True,
        description="Ignore whitespace differences"
    )
    
    ignore_punctuation: bool = Field(
        default=False,
        description="Ignore punctuation differences"
    )
    
    # Performance settings
    min_content_length: int = Field(
        default=100,
        ge=10,
        description="Minimum content length to process"
    )
    
    max_comparisons: int = Field(
        default=10000,
        ge=100,
        description="Maximum pairwise comparisons"
    )
    
    batch_size: int = Field(
        default=1000,
        ge=10,
        description="Batch size for processing"
    )
    
    # Shingle settings (for n-gram similarity)
    shingle_size: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Size of n-gram shingles"
    )


class ContentDeduplicator:
    """
    Content deduplication with multiple similarity algorithms.
    
    Provides comprehensive content deduplication capabilities using various
    similarity detection methods, from exact hash matching to fuzzy similarity,
    with intelligent grouping and quality assessment for Document360 content.
    """
    
    def __init__(self, config: Optional[DeduplicationConfig] = None):
        """
        Initialize content deduplicator.
        
        Args:
            config: Deduplication configuration
        """
        self.config = config or DeduplicationConfig()
        self._content_cache: Dict[str, str] = {}
        self._hash_cache: Dict[str, str] = {}
        self._similarity_cache: Dict[Tuple[str, str], float] = {}
        
        logger.info(
            "ContentDeduplicator initialized",
            primary_algorithm=self.config.primary_algorithm.value,
            thresholds={
                "exact": self.config.exact_threshold,
                "near": self.config.near_duplicate_threshold,
                "similar": self.config.similar_threshold
            }
        )
    
    def find_duplicates(
        self, 
        content_items: Dict[str, str],
        return_groups: bool = True
    ) -> Union[List[DuplicateGroup], Dict[str, DuplicateStatus]]:
        """
        Find duplicate content in a collection.
        
        Args:
            content_items: Dictionary mapping item IDs to content
            return_groups: Whether to return duplicate groups or status dict
            
        Returns:
            Either list of duplicate groups or dict of item statuses
            
        Raises:
            Document360Error: If deduplication fails
        """
        try:
            logger.info(f"Finding duplicates in {len(content_items)} items")
            
            # Filter content by minimum length
            filtered_items = {
                item_id: content for item_id, content in content_items.items()
                if len(content.strip()) >= self.config.min_content_length
            }
            
            if len(filtered_items) != len(content_items):
                logger.info(f"Filtered to {len(filtered_items)} items after length check")
            
            # Cache normalized content
            self._cache_normalized_content(filtered_items)
            
            # Find similar pairs using primary algorithm
            similar_pairs = self._find_similar_pairs(filtered_items)
            
            # Verify with secondary algorithms if configured
            if self.config.secondary_algorithms:
                similar_pairs = self._verify_with_secondary_algorithms(
                    similar_pairs, filtered_items
                )
            
            # Group duplicates
            duplicate_groups = self._group_duplicates(similar_pairs)
            
            logger.info(
                f"Deduplication completed",
                total_items=len(content_items),
                processed_items=len(filtered_items),
                duplicate_groups=len(duplicate_groups),
                similar_pairs=len(similar_pairs)
            )
            
            if return_groups:
                return duplicate_groups
            else:
                return self._create_status_dict(duplicate_groups, filtered_items)
        
        except Exception as e:
            error_msg = f"Failed to find duplicates: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
    
    def calculate_similarity(
        self, 
        content1: str, 
        content2: str,
        algorithm: Optional[SimilarityAlgorithm] = None
    ) -> SimilarityScore:
        """
        Calculate similarity between two pieces of content.
        
        Args:
            content1: First content item
            content2: Second content item
            algorithm: Similarity algorithm to use
            
        Returns:
            Similarity score with metadata
        """
        algorithm = algorithm or self.config.primary_algorithm
        
        # Check cache first
        cache_key = (
            hashlib.md5(content1.encode()).hexdigest(),
            hashlib.md5(content2.encode()).hexdigest()
        )
        
        if cache_key in self._similarity_cache:
            cached_score = self._similarity_cache[cache_key]
            return SimilarityScore(
                algorithm=algorithm,
                score=cached_score,
                confidence=1.0,
                metadata={"cached": True}
            )
        
        # Normalize content
        norm_content1 = self._normalize_content(content1)
        norm_content2 = self._normalize_content(content2)
        
        # Calculate similarity based on algorithm
        if algorithm == SimilarityAlgorithm.EXACT_HASH:
            score = self._exact_hash_similarity(norm_content1, norm_content2)
            confidence = 1.0
        elif algorithm == SimilarityAlgorithm.CONTENT_HASH:
            score = self._content_hash_similarity(norm_content1, norm_content2)
            confidence = 1.0
        elif algorithm == SimilarityAlgorithm.JACCARD:
            score = self._jaccard_similarity(norm_content1, norm_content2)
            confidence = 0.8
        elif algorithm == SimilarityAlgorithm.SHINGLE:
            score = self._shingle_similarity(norm_content1, norm_content2)
            confidence = 0.85
        elif algorithm == SimilarityAlgorithm.LEVENSHTEIN:
            score = self._levenshtein_similarity(norm_content1, norm_content2)
            confidence = 0.7
        else:
            # Fallback to content hash
            score = self._content_hash_similarity(norm_content1, norm_content2)
            confidence = 0.9
        
        # Cache result
        self._similarity_cache[cache_key] = score
        
        return SimilarityScore(
            algorithm=algorithm,
            score=score,
            confidence=confidence,
            metadata={
                "content1_length": len(content1),
                "content2_length": len(content2),
                "normalized": True
            }
        )
    
    def _cache_normalized_content(self, content_items: Dict[str, str]) -> None:
        """Cache normalized content for efficiency."""
        for item_id, content in content_items.items():
            normalized = self._normalize_content(content)
            self._content_cache[item_id] = normalized
            
            # Also cache content hash
            content_hash = hashlib.sha256(normalized.encode()).hexdigest()
            self._hash_cache[item_id] = content_hash
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for comparison."""
        if not self.config.normalize_content:
            return content
        
        normalized = content
        
        # Convert to lowercase
        if self.config.ignore_case:
            normalized = normalized.lower()
        
        # Remove extra whitespace
        if self.config.ignore_whitespace:
            normalized = re.sub(r'\s+', ' ', normalized)
            normalized = normalized.strip()
        
        # Remove punctuation
        if self.config.ignore_punctuation:
            normalized = re.sub(r'[^\w\s]', '', normalized)
        
        return normalized
    
    def _find_similar_pairs(self, content_items: Dict[str, str]) -> List[Tuple[str, str, float]]:
        """Find similar pairs using the primary algorithm."""
        similar_pairs = []
        item_ids = list(content_items.keys())
        
        # Limit comparisons to prevent performance issues
        total_comparisons = len(item_ids) * (len(item_ids) - 1) // 2
        if total_comparisons > self.config.max_comparisons:
            logger.warning(
                f"Limiting comparisons from {total_comparisons} to {self.config.max_comparisons}"
            )
            # Use a sample of items
            import random
            sample_size = int((2 * self.config.max_comparisons) ** 0.5)
            item_ids = random.sample(item_ids, min(sample_size, len(item_ids)))
        
        # Compare all pairs
        for i, item_id1 in enumerate(item_ids):
            for item_id2 in item_ids[i + 1:]:
                similarity = self.calculate_similarity(
                    self._content_cache[item_id1],
                    self._content_cache[item_id2],
                    self.config.primary_algorithm
                )
                
                if similarity.score >= self.config.related_threshold:
                    similar_pairs.append((item_id1, item_id2, similarity.score))
        
        # Sort by similarity score (descending)
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return similar_pairs
    
    def _verify_with_secondary_algorithms(
        self, 
        similar_pairs: List[Tuple[str, str, float]],
        content_items: Dict[str, str]
    ) -> List[Tuple[str, str, float]]:
        """Verify similarity with secondary algorithms."""
        verified_pairs = []
        
        for item_id1, item_id2, primary_score in similar_pairs:
            secondary_scores = []
            
            for algorithm in self.config.secondary_algorithms:
                similarity = self.calculate_similarity(
                    self._content_cache[item_id1],
                    self._content_cache[item_id2],
                    algorithm
                )
                secondary_scores.append(similarity.score)
            
            # Use average of all scores
            if secondary_scores:
                average_score = (primary_score + sum(secondary_scores)) / (len(secondary_scores) + 1)
            else:
                average_score = primary_score
            
            # Only keep if average still meets threshold
            if average_score >= self.config.related_threshold:
                verified_pairs.append((item_id1, item_id2, average_score))
        
        return verified_pairs
    
    def _group_duplicates(self, similar_pairs: List[Tuple[str, str, float]]) -> List[DuplicateGroup]:
        """Group similar items into duplicate groups."""
        # Use Union-Find to group connected items
        parent = {}
        
        def find(x):
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # Group items based on similarity
        for item_id1, item_id2, score in similar_pairs:
            if score >= self.config.similar_threshold:
                union(item_id1, item_id2)
        
        # Collect groups
        groups = {}
        for item_id1, item_id2, score in similar_pairs:
            if score >= self.config.similar_threshold:
                root = find(item_id1)
                if root not in groups:
                    groups[root] = {
                        'items': set(),
                        'scores': []
                    }
                groups[root]['items'].add(item_id1)
                groups[root]['items'].add(item_id2)
                groups[root]['scores'].append(score)
        
        # Create DuplicateGroup objects
        duplicate_groups = []
        for root, group_data in groups.items():
            items = list(group_data['items'])
            scores = group_data['scores']
            
            if len(items) > 1:  # Only groups with multiple items
                # Determine status based on average score
                avg_score = sum(scores) / len(scores)
                
                if avg_score >= self.config.exact_threshold:
                    status = DuplicateStatus.EXACT_DUPLICATE
                elif avg_score >= self.config.near_duplicate_threshold:
                    status = DuplicateStatus.NEAR_DUPLICATE
                elif avg_score >= self.config.similar_threshold:
                    status = DuplicateStatus.SIMILAR
                else:
                    status = DuplicateStatus.RELATED
                
                duplicate_groups.append(DuplicateGroup(
                    representative_id=root,
                    item_ids=items,
                    similarity_scores=scores,
                    status=status
                ))
        
        return duplicate_groups
    
    def _create_status_dict(
        self, 
        duplicate_groups: List[DuplicateGroup],
        content_items: Dict[str, str]
    ) -> Dict[str, DuplicateStatus]:
        """Create status dictionary for all items."""
        status_dict = {}
        
        # Mark items in groups
        for group in duplicate_groups:
            for item_id in group.item_ids:
                status_dict[item_id] = group.status
        
        # Mark remaining items as unique
        for item_id in content_items.keys():
            if item_id not in status_dict:
                status_dict[item_id] = DuplicateStatus.UNIQUE
        
        return status_dict
    
    def _exact_hash_similarity(self, content1: str, content2: str) -> float:
        """Calculate exact hash similarity."""
        hash1 = hashlib.sha256(content1.encode()).hexdigest()
        hash2 = hashlib.sha256(content2.encode()).hexdigest()
        return 1.0 if hash1 == hash2 else 0.0
    
    def _content_hash_similarity(self, content1: str, content2: str) -> float:
        """Calculate content-based hash similarity."""
        # Use a more flexible hash that ignores minor differences
        normalized1 = re.sub(r'\W+', '', content1.lower())
        normalized2 = re.sub(r'\W+', '', content2.lower())
        
        hash1 = hashlib.sha256(normalized1.encode()).hexdigest()
        hash2 = hashlib.sha256(normalized2.encode()).hexdigest()
        
        return 1.0 if hash1 == hash2 else 0.0
    
    def _jaccard_similarity(self, content1: str, content2: str) -> float:
        """Calculate Jaccard similarity."""
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _shingle_similarity(self, content1: str, content2: str) -> float:
        """Calculate n-gram shingle similarity."""
        def get_shingles(text: str, k: int) -> Set[str]:
            words = text.split()
            return {' '.join(words[i:i+k]) for i in range(len(words) - k + 1)}
        
        shingles1 = get_shingles(content1, self.config.shingle_size)
        shingles2 = get_shingles(content2, self.config.shingle_size)
        
        if not shingles1 and not shingles2:
            return 1.0
        
        intersection = shingles1.intersection(shingles2)
        union = shingles1.union(shingles2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _levenshtein_similarity(self, content1: str, content2: str) -> float:
        """Calculate Levenshtein distance similarity."""
        # Simplified Levenshtein distance calculation
        if content1 == content2:
            return 1.0
        
        len1, len2 = len(content1), len(content2)
        if len1 == 0:
            return 0.0
        if len2 == 0:
            return 0.0
        
        # Use a simplified approach for performance
        # This is not the full Levenshtein algorithm but a reasonable approximation
        max_len = max(len1, len2)
        min_len = min(len1, len2)
        
        # Very rough similarity based on character overlap
        common_chars = sum(1 for c in content1 if c in content2)
        similarity = common_chars / max_len
        
        return min(1.0, similarity)
    
    def clear_cache(self) -> None:
        """Clear internal caches."""
        self._content_cache.clear()
        self._hash_cache.clear()
        self._similarity_cache.clear()
        logger.info("ContentDeduplicator caches cleared")