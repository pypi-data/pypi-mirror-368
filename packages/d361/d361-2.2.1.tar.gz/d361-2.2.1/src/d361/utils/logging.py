# this_file: external/int_folders/d361/src/d361/utils/logging.py
"""
LoggingManager - Centralized logging configuration with loguru.

This module provides a comprehensive logging system that standardizes 
loguru configuration across all d361 components. It supports both 
human-readable console logging for development and structured JSON 
logging for production environments.
"""

from __future__ import annotations

import json
import sys
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field

# Context variables for correlation tracking
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")
user_id_ctx: ContextVar[str] = ContextVar("user_id", default="")
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class LogLevel(str, Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Supported log output formats."""
    CONSOLE = "console"
    JSON = "json"
    STRUCTURED = "structured"


class LogHandlerConfig(BaseModel):
    """Configuration for a log handler."""
    sink: Union[str, object] = Field(default=sys.stderr, description="Log destination")
    level: LogLevel = Field(default=LogLevel.INFO, description="Minimum log level")
    format: str = Field(default="", description="Log format string")
    rotation: Optional[str] = Field(default=None, description="Log rotation policy")
    retention: Optional[str] = Field(default=None, description="Log retention policy")
    compression: Optional[str] = Field(default=None, description="Log compression format")
    serialize: bool = Field(default=False, description="Enable JSON serialization")
    enqueue: bool = Field(default=True, description="Enable async logging")
    catch: bool = Field(default=True, description="Catch exceptions in handler")


class LoggingConfig(BaseModel):
    """Complete logging configuration."""
    level: LogLevel = Field(default=LogLevel.INFO, description="Global log level")
    format: LogFormat = Field(default=LogFormat.CONSOLE, description="Default log format")
    handlers: List[LogHandlerConfig] = Field(default_factory=list, description="Log handlers")
    enable_correlation: bool = Field(default=True, description="Enable correlation tracking")
    enable_caller_info: bool = Field(default=True, description="Include caller info in logs")
    enable_process_info: bool = Field(default=False, description="Include process info in logs")
    log_file: Optional[Path] = Field(default=None, description="Log file path")
    max_file_size: str = Field(default="10 MB", description="Max log file size")
    backup_count: int = Field(default=5, description="Number of backup files")


@dataclass
class LogContext:
    """Context information for log correlation."""
    correlation_id: str = ""
    user_id: str = ""
    request_id: str = ""
    session_id: str = ""
    operation: str = ""
    component: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        ctx = {
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "operation": self.operation,
            "component": self.component,
        }
        ctx.update(self.extra)
        # Remove empty values
        return {k: v for k, v in ctx.items() if v}


class LoggingManager:
    """
    Centralized logging manager using loguru.
    
    Features:
    - Standardized loguru configuration
    - Multiple output formats (console, JSON, structured)
    - Context correlation tracking
    - Environment-specific configurations
    - File rotation and retention policies
    - Async logging support
    - Exception handling integration
    """
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        self.config = config or LoggingConfig()
        self._initialized = False
        self._handlers: List[int] = []
        
    def initialize(self) -> None:
        """Initialize logging system with configuration."""
        if self._initialized:
            return
            
        # Remove default handler
        logger.remove()
        
        # Add configured handlers or create defaults
        if self.config.handlers:
            for handler_config in self.config.handlers:
                self._add_handler(handler_config)
        else:
            self._add_default_handlers()
            
        # Configure correlation context if enabled
        if self.config.enable_correlation:
            self._configure_correlation()
            
        self._initialized = True
        logger.info("LoggingManager initialized", config=self.config.model_dump())
        
    def _add_handler(self, handler_config: LogHandlerConfig) -> None:
        """Add a log handler with the given configuration."""
        handler_kwargs = {
            "sink": handler_config.sink,
            "level": handler_config.level.value,
            "format": handler_config.format or self._get_format(),
            "enqueue": handler_config.enqueue,
            "catch": handler_config.catch,
        }
        
        # Add optional parameters if specified
        if handler_config.rotation:
            handler_kwargs["rotation"] = handler_config.rotation
        if handler_config.retention:
            handler_kwargs["retention"] = handler_config.retention  
        if handler_config.compression:
            handler_kwargs["compression"] = handler_config.compression
        if handler_config.serialize:
            handler_kwargs["serialize"] = handler_config.serialize
            
        handler_id = logger.add(**handler_kwargs)
        self._handlers.append(handler_id)
        
    def _add_default_handlers(self) -> None:
        """Add default handlers based on configuration."""
        # Console handler
        console_handler = LogHandlerConfig(
            sink=sys.stderr,
            level=self.config.level,
            format=self._get_format(),
            serialize=(self.config.format == LogFormat.JSON),
        )
        self._add_handler(console_handler)
        
        # File handler if log_file is specified
        if self.config.log_file:
            file_handler = LogHandlerConfig(
                sink=str(self.config.log_file),
                level=self.config.level,
                format=self._get_format(),
                rotation=self.config.max_file_size,
                retention=f"{self.config.backup_count} files",
                compression="gz",
                serialize=(self.config.format in [LogFormat.JSON, LogFormat.STRUCTURED]),
            )
            self._add_handler(file_handler)
            
    def _get_format(self) -> str:
        """Get log format string based on configuration."""
        if self.config.format == LogFormat.JSON:
            return self._get_json_format()
        elif self.config.format == LogFormat.STRUCTURED:
            return self._get_structured_format()
        else:
            return self._get_console_format()
            
    def _get_console_format(self) -> str:
        """Get human-readable console format."""
        base_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
        )
        
        if self.config.enable_caller_info:
            base_format += "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            
        base_format += "<level>{message}</level>"
        
        if self.config.enable_process_info:
            base_format += " | <dim>PID:{process}</dim>"
            
        return base_format
        
    def _get_json_format(self) -> str:
        """Get JSON format for structured logging."""
        # For JSON format, we use serialize=True in the handler config
        # which makes loguru automatically serialize to JSON
        return "{message}"
        
    def _get_structured_format(self) -> str:
        """Get structured format (JSON-like but more readable)."""
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | "
            "{message} | {{process={process}, thread={thread}, extra={extra}}}"
        )
        
    def _configure_correlation(self) -> None:
        """Configure correlation context integration."""
        def correlation_filter(record):
            """Add correlation context to log record."""
            record["extra"]["correlation_id"] = correlation_id_ctx.get("")
            record["extra"]["user_id"] = user_id_ctx.get("")
            record["extra"]["request_id"] = request_id_ctx.get("")
            return True
            
        # Apply correlation filter - configure function is handled in get_logger method
        
    def set_level(self, level: LogLevel) -> None:
        """Change global log level."""
        self.config.level = level
        # Update all handlers
        for handler_id in self._handlers:
            logger.remove(handler_id)
        self._handlers.clear()
        
        if self.config.handlers:
            for handler_config in self.config.handlers:
                handler_config.level = level
                self._add_handler(handler_config)
        else:
            self._add_default_handlers()
            
    def add_handler(
        self,
        sink: Union[str, object],
        level: LogLevel = LogLevel.INFO,
        format_type: Optional[LogFormat] = None,
        **kwargs,
    ) -> None:
        """Add a new log handler."""
        handler_config = LogHandlerConfig(
            sink=sink,
            level=level,
            format=self._get_format() if format_type is None else self._format_for_type(format_type),
            **kwargs,
        )
        self._add_handler(handler_config)
        
    def _format_for_type(self, format_type: LogFormat) -> str:
        """Get format string for specific format type."""
        original_format = self.config.format
        self.config.format = format_type
        format_str = self._get_format()
        self.config.format = original_format
        return format_str
        
    def create_context(
        self,
        correlation_id: str = "",
        user_id: str = "",
        request_id: str = "",
        **kwargs,
    ) -> LogContext:
        """Create a new log context."""
        return LogContext(
            correlation_id=correlation_id,
            user_id=user_id,
            request_id=request_id,
            extra=kwargs,
        )
        
    def set_context(self, context: LogContext) -> None:
        """Set context variables for correlation tracking."""
        if context.correlation_id:
            correlation_id_ctx.set(context.correlation_id)
        if context.user_id:
            user_id_ctx.set(context.user_id)
        if context.request_id:
            request_id_ctx.set(context.request_id)
            
    def clear_context(self) -> None:
        """Clear all context variables."""
        correlation_id_ctx.set("")
        user_id_ctx.set("")
        request_id_ctx.set("")
        
    def get_logger(self, name: str) -> object:
        """Get a logger instance with the given name."""
        if self.config.enable_correlation:
            return logger.bind(
                component=name,
                correlation_id=correlation_id_ctx.get(""),
                user_id=user_id_ctx.get(""),
                request_id=request_id_ctx.get(""),
            )
        else:
            return logger.bind(component=name)
        
    def shutdown(self) -> None:
        """Shutdown logging system and cleanup resources."""
        if self._initialized:
            for handler_id in self._handlers:
                logger.remove(handler_id)
            self._handlers.clear()
            self._initialized = False
            logger.info("LoggingManager shutdown complete")


# Global logging manager instance
_logging_manager: Optional[LoggingManager] = None


def get_logging_manager() -> LoggingManager:
    """Get the global logging manager instance."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
        _logging_manager.initialize()
    return _logging_manager


def setup_logging(
    level: LogLevel = LogLevel.INFO,
    format_type: LogFormat = LogFormat.CONSOLE,
    log_file: Optional[Path] = None,
    enable_correlation: bool = True,
) -> LoggingManager:
    """
    Setup logging with common configuration.
    
    Args:
        level: Global log level
        format_type: Log output format
        log_file: Optional log file path
        enable_correlation: Enable correlation tracking
        
    Returns:
        Configured LoggingManager instance
    """
    config = LoggingConfig(
        level=level,
        format=format_type,
        log_file=log_file,
        enable_correlation=enable_correlation,
    )
    
    global _logging_manager
    _logging_manager = LoggingManager(config)
    _logging_manager.initialize()
    return _logging_manager


def get_logger(name: str) -> object:
    """
    Get a logger instance for the specified component.
    
    Args:
        name: Component name for the logger
        
    Returns:
        Loguru logger instance bound to the component with context
    """
    manager = get_logging_manager()
    if manager.config.enable_correlation:
        return logger.bind(
            component=name,
            correlation_id=correlation_id_ctx.get(""),
            user_id=user_id_ctx.get(""), 
            request_id=request_id_ctx.get(""),
        )
    else:
        return logger.bind(component=name)


# Convenience functions for context management
def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in context."""
    correlation_id_ctx.set(correlation_id)


def set_user_id(user_id: str) -> None:
    """Set user ID in context."""
    user_id_ctx.set(user_id)


def set_request_id(request_id: str) -> None:
    """Set request ID in context."""
    request_id_ctx.set(request_id)


def clear_log_context() -> None:
    """Clear all log context variables."""
    get_logging_manager().clear_context()


# Development and production presets
def setup_development_logging(log_file: Optional[Path] = None) -> LoggingManager:
    """Setup logging optimized for development."""
    return setup_logging(
        level=LogLevel.DEBUG,
        format_type=LogFormat.CONSOLE,
        log_file=log_file,
        enable_correlation=True,
    )


def setup_production_logging(log_file: Path) -> LoggingManager:
    """Setup logging optimized for production."""
    return setup_logging(
        level=LogLevel.INFO,
        format_type=LogFormat.JSON,
        log_file=log_file,
        enable_correlation=True,
    )