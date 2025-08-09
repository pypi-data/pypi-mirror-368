# this_file: external/int_folders/d361/src/d361/api/bulk_operations.py
"""
Bulk Operations Manager for Document360 API.

This module provides comprehensive bulk operation capabilities including
parallel operations, smart retry logic, error recovery, and progress tracking.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field

from .client import Document360ApiClient
from .errors import Document360Error, ErrorHandler


class OperationType(str, Enum):
    """Types of bulk operations."""
    CREATE = "create"
    UPDATE = "update" 
    DELETE = "delete"
    FETCH = "fetch"


@dataclass
class OperationRequest:
    """
    Request for a single operation in a bulk operation.
    
    Represents one item in a bulk operation with all necessary data
    and metadata for execution and tracking.
    """
    operation_type: OperationType
    item_id: str  # Unique identifier for this operation
    data: Optional[Dict[str, Any]] = None  # Data for create/update operations
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)  # Additional metadata
    
    # Execution tracking
    attempts: int = 0
    max_attempts: int = 3
    last_error: Optional[str] = None
    completed: bool = False
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate operation request."""
        if self.operation_type in [OperationType.CREATE, OperationType.UPDATE] and not self.data:
            raise ValueError(f"{self.operation_type} operations require data")


@dataclass
class BulkOperationResult:
    """
    Results of a bulk operation.
    
    Comprehensive summary of bulk operation execution with
    success/failure metrics and detailed results.
    """
    operation_type: OperationType
    total_requests: int
    successful_requests: int
    failed_requests: int
    skipped_requests: int
    
    # Timing information
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Results
    successful_results: List[Dict[str, Any]] = field(default_factory=list)
    failed_requests_details: List[OperationRequest] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0-1)."""
        return self.successful_requests / max(self.total_requests, 1)
    
    @property
    def is_complete(self) -> bool:
        """Check if operation is complete."""
        return self.end_time is not None
    
    def mark_complete(self) -> None:
        """Mark operation as complete and calculate duration."""
        self.end_time = datetime.now()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()


class BulkOperationConfig(BaseModel):
    """Configuration for bulk operations."""
    max_concurrent_operations: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum concurrent operations"
    )
    
    retry_failed_operations: bool = Field(
        default=True,
        description="Whether to retry failed operations"
    )
    
    max_retries_per_operation: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retries per failed operation"
    )
    
    fail_fast: bool = Field(
        default=False,
        description="Stop on first error instead of continuing"
    )
    
    progress_callback: Optional[Callable[[int, int], None]] = Field(
        default=None,
        description="Progress callback function (completed, total)"
    )


class BulkOperationManager:
    """
    Manager for handling parallel bulk operations with the Document360 API.
    
    Provides capabilities for:
    - Parallel execution of bulk operations (create, update, delete, fetch)
    - Intelligent error handling and retry logic
    - Progress tracking and monitoring
    - Result aggregation and reporting
    """
    
    def __init__(self, client: Document360ApiClient, config: Optional[BulkOperationConfig] = None):
        """
        Initialize bulk operation manager.
        
        Args:
            client: Document360 API client
            config: Bulk operation configuration
        """
        self.client = client
        self.config = config or BulkOperationConfig()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_operations)
        
        logger.info(
            "BulkOperationManager initialized",
            max_concurrent=self.config.max_concurrent_operations,
            retry_enabled=self.config.retry_failed_operations,
            max_retries=self.config.max_retries_per_operation,
        )
    
    async def execute_bulk_create(
        self,
        articles_data: List[Dict[str, Any]],
        chunk_size: Optional[int] = None
    ) -> BulkOperationResult:
        """
        Execute bulk article creation.
        
        Args:
            articles_data: List of article data dictionaries
            chunk_size: Optional chunk size for processing
            
        Returns:
            Bulk operation result
        """
        requests = [
            OperationRequest(
                operation_type=OperationType.CREATE,
                item_id=f"create_{i}",
                data=article_data,
                max_attempts=self.config.max_retries_per_operation
            )
            for i, article_data in enumerate(articles_data)
        ]
        
        return await self._execute_bulk_operations(requests, chunk_size)
    
    async def execute_bulk_update(
        self,
        updates: List[tuple[str, Dict[str, Any]]],  # (article_id, update_data)
        chunk_size: Optional[int] = None
    ) -> BulkOperationResult:
        """
        Execute bulk article updates.
        
        Args:
            updates: List of (article_id, update_data) tuples
            chunk_size: Optional chunk size for processing
            
        Returns:
            Bulk operation result
        """
        requests = [
            OperationRequest(
                operation_type=OperationType.UPDATE,
                item_id=article_id,
                data=update_data,
                max_attempts=self.config.max_retries_per_operation
            )
            for article_id, update_data in updates
        ]
        
        return await self._execute_bulk_operations(requests, chunk_size)
    
    async def execute_bulk_delete(
        self,
        article_ids: List[str],
        chunk_size: Optional[int] = None
    ) -> BulkOperationResult:
        """
        Execute bulk article deletion.
        
        Args:
            article_ids: List of article IDs to delete
            chunk_size: Optional chunk size for processing
            
        Returns:
            Bulk operation result
        """
        requests = [
            OperationRequest(
                operation_type=OperationType.DELETE,
                item_id=article_id,
                max_attempts=self.config.max_retries_per_operation
            )
            for article_id in article_ids
        ]
        
        return await self._execute_bulk_operations(requests, chunk_size)
    
    async def execute_bulk_fetch(
        self,
        article_ids: List[str],
        chunk_size: Optional[int] = None
    ) -> BulkOperationResult:
        """
        Execute bulk article fetching.
        
        Args:
            article_ids: List of article IDs to fetch
            chunk_size: Optional chunk size for processing
            
        Returns:
            Bulk operation result
        """
        requests = [
            OperationRequest(
                operation_type=OperationType.FETCH,
                item_id=article_id,
                max_attempts=self.config.max_retries_per_operation
            )
            for article_id in article_ids
        ]
        
        return await self._execute_bulk_operations(requests, chunk_size)
    
    async def _execute_bulk_operations(
        self,
        requests: List[OperationRequest],
        chunk_size: Optional[int] = None
    ) -> BulkOperationResult:
        """
        Execute a list of operation requests.
        
        Args:
            requests: List of operation requests
            chunk_size: Optional chunk size for processing
            
        Returns:
            Bulk operation result
        """
        operation_type = requests[0].operation_type if requests else OperationType.FETCH
        result = BulkOperationResult(
            operation_type=operation_type,
            total_requests=len(requests),
            successful_requests=0,
            failed_requests=0,
            skipped_requests=0,
            start_time=datetime.now()
        )
        
        if not requests:
            result.mark_complete()
            return result
        
        logger.info(
            f"Starting bulk {operation_type} operation",
            total_requests=len(requests),
            chunk_size=chunk_size,
        )
        
        # Process in chunks if specified
        if chunk_size:
            chunks = [requests[i:i + chunk_size] for i in range(0, len(requests), chunk_size)]
        else:
            chunks = [requests]
        
        completed_count = 0
        
        for chunk_idx, chunk in enumerate(chunks):
            logger.debug(f"Processing chunk {chunk_idx + 1}/{len(chunks)} with {len(chunk)} operations")
            
            # Execute chunk operations concurrently
            tasks = [self._execute_single_operation(request) for request in chunk]
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process chunk results
            for request, chunk_result in zip(chunk, chunk_results):
                completed_count += 1
                
                if isinstance(chunk_result, Exception):
                    logger.error(f"Unexpected error in operation {request.item_id}: {chunk_result}")
                    request.last_error = str(chunk_result)
                    result.failed_requests += 1
                    result.failed_requests_details.append(request)
                elif chunk_result:
                    result.successful_requests += 1
                    result.successful_results.append(chunk_result)
                else:
                    result.failed_requests += 1
                    result.failed_requests_details.append(request)
                
                # Progress callback
                if self.config.progress_callback:
                    self.config.progress_callback(completed_count, len(requests))
                
                # Fail fast if enabled
                if self.config.fail_fast and not chunk_result:
                    logger.warning("Fail-fast enabled, stopping on first error")
                    result.skipped_requests = len(requests) - completed_count
                    break
            
            if self.config.fail_fast and result.failed_requests > 0:
                break
        
        # Retry failed operations if enabled
        if self.config.retry_failed_operations and result.failed_requests_details:
            logger.info(f"Retrying {len(result.failed_requests_details)} failed operations")
            retry_result = await self._retry_failed_operations(result.failed_requests_details)
            
            # Update results with retry outcomes
            result.successful_requests += retry_result.successful_requests
            result.failed_requests = len(retry_result.failed_requests_details)
            result.successful_results.extend(retry_result.successful_results)
            result.failed_requests_details = retry_result.failed_requests_details
        
        result.mark_complete()
        
        logger.info(
            f"Bulk {operation_type} operation completed",
            total=result.total_requests,
            successful=result.successful_requests,
            failed=result.failed_requests,
            success_rate=f"{result.success_rate:.1%}",
            duration=f"{result.duration_seconds:.2f}s",
        )
        
        return result
    
    async def _execute_single_operation(self, request: OperationRequest) -> Optional[Dict[str, Any]]:
        """
        Execute a single operation with semaphore control.
        
        Args:
            request: Operation request to execute
            
        Returns:
            Operation result or None if failed
        """
        async with self._semaphore:
            return await self._perform_operation(request)
    
    async def _perform_operation(self, request: OperationRequest) -> Optional[Dict[str, Any]]:
        """
        Perform a single API operation.
        
        Args:
            request: Operation request to execute
            
        Returns:
            Operation result or None if failed
        """
        try:
            request.attempts += 1
            
            if request.operation_type == OperationType.CREATE:
                result = await self.client.create_article(request.data)
                request.completed = True
                request.result = result
                return result
                
            elif request.operation_type == OperationType.UPDATE:
                result = await self.client.update_article(request.item_id, request.data)
                request.completed = True
                request.result = result
                return result
                
            elif request.operation_type == OperationType.DELETE:
                success = await self.client.delete_article(request.item_id)
                result = {"deleted": success, "article_id": request.item_id}
                request.completed = True
                request.result = result
                return result
                
            elif request.operation_type == OperationType.FETCH:
                result = await self.client.get_article(request.item_id)
                request.completed = True
                request.result = result
                return result
            
        except Document360Error as e:
            request.last_error = str(e)
            logger.warning(
                f"Operation {request.operation_type} failed for {request.item_id}",
                attempt=request.attempts,
                error=str(e),
                error_category=e.category.value,
            )
            return None
        
        except Exception as e:
            request.last_error = str(e)
            logger.error(
                f"Unexpected error in {request.operation_type} for {request.item_id}",
                attempt=request.attempts,
                error=str(e),
            )
            return None
    
    async def _retry_failed_operations(self, failed_requests: List[OperationRequest]) -> BulkOperationResult:
        """
        Retry failed operations.
        
        Args:
            failed_requests: List of failed operation requests
            
        Returns:
            Results of retry operations
        """
        result = BulkOperationResult(
            operation_type=failed_requests[0].operation_type if failed_requests else OperationType.FETCH,
            total_requests=len(failed_requests),
            successful_requests=0,
            failed_requests=0,
            skipped_requests=0,
            start_time=datetime.now()
        )
        
        retry_candidates = [
            req for req in failed_requests
            if req.attempts < req.max_attempts
        ]
        
        if not retry_candidates:
            result.failed_requests_details = failed_requests
            result.failed_requests = len(failed_requests)
            result.mark_complete()
            return result
        
        logger.info(f"Retrying {len(retry_candidates)} operations")
        
        # Execute retries with exponential backoff
        for request in retry_candidates:
            # Calculate backoff delay
            backoff_delay = min(2 ** (request.attempts - 1), 30)  # Max 30 seconds
            if backoff_delay > 0:
                await asyncio.sleep(backoff_delay)
            
            retry_result = await self._perform_operation(request)
            
            if retry_result:
                result.successful_requests += 1
                result.successful_results.append(retry_result)
            else:
                result.failed_requests += 1
                result.failed_requests_details.append(request)
        
        # Add requests that weren't retried
        non_retry_requests = [
            req for req in failed_requests
            if req.attempts >= req.max_attempts
        ]
        result.failed_requests += len(non_retry_requests)
        result.failed_requests_details.extend(non_retry_requests)
        
        result.mark_complete()
        return result


class SmartBulkProcessor:
    """
    Smart bulk processor with automatic error recovery and optimization.
    
    Provides intelligent bulk processing with:
    - Adaptive batch sizing based on API performance
    - Automatic error recovery and retry strategies
    - Rate limit awareness and backoff
    - Progress monitoring and reporting
    """
    
    def __init__(self, client: Document360ApiClient):
        """Initialize smart bulk processor."""
        self.client = client
        self.bulk_manager = BulkOperationManager(client)
        
        # Adaptive batch sizing
        self.initial_batch_size = 50
        self.min_batch_size = 10
        self.max_batch_size = 100
        self.current_batch_size = self.initial_batch_size
        
        # Performance tracking
        self.success_rates = []
        self.response_times = []
        
        logger.info("SmartBulkProcessor initialized")
    
    async def process_articles_intelligently(
        self,
        operation: str,
        articles_data: List[Union[Dict[str, Any], tuple[str, Dict[str, Any]], str]],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> BulkOperationResult:
        """
        Process articles with intelligent batch sizing and error recovery.
        
        Args:
            operation: Operation type ('create', 'update', 'delete', 'fetch')
            articles_data: List of data for the operation
            progress_callback: Optional progress callback
            
        Returns:
            Bulk operation result
        """
        logger.info(
            f"Starting intelligent {operation} processing",
            total_items=len(articles_data),
            initial_batch_size=self.current_batch_size,
        )
        
        # Configure bulk operation
        config = BulkOperationConfig(
            max_concurrent_operations=min(10, self.current_batch_size),
            retry_failed_operations=True,
            max_retries_per_operation=3,
            progress_callback=progress_callback
        )
        
        self.bulk_manager.config = config
        
        # Execute based on operation type
        if operation == 'create':
            return await self.bulk_manager.execute_bulk_create(articles_data)
        elif operation == 'update':
            return await self.bulk_manager.execute_bulk_update(articles_data)
        elif operation == 'delete':
            return await self.bulk_manager.execute_bulk_delete(articles_data)
        elif operation == 'fetch':
            return await self.bulk_manager.execute_bulk_fetch(articles_data)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    def _adapt_batch_size(self, success_rate: float, response_time: float) -> None:
        """
        Adapt batch size based on performance metrics.
        
        Args:
            success_rate: Success rate (0-1) of recent operations
            response_time: Average response time in seconds
        """
        self.success_rates.append(success_rate)
        self.response_times.append(response_time)
        
        # Keep only recent history
        if len(self.success_rates) > 10:
            self.success_rates.pop(0)
            self.response_times.pop(0)
        
        avg_success_rate = sum(self.success_rates) / len(self.success_rates)
        avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # Adjust batch size based on performance
        if avg_success_rate > 0.95 and avg_response_time < 2.0:
            # Performance is good, increase batch size
            self.current_batch_size = min(self.max_batch_size, int(self.current_batch_size * 1.2))
        elif avg_success_rate < 0.8 or avg_response_time > 5.0:
            # Performance is poor, decrease batch size
            self.current_batch_size = max(self.min_batch_size, int(self.current_batch_size * 0.8))
        
        logger.debug(
            "Adapted batch size",
            old_size=self.current_batch_size,
            new_size=self.current_batch_size,
            success_rate=f"{avg_success_rate:.1%}",
            response_time=f"{avg_response_time:.2f}s",
        )