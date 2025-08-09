"""Content enhancement for Document360 → MkDocs conversion.

This module provides comprehensive content optimization specifically for MkDocs,
including frontmatter enrichment, content validation, and quality assessment.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/content_enhancer.py

import re
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
from datetime import datetime
import asyncio
from urllib.parse import urlparse, urljoin

from loguru import logger

from d361.core.models import Article, Category

# Optional imports for HTML → Markdown conversion
try:
    import html2text
    from bs4 import BeautifulSoup
    import requests
    HTML_PROCESSING_AVAILABLE = True
except ImportError:
    HTML_PROCESSING_AVAILABLE = False
    logger.warning("HTML processing dependencies not available - install html2text, beautifulsoup4, requests for full functionality")

# Optional import for MkDocs extensions support
try:
    import markdown
    from markdown.extensions import admonition, codehilite, tables, toc
    MARKDOWN_EXTENSIONS_AVAILABLE = True
except ImportError:
    MARKDOWN_EXTENSIONS_AVAILABLE = False
    logger.warning("Python Markdown extensions not available - install markdown for enhanced processing")


class ContentEnhancer:
    """Enhance Document360 content for optimal MkDocs presentation.
    
    This class optimizes content for MkDocs by adding frontmatter, improving
    structure, validating quality, and ensuring proper cross-references.
    
    Features:
    - YAML frontmatter generation with MkDocs metadata
    - Content structure optimization (headings, links, images)
    - Quality assessment and validation
    - SEO metadata generation
    - Navigation hint generation
    - Tag and category extraction
    
    Example:
        enhancer = ContentEnhancer(
            site_url="https://docs.example.com",
            enable_seo=True,
            validate_links=True
        )
        enhanced_content = await enhancer.enhance_article(article)
    """
    
    def __init__(
        self,
        site_url: Optional[str] = None,
        enable_seo: bool = True,
        validate_links: bool = True,
        add_edit_links: bool = True,
        enable_social_cards: bool = False,
        custom_css_classes: Optional[Dict[str, str]] = None,
        # Phase 2 enhancements
        enable_html_conversion: bool = True,
        mkdocs_extensions: Optional[List[str]] = None,
        enable_admonitions: bool = True,
        enable_superfences: bool = True,
        enable_tabbed_content: bool = True,
        enable_task_lists: bool = True,
        validate_content_quality: bool = True,
        check_broken_links: bool = False,
        reading_time_estimation: bool = True,
    ) -> None:
        """Initialize content enhancer.
        
        Args:
            site_url: Base site URL for absolute link generation
            enable_seo: Enable SEO metadata generation
            validate_links: Validate internal and external links
            add_edit_links: Add edit link metadata to frontmatter
            enable_social_cards: Enable social card metadata
            custom_css_classes: Custom CSS classes for content elements
            # Phase 2 enhancements
            enable_html_conversion: Enable HTML → Markdown conversion
            mkdocs_extensions: List of MkDocs extensions to enable
            enable_admonitions: Enable admonition blocks (!!! note, !!! warning, etc.)
            enable_superfences: Enable enhanced code blocks with superfences
            enable_tabbed_content: Enable tabbed content containers
            enable_task_lists: Enable GitHub-style task lists
            validate_content_quality: Enable advanced content quality validation
            check_broken_links: Enable broken link detection and reporting
            reading_time_estimation: Enable reading time calculation
        """
        self.site_url = site_url.rstrip('/') if site_url else None
        self.enable_seo = enable_seo
        self.validate_links = validate_links
        self.add_edit_links = add_edit_links
        self.enable_social_cards = enable_social_cards
        self.custom_css_classes = custom_css_classes or {}
        
        # Phase 2 enhancements
        self.enable_html_conversion = enable_html_conversion and HTML_PROCESSING_AVAILABLE
        self.mkdocs_extensions = mkdocs_extensions or ['admonition', 'codehilite', 'tables', 'toc', 'footnotes', 'attr_list', 'def_list']
        self.enable_admonitions = enable_admonitions
        self.enable_superfences = enable_superfences
        self.enable_tabbed_content = enable_tabbed_content
        self.enable_task_lists = enable_task_lists
        self.validate_content_quality = validate_content_quality
        self.check_broken_links = check_broken_links
        self.reading_time_estimation = reading_time_estimation
        
        # Initialize HTML to Markdown converter if available
        if self.enable_html_conversion and HTML_PROCESSING_AVAILABLE:
            self._html_converter = html2text.HTML2Text()
            self._html_converter.ignore_links = False
            self._html_converter.ignore_images = False
            self._html_converter.ignore_emphasis = False
            self._html_converter.body_width = 0  # Don't wrap lines
            self._html_converter.unicode_snob = True
            self._html_converter.escape_snob = True
        else:
            self._html_converter = None
        
        # Initialize Markdown processor if available
        if MARKDOWN_EXTENSIONS_AVAILABLE:
            self._markdown_processor = markdown.Markdown(
                extensions=self.mkdocs_extensions,
                extension_configs={
                    'codehilite': {'css_class': 'highlight'},
                    'toc': {'permalink': True},
                }
            )
        else:
            self._markdown_processor = None
        
        # Compile regex patterns for performance
        self._heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self._link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self._image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self._code_block_pattern = re.compile(r'^```(\w+)?\n(.*?)^```$', re.MULTILINE | re.DOTALL)
        
        # Phase 2 patterns
        self._html_pattern = re.compile(r'<[^>]+>')
        self._broken_link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]*)\)')
        self._admonition_pattern = re.compile(r'^!!! (note|warning|info|tip|success|question|failure|danger|bug|example|quote)\s*(.*?)$', re.MULTILINE)
        
        logger.debug(f"Initialized ContentEnhancer with site_url={site_url}, HTML conversion={self.enable_html_conversion}")
    
    async def enhance_article(self, article: Article) -> Dict[str, Any]:
        """Enhance a single article for MkDocs.
        
        Args:
            article: Article to enhance
            
        Returns:
            Dictionary with enhanced content and metadata
        """
        logger.debug(f"Enhancing article: {article.title}")
        
        raw_content = article.content or ""
        
        # Phase 2: Convert HTML to Markdown if needed
        if self.enable_html_conversion and self._has_html_content(raw_content):
            raw_content = await self._convert_html_to_markdown(raw_content)
            logger.debug(f"Converted HTML to Markdown for article: {article.title}")
        
        # Phase 2: Process MkDocs extensions
        if self.enable_admonitions:
            raw_content = self._convert_to_admonitions(raw_content)
        
        if self.enable_superfences:
            raw_content = self._enhance_code_blocks_superfences(raw_content)
        
        if self.enable_tabbed_content:
            raw_content = self._convert_to_tabbed_content(raw_content)
            
        if self.enable_task_lists:
            raw_content = self._convert_to_task_lists(raw_content)
        
        # Generate frontmatter
        frontmatter = self._generate_frontmatter(article)
        
        # Process content (original processing)
        enhanced_content = self._process_content(raw_content)
        
        # Phase 2: Advanced quality assessment
        quality_metrics = await self._assess_quality_advanced(enhanced_content, article)
        
        # Phase 2: Broken link detection
        broken_links = []
        if self.check_broken_links:
            broken_links = await self._detect_broken_links(enhanced_content)
        
        # Generate navigation hints
        nav_hints = self._generate_navigation_hints(article)
        
        # Phase 2: Reading time estimation
        reading_time = 0
        if self.reading_time_estimation:
            reading_time = self._calculate_reading_time(enhanced_content)
        
        result = {
            'frontmatter': frontmatter,
            'content': enhanced_content,
            'quality_metrics': quality_metrics,
            'navigation_hints': nav_hints,
            'file_path': self._generate_file_path(article),
            'edit_url': self._generate_edit_url(article) if self.add_edit_links else None,
            # Phase 2 additions
            'broken_links': broken_links,
            'reading_time': reading_time,
            'has_html_conversion': self.enable_html_conversion and self._has_html_content(article.content or ""),
            'mkdocs_extensions_used': self._get_used_extensions(enhanced_content),
        }
        
        logger.debug(f"Enhanced article '{article.title}' with quality score: {quality_metrics.get('overall_score', 0)}, reading time: {reading_time}min")
        return result
    
    def _generate_frontmatter(self, article: Article) -> Dict[str, Any]:
        """Generate YAML frontmatter for the article.
        
        Args:
            article: Article to generate frontmatter for
            
        Returns:
            Dictionary of frontmatter data
        """
        frontmatter = {
            'title': article.title,
            'description': self._extract_description(article.content or ""),
        }
        
        # Add basic metadata
        if article.slug:
            frontmatter['slug'] = article.slug
        
        if hasattr(article, 'created_at') and article.created_at:
            frontmatter['date'] = article.created_at.isoformat()
        
        if hasattr(article, 'updated_at') and article.updated_at:
            frontmatter['last_modified'] = article.updated_at.isoformat()
        
        # Add category information
        if hasattr(article, 'category_id') and article.category_id:
            frontmatter['category_id'] = article.category_id
        
        # Add tags if available
        tags = self._extract_tags(article)
        if tags:
            frontmatter['tags'] = tags
        
        # Add SEO metadata if enabled
        if self.enable_seo:
            seo_data = self._generate_seo_metadata(article)
            frontmatter.update(seo_data)
        
        # Add social card metadata if enabled
        if self.enable_social_cards:
            social_data = self._generate_social_card_metadata(article)
            frontmatter.update(social_data)
        
        # Add custom template if needed
        template = self._determine_template(article)
        if template:
            frontmatter['template'] = template
        
        return frontmatter
    
    def _process_content(self, content: str) -> str:
        """Process and enhance markdown content.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Enhanced markdown content
        """
        # Normalize headings
        content = self._normalize_headings(content)
        
        # Process links
        content = self._process_links(content)
        
        # Process images
        content = self._process_images(content)
        
        # Enhance code blocks
        content = self._enhance_code_blocks(content)
        
        # Add custom CSS classes if configured
        content = self._add_css_classes(content)
        
        # Clean up whitespace
        content = self._clean_whitespace(content)
        
        return content
    
    def _normalize_headings(self, content: str) -> str:
        """Normalize heading structure for better MkDocs navigation.
        
        Args:
            content: Content to normalize
            
        Returns:
            Content with normalized headings
        """
        def replace_heading(match):
            level = len(match.group(1))
            title = match.group(2).strip()
            
            # Ensure we don't have H1 in content (reserved for page title)
            if level == 1:
                level = 2
            
            # Add anchor-friendly ID if it doesn't exist
            anchor_id = re.sub(r'[^\w\-]', '-', title.lower()).strip('-')
            anchor_id = re.sub(r'-+', '-', anchor_id)
            
            return f"{'#' * level} {title} {{: #{anchor_id} }}"
        
        return self._heading_pattern.sub(replace_heading, content)
    
    def _process_links(self, content: str) -> str:
        """Process and validate links in content.
        
        Args:
            content: Content with links to process
            
        Returns:
            Content with processed links
        """
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            
            # Process internal Document360 links
            if self._is_internal_d360_link(url):
                processed_url = self._convert_internal_link(url)
                return f"[{text}]({processed_url})"
            
            # Add external link attributes
            if self._is_external_link(url):
                return f"[{text}]({url}){{: target=\"_blank\" rel=\"noopener noreferrer\" }}"
            
            return match.group(0)
        
        return self._link_pattern.sub(replace_link, content)
    
    def _process_images(self, content: str) -> str:
        """Process images for optimal MkDocs display.
        
        Args:
            content: Content with images to process
            
        Returns:
            Content with processed images
        """
        def replace_image(match):
            alt_text = match.group(1)
            src = match.group(2)
            
            # Process Document360 CDN URLs
            if 'document360' in src.lower():
                processed_src = self._process_d360_image_url(src)
                return f"![{alt_text}]({processed_src})"
            
            # Add responsive image attributes for large images
            if self._is_large_image_url(src):
                return f"![{alt_text}]({src}){{: .responsive-image loading=\"lazy\" }}"
            
            return match.group(0)
        
        return self._image_pattern.sub(replace_image, content)
    
    def _enhance_code_blocks(self, content: str) -> str:
        """Enhance code blocks with better formatting and features.
        
        Args:
            content: Content with code blocks
            
        Returns:
            Content with enhanced code blocks
        """
        def replace_code_block(match):
            language = match.group(1) or ""
            code = match.group(2).strip()
            
            # Detect language if not specified
            if not language:
                language = self._detect_code_language(code)
            
            # Add line numbers for long code blocks
            if len(code.split('\n')) > 10:
                return f"```{language} linenums=\"1\"\n{code}\n```"
            else:
                return f"```{language}\n{code}\n```"
        
        return self._code_block_pattern.sub(replace_code_block, content)
    
    def _add_css_classes(self, content: str) -> str:
        """Add custom CSS classes to content elements.
        
        Args:
            content: Content to enhance with CSS classes
            
        Returns:
            Content with added CSS classes
        """
        if not self.custom_css_classes:
            return content
        
        # Add classes based on configuration
        for element, css_class in self.custom_css_classes.items():
            if element == 'tables':
                content = re.sub(
                    r'(\|.*\|)', 
                    f'\\1{{: .{css_class} }}', 
                    content
                )
            elif element == 'blockquotes':
                content = re.sub(
                    r'^(>\s*.+)$', 
                    f'\\1{{: .{css_class} }}', 
                    content, 
                    flags=re.MULTILINE
                )
        
        return content
    
    def _clean_whitespace(self, content: str) -> str:
        """Clean up excessive whitespace in content.
        
        Args:
            content: Content to clean
            
        Returns:
            Cleaned content
        """
        # Remove excessive blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove trailing whitespace from lines
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        
        # Ensure single newline at end of file
        content = content.rstrip() + '\n'
        
        return content
    
    def _assess_quality(self, content: str) -> Dict[str, Any]:
        """Assess content quality for MkDocs optimization.
        
        Args:
            content: Content to assess
            
        Returns:
            Quality metrics dictionary
        """
        metrics = {
            'word_count': len(content.split()),
            'heading_count': len(self._heading_pattern.findall(content)),
            'link_count': len(self._link_pattern.findall(content)),
            'image_count': len(self._image_pattern.findall(content)),
            'code_block_count': len(self._code_block_pattern.findall(content)),
            'estimated_reading_time': max(1, len(content.split()) // 200),  # ~200 WPM
        }
        
        # Calculate overall quality score (0-100)
        score = 0
        
        # Word count scoring
        if 100 <= metrics['word_count'] <= 2000:
            score += 30
        elif metrics['word_count'] > 2000:
            score += 20
        elif metrics['word_count'] >= 50:
            score += 15
        
        # Structure scoring
        if metrics['heading_count'] > 0:
            score += 20
        if metrics['heading_count'] >= 3:
            score += 10
        
        # Content richness scoring
        if metrics['link_count'] > 0:
            score += 15
        if metrics['image_count'] > 0:
            score += 15
        if metrics['code_block_count'] > 0:
            score += 10
        
        metrics['overall_score'] = min(100, score)
        metrics['quality_level'] = self._determine_quality_level(score)
        
        return metrics
    
    def _generate_navigation_hints(self, article: Article) -> Dict[str, Any]:
        """Generate navigation hints for MkDocs.
        
        Args:
            article: Article to generate hints for
            
        Returns:
            Navigation hints dictionary
        """
        return {
            'suggested_nav_title': self._generate_nav_title(article.title),
            'breadcrumb_path': self._generate_breadcrumb_path(article),
            'related_articles': [],  # Could be enhanced with ML-based suggestions
            'navigation_weight': self._calculate_navigation_weight(article),
        }
    
    def _generate_file_path(self, article: Article) -> str:
        """Generate appropriate file path for the article.
        
        Args:
            article: Article to generate path for
            
        Returns:
            Suggested file path
        """
        if article.slug:
            base_name = article.slug
        else:
            # Generate slug from title
            base_name = re.sub(r'[^\w\-]', '-', article.title.lower()).strip('-')
            base_name = re.sub(r'-+', '-', base_name)
        
        # Ensure .md extension
        if not base_name.endswith('.md'):
            base_name += '.md'
        
        return base_name
    
    # Phase 2: Advanced Enhancement Methods
    
    def _has_html_content(self, content: str) -> bool:
        """Check if content contains HTML tags."""
        return bool(self._html_pattern.search(content))
    
    async def _convert_html_to_markdown(self, content: str) -> str:
        """Convert HTML content to Markdown using html2text."""
        if not self._html_converter:
            return content
        
        try:
            # Clean up common HTML issues before conversion
            content = self._preprocess_html(content)
            
            # Convert HTML to Markdown
            markdown_content = self._html_converter.handle(content)
            
            # Post-process the converted markdown
            markdown_content = self._postprocess_converted_markdown(markdown_content)
            
            return markdown_content
            
        except Exception as e:
            logger.warning(f"Failed to convert HTML to Markdown: {e}")
            return content
    
    def _preprocess_html(self, html_content: str) -> str:
        """Preprocess HTML before conversion."""
        if not HTML_PROCESSING_AVAILABLE:
            return html_content
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Convert Document360-specific elements
        for div in soup.find_all('div', class_='callout'):
            # Convert callouts to admonition format
            callout_type = div.get('data-type', 'note')
            title = div.find(class_='callout-title')
            title_text = title.get_text().strip() if title else ''
            
            # Replace with admonition placeholder
            div.name = 'div'
            div['class'] = f'admonition-{callout_type}'
            if title_text:
                div['data-title'] = title_text
        
        # Convert code blocks
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                lang = code.get('class', [''])[0].replace('language-', '') if code.get('class') else ''
                pre['data-language'] = lang
        
        return str(soup)
    
    def _postprocess_converted_markdown(self, markdown_content: str) -> str:
        """Post-process converted Markdown content."""
        # Fix common conversion issues
        
        # Fix excessive newlines
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # Fix broken links
        markdown_content = re.sub(r'\[\]\(([^)]+)\)', r'[\1](\1)', markdown_content)
        
        # Fix image alt text
        markdown_content = re.sub(r'!\[\]\(([^)]+)\)', r'![Image](\1)', markdown_content)
        
        return markdown_content.strip()
    
    def _convert_to_admonitions(self, content: str) -> str:
        """Convert various callout formats to MkDocs admonitions."""
        # Convert blockquotes with specific patterns to admonitions
        content = re.sub(
            r'> \*\*Note:\*\*\s*(.*?)(?=\n(?:[^>]|\n))',
            r'!!! note "Note"\n    \1',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        content = re.sub(
            r'> \*\*Warning:\*\*\s*(.*?)(?=\n(?:[^>]|\n))',
            r'!!! warning "Warning"\n    \1',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        content = re.sub(
            r'> \*\*Tip:\*\*\s*(.*?)(?=\n(?:[^>]|\n))',
            r'!!! tip "Tip"\n    \1',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Convert HTML callouts from preprocessing
        content = re.sub(
            r'<div class="admonition-(\w+)"(?: data-title="([^"]*)")?>(.*?)</div>',
            lambda m: f'!!! {m.group(1)} "{m.group(2) or m.group(1).title()}"\n    {m.group(3).strip()}',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        return content
    
    def _enhance_code_blocks_superfences(self, content: str) -> str:
        """Enhance code blocks with superfences features."""
        def enhance_code_block(match):
            language = match.group(1) or ""
            code = match.group(2).strip()
            
            # Add title if language suggests it's a filename
            if language in ['bash', 'shell', 'sh']:
                if any(keyword in code for keyword in ['curl', 'wget', 'pip install', 'npm install']):
                    return f'```{language} title="Command"\n{code}\n```'
            elif language in ['yaml', 'yml']:
                if 'site_name' in code or 'nav:' in code:
                    return f'```{language} title="mkdocs.yml"\n{code}\n```'
            elif language in ['json']:
                if '"name"' in code and '"version"' in code:
                    return f'```{language} title="package.json"\n{code}\n```'
            
            # Add line numbers for long blocks
            line_count = len(code.split('\n'))
            if line_count > 10:
                return f'```{language} linenums="1"\n{code}\n```'
            
            return match.group(0)
        
        return self._code_block_pattern.sub(enhance_code_block, content)
    
    def _convert_to_tabbed_content(self, content: str) -> str:
        """Convert sections to tabbed content where appropriate."""
        # Look for patterns that suggest tabbed content
        # Example: multiple H3s that look like different approaches/languages
        
        tab_patterns = [
            (r'### Python\n(.*?)\n### JavaScript\n(.*?)\n### cURL\n(.*?)(?=\n###|\n\n|\Z)', 'code-examples'),
            (r'### Windows\n(.*?)\n### macOS\n(.*?)\n### Linux\n(.*?)(?=\n###|\n\n|\Z)', 'platform-specific'),
            (r'### Step 1\n(.*?)\n### Step 2\n(.*?)\n### Step 3\n(.*?)(?=\n###|\n\n|\Z)', 'steps'),
        ]
        
        for pattern, tab_type in tab_patterns:
            def replace_with_tabs(match):
                parts = [match.group(i) for i in range(1, match.lastindex + 1)]
                tab_names = ['Python', 'JavaScript', 'cURL'] if tab_type == 'code-examples' else ['Windows', 'macOS', 'Linux'] if tab_type == 'platform-specific' else [f'Step {i}' for i in range(1, len(parts) + 1)]
                
                tabs_content = []
                for i, (name, content) in enumerate(zip(tab_names, parts)):
                    indent = "    "
                    indented_content = '\n'.join(indent + line if line.strip() else '' for line in content.strip().split('\n'))
                    tabs_content.append(f'=== "{name}"\n\n{indented_content}')
                
                return '\n\n'.join(tabs_content)
            
            content = re.sub(pattern, replace_with_tabs, content, flags=re.MULTILINE | re.DOTALL)
        
        return content
    
    def _convert_to_task_lists(self, content: str) -> str:
        """Convert list items to GitHub-style task lists where appropriate."""
        # Convert "- [ ]" and "- [x]" patterns
        content = re.sub(r'^(\s*)- \[ \]', r'\1- [ ]', content, flags=re.MULTILINE)
        content = re.sub(r'^(\s*)- \[x\]', r'\1- [x]', content, flags=re.MULTILINE)
        content = re.sub(r'^(\s*)- \[X\]', r'\1- [x]', content, flags=re.MULTILINE)
        
        # Convert checklist-like patterns
        content = re.sub(r'^(\s*)- (.*?)(\s*)\(completed\)', r'\1- [x] \2', content, flags=re.MULTILINE)
        content = re.sub(r'^(\s*)- (.*?)(\s*)\(pending\)', r'\1- [ ] \2', content, flags=re.MULTILINE)
        content = re.sub(r'^(\s*)- (.*?)(\s*)\(todo\)', r'\1- [ ] \2', content, flags=re.MULTILINE)
        
        return content
    
    async def _assess_quality_advanced(self, content: str, article: Article) -> Dict[str, Any]:
        """Advanced content quality assessment for Phase 2."""
        # Get basic quality metrics first
        basic_metrics = self._assess_quality(content)
        
        # Advanced quality analysis
        advanced_metrics = {
            'has_introduction': self._has_introduction(content),
            'has_conclusion': self._has_conclusion(content),
            'heading_structure_score': self._analyze_heading_structure(content),
            'content_depth_score': self._analyze_content_depth(content),
            'internal_linking_score': self._analyze_internal_linking(content),
            'code_example_quality': self._analyze_code_examples(content),
            'media_richness_score': self._analyze_media_richness(content),
            'readability_score': self._calculate_readability_score(content),
            'seo_optimization_score': self._analyze_seo_optimization(content, article),
            'mkdocs_compatibility_score': self._analyze_mkdocs_compatibility(content),
        }
        
        # Calculate enhanced overall score
        weights = {
            'word_count': 0.15,
            'heading_structure': 0.15,
            'content_depth': 0.15,
            'internal_linking': 0.10,
            'code_quality': 0.10,
            'media_richness': 0.10,
            'readability': 0.10,
            'seo_optimization': 0.10,
            'mkdocs_compatibility': 0.05
        }
        
        enhanced_score = (
            (basic_metrics['overall_score'] * weights['word_count']) +
            (advanced_metrics['heading_structure_score'] * weights['heading_structure']) +
            (advanced_metrics['content_depth_score'] * weights['content_depth']) +
            (advanced_metrics['internal_linking_score'] * weights['internal_linking']) +
            (advanced_metrics['code_example_quality'] * weights['code_quality']) +
            (advanced_metrics['media_richness_score'] * weights['media_richness']) +
            (advanced_metrics['readability_score'] * weights['readability']) +
            (advanced_metrics['seo_optimization_score'] * weights['seo_optimization']) +
            (advanced_metrics['mkdocs_compatibility_score'] * weights['mkdocs_compatibility'])
        )
        
        # Merge basic and advanced metrics
        combined_metrics = {**basic_metrics, **advanced_metrics}
        combined_metrics['overall_score'] = min(100, enhanced_score)
        combined_metrics['quality_level'] = self._determine_quality_level(enhanced_score)
        combined_metrics['recommendations'] = self._generate_quality_recommendations(combined_metrics)
        
        return combined_metrics
    
    async def _detect_broken_links(self, content: str) -> List[Dict[str, Any]]:
        """Detect potentially broken links in content."""
        broken_links = []
        
        for match in self._broken_link_pattern.finditer(content):
            text = match.group(1)
            url = match.group(2)
            
            # Skip if URL is empty or anchor-only
            if not url or url.startswith('#'):
                continue
            
            is_broken = False
            error_reason = None
            
            # Check for obvious issues
            if not url.strip():
                is_broken = True
                error_reason = "Empty URL"
            elif url.count('(') != url.count(')'):
                is_broken = True
                error_reason = "Malformed URL - unmatched parentheses"
            elif re.match(r'^\w+:(?!//).*', url):
                # Malformed protocol
                is_broken = True
                error_reason = "Malformed protocol"
            elif url.startswith('http') and not re.match(r'https?://\S+', url):
                is_broken = True
                error_reason = "Invalid HTTP URL format"
            
            # For external links, could add actual HTTP checking here
            # (but that would be expensive, so we'll keep it simple for now)
            
            if is_broken:
                broken_links.append({
                    'text': text,
                    'url': url,
                    'error': error_reason,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return broken_links
    
    def _calculate_reading_time(self, content: str) -> int:
        """Calculate estimated reading time in minutes."""
        # Average reading speed: 200-250 WPM for technical content
        words_per_minute = 220
        
        # Count words, but adjust for code blocks (slower reading)
        words = len(content.split())
        
        # Count code blocks and add extra time
        code_blocks = len(self._code_block_pattern.findall(content))
        code_lines = sum(len(block[1].split('\n')) for block in self._code_block_pattern.findall(content))
        
        # Add extra time for code (slower reading/processing)
        code_adjustment = (code_lines * 0.5) + (code_blocks * 1)  # 0.5 min per code line + 1 min per block
        
        # Calculate reading time
        base_time = words / words_per_minute
        total_time = base_time + code_adjustment
        
        return max(1, round(total_time))
    
    def _get_used_extensions(self, content: str) -> List[str]:
        """Identify which MkDocs extensions are being used in content."""
        used_extensions = []
        
        # Check for admonitions
        if re.search(r'^!!! \w+', content, re.MULTILINE):
            used_extensions.append('admonition')
        
        # Check for code blocks with highlighting
        if re.search(r'^```\w+', content, re.MULTILINE):
            used_extensions.append('codehilite')
        
        # Check for tables
        if '|' in content and re.search(r'\|.*\|.*\|', content):
            used_extensions.append('tables')
        
        # Check for footnotes
        if re.search(r'\[\^\w+\]', content):
            used_extensions.append('footnotes')
        
        # Check for definition lists
        if re.search(r'^\w+.*\n:\s+', content, re.MULTILINE):
            used_extensions.append('def_list')
        
        # Check for task lists
        if re.search(r'^- \[[x ]\]', content, re.MULTILINE):
            used_extensions.append('task_list')
        
        # Check for tabbed content
        if re.search(r'^=== "', content, re.MULTILINE):
            used_extensions.append('pymdownx.tabbed')
        
        return used_extensions
    
    # Advanced quality analysis helper methods
    
    def _has_introduction(self, content: str) -> bool:
        """Check if content has a proper introduction."""
        # Look for introduction patterns in the first few paragraphs
        first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:500]
        intro_patterns = [
            r'\bintroduction\b',
            r'\boverview\b',
            r'\bthis (guide|tutorial|article|document)\b',
            r'\bin this (guide|tutorial|article|document)\b',
            r'\blearn (how to|about)\b'
        ]
        return any(re.search(pattern, first_paragraph, re.IGNORECASE) for pattern in intro_patterns)
    
    def _has_conclusion(self, content: str) -> bool:
        """Check if content has a proper conclusion."""
        # Look for conclusion patterns in the last few paragraphs
        last_paragraphs = content.split('\n\n')[-3:] if '\n\n' in content else [content[-500:]]
        conclusion_patterns = [
            r'\bconclusion\b',
            r'\bsummary\b',
            r'\bin (summary|conclusion)\b',
            r'\b(next steps|what\'s next)\b',
            r'\bto summarize\b'
        ]
        for paragraph in last_paragraphs:
            if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in conclusion_patterns):
                return True
        return False
    
    def _analyze_heading_structure(self, content: str) -> int:
        """Analyze heading structure quality (0-100)."""
        headings = self._heading_pattern.findall(content)
        if not headings:
            return 0
        
        score = 50  # Base score for having headings
        
        # Check for logical heading hierarchy
        levels = [len(h[0]) for h in headings]
        
        # Penalty for skipping heading levels
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                score -= 10
        
        # Bonus for good heading distribution
        if 3 <= len(headings) <= 8:
            score += 20
        elif len(headings) > 8:
            score += 10
        
        # Bonus for having H2s (good structure)
        if any(level == 2 for level in levels):
            score += 15
        
        return min(100, max(0, score))
    
    def _analyze_content_depth(self, content: str) -> int:
        """Analyze content depth and comprehensiveness (0-100)."""
        word_count = len(content.split())
        
        if word_count < 100:
            return 20
        elif word_count < 300:
            return 40
        elif word_count < 800:
            return 70
        elif word_count < 2000:
            return 90
        else:
            return 85  # Very long content might have quality issues
    
    def _analyze_internal_linking(self, content: str) -> int:
        """Analyze internal linking quality (0-100)."""
        links = self._link_pattern.findall(content)
        internal_links = [link for link in links if not link[1].startswith(('http://', 'https://'))]
        
        word_count = len(content.split())
        if word_count == 0:
            return 0
        
        # Ratio of internal links to words
        link_ratio = len(internal_links) / max(word_count, 1) * 100
        
        if link_ratio > 2:
            return 100
        elif link_ratio > 1:
            return 80
        elif link_ratio > 0.5:
            return 60
        elif link_ratio > 0:
            return 40
        else:
            return 20
    
    def _analyze_code_examples(self, content: str) -> int:
        """Analyze code example quality (0-100)."""
        code_blocks = self._code_block_pattern.findall(content)
        if not code_blocks:
            return 50  # Not all content needs code examples
        
        score = 60  # Base score for having code examples
        
        # Bonus for language specification
        lang_specified = sum(1 for block in code_blocks if block[0])
        score += min(30, (lang_specified / len(code_blocks)) * 30)
        
        # Bonus for reasonable code block length
        avg_length = sum(len(block[1].split('\n')) for block in code_blocks) / len(code_blocks)
        if 3 <= avg_length <= 20:
            score += 10
        
        return min(100, score)
    
    def _analyze_media_richness(self, content: str) -> int:
        """Analyze media richness (images, videos, etc.) (0-100)."""
        images = self._image_pattern.findall(content)
        word_count = len(content.split())
        
        if word_count == 0:
            return 50
        
        # Ideal ratio: 1 image per 200-500 words
        ideal_images = word_count / 350
        actual_images = len(images)
        
        if actual_images == 0:
            return 30
        elif abs(actual_images - ideal_images) <= 1:
            return 100
        elif abs(actual_images - ideal_images) <= 2:
            return 80
        else:
            return 60
    
    def _calculate_readability_score(self, content: str) -> int:
        """Calculate readability score (simplified) (0-100)."""
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        if not sentences or not words:
            return 50
        
        # Average words per sentence (ideal: 15-20)
        avg_words_per_sentence = len(words) / len(sentences)
        
        if 15 <= avg_words_per_sentence <= 20:
            sentence_score = 100
        elif 10 <= avg_words_per_sentence <= 25:
            sentence_score = 80
        elif 8 <= avg_words_per_sentence <= 30:
            sentence_score = 60
        else:
            sentence_score = 40
        
        # Check for transition words
        transitions = ['however', 'therefore', 'furthermore', 'additionally', 'consequently']
        transition_count = sum(content.lower().count(word) for word in transitions)
        transition_score = min(20, transition_count * 5)
        
        return min(100, sentence_score + transition_score)
    
    def _analyze_seo_optimization(self, content: str, article: Article) -> int:
        """Analyze SEO optimization (0-100)."""
        score = 50  # Base score
        
        # Check if title appears in first paragraph
        first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content[:200]
        if article.title.lower() in first_paragraph.lower():
            score += 15
        
        # Check for meta description potential
        if len(first_paragraph) >= 120:
            score += 10
        
        # Check for headings (good for SEO)
        headings = self._heading_pattern.findall(content)
        if headings:
            score += 15
        
        # Check for internal links
        internal_links = [link for link in self._link_pattern.findall(content) 
                         if not link[1].startswith(('http://', 'https://'))]
        if internal_links:
            score += 10
        
        return min(100, score)
    
    def _analyze_mkdocs_compatibility(self, content: str) -> int:
        """Analyze MkDocs compatibility score (0-100)."""
        score = 80  # Good base score
        
        # Bonus for using MkDocs extensions
        if re.search(r'^!!! \w+', content, re.MULTILINE):
            score += 5
        
        if re.search(r'^=== "', content, re.MULTILINE):
            score += 5
        
        if re.search(r'^- \[[x ]\]', content, re.MULTILINE):
            score += 5
        
        # Check for potential issues
        if '<script' in content.lower():
            score -= 20  # JavaScript might not work well
        
        if '<style' in content.lower():
            score -= 10  # Inline styles should be avoided
        
        return min(100, max(0, score))
    
    def _generate_quality_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on quality metrics."""
        recommendations = []
        
        if metrics.get('word_count', 0) < 100:
            recommendations.append("Consider expanding the content - articles with at least 200 words tend to be more helpful")
        
        if metrics.get('heading_count', 0) == 0:
            recommendations.append("Add headings to improve content structure and navigation")
        
        if not metrics.get('has_introduction', False):
            recommendations.append("Add an introduction to help readers understand what they'll learn")
        
        if not metrics.get('has_conclusion', False):
            recommendations.append("Add a conclusion or summary to wrap up the content")
        
        if metrics.get('internal_linking_score', 0) < 40:
            recommendations.append("Add more internal links to related articles to improve navigation")
        
        if metrics.get('media_richness_score', 0) < 40:
            recommendations.append("Consider adding relevant images or diagrams to illustrate key concepts")
        
        if metrics.get('readability_score', 0) < 60:
            recommendations.append("Consider breaking up long sentences and paragraphs for better readability")
        
        if len(metrics.get('broken_links', [])) > 0:
            recommendations.append("Fix broken links found in the content")
        
        return recommendations
    
    # Helper methods
    def _extract_description(self, content: str) -> str:
        """Extract description from content."""
        # Remove markdown formatting and take first paragraph
        clean_content = re.sub(r'[#*`\[\]()!]', '', content)
        paragraphs = clean_content.split('\n\n')
        
        if paragraphs:
            desc = paragraphs[0].strip()[:160]  # SEO-friendly length
            return desc + '...' if len(paragraphs[0]) > 160 else desc
        
        return ""
    
    def _extract_tags(self, article: Article) -> List[str]:
        """Extract tags from article metadata."""
        tags = []
        
        # Extract from content (e.g., #hashtags)
        if article.content:
            hashtag_pattern = re.compile(r'#(\w+)')
            hashtags = hashtag_pattern.findall(article.content)
            tags.extend(hashtags[:5])  # Limit to 5 tags
        
        # Add category as tag if available
        if hasattr(article, 'category_name') and article.category_name:
            tags.append(article.category_name.lower().replace(' ', '-'))
        
        return list(set(tags))  # Remove duplicates
    
    def _generate_seo_metadata(self, article: Article) -> Dict[str, str]:
        """Generate SEO metadata."""
        return {
            'og:title': article.title,
            'og:description': self._extract_description(article.content or ""),
            'og:type': 'article',
            'twitter:card': 'summary',
            'twitter:title': article.title,
        }
    
    def _generate_social_card_metadata(self, article: Article) -> Dict[str, str]:
        """Generate social card metadata."""
        return {
            'social_card': True,
            'social_card_title': article.title,
            'social_card_description': self._extract_description(article.content or ""),
        }
    
    def _determine_template(self, article: Article) -> Optional[str]:
        """Determine appropriate MkDocs template."""
        # Could be enhanced with content analysis
        return None
    
    def _is_internal_d360_link(self, url: str) -> bool:
        """Check if URL is an internal Document360 link."""
        return 'document360' in url.lower() or url.startswith('/') or url.startswith('../')
    
    def _convert_internal_link(self, url: str) -> str:
        """Convert Document360 internal link to MkDocs format."""
        # This would need to be customized based on the specific URL structure
        return url.replace('/docs/', '../').replace('.html', '.md')
    
    def _is_external_link(self, url: str) -> bool:
        """Check if URL is external."""
        return url.startswith(('http://', 'https://')) and self.site_url and self.site_url not in url
    
    def _process_d360_image_url(self, src: str) -> str:
        """Process Document360 CDN image URLs."""
        # Add optimization parameters or convert to local paths
        return src
    
    def _is_large_image_url(self, src: str) -> bool:
        """Check if image URL likely points to a large image."""
        large_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
        return any(src.lower().endswith(ext) for ext in large_extensions)
    
    def _detect_code_language(self, code: str) -> str:
        """Detect programming language from code content."""
        # Simple heuristic-based detection
        code_lower = code.lower()
        
        if 'def ' in code_lower and 'import ' in code_lower:
            return 'python'
        elif 'function' in code_lower and ('{' in code or '}' in code):
            return 'javascript'
        elif 'SELECT' in code.upper() and 'FROM' in code.upper():
            return 'sql'
        elif '<?php' in code_lower:
            return 'php'
        elif 'curl' in code_lower or '$' in code:
            return 'bash'
        
        return 'text'
    
    def _determine_quality_level(self, score: int) -> str:
        """Determine quality level from score."""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _generate_nav_title(self, title: str) -> str:
        """Generate navigation-friendly title."""
        return title[:50] + '...' if len(title) > 50 else title
    
    def _generate_breadcrumb_path(self, article: Article) -> List[str]:
        """Generate breadcrumb path."""
        path = []
        
        if hasattr(article, 'category_name') and article.category_name:
            path.append(article.category_name)
        
        path.append(article.title)
        return path
    
    def _calculate_navigation_weight(self, article: Article) -> int:
        """Calculate navigation weight for ordering."""
        # Could be based on article popularity, date, etc.
        return getattr(article, 'order', 0)
    
    def _generate_edit_url(self, article: Article) -> Optional[str]:
        """Generate edit URL for the article."""
        if not self.site_url:
            return None
        
        # This would need to be customized based on the repository structure
        file_path = self._generate_file_path(article)
        return f"{self.site_url}/edit/main/docs/{file_path}"