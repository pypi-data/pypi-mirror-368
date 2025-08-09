# this_file: external/int_folders/d361/src/d361/config/environment.py
"""
Environment configuration loading with support for multiple sources.

This module provides the EnvironmentLoader class for loading configuration
from .env files, system environment variables, and configuration files with
hierarchical merging and hot-reloading capabilities for development.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from threading import Thread, Event
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from loguru import logger
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

from .schema import AppConfig, Environment
from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class ConfigFileHandler(FileSystemEventHandler):
    """Handler for configuration file changes."""
    
    def __init__(self, config_paths: List[Path], callback: Callable[[Path], None]):
        """
        Initialize file change handler.
        
        Args:
            config_paths: List of configuration file paths to monitor
            callback: Callback function when file changes
        """
        self.config_paths = {str(path.resolve()) for path in config_paths}
        self.callback = callback
        super().__init__()
    
    def on_modified(self, event):
        """Handle file modification events."""
        if isinstance(event, FileModifiedEvent) and not event.is_directory:
            file_path = str(Path(event.src_path).resolve())
            if file_path in self.config_paths:
                logger.info(f"Configuration file changed: {event.src_path}")
                self.callback(Path(event.src_path))


class EnvironmentLoader:
    """
    Environment configuration loader with multiple source support.
    
    Provides hierarchical configuration loading from files, environment variables,
    and system settings with hot-reloading capabilities for development environments.
    """
    
    def __init__(
        self,
        base_config_dir: Optional[Path] = None,
        environment_override: Optional[str] = None
    ):
        """
        Initialize environment loader.
        
        Args:
            base_config_dir: Base directory for configuration files
            environment_override: Override environment detection
        """
        self.base_config_dir = base_config_dir or Path.cwd()
        self.environment_override = environment_override
        
        # Hot-reloading state
        self._observer: Optional[Observer] = None
        self._reload_callback: Optional[Callable[[AppConfig], None]] = None
        self._current_config: Optional[AppConfig] = None
        self._stop_event = Event()
        
        # Configuration sources in priority order (highest to lowest)
        self.config_sources: List[str] = [
            "environment_variables",  # Highest priority
            "environment_specific_file", 
            "base_config_file",
            "defaults"  # Lowest priority
        ]
        
        logger.info(
            "EnvironmentLoader initialized",
            base_config_dir=str(self.base_config_dir),
            environment_override=environment_override
        )
    
    def detect_environment(self) -> Environment:
        """
        Detect the current deployment environment.
        
        Returns:
            Detected environment
        """
        if self.environment_override:
            try:
                return Environment(self.environment_override)
            except ValueError:
                logger.warning(f"Invalid environment override: {self.environment_override}")
        
        # Check environment variable
        env_var = os.getenv("D361_ENVIRONMENT", os.getenv("ENVIRONMENT", "")).lower()
        if env_var:
            try:
                return Environment(env_var)
            except ValueError:
                logger.warning(f"Invalid environment from variable: {env_var}")
        
        # Check for environment-specific files
        for env in [Environment.PRODUCTION, Environment.STAGING]:
            env_file = self.base_config_dir / f".env.{env.value}"
            if env_file.exists():
                logger.info(f"Detected environment from file: {env_file}")
                return env
        
        # Default to development
        logger.info("Defaulting to development environment")
        return Environment.DEVELOPMENT
    
    def load_dotenv_file(self, env_file: Path) -> Dict[str, str]:
        """
        Load environment variables from .env file.
        
        Args:
            env_file: Path to .env file
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        if not env_file.exists():
            return env_vars
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        env_vars[key] = value
                    else:
                        logger.warning(f"Invalid line in {env_file}:{line_num}: {line}")
            
            logger.debug(f"Loaded {len(env_vars)} variables from {env_file}")
            
        except Exception as e:
            logger.error(f"Failed to load {env_file}: {e}")
            raise Document360Error(
                f"Failed to load environment file {env_file}: {e}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
        
        return env_vars
    
    def get_config_file_paths(self, environment: Environment) -> List[Path]:
        """
        Get configuration file paths for the environment.
        
        Args:
            environment: Target environment
            
        Returns:
            List of configuration file paths in priority order
        """
        config_paths = []
        
        # Base configuration files
        for filename in ["config.yaml", "config.yml", "config.json"]:
            config_path = self.base_config_dir / filename
            if config_path.exists():
                config_paths.append(config_path)
                break
        
        # Environment-specific configuration files
        for ext in ["yaml", "yml", "json"]:
            env_config_path = self.base_config_dir / f"config.{environment.value}.{ext}"
            if env_config_path.exists():
                config_paths.append(env_config_path)
                break
        
        return config_paths
    
    def get_env_file_paths(self, environment: Environment) -> List[Path]:
        """
        Get .env file paths for the environment.
        
        Args:
            environment: Target environment
            
        Returns:
            List of .env file paths in priority order
        """
        env_paths = []
        
        # Base .env file
        base_env = self.base_config_dir / ".env"
        if base_env.exists():
            env_paths.append(base_env)
        
        # Environment-specific .env file
        env_env = self.base_config_dir / f".env.{environment.value}"
        if env_env.exists():
            env_paths.append(env_env)
        
        # Local development overrides
        if environment == Environment.DEVELOPMENT:
            local_env = self.base_config_dir / ".env.local"
            if local_env.exists():
                env_paths.append(local_env)
        
        return env_paths
    
    def load_from_files(self, environment: Environment) -> Dict[str, Any]:
        """
        Load configuration from files.
        
        Args:
            environment: Target environment
            
        Returns:
            Merged configuration dictionary
        """
        config_data = {}
        
        # Load configuration files
        config_paths = self.get_config_file_paths(environment)
        for config_path in config_paths:
            try:
                file_config = self._load_config_file(config_path)
                config_data.update(file_config)
                logger.debug(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration file {config_path}: {e}")
        
        return config_data
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from a specific file."""
        suffix = config_path.suffix.lower()
        
        if suffix == ".json":
            import json
            with open(config_path, 'r') as f:
                return json.load(f)
        elif suffix in [".yml", ".yaml"]:
            try:
                import yaml
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            except ImportError:
                raise Document360Error(
                    "PyYAML is required to load YAML configuration files",
                    category=ErrorCategory.CONFIGURATION,
                    severity=ErrorSeverity.HIGH
                )
        else:
            raise Document360Error(
                f"Unsupported configuration file format: {suffix}",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.HIGH
            )
    
    def merge_env_vars(self, base_data: Dict[str, Any], environment: Environment) -> Dict[str, Any]:
        """
        Merge environment variables into configuration data.
        
        Args:
            base_data: Base configuration data
            environment: Target environment
            
        Returns:
            Configuration data with environment variables merged
        """
        # Load .env files first
        env_vars = {}
        env_paths = self.get_env_file_paths(environment)
        
        for env_path in env_paths:
            file_env_vars = self.load_dotenv_file(env_path)
            env_vars.update(file_env_vars)
        
        # Apply .env variables to environment first
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        try:
            # Use Pydantic's environment variable parsing
            # This will automatically parse D361_* prefixed variables
            temp_config = AppConfig(**base_data)
            return temp_config.dict()
        finally:
            # Restore original environment
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value
    
    def load_configuration(self, environment: Optional[Environment] = None) -> AppConfig:
        """
        Load complete configuration from all sources.
        
        Args:
            environment: Target environment (auto-detected if None)
            
        Returns:
            Loaded and validated configuration
            
        Raises:
            Document360Error: If configuration loading fails
        """
        try:
            # Detect environment if not provided
            if environment is None:
                environment = self.detect_environment()
            
            logger.info(f"Loading configuration for environment: {environment.value}")
            
            # Start with file-based configuration
            config_data = self.load_from_files(environment)
            
            # Set environment in config data
            config_data["environment"] = environment.value
            
            # Merge environment variables
            config_data = self.merge_env_vars(config_data, environment)
            
            # Create and validate configuration
            config = AppConfig(**config_data)
            
            # Validate configuration
            validation_issues = config.validate_configuration()
            if validation_issues:
                logger.warning(f"Configuration validation issues: {validation_issues}")
                if environment == Environment.PRODUCTION:
                    # Fail fast in production
                    raise Document360Error(
                        f"Configuration validation failed in production: {validation_issues}",
                        category=ErrorCategory.CONFIGURATION,
                        severity=ErrorSeverity.CRITICAL
                    )
            
            self._current_config = config
            logger.info(f"Configuration loaded successfully for {environment.value}")
            
            return config
            
        except Exception as e:
            error_msg = f"Failed to load configuration for {environment}: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.CRITICAL
            )
    
    def start_hot_reload(
        self,
        reload_callback: Callable[[AppConfig], None],
        poll_interval: float = 1.0
    ) -> None:
        """
        Start hot-reloading configuration files for development.
        
        Args:
            reload_callback: Function to call when configuration changes
            poll_interval: Polling interval in seconds
        """
        if self._observer is not None:
            logger.warning("Hot reload already started")
            return
        
        if not self._current_config or self._current_config.is_production():
            logger.info("Hot reload disabled for production environment")
            return
        
        self._reload_callback = reload_callback
        
        # Get files to monitor
        environment = self._current_config.environment
        config_paths = self.get_config_file_paths(environment)
        env_paths = self.get_env_file_paths(environment)
        all_paths = config_paths + env_paths
        
        if not all_paths:
            logger.info("No configuration files to monitor for hot reload")
            return
        
        # Setup file system watcher
        self._observer = Observer()
        handler = ConfigFileHandler(all_paths, self._handle_file_change)
        
        # Watch directories containing config files
        watched_dirs = set()
        for path in all_paths:
            dir_path = path.parent
            if dir_path not in watched_dirs:
                self._observer.schedule(handler, str(dir_path), recursive=False)
                watched_dirs.add(dir_path)
                logger.debug(f"Watching directory for config changes: {dir_path}")
        
        # Start observer
        self._observer.start()
        logger.info(f"Started hot reload monitoring for {len(all_paths)} files")
    
    def stop_hot_reload(self) -> None:
        """Stop hot-reloading configuration files."""
        if self._observer is None:
            return
        
        self._stop_event.set()
        self._observer.stop()
        self._observer.join(timeout=5.0)
        self._observer = None
        self._reload_callback = None
        
        logger.info("Stopped configuration hot reload")
    
    def _handle_file_change(self, file_path: Path) -> None:
        """Handle configuration file changes."""
        if not self._reload_callback or not self._current_config:
            return
        
        try:
            # Small delay to avoid partial file reads
            time.sleep(0.1)
            
            # Reload configuration
            new_config = self.load_configuration(self._current_config.environment)
            
            # Call reload callback
            self._reload_callback(new_config)
            
            logger.info(f"Configuration reloaded due to {file_path} change")
            
        except Exception as e:
            logger.error(f"Failed to reload configuration after {file_path} change: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get summary of configuration loading.
        
        Returns:
            Configuration summary information
        """
        environment = self.detect_environment()
        
        return {
            "environment": environment.value,
            "base_config_dir": str(self.base_config_dir),
            "config_files": [str(p) for p in self.get_config_file_paths(environment)],
            "env_files": [str(p) for p in self.get_env_file_paths(environment)],
            "hot_reload_active": self._observer is not None,
            "sources_priority": self.config_sources
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.stop_hot_reload()