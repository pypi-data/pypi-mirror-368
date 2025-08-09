# this_file: src/d361/offline/content.py

from loguru import logger
from markdownify import markdownify as md
from playwright.async_api import Page
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
async def extract_page_content(page: Page) -> dict[str, str] | None:
    """Extract title, HTML content, and Markdown from a page.

    Args:
        page: Playwright page object

    Returns:
        Dictionary with title, html, and markdown content, or None if extraction failed
    """
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)

        # Try to dismiss cookie consent banners
        for cookie_selector in [
            "button[id*='cookie']",
            "button[id*='Cookie']",
            "button[id*='consent']",
            "a[id*='cookie-accept']",
            ".cookie-consent-button",
            "[aria-label='Accept cookies']",
            "[data-action='accept-all']",
            ".accept-cookies",
            ".cookie-accept",
        ]:
            try:
                cookie_button = await page.query_selector(cookie_selector)
                if cookie_button and await cookie_button.is_visible():
                    logger.debug(f"Clicking cookie consent button: {cookie_selector}")
                    await cookie_button.click()
                    break
            except Exception as cookie_err:
                logger.debug(f"Cookie button error: {cookie_err}")

        # Wait a bit more for content to fully render
        await page.wait_for_timeout(1000)

        # Extract title
        title = None
        title_selectors = [
            "h1.article-title",
            ".article-title",
            "#main-content h1",
            ".content-header h1",
            "header h1",
            ".entry-title",
            ".page-title",
            "h1.title",
            "h1",
        ]

        for selector in title_selectors:
            try:
                title_element = await page.query_selector(selector)
                if title_element:
                    title = await title_element.inner_text()
                    title = title.strip()
                    logger.debug(f"Found title using selector: {selector}")
                    break
            except Exception as title_err:
                logger.debug(f"Error with title selector {selector}: {title_err}")

        # Extract article content with more selectors
        html_content = None
        content_selectors = [
            "#articleContent",
            "d360-article-content",
            ".article-content",
            ".document-content",
            ".main-content article",
            ".content-body",
            "#main-content",
            ".content-container",
            "article",
            ".article",
            ".doc-content",
            "main",
        ]

        for selector in content_selectors:
            try:
                content_element = await page.query_selector(selector)
                if content_element:
                    html_content = await content_element.inner_html()
                    logger.debug(f"Found content using selector: {selector}")
                    break
            except Exception as content_err:
                logger.debug(f"Error with content selector {selector}: {content_err}")

        # Fallback: if no content found with specific selectors, try getting the main content area
        if not html_content:
            logger.debug("Trying fallback content extraction")
            try:
                # Wait for the main content to be available
                await page.wait_for_selector("body", timeout=5000)

                # Remove potentially unwanted elements
                for remove_selector in [
                    "nav",
                    "header",
                    "footer",
                    ".navigation",
                    ".sidebar",
                    "#sidebar",
                    ".menu",
                    ".cookie-banner",
                ]:
                    try:
                        elements = await page.query_selector_all(remove_selector)
                        for element in elements:
                            await page.evaluate("(el) => el.remove()", element)
                    except Exception:
                        pass

                # Extract the body content as a fallback
                body = await page.query_selector("body")
                if body:
                    html_content = await body.inner_html()
                    logger.debug("Extracted content from body as fallback")
            except Exception as fallback_err:
                logger.debug(f"Fallback extraction error: {fallback_err}")

        if not html_content and not title:
            logger.warning("No content or title found in page")
            return None

        # Convert HTML to Markdown using markdownify
        markdown_content = ""
        if html_content:
            markdown_content = md(html_content, heading_style="ATX")

        # Capture the page URL for reference
        url = page.url

        return {
            "title": title or "Untitled",
            "html": html_content or "<p>No content available</p>",
            "markdown": markdown_content or "No content available",
            "url": url,
        }

    except Exception as e:
        logger.error(f"Error extracting page content: {e}")
        return None
