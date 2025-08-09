#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["beautifulsoup4", "fire", "rich", "lxml", "html2text", "pathlib", "loguru", "playwright", "tqdm", "asyncio"]
# ///
# this_file: d361api/_private/d360-docs/docs.document360.com/d360xtr.py

import asyncio
from pathlib import Path
from typing import Any, cast

import fire
import html2text
import tqdm
import tqdm.asyncio  # Import tqdm.asyncio explicitly
from bs4 import BeautifulSoup, Tag
from loguru import logger
from rich.console import Console

console = Console()

# Get the current script directory
SCRIPT_DIR = Path(__file__).parent.absolute()
DEFAULT_CSS_PATH = SCRIPT_DIR / "d360xtr.css"

# Constants for Playwright settings
PLAYWRIGHT_TIMEOUT = 90000  # 90 seconds
PLAYWRIGHT_RETRY_COUNT = 3
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


def load_css(css_path: str | None = None) -> str:
    """
    Load CSS from a file.

    Args:
        css_path: Path to a CSS file. If None, the default CSS file will be used.

    Returns:
        The CSS content as a string
    """
    # If no custom CSS is specified, use the default one
    if css_path is None:
        css_file = DEFAULT_CSS_PATH
    else:
        css_file = Path(css_path)

    # Check if the CSS file exists
    if not css_file.exists():
        logger.warning(f"CSS file {css_file} not found, using minimal default styles")
        return """
        body { font-family: sans-serif; }
        aside { float: left; width: 280px; }
        main { margin-left: 300px; }
        """

    # Read the CSS file
    try:
        with open(css_file, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading CSS file {css_file}: {e}")
        return """
        body { font-family: sans-serif; }
        aside { float: left; width: 280px; }
        main { margin-left: 300px; }
        """


class Document360Extractor:
    """
    A tool that transforms the content of downloaded Document360 documentation
    into one long HTML file and one long Markdown file.
    """

    def __init__(
        self,
        nav_file: str | None = None,
        docs_dir: str = "docs",
        output_html: str = "document360_docs.html",
        output_md: str = "document360_docs.md",
        site_url: str | None = None,
        css_file: str | None = None,
        *,
        pages: int | None = None,
        verbose: bool = False,
        email: str | None = None,
        password: str | None = None,
    ) -> None:
        """
        Initialize the Document360 extractor.

        Args:
            nav_file: Path to the navigation XHTML file relative to the current directory
            docs_dir: Directory containing the documentation HTML files
            output_html: Output HTML filename
            output_md: Output Markdown filename
            site_url: URL of the live Document360 site to scrape
            css_file: Path to a custom CSS file for styling the HTML output
            pages: Maximum number of pages to process (None for all)
            verbose: Enable verbose logging
            email: Email for Document360 login (if authentication is required)
            password: Password for Document360 login (if authentication is required)
        """
        self.nav_file = Path(nav_file) if nav_file else None
        self.docs_dir = Path(docs_dir)
        self.output_html = output_html
        self.output_md = output_md
        self.site_url = site_url
        self.css_file = css_file
        self.pages = pages
        self.verbose = verbose
        self.email = email
        self.password = password
        # Use Playwright for content if site_url is provided
        self.use_playwright_for_content = site_url is not None
        # Always prioritize local nav file for TOC if provided
        self.use_local_toc = self.nav_file is not None
        # Store browser context for reuse
        self.browser_context = None

        # Load the CSS
        self.css = load_css(css_file)

        # Set up logger
        logger.remove()
        if verbose:
            logger.add(lambda msg: console.print(f"[blue]LOG:[/] {msg}"), level="DEBUG")
        else:
            logger.add(lambda msg: console.print(f"[blue]LOG:[/] {msg}"), level="INFO")

        # Check if required files and directories exist when using local TOC
        if self.use_local_toc:
            if self.nav_file is not None and not self.nav_file.exists():
                logger.error(f"Navigation file {nav_file} not found")
                msg = f"Navigation file {nav_file} not found"
                raise FileNotFoundError(msg)

            if not self.docs_dir.exists():
                logger.error(f"Documentation directory {docs_dir} not found")
                msg = f"Documentation directory {docs_dir} not found"
                raise FileNotFoundError(msg)
        elif not self.use_playwright_for_content:
            # If neither local TOC nor Playwright is used, we have no source
            logger.error("Either navigation file or site URL must be provided")
            msg = "Either navigation file or site URL must be provided"
            raise ValueError(msg)

        self.toc_links: list[dict[str, str]] = []  # Will store links from the TOC
        self.articles: dict[str, dict[str, Any]] = {}  # Will store the parsed articles

    def parse_toc(self) -> list[dict[str, str]]:
        """
        Parse the table of contents from the nav.xhtml file or the live site.
        If a local navigation file is provided, it will be prioritized over the site URL.

        Returns:
            List of dictionaries with link and title information
        """
        if self.use_local_toc:
            logger.info("Prioritizing local navigation file for TOC")
            return self._parse_toc_from_file()
        elif self.use_playwright_for_content:
            return self._parse_toc_from_site()
        else:
            # This should never happen due to the checks in __init__
            msg = "No source for table of contents"
            raise ValueError(msg)

    def _parse_toc_from_file(self) -> list[dict[str, str]]:
        """Parse the TOC from a local nav.xhtml file."""
        if not self.nav_file:
            logger.error("Navigation file not provided")
            msg = "Navigation file not provided"
            raise ValueError(msg)

        logger.info(f"Parsing TOC from local file {self.nav_file}")
        with open(self.nav_file, encoding="utf-8") as f:
            toc_content = f.read()

        # Parse the XHTML content
        soup = BeautifulSoup(toc_content, "lxml")

        # Find all links in the TOC
        links = []
        for li in soup.find_all("li"):
            a_tag = li.find("a")
            if a_tag and a_tag.get("href"):
                href = a_tag.get("href")
                # Extract the part after /docs/
                if "/docs/" in href:
                    filename = href.split("/docs/")[-1]
                    title = a_tag.text.strip()

                    # If using site for content, don't check for local files
                    if self.use_playwright_for_content:
                        # Construct URL for site content
                        site_url = cast(str, self.site_url)
                        url = f"{site_url.rstrip('/')}/{filename}"
                        links.append(
                            {
                                "href": href,
                                "filename": filename,
                                "title": title,
                                "url": url,
                            }
                        )
                    else:
                        # For local only mode, map the link to the local file path
                        file_path = self.docs_dir / f"{filename}.html"
                        if file_path.exists():
                            links.append(
                                {
                                    "href": href,
                                    "filename": filename,
                                    "title": title,
                                    "file_path": str(file_path),
                                }
                            )
                        else:
                            logger.warning(f"File {file_path} not found, skipping")

        logger.info(f"Found {len(links)} links in TOC")
        self.toc_links = links
        return links

    async def _setup_browser(self):
        """Set up a browser with authentication if needed."""
        from playwright.async_api import async_playwright

        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=USER_AGENT, viewport={"width": 1920, "height": 1080}
        )

        # Add stealth script
        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """)

        # Set longer timeout
        page.set_default_timeout(PLAYWRIGHT_TIMEOUT)

        # Handle authentication if credentials provided
        if self.email and self.password and self.site_url:
            logger.info("Authenticating with Document360 using provided credentials")

            # Navigate to login page
            login_url = f"{self.site_url.rstrip('/').replace('/docs', '')}/login"
            logger.debug(f"Navigating to login page: {login_url}")
            await page.goto(login_url, wait_until="networkidle")

            # Take a screenshot of login page
            await page.screenshot(path="debug_login.png")

            try:
                # Check if we're on a login page by looking for email/password fields
                if (
                    await page.locator(
                        "input[type='email'], input[name='email']"
                    ).count()
                    > 0
                ):
                    logger.debug("Login form detected")

                    # Fill email field - trying multiple possible selectors
                    for selector in [
                        "input[type='email']",
                        "input[name='email']",
                        "#email",
                    ]:
                        if await page.locator(selector).count() > 0:
                            await page.fill(selector, self.email)
                            logger.debug(f"Filled email using selector: {selector}")
                            break

                    # Fill password field - trying multiple possible selectors
                    for selector in [
                        "input[type='password']",
                        "input[name='password']",
                        "#password",
                    ]:
                        if await page.locator(selector).count() > 0:
                            await page.fill(selector, self.password)
                            logger.debug(f"Filled password using selector: {selector}")
                            break

                    # Click login button - trying multiple possible selectors
                    for selector in [
                        "button[type='submit']",
                        "input[type='submit']",
                        "button:has-text('Sign in')",
                        "button:has-text('Log in')",
                    ]:
                        if await page.locator(selector).count() > 0:
                            await page.click(selector)
                            logger.debug(
                                f"Clicked login button using selector: {selector}"
                            )
                            break

                    # Wait for navigation after login
                    await page.wait_for_load_state("networkidle")
                    await page.screenshot(path="debug_after_login.png")

                    # Check if login was successful by looking for error messages
                    error_selectors = [
                        ".error",
                        ".alert-danger",
                        "text=Invalid credentials",
                    ]
                    for selector in error_selectors:
                        if await page.locator(selector).count() > 0:
                            error_text = await page.inner_text(selector)
                            logger.error(f"Login failed: {error_text}")
                            msg = f"Login failed: {error_text}"
                            raise ValueError(msg)

                    logger.info("Authentication successful")
                else:
                    logger.debug(
                        "No login form detected, may already be logged in or no auth required"
                    )
            except Exception as e:
                logger.error(f"Authentication error: {e!s}")

        return p, browser, context, page

    async def _parse_toc_from_site_async(self):
        """Parse the TOC from the live site using Playwright asynchronously."""
        if not self.site_url:
            logger.error("Site URL not provided")
            msg = "Site URL not provided"
            raise ValueError(msg)

        logger.info(f"Parsing TOC from live site {self.site_url}")

        # Set up browser with authentication if needed
        p, browser, context, page = await self._setup_browser()

        try:
            # Navigate to the site
            site_url = cast(str, self.site_url)
            await page.goto(site_url, wait_until="networkidle")

            # Take a screenshot for debugging
            await page.screenshot(path="debug_toc.png")

            # Wait for navigation to complete and TOC to load
            toc_html = ""
            try:
                await page.wait_for_selector(
                    "nav[role='doc-toc']", state="visible", timeout=30000
                )
                # Extract TOC
                toc_html = await page.inner_html("nav[role='doc-toc']")
            except Exception as e:
                logger.warning(
                    f"Could not find TOC with selector 'nav[role='doc-toc']', trying alternative: {e!s}"
                )
                # Try alternative selectors for TOC
                try:
                    await page.wait_for_selector("nav", state="visible", timeout=10000)
                    toc_html = await page.inner_html("nav")
                except Exception as e2:
                    logger.error(f"Could not find any TOC: {e2!s}")

                    # Try to get the page links from any navigation element
                    try:
                        await page.wait_for_selector(
                            "a[href*='/docs/']", state="visible", timeout=10000
                        )
                        # Get all links that point to docs
                        links_html = await page.evaluate("""
                            () => {
                                const links = Array.from(document.querySelectorAll('a[href*="/docs/"]'));
                                return links.map(a => a.outerHTML).join('');
                            }
                        """)
                        toc_html = f"<nav><ul>{links_html}</ul></nav>"
                    except Exception as e3:
                        logger.error(f"Could not find any docs links: {e3!s}")
                        toc_html = ""
        finally:
            await browser.close()
            await p.stop()

        return toc_html

    def _parse_toc_from_site(self) -> list[dict[str, str]]:
        """Parse the TOC from the live site using Playwright."""
        import asyncio

        # Run the async function to get the TOC HTML
        toc_html = asyncio.run(self._parse_toc_from_site_async())

        # Parse the HTML content
        soup = BeautifulSoup(toc_html, "lxml")

        # Find all links in the TOC
        links = []
        for li in soup.find_all("li"):
            a_tag = li.find("a")
            if a_tag and a_tag.get("href"):
                href = a_tag.get("href")
                # Extract the part after /docs/
                if "/docs/" in href:
                    filename = href.split("/docs/")[-1]
                    title = a_tag.text.strip()

                    # For live site, construct the full URL
                    site_url = cast(str, self.site_url)  # We've checked it's not None
                    url = f"{site_url.rstrip('/')}/{filename}"

                    links.append(
                        {
                            "href": href,
                            "filename": filename,
                            "title": title,
                            "url": url,
                        }
                    )

        logger.info(f"Found {len(links)} links in TOC from live site")

        # Apply the pages limit if specified
        if self.pages is not None and self.pages > 0:
            links = links[: self.pages]
            logger.info(f"Limited to first {len(links)} pages as requested")

        self.toc_links = links
        return links

    def extract_article_content(self, source: str) -> dict[str, Any]:
        """
        Extract the title and content from an article file or URL.

        Args:
            source: Path to the article HTML file or URL

        Returns:
            Dictionary with title and content
        """
        if self.use_playwright_for_content and source.startswith(
            ("http://", "https://")
        ):
            return self._extract_content_from_site(source)
        else:
            return self._extract_content_from_file(source)

    def _extract_content_from_file(self, file_path: str) -> dict[str, Any]:
        """Extract content from a local HTML file."""
        logger.debug(f"Extracting content from local file {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "lxml")

            # Extract the article title - try multiple selectors
            title = "Untitled Article"
            for selector in [".article-title", "h1.title", "h1", "title"]:
                title_elem = soup.select_one(selector)
                if title_elem:
                    # Remove the button for copying article link
                    for button in title_elem.select("button"):
                        button.extract()
                    title = title_elem.text.strip()
                    break

            # Extract the article content - try multiple selectors
            content = ""
            for selector in [
                "#articleContent",
                ".article-content",
                "article",
                "main",
                "body",
            ]:
                article_content = soup.select_one(selector)
                if article_content:
                    content = str(article_content)
                    break

            if not content:
                # Last resort - try to find main content area
                body = soup.find("body")
                if body and isinstance(
                    body, Tag
                ):  # Check if body is a Tag, not NavigableString
                    # Remove header, footer, nav elements
                    for tag in body.find_all(["header", "footer", "nav"]):
                        tag.extract()
                    content = str(body)
                    logger.warning(f"Using body content as fallback for {file_path}")
                else:
                    logger.warning(f"No article content found in {file_path}")
                    content = "<p>No content could be extracted from this file.</p>"

            return {"title": title, "content": content, "file_path": file_path}
        except Exception as e:
            logger.error(f"Error extracting content from file {file_path}: {e!s}")
            return {
                "title": f"Error: Could not read {Path(file_path).name}",
                "content": f"<p>Error reading file: {e!s}</p>",
                "file_path": file_path,
            }

    def _extract_content_from_site(self, url: str) -> dict[str, Any]:
        """Extract content from a live site URL using Playwright."""
        import asyncio

        from playwright.async_api import async_playwright

        logger.debug(f"Extracting content from URL {url}")

        async def get_content_from_url():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()

                # Navigate to the URL
                await page.goto(url)

                # Wait for content to load
                await page.wait_for_selector(".article-title", state="visible")
                await page.wait_for_selector("#articleContent", state="visible")

                # Extract title and content
                title_html = await page.inner_html(".article-title")
                content_html = await page.inner_html("#articleContent")

                await browser.close()
                return {"title_html": title_html, "content_html": content_html}

        # Run the async function to get content
        result = asyncio.run(get_content_from_url())

        # Parse the HTML content
        title_soup = BeautifulSoup(result["title_html"], "lxml")

        # Clean up the title
        for button in title_soup.select("button"):
            button.extract()
        title = title_soup.text.strip()

        return {"title": title, "content": result["content_html"], "url": url}

    async def _extract_content_from_site_async(self, url: str) -> dict[str, Any]:
        """Extract content from a live site URL using Playwright asynchronously."""
        import asyncio

        from playwright.async_api import TimeoutError

        logger.debug(f"Extracting content from URL {url}")

        # Initialize retry count
        retries = 0
        last_error: Exception | None = None

        while retries < PLAYWRIGHT_RETRY_COUNT:
            try:
                # Set up browser with authentication if needed
                p, browser, context, page = await self._setup_browser()

                try:
                    # Navigate to the URL with a more reliable wait policy
                    await page.goto(url, wait_until="domcontentloaded")

                    # Random wait to simulate human behavior (1-3 seconds)
                    import random

                    await asyncio.sleep(1 + random.random() * 2)

                    # Check if we hit an error page
                    error_text = await page.evaluate("""() => {
                        const content = document.body.innerText;
                        if (content.includes('Oops! Something went wrong') &&
                            content.includes('No content could be extracted from this page')) {
                            return true;
                        }
                        return false;
                    }""")

                    if error_text:
                        logger.warning(
                            f"Detected error page for {url}, retrying with different approach"
                        )

                        # In case of anti-bot measures, try reloading the page
                        await page.reload(wait_until="networkidle")
                        await asyncio.sleep(2)

                        # Take a screenshot for debugging
                        screenshot_path = f"debug_error_{url.split('/')[-1]}.png"
                        await page.screenshot(path=screenshot_path)

                        # Try a different URL format
                        modified_url = url.replace("/docs/docs/", "/docs/")
                        logger.info(f"Trying modified URL: {modified_url}")
                        await page.goto(modified_url, wait_until="networkidle")
                        await asyncio.sleep(3)

                    # Another screenshot after possible reloading
                    screenshot_path = f"debug_{url.split('/')[-1]}.png"
                    await page.screenshot(path=screenshot_path)

                    # Document360 specific selectors based on the actual HTML structure
                    title_selectors = [
                        "#main-content > d360-article-header > div.d-flex.justify-content-between.align-items-center.mb-3 > h1",
                        "d360-article-header h1.article-title",
                        "h1.article-title",
                        ".article-title",
                        "h1",
                    ]

                    content_selectors = [
                        "#main-content > d360-article-content",
                        "d360-article-content",
                        "#articleContent",
                        ".article-content",
                        "article",
                        "main article",
                    ]

                    # Wait for page content to be available
                    await asyncio.sleep(2)

                    # Try to detect and handle JS rendering
                    await page.evaluate("""() => {
                        // Wait for any Angular/React/Vue rendering to complete
                        return new Promise(resolve => {
                            // Give time for JS frameworks to render
                            setTimeout(resolve, 2000);
                        });
                    }""")

                    title_html = ""
                    for selector in title_selectors:
                        try:
                            # Check if selector exists
                            if await page.locator(selector).count() > 0:
                                title_html = await page.inner_html(selector)
                                logger.debug(f"Found title with selector: {selector}")
                                break
                        except Exception as e:
                            logger.debug(f"Selector {selector} failed: {e!s}")

                    content_html = ""
                    for selector in content_selectors:
                        try:
                            # Check if selector exists
                            if await page.locator(selector).count() > 0:
                                content_html = await page.inner_html(selector)
                                logger.debug(f"Found content with selector: {selector}")
                                break
                        except Exception as e:
                            logger.debug(f"Selector {selector} failed: {e!s}")

                    # If we still don't have content, try to get the whole main content
                    if not content_html:
                        try:
                            logger.debug("Trying to get whole main content as fallback")
                            content_html = await page.inner_html("#main-content")
                        except Exception as e:
                            logger.debug(
                                f"Fallback main content selector failed: {e!s}"
                            )

                    # Take a screenshot for debugging if no content found
                    if not title_html or not content_html:
                        await page.screenshot(path=screenshot_path)
                        logger.warning(
                            f"Could not find all content, saved screenshot to {screenshot_path}"
                        )

                        # Last resort - get entire body
                        try:
                            logger.debug("Trying to get entire body as final fallback")
                            html = await page.content()
                            body_soup = BeautifulSoup(html, "lxml")

                            if not title_html:
                                title_elem = body_soup.select_one("title")
                                if title_elem:
                                    title_html = str(title_elem)

                            if not content_html:
                                body = body_soup.find("body")
                                if body:
                                    content_html = str(body)
                        except Exception as e:
                            logger.error(f"Final fallback failed: {e!s}")

                    # Parse the HTML content
                    title_soup = BeautifulSoup(title_html, "lxml")

                    # Clean up the title - remove buttons and other elements
                    for element in title_soup.select("button, d360-copy-article-link"):
                        element.extract()

                    # Also clean up icons and other non-text elements
                    for element in title_soup.select("i, span.me-2"):
                        element.extract()

                    title = (
                        title_soup.text.strip()
                        if title_soup.text
                        else "Untitled Article"
                    )

                    if not content_html:
                        logger.warning(
                            f"No content found for {url}. Using fallback empty content."
                        )
                        content_html = (
                            "<p>No content could be extracted from this page.</p>"
                        )

                    return {"title": title, "content": content_html, "url": url}

                finally:
                    await browser.close()
                    await p.stop()

            except TimeoutError as e:
                retries += 1
                last_error = e
                logger.warning(
                    f"Timeout on try {retries}/{PLAYWRIGHT_RETRY_COUNT} for {url}: {e!s}"
                )
                await asyncio.sleep(2)  # Wait before retrying
            except Exception as e:
                retries += 1
                last_error = e
                logger.warning(
                    f"Error on try {retries}/{PLAYWRIGHT_RETRY_COUNT} for {url}: {e!s}"
                )
                await asyncio.sleep(2)  # Wait before retrying

        # If we get here, all retries failed
        logger.error(
            f"Failed to extract content from {url} after {PLAYWRIGHT_RETRY_COUNT} attempts: {last_error!s}"
        )
        return {
            "title": f"Error: Could not load {url.split('/')[-1]}",
            "content": f"<p>Error: Could not extract content from this page after {PLAYWRIGHT_RETRY_COUNT} attempts.</p>",
            "url": url,
            "error": str(last_error),
        }

    async def process_articles_async(self) -> dict[str, dict[str, Any]]:
        """
        Process all articles from the TOC links asynchronously.

        Returns:
            Dictionary mapping filenames to article information
        """
        logger.info("Processing articles asynchronously")
        articles: dict[str, dict[str, Any]] = {}

        # If we're using Playwright for content (site_url is provided)
        if self.use_playwright_for_content:
            # Create a semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(
                5
            )  # Process 5 pages at a time to avoid overloading

            async def process_with_semaphore(
                i: int, link: dict[str, str]
            ) -> tuple[str, dict[str, Any]]:
                async with semaphore:
                    filename = link["filename"]
                    # Use the URL from the link or construct it
                    url = link.get("url", "")
                    if not url and self.site_url:
                        url = f"{self.site_url.rstrip('/')}/{filename}"

                    logger.info(
                        f"Processing {i + 1}/{len(self.toc_links)}: {filename} from {url}"
                    )
                    try:
                        article = await self._extract_content_from_site_async(url)
                        return filename, {
                            "title": article["title"],
                            "content": article["content"],
                            "href": link["href"],
                            "source": url,
                        }
                    except Exception as e:
                        logger.error(f"Error processing {url}: {e!s}")
                        return filename, {
                            "title": f"Error: Could not load {filename}",
                            "content": "<p>Error: Could not extract content from this page.</p>",
                            "href": link["href"],
                            "source": url,
                        }

            # Create tasks for each link
            tasks = [
                process_with_semaphore(i, link) for i, link in enumerate(self.toc_links)
            ]

            # Process with progress reporting using tqdm
            for task in tqdm.asyncio.tqdm.as_completed(tasks):
                filename, article_data = await task
                articles[filename] = article_data
        else:
            # For local files only
            async def process_local_file(
                link: dict[str, str],
            ) -> tuple[str, dict[str, Any]]:
                filename = link["filename"]
                file_path = link.get("file_path", "")

                try:
                    article = self._extract_content_from_file(file_path)
                    return filename, {
                        "title": article["title"],
                        "content": article["content"],
                        "href": link["href"],
                        "source": file_path,
                    }
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e!s}")
                    return filename, {
                        "title": f"Error: Could not load {filename}",
                        "content": "<p>Error: Could not extract content from this page.</p>",
                        "href": link.get("href", ""),
                        "source": file_path,
                    }

            # Process local files in parallel using asyncio
            tasks = [process_local_file(link) for link in self.toc_links]

            # Show progress using manual tracking
            with console.status(f"Processing {len(tasks)} articles..."):
                # Use asyncio.gather to run all tasks concurrently
                results = await asyncio.gather(*tasks)

                # Combine results
                for filename, article_data in results:
                    articles[filename] = article_data

        self.articles = articles
        logger.info(f"Processed {len(articles)} articles")
        return articles

    def process_articles(self) -> dict[str, dict[str, Any]]:
        """
        Process all articles from the TOC links.
        This is a synchronous wrapper around the async processing function.

        Returns:
            Dictionary mapping filenames to article information
        """
        # Apply the pages limit if specified and not already applied
        if self.pages is not None and len(self.toc_links) > self.pages:
            self.toc_links = self.toc_links[: self.pages]
            logger.info(f"Limited to first {len(self.toc_links)} pages as requested")

        # Call the async function
        return asyncio.run(self.process_articles_async())

    def generate_html_document(self) -> str:
        """
        Generate a complete HTML document from the processed articles.

        Returns:
            The generated HTML document as a string
        """
        logger.info("Generating HTML document")

        # Start with the HTML structure
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Document360 Documentation</title>
    <style>
{self.css}
    </style>
</head>
<body>
    <aside>
        <nav>
            <ul>
"""

        # Add the TOC
        for link in self.toc_links:
            href = f"#{link['filename']}"
            title = link["title"]
            html += f'                <li><a href="{href}">{title}</a></li>\n'

        html += """
            </ul>
        </nav>
    </aside>
    <main>
"""

        # Add the articles
        for link in self.toc_links:
            filename = link["filename"]
            if filename in self.articles:
                article = self.articles[filename]
                html += f'        <div id="{filename}">\n'
                html += f"            <h1>{article['title']}</h1>\n"
                html += f"            {article['content']}\n"
                html += "        </div>\n"

        html += """
    </main>
</body>
</html>
"""

        return html

    def generate_markdown_document(self, html_document: str) -> str:
        """
        Generate a Markdown document from the HTML document.

        Args:
            html_document: The HTML document to convert

        Returns:
            The generated Markdown document as a string
        """
        logger.info("Generating Markdown document")

        # Configure the HTML to text converter
        h2t = html2text.HTML2Text()
        h2t.ignore_links = False
        h2t.body_width = 0  # No wrapping
        h2t.protect_links = True
        h2t.unicode_snob = True
        h2t.ignore_images = False
        h2t.ignore_tables = False

        # Convert HTML to Markdown
        markdown = h2t.handle(html_document)

        return markdown

    def run(self) -> tuple[str, str]:
        """
        Run the extraction process.

        Returns:
            Tuple containing paths to the output HTML and Markdown files
        """
        logger.info("Starting Document360 extraction")

        if self.use_playwright_for_content:
            logger.info(f"Using Playwright to extract content from {self.site_url}")
        else:
            logger.info(f"Using local files from {self.docs_dir}")

        # Parse the TOC
        self.parse_toc()

        # Process the articles
        self.process_articles()

        # Generate the HTML document
        html_document = self.generate_html_document()

        # Write the HTML document to a file
        with open(self.output_html, "w", encoding="utf-8") as f:
            f.write(html_document)
        logger.info(f"HTML document written to {self.output_html}")

        # Generate the Markdown document
        markdown_document = self.generate_markdown_document(html_document)

        # Write the Markdown document to a file
        with open(self.output_md, "w", encoding="utf-8") as f:
            f.write(markdown_document)
        logger.info(f"Markdown document written to {self.output_md}")

        return self.output_html, self.output_md


def main(
    nav: str | None = None,
    docs_dir: str = "docs",
    html: str = "document360_docs.html",
    md: str = "document360_docs.md",
    site: str | None = None,
    css: str | None = None,
    pages: int | None = None,
    *,
    email: str | None = None,
    password: str | None = None,
    verbose: bool = False,
) -> None:
    """
    Transform Document360 documentation into a complete HTML and Markdown document.

    Args:
        nav: Path to the navigation XHTML file (prioritized if provided)
        docs_dir: Directory containing the documentation HTML files
        html: Output HTML filename
        md: Output Markdown filename
        site: URL of the live Document360 site to scrape (e.g., https://docs.document360.com/docs/)
        css: Path to a custom CSS file for styling the HTML output
        pages: Maximum number of pages to process (default: all)
        email: Email for Document360 login if the site requires authentication
        password: Password for Document360 login if the site requires authentication
        verbose: Enable verbose logging
    """
    if site is None and nav is None:
        console.print("[red]Error:[/] Either --nav or --site must be specified")
        return

    if pages is not None and pages <= 0:
        console.print("[red]Error:[/] --pages must be a positive number")
        return

    if nav:
        console.print(f"[blue]Info:[/] Using local navigation file: {nav}")
        if site:
            console.print(f"[blue]Info:[/] Will use site for content: {site}")

    if css:
        console.print(f"[blue]Info:[/] Using custom CSS file: {css}")
    else:
        console.print(f"[blue]Info:[/] Using default CSS file: {DEFAULT_CSS_PATH}")

    if email and password:
        console.print("[blue]Info:[/] Using provided credentials for authentication")
    elif site and (email or password):
        console.print(
            "[yellow]Warning:[/] Only partial credentials provided, authentication may fail"
        )

    extractor = Document360Extractor(
        nav_file=nav,
        docs_dir=docs_dir,
        output_html=html,
        output_md=md,
        site_url=site,
        css_file=css,
        pages=pages,
        email=email,
        password=password,
        verbose=verbose,
    )

    html_path, md_path = extractor.run()

    console.print("\n[green]Success![/] Document360 documentation extracted:")
    console.print(f"  - HTML: [bold]{html_path}[/bold]")
    console.print(f"  - Markdown: [bold]{md_path}[/bold]")
    if pages is not None:
        console.print(f"  - Limited to first [bold]{pages}[/bold] pages")
    if nav:
        console.print(f"  - TOC source: [bold]Local file ({nav})[/bold]")
    else:
        console.print(f"  - TOC source: [bold]Site ({site})[/bold]")
    console.print(f"  - CSS source: [bold]{css or DEFAULT_CSS_PATH}[/bold]")


if __name__ == "__main__":
    fire.Fire(main)
