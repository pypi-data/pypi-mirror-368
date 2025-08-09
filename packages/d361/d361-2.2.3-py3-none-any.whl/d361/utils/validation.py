# this_file: external/int_folders/d361/src/d361/utils/validation.py
"""
Pydantic v2 Migration Strategy and Validation Utilities.

This module provides comprehensive validation utilities, migration helpers,
and decorators to support the transition from Pydantic v1 to v2 and enhance
data validation capabilities across the d361 library.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from urllib.parse import urlparse

from loguru import logger
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

# Try to import email and URL types, fallback if not available
try:
    from pydantic import EmailStr, HttpUrl
except ImportError:
    try:
        from pydantic.types import EmailStr, HttpUrl
    except ImportError:
        # Define fallback types if pydantic email/url validation not available
        EmailStr = str
        HttpUrl = str

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])

class ValidationException(Exception):
    """Enhanced validation error with detailed context."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None, errors: Optional[List[Dict]] = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.errors = errors or []


class ValidationHelper:
    """
    Comprehensive validation helper for common data validation tasks.
    
    Provides utilities for URL validation, date formatting, file path validation,
    email validation, and other common patterns used throughout the d361 library.
    """
    
    # Common regex patterns
    SLUG_PATTERN = re.compile(r'^[a-z0-9-_]+$')
    VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9\-\.]+)?$')
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
    API_TOKEN_PATTERN = re.compile(r'^[A-Za-z0-9_\-]{20,}$')
    
    @classmethod
    def validate_url(cls, value: Any, allow_relative: bool = False) -> str:
        """
        Validate URL format with optional relative URL support.
        
        Args:
            value: URL string to validate
            allow_relative: Whether to allow relative URLs
            
        Returns:
            Validated URL string
            
        Raises:
            ValidationException: If URL format is invalid
        """
        if not isinstance(value, str):
            raise ValidationException("URL must be a string", value=value)
        
        if not value.strip():
            raise ValidationException("URL cannot be empty", value=value)
        
        # Handle relative URLs
        if allow_relative and not value.startswith(('http://', 'https://')):
            return value.strip()
        
        try:
            # Use pydantic's HttpUrl for validation
            from pydantic import HttpUrl
            HttpUrl(value)
            return value.strip()
        except Exception as e:
            raise ValidationException(f"Invalid URL format: {value}", value=value) from e
    
    @classmethod
    def validate_email(cls, value: Any) -> str:
        """
        Validate email address format.
        
        Args:
            value: Email string to validate
            
        Returns:
            Validated email string
            
        Raises:
            ValidationException: If email format is invalid
        """
        if not isinstance(value, str):
            raise ValidationException("Email must be a string", value=value)
        
        try:
            # Use pydantic's EmailStr for validation
            EmailStr._validate(value, None)
            return value.strip().lower()
        except Exception as e:
            raise ValidationException(f"Invalid email format: {value}", value=value) from e
    
    @classmethod
    def validate_slug(cls, value: Any, allow_empty: bool = False) -> str:
        """
        Validate slug format (lowercase alphanumeric with hyphens and underscores).
        
        Args:
            value: Slug string to validate
            allow_empty: Whether to allow empty slugs
            
        Returns:
            Validated slug string
            
        Raises:
            ValidationException: If slug format is invalid
        """
        if not isinstance(value, str):
            raise ValidationException("Slug must be a string", value=value)
        
        value = value.strip()
        
        if not value and not allow_empty:
            raise ValidationException("Slug cannot be empty", value=value)
        
        if value and not cls.SLUG_PATTERN.match(value):
            raise ValidationException(
                "Slug must contain only lowercase letters, numbers, hyphens, and underscores",
                value=value
            )
        
        return value
    
    @classmethod
    def validate_version(cls, value: Any) -> str:
        """
        Validate semantic version format (e.g., 1.2.3, 1.0.0-beta.1).
        
        Args:
            value: Version string to validate
            
        Returns:
            Validated version string
            
        Raises:
            ValidationException: If version format is invalid
        """
        if not isinstance(value, str):
            raise ValidationException("Version must be a string", value=value)
        
        value = value.strip()
        
        if not cls.VERSION_PATTERN.match(value):
            raise ValidationException(
                "Version must follow semantic versioning (e.g., 1.2.3)",
                value=value
            )
        
        return value
    
    @classmethod
    def validate_uuid(cls, value: Any) -> str:
        """
        Validate UUID format.
        
        Args:
            value: UUID string to validate
            
        Returns:
            Validated UUID string in lowercase
            
        Raises:
            ValidationException: If UUID format is invalid
        """
        if not isinstance(value, str):
            raise ValidationException("UUID must be a string", value=value)
        
        value = value.strip().lower()
        
        if not cls.UUID_PATTERN.match(value):
            raise ValidationException(
                "UUID must be in format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                value=value
            )
        
        return value
    
    @classmethod
    def validate_api_token(cls, value: Any, min_length: int = 20) -> str:
        """
        Validate API token format.
        
        Args:
            value: API token string to validate
            min_length: Minimum token length
            
        Returns:
            Validated API token string
            
        Raises:
            ValidationException: If token format is invalid
        """
        if not isinstance(value, str):
            raise ValidationException("API token must be a string", value=value)
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationException(
                f"API token must be at least {min_length} characters long",
                value="[REDACTED]"
            )
        
        if not cls.API_TOKEN_PATTERN.match(value):
            raise ValidationException(
                "API token must contain only letters, numbers, hyphens, and underscores",
                value="[REDACTED]"
            )
        
        return value
    
    @classmethod
    def validate_file_path(cls, value: Any, must_exist: bool = False, must_be_file: bool = True) -> Path:
        """
        Validate file path.
        
        Args:
            value: File path to validate
            must_exist: Whether the path must exist on the filesystem
            must_be_file: Whether the path must be a file (not directory)
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationException: If path is invalid
        """
        if isinstance(value, str):
            path = Path(value)
        elif isinstance(value, Path):
            path = value
        else:
            raise ValidationException("File path must be a string or Path object", value=value)
        
        if must_exist:
            if not path.exists():
                raise ValidationException(f"Path does not exist: {path}", value=str(path))
            
            if must_be_file and not path.is_file():
                raise ValidationException(f"Path is not a file: {path}", value=str(path))
        
        return path.resolve()
    
    @classmethod
    def validate_date_string(cls, value: Any, format: str = "%Y-%m-%d") -> datetime:
        """
        Validate and parse date string.
        
        Args:
            value: Date string to validate
            format: Expected date format (strftime format)
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValidationException: If date format is invalid
        """
        if not isinstance(value, str):
            raise ValidationException("Date must be a string", value=value)
        
        try:
            return datetime.strptime(value.strip(), format).replace(tzinfo=timezone.utc)
        except ValueError as e:
            raise ValidationException(
                f"Invalid date format. Expected {format}, got: {value}",
                value=value
            ) from e
    
    @classmethod
    def validate_json_dict(cls, value: Any, required_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate JSON dictionary with optional required keys.
        
        Args:
            value: Dictionary to validate
            required_keys: List of required keys
            
        Returns:
            Validated dictionary
            
        Raises:
            ValidationException: If validation fails
        """
        if not isinstance(value, dict):
            raise ValidationException("Value must be a dictionary", value=value)
        
        if required_keys:
            missing_keys = [key for key in required_keys if key not in value]
            if missing_keys:
                raise ValidationException(
                    f"Missing required keys: {missing_keys}",
                    value=list(value.keys())
                )
        
        return value
    
    @classmethod
    def clean_html_content(cls, value: Any, allow_basic_tags: bool = True) -> str:
        """
        Clean HTML content for safe storage and display.
        
        Args:
            value: HTML content string
            allow_basic_tags: Whether to allow basic HTML tags
            
        Returns:
            Cleaned HTML string
            
        Raises:
            ValidationException: If input is not a string
        """
        if not isinstance(value, str):
            raise ValidationException("HTML content must be a string", value=value)
        
        # Basic HTML cleaning - in production, use a proper HTML sanitizer like bleach
        content = value.strip()
        
        if not allow_basic_tags:
            # Strip all HTML tags
            import html
            content = html.escape(content)
        
        return content


# Validation decorators for common patterns

def validate_url_field(allow_relative: bool = False):
    """Field validator decorator for URL validation."""
    def validator(cls, v):
        return ValidationHelper.validate_url(v, allow_relative=allow_relative)
    return field_validator('url', mode='before')(validator)


def validate_email_field():
    """Field validator decorator for email validation."""
    def validator(cls, v):
        return ValidationHelper.validate_email(v)
    return field_validator('email', mode='before')(validator)


def validate_slug_field(allow_empty: bool = False):
    """Field validator decorator for slug validation."""
    def validator(cls, v):
        return ValidationHelper.validate_slug(v, allow_empty=allow_empty)
    return field_validator('slug', mode='before')(validator)


def validate_api_token_field(min_length: int = 20):
    """Field validator decorator for API token validation."""
    def validator(cls, v):
        return ValidationHelper.validate_api_token(v, min_length=min_length)
    return field_validator('api_token', mode='before')(validator)


def validate_function_inputs(**field_validators: Dict[str, Callable]):
    """
    Decorator to validate function inputs using ValidationHelper.
    
    Args:
        **field_validators: Mapping of parameter names to validation functions
        
    Example:
        @validate_function_inputs(
            email=ValidationHelper.validate_email,
            url=lambda x: ValidationHelper.validate_url(x, allow_relative=True)
        )
        def process_data(email: str, url: str):
            # Function inputs are automatically validated
            pass
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature for parameter mapping
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate specified parameters
            for param_name, validator in field_validators.items():
                if param_name in bound_args.arguments:
                    try:
                        validated_value = validator(bound_args.arguments[param_name])
                        bound_args.arguments[param_name] = validated_value
                    except ValidationException as e:
                        logger.error(f"Validation failed for parameter '{param_name}': {e}")
                        raise
            
            return func(*bound_args.args, **bound_args.kwargs)
        
        return wrapper
    return decorator


# Pydantic v2 Migration Helpers

class MigrationHelper:
    """
    Helper class for migrating from Pydantic v1 to v2.
    
    Provides utilities for updating model definitions, field configurations,
    and validation patterns to be compatible with Pydantic v2.
    """
    
    @staticmethod
    def convert_v1_field_to_v2(
        v1_field: Any,
        field_name: str,
        default: Any = None,
        description: Optional[str] = None,
        **extra_kwargs
    ):
        """
        Convert Pydantic v1 Field definition to v2 Field.
        
        Args:
            v1_field: Original v1 field definition
            field_name: Name of the field
            default: Default value
            description: Field description
            **extra_kwargs: Additional field parameters
            
        Returns:
            Pydantic v2 Field definition
        """
        # Extract common field properties from v1 field
        field_kwargs = extra_kwargs.copy()
        
        if description:
            field_kwargs['description'] = description
        
        # Handle common v1 -> v2 migrations
        if hasattr(v1_field, 'min_length'):
            field_kwargs['min_length'] = v1_field.min_length
        if hasattr(v1_field, 'max_length'):
            field_kwargs['max_length'] = v1_field.max_length
        if hasattr(v1_field, 'regex'):
            field_kwargs['pattern'] = v1_field.regex
        
        return Field(default=default, **field_kwargs)
    
    @staticmethod
    def create_migration_report(model_class: Type[BaseModel]) -> Dict[str, Any]:
        """
        Generate a migration report for a Pydantic model.
        
        Args:
            model_class: Pydantic model class to analyze
            
        Returns:
            Dictionary containing migration information
        """
        report = {
            'model_name': model_class.__name__,
            'fields': {},
            'validators': [],
            'recommendations': []
        }
        
        # Analyze model fields
        if hasattr(model_class, 'model_fields'):
            # v2 model
            for field_name, field_info in model_class.model_fields.items():
                report['fields'][field_name] = {
                    'type': str(field_info.annotation) if hasattr(field_info, 'annotation') else 'unknown',
                    'required': field_info.is_required() if hasattr(field_info, 'is_required') else True,
                    'default': field_info.default if hasattr(field_info, 'default') else None,
                }
        
        # Check for common v1 patterns that need updating
        if hasattr(model_class, '__validators__'):
            report['recommendations'].append("Update __validators__ to use @field_validator or @model_validator")
        
        if hasattr(model_class, '__root__'):
            report['recommendations'].append("Replace __root__ with RootModel for v2")
        
        return report


# Enhanced base models for common patterns

class ValidatedBaseModel(BaseModel):
    """
    Enhanced base model with common validation patterns.
    
    Provides automatic validation for common field types and
    enhanced error handling with detailed context.
    """
    
    model_config = {
        'extra': 'forbid',
        'validate_assignment': True,
        'use_enum_values': True,
        'json_encoders': {
            datetime: lambda v: v.isoformat(),
            Path: str,
        }
    }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidatedBaseModel':
        """
        Create model instance from dictionary with enhanced error handling.
        
        Args:
            data: Dictionary data to convert
            
        Returns:
            Model instance
            
        Raises:
            ValidationException: If validation fails with detailed context
        """
        try:
            return cls(**data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append({
                    'field': '.'.join(str(x) for x in error['loc']),
                    'message': error['msg'],
                    'type': error['type'],
                    'input': error.get('input')
                })
            
            raise ValidationException(
                f"Validation failed for {cls.__name__}",
                errors=errors
            ) from e
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """
        Convert model to dictionary with customizable options.
        
        Args:
            exclude_none: Whether to exclude None values
            
        Returns:
            Dictionary representation
        """
        return self.model_dump(exclude_none=exclude_none)
    
    @model_validator(mode='before')
    def validate_dict_input(cls, values):
        """Ensure input is processed correctly."""
        if isinstance(values, dict):
            # Clean up common issues
            cleaned = {}
            for key, value in values.items():
                # Convert empty strings to None for optional fields
                if value == '' and key in cls.model_fields:
                    field_info = cls.model_fields[key]
                    if not field_info.is_required():
                        value = None
                cleaned[key] = value
            return cleaned
        return values


# Example migration-ready models

class Article(ValidatedBaseModel):
    """
    Enhanced Article model with comprehensive validation.
    
    Demonstrates Pydantic v2 patterns and validation best practices.
    """
    
    id: str = Field(..., description="Unique article identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Article title")
    slug: str = Field(..., description="URL-friendly article slug")
    content: str = Field(..., min_length=1, description="Article content")
    url: Optional[HttpUrl] = Field(None, description="Article URL")
    author_email: Optional[EmailStr] = Field(None, description="Author email address")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        return ValidationHelper.validate_slug(v)
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if v:
            return [ValidationHelper.validate_slug(tag) for tag in v]
        return v
    
    @model_validator(mode='after')
    def validate_article_consistency(self):
        """Ensure article data is consistent."""
        if self.published_at and not self.author_email:
            logger.warning(f"Published article {self.id} has no author email")
        return self