#!/usr/bin/env python3
# this_file: external/int_folders/d361/src/d361/api/api_updater.py
"""
Automated API Client Updater

This module provides automated monitoring and updating of API clients when
the Document360 OpenAPI specification changes. It can run as a background
service or be triggered manually to check for updates and regenerate
models and client code as needed.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field

from .openapi_integration import OpenApiIntegration, OpenApiConfig, OpenApiSpec
from .generate_models import ModelGenerator, ModelGenerationConfig, GenerationResult


class UpdateTrigger(str, Enum):
    """Types of update triggers."""
    MANUAL = "manual"           # Manually triggered update
    SCHEDULED = "scheduled"     # Scheduled periodic check
    WEBHOOK = "webhook"         # Triggered by webhook
    FILE_WATCH = "file_watch"   # Triggered by file system changes


class UpdateStatus(str, Enum):
    """Status of update operations."""
    PENDING = "pending"         # Update is queued
    RUNNING = "running"         # Update is in progress
    SUCCESS = "success"         # Update completed successfully
    FAILED = "failed"           # Update failed
    SKIPPED = "skipped"         # Update was skipped (no changes)


@dataclass
class UpdateEvent:
    """Record of an update event."""
    timestamp: datetime
    trigger: UpdateTrigger
    status: UpdateStatus
    old_spec_hash: Optional[str] = None
    new_spec_hash: Optional[str] = None
    changes_detected: List[str] = field(default_factory=list)
    files_updated: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_seconds: Optional[float] = None


class ApiUpdaterConfig(BaseModel):
    """Configuration for the API updater."""
    
    # OpenAPI and model generation configs
    openapi_config: OpenApiConfig = Field(
        default_factory=OpenApiConfig,
        description="OpenAPI integration configuration"
    )
    
    model_generation_config: ModelGenerationConfig = Field(
        default_factory=ModelGenerationConfig,
        description="Model generation configuration"
    )
    
    # Update behavior
    check_interval_seconds: int = Field(
        default=3600,  # 1 hour
        ge=60,
        le=86400,
        description="Interval between automatic checks (seconds)"
    )
    
    auto_update_enabled: bool = Field(
        default=False,
        description="Enable automatic updates when changes are detected"
    )
    
    # Notification and logging
    log_updates: bool = Field(
        default=True,
        description="Log update events"
    )
    
    max_history_entries: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of update events to keep in history"
    )
    
    # File watching
    watch_spec_files: List[Path] = Field(
        default_factory=list,
        description="Local OpenAPI spec files to watch for changes"
    )
    
    # Webhooks and callbacks
    on_update_start: Optional[str] = Field(
        None,
        description="Callback function name for update start"
    )
    
    on_update_complete: Optional[str] = Field(
        None,
        description="Callback function name for update completion"
    )
    
    on_update_failed: Optional[str] = Field(
        None,
        description="Callback function name for update failure"
    )


class ApiUpdater:
    """
    Automated API client updater for Document360 OpenAPI specifications.
    
    Monitors the OpenAPI specification for changes and automatically
    regenerates Pydantic models and updates API client code when
    changes are detected.
    """
    
    def __init__(
        self,
        config: Optional[ApiUpdaterConfig] = None,
        callbacks: Optional[Dict[str, Callable]] = None
    ):
        """
        Initialize the API updater.
        
        Args:
            config: Updater configuration
            callbacks: Dictionary of callback functions
        """
        self.config = config or ApiUpdaterConfig()
        self.callbacks = callbacks or {}
        
        # Initialize components
        self.openapi_integration = OpenApiIntegration(self.config.openapi_config)
        self.model_generator = ModelGenerator(self.config.model_generation_config)
        
        # Internal state
        self._current_spec_hash: Optional[str] = None
        self._update_history: List[UpdateEvent] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        logger.info(
            f"ApiUpdater initialized",
            check_interval=self.config.check_interval_seconds,
            auto_update=self.config.auto_update_enabled
        )
    
    async def start_monitoring(self) -> None:
        """Start background monitoring for OpenAPI spec changes."""
        if self._running:
            logger.warning("ApiUpdater is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started OpenAPI monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped OpenAPI monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        logger.info(f"Starting monitoring loop with {self.config.check_interval_seconds}s interval")
        
        while self._running:
            try:
                # Check for updates
                has_updates = await self.check_for_updates()
                
                if has_updates and self.config.auto_update_enabled:
                    logger.info("Changes detected, triggering automatic update")
                    await self.update_api_client(trigger=UpdateTrigger.SCHEDULED)
                
                # Wait for next check
                await asyncio.sleep(self.config.check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Continue monitoring despite errors
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def check_for_updates(self) -> bool:
        """
        Check if the OpenAPI specification has updates.
        
        Returns:
            True if updates are available
        """
        try:
            # Get current spec
            current_spec = await self.openapi_integration.get_spec()
            
            # Compare with last known hash
            if self._current_spec_hash is None:
                # First time - always consider as "updated"
                self._current_spec_hash = current_spec.content_hash
                return True
            
            if current_spec.content_hash != self._current_spec_hash:
                logger.info(
                    f"OpenAPI spec changes detected",
                    old_hash=self._current_spec_hash[:8],
                    new_hash=current_spec.content_hash[:8]
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return False
    
    async def update_api_client(
        self,
        trigger: UpdateTrigger = UpdateTrigger.MANUAL,
        force: bool = False
    ) -> UpdateEvent:
        """
        Update the API client when changes are detected.
        
        Args:
            trigger: What triggered this update
            force: Force update even if no changes detected
            
        Returns:
            Update event record
        """
        start_time = datetime.now()
        event = UpdateEvent(
            timestamp=start_time,
            trigger=trigger,
            status=UpdateStatus.RUNNING
        )
        
        logger.info(f"Starting API client update (trigger: {trigger})")
        
        try:
            # Execute callback if configured
            await self._execute_callback('on_update_start', event)
            
            # Get current and new specs
            old_spec_hash = self._current_spec_hash
            new_spec = await self.openapi_integration.get_spec(force_refresh=force)
            
            # Check if update is needed
            if not force and old_spec_hash == new_spec.content_hash:
                event.status = UpdateStatus.SKIPPED
                logger.info("No changes detected, skipping update")
                return event
            
            # Track changes
            event.old_spec_hash = old_spec_hash
            event.new_spec_hash = new_spec.content_hash
            
            if old_spec_hash:
                # Get detailed changes if we have an old spec
                changes = await self._get_spec_changes(old_spec_hash, new_spec)
                event.changes_detected = changes
            
            # Generate new models
            logger.info("Regenerating Pydantic models")
            generation_result = await self.model_generator.generate_models(force_refresh=True)
            
            if not generation_result.success:
                event.status = UpdateStatus.FAILED
                event.errors = generation_result.errors
                logger.error(f"Model generation failed: {generation_result.errors}")
                return event
            
            # Track updated files
            event.files_updated.append(generation_result.output_file)
            
            # Update internal state
            self._current_spec_hash = new_spec.content_hash
            event.status = UpdateStatus.SUCCESS
            
            logger.info(
                f"API client update completed successfully",
                models_generated=generation_result.model_count,
                files_updated=len(event.files_updated)
            )
            
            # Execute success callback
            await self._execute_callback('on_update_complete', event)
            
        except Exception as e:
            event.status = UpdateStatus.FAILED
            event.errors = [str(e)]
            logger.error(f"API client update failed: {e}")
            
            # Execute failure callback
            await self._execute_callback('on_update_failed', event)
            
        finally:
            # Record timing and add to history
            event.duration_seconds = (datetime.now() - start_time).total_seconds()
            self._add_to_history(event)
        
        return event
    
    async def _get_spec_changes(self, old_hash: str, new_spec: OpenApiSpec) -> List[str]:
        """Get a list of changes between old and new specs."""
        # For now, just return a basic change description
        # In a full implementation, this could do detailed diff analysis
        changes = [
            f"Specification updated from {old_hash[:8]} to {new_spec.content_hash[:8]}",
            f"API version: {new_spec.api_version}",
            f"Total endpoints: {len(new_spec.get_endpoints())}",
            f"Total schemas: {len(new_spec.schemas)}"
        ]
        
        return changes
    
    async def _execute_callback(self, callback_name: str, event: UpdateEvent) -> None:
        """Execute a configured callback if available."""
        callback_func = self.callbacks.get(callback_name)
        if callback_func:
            try:
                if asyncio.iscoroutinefunction(callback_func):
                    await callback_func(event)
                else:
                    callback_func(event)
            except Exception as e:
                logger.warning(f"Callback {callback_name} failed: {e}")
    
    def _add_to_history(self, event: UpdateEvent) -> None:
        """Add an update event to history."""
        self._update_history.append(event)
        
        # Trim history if needed
        if len(self._update_history) > self.config.max_history_entries:
            self._update_history = self._update_history[-self.config.max_history_entries:]
    
    def get_update_history(self, limit: Optional[int] = None) -> List[UpdateEvent]:
        """
        Get update history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of update events, most recent first
        """
        history = list(reversed(self._update_history))
        if limit:
            history = history[:limit]
        return history
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the API updater."""
        return {
            'running': self._running,
            'current_spec_hash': self._current_spec_hash,
            'auto_update_enabled': self.config.auto_update_enabled,
            'check_interval_seconds': self.config.check_interval_seconds,
            'history_count': len(self._update_history),
            'last_update': self._update_history[-1].timestamp.isoformat() if self._update_history else None
        }
    
    async def close(self) -> None:
        """Close the updater and cleanup resources."""
        await self.stop_monitoring()
        await self.openapi_integration.close()
        await self.model_generator.close()
        
        logger.debug("ApiUpdater closed")


# Convenience functions for easy usage

async def create_updater(
    output_dir: Optional[str] = None,
    check_interval_seconds: int = 3600,
    auto_update: bool = False,
    callbacks: Optional[Dict[str, Callable]] = None
) -> ApiUpdater:
    """
    Create and configure an API updater with common settings.
    
    Args:
        output_dir: Output directory for generated models
        check_interval_seconds: Check interval in seconds
        auto_update: Enable automatic updates
        callbacks: Callback functions
        
    Returns:
        Configured API updater
    """
    config = ApiUpdaterConfig(
        check_interval_seconds=check_interval_seconds,
        auto_update_enabled=auto_update
    )
    
    if output_dir:
        config.model_generation_config.output_dir = Path(output_dir)
    
    return ApiUpdater(config, callbacks)


async def run_one_time_update(output_dir: Optional[str] = None, force: bool = False) -> UpdateEvent:
    """
    Run a one-time update check and model generation.
    
    Args:
        output_dir: Output directory for generated models
        force: Force update even if no changes
        
    Returns:
        Update event record
    """
    updater = await create_updater(output_dir=output_dir)
    
    try:
        return await updater.update_api_client(
            trigger=UpdateTrigger.MANUAL,
            force=force
        )
    finally:
        await updater.close()