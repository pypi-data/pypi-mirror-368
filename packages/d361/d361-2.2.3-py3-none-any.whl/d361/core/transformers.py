# this_file: external/int_folders/d361/src/d361/core/transformers.py
"""
Data transformation utilities for converting between different data formats.

This module provides centralized transformation logic for converting data from
various sources (API responses, archive metadata, web scraped content) into
the canonical Pydantic models.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .models import Article, Category, ProjectVersion, PublishStatus


class ModelTransformer:
    """Centralized transformer for converting data into canonical models.
    
    This class handles the complex logic of mapping data from different sources
    and formats into our standardized Pydantic models, ensuring data consistency
    across all providers.
    """

    @staticmethod
    def from_api_response(data: dict[str, Any], content_type: str = "article") -> Article | Category | ProjectVersion:
        """Transform API response data into canonical models.
        
        Args:
            data: Raw API response dictionary
            content_type: Type of content ("article", "category", "project")
            
        Returns:
            Canonical model instance
            
        Raises:
            ValueError: If content_type is unsupported or data is invalid
        """
        if content_type == "article":
            return ModelTransformer._transform_api_article(data)
        elif content_type == "category":
            return ModelTransformer._transform_api_category(data)
        elif content_type == "project":
            return ModelTransformer._transform_api_project(data)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

    @staticmethod
    def _transform_api_article(data: dict[str, Any]) -> Article:
        """Transform API article response to canonical Article model."""
        # Handle common API field variations
        article_id = data.get("id") or data.get("article_id") or data.get("Id")
        if not article_id:
            raise ValueError("Article ID is required but not found in API response")

        # Parse timestamps with fallbacks
        created_at = ModelTransformer._parse_timestamp(
            data.get("created_at") or data.get("CreatedAt") or data.get("created_date")
        )
        updated_at = ModelTransformer._parse_timestamp(
            data.get("updated_at") or data.get("UpdatedAt") or data.get("modified_date")
        ) or created_at

        # Handle status mapping
        status_mapping = {
            "published": PublishStatus.PUBLISHED,
            "draft": PublishStatus.DRAFT,
            "archived": PublishStatus.ARCHIVED,
            "under_review": PublishStatus.UNDER_REVIEW,
            "scheduled": PublishStatus.SCHEDULED,
            "1": PublishStatus.PUBLISHED,  # Document360 uses 1 for published
            "0": PublishStatus.DRAFT,      # Document360 uses 0 for draft
            True: PublishStatus.PUBLISHED,
            False: PublishStatus.DRAFT,
        }
        
        raw_status = data.get("status") or data.get("Status") or data.get("is_published")
        status = status_mapping.get(raw_status, PublishStatus.DRAFT)

        return Article(
            id=int(article_id),
            title=str(data.get("title") or data.get("Title") or ""),
            slug=str(data.get("slug") or data.get("Slug") or ""),
            content=str(data.get("content") or data.get("Content") or data.get("body") or ""),
            content_markdown=str(data.get("content_markdown") or data.get("markdown") or ""),
            excerpt=str(data.get("excerpt") or data.get("Excerpt") or data.get("summary") or ""),
            category_id=int(data.get("category_id") or data.get("CategoryId") or data.get("category") or 0),
            order=int(data.get("order") or data.get("Order") or data.get("sort_order") or 0),
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            published_at=ModelTransformer._parse_timestamp(
                data.get("published_at") or data.get("PublishedAt") or data.get("publish_date")
            ),
            author_id=data.get("author_id") or data.get("AuthorId"),
            author_name=str(data.get("author_name") or data.get("AuthorName") or data.get("author") or ""),
            author_email=str(data.get("author_email") or data.get("AuthorEmail") or ""),
            meta_title=str(data.get("meta_title") or data.get("MetaTitle") or data.get("seo_title") or ""),
            meta_description=str(data.get("meta_description") or data.get("MetaDescription") or ""),
            tags=ModelTransformer._parse_tags(data.get("tags") or data.get("Tags") or []),
            version_id=data.get("version_id") or data.get("VersionId"),
            language_code=str(data.get("language_code") or data.get("LanguageCode") or "en"),
            is_public=bool(data.get("is_public", True)),
            metadata=data.get("metadata", {}),
            custom_fields=data.get("custom_fields", {}),
        )

    @staticmethod
    def _transform_api_category(data: dict[str, Any]) -> Category:
        """Transform API category response to canonical Category model."""
        category_id = data.get("id") or data.get("category_id") or data.get("Id")
        if not category_id:
            raise ValueError("Category ID is required but not found in API response")

        created_at = ModelTransformer._parse_timestamp(
            data.get("created_at") or data.get("CreatedAt") or data.get("created_date")
        )
        updated_at = ModelTransformer._parse_timestamp(
            data.get("updated_at") or data.get("UpdatedAt") or data.get("modified_date")
        ) or created_at

        # Handle status mapping for categories
        status_mapping = {
            "published": PublishStatus.PUBLISHED,
            "draft": PublishStatus.DRAFT,
            "archived": PublishStatus.ARCHIVED,
            "1": PublishStatus.PUBLISHED,
            "0": PublishStatus.DRAFT,
            True: PublishStatus.PUBLISHED,
            False: PublishStatus.DRAFT,
        }
        
        raw_status = data.get("status") or data.get("Status") or True
        status = status_mapping.get(raw_status, PublishStatus.PUBLISHED)

        return Category(
            id=int(category_id),
            name=str(data.get("name") or data.get("Name") or ""),
            slug=str(data.get("slug") or data.get("Slug") or ""),
            parent_id=data.get("parent_id") or data.get("ParentId"),
            order=int(data.get("order") or data.get("Order") or data.get("sort_order") or 0),
            level=int(data.get("level") or data.get("Level") or 0),
            path=str(data.get("path") or data.get("Path") or ""),
            description=str(data.get("description") or data.get("Description") or ""),
            icon=str(data.get("icon") or data.get("Icon") or ""),
            color=str(data.get("color") or data.get("Color") or ""),
            is_public=bool(data.get("is_public", True)),
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
            article_count=int(data.get("article_count") or data.get("ArticleCount") or 0),
            subcategory_count=int(data.get("subcategory_count") or data.get("SubcategoryCount") or 0),
        )

    @staticmethod
    def _transform_api_project(data: dict[str, Any]) -> ProjectVersion:
        """Transform API project response to canonical ProjectVersion model."""
        project_id = data.get("id") or data.get("project_id") or data.get("Id")
        if not project_id:
            raise ValueError("Project ID is required but not found in API response")

        created_at = ModelTransformer._parse_timestamp(
            data.get("created_at") or data.get("CreatedAt") or data.get("created_date")
        )
        updated_at = ModelTransformer._parse_timestamp(
            data.get("updated_at") or data.get("UpdatedAt") or data.get("modified_date")
        ) or created_at

        return ProjectVersion(
            id=int(project_id),
            name=str(data.get("name") or data.get("Name") or ""),
            version_number=str(data.get("version_number") or data.get("VersionNumber") or "1.0.0"),
            is_default=bool(data.get("is_default") or data.get("IsDefault", False)),
            project_id=int(data.get("project_id") or data.get("ProjectId") or project_id),
            project_name=str(data.get("project_name") or data.get("ProjectName") or ""),
            project_slug=str(data.get("project_slug") or data.get("ProjectSlug") or ""),
            created_at=created_at,
            updated_at=updated_at,
            published_at=ModelTransformer._parse_timestamp(
                data.get("published_at") or data.get("PublishedAt") or data.get("publish_date")
            ),
            language_code=str(data.get("language_code") or data.get("LanguageCode") or "en"),
            timezone=str(data.get("timezone") or data.get("Timezone") or "UTC"),
            is_public=bool(data.get("is_public", True)),
            site_title=str(data.get("site_title") or data.get("SiteTitle") or ""),
            site_description=str(data.get("site_description") or data.get("SiteDescription") or ""),
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def from_archive_metadata(data: dict[str, Any], content_type: str = "article") -> Article | Category | ProjectVersion:
        """Transform archive metadata into canonical models.
        
        Archive data typically has a different structure than API responses,
        often being flatter and with different field names.
        
        Args:
            data: Archive metadata dictionary
            content_type: Type of content ("article", "category", "project")
            
        Returns:
            Canonical model instance
        """
        if content_type == "article":
            return ModelTransformer._transform_archive_article(data)
        elif content_type == "category":
            return ModelTransformer._transform_archive_category(data)
        elif content_type == "project":
            return ModelTransformer._transform_archive_project(data)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")

    @staticmethod
    def _transform_archive_article(data: dict[str, Any]) -> Article:
        """Transform archive article data to canonical Article model."""
        # Archive data might use different field names
        article_id = data.get("id") or data.get("articleId") or data.get("article_id")
        if not article_id:
            # Try to extract from filename or path if available
            filename = data.get("filename", "")
            match = re.search(r"(\d+)", filename)
            if match:
                article_id = int(match.group(1))
            else:
                raise ValueError("Article ID is required but not found in archive metadata")

        # Archive timestamps might be in different formats
        created_at = ModelTransformer._parse_timestamp(
            data.get("createdAt") or data.get("created") or data.get("date_created")
        )
        updated_at = ModelTransformer._parse_timestamp(
            data.get("updatedAt") or data.get("modified") or data.get("date_modified")
        ) or created_at

        return Article(
            id=int(article_id),
            title=str(data.get("title") or data.get("name") or ""),
            slug=str(data.get("slug") or data.get("url_slug") or ""),
            content=str(data.get("content") or data.get("body") or data.get("html") or ""),
            content_markdown=str(data.get("markdown") or data.get("content_markdown") or ""),
            category_id=int(data.get("categoryId") or data.get("category") or 0),
            status=PublishStatus.PUBLISHED,  # Archive items are typically published
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def _transform_archive_category(data: dict[str, Any]) -> Category:
        """Transform archive category data to canonical Category model."""
        category_id = data.get("id") or data.get("categoryId") or data.get("category_id")
        if not category_id:
            raise ValueError("Category ID is required but not found in archive metadata")

        return Category(
            id=int(category_id),
            name=str(data.get("name") or data.get("title") or ""),
            slug=str(data.get("slug") or data.get("url_slug") or ""),
            parent_id=data.get("parentId") or data.get("parent"),
            created_at=ModelTransformer._parse_timestamp(data.get("created") or data.get("createdAt")),
            updated_at=ModelTransformer._parse_timestamp(data.get("modified") or data.get("updatedAt")),
            status=PublishStatus.PUBLISHED,
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def _transform_archive_project(data: dict[str, Any]) -> ProjectVersion:
        """Transform archive project data to canonical ProjectVersion model."""
        project_id = data.get("id") or data.get("projectId") or data.get("project_id") or 1
        
        return ProjectVersion(
            id=int(project_id),
            name=str(data.get("name") or data.get("title") or "Archived Project"),
            version_number=str(data.get("version") or data.get("version_number") or "1.0.0"),
            project_id=int(project_id),
            project_name=str(data.get("project_name") or data.get("name") or ""),
            created_at=ModelTransformer._parse_timestamp(data.get("created") or data.get("createdAt")),
            updated_at=ModelTransformer._parse_timestamp(data.get("modified") or data.get("updatedAt")),
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def to_legacy_format(model: Article | Category | ProjectVersion, format_name: str) -> dict[str, Any]:
        """Transform canonical models to legacy formats for backward compatibility.
        
        Args:
            model: Canonical model instance
            format_name: Target legacy format ("d361api", "d362a", etc.)
            
        Returns:
            Dictionary in legacy format
        """
        if isinstance(model, Article):
            return ModelTransformer._article_to_legacy(model, format_name)
        elif isinstance(model, Category):
            return ModelTransformer._category_to_legacy(model, format_name)
        elif isinstance(model, ProjectVersion):
            return ModelTransformer._project_to_legacy(model, format_name)
        else:
            raise ValueError(f"Unsupported model type: {type(model)}")

    @staticmethod
    def _article_to_legacy(article: Article, format_name: str) -> dict[str, Any]:
        """Convert Article model to legacy format."""
        base_data = {
            "id": article.id,
            "title": article.title,
            "content": article.content,
            "category_id": article.category_id,
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat(),
            "status": article.status.value,
        }
        
        if format_name == "d361api":
            # d361api format expects different field names
            return {
                "article_id": article.id,
                "article_title": article.title,
                "article_content": article.content,
                "category": article.category_id,
                "published": article.is_published,
                **base_data,
            }
        elif format_name == "d362a":
            # d362a format has its own conventions
            return {
                "Id": article.id,
                "Title": article.title,
                "Content": article.content,
                "CategoryId": article.category_id,
                "IsPublished": article.is_published,
                **base_data,
            }
        else:
            return base_data

    @staticmethod
    def _category_to_legacy(category: Category, format_name: str) -> dict[str, Any]:
        """Convert Category model to legacy format."""
        return {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "order": category.order,
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat(),
        }

    @staticmethod
    def _project_to_legacy(project: ProjectVersion, format_name: str) -> dict[str, Any]:
        """Convert ProjectVersion model to legacy format."""
        return {
            "id": project.id,
            "name": project.name,
            "version": project.version_number,
            "project_id": project.project_id,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime:
        """Parse various timestamp formats into datetime objects.
        
        Args:
            value: Timestamp value (string, int, datetime, etc.)
            
        Returns:
            datetime: Parsed datetime object
        """
        if value is None:
            return datetime.now()
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        
        if isinstance(value, str):
            # Try common timestamp formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO with microseconds
                "%Y-%m-%dT%H:%M:%SZ",     # ISO without microseconds
                "%Y-%m-%dT%H:%M:%S",      # ISO without timezone
                "%Y-%m-%d %H:%M:%S",      # Space separated
                "%Y-%m-%d",               # Date only
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        
        # Fallback to current time if parsing fails
        return datetime.now()

    @staticmethod
    def _parse_tags(tags: Any) -> list[str]:
        """Parse tags from various formats into a list of strings.
        
        Args:
            tags: Tags in various formats (string, list, etc.)
            
        Returns:
            list[str]: List of tag strings
        """
        if not tags:
            return []
        
        if isinstance(tags, list):
            return [str(tag).strip() for tag in tags if tag]
        
        if isinstance(tags, str):
            # Try to split by common delimiters
            for delimiter in [",", ";", "|"]:
                if delimiter in tags:
                    return [tag.strip() for tag in tags.split(delimiter) if tag.strip()]
            return [tags.strip()] if tags.strip() else []
        
        return []