# this_file: external/int_folders/d361/src/d361/scraping/extractor.py
"""
Content extraction and processing for scraped HTML content.

This module provides robust HTML content extraction, cleaning, and structuring
capabilities for Document360 websites with intelligent content detection,
metadata extraction, and integration with d361 architecture patterns.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urljoin, urlparse

from loguru import logger
from pydantic import BaseModel, Field, validator
from bs4 import BeautifulSoup, Tag, NavigableString
from bs4.formatter import HTMLFormatter

from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class ContentType(str, Enum):
    """Types of content that can be extracted."""
    ARTICLE = "article"
    CATEGORY = "category"
    FAQ = "faq"
    GUIDE = "guide"
    TUTORIAL = "tutorial"
    REFERENCE = "reference"
    UNKNOWN = "unknown"


class ExtractionQuality(str, Enum):
    """Quality levels for content extraction."""
    EXCELLENT = "excellent"  # >90% content confidence
    GOOD = "good"           # 70-90% content confidence
    FAIR = "fair"           # 50-70% content confidence
    POOR = "poor"           # <50% content confidence


@dataclass
class ContentBlock:
    """Individual content block with metadata."""
    block_type: str
    content: str
    html: str
    position: int = 0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_significant(self) -> bool:
        """Check if content block is significant (not just whitespace)."""
        return len(self.content.strip()) > 10 and self.confidence > 0.3


class ExtractionConfig(BaseModel):
    """Configuration for content extraction operations."""
    
    # Content selection
    article_selectors: List[str] = Field(
        default=[
            "article", ".article", "#article-content", 
            ".content", "#content", ".post-content",
            ".doc-content", ".documentation", ".guide-content"
        ],
        description="CSS selectors for main article content"
    )
    
    title_selectors: List[str] = Field(
        default=["h1", ".title", ".article-title", "#title"],
        description="CSS selectors for article titles"
    )
    
    metadata_selectors: Dict[str, List[str]] = Field(
        default={
            "author": [".author", ".by-author", "[data-author]"],
            "date": [".date", ".published", "[datetime]", "time"],
            "tags": [".tags", ".categories", ".labels"],
            "breadcrumb": [".breadcrumb", ".navigation", ".path"]
        },
        description="CSS selectors for metadata extraction"
    )
    
    # Content filtering
    remove_selectors: List[str] = Field(
        default=[
            "script", "style", "nav", "header", "footer",
            ".sidebar", ".navigation", ".ads", ".advertisement",
            ".comments", ".social-share", ".related-articles",
            ".cookie-banner", ".gdpr-notice"
        ],
        description="Elements to remove during extraction"
    )
    
    # Text processing
    min_content_length: int = Field(
        default=50,
        ge=10,
        description="Minimum content length to consider valid"
    )
    
    max_title_length: int = Field(
        default=200,
        ge=50,
        description="Maximum title length"
    )
    
    normalize_whitespace: bool = Field(
        default=True,
        description="Normalize whitespace in extracted text"
    )
    
    extract_links: bool = Field(
        default=True,
        description="Extract and process internal/external links"
    )
    
    extract_images: bool = Field(
        default=True,
        description="Extract image metadata and URLs"
    )
    
    # Language detection
    detect_language: bool = Field(
        default=True,
        description="Attempt to detect content language"
    )
    
    # Quality thresholds
    min_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum extraction confidence threshold"
    )


@dataclass
class ExtractedContent:
    """Complete extracted content with metadata and quality assessment."""
    
    # Core content
    title: str
    content: str
    html: str
    url: str
    
    # Content analysis
    content_type: ContentType = ContentType.UNKNOWN
    quality: ExtractionQuality = ExtractionQuality.FAIR
    confidence: float = 0.5
    word_count: int = 0
    
    # Metadata
    author: Optional[str] = None
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Structure
    headings: List[Dict[str, str]] = field(default_factory=list)
    blocks: List[ContentBlock] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    
    # Technical metadata
    language: Optional[str] = None
    extraction_time: datetime = field(default_factory=datetime.now)
    extracted_at: datetime = field(default_factory=datetime.now)
    processing_time_ms: float = 0
    
    @property
    def is_high_quality(self) -> bool:
        """Check if extraction is high quality."""
        return (
            self.quality in [ExtractionQuality.EXCELLENT, ExtractionQuality.GOOD] and
            self.confidence >= 0.7 and
            self.word_count >= 100
        )
    
    @property
    def summary(self) -> str:
        """Generate a summary of the extracted content."""
        words = self.content.split()[:50]
        return " ".join(words) + ("..." if len(words) == 50 else "")


class ContentExtractor:
    """
    Content extraction and processing for HTML content.
    
    Provides intelligent HTML parsing with content detection, cleaning,
    and structuring capabilities optimized for Document360 content
    with robust error handling and quality assessment.
    """
    
    # Document360 specific selectors
    D360_SELECTORS = {
        "article": [
            ".article-content", ".documentation-content",
            ".guide-body", ".help-content", "#article-body"
        ],
        "title": [
            ".article-title", ".doc-title", ".guide-title",
            "h1.title", ".page-title"
        ],
        "metadata": {
            "breadcrumb": [".breadcrumb", ".doc-path", ".navigation-path"],
            "category": [".category", ".doc-category", ".guide-category"],
            "last_updated": [".last-updated", ".modified-date", "[data-modified]"]
        }
    }
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """
        Initialize content extractor.
        
        Args:
            config: Extraction configuration
        """
        self.config = config or ExtractionConfig()
        logger.info("ContentExtractor initialized", config=self.config.dict())
    
    def extract(self, html: str, url: str) -> ExtractedContent:
        """
        Extract structured content from HTML.
        
        Args:
            html: Raw HTML content
            url: Source URL for context
            
        Returns:
            Structured extracted content
            
        Raises:
            Document360Error: If extraction fails
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Extracting content from URL: {url}")
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            self._clean_html(soup)
            
            # Extract core content
            title = self._extract_title(soup)
            article_content = self._extract_article_content(soup)
            content_text = self._extract_text(article_content) if article_content else ""
            
            # Analyze content
            content_type = self._detect_content_type(title, content_text, soup)
            quality, confidence = self._assess_quality(title, content_text, soup)
            word_count = len(content_text.split())
            
            # Extract metadata
            metadata = self._extract_metadata(soup, url)
            
            # Extract structural elements
            headings = self._extract_headings(article_content or soup)
            blocks = self._extract_content_blocks(article_content or soup)
            
            # Extract links and images if configured
            links = self._extract_links(soup, url) if self.config.extract_links else []
            images = self._extract_images(soup, url) if self.config.extract_images else []
            
            # Detect language if configured
            language = self._detect_language(content_text) if self.config.detect_language else None
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = ExtractedContent(
                title=title,
                content=content_text,
                html=str(article_content) if article_content else str(soup),
                url=url,
                content_type=content_type,
                quality=quality,
                confidence=confidence,
                word_count=word_count,
                headings=headings,
                blocks=blocks,
                links=links,
                images=images,
                language=language,
                processing_time_ms=processing_time,
                **metadata
            )
            
            logger.info(
                f"Content extraction completed",
                url=url,
                quality=quality.value,
                confidence=confidence,
                word_count=word_count,
                processing_time_ms=processing_time
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to extract content from {url}: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM
            )
    
    def _clean_html(self, soup: BeautifulSoup) -> None:
        """Remove unwanted elements from HTML."""
        for selector in self.config.remove_selectors:
            for element in soup.select(selector):
                element.decompose()
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try Document360 specific selectors first
        for selector in self.D360_SELECTORS["title"]:
            elements = soup.select(selector)
            if elements:
                title = elements[0].get_text(strip=True)
                if title and len(title) <= self.config.max_title_length:
                    return title
        
        # Try general selectors
        for selector in self.config.title_selectors:
            elements = soup.select(selector)
            if elements:
                title = elements[0].get_text(strip=True)
                if title and len(title) <= self.config.max_title_length:
                    return title
        
        # Fallback to HTML title tag
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            if len(title) <= self.config.max_title_length:
                return title
        
        return "Untitled"
    
    def _extract_article_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Extract main article content container."""
        # Try Document360 specific selectors first
        for selector in self.D360_SELECTORS["article"]:
            elements = soup.select(selector)
            if elements:
                return elements[0]
        
        # Try general selectors
        for selector in self.config.article_selectors:
            elements = soup.select(selector)
            if elements:
                return elements[0]
        
        return None
    
    def _extract_text(self, element: Tag) -> str:
        """Extract clean text from HTML element."""
        if not element:
            return ""
        
        text = element.get_text(separator=' ', strip=True)
        
        if self.config.normalize_whitespace:
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
        
        return text
    
    def _detect_content_type(self, title: str, content: str, soup: BeautifulSoup) -> ContentType:
        """Detect the type of content based on various signals."""
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Check for FAQ patterns
        if any(keyword in title_lower for keyword in ["faq", "frequently asked", "questions"]):
            return ContentType.FAQ
        
        # Check for tutorial patterns
        if any(keyword in title_lower for keyword in ["tutorial", "how to", "step by step", "guide"]):
            return ContentType.TUTORIAL
        
        # Check for guide patterns
        if any(keyword in title_lower for keyword in ["guide", "getting started", "quickstart"]):
            return ContentType.GUIDE
        
        # Check for reference patterns
        if any(keyword in title_lower for keyword in ["reference", "api", "documentation", "spec"]):
            return ContentType.REFERENCE
        
        # Check content for numbered lists (tutorials)
        numbered_lists = soup.find_all(['ol', 'li'])
        if len(numbered_lists) > 3:
            return ContentType.TUTORIAL
        
        # Default to article
        return ContentType.ARTICLE
    
    def _assess_quality(self, title: str, content: str, soup: BeautifulSoup) -> tuple[ExtractionQuality, float]:
        """Assess extraction quality and confidence."""
        score = 0.0
        max_score = 10.0
        
        # Title quality (2 points)
        if title and title != "Untitled":
            score += 2.0
        elif title:
            score += 1.0
        
        # Content length (3 points)
        word_count = len(content.split())
        if word_count >= 500:
            score += 3.0
        elif word_count >= 200:
            score += 2.0
        elif word_count >= self.config.min_content_length:
            score += 1.0
        
        # Structure quality (3 points)
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) >= 3:
            score += 2.0
        elif len(headings) >= 1:
            score += 1.0
        
        paragraphs = soup.find_all('p')
        if len(paragraphs) >= 3:
            score += 1.0
        
        # Content richness (2 points)
        links = soup.find_all('a')
        images = soup.find_all('img')
        if len(links) > 5 or len(images) > 2:
            score += 1.0
        if len(links) > 0 or len(images) > 0:
            score += 1.0
        
        confidence = score / max_score
        
        # Determine quality level
        if confidence >= 0.9:
            quality = ExtractionQuality.EXCELLENT
        elif confidence >= 0.7:
            quality = ExtractionQuality.GOOD
        elif confidence >= 0.5:
            quality = ExtractionQuality.FAIR
        else:
            quality = ExtractionQuality.POOR
        
        return quality, confidence
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML."""
        metadata = {}
        
        # Extract author
        for selector in self.config.metadata_selectors.get("author", []):
            elements = soup.select(selector)
            if elements:
                metadata["author"] = elements[0].get_text(strip=True)
                break
        
        # Extract dates
        for selector in self.config.metadata_selectors.get("date", []):
            elements = soup.select(selector)
            if elements:
                date_text = elements[0].get_text(strip=True)
                # Try to parse date (simplified)
                try:
                    # This is a simplified date parsing - could be enhanced
                    if "datetime" in elements[0].attrs:
                        date_text = elements[0]["datetime"]
                    metadata["published_date"] = self._parse_date(date_text)
                except:
                    pass
                break
        
        # Extract tags/categories
        tags = []
        for selector in self.config.metadata_selectors.get("tags", []):
            elements = soup.select(selector)
            for element in elements:
                tag_text = element.get_text(strip=True)
                if tag_text:
                    tags.extend([t.strip() for t in tag_text.split(',')])
        
        if tags:
            metadata["tags"] = list(set(tags))
        
        return metadata
    
    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        # Simplified date parsing - could use dateutil.parser for robustness
        common_formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%B %d, %Y",
            "%b %d, %Y"
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def _extract_headings(self, element: Tag) -> List[Dict[str, str]]:
        """Extract headings structure."""
        headings = []
        
        for i, heading in enumerate(element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            headings.append({
                "level": int(heading.name[1]),
                "text": heading.get_text(strip=True),
                "id": heading.get("id", f"heading-{i}"),
                "position": i
            })
        
        return headings
    
    def _extract_content_blocks(self, element: Tag) -> List[ContentBlock]:
        """Extract structured content blocks."""
        blocks = []
        
        for i, child in enumerate(element.children):
            if isinstance(child, Tag):
                content_text = child.get_text(strip=True)
                if content_text and len(content_text) > 10:
                    block = ContentBlock(
                        block_type=child.name,
                        content=content_text,
                        html=str(child),
                        position=i,
                        confidence=0.8 if child.name in ['p', 'div', 'section'] else 0.6
                    )
                    
                    if block.is_significant:
                        blocks.append(block)
        
        return blocks
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract and categorize links."""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            if href and text:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                link_domain = urlparse(absolute_url).netloc
                
                links.append({
                    "url": absolute_url,
                    "text": text,
                    "type": "internal" if link_domain == base_domain else "external",
                    "title": link.get("title", "")
                })
        
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract image metadata."""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, src)
            
            images.append({
                "url": absolute_url,
                "alt": img.get("alt", ""),
                "title": img.get("title", ""),
                "width": img.get("width", ""),
                "height": img.get("height", "")
            })
        
        return images
    
    def _detect_language(self, content: str) -> Optional[str]:
        """Basic language detection."""
        # Simplified language detection - could use proper library like langdetect
        if not content:
            return None
        
        # Check for common English patterns
        english_words = {'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'you', 'that'}
        words = content.lower().split()[:100]  # Check first 100 words
        
        english_count = sum(1 for word in words if word in english_words)
        
        if len(words) > 0 and english_count / len(words) > 0.1:
            return "en"
        
        return None