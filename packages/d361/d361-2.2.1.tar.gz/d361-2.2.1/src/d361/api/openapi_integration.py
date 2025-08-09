# this_file: external/int_folders/d361/src/d361/api/openapi_integration.py
"""
OpenAPI Integration for Document360 API.

This module provides comprehensive OpenAPI specification fetching, caching, 
and model generation capabilities with:
- Automatic OpenAPI spec retrieval and validation
- Intelligent caching with etag and timestamp-based updates
- Pydantic model generation from OpenAPI schemas
- API client method generation and updates
- Version tracking and change detection
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from loguru import logger
from pydantic import BaseModel, Field, validator

from ..http import UnifiedHttpClient
from .errors import Document360Error, ErrorCategory, ErrorSeverity


class OpenApiConfig(BaseModel):
    """Configuration for OpenAPI integration."""
    
    # API specification URLs
    openapi_url: str = Field(
        default="https://apihub.document360.io/docs/openapi.json",
        description="URL to fetch OpenAPI specification"
    )
    
    backup_urls: List[str] = Field(
        default_factory=lambda: [
            "https://apihub.document360.io/docs/v1/openapi.json",
            "https://developers.document360.io/openapi.json"
        ],
        description="Backup URLs if primary fails"
    )
    
    # Caching configuration
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".d361" / "openapi_cache",
        description="Directory for caching OpenAPI specs"
    )
    
    cache_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Cache TTL in hours"
    )
    
    # Update behavior
    auto_update: bool = Field(
        default=True,
        description="Automatically check for spec updates"
    )
    
    update_check_interval: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Seconds between update checks"
    )
    
    # Model generation
    models_output_dir: Path = Field(
        default_factory=lambda: Path("generated") / "models",
        description="Directory for generated Pydantic models"
    )
    
    generate_models: bool = Field(
        default=False,
        description="Automatically generate Pydantic models"
    )
    
    # Validation settings
    strict_validation: bool = Field(
        default=True,
        description="Enable strict OpenAPI validation"
    )
    
    required_paths: Set[str] = Field(
        default_factory=lambda: {
            "/api/v1/articles",
            "/api/v1/categories",
            "/api/v1/projects"
        },
        description="Required API paths that must exist"
    )


class OpenApiSpec(BaseModel):
    """OpenAPI specification data model."""
    
    # Specification content
    spec: Dict[str, Any] = Field(..., description="OpenAPI specification JSON")
    
    # Metadata
    version: str = Field(..., description="OpenAPI spec version")
    title: str = Field(..., description="API title")
    api_version: str = Field(..., description="API version")
    
    # Caching metadata
    fetched_at: datetime = Field(default_factory=datetime.now, description="When spec was fetched")
    etag: Optional[str] = Field(None, description="HTTP ETag for caching")
    last_modified: Optional[datetime] = Field(None, description="Last modification time")
    content_hash: str = Field(..., description="Hash of spec content")
    source_url: str = Field(..., description="URL where spec was fetched")
    
    @validator('content_hash', pre=True, always=True)
    def generate_content_hash(cls, v, values):
        """Generate hash of spec content."""
        if v:
            return v
        
        spec = values.get('spec', {})
        content = json.dumps(spec, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    @property
    def is_expired(self, ttl_hours: int = 24) -> bool:
        """Check if spec is expired based on TTL."""
        if not self.fetched_at:
            return True
        
        age = datetime.now() - self.fetched_at
        return age > timedelta(hours=ttl_hours)
    
    @property
    def paths(self) -> Dict[str, Any]:
        """Get API paths from spec."""
        return self.spec.get('paths', {})
    
    @property
    def components(self) -> Dict[str, Any]:
        """Get components/schemas from spec."""
        return self.spec.get('components', {})
    
    @property
    def schemas(self) -> Dict[str, Any]:
        """Get schema definitions."""
        return self.components.get('schemas', {})
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Extract all API endpoints with methods."""
        endpoints = []
        
        for path, methods in self.paths.items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoints.append({
                        'path': path,
                        'method': method.upper(),
                        'operation_id': details.get('operationId'),
                        'summary': details.get('summary'),
                        'description': details.get('description'),
                        'parameters': details.get('parameters', []),
                        'responses': details.get('responses', {}),
                        'tags': details.get('tags', [])
                    })
        
        return endpoints
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Extract model definitions for code generation."""
        models = []
        
        for name, schema in self.schemas.items():
            models.append({
                'name': name,
                'schema': schema,
                'properties': schema.get('properties', {}),
                'required': schema.get('required', []),
                'type': schema.get('type', 'object')
            })
        
        return models
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'spec': self.spec,
            'version': self.version,
            'title': self.title,
            'api_version': self.api_version,
            'fetched_at': self.fetched_at.isoformat(),
            'etag': self.etag,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'content_hash': self.content_hash,
            'source_url': self.source_url
        }


class OpenApiIntegration:
    """
    OpenAPI integration for Document360 API.
    
    Provides comprehensive OpenAPI specification management with:
    - Automatic spec fetching with intelligent caching
    - ETag and timestamp-based update detection
    - Pydantic model generation from schemas
    - API client method generation and updates
    - Version tracking and change detection
    """
    
    def __init__(
        self,
        config: Optional[OpenApiConfig] = None,
        http_client: Optional[UnifiedHttpClient] = None
    ):
        """
        Initialize OpenAPI integration.
        
        Args:
            config: OpenAPI configuration
            http_client: HTTP client for fetching specs
        """
        self.config = config or OpenApiConfig()
        self.http_client = http_client or UnifiedHttpClient()
        
        # Ensure cache directory exists
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Internal state
        self._current_spec: Optional[OpenApiSpec] = None
        self._last_check: Optional[datetime] = None
        
        logger.info(
            f"OpenApiIntegration initialized",
            cache_dir=str(self.config.cache_dir),
            auto_update=self.config.auto_update,
            cache_ttl=self.config.cache_ttl_hours
        )
    
    async def get_spec(self, force_refresh: bool = False) -> OpenApiSpec:
        """
        Get OpenAPI specification, fetching if needed.
        
        Args:
            force_refresh: Force refresh from remote
            
        Returns:
            OpenAPI specification
            
        Raises:
            Document360Error: If spec cannot be fetched or is invalid
        """
        # Check if we have a cached spec and it's not expired
        if not force_refresh and self._current_spec and not self._current_spec.is_expired(self.config.cache_ttl_hours):
            return self._current_spec
        
        # Try to load from disk cache first
        if not force_refresh:
            cached_spec = await self._load_cached_spec()
            if cached_spec and not cached_spec.is_expired(self.config.cache_ttl_hours):
                self._current_spec = cached_spec
                return cached_spec
        
        # Fetch from remote
        spec = await self._fetch_spec()
        
        # Cache the spec
        await self._save_cached_spec(spec)
        
        self._current_spec = spec
        return spec
    
    async def _fetch_spec(self) -> OpenApiSpec:
        """Fetch OpenAPI spec from remote URLs."""
        urls_to_try = [self.config.openapi_url] + self.config.backup_urls
        last_exception = None
        
        for url in urls_to_try:
            try:
                logger.info(f"Fetching OpenAPI spec from {url}")
                
                headers = {
                    'Accept': 'application/json',
                    'User-Agent': 'd361-openapi-client/1.0'
                }
                
                # Add etag if we have one
                if self._current_spec and self._current_spec.etag:
                    headers['If-None-Match'] = self._current_spec.etag
                
                response = await self.http_client.get(url, headers=headers)
                
                if response.status_code == 304:
                    # Not modified, use cached version
                    logger.info("OpenAPI spec not modified, using cached version")
                    if self._current_spec:
                        return self._current_spec
                
                if response.status_code != 200:
                    raise Document360Error(
                        f"Failed to fetch OpenAPI spec: HTTP {response.status_code}",
                        category=ErrorCategory.CLIENT_ERROR,
                        severity=ErrorSeverity.HIGH,
                        context={'url': url, 'status': response.status_code}
                    )
                
                # Parse JSON response
                spec_data = response.json_data
                if spec_data is None:
                    # Try to parse manually if httpx didn't parse it
                    try:
                        import json
                        spec_data = json.loads(response.text)
                    except json.JSONDecodeError as e:
                        raise Document360Error(
                            f"Failed to parse JSON response from {url}: {e}",
                            category=ErrorCategory.CLIENT_ERROR,
                            severity=ErrorSeverity.HIGH,
                            context={'url': url, 'response_text': response.text[:500]}
                        )
                
                # Validate basic OpenAPI structure
                await self._validate_spec(spec_data)
                
                # Extract metadata
                info = spec_data.get('info', {})
                
                spec = OpenApiSpec(
                    spec=spec_data,
                    version=spec_data.get('openapi', '3.0.0'),
                    title=info.get('title', 'Document360 API'),
                    api_version=info.get('version', '1.0'),
                    etag=response.headers.get('etag'),
                    source_url=url
                )
                
                # Set last modified from header
                last_modified_header = response.headers.get('last-modified')
                if last_modified_header:
                    from email.utils import parsedate_to_datetime
                    try:
                        spec.last_modified = parsedate_to_datetime(last_modified_header)
                    except Exception:
                        pass
                
                logger.info(
                    f"Successfully fetched OpenAPI spec",
                    title=spec.title,
                    version=spec.api_version,
                    paths=len(spec.paths),
                    schemas=len(spec.schemas)
                )
                
                return spec
                
            except Exception as e:
                logger.warning(f"Failed to fetch from {url}: {e}")
                last_exception = e
                continue
        
        # All URLs failed
        raise Document360Error(
            f"Failed to fetch OpenAPI spec from all URLs: {last_exception}",
            category=ErrorCategory.CLIENT_ERROR,
            severity=ErrorSeverity.HIGH,
            retryable=True,
            context={'urls_tried': urls_to_try}
        )
    
    async def _validate_spec(self, spec_data: Dict[str, Any]) -> None:
        """Validate OpenAPI specification."""
        if not self.config.strict_validation:
            return
        
        # Basic structure validation
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec_data:
                raise Document360Error(
                    f"Invalid OpenAPI spec: missing required field '{field}'",
                    category=ErrorCategory.VALIDATION,
                    severity=ErrorSeverity.HIGH,
                    context={'missing_field': field}
                )
        
        # Check required paths exist
        paths = spec_data.get('paths', {})
        missing_paths = []
        
        for required_path in self.config.required_paths:
            if required_path not in paths:
                missing_paths.append(required_path)
        
        if missing_paths:
            logger.warning(f"OpenAPI spec missing expected paths: {missing_paths}")
            # Don't fail, just warn for flexibility
    
    async def _load_cached_spec(self) -> Optional[OpenApiSpec]:
        """Load OpenAPI spec from disk cache."""
        try:
            cache_file = self.config.cache_dir / "openapi_spec.json"
            
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Reconstruct OpenApiSpec
            spec = OpenApiSpec(
                spec=cached_data['spec'],
                version=cached_data['version'],
                title=cached_data['title'],
                api_version=cached_data['api_version'],
                fetched_at=datetime.fromisoformat(cached_data['fetched_at']),
                etag=cached_data.get('etag'),
                last_modified=datetime.fromisoformat(cached_data['last_modified']) if cached_data.get('last_modified') else None,
                content_hash=cached_data['content_hash'],
                source_url=cached_data['source_url']
            )
            
            logger.debug(f"Loaded cached OpenAPI spec from {cache_file}")
            return spec
            
        except Exception as e:
            logger.warning(f"Failed to load cached OpenAPI spec: {e}")
            return None
    
    async def _save_cached_spec(self, spec: OpenApiSpec) -> None:
        """Save OpenAPI spec to disk cache."""
        try:
            cache_file = self.config.cache_dir / "openapi_spec.json"
            
            with open(cache_file, 'w') as f:
                json.dump(spec.to_dict(), f, indent=2, default=str)
            
            logger.debug(f"Saved OpenAPI spec to cache: {cache_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save OpenAPI spec to cache: {e}")
    
    async def check_for_updates(self) -> bool:
        """
        Check if OpenAPI spec has updates available.
        
        Returns:
            True if updates are available
        """
        if not self.config.auto_update:
            return False
        
        # Check if enough time has passed since last check
        if self._last_check:
            time_since_check = datetime.now() - self._last_check
            if time_since_check.total_seconds() < self.config.update_check_interval:
                return False
        
        self._last_check = datetime.now()
        
        try:
            # Fetch latest spec
            latest_spec = await self._fetch_spec()
            
            # Compare with current spec
            if self._current_spec:
                return latest_spec.content_hash != self._current_spec.content_hash
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to check for OpenAPI spec updates: {e}")
            return False
    
    async def get_endpoint_changes(self, old_spec: OpenApiSpec, new_spec: OpenApiSpec) -> Dict[str, Any]:
        """
        Compare two OpenAPI specs and identify changes.
        
        Args:
            old_spec: Previous OpenAPI specification
            new_spec: New OpenAPI specification
            
        Returns:
            Dictionary with detailed changes
        """
        changes = {
            'version_changed': old_spec.api_version != new_spec.api_version,
            'added_paths': [],
            'removed_paths': [],
            'modified_paths': [],
            'added_schemas': [],
            'removed_schemas': [],
            'modified_schemas': []
        }
        
        # Compare paths
        old_paths = set(old_spec.paths.keys())
        new_paths = set(new_spec.paths.keys())
        
        changes['added_paths'] = list(new_paths - old_paths)
        changes['removed_paths'] = list(old_paths - new_paths)
        
        # Check for modified paths
        common_paths = old_paths & new_paths
        for path in common_paths:
            old_methods = set(old_spec.paths[path].keys())
            new_methods = set(new_spec.paths[path].keys())
            
            if old_methods != new_methods:
                changes['modified_paths'].append({
                    'path': path,
                    'added_methods': list(new_methods - old_methods),
                    'removed_methods': list(old_methods - new_methods)
                })
        
        # Compare schemas
        old_schemas = set(old_spec.schemas.keys())
        new_schemas = set(new_spec.schemas.keys())
        
        changes['added_schemas'] = list(new_schemas - old_schemas)
        changes['removed_schemas'] = list(old_schemas - new_schemas)
        
        # Check for modified schemas (simplified check)
        common_schemas = old_schemas & new_schemas
        for schema_name in common_schemas:
            old_schema_hash = hashlib.sha256(
                json.dumps(old_spec.schemas[schema_name], sort_keys=True).encode()
            ).hexdigest()
            new_schema_hash = hashlib.sha256(
                json.dumps(new_spec.schemas[schema_name], sort_keys=True).encode()
            ).hexdigest()
            
            if old_schema_hash != new_schema_hash:
                changes['modified_schemas'].append(schema_name)
        
        return changes
    
    async def generate_models_script(self, output_file: Path) -> str:
        """
        Generate a script to create Pydantic models from OpenAPI spec.
        
        Args:
            output_file: Where to save the generation script
            
        Returns:
            Generated script content
        """
        spec = await self.get_spec()
        
        script_content = f'''#!/usr/bin/env python3
"""
Generated Pydantic models from Document360 OpenAPI specification.

This file was auto-generated on {datetime.now().isoformat()}
from OpenAPI spec version: {spec.api_version}
Source: {spec.source_url}

DO NOT EDIT THIS FILE MANUALLY - it will be overwritten.
Use the OpenAPI integration to regenerate models when the spec changes.
"""

from datamodel_code_generator import generate

# OpenAPI spec content hash: {spec.content_hash}
SPEC_VERSION = "{spec.api_version}"
SPEC_HASH = "{spec.content_hash}"

def generate_models():
    """Generate Pydantic models from OpenAPI spec."""
    import json
    from pathlib import Path
    
    # OpenAPI specification
    spec = {json.dumps(spec.spec, indent=4)}
    
    # Save spec to temporary file
    spec_file = Path("/tmp/openapi_spec.json")
    with open(spec_file, "w") as f:
        json.dump(spec, f, indent=2)
    
    # Generate models
    output_dir = Path("{self.config.models_output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    models_file = output_dir / "document360_models.py"
    
    generate(
        input_=spec_file,
        output=models_file,
        input_file_type="openapi",
        use_double_quotes=True,
        use_schema_description=True,
        use_field_description=True,
        use_default_kwarg=True,
        use_union_operator=True,
        target_python_version="3.12",
        use_standard_collections=True,
    )
    
    print(f"Generated Pydantic models: {{models_file}}")
    print(f"OpenAPI spec version: {spec.api_version}")
    print(f"Generated at: {datetime.now().isoformat()}")
    
    # Cleanup
    spec_file.unlink()

if __name__ == "__main__":
    generate_models()
'''
        
        # Save script
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(script_content)
        
        # Make executable
        output_file.chmod(0o755)
        
        logger.info(f"Generated model generation script: {output_file}")
        return script_content
    
    async def get_api_summary(self) -> Dict[str, Any]:
        """Get summary of API capabilities from OpenAPI spec."""
        spec = await self.get_spec()
        endpoints = spec.get_endpoints()
        
        # Group by tags/categories
        by_tags = {}
        for endpoint in endpoints:
            tags = endpoint.get('tags', ['Uncategorized'])
            for tag in tags:
                if tag not in by_tags:
                    by_tags[tag] = []
                by_tags[tag].append(endpoint)
        
        return {
            'api_title': spec.title,
            'api_version': spec.api_version,
            'openapi_version': spec.version,
            'total_endpoints': len(endpoints),
            'total_schemas': len(spec.schemas),
            'endpoints_by_tag': {
                tag: len(endpoints) 
                for tag, endpoints in by_tags.items()
            },
            'available_methods': list(set(
                endpoint['method'] for endpoint in endpoints
            )),
            'last_updated': spec.fetched_at.isoformat(),
            'spec_hash': spec.content_hash
        }
    
    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if self.http_client:
            await self.http_client.close()
        
        logger.debug("OpenApiIntegration closed")