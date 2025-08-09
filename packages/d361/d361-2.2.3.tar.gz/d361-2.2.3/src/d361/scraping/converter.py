# this_file: external/int_folders/d361/src/d361/scraping/converter.py
"""
HTML to Markdown conversion with Document360-specific optimizations.

This module provides robust HTML-to-Markdown conversion with custom formatting
rules, link handling, and asset reference management optimized for Document360
content structure and presentation requirements.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin, urlparse

from loguru import logger
from pydantic import BaseModel, Field, validator
from bs4 import BeautifulSoup, Tag
import markdownify
from markdownify import MarkdownConverter as BaseMarkdownConverter

from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class MarkdownStyle(str, Enum):
    """Markdown formatting styles."""
    GITHUB = "github"           # GitHub-flavored markdown
    DOCUMENT360 = "document360" # Document360 optimized
    STANDARD = "standard"       # Standard markdown
    MINIMAL = "minimal"         # Minimal formatting


class LinkHandling(str, Enum):
    """Link processing strategies."""
    PRESERVE = "preserve"       # Keep original URLs
    RELATIVIZE = "relativize"   # Convert to relative paths
    RESOLVE = "resolve"         # Resolve all to absolute URLs
    REMOVE = "remove"          # Remove links entirely


@dataclass
class ConversionStats:
    """Statistics from markdown conversion."""
    input_size: int = 0
    output_size: int = 0
    elements_converted: int = 0
    links_processed: int = 0
    images_processed: int = 0
    tables_converted: int = 0
    code_blocks_found: int = 0
    warnings: List[str] = field(default_factory=list)
    processing_time_ms: float = 0


class ConversionConfig(BaseModel):
    """Configuration for HTML to Markdown conversion."""
    
    # Style and formatting
    style: MarkdownStyle = Field(
        default=MarkdownStyle.DOCUMENT360,
        description="Markdown style to use"
    )
    
    # Link handling
    link_handling: LinkHandling = Field(
        default=LinkHandling.PRESERVE,
        description="How to handle links during conversion"
    )
    
    base_url: Optional[str] = Field(
        None,
        description="Base URL for relative link resolution"
    )
    
    # Content processing
    strip_tags: List[str] = Field(
        default=[
            "script", "style", "nav", "footer", "aside",
            ".sidebar", ".navigation", ".ads"
        ],
        description="HTML tags/selectors to remove"
    )
    
    preserve_attributes: List[str] = Field(
        default=["id", "class", "data-*"],
        description="HTML attributes to preserve as markdown attributes"
    )
    
    # Formatting options
    heading_style: str = Field(
        default="atx",  # # ## ### vs underline style
        description="Heading style: 'atx' (#) or 'underline'"
    )
    
    bullet_style: str = Field(
        default="-",
        description="Bullet list style: '-', '*', or '+'"
    )
    
    emphasis_style: str = Field(
        default="*",
        description="Emphasis style: '*' or '_'"
    )
    
    strong_style: str = Field(
        default="**",
        description="Strong emphasis style: '**' or '__'"
    )
    
    # Code formatting
    code_language_detection: bool = Field(
        default=True,
        description="Attempt to detect code block languages"
    )
    
    fence_code_blocks: bool = Field(
        default=True,
        description="Use fenced code blocks (```)"
    )
    
    # Table handling
    convert_tables: bool = Field(
        default=True,
        description="Convert HTML tables to Markdown tables"
    )
    
    # Image handling
    download_images: bool = Field(
        default=False,
        description="Download and localize images"
    )
    
    image_directory: Optional[Path] = Field(
        None,
        description="Directory for downloaded images"
    )
    
    # Quality control
    validate_markdown: bool = Field(
        default=True,
        description="Validate generated markdown"
    )
    
    max_line_length: Optional[int] = Field(
        default=None,
        ge=80,
        description="Maximum line length for wrapping"
    )


@dataclass
class ConversionResult:
    """Result of HTML to Markdown conversion."""
    
    # Core results
    markdown: str
    original_html: str
    
    # Metadata
    title: Optional[str] = None
    stats: ConversionStats = field(default_factory=ConversionStats)
    
    # Asset tracking
    images: List[Dict[str, str]] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    
    # Quality assessment
    conversion_quality: float = 1.0  # 0-1 score
    warnings: List[str] = field(default_factory=list)
    
    # Processing metadata
    converted_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_high_quality(self) -> bool:
        """Check if conversion is high quality."""
        return (
            self.conversion_quality >= 0.8 and
            len(self.warnings) < 5 and
            len(self.markdown.strip()) > 0
        )
    
    @property
    def compression_ratio(self) -> float:
        """Calculate compression ratio (markdown size / html size)."""
        if self.stats.input_size == 0:
            return 0.0
        return self.stats.output_size / self.stats.input_size


class Document360MarkdownConverter(BaseMarkdownConverter):
    """
    Custom MarkdownConverter optimized for Document360 content.
    
    Extends markdownify with Document360-specific formatting rules,
    enhanced table support, and better code block handling.
    """
    
    def __init__(self, **options):
        # Document360 specific options
        default_options = {
            'heading_style': 'atx',
            'bullets': '-',
            'emphasis_mark': '*',
            'strong_mark': '**',
            'strip': ['script', 'style'],
            'convert': ['b', 'strong', 'i', 'em', 'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'hr', 'br',
                       'table', 'thead', 'tbody', 'tr', 'th', 'td', 'img']
        }
        default_options.update(options)
        
        super().__init__(**default_options)
        self._code_block_counter = 0
    
    def convert_hn(self, n, el, text, convert_as_inline):
        """Enhanced heading conversion with ID preservation."""
        if convert_as_inline:
            return text
        
        # Preserve heading IDs if present
        heading_id = el.get('id')
        prefix = '#' * n + ' '
        
        if heading_id:
            return f"{prefix}{text} {{#{heading_id}}}\n\n"
        else:
            return f"{prefix}{text}\n\n"
    
    def convert_code(self, el, text, convert_as_inline):
        """Enhanced code conversion with language detection."""
        if not text.strip():
            return ""
        
        # Inline code
        if convert_as_inline or '\n' not in text:
            return f"`{text}`"
        
        # Block code - try to detect language
        language = ""
        classes = el.get('class', [])
        
        for cls in classes:
            if cls.startswith('language-'):
                language = cls[9:]  # Remove 'language-' prefix
                break
            elif cls in ['python', 'javascript', 'json', 'bash', 'sql', 'yaml', 'xml', 'html', 'css']:
                language = cls
                break
        
        return f"```{language}\n{text}\n```\n\n"
    
    def convert_pre(self, el, text, convert_as_inline):
        """Enhanced pre block conversion."""
        # Check if pre contains code
        code_el = el.find('code')
        if code_el:
            return self.convert_code(code_el, text, False)
        
        # Regular pre block
        return f"```\n{text}\n```\n\n"
    
    def convert_table(self, el, text, convert_as_inline):
        """Enhanced table conversion with proper markdown formatting."""
        if convert_as_inline:
            return text
        
        # Extract table structure
        rows = el.find_all('tr')
        if not rows:
            return text
        
        markdown_rows = []
        is_first_row = True
        
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if not cells:
                continue
            
            # Convert cells to text
            cell_texts = []
            for cell in cells:
                cell_text = self.process_tag(cell, children_only=True).strip()
                # Escape pipes in cell content
                cell_text = cell_text.replace('|', '\\|')
                cell_texts.append(cell_text)
            
            # Create markdown row
            markdown_row = '| ' + ' | '.join(cell_texts) + ' |'
            markdown_rows.append(markdown_row)
            
            # Add header separator after first row if it contains th elements
            if is_first_row and any(cell.name == 'th' for cell in cells):
                separator = '|' + ''.join([' --- |' for _ in cells])
                markdown_rows.append(separator)
            
            is_first_row = False
        
        return '\n'.join(markdown_rows) + '\n\n'
    
    def convert_img(self, el, text, convert_as_inline):
        """Enhanced image conversion with alt text and title support."""
        src = el.get('src', '')
        alt = el.get('alt', '')
        title = el.get('title', '')
        
        if not src:
            return ""
        
        # Build markdown image syntax
        if title:
            return f'![{alt}]({src} "{title}")'
        else:
            return f'![{alt}]({src})'
    
    def convert_a(self, el, text, convert_as_inline):
        """Enhanced link conversion with title support."""
        href = el.get('href', '')
        title = el.get('title', '')
        
        if not href:
            return text
        
        # Build markdown link syntax
        if title:
            return f'[{text}]({href} "{title}")'
        else:
            return f'[{text}]({href})'


class MarkdownConverter:
    """
    HTML to Markdown converter with Document360 optimizations.
    
    Provides comprehensive HTML-to-Markdown conversion with custom formatting
    rules, asset handling, and quality assessment specifically optimized for
    Document360 content structure and requirements.
    """
    
    def __init__(self, config: Optional[ConversionConfig] = None):
        """
        Initialize markdown converter.
        
        Args:
            config: Conversion configuration
        """
        self.config = config or ConversionConfig()
        logger.info("MarkdownConverter initialized", style=self.config.style.value)
    
    def convert(self, html: str, title: Optional[str] = None) -> ConversionResult:
        """
        Convert HTML to Markdown.
        
        Args:
            html: HTML content to convert
            title: Optional title for the content
            
        Returns:
            Conversion result with markdown and metadata
            
        Raises:
            Document360Error: If conversion fails
        """
        start_time = datetime.now()
        stats = ConversionStats(input_size=len(html))
        
        try:
            logger.info("Starting HTML to Markdown conversion", input_size=len(html))
            
            # Parse and clean HTML
            soup = BeautifulSoup(html, 'html.parser')
            cleaned_html = self._preprocess_html(soup, stats)
            
            # Configure converter based on style
            converter_options = self._get_converter_options()
            
            # Convert to markdown
            converter = Document360MarkdownConverter(**converter_options)
            raw_markdown = converter.convert(str(cleaned_html))
            
            # Post-process markdown
            processed_markdown = self._postprocess_markdown(raw_markdown, stats)
            
            # Extract assets
            images = self._extract_images(soup)
            links = self._extract_links(soup)
            
            # Assess quality
            quality_score = self._assess_conversion_quality(
                html, processed_markdown, stats
            )
            
            # Update stats
            stats.output_size = len(processed_markdown)
            stats.processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            result = ConversionResult(
                markdown=processed_markdown,
                original_html=html,
                title=title,
                stats=stats,
                images=images,
                links=links,
                conversion_quality=quality_score,
                warnings=stats.warnings
            )
            
            logger.info(
                f"Markdown conversion completed",
                input_size=stats.input_size,
                output_size=stats.output_size,
                quality=quality_score,
                processing_time_ms=stats.processing_time_ms
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to convert HTML to Markdown: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
    
    def _preprocess_html(self, soup: BeautifulSoup, stats: ConversionStats) -> BeautifulSoup:
        """Preprocess HTML before conversion."""
        # Remove unwanted elements
        for selector in self.config.strip_tags:
            for element in soup.select(selector):
                element.decompose()
                stats.elements_converted += 1
        
        # Clean up whitespace
        self._normalize_whitespace(soup)
        
        # Process code blocks
        self._enhance_code_blocks(soup, stats)
        
        # Process tables
        if self.config.convert_tables:
            stats.tables_converted = len(soup.find_all('table'))
        
        return soup
    
    def _normalize_whitespace(self, soup: BeautifulSoup) -> None:
        """Normalize whitespace in HTML."""
        # Remove excessive whitespace while preserving structure
        for text_node in soup.find_all(text=True):
            if text_node.parent.name not in ['pre', 'code']:
                normalized = re.sub(r'\s+', ' ', str(text_node))
                text_node.replace_with(normalized)
    
    def _enhance_code_blocks(self, soup: BeautifulSoup, stats: ConversionStats) -> None:
        """Enhance code block detection and formatting."""
        code_blocks = soup.find_all(['pre', 'code'])
        stats.code_blocks_found = len(code_blocks)
        
        for block in code_blocks:
            # Try to detect language from various sources
            language = self._detect_code_language(block)
            if language:
                # Ensure class attribute exists for language
                classes = block.get('class', [])
                if isinstance(classes, str):
                    classes = classes.split()
                
                if f'language-{language}' not in classes:
                    classes.append(f'language-{language}')
                    block['class'] = classes
    
    def _detect_code_language(self, element: Tag) -> Optional[str]:
        """Detect programming language from code block."""
        # Check existing classes
        classes = element.get('class', [])
        if isinstance(classes, str):
            classes = classes.split()
        
        for cls in classes:
            if cls.startswith('language-'):
                return cls[9:]  # Remove 'language-' prefix
            elif cls in ['python', 'javascript', 'json', 'bash', 'sql', 'yaml', 'xml', 'html', 'css']:
                return cls
        
        # Try to detect from content (very basic)
        content = element.get_text()
        if not content:
            return None
        
        # Simple pattern matching
        if 'def ' in content or 'import ' in content or 'from ' in content:
            return 'python'
        elif 'function' in content or 'const ' in content or 'let ' in content:
            return 'javascript'
        elif content.strip().startswith('{') and content.strip().endswith('}'):
            return 'json'
        elif '#!/bin/bash' in content or 'echo ' in content:
            return 'bash'
        
        return None
    
    def _postprocess_markdown(self, markdown: str, stats: ConversionStats) -> str:
        """Post-process generated markdown."""
        # Clean up excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)
        
        # Fix list formatting
        markdown = self._fix_list_formatting(markdown)
        
        # Fix table formatting if needed
        if self.config.convert_tables:
            markdown = self._fix_table_formatting(markdown)
        
        # Apply line length limits if configured
        if self.config.max_line_length:
            markdown = self._wrap_lines(markdown, self.config.max_line_length)
        
        # Validate markdown if configured
        if self.config.validate_markdown:
            validation_issues = self._validate_markdown(markdown)
            stats.warnings.extend(validation_issues)
        
        return markdown.strip()
    
    def _fix_list_formatting(self, markdown: str) -> str:
        """Fix common list formatting issues."""
        # Ensure proper spacing around lists
        lines = markdown.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if line.strip().startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\. ', line.strip()):
                # List item - ensure previous line is empty if it's not a list item
                if (i > 0 and 
                    fixed_lines and 
                    fixed_lines[-1].strip() and 
                    not fixed_lines[-1].strip().startswith(('- ', '* ', '+ ')) and 
                    not re.match(r'^\d+\. ', fixed_lines[-1].strip())):
                    fixed_lines.append('')
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_table_formatting(self, markdown: str) -> str:
        """Fix markdown table formatting issues."""
        # Ensure tables have proper spacing
        lines = markdown.split('\n')
        fixed_lines = []
        
        in_table = False
        for line in lines:
            is_table_line = line.strip().startswith('|') and line.strip().endswith('|')
            
            if is_table_line and not in_table:
                # Starting a table - ensure blank line before
                if fixed_lines and fixed_lines[-1].strip():
                    fixed_lines.append('')
                in_table = True
            elif not is_table_line and in_table:
                # Ending a table - ensure blank line after
                in_table = False
                fixed_lines.append(line)
                if line.strip():
                    fixed_lines.append('')
                continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _wrap_lines(self, markdown: str, max_length: int) -> str:
        """Wrap long lines to specified length."""
        lines = markdown.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= max_length:
                wrapped_lines.append(line)
            else:
                # Don't wrap code blocks or tables
                if line.strip().startswith('```') or line.strip().startswith('|'):
                    wrapped_lines.append(line)
                else:
                    # Simple word wrapping
                    words = line.split()
                    current_line = ""
                    
                    for word in words:
                        if len(current_line + word + ' ') <= max_length:
                            current_line += word + ' '
                        else:
                            if current_line:
                                wrapped_lines.append(current_line.strip())
                            current_line = word + ' '
                    
                    if current_line:
                        wrapped_lines.append(current_line.strip())
        
        return '\n'.join(wrapped_lines)
    
    def _validate_markdown(self, markdown: str) -> List[str]:
        """Validate generated markdown for common issues."""
        issues = []
        
        # Check for unmatched brackets/parentheses
        brackets = markdown.count('[') - markdown.count(']')
        if brackets != 0:
            issues.append(f"Unmatched square brackets: {brackets}")
        
        parens = markdown.count('(') - markdown.count(')')
        if parens != 0:
            issues.append(f"Unmatched parentheses: {parens}")
        
        # Check for malformed links
        malformed_links = re.findall(r'\]\([^)]*$', markdown)
        if malformed_links:
            issues.append(f"Found {len(malformed_links)} malformed links")
        
        # Check for empty headings
        empty_headings = re.findall(r'^#+\s*$', markdown, re.MULTILINE)
        if empty_headings:
            issues.append(f"Found {len(empty_headings)} empty headings")
        
        return issues
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract image information from HTML."""
        images = []
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                images.append({
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                })
        
        return images
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract link information from HTML."""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            if href and text:
                links.append({
                    'href': href,
                    'text': text,
                    'title': link.get('title', ''),
                    'type': 'internal' if not href.startswith(('http://', 'https://')) else 'external'
                })
        
        return links
    
    def _assess_conversion_quality(self, html: str, markdown: str, stats: ConversionStats) -> float:
        """Assess the quality of the conversion."""
        score = 0.0
        max_score = 10.0
        
        # Basic conversion success (2 points)
        if markdown and len(markdown.strip()) > 0:
            score += 2.0
        
        # Content preservation (3 points)
        html_text_length = len(BeautifulSoup(html, 'html.parser').get_text())
        markdown_text_length = len(re.sub(r'[#*`_\[\]()]', '', markdown))
        
        if html_text_length > 0:
            preservation_ratio = markdown_text_length / html_text_length
            if 0.8 <= preservation_ratio <= 1.2:
                score += 3.0
            elif 0.6 <= preservation_ratio <= 1.5:
                score += 2.0
            elif preservation_ratio > 0.3:
                score += 1.0
        
        # Structure preservation (3 points)
        html_headings = len(BeautifulSoup(html, 'html.parser').find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        markdown_headings = len(re.findall(r'^#+', markdown, re.MULTILINE))
        
        if html_headings > 0:
            if markdown_headings >= html_headings * 0.8:
                score += 2.0
            elif markdown_headings >= html_headings * 0.5:
                score += 1.0
        
        # Lists preservation
        html_lists = len(BeautifulSoup(html, 'html.parser').find_all(['ul', 'ol']))
        markdown_lists = len(re.findall(r'^\s*[-*+]|\d+\.', markdown, re.MULTILINE))
        
        if html_lists > 0 and markdown_lists >= html_lists * 0.5:
            score += 1.0
        
        # Quality deductions (2 points)
        warnings_penalty = min(len(stats.warnings) * 0.2, 2.0)
        score -= warnings_penalty
        
        return max(0.0, min(1.0, score / max_score))
    
    def _get_converter_options(self) -> Dict[str, Any]:
        """Get converter options based on configuration."""
        options = {}
        
        # Set heading style
        if self.config.heading_style == 'atx':
            options['heading_style'] = 'atx'
        
        # Set list bullet style
        options['bullets'] = self.config.bullet_style
        
        # Set emphasis styles
        options['emphasis_mark'] = self.config.emphasis_style
        options['strong_mark'] = self.config.strong_style
        
        # Configure elements to convert/strip
        options['strip'] = self.config.strip_tags
        
        return options