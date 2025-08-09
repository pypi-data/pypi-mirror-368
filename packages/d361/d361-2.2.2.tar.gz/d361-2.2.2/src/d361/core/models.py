# this_file: external/int_folders/d361/src/d361/core/models.py
"""
Canonical data models for the d361 package.

These Pydantic v2 models serve as the single source of truth for all data structures
in the hexagonal architecture, ensuring consistent data representation across all
providers and adapters.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Union

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ContentType(str, Enum):
    """Enumeration of supported content types."""
    
    ARTICLE = "article"
    CATEGORY = "category"
    PROJECT = "project"
    ATTACHMENT = "attachment"


class PublishStatus(str, Enum):
    """Enumeration of publication statuses."""
    
    DRAFT = "draft"
    PUBLISHED = "published" 
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"
    SCHEDULED = "scheduled"


class Article(BaseModel):
    """Canonical article model representing a Document360 article.
    
    This model serves as the single source of truth for article data,
    regardless of the source provider (API, archive, scraper).
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        frozen=False,  # Allow modification for transformations
    )

    # Core identifiers
    id: Union[int, str] = Field(..., description="Unique article identifier (integer or UUID string)")
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    slug: str = Field("", description="URL-friendly version of the title")
    
    # Content
    content: str = Field("", description="Article content in HTML format")
    content_markdown: str = Field("", description="Article content in Markdown format")
    excerpt: str = Field("", max_length=1000, description="Article excerpt or summary")
    
    # Categorization and structure
    category_id: Union[int, str] = Field(..., description="Parent category identifier (integer or UUID string)")
    order: int = Field(0, ge=0, description="Display order within category")
    status: PublishStatus = Field(PublishStatus.DRAFT, description="Publication status")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    published_at: datetime | None = Field(None, description="Publication timestamp")
    
    # Author and attribution
    author_id: Union[int, str, None] = Field(None, description="Author identifier (integer or UUID string)")
    author_name: str = Field("", description="Author display name")
    author_email: str = Field("", description="Author email address")
    
    # SEO and metadata
    meta_title: str = Field("", max_length=100, description="SEO meta title")
    meta_description: str = Field("", max_length=300, description="SEO meta description")
    tags: list[str] = Field(default_factory=list, description="Article tags")
    
    # Document360-specific fields
    version_id: Union[int, str, None] = Field(None, description="Version identifier (integer or UUID string)")
    language_code: str = Field("en", description="Content language code")
    is_public: bool = Field(True, description="Whether article is publicly accessible")
    
    # Additional metadata and custom fields
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    custom_fields: dict[str, Any] = Field(default_factory=dict, description="Custom field values")
    
    # Computed properties
    @computed_field
    @property
    def word_count(self) -> int:
        """Calculate word count from content."""
        if self.content_markdown:
            return len(self.content_markdown.split())
        elif self.content:
            # Strip HTML tags for word count
            import re
            clean_text = re.sub(r'<[^>]+>', '', self.content)
            return len(clean_text.split())
        return 0
    
    @computed_field
    @property
    def reading_time_minutes(self) -> int:
        """Estimate reading time in minutes (assuming 200 words per minute)."""
        return max(1, self.word_count // 200)
    
    @computed_field
    @property
    def is_published(self) -> bool:
        """Check if article is in published state."""
        return self.status == PublishStatus.PUBLISHED
    
    def __str__(self) -> str:
        return f"Article(id={self.id}, title='{self.title[:50]}{'...' if len(self.title) > 50 else ''}')"


class Category(BaseModel):
    """Canonical category model representing a Document360 category.
    
    Categories provide hierarchical organization for articles and can contain
    subcategories to create a nested structure.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        frozen=False,
    )

    # Core identifiers
    id: Union[int, str] = Field(..., description="Unique category identifier (integer or UUID string)")
    name: str = Field(..., min_length=1, max_length=200, description="Category name")
    slug: str = Field("", description="URL-friendly version of the name")
    
    # Hierarchy and structure
    parent_id: Union[int, str, None] = Field(None, description="Parent category identifier (integer or UUID string)")
    order: int = Field(0, ge=0, description="Display order within parent")
    level: int = Field(0, ge=0, description="Hierarchy level (0 = root)")
    path: str = Field("", description="Full hierarchical path")
    
    # Content and description
    description: str = Field("", max_length=1000, description="Category description")
    icon: str = Field("", description="Icon identifier or URL")
    color: str = Field("", pattern=r"^#[0-9A-Fa-f]{6}$|^$", description="Hex color code")
    
    # Visibility and access
    is_public: bool = Field(True, description="Whether category is publicly accessible")
    status: PublishStatus = Field(PublishStatus.PUBLISHED, description="Publication status")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    
    # Statistics (populated by providers when available)
    article_count: int = Field(0, ge=0, description="Number of articles in this category")
    subcategory_count: int = Field(0, ge=0, description="Number of direct subcategories")
    
    @computed_field
    @property
    def is_root_category(self) -> bool:
        """Check if this is a root-level category."""
        return self.parent_id is None
    
    @computed_field
    @property
    def full_name(self) -> str:
        """Get the full hierarchical name."""
        if self.path:
            return self.path.replace("/", " > ")
        return self.name
    
    def __str__(self) -> str:
        return f"Category(id={self.id}, name='{self.name}', level={self.level})"


class ProjectVersion(BaseModel):
    """Canonical project version model representing Document360 project metadata.
    
    This model contains version information and settings for a Document360 project.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=False,
    )

    # Version identification
    id: int = Field(..., description="Unique version identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Version name")
    version_number: str = Field(..., description="Version number (e.g., '1.0.0')")
    is_default: bool = Field(False, description="Whether this is the default version")
    
    # Project information
    project_id: int = Field(..., description="Parent project identifier")
    project_name: str = Field("", description="Project name")
    project_slug: str = Field("", description="Project URL slug")
    
    # Timestamps and lifecycle
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    published_at: datetime | None = Field(None, description="Publication timestamp")
    
    # Configuration
    language_code: str = Field("en", description="Default language code")
    timezone: str = Field("UTC", description="Project timezone")
    is_public: bool = Field(True, description="Whether version is publicly accessible")
    
    # SEO and branding
    site_title: str = Field("", description="Site title for SEO")
    site_description: str = Field("", description="Site description for SEO")
    favicon_url: str = Field("", description="Favicon URL")
    logo_url: str = Field("", description="Logo URL")
    
    # Theme and styling
    theme_name: str = Field("default", description="Theme identifier")
    custom_css: str = Field("", description="Custom CSS styles")
    custom_js: str = Field("", description="Custom JavaScript code")
    
    # Analytics and tracking
    google_analytics_id: str = Field("", description="Google Analytics tracking ID")
    custom_tracking_code: str = Field("", description="Custom tracking/analytics code")
    
    # API and integration settings
    api_base_url: str = Field("", description="Base URL for API access")
    webhook_urls: list[str] = Field(default_factory=list, description="Webhook endpoints")
    
    # Statistics
    total_articles: int = Field(0, ge=0, description="Total number of articles")
    total_categories: int = Field(0, ge=0, description="Total number of categories")
    
    # Additional metadata
    metadata: dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    
    @computed_field
    @property
    def full_project_name(self) -> str:
        """Get the full project name with version."""
        return f"{self.project_name} (v{self.version_number})"
    
    def __str__(self) -> str:
        return f"ProjectVersion(id={self.id}, name='{self.name}', version='{self.version_number}')"


class SearchResult(BaseModel):
    """Model for search results containing multiple content types."""

    model_config = ConfigDict(use_enum_values=True)

    query: str = Field(..., description="Original search query")
    total_results: int = Field(0, ge=0, description="Total number of results")
    results: list[Article | Category] = Field(default_factory=list, description="Search results")
    took_ms: int = Field(0, ge=0, description="Search time in milliseconds")
    
    # Faceting and filtering
    facets: dict[str, dict[str, int]] = Field(default_factory=dict, description="Search facets")
    filters_applied: dict[str, Any] = Field(default_factory=dict, description="Applied filters")
    
    @computed_field
    @property
    def has_results(self) -> bool:
        """Check if search returned any results."""
        return self.total_results > 0
    
    def __str__(self) -> str:
        return f"SearchResult(query='{self.query}', results={self.total_results})"


class BulkOperation(BaseModel):
    """Model for tracking bulk operations on content."""

    model_config = ConfigDict(use_enum_values=True)

    operation_id: str = Field(..., description="Unique operation identifier")
    operation_type: str = Field(..., description="Type of operation (create, update, delete)")
    total_items: int = Field(0, ge=0, description="Total number of items to process")
    completed_items: int = Field(0, ge=0, description="Number of completed items")
    failed_items: int = Field(0, ge=0, description="Number of failed items")
    
    started_at: datetime = Field(..., description="Operation start time")
    completed_at: datetime | None = Field(None, description="Operation completion time")
    
    errors: list[str] = Field(default_factory=list, description="Error messages")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    
    @computed_field
    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    @computed_field
    @property
    def is_completed(self) -> bool:
        """Check if operation is completed."""
        return self.completed_at is not None
    
    @computed_field
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        total_processed = self.completed_items + self.failed_items
        if total_processed == 0:
            return 0.0
        return (self.completed_items / total_processed) * 100
    
    def __str__(self) -> str:
        return f"BulkOperation(id='{self.operation_id}', progress={self.progress_percentage:.1f}%)"