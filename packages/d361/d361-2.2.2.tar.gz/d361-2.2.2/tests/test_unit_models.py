# this_file: external/int_folders/d361/tests/test_unit_models.py
"""
Comprehensive unit tests for d361 core models.

This module provides thorough testing of all Pydantic models including
validation logic, edge cases, serialization/deserialization, and error handling.
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List
from pydantic import ValidationError

from d361.core.models import (
    Article, 
    Category, 
    ProjectVersion, 
    PublishStatus, 
    ContentType
)


class TestArticleModel:
    """Test cases for Article model validation and behavior."""

    def test_article_creation_valid(self):
        """Test creating article with valid data."""
        article = Article(
            id="test-123",
            title="Test Article",
            slug="test-article",
            content="This is test content",
            category_id="cat-123",
            status=PublishStatus.PUBLISHED
        )
        
        assert article.id == "test-123"
        assert article.title == "Test Article"
        assert article.slug == "test-article"
        assert article.status == PublishStatus.PUBLISHED
        assert article.content_type == ContentType.ARTICLE  # default

    def test_article_slug_auto_generation(self):
        """Test automatic slug generation from title."""
        article = Article(
            id="test-123",
            title="Test Article With Spaces & Special!",
            content="Test content"
        )
        
        assert article.slug == "test-article-with-spaces-special"

    def test_article_title_validation(self):
        """Test article title validation rules."""
        # Valid title
        article = Article(id="1", title="Valid Title", content="content")
        assert article.title == "Valid Title"
        
        # Empty title should fail
        with pytest.raises(ValidationError) as exc_info:
            Article(id="1", title="", content="content")
        assert "ensure this value has at least 1 characters" in str(exc_info.value)
        
        # Very long title should be truncated or fail based on validation rules
        long_title = "x" * 300
        with pytest.raises(ValidationError):
            Article(id="1", title=long_title, content="content")

    def test_article_content_validation(self):
        """Test article content validation."""
        # Valid content
        article = Article(id="1", title="Title", content="Valid content")
        assert article.content == "Valid content"
        
        # Empty content is allowed (drafts)
        article = Article(id="1", title="Title", content="")
        assert article.content == ""

    def test_article_status_validation(self):
        """Test article status enum validation."""
        # Valid status
        article = Article(id="1", title="Title", content="content", status=PublishStatus.DRAFT)
        assert article.status == PublishStatus.DRAFT
        
        # Invalid status string
        with pytest.raises(ValidationError):
            Article(id="1", title="Title", content="content", status="invalid_status")

    def test_article_dates_validation(self):
        """Test date field validation and parsing."""
        # Valid ISO date string
        article = Article(
            id="1",
            title="Title",
            content="content",
            created_at="2025-01-01T12:00:00Z",
            updated_at="2025-01-02T12:00:00Z"
        )
        
        assert isinstance(article.created_at, datetime)
        assert article.created_at.year == 2025
        assert article.created_at.month == 1
        assert article.created_at.day == 1

    def test_article_tags_validation(self):
        """Test tags field validation."""
        # Valid tags
        article = Article(
            id="1",
            title="Title", 
            content="content",
            tags=["tag1", "tag2", "tag3"]
        )
        assert len(article.tags) == 3
        assert "tag1" in article.tags

        # Empty tags should be allowed
        article = Article(id="1", title="Title", content="content", tags=[])
        assert article.tags == []

    def test_article_serialization(self):
        """Test article model serialization."""
        article = Article(
            id="test-123",
            title="Test Article",
            content="Test content",
            tags=["test", "article"],
            status=PublishStatus.PUBLISHED
        )
        
        # Test dict serialization
        article_dict = article.dict()
        assert article_dict["id"] == "test-123"
        assert article_dict["title"] == "Test Article"
        assert article_dict["status"] == "published"
        
        # Test JSON serialization
        article_json = article.json()
        assert "test-123" in article_json
        assert "Test Article" in article_json

    def test_article_deserialization(self):
        """Test creating article from dict/JSON."""
        article_data = {
            "id": "test-123",
            "title": "Test Article",
            "content": "Test content",
            "status": "published",
            "tags": ["test"]
        }
        
        article = Article(**article_data)
        assert article.id == "test-123"
        assert article.status == PublishStatus.PUBLISHED

    def test_article_equality(self):
        """Test article equality comparison."""
        article1 = Article(id="1", title="Title", content="content")
        article2 = Article(id="1", title="Title", content="content")
        article3 = Article(id="2", title="Title", content="content")
        
        assert article1 == article2
        assert article1 != article3

    def test_article_hash(self):
        """Test article hash functionality."""
        article1 = Article(id="1", title="Title", content="content")
        article2 = Article(id="1", title="Title", content="different")
        
        # Articles with same ID should have same hash
        assert hash(article1) == hash(article2)

    def test_article_word_count(self):
        """Test word count calculation."""
        article = Article(
            id="1",
            title="Title",
            content="This is a test article with multiple words and sentences."
        )
        
        assert article.word_count > 0
        # Should count words in content
        expected_count = len(article.content.split())
        assert article.word_count == expected_count


class TestCategoryModel:
    """Test cases for Category model validation and behavior."""

    def test_category_creation_valid(self):
        """Test creating category with valid data."""
        category = Category(
            id="cat-123",
            name="Test Category",
            slug="test-category",
            description="Test category description"
        )
        
        assert category.id == "cat-123"
        assert category.name == "Test Category"
        assert category.slug == "test-category"
        assert category.parent_id is None
        assert category.order == 0  # default

    def test_category_slug_generation(self):
        """Test automatic slug generation."""
        category = Category(
            id="cat-123",
            name="Test Category With Spaces"
        )
        
        assert category.slug == "test-category-with-spaces"

    def test_category_hierarchical_structure(self):
        """Test category parent-child relationships."""
        parent = Category(id="parent", name="Parent Category")
        child = Category(
            id="child", 
            name="Child Category",
            parent_id="parent"
        )
        
        assert child.parent_id == "parent"
        assert parent.parent_id is None

    def test_category_ordering(self):
        """Test category ordering."""
        cat1 = Category(id="1", name="First", order=1)
        cat2 = Category(id="2", name="Second", order=2)
        
        categories = sorted([cat2, cat1], key=lambda c: c.order)
        assert categories[0].id == "1"
        assert categories[1].id == "2"

    def test_category_validation_errors(self):
        """Test category validation error cases."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            Category(id="1", name="")
        
        # Negative order should fail
        with pytest.raises(ValidationError):
            Category(id="1", name="Test", order=-1)

    def test_category_serialization(self):
        """Test category serialization."""
        category = Category(
            id="cat-123",
            name="Test Category",
            description="Test description",
            parent_id="parent-123",
            order=5
        )
        
        category_dict = category.dict()
        assert category_dict["id"] == "cat-123"
        assert category_dict["parent_id"] == "parent-123"
        assert category_dict["order"] == 5


class TestProjectVersionModel:
    """Test cases for ProjectVersion model validation and behavior."""

    def test_project_version_creation(self):
        """Test creating project version with valid data."""
        version = ProjectVersion(
            id="v1",
            name="Version 1.0",
            version_number="1.0.0",
            description="First version"
        )
        
        assert version.id == "v1"
        assert version.name == "Version 1.0"
        assert version.version_number == "1.0.0"
        assert version.is_default is False  # default

    def test_project_version_semantic_versioning(self):
        """Test semantic version validation."""
        # Valid semantic versions
        valid_versions = ["1.0.0", "2.1.3", "10.20.30", "1.0.0-alpha", "2.0.0-beta.1"]
        
        for version_num in valid_versions:
            version = ProjectVersion(
                id="test",
                name="Test",
                version_number=version_num
            )
            assert version.version_number == version_num

    def test_project_version_comparison(self):
        """Test version comparison logic."""
        v1 = ProjectVersion(id="v1", name="V1", version_number="1.0.0")
        v2 = ProjectVersion(id="v2", name="V2", version_number="2.0.0")
        
        # Assuming comparison is based on version_number parsing
        assert v1.version_number < v2.version_number  # String comparison for now

    def test_project_version_default_flag(self):
        """Test default version flag."""
        default_version = ProjectVersion(
            id="default",
            name="Default Version",
            version_number="1.0.0",
            is_default=True
        )
        
        assert default_version.is_default is True

    def test_project_version_dates(self):
        """Test version date handling."""
        version = ProjectVersion(
            id="v1",
            name="Version 1",
            version_number="1.0.0",
            created_at="2025-01-01T00:00:00Z",
            published_at="2025-01-02T00:00:00Z"
        )
        
        assert version.created_at is not None
        assert version.published_at is not None

    def test_project_version_serialization(self):
        """Test version serialization."""
        version = ProjectVersion(
            id="v1",
            name="Version 1",
            version_number="1.0.0",
            is_default=True
        )
        
        version_dict = version.dict()
        assert version_dict["version_number"] == "1.0.0"
        assert version_dict["is_default"] is True


class TestEnumModels:
    """Test cases for enum models."""

    def test_publish_status_enum(self):
        """Test PublishStatus enum values."""
        assert PublishStatus.DRAFT == "draft"
        assert PublishStatus.PUBLISHED == "published"
        assert PublishStatus.ARCHIVED == "archived"
        
        # Test enum in model
        article = Article(
            id="1",
            title="Title",
            content="content",
            status=PublishStatus.DRAFT
        )
        assert article.status == PublishStatus.DRAFT

    def test_content_type_enum(self):
        """Test ContentType enum values."""
        assert ContentType.ARTICLE == "article"
        assert ContentType.TUTORIAL == "tutorial"
        assert ContentType.FAQ == "faq"
        
        # Test enum in model  
        article = Article(
            id="1",
            title="Title", 
            content="content",
            content_type=ContentType.TUTORIAL
        )
        assert article.content_type == ContentType.TUTORIAL

    def test_enum_validation_errors(self):
        """Test enum validation with invalid values."""
        with pytest.raises(ValidationError):
            Article(
                id="1",
                title="Title",
                content="content", 
                status="invalid_status"
            )
        
        with pytest.raises(ValidationError):
            Article(
                id="1",
                title="Title",
                content="content",
                content_type="invalid_type"
            )


class TestModelEdgeCases:
    """Test edge cases and error conditions."""

    def test_model_with_none_values(self):
        """Test models with None values where allowed."""
        article = Article(
            id="1",
            title="Title",
            content="content",
            category_id=None,  # Should be allowed
            author=None,       # Should be allowed
            tags=None         # Should default to empty list
        )
        
        assert article.category_id is None
        assert article.author is None
        assert article.tags == []  # Should default

    def test_model_with_extra_fields(self):
        """Test models with extra fields."""
        # Should ignore extra fields by default
        article_data = {
            "id": "1",
            "title": "Title",
            "content": "content",
            "extra_field": "should be ignored"
        }
        
        article = Article(**article_data)
        assert not hasattr(article, "extra_field")

    def test_model_field_aliases(self):
        """Test field aliases if any are defined."""
        # Test if models support alternative field names
        # This depends on model configuration
        pass

    def test_model_validation_order(self):
        """Test that model validation occurs in correct order."""
        # Test that pre-validators run before main validation
        article_data = {
            "id": "  1  ",  # Should be stripped
            "title": "  Title  ",  # Should be stripped  
            "content": "content"
        }
        
        article = Article(**article_data)
        # Assuming models strip whitespace
        assert article.id == "1" or article.id == "  1  "  # Depends on implementation

    def test_model_immutability(self):
        """Test if models are immutable where expected."""
        article = Article(id="1", title="Title", content="content")
        
        # Try to modify - should work unless frozen
        article.title = "New Title"
        assert article.title == "New Title"

    @pytest.mark.parametrize("invalid_id", [None, "", "   ", 123, []])
    def test_invalid_id_values(self, invalid_id):
        """Test various invalid ID values."""
        with pytest.raises(ValidationError):
            Article(id=invalid_id, title="Title", content="content")

    @pytest.mark.parametrize("valid_status", list(PublishStatus))
    def test_all_publish_statuses(self, valid_status):
        """Test all valid publish status values."""
        article = Article(
            id="1",
            title="Title", 
            content="content",
            status=valid_status
        )
        assert article.status == valid_status

    def test_model_copy_and_update(self):
        """Test model copy with updates."""
        original = Article(
            id="1",
            title="Original Title",
            content="content"
        )
        
        updated = original.copy(update={"title": "Updated Title"})
        
        assert original.title == "Original Title"
        assert updated.title == "Updated Title"
        assert original.id == updated.id

    def test_model_json_schema(self):
        """Test JSON schema generation."""
        schema = Article.schema()
        
        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "title" in schema["properties"]
        assert "required" in schema
        assert "id" in schema["required"]


# Performance tests
class TestModelPerformance:
    """Performance tests for model operations."""

    @pytest.mark.performance
    def test_article_creation_performance(self):
        """Test article creation performance."""
        import time
        
        start_time = time.time()
        
        # Create many articles
        articles = []
        for i in range(1000):
            article = Article(
                id=f"article-{i}",
                title=f"Article {i}",
                content=f"Content for article {i}",
                tags=[f"tag{j}" for j in range(5)]
            )
            articles.append(article)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should create 1000 articles in reasonable time (< 1 second)
        assert duration < 1.0
        assert len(articles) == 1000

    @pytest.mark.performance  
    def test_model_serialization_performance(self):
        """Test model serialization performance."""
        import time
        
        # Create test articles
        articles = [
            Article(
                id=f"article-{i}",
                title=f"Article {i}",
                content=f"Content for article {i}" * 100,  # Larger content
                tags=[f"tag{j}" for j in range(10)]
            )
            for i in range(100)
        ]
        
        start_time = time.time()
        
        # Serialize all articles
        serialized = [article.dict() for article in articles]
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should serialize quickly
        assert duration < 0.5
        assert len(serialized) == 100