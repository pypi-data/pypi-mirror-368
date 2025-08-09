"""Navigation builder for MkDocs from Document360 structure.

This module creates intelligent navigation structures from Document360
category and article hierarchies, with support for different navigation
patterns and MkDocs-specific features.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/exporters/navigation_builder.py

from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import re
import asyncio
from dataclasses import dataclass

from loguru import logger

from d361.core.models import Article, Category

# Phase 2 dataclasses for enhanced navigation
@dataclass
class NavigationItem:
    """Represents a navigation item with metadata."""
    title: str
    path: str
    weight: int = 0
    level: int = 0
    is_section: bool = False
    children: List['NavigationItem'] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}

@dataclass  
class NavigationAnalytics:
    """Navigation analytics and metrics."""
    total_items: int = 0
    max_depth: int = 0
    sections_count: int = 0
    orphaned_articles: List[str] = None
    duplicate_titles: List[str] = None
    broken_references: List[str] = None
    
    def __post_init__(self):
        if self.orphaned_articles is None:
            self.orphaned_articles = []
        if self.duplicate_titles is None:
            self.duplicate_titles = []
        if self.broken_references is None:
            self.broken_references = []


class NavigationBuilder:
    """Build MkDocs navigation from Document360 structure.
    
    This class generates intelligent navigation structures that work well
    with MkDocs themes and plugins, supporting various organization patterns
    and navigation features.
    
    Features:
    - Hierarchical navigation from Document360 categories
    - Smart section indexes for categories
    - Support for mkdocs-literate-nav (SUMMARY.md) generation
    - Automatic ordering and organization
    - Navigation validation and optimization
    
    Example:
        builder = NavigationBuilder()
        navigation = await builder.build_navigation(articles, categories)
    """
    
    def __init__(
        self,
        use_category_indexes: bool = True,
        sort_by_order: bool = True,
        include_hidden: bool = False,
        max_depth: int = 5,
        # Phase 2 enhancements
        enable_literate_nav: bool = True,
        generate_section_indexes: bool = True,
        smart_ordering: bool = True,
        enable_navigation_analytics: bool = True,
        auto_generate_titles: bool = True,
        enable_breadcrumbs: bool = True,
        navigation_validation: bool = True,
        optimize_for_mobile: bool = True,
    ) -> None:
        """Initialize navigation builder.
        
        Args:
            use_category_indexes: Create index pages for categories
            sort_by_order: Sort items by order field
            include_hidden: Include hidden articles in navigation
            max_depth: Maximum navigation depth
            # Phase 2 enhancements
            enable_literate_nav: Enable mkdocs-literate-nav integration
            generate_section_indexes: Auto-generate section index pages
            smart_ordering: Enable intelligent content ordering
            enable_navigation_analytics: Enable navigation analytics and validation
            auto_generate_titles: Auto-generate navigation titles from content
            enable_breadcrumbs: Generate breadcrumb navigation data
            navigation_validation: Validate navigation structure for issues
            optimize_for_mobile: Optimize navigation structure for mobile devices
        """
        self.use_category_indexes = use_category_indexes
        self.sort_by_order = sort_by_order
        self.include_hidden = include_hidden
        self.max_depth = max_depth
        
        # Phase 2 enhancements
        self.enable_literate_nav = enable_literate_nav
        self.generate_section_indexes = generate_section_indexes
        self.smart_ordering = smart_ordering
        self.enable_navigation_analytics = enable_navigation_analytics
        self.auto_generate_titles = auto_generate_titles
        self.enable_breadcrumbs = enable_breadcrumbs
        self.navigation_validation = navigation_validation
        self.optimize_for_mobile = optimize_for_mobile
        
        # Phase 2 tracking and analytics
        self.navigation_analytics = NavigationAnalytics()
        self.section_indexes_generated: Dict[str, str] = {}  # category_id -> index_path
        self.breadcrumb_cache: Dict[str, List[Dict[str, str]]] = {}  # article_id -> breadcrumbs
        self.navigation_tree: Optional[NavigationItem] = None
        
        logger.info(f"Initialized NavigationBuilder with Phase 2 enhancements: literate_nav={enable_literate_nav}, smart_ordering={smart_ordering}")
    
    async def build_navigation(
        self,
        articles: List[Article],
        categories: List[Category],
    ) -> Dict[str, Any]:
        """Build navigation structure from articles and categories.
        
        Args:
            articles: List of articles to include in navigation
            categories: List of categories for organization
            
        Returns:
            Enhanced navigation structure with Phase 2 features
        """
        logger.info("Building MkDocs navigation structure with Phase 2 enhancements")
        
        # Phase 2: Initialize analytics
        if self.enable_navigation_analytics:
            self.navigation_analytics = NavigationAnalytics()
            self.navigation_analytics.total_items = len(articles)
        
        # Filter articles if needed
        if not self.include_hidden:
            articles = [a for a in articles if not getattr(a, 'is_hidden', False)]
        
        # Phase 2: Smart ordering if enabled
        if self.smart_ordering:
            articles = await self._apply_smart_ordering(articles)
            categories = await self._apply_smart_category_ordering(categories)
        
        # Build category hierarchy
        category_tree = self._build_category_tree(categories)
        
        # Map articles to categories
        article_map = self._map_articles_to_categories(articles, categories)
        
        # Phase 2: Generate section indexes if enabled
        section_indexes = {}
        if self.generate_section_indexes:
            section_indexes = await self._generate_section_indexes(categories, articles)
        
        # Build enhanced navigation structure
        navigation_items = []
        
        # Add home page if it exists
        home_article = self._find_home_article(articles)
        if home_article:
            home_item = NavigationItem(
                title="Home",
                path=f"{home_article.slug}.md",
                weight=0,
                level=0,
                metadata={'article_id': home_article.id, 'is_home': True}
            )
            navigation_items.append(home_item)
        
        # Build category navigation with enhanced features
        for category in category_tree:
            nav_item = await self._build_enhanced_category_navigation(
                category, article_map, section_indexes, depth=0
            )
            if nav_item:
                navigation_items.append(nav_item)
        
        # Add orphaned articles (not in any category)
        orphaned = self._find_orphaned_articles(articles, categories)
        if orphaned:
            if self.enable_navigation_analytics:
                self.navigation_analytics.orphaned_articles = [a.id for a in orphaned if a.id]
            
            for article in orphaned:
                orphaned_item = NavigationItem(
                    title=article.title,
                    path=f"{article.slug}.md",
                    weight=1000,  # Place at end
                    level=0,
                    metadata={'article_id': article.id, 'is_orphaned': True}
                )
                navigation_items.append(orphaned_item)
        
        # Phase 2: Build navigation tree
        self.navigation_tree = NavigationItem(
            title="Root",
            path="",
            children=navigation_items,
            is_section=True
        )
        
        # Phase 2: Generate breadcrumbs if enabled
        breadcrumbs = {}
        if self.enable_breadcrumbs:
            breadcrumbs = self._generate_breadcrumbs(navigation_items)
        
        # Phase 2: Validate navigation if enabled
        validation_report = {}
        if self.navigation_validation:
            validation_report = await self._validate_navigation(navigation_items, articles)
        
        # Convert to standard MkDocs format
        mkdocs_navigation = self._convert_to_mkdocs_format(navigation_items)
        
        # Phase 2: Generate literate navigation if enabled
        literate_nav_content = ""
        if self.enable_literate_nav:
            literate_nav_content = self._generate_literate_nav(navigation_items)
        
        logger.info(f"Built enhanced navigation with {len(navigation_items)} top-level items")
        
        # Return enhanced navigation structure
        return {
            'navigation': mkdocs_navigation,
            'navigation_tree': navigation_items,
            'literate_nav_content': literate_nav_content,
            'section_indexes': section_indexes,
            'breadcrumbs': breadcrumbs,
            'validation_report': validation_report,
            'analytics': self.navigation_analytics.__dict__ if self.enable_navigation_analytics else {},
            'metadata': {
                'total_items': len(navigation_items),
                'max_depth': self._calculate_max_depth(navigation_items),
                'orphaned_count': len(orphaned),
                'sections_count': len([item for item in navigation_items if item.is_section or item.children]),
                'phase_2_features_enabled': {
                    'literate_nav': self.enable_literate_nav,
                    'smart_ordering': self.smart_ordering,
                    'section_indexes': self.generate_section_indexes,
                    'breadcrumbs': self.enable_breadcrumbs,
                    'validation': self.navigation_validation,
                    'analytics': self.enable_navigation_analytics,
                }
            }
        }
    
    def _build_category_tree(self, categories: List[Category]) -> List[Category]:
        """Build hierarchical category tree."""
        # Sort categories by order if enabled
        if self.sort_by_order:
            categories = sorted(categories, key=lambda c: getattr(c, 'order', 0))
        
        # For now, assume flat category structure
        # TODO: Implement proper hierarchy if Document360 supports it
        return categories
    
    def _map_articles_to_categories(
        self, 
        articles: List[Article], 
        categories: List[Category]
    ) -> Dict[str, List[Article]]:
        """Map articles to their categories."""
        article_map: Dict[str, List[Article]] = {}
        
        # Initialize category maps
        for category in categories:
            article_map[str(category.id)] = []
        
        # Map articles to categories
        for article in articles:
            category_id = str(article.category_id)
            if category_id in article_map:
                article_map[category_id].append(article)
            else:
                # Handle orphaned articles
                if "orphaned" not in article_map:
                    article_map["orphaned"] = []
                article_map["orphaned"].append(article)
        
        # Sort articles within categories
        if self.sort_by_order:
            for category_id in article_map:
                article_map[category_id] = sorted(
                    article_map[category_id], 
                    key=lambda a: getattr(a, 'order', 0)
                )
        
        return article_map
    
    async def _build_category_navigation(
        self,
        category: Category,
        article_map: Dict[str, List[Article]],
        depth: int = 0,
    ) -> Optional[Dict[str, Any]]:
        """Build navigation for a category."""
        if depth > self.max_depth:
            logger.warning(f"Maximum navigation depth reached for category {category.name}")
            return None
        
        category_id = str(category.id)
        articles = article_map.get(category_id, [])
        
        # Skip empty categories unless they have subcategories
        if not articles and not getattr(category, 'subcategories', []):
            return None
        
        # Build category navigation item
        nav_items = []
        
        # Add category index if enabled
        if self.use_category_indexes:
            nav_items.append(f"{category.slug}/index.md")
        
        # Add articles
        for article in articles:
            nav_items.append({
                article.title: f"{category.slug}/{article.slug}.md"
            })
        
        # Add subcategories (if supported)
        subcategories = getattr(category, 'subcategories', [])
        for subcategory in subcategories:
            subcat_nav = await self._build_category_navigation(
                subcategory, article_map, depth + 1
            )
            if subcat_nav:
                nav_items.append(subcat_nav)
        
        # Return navigation structure
        if len(nav_items) == 1 and not self.use_category_indexes:
            # Single item category - flatten
            return nav_items[0]
        else:
            return {category.name: nav_items}
    
    def _find_home_article(self, articles: List[Article]) -> Optional[Article]:
        """Find article to use as home page."""
        # Look for common home page patterns
        home_patterns = [
            r"^home$",
            r"^index$", 
            r"^introduction$",
            r"^overview$",
            r"^welcome$",
            r"^getting[_\-]started$",
        ]
        
        for pattern in home_patterns:
            for article in articles:
                if re.match(pattern, article.slug.lower()):
                    return article
        
        # If no specific home page found, use first article
        if articles:
            return articles[0]
        
        return None
    
    def _find_orphaned_articles(
        self, 
        articles: List[Article], 
        categories: List[Category]
    ) -> List[Article]:
        """Find articles not assigned to any category."""
        category_ids = {str(cat.id) for cat in categories}
        orphaned = []
        
        for article in articles:
            if str(article.category_id) not in category_ids:
                orphaned.append(article)
        
        return orphaned
    
    async def generate_literate_nav(
        self,
        articles: List[Article],
        categories: List[Category],
        output_path: Path,
    ) -> Path:
        """Generate SUMMARY.md file for mkdocs-literate-nav plugin.
        
        Args:
            articles: Articles to include
            categories: Categories for organization
            output_path: Output directory
            
        Returns:
            Path to generated SUMMARY.md file
        """
        logger.info("Generating SUMMARY.md for literate navigation")
        
        summary_lines = ["# Navigation", ""]
        
        # Build navigation structure
        navigation = await self.build_navigation(articles, categories)
        
        # Convert to literate nav format
        for nav_item in navigation:
            summary_lines.extend(self._nav_item_to_literate(nav_item, level=0))
        
        # Write SUMMARY.md
        summary_path = output_path / "docs" / "SUMMARY.md"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
        
        logger.info(f"Generated literate navigation: {summary_path}")
        return summary_path
    
    def _nav_item_to_literate(
        self, 
        nav_item: Dict[str, Any] | str, 
        level: int = 0
    ) -> List[str]:
        """Convert navigation item to literate nav format."""
        indent = "  " * level
        lines = []
        
        if isinstance(nav_item, str):
            # Simple link
            lines.append(f"{indent}* [{nav_item}]({nav_item})")
        elif isinstance(nav_item, dict):
            for title, content in nav_item.items():
                if isinstance(content, str):
                    # Simple link with title
                    lines.append(f"{indent}* [{title}]({content})")
                elif isinstance(content, list):
                    # Section with subsections
                    lines.append(f"{indent}* {title}")
                    for sub_item in content:
                        lines.extend(self._nav_item_to_literate(sub_item, level + 1))
                elif isinstance(content, dict):
                    # Nested section
                    lines.append(f"{indent}* {title}")
                    lines.extend(self._nav_item_to_literate(content, level + 1))
        
        return lines
    
    async def validate_navigation(
        self,
        navigation: List[Dict[str, Any]],
        docs_path: Path,
    ) -> Dict[str, Any]:
        """Validate navigation structure and file references.
        
        Args:
            navigation: Navigation structure to validate
            docs_path: Path to docs directory
            
        Returns:
            Validation results
        """
        logger.info("Validating navigation structure")
        
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "missing_files": [],
            "broken_links": [],
        }
        
        def validate_nav_item(item: Dict[str, Any] | str, path_prefix: str = ""):
            """Recursively validate navigation items."""
            if isinstance(item, str):
                # File reference
                file_path = docs_path / item
                if not file_path.exists():
                    validation_results["missing_files"].append(str(file_path))
                    validation_results["valid"] = False
            elif isinstance(item, dict):
                for title, content in item.items():
                    if isinstance(content, str):
                        # File reference with title
                        file_path = docs_path / content
                        if not file_path.exists():
                            validation_results["missing_files"].append(str(file_path))
                            validation_results["valid"] = False
                    elif isinstance(content, list):
                        # Subsection
                        for sub_item in content:
                            validate_nav_item(sub_item, path_prefix)
                    elif isinstance(content, dict):
                        # Nested navigation
                        validate_nav_item(content, path_prefix)
        
        # Validate all navigation items
        for nav_item in navigation:
            validate_nav_item(nav_item)
        
        # Add summary to results
        if validation_results["missing_files"]:
            validation_results["errors"].append(
                f"Found {len(validation_results['missing_files'])} missing files"
            )
        
        logger.info(f"Navigation validation complete: {len(validation_results['errors'])} errors")
        return validation_results
    
    # Phase 2: Advanced Navigation Methods
    
    async def _apply_smart_ordering(self, articles: List[Article]) -> List[Article]:
        """Apply intelligent ordering to articles based on content analysis."""
        def calculate_article_weight(article: Article) -> int:
            weight = getattr(article, 'order', 1000)
            
            # Boost weight for introduction/overview articles
            title_lower = article.title.lower()
            if any(pattern in title_lower for pattern in ['introduction', 'overview', 'getting started', 'quick start']):
                weight -= 500
            elif any(pattern in title_lower for pattern in ['tutorial', 'guide', 'how to']):
                weight -= 300
            elif any(pattern in title_lower for pattern in ['reference', 'api', 'advanced']):
                weight += 200
            elif any(pattern in title_lower for pattern in ['troubleshoot', 'faq', 'error']):
                weight += 400
            
            # Consider content length (longer articles might be more comprehensive)
            if hasattr(article, 'content') and article.content:
                content_length = len(article.content)
                if content_length > 2000:
                    weight -= 100
                elif content_length < 200:
                    weight += 200
            
            return weight
        
        return sorted(articles, key=calculate_article_weight)
    
    async def _apply_smart_category_ordering(self, categories: List[Category]) -> List[Category]:
        """Apply intelligent ordering to categories."""
        def calculate_category_weight(category: Category) -> int:
            weight = getattr(category, 'order', 1000)
            
            # Prioritize certain category types
            name_lower = category.name.lower()
            if any(pattern in name_lower for pattern in ['getting started', 'introduction', 'overview']):
                weight -= 500
            elif any(pattern in name_lower for pattern in ['tutorial', 'guide', 'how to']):
                weight -= 300
            elif any(pattern in name_lower for pattern in ['reference', 'api']):
                weight += 100
            elif any(pattern in name_lower for pattern in ['troubleshoot', 'faq']):
                weight += 300
            
            return weight
        
        return sorted(categories, key=calculate_category_weight)
    
    async def _generate_section_indexes(self, categories: List[Category], articles: List[Article]) -> Dict[str, str]:
        """Generate section index pages for categories."""
        section_indexes = {}
        
        for category in categories:
            category_id = str(category.id)
            category_articles = [a for a in articles if str(a.category_id) == category_id]
            
            if category_articles:
                # Generate index content
                index_content = self._create_section_index_content(category, category_articles)
                index_filename = f"{category.slug}/index.md"
                section_indexes[category_id] = {
                    'filename': index_filename,
                    'content': index_content,
                    'articles_count': len(category_articles),
                    'category': category.name
                }
                
                # Track generated index
                self.section_indexes_generated[category_id] = index_filename
        
        logger.debug(f"Generated {len(section_indexes)} section indexes")
        return section_indexes
    
    def _create_section_index_content(self, category: Category, articles: List[Article]) -> str:
        """Create content for a section index page."""
        lines = [
            f"# {category.name}",
            "",
        ]
        
        # Add category description if available
        if hasattr(category, 'description') and category.description:
            lines.extend([
                category.description,
                ""
            ])
        else:
            lines.extend([
                f"This section contains {len(articles)} articles about {category.name.lower()}.",
                ""
            ])
        
        # Add table of contents
        lines.extend([
            "## Articles in this section",
            ""
        ])
        
        for article in articles:
            # Extract first sentence for description
            description = "No description available"
            if article.content:
                sentences = re.split(r'[.!?]+', article.content.strip())
                if sentences and len(sentences[0]) > 20:
                    description = sentences[0].strip()[:100] + ("..." if len(sentences[0]) > 100 else "")
            
            lines.extend([
                f"### [{article.title}]({article.slug}.md)",
                f"{description}",
                ""
            ])
        
        return "\n".join(lines)
    
    async def _build_enhanced_category_navigation(
        self,
        category: Category,
        article_map: Dict[str, List[Article]],
        section_indexes: Dict[str, str],
        depth: int = 0,
    ) -> Optional[NavigationItem]:
        """Build enhanced navigation for a category with Phase 2 features."""
        if depth > self.max_depth:
            logger.warning(f"Maximum navigation depth reached for category {category.name}")
            return None
        
        category_id = str(category.id)
        articles = article_map.get(category_id, [])
        
        # Skip empty categories unless they have subcategories
        if not articles and not getattr(category, 'subcategories', []):
            return None
        
        # Create navigation item for category
        nav_item = NavigationItem(
            title=category.name,
            path="",
            level=depth,
            weight=getattr(category, 'order', 1000),
            is_section=True,
            metadata={
                'category_id': category_id,
                'articles_count': len(articles),
                'has_index': category_id in section_indexes
            }
        )
        
        # Add category index if enabled and generated
        if self.generate_section_indexes and category_id in section_indexes:
            index_item = NavigationItem(
                title="Overview",
                path=f"{category.slug}/index.md",
                level=depth + 1,
                weight=0,
                metadata={'is_section_index': True, 'category_id': category_id}
            )
            nav_item.children.append(index_item)
        
        # Add articles
        for i, article in enumerate(articles):
            article_item = NavigationItem(
                title=article.title,
                path=f"{category.slug}/{article.slug}.md",
                level=depth + 1,
                weight=getattr(article, 'order', i * 100),
                metadata={
                    'article_id': article.id,
                    'category_id': category_id,
                    'article_type': self._classify_article_type(article)
                }
            )
            nav_item.children.append(article_item)
        
        # Add subcategories (if supported)
        subcategories = getattr(category, 'subcategories', [])
        for subcategory in subcategories:
            subcat_nav = await self._build_enhanced_category_navigation(
                subcategory, article_map, section_indexes, depth + 1
            )
            if subcat_nav:
                nav_item.children.append(subcat_nav)
        
        # Sort children by weight
        nav_item.children.sort(key=lambda x: x.weight)
        
        return nav_item
    
    def _classify_article_type(self, article: Article) -> str:
        """Classify article type based on title and content analysis."""
        title_lower = article.title.lower()
        
        if any(pattern in title_lower for pattern in ['tutorial', 'how to', 'step by step']):
            return 'tutorial'
        elif any(pattern in title_lower for pattern in ['reference', 'api', 'specification']):
            return 'reference'
        elif any(pattern in title_lower for pattern in ['guide', 'overview', 'introduction']):
            return 'guide'
        elif any(pattern in title_lower for pattern in ['troubleshoot', 'error', 'fix', 'problem']):
            return 'troubleshooting'
        elif any(pattern in title_lower for pattern in ['faq', 'frequently asked']):
            return 'faq'
        elif any(pattern in title_lower for pattern in ['example', 'sample', 'demo']):
            return 'example'
        else:
            return 'article'
    
    def _generate_breadcrumbs(self, navigation_items: List[NavigationItem]) -> Dict[str, List[Dict[str, str]]]:
        """Generate breadcrumb navigation for all articles."""
        breadcrumbs = {}
        
        def build_breadcrumbs(item: NavigationItem, path: List[Dict[str, str]] = None):
            if path is None:
                path = []
            
            current_path = path + [{'title': item.title, 'url': item.path}]
            
            # If this item has an article_id, store breadcrumbs
            if item.metadata and 'article_id' in item.metadata:
                article_id = item.metadata['article_id']
                if article_id:
                    breadcrumbs[article_id] = current_path[1:]  # Skip root
            
            # Process children
            for child in item.children:
                build_breadcrumbs(child, current_path[:-1] if not item.path else current_path)
        
        # Build breadcrumbs for all navigation items
        for nav_item in navigation_items:
            build_breadcrumbs(nav_item)
        
        self.breadcrumb_cache = breadcrumbs
        return breadcrumbs
    
    async def _validate_navigation(self, navigation_items: List[NavigationItem], articles: List[Article]) -> Dict[str, Any]:
        """Validate navigation structure for common issues."""
        validation_report = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'duplicate_titles': [],
            'missing_articles': [],
            'deep_nesting': [],
            'empty_sections': [],
        }
        
        # Track titles to find duplicates
        title_counts = {}
        article_ids_in_nav = set()
        
        def validate_item(item: NavigationItem, depth: int = 0):
            # Check for deep nesting
            if depth > 4:  # More than 4 levels deep
                validation_report['deep_nesting'].append({
                    'title': item.title,
                    'depth': depth,
                    'path': item.path
                })
                validation_report['warnings'].append(f"Deep nesting detected: {item.title} at depth {depth}")
            
            # Track titles for duplicates
            title_counts[item.title] = title_counts.get(item.title, 0) + 1
            
            # Track article IDs
            if item.metadata and 'article_id' in item.metadata:
                article_id = item.metadata['article_id']
                if article_id:
                    article_ids_in_nav.add(article_id)
            
            # Check for empty sections
            if item.is_section and not item.children:
                validation_report['empty_sections'].append(item.title)
                validation_report['warnings'].append(f"Empty section: {item.title}")
            
            # Validate children
            for child in item.children:
                validate_item(child, depth + 1)
        
        # Validate all navigation items
        for nav_item in navigation_items:
            validate_item(nav_item)
        
        # Find duplicate titles
        duplicates = [title for title, count in title_counts.items() if count > 1]
        validation_report['duplicate_titles'] = duplicates
        if duplicates:
            validation_report['warnings'].extend([f"Duplicate title: {title}" for title in duplicates])
        
        # Find missing articles (articles not in navigation)
        all_article_ids = {a.id for a in articles if a.id}
        missing_article_ids = all_article_ids - article_ids_in_nav
        if missing_article_ids:
            missing_articles = [a for a in articles if a.id in missing_article_ids]
            validation_report['missing_articles'] = [{'id': a.id, 'title': a.title} for a in missing_articles]
            validation_report['warnings'].extend([f"Article not in navigation: {a.title}" for a in missing_articles])
        
        # Update analytics
        if self.enable_navigation_analytics:
            self.navigation_analytics.duplicate_titles = duplicates
            self.navigation_analytics.orphaned_articles.extend([a['id'] for a in validation_report['missing_articles']])
        
        # Set overall validity
        validation_report['is_valid'] = len(validation_report['errors']) == 0
        
        return validation_report
    
    def _convert_to_mkdocs_format(self, navigation_items: List[NavigationItem]) -> List[Dict[str, Any]]:
        """Convert NavigationItem objects to standard MkDocs navigation format."""
        def convert_item(item: NavigationItem) -> Dict[str, Any] | str:
            if not item.children:
                # Leaf item
                return {item.title: item.path} if item.path else item.title
            else:
                # Section with children
                children = [convert_item(child) for child in item.children]
                return {item.title: children}
        
        return [convert_item(item) for item in navigation_items]
    
    def _generate_literate_nav(self, navigation_items: List[NavigationItem]) -> str:
        """Generate mkdocs-literate-nav compatible SUMMARY.md content."""
        lines = ["# Navigation", ""]
        
        def add_nav_item(item: NavigationItem, level: int = 0):
            indent = "  " * level
            
            if item.path:
                # Item with path
                lines.append(f"{indent}* [{item.title}]({item.path})")
            else:
                # Section header
                lines.append(f"{indent}* {item.title}")
            
            # Add children
            for child in item.children:
                add_nav_item(child, level + 1 if item.path else level)
        
        # Process all navigation items
        for nav_item in navigation_items:
            add_nav_item(nav_item)
        
        return "\n".join(lines)
    
    def _calculate_max_depth(self, navigation_items: List[NavigationItem]) -> int:
        """Calculate maximum depth of navigation tree."""
        max_depth = 0
        
        def get_depth(item: NavigationItem) -> int:
            if not item.children:
                return item.level
            return max(get_depth(child) for child in item.children)
        
        for nav_item in navigation_items:
            depth = get_depth(nav_item)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def get_navigation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive navigation analytics."""
        if not self.enable_navigation_analytics:
            return {'enabled': False}
        
        analytics = self.navigation_analytics.__dict__.copy()
        analytics.update({
            'enabled': True,
            'section_indexes_count': len(self.section_indexes_generated),
            'breadcrumbs_generated': len(self.breadcrumb_cache),
            'navigation_tree_depth': self._calculate_max_depth([self.navigation_tree]) if self.navigation_tree else 0,
            'features_enabled': {
                'literate_nav': self.enable_literate_nav,
                'smart_ordering': self.smart_ordering,
                'section_indexes': self.generate_section_indexes,
                'breadcrumbs': self.enable_breadcrumbs,
                'validation': self.navigation_validation,
                'mobile_optimization': self.optimize_for_mobile,
            }
        })
        
        return analytics