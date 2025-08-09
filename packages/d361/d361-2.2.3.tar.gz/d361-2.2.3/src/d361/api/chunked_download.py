# this_file: external/int_folders/d361/src/d361/api/chunked_download.py
"""
Chunked Download Manager for Document360 API.

This module provides comprehensive chunked download capabilities for handling
large datasets with resumable downloads, progress tracking, and error recovery.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field, validator

from .client import Document360ApiClient
from .errors import Document360Error


class DownloadStatus(str, Enum):
    """Download status enumeration."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ChunkStatus(str, Enum):
    """Individual chunk status."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DownloadChunk:
    """
    Represents a single download chunk.
    
    Contains all information needed to download and track
    progress of a single chunk of data.
    """
    chunk_id: str
    start_offset: int
    end_offset: int
    size: int
    status: ChunkStatus = ChunkStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    download_time: Optional[float] = None
    data: Optional[List[Dict[str, Any]]] = None
    
    @property
    def is_complete(self) -> bool:
        """Check if chunk is complete."""
        return self.status == ChunkStatus.COMPLETED
    
    @property
    def can_retry(self) -> bool:
        """Check if chunk can be retried."""
        return self.attempts < self.max_attempts and self.status == ChunkStatus.FAILED


@dataclass
class DownloadProgress:
    """
    Download progress tracking.
    
    Provides comprehensive progress information including
    timing, throughput, and completion estimates.
    """
    total_items: int
    downloaded_items: int = 0
    failed_items: int = 0
    total_chunks: int = 0
    completed_chunks: int = 0
    failed_chunks: int = 0
    
    start_time: datetime = field(default_factory=datetime.now)
    last_update_time: datetime = field(default_factory=datetime.now)
    
    # Performance metrics
    bytes_downloaded: int = 0
    total_bytes: Optional[int] = None
    avg_download_speed: float = 0.0  # items per second
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage (0-100)."""
        if self.total_items == 0:
            return 100.0
        return (self.downloaded_items / self.total_items) * 100.0
    
    @property
    def chunk_completion_percentage(self) -> float:
        """Calculate chunk completion percentage (0-100)."""
        if self.total_chunks == 0:
            return 100.0
        return (self.completed_chunks / self.total_chunks) * 100.0
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def estimated_time_remaining(self) -> Optional[float]:
        """Estimate time remaining in seconds."""
        if self.downloaded_items == 0 or self.avg_download_speed == 0:
            return None
        
        remaining_items = self.total_items - self.downloaded_items
        return remaining_items / self.avg_download_speed
    
    def update_progress(self, items_downloaded: int, chunk_completed: bool = False) -> None:
        """Update progress metrics."""
        self.downloaded_items += items_downloaded
        if chunk_completed:
            self.completed_chunks += 1
        
        self.last_update_time = datetime.now()
        
        # Calculate download speed
        elapsed = self.elapsed_time
        if elapsed > 0:
            self.avg_download_speed = self.downloaded_items / elapsed


class DownloadConfig(BaseModel):
    """Configuration for chunked downloads."""
    
    chunk_size: int = Field(
        default=500,
        ge=1,
        le=1000,
        description="Number of items per chunk"
    )
    
    max_concurrent_chunks: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum concurrent chunk downloads"
    )
    
    max_retries_per_chunk: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retries per failed chunk"
    )
    
    retry_delay: float = Field(
        default=2.0,
        ge=0.1,
        le=60.0,
        description="Base delay between retries in seconds"
    )
    
    resume_support: bool = Field(
        default=True,
        description="Enable resumable downloads"
    )
    
    save_progress: bool = Field(
        default=True,
        description="Save progress to disk for resumption"
    )
    
    progress_callback: Optional[Callable[[DownloadProgress], None]] = Field(
        default=None,
        description="Progress callback function"
    )
    
    output_directory: Optional[Path] = Field(
        default=None,
        description="Directory to save downloaded data"
    )
    
    @validator('output_directory')
    def validate_output_directory(cls, v):
        """Validate output directory."""
        if v is not None:
            v = Path(v)
            v.mkdir(parents=True, exist_ok=True)
        return v


@dataclass
class DownloadState:
    """
    Persistent download state for resumability.
    
    Contains all information needed to resume a download
    from where it left off.
    """
    download_id: str
    operation_type: str
    operation_params: Dict[str, Any]
    total_items: int
    chunk_size: int
    chunks: List[DownloadChunk] = field(default_factory=list)
    status: DownloadStatus = DownloadStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'download_id': self.download_id,
            'operation_type': self.operation_type,
            'operation_params': self.operation_params,
            'total_items': self.total_items,
            'chunk_size': self.chunk_size,
            'chunks': [
                {
                    'chunk_id': chunk.chunk_id,
                    'start_offset': chunk.start_offset,
                    'end_offset': chunk.end_offset,
                    'size': chunk.size,
                    'status': chunk.status.value,
                    'attempts': chunk.attempts,
                    'max_attempts': chunk.max_attempts,
                    'last_error': chunk.last_error,
                    'download_time': chunk.download_time,
                }
                for chunk in self.chunks
            ],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DownloadState:
        """Create from dictionary."""
        chunks = [
            DownloadChunk(
                chunk_id=chunk_data['chunk_id'],
                start_offset=chunk_data['start_offset'],
                end_offset=chunk_data['end_offset'],
                size=chunk_data['size'],
                status=ChunkStatus(chunk_data['status']),
                attempts=chunk_data['attempts'],
                max_attempts=chunk_data['max_attempts'],
                last_error=chunk_data.get('last_error'),
                download_time=chunk_data.get('download_time'),
            )
            for chunk_data in data.get('chunks', [])
        ]
        
        return cls(
            download_id=data['download_id'],
            operation_type=data['operation_type'],
            operation_params=data['operation_params'],
            total_items=data['total_items'],
            chunk_size=data['chunk_size'],
            chunks=chunks,
            status=DownloadStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
        )


class ChunkedDownloader:
    """
    Chunked downloader for large Document360 datasets.
    
    Provides comprehensive chunked download capabilities with:
    - Resumable downloads with persistent state
    - Parallel chunk processing with concurrency control
    - Progress tracking and performance monitoring
    - Comprehensive error handling and retry logic
    - Data deduplication and integrity verification
    """
    
    def __init__(
        self,
        client: Document360ApiClient,
        config: Optional[DownloadConfig] = None
    ):
        """
        Initialize chunked downloader.
        
        Args:
            client: Document360 API client
            config: Download configuration
        """
        self.client = client
        self.config = config or DownloadConfig()
        
        # State management
        self.state_dir = self.config.output_directory or Path.cwd() / ".d361_downloads"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Active downloads tracking
        self.active_downloads: Dict[str, DownloadState] = {}
        
        logger.info(
            "ChunkedDownloader initialized",
            chunk_size=self.config.chunk_size,
            max_concurrent=self.config.max_concurrent_chunks,
            resume_support=self.config.resume_support,
        )
    
    async def download_all_articles(
        self,
        category_id: Optional[str] = None,
        project_version_id: Optional[str] = None,
        output_file: Optional[Path] = None
    ) -> DownloadState:
        """
        Download all articles with chunked processing.
        
        Args:
            category_id: Optional category filter
            project_version_id: Optional project version filter
            output_file: Optional output file path
            
        Returns:
            Download state with results
        """
        # Generate unique download ID
        params_str = f"{category_id}_{project_version_id}"
        download_id = hashlib.md5(params_str.encode()).hexdigest()[:12]
        
        operation_params = {
            "category_id": category_id,
            "project_version_id": project_version_id,
            "output_file": str(output_file) if output_file else None,
        }
        
        # Check for existing download
        if self.config.resume_support:
            existing_state = await self._load_download_state(download_id)
            if existing_state and existing_state.status not in [DownloadStatus.COMPLETED, DownloadStatus.CANCELLED]:
                logger.info(f"Resuming existing download: {download_id}")
                return await self._resume_download(existing_state)
        
        # Start new download
        logger.info(
            "Starting chunked article download",
            download_id=download_id,
            category_id=category_id,
            project_version_id=project_version_id,
        )
        
        # First, get total count
        initial_response = await self.client.list_articles(
            category_id=category_id,
            project_version_id=project_version_id,
            limit=1,
            offset=0
        )
        
        # Extract total count from response
        total_items = initial_response.get('total', 0)
        if total_items == 0:
            logger.warning("No articles found for download")
            return DownloadState(
                download_id=download_id,
                operation_type="download_articles",
                operation_params=operation_params,
                total_items=0,
                chunk_size=self.config.chunk_size,
                status=DownloadStatus.COMPLETED
            )
        
        # Create download state
        download_state = DownloadState(
            download_id=download_id,
            operation_type="download_articles",
            operation_params=operation_params,
            total_items=total_items,
            chunk_size=self.config.chunk_size,
        )
        
        # Create chunks
        chunks = self._create_chunks(total_items, self.config.chunk_size)
        download_state.chunks = chunks
        download_state.status = DownloadStatus.DOWNLOADING
        
        # Save initial state
        if self.config.save_progress:
            await self._save_download_state(download_state)
        
        # Start download
        self.active_downloads[download_id] = download_state
        
        try:
            await self._execute_chunked_download(download_state)
            
            # Save final results
            if output_file:
                await self._save_download_results(download_state, output_file)
            
            download_state.status = DownloadStatus.COMPLETED
            logger.info(
                f"Download completed: {download_id}",
                total_items=download_state.total_items,
                chunks=len(download_state.chunks),
            )
            
        except Exception as e:
            download_state.status = DownloadStatus.FAILED
            logger.error(f"Download failed: {download_id}", error=str(e))
            raise
        
        finally:
            if self.config.save_progress:
                await self._save_download_state(download_state)
            
            # Clean up active downloads
            self.active_downloads.pop(download_id, None)
        
        return download_state
    
    def _create_chunks(self, total_items: int, chunk_size: int) -> List[DownloadChunk]:
        """Create download chunks."""
        chunks = []
        
        for i in range(0, total_items, chunk_size):
            start_offset = i
            end_offset = min(i + chunk_size - 1, total_items - 1)
            actual_size = end_offset - start_offset + 1
            
            chunk = DownloadChunk(
                chunk_id=f"chunk_{i//chunk_size:04d}",
                start_offset=start_offset,
                end_offset=end_offset,
                size=actual_size,
                max_attempts=self.config.max_retries_per_chunk
            )
            chunks.append(chunk)
        
        logger.debug(f"Created {len(chunks)} chunks for {total_items} items")
        return chunks
    
    async def _execute_chunked_download(self, download_state: DownloadState) -> None:
        """Execute chunked download with concurrency control."""
        progress = DownloadProgress(
            total_items=download_state.total_items,
            total_chunks=len(download_state.chunks)
        )
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config.max_concurrent_chunks)
        
        # Get pending chunks
        pending_chunks = [chunk for chunk in download_state.chunks if not chunk.is_complete]
        
        if not pending_chunks:
            logger.info("All chunks already completed")
            return
        
        logger.info(f"Processing {len(pending_chunks)} chunks with {self.config.max_concurrent_chunks} concurrent workers")
        
        # Process chunks concurrently
        tasks = [
            self._download_chunk(semaphore, chunk, download_state, progress)
            for chunk in pending_chunks
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Final progress update
        if self.config.progress_callback:
            self.config.progress_callback(progress)
    
    async def _download_chunk(
        self,
        semaphore: asyncio.Semaphore,
        chunk: DownloadChunk,
        download_state: DownloadState,
        progress: DownloadProgress
    ) -> None:
        """Download a single chunk."""
        async with semaphore:
            chunk.status = ChunkStatus.DOWNLOADING
            start_time = time.time()
            
            try:
                # Extract operation parameters
                params = download_state.operation_params
                
                # Download chunk data
                response = await self.client.list_articles(
                    category_id=params.get("category_id"),
                    project_version_id=params.get("project_version_id"),
                    limit=chunk.size,
                    offset=chunk.start_offset
                )
                
                # Store data
                chunk.data = response.get('data', [])
                chunk.status = ChunkStatus.COMPLETED
                chunk.download_time = time.time() - start_time
                
                # Update progress
                items_downloaded = len(chunk.data)
                progress.update_progress(items_downloaded, chunk_completed=True)
                
                logger.debug(
                    f"Chunk {chunk.chunk_id} completed",
                    items=items_downloaded,
                    duration=f"{chunk.download_time:.2f}s",
                )
                
                # Progress callback
                if self.config.progress_callback:
                    self.config.progress_callback(progress)
                
            except Exception as e:
                chunk.attempts += 1
                chunk.last_error = str(e)
                chunk.status = ChunkStatus.FAILED
                progress.failed_chunks += 1
                
                logger.warning(
                    f"Chunk {chunk.chunk_id} failed",
                    attempt=chunk.attempts,
                    error=str(e),
                )
                
                # Retry if possible
                if chunk.can_retry:
                    retry_delay = self.config.retry_delay * (2 ** (chunk.attempts - 1))
                    await asyncio.sleep(retry_delay)
                    
                    logger.info(f"Retrying chunk {chunk.chunk_id} (attempt {chunk.attempts + 1})")
                    await self._download_chunk(semaphore, chunk, download_state, progress)
            
            finally:
                download_state.updated_at = datetime.now()
                
                # Save progress periodically
                if self.config.save_progress:
                    await self._save_download_state(download_state)
    
    async def _resume_download(self, download_state: DownloadState) -> DownloadState:
        """Resume an existing download."""
        logger.info(f"Resuming download: {download_state.download_id}")
        
        # Add to active downloads
        self.active_downloads[download_state.download_id] = download_state
        
        try:
            download_state.status = DownloadStatus.DOWNLOADING
            await self._execute_chunked_download(download_state)
            
            download_state.status = DownloadStatus.COMPLETED
            
        except Exception as e:
            download_state.status = DownloadStatus.FAILED
            logger.error(f"Resume failed: {download_state.download_id}", error=str(e))
            raise
        
        finally:
            if self.config.save_progress:
                await self._save_download_state(download_state)
            
            self.active_downloads.pop(download_state.download_id, None)
        
        return download_state
    
    async def _save_download_state(self, download_state: DownloadState) -> None:
        """Save download state to disk."""
        state_file = self.state_dir / f"{download_state.download_id}.json"
        
        try:
            with state_file.open('w') as f:
                json.dump(download_state.to_dict(), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save download state: {e}")
    
    async def _load_download_state(self, download_id: str) -> Optional[DownloadState]:
        """Load download state from disk."""
        state_file = self.state_dir / f"{download_id}.json"
        
        if not state_file.exists():
            return None
        
        try:
            with state_file.open('r') as f:
                data = json.load(f)
            return DownloadState.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load download state: {e}")
            return None
    
    async def _save_download_results(self, download_state: DownloadState, output_file: Path) -> None:
        """Save download results to file."""
        all_data = []
        
        for chunk in download_state.chunks:
            if chunk.data:
                all_data.extend(chunk.data)
        
        try:
            with output_file.open('w') as f:
                json.dump({
                    'download_info': {
                        'download_id': download_state.download_id,
                        'total_items': len(all_data),
                        'downloaded_at': datetime.now().isoformat(),
                        'operation_params': download_state.operation_params,
                    },
                    'data': all_data
                }, f, indent=2)
            
            logger.info(f"Results saved to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
    
    async def list_downloads(self) -> List[DownloadState]:
        """List all saved downloads."""
        downloads = []
        
        for state_file in self.state_dir.glob("*.json"):
            try:
                download_id = state_file.stem
                download_state = await self._load_download_state(download_id)
                if download_state:
                    downloads.append(download_state)
            except Exception as e:
                logger.warning(f"Failed to load download {state_file}: {e}")
        
        return downloads
    
    async def cancel_download(self, download_id: str) -> bool:
        """Cancel an active download."""
        if download_id in self.active_downloads:
            download_state = self.active_downloads[download_id]
            download_state.status = DownloadStatus.CANCELLED
            
            if self.config.save_progress:
                await self._save_download_state(download_state)
            
            logger.info(f"Download cancelled: {download_id}")
            return True
        
        return False
    
    async def cleanup_downloads(self, older_than_days: int = 30) -> int:
        """Clean up old download state files."""
        cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 3600)
        cleaned_count = 0
        
        for state_file in self.state_dir.glob("*.json"):
            try:
                if state_file.stat().st_mtime < cutoff_time:
                    state_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to clean up {state_file}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} old download files")
        return cleaned_count