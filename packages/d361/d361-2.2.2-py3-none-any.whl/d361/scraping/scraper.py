# this_file: external/int_folders/d361/src/d361/scraping/scraper.py
"""
Document360 web scraper using Playwright.

This module provides robust web scraping capabilities with browser automation,
anti-detection measures, rate limiting, and respectful crawling practices
for Document360 documentation websites.
"""

from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, AsyncIterator
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger
from pydantic import BaseModel, Field, validator
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from ..api.errors import Document360Error, ErrorCategory, ErrorSeverity


class BrowserType(str, Enum):
    """Supported browser types."""
    CHROMIUM = "chromium"
    FIREFOX = "firefox" 
    WEBKIT = "webkit"


class ScrapingMode(str, Enum):
    """Scraping operation modes."""
    SINGLE_PAGE = "single"      # Scrape single page
    SITEMAP = "sitemap"         # Follow sitemap
    CRAWL = "crawl"             # Recursive crawling
    TARGETED = "targeted"       # Target specific URLs


@dataclass
class UserAgent:
    """User agent configuration."""
    name: str
    string: str
    platform: str


class ScrapingConfig(BaseModel):
    """Configuration for web scraping operations."""
    
    # Browser settings
    browser_type: BrowserType = Field(
        default=BrowserType.CHROMIUM,
        description="Browser type to use"
    )
    
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode"
    )
    
    viewport_width: int = Field(
        default=1920,
        ge=800,
        le=3840,
        description="Browser viewport width"
    )
    
    viewport_height: int = Field(
        default=1080,
        ge=600,
        le=2160,
        description="Browser viewport height"
    )
    
    # Request settings
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Page load timeout in seconds"
    )
    
    navigation_timeout: int = Field(
        default=30000,
        ge=5000,
        le=300000,
        description="Navigation timeout in milliseconds"
    )
    
    # Rate limiting
    delay_min_seconds: float = Field(
        default=1.0,
        ge=0.1,
        description="Minimum delay between requests"
    )
    
    delay_max_seconds: float = Field(
        default=3.0,
        ge=0.5,
        description="Maximum delay between requests"
    )
    
    concurrent_pages: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Number of concurrent pages"
    )
    
    # Anti-detection
    randomize_user_agent: bool = Field(
        default=True,
        description="Randomize user agents"
    )
    
    randomize_viewport: bool = Field(
        default=True,
        description="Randomize viewport size"
    )
    
    dismiss_cookie_banners: bool = Field(
        default=True,
        description="Attempt to dismiss cookie banners"
    )
    
    block_ads: bool = Field(
        default=True,
        description="Block ads and tracking"
    )
    
    # Content filtering  
    allowed_domains: Set[str] = Field(
        default_factory=set,
        description="Allowed domains for crawling"
    )
    
    blocked_extensions: Set[str] = Field(
        default_factory=lambda: {".pdf", ".zip", ".exe", ".dmg"},
        description="File extensions to block"
    )
    
    max_pages: int = Field(
        default=1000,
        ge=1,
        description="Maximum pages to scrape"
    )
    
    # Respect settings
    respect_robots_txt: bool = Field(
        default=True,
        description="Respect robots.txt"
    )
    
    max_requests_per_domain: int = Field(
        default=100,
        ge=1,
        description="Max requests per domain"
    )
    
    # Storage
    save_screenshots: bool = Field(
        default=False,
        description="Save page screenshots"
    )
    
    screenshot_dir: Optional[Path] = Field(
        None,
        description="Directory for screenshots"
    )


@dataclass
class ScrapedPage:
    """Results from scraping a single page."""
    url: str
    title: str
    html: str
    text_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    scraped_at: datetime = field(default_factory=datetime.now)
    load_time_ms: float = 0
    status_code: int = 200
    error: Optional[str] = None
    screenshot_path: Optional[Path] = None


class ScrapingSession(BaseModel):
    """Scraping session with statistics."""
    
    session_id: str = Field(..., description="Unique session identifier")
    start_time: datetime = Field(default_factory=datetime.now, description="Session start time")
    end_time: Optional[datetime] = Field(None, description="Session end time")
    
    # Statistics
    pages_scraped: int = Field(default=0, description="Pages successfully scraped")
    pages_failed: int = Field(default=0, description="Pages that failed to scrape")
    total_requests: int = Field(default=0, description="Total HTTP requests made")
    
    # URLs
    start_urls: List[str] = Field(default_factory=list, description="Starting URLs")
    scraped_urls: Set[str] = Field(default_factory=set, description="Successfully scraped URLs")
    failed_urls: Set[str] = Field(default_factory=set, description="Failed URLs")
    pending_urls: Set[str] = Field(default_factory=set, description="URLs pending scraping")
    
    @property
    def success_rate(self) -> float:
        """Calculate scraping success rate."""
        total = self.pages_scraped + self.pages_failed
        return self.pages_scraped / total if total > 0 else 0.0
    
    @property
    def duration_seconds(self) -> float:
        """Calculate session duration."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()


class Document360Scraper:
    """
    Document360 web scraper with Playwright browser automation.
    
    Provides comprehensive web scraping capabilities with anti-detection
    measures, rate limiting, respectful crawling practices, and robust
    error handling for Document360 documentation websites.
    """
    
    # Common user agents for rotation
    USER_AGENTS = [
        UserAgent("Chrome_Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Win32"),
        UserAgent("Chrome_Mac", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "MacIntel"),
        UserAgent("Firefox_Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0", "Win32"),
        UserAgent("Firefox_Mac", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0", "MacIntel"),
        UserAgent("Safari_Mac", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15", "MacIntel"),
    ]
    
    # Cookie banner selectors to dismiss
    COOKIE_SELECTORS = [
        '[id*="cookie"] button',
        '[class*="cookie"] button',
        '[id*="consent"] button',
        '[class*="consent"] button',
        'button[aria-label*="Accept"]',
        'button[aria-label*="Agree"]',
        'button:has-text("Accept")',
        'button:has-text("Agree")',
        'button:has-text("OK")',
        '.gdpr-consent button',
        '#cookieConsent button',
    ]
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        """
        Initialize Document360 scraper.
        
        Args:
            config: Scraping configuration
        """
        self.config = config or ScrapingConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.session: Optional[ScrapingSession] = None
        
        # Rate limiting
        self._last_request_time = 0.0
        self._request_count = 0
        self._domain_requests: Dict[str, int] = {}
        
        logger.info(
            f"Document360Scraper initialized",
            browser_type=self.config.browser_type,
            headless=self.config.headless,
            concurrent_pages=self.config.concurrent_pages
        )
    
    async def start(self) -> None:
        """Start the scraper and initialize browser."""
        if self.browser:
            return
        
        logger.info("Starting Document360Scraper")
        
        try:
            playwright = await async_playwright().start()
            
            # Launch browser based on type
            if self.config.browser_type == BrowserType.CHROMIUM:
                self.browser = await playwright.chromium.launch(
                    headless=self.config.headless,
                    args=['--no-sandbox', '--disable-dev-shm-usage'] if self.config.headless else None
                )
            elif self.config.browser_type == BrowserType.FIREFOX:
                self.browser = await playwright.firefox.launch(headless=self.config.headless)
            elif self.config.browser_type == BrowserType.WEBKIT:
                self.browser = await playwright.webkit.launch(headless=self.config.headless)
            
            # Create browser context with settings
            context_options = {
                'viewport': {
                    'width': self.config.viewport_width,
                    'height': self.config.viewport_height
                },
                'user_agent': self._get_random_user_agent().string,
            }
            
            self.context = await self.browser.new_context(**context_options)
            
            # Configure context for anti-detection
            if self.config.block_ads:
                await self._setup_ad_blocking()
            
            logger.info("Document360Scraper started successfully")
            
        except Exception as e:
            error_msg = f"Failed to start scraper: {e}"
            logger.error(error_msg)
            raise Document360Error(
                error_msg,
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.HIGH
            )
    
    async def stop(self) -> None:
        """Stop the scraper and cleanup resources."""
        logger.info("Stopping Document360Scraper")
        
        if self.context:
            await self.context.close()
            self.context = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.session and not self.session.end_time:
            self.session.end_time = datetime.now()
        
        logger.info("Document360Scraper stopped")
    
    async def scrape_url(self, url: str) -> ScrapedPage:
        """
        Scrape a single URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Scraped page data
            
        Raises:
            Document360Error: If scraping fails
        """
        if not self.browser or not self.context:
            await self.start()
        
        logger.info(f"Scraping URL: {url}")
        
        # Rate limiting
        await self._respect_rate_limits(url)
        
        page = None
        try:
            # Create new page
            page = await self.context.new_page()
            
            # Configure page
            await self._configure_page(page)
            
            # Navigate to URL
            start_time = time.time()
            response = await page.goto(
                url,
                timeout=self.config.navigation_timeout,
                wait_until='domcontentloaded'
            )
            
            load_time_ms = (time.time() - start_time) * 1000
            
            if not response:
                raise Document360Error(
                    f"Failed to navigate to URL: {url}",
                    category=ErrorCategory.NETWORK,
                    severity=ErrorSeverity.MEDIUM
                )
            
            # Handle cookie banners
            if self.config.dismiss_cookie_banners:
                await self._dismiss_cookie_banners(page)
            
            # Wait for content to load
            await page.wait_for_load_state('domcontentloaded')
            
            # Extract content
            scraped_page = await self._extract_page_content(page, url, load_time_ms, response.status)
            
            # Save screenshot if configured
            if self.config.save_screenshots and self.config.screenshot_dir:
                screenshot_path = await self._save_screenshot(page, url)
                scraped_page.screenshot_path = screenshot_path
            
            # Update session statistics
            if self.session:
                self.session.pages_scraped += 1
                self.session.scraped_urls.add(url)
                self.session.total_requests += 1
            
            logger.info(f"Successfully scraped URL: {url} ({load_time_ms:.1f}ms)")
            return scraped_page
            
        except Exception as e:
            error_msg = f"Failed to scrape URL {url}: {e}"
            logger.error(error_msg)
            
            # Update session statistics
            if self.session:
                self.session.pages_failed += 1
                self.session.failed_urls.add(url)
            
            # Create failed page result
            return ScrapedPage(
                url=url,
                title="",
                html="",
                text_content="",
                status_code=getattr(e, 'status_code', 0),
                error=str(e)
            )
            
        finally:
            if page:
                await page.close()
    
    async def scrape_multiple(self, urls: List[str]) -> List[ScrapedPage]:
        """
        Scrape multiple URLs with concurrency control.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of scraped pages
        """
        logger.info(f"Scraping {len(urls)} URLs")
        
        # Initialize session
        self.session = ScrapingSession(
            session_id=f"session_{int(time.time())}",
            start_urls=urls,
            pending_urls=set(urls)
        )
        
        results = []
        semaphore = asyncio.Semaphore(self.config.concurrent_pages)
        
        async def scrape_with_semaphore(url: str) -> ScrapedPage:
            async with semaphore:
                return await self.scrape_url(url)
        
        # Create tasks for all URLs
        tasks = [scrape_with_semaphore(url) for url in urls[:self.config.max_pages]]
        
        # Execute with progress tracking
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            
            # Update pending URLs
            if self.session:
                self.session.pending_urls.discard(result.url)
        
        # Finalize session
        if self.session:
            self.session.end_time = datetime.now()
        
        logger.info(
            f"Scraping completed",
            total_urls=len(urls),
            successful=len([r for r in results if not r.error]),
            failed=len([r for r in results if r.error])
        )
        
        return results
    
    async def _respect_rate_limits(self, url: str) -> None:
        """Implement rate limiting."""
        domain = urlparse(url).netloc
        
        # Check domain request limits
        if domain in self._domain_requests:
            if self._domain_requests[domain] >= self.config.max_requests_per_domain:
                raise Document360Error(
                    f"Exceeded request limit for domain: {domain}",
                    category=ErrorCategory.CLIENT_ERROR,
                    severity=ErrorSeverity.MEDIUM
                )
        
        # Calculate delay
        if self._last_request_time > 0:
            elapsed = time.time() - self._last_request_time
            min_delay = self.config.delay_min_seconds
            
            if elapsed < min_delay:
                delay = random.uniform(min_delay, self.config.delay_max_seconds)
                logger.debug(f"Rate limiting: waiting {delay:.2f}s")
                await asyncio.sleep(delay)
        
        # Update counters
        self._last_request_time = time.time()
        self._request_count += 1
        self._domain_requests[domain] = self._domain_requests.get(domain, 0) + 1
    
    def _get_random_user_agent(self) -> UserAgent:
        """Get a random user agent for anti-detection."""
        return random.choice(self.USER_AGENTS)
    
    async def _configure_page(self, page: Page) -> None:
        """Configure page for scraping."""
        # Set random viewport if configured
        if self.config.randomize_viewport:
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            await page.set_viewport_size({'width': width, 'height': height})
        
        # Set timeout
        page.set_default_timeout(self.config.timeout_seconds * 1000)
        page.set_default_navigation_timeout(self.config.navigation_timeout)
    
    async def _setup_ad_blocking(self) -> None:
        """Setup ad blocking and tracking protection."""
        if not self.context:
            return
        
        # Block tracking and ads
        await self.context.route("**/*", self._block_requests)
    
    async def _block_requests(self, route, request) -> None:
        """Block ads and tracking requests."""
        url = request.url
        
        # Block common ad/tracking domains
        blocked_domains = [
            'doubleclick.net', 'google-analytics.com', 'googletagmanager.com',
            'facebook.com', 'facebook.net', 'googlesyndication.com',
            'amazon-adsystem.com', 'adsystem.amazon.com'
        ]
        
        if any(domain in url for domain in blocked_domains):
            await route.abort()
        elif request.resource_type in ['image', 'font', 'stylesheet'] and 'ad' in url:
            await route.abort()
        else:
            await route.continue_()
    
    async def _dismiss_cookie_banners(self, page: Page) -> None:
        """Attempt to dismiss cookie consent banners."""
        try:
            # Try each selector with a timeout
            for selector in self.COOKIE_SELECTORS:
                try:
                    element = await page.wait_for_selector(selector, timeout=2000)
                    if element:
                        await element.click()
                        logger.debug(f"Dismissed cookie banner with selector: {selector}")
                        await asyncio.sleep(1)  # Wait for banner to disappear
                        break
                except:
                    continue
        except Exception as e:
            logger.debug(f"Could not dismiss cookie banners: {e}")
    
    async def _extract_page_content(
        self, 
        page: Page, 
        url: str, 
        load_time_ms: float,
        status_code: int
    ) -> ScrapedPage:
        """Extract content from a page."""
        try:
            # Get basic content
            title = await page.title()
            html = await page.content()
            text_content = await page.locator('body').text_content() or ""
            
            # Extract links
            link_elements = await page.locator('a[href]').all()
            links = []
            for link in link_elements:
                href = await link.get_attribute('href')
                if href:
                    absolute_url = urljoin(url, href)
                    links.append(absolute_url)
            
            # Extract images
            img_elements = await page.locator('img[src]').all()
            images = []
            for img in img_elements:
                src = await img.get_attribute('src')
                if src:
                    absolute_url = urljoin(url, src)
                    images.append(absolute_url)
            
            # Extract metadata
            metadata = {}
            try:
                # Get meta tags
                meta_elements = await page.locator('meta').all()
                for meta in meta_elements:
                    name = await meta.get_attribute('name')
                    content = await meta.get_attribute('content')
                    if name and content:
                        metadata[name] = content
            except Exception as e:
                logger.debug(f"Failed to extract metadata: {e}")
            
            return ScrapedPage(
                url=url,
                title=title,
                html=html,
                text_content=text_content,
                metadata=metadata,
                links=links,
                images=images,
                load_time_ms=load_time_ms,
                status_code=status_code
            )
            
        except Exception as e:
            logger.error(f"Failed to extract content from {url}: {e}")
            return ScrapedPage(
                url=url,
                title="",
                html="",
                text_content="",
                load_time_ms=load_time_ms,
                status_code=status_code,
                error=str(e)
            )
    
    async def _save_screenshot(self, page: Page, url: str) -> Path:
        """Save page screenshot."""
        if not self.config.screenshot_dir:
            raise ValueError("Screenshot directory not configured")
        
        # Create filename from URL
        domain = urlparse(url).netloc
        timestamp = int(time.time())
        filename = f"{domain}_{timestamp}.png"
        
        screenshot_path = self.config.screenshot_dir / filename
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        await page.screenshot(path=str(screenshot_path), full_page=True)
        
        return screenshot_path
    
    async def get_session_stats(self) -> Optional[ScrapingSession]:
        """Get current session statistics."""
        return self.session
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()