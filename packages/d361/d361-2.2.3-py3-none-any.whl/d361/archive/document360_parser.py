"""Document360 export parser for d361 package."""
# this_file: external/int_folders/d361/src/d361/archive/document360_parser.py

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from d361.core.models import Article, Category


class Document360Parser:
    """Parse Document360 export structure using d361 canonical models.
    
    This parser migrated from vexy_help and now uses d361's canonical
    Article and Category models for consistent data representation.
    """

    def __init__(self, export_path: Path) -> None:
        """Initialize parser with export path.

        Args:
            export_path: Path to Document360 export directory
        """
        self.export_path = Path(export_path)
        self._validate_export_structure()

        # Find version directory (e.g., v1)
        self.version_dir = self._find_version_dir()
        self.articles_dir = self.version_dir / "articles"
        self.categories_dir = self.version_dir / "categories"
        self.metadata_file = self._find_metadata_file()

        logger.info(f"Initialized Document360Parser with export at {self.export_path}")

    def _validate_export_structure(self) -> None:
        """Validate that the export has expected structure."""
        if not self.export_path.exists():
            raise FileNotFoundError(f"Export path does not exist: {self.export_path}")

        if not self.export_path.is_dir():
            raise ValueError(f"Export path is not a directory: {self.export_path}")

    def _find_version_dir(self) -> Path:
        """Find the version directory (e.g., v1)."""
        # Look for directories like v1, v2, etc.
        version_dirs = [
            d for d in self.export_path.iterdir() if d.is_dir() and re.match(r"^v\d+$", d.name)
        ]

        if not version_dirs:
            raise ValueError(f"No version directory found in {self.export_path}")

        # Use the first version directory found
        return version_dirs[0]

    def _find_metadata_file(self) -> Path:
        """Find the metadata JSON file."""
        # Look for files like v1_categories_articles.json
        pattern = f"{self.version_dir.name}_categories_articles.json"

        # Check in the version directory first
        metadata_file = self.version_dir / pattern
        if metadata_file.exists():
            return metadata_file

        # Then check in the export root
        metadata_files = list(self.export_path.glob(pattern))
        if metadata_files:
            return metadata_files[0]

        raise ValueError(f"No metadata file matching {pattern} found")

    def parse(self) -> tuple[list[Category], list[Article]]:
        """Parse the complete Document360 export.

        Returns:
            Tuple of (categories, articles) using d361 canonical models
        """
        import json
        
        # Load metadata
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Parse structure
        categories = self._parse_categories(metadata)
        articles = self._parse_articles_from_categories(metadata, categories)

        # Load article content from files
        self._load_article_content(articles)

        logger.info(
            f"Parsed {len(articles)} articles in {len(categories)} categories"
        )

        return categories, articles

    def _parse_categories(self, metadata: dict[str, Any]) -> list[Category]:
        """Parse category structure from metadata.

        Args:
            metadata: JSON metadata

        Returns:
            List of all categories (flattened hierarchy)
        """
        # Document360 uses "Categories" with capital C
        categories_data = metadata.get("Categories", metadata.get("categories", []))
        categories = []

        # Recursively parse categories
        def parse_category_tree(
            cat_data: dict[str, Any], 
            parent_id: int | None = None, 
            level: int = 0,
            path_prefix: str = ""
        ) -> None:
            # Get language-specific data
            lang_data = cat_data.get("Languages", [{}])[0]

            # Get slug from language data or generate from path
            cat_path = cat_data.get("Path", "")
            if cat_path:
                slug = cat_path.replace(".md", "")
            else:
                slug = lang_data.get("Slug", str(cat_data.get("Id", "")))

            # Build hierarchical path
            cat_name = cat_data.get("Title", lang_data.get("Title", "Untitled"))
            current_path = f"{path_prefix}/{cat_name}" if path_prefix else cat_name

            # Create d361 canonical Category model  
            category = Category(
                id=cat_data["Id"],  # Support both integer and UUID string IDs
                name=cat_name,
                slug=slug,
                parent_id=parent_id,
                order=cat_data.get("Order", 0),
                level=level,
                path=current_path,
                description=lang_data.get("Description") or "",  # Handle null descriptions
                created_at=datetime.now(),  # Default since not in export
                updated_at=datetime.now(),  # Default since not in export
                is_public=True,  # Default for Document360
                language_code="en",  # Default, could be extracted from lang_data
            )
            categories.append(category)

            # Recursively parse subcategories
            for subcat_data in cat_data.get("SubCategories", []):
                parse_category_tree(subcat_data, category.id, level + 1, current_path)

        # Process root categories
        for cat_data in categories_data:
            parse_category_tree(cat_data)

        # Sort categories by order
        categories.sort(key=lambda c: (c.level, c.order))

        return categories

    def _parse_articles_from_categories(
        self, 
        metadata: dict[str, Any], 
        categories: list[Category]
    ) -> list[Article]:
        """Parse articles from category metadata.

        Args:
            metadata: JSON metadata
            categories: Parsed categories

        Returns:
            List of articles using d361 canonical models
        """
        articles = []
        category_id_map = {cat.id: cat for cat in categories}

        def extract_articles_from_category(cat_data: dict[str, Any], category_id: int | str) -> None:
            # Parse articles in this category
            articles_data = cat_data.get("Articles", [])
            for art_data in articles_data:
                article = self._parse_article_metadata(art_data, category_id)
                articles.append(article)

            # Recursively process subcategories
            for subcat_data in cat_data.get("SubCategories", []):
                extract_articles_from_category(subcat_data, subcat_data["Id"])  # Support both integer and UUID string IDs

        # Process root categories from metadata
        categories_data = metadata.get("Categories", metadata.get("categories", []))
        for cat_data in categories_data:
            extract_articles_from_category(cat_data, cat_data["Id"])  # Support both integer and UUID string IDs

        # Sort articles by category and order
        articles.sort(key=lambda a: (a.category_id, a.order))

        return articles

    def _parse_article_metadata(self, art_data: dict[str, Any], category_id: int | str) -> Article:
        """Parse article metadata into d361 canonical model.

        Args:
            art_data: Article data from JSON
            category_id: Parent category ID (integer or UUID string)

        Returns:
            Article instance using d361 canonical model
        """
        # Extract slug from Path field
        path = art_data.get("Path", "")
        slug = path.replace(".md", "") if path else ""

        # Create d361 canonical Article model
        # Note: Some fields will be updated when loading content from files
        article = Article(
            id=art_data["Id"],  # Support both integer and UUID string IDs
            title=slug.replace("-", " ").title(),  # Will be updated from file
            slug=slug,
            content="",  # Will be loaded from file
            content_markdown="",  # Will be loaded from file
            category_id=category_id,
            order=art_data.get("Order", 0),
            created_at=datetime.now(),  # Default since not in export
            updated_at=datetime.now(),  # Default since not in export
            author_name="",  # Will be updated if found in file
            language_code="en",  # Default, could be extracted from metadata
            is_public=True,  # Default for Document360
            metadata={"original_data": art_data}  # Store original for reference
        )

        return article

    def _load_article_content(self, articles: list[Article]) -> None:
        """Load article content from markdown files.

        Args:
            articles: List of articles to populate with content
        """
        if not self.articles_dir.exists():
            logger.warning(f"Articles directory not found: {self.articles_dir}")
            return

        # Create lookup for articles by slug
        articles_by_slug = {}
        for article in articles:
            # Handle numeric prefixes in slugs
            clean_slug = self._strip_numeric_prefix(article.slug)
            articles_by_slug[clean_slug] = article

        # Find all markdown files
        for md_file in self.articles_dir.glob("*.md"):
            # Skip duplicate files with (1) suffix
            if "(1)" in md_file.stem:
                continue

            # Try to match file to article by slug
            file_slug = self._strip_numeric_prefix(md_file.stem)

            # Find matching article
            article = articles_by_slug.get(file_slug)
            if not article:
                logger.warning(f"No article found for file: {md_file.name}")
                continue

            # Load content
            try:
                frontmatter, content = self._parse_markdown_file(md_file)
                article.content_markdown = content

                # Update article with file metadata if present
                if frontmatter:
                    article.title = frontmatter.get("title", article.title)
                    article.meta_title = frontmatter.get("seoTitle", "")
                    article.meta_description = frontmatter.get("description", "")
                    article.language_code = frontmatter.get("code", article.language_code)
                    
                    # Handle visibility
                    if "hidden" in frontmatter:
                        article.is_public = frontmatter["hidden"] != "true"

                # Store file path in metadata
                article.metadata["file_path"] = str(md_file)

            except Exception as e:
                logger.error(f"Failed to parse {md_file}: {e}")

    def _parse_markdown_file(self, md_file: Path) -> tuple[dict[str, Any] | None, str]:
        """Parse markdown file with frontmatter.

        Args:
            md_file: Path to markdown file

        Returns:
            Tuple of (frontmatter_dict, content)
        """
        content = md_file.read_text(encoding='utf-8')
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1])
                    content = parts[2].strip()
                    return frontmatter, content
                except Exception as e:
                    logger.warning(f"Failed to parse frontmatter in {md_file}: {e}")
        
        return None, content

    def _strip_numeric_prefix(self, slug: str) -> str:
        """Strip numeric prefixes from slugs (e.g., '001-article-name' -> 'article-name').

        Args:
            slug: Original slug

        Returns:
            Cleaned slug
        """
        # Remove leading numbers and dashes
        return re.sub(r'^\d+-', '', slug)

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the parsed export.

        Returns:
            Dictionary with statistics
        """
        categories, articles = self.parse()

        stats = {
            "total_categories": len(categories),
            "total_articles": len(articles),
            "root_categories": len([c for c in categories if c.parent_id is None]),
            "public_articles": len([a for a in articles if a.is_public]),
            "articles_with_content": len([a for a in articles if a.content_markdown]),
            "max_category_depth": max([c.level for c in categories]) if categories else 0,
            "duplicate_files": len(list(self.articles_dir.glob("*(1).md"))) 
                if self.articles_dir.exists() else 0,
        }

        # Language distribution
        languages = {}
        for article in articles:
            lang = article.language_code
            languages[lang] = languages.get(lang, 0) + 1
        stats["language_distribution"] = languages

        return stats