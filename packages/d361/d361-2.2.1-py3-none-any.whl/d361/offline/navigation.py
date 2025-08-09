# this_file: src/d361/offline/navigation.py

from typing import Any
from urllib.parse import urljoin

from loguru import logger
from playwright.async_api import Page

from .browser import expand_all_items, scroll_to_bottom


async def extract_navigation(
    page: Page, nav_url: str, test: bool = False
) -> dict[str, Any]:
    """Extract navigation structure from Document360 page.

    Args:
        page: Playwright page
        nav_url: URL to extract navigation from
        test: If True, limit the number of items processed

    Returns:
        Navigation structure as a dictionary
    """
    try:
        logger.info(f"Navigating to {nav_url} to extract navigation")

        # Navigate to the page with longer timeout and wait for network to be idle
        await page.goto(nav_url, wait_until="networkidle", timeout=60000)
        logger.info("Page loaded, waiting for content...")

        # Wait longer for the content to fully load
        await page.wait_for_timeout(5000)

        # More robust cookie consent handling
        cookie_handled = False
        try:
            # First, focus on Document360 specific cookie buttons as highest priority
            document360_cookie_selectors = [
                "button.cookie-close.rounded-3",  # Document360 specific button
                "button.cookie-close.cookie-close-icon.cookie-dismiss",  # Document360 dismiss button
                ".cookie-consent-accept",  # Another possible selector
                ".cookie-close",  # General close button
            ]

            # Try Document360 specific selectors first with a higher timeout
            for selector in document360_cookie_selectors:
                try:
                    cookie_button = await page.wait_for_selector(selector, timeout=2000)
                    if cookie_button:
                        logger.info(
                            f"Found Document360 cookie consent button: {selector}"
                        )
                        is_visible = await cookie_button.is_visible()
                        is_enabled = await cookie_button.is_enabled()

                        if is_visible and is_enabled:
                            logger.info(
                                f"Clicking Document360 cookie button: {selector}"
                            )
                            await cookie_button.click()
                            await page.wait_for_timeout(
                                1500
                            )  # Wait longer to ensure dialog closes
                            cookie_handled = True

                            # Check if cookie banner is gone
                            banner_visible = await page.is_visible(
                                ".cookie-consent, .cookie-banner"
                            )
                            if not banner_visible:
                                logger.info(
                                    "Document360 cookie banner closed successfully"
                                )
                                break
                except Exception as e:
                    logger.debug(
                        f"Document360 cookie selector {selector} not found: {e}"
                    )

            # If Document360 specific buttons didn't work, try more generic approaches
            if not cookie_handled:
                # Define fallback cookie consent selectors
                fallback_selectors = [
                    "button#onetrust-accept-btn-handler",  # OneTrust button
                    ".cookie-btn-accept",  # Generic accept
                    ".cookie-consent button",  # Generic cookie button
                    "#cookie-consent-accept",  # ID-based cookie button
                    "div[aria-label='Cookie banner'] button",  # ARIA-labeled cookie banner
                    "button:has-text('Accept')",  # Text-based accept button
                    "button:has-text('Accept All')",  # Text-based accept all button
                    "button:has-text('Accept Cookies')",  # Text-based accept cookies button
                    "button:has-text('I Agree')",  # Text-based agree button
                    "button:has-text('Close')",  # Text-based close button
                    "button:has-text('Got it')",  # Text-based got it button
                ]

                # Try each selector with a timeout to prevent hanging
                for selector in fallback_selectors:
                    try:
                        cookie_button = await page.wait_for_selector(
                            selector, timeout=1000
                        )
                        if cookie_button:
                            logger.info(
                                f"Found cookie consent button with selector: {selector}"
                            )

                            # Check if button is visible and enabled before clicking
                            is_visible = await cookie_button.is_visible()
                            is_enabled = await cookie_button.is_enabled()

                            if is_visible and is_enabled:
                                logger.info(
                                    f"Clicking cookie consent button: {selector}"
                                )
                                await cookie_button.click()
                                await page.wait_for_timeout(1000)
                                cookie_handled = True

                                # Check if cookie banner is still visible
                                banner_visible = await page.is_visible(
                                    ".cookie-banner, .cookie-consent, #onetrust-banner-sdk"
                                )
                                if not banner_visible:
                                    logger.info("Cookie banner closed successfully")
                                    break
                                else:
                                    logger.warning(
                                        "Cookie banner still visible after clicking button, trying next selector"
                                    )
                            else:
                                logger.warning(
                                    f"Cookie button found but not clickable (visible: {is_visible}, enabled: {is_enabled})"
                                )
                    except Exception as e:
                        # Just log and continue to the next selector
                        logger.debug(
                            f"Selector {selector} not found or not clickable: {e}"
                        )
                        continue

            # If buttons didn't work, try JavaScript approaches
            if not cookie_handled:
                # Try to use JavaScript to dismiss common cookie banners
                dismiss_scripts = [
                    # Document360 specific scripts
                    "document.querySelector('button.cookie-close.rounded-3')?.click();",
                    "document.querySelector('button.cookie-close.cookie-close-icon.cookie-dismiss')?.click();",
                    "document.querySelector('.cookie-close')?.click();",
                    # More generic scripts
                    "document.querySelector('.cookie-btn-accept')?.click();",
                    "document.querySelector('#onetrust-accept-btn-handler')?.click();",
                    "document.querySelectorAll('button').forEach(b => { if(b.innerText.includes('Accept') || b.innerText.includes('Agree') || b.innerText.includes('Cookie')) b.click(); });",
                    # More aggressive approach: hide all elements that might be cookie banners
                    "document.querySelectorAll('.cookie-banner, .cookie-consent, #onetrust-banner-sdk').forEach(el => { el.style.display = 'none'; });",
                ]

                for script in dismiss_scripts:
                    try:
                        await page.evaluate(script)
                        await page.wait_for_timeout(1000)
                        # Check if cookie banner is gone
                        banner_visible = await page.is_visible(
                            ".cookie-banner, .cookie-consent, #onetrust-banner-sdk"
                        )
                        if not banner_visible:
                            logger.info("Cookie banner closed via JavaScript")
                            cookie_handled = True
                            break
                    except Exception as e:
                        logger.debug(f"JavaScript cookie dismissal failed: {e}")

            # As a last resort, let's try to press Escape key which sometimes closes popups
            if not cookie_handled:
                try:
                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(1000)
                    logger.info("Tried to dismiss cookie banner with Escape key")
                except Exception as e:
                    logger.debug(f"Escape key dismissal failed: {e}")

        except Exception as e:
            logger.warning(f"Error during cookie consent handling: {e}")
            # Even if cookie handling fails, we'll continue with navigation extraction

        # Continue with navigation extraction
        logger.info("Proceeding with navigation extraction")

        # Wait for navigation tree to be available
        tree_selector = "#left-panel > div.catergory-list > site-category-list-tree-view > d360-data-list-tree-view"
        try:
            tree_element = await page.wait_for_selector(tree_selector, timeout=10000)
            if tree_element:
                logger.info("Document360 navigation tree found")
            else:
                msg = "Tree element not found after wait_for_selector"
                raise Exception(msg)
        except Exception as e:
            logger.warning(f"Main tree selector not found: {e}")
            # Try fallback to direct tree selector
            tree_selector = "d360-data-list-tree-view"
            try:
                tree_element = await page.wait_for_selector(
                    tree_selector, timeout=10000
                )
                if tree_element:
                    logger.info(
                        "Document360 navigation tree found with fallback selector"
                    )
                else:
                    msg = "Fallback tree element not found after wait_for_selector"
                    raise Exception(msg)
            except Exception as e:
                logger.warning(f"Fallback tree selector not found: {e}")
                logger.warning(
                    "Could not find Document360 navigation tree, trying fallback methods"
                )
                return await extract_fallback_nav_structure(page)

        # Expand navigation tree - first scroll to bottom, then expand elements
        await expand_navigation_tree(page, test)

        # Extract tree structure
        nav_structure = await extract_tree_structure(page, tree_selector)

        logger.info(
            f"Successfully extracted navigation with {len(nav_structure['items'])} top-level items"
        )
        return nav_structure

    except Exception as e:
        logger.error(f"Error extracting navigation: {e}")
        # Return a minimal structure to avoid further errors
        return {"items": []}


async def expand_navigation_tree(page: Page, test: bool = False) -> None:
    """Expand the navigation tree to show all items.

    Args:
        page: Playwright page
        test: If True, limit the expansion (not used currently)
    """
    try:
        # First scroll to ensure all virtual items are loaded
        await scroll_to_bottom(
            page, "d360-data-list-tree-view cdk-virtual-scroll-viewport"
        )

        # Then expand all collapsible items
        tree_selector = "d360-data-list-tree-view"
        expanded = await expand_all_items(
            page, tree_selector, max_attempts=3 if test else 5
        )
        logger.info(f"Expanded {expanded} navigation items")

    except Exception as e:
        logger.error(f"Error expanding navigation tree: {e}")


async def extract_tree_structure(page: Page, tree_selector: str) -> dict[str, Any]:
    """Extract the navigation tree structure.

    Args:
        page: Playwright page
        tree_selector: CSS selector for the tree view

    Returns:
        Dictionary containing navigation structure
    """
    try:
        # Use approach from d360_getsitenav.py to extract tree nodes
        nodes = await page.query_selector_all(f"{tree_selector} .tree-wrapper")

        if not nodes:
            # Try another selector pattern
            nodes = await page.query_selector_all(".tree-wrapper")

        if not nodes:
            logger.warning("No tree nodes found")
            return {"items": []}

        logger.info(f"Found {len(nodes)} navigation nodes")

        # Extract the tree structure using a more robust approach
        root: dict[str, Any] = {"title": "Root", "link": None, "children": []}
        stack: list[dict[str, Any]] = [root]
        previous_level = -1
        base_url = await page.evaluate("window.location.origin")

        for node in nodes:
            # Determine hierarchy level by counting filler divs
            fillers = await node.query_selector_all(".filler")
            level = len(fillers)

            # Adjust stack to find the correct parent based on level
            while level <= previous_level:
                stack.pop()
                previous_level -= 1

            parent = stack[-1]

            # Extract title and link
            title_element = await node.query_selector(".data-title")

            if title_element:
                title = await title_element.inner_text()
                title = title.strip() if title else "Untitled"

                href = await title_element.get_attribute("href")
                link = urljoin(base_url, href) if href else None

                # Create new node and add to parent's children
                new_node: dict[str, Any] = {
                    "title": title,
                    "link": link,
                    "children": [],
                }
                parent["children"].append(new_node)
                stack.append(new_node)
                previous_level = level

        # Convert to the expected format
        result = {"items": root["children"]}
        return result

    except Exception as e:
        logger.error(f"Error extracting tree structure: {e}")
        return {"items": []}


async def extract_fallback_nav_structure(page: Page) -> dict[str, Any]:
    """Fallback method to extract navigation by looking for other navigation elements.

    Args:
        page: Playwright page

    Returns:
        Dictionary containing navigation structure
    """
    try:
        # Try to find a different navigation selector
        # Document360 sometimes uses different navigation patterns
        selectors = [
            ".navigation-menu",
            ".sidebar-menu",
            ".nav-container",
            "#left-panel nav",
            "nav.sidebar",
        ]

        for selector in selectors:
            nav_element = await page.query_selector(selector)
            if nav_element:
                logger.info(f"Found fallback navigation with selector: {selector}")

                # Try to extract links
                links = await nav_element.query_selector_all("a")

                if links:
                    items = []
                    base_url = await page.evaluate("window.location.origin")

                    for link in links:
                        text = await link.inner_text()
                        href = await link.get_attribute("href")
                        if href:
                            full_url = urljoin(base_url, href)
                            items.append(
                                {
                                    "title": text.strip(),
                                    "link": full_url,
                                    "children": [],
                                }
                            )

                    logger.info(
                        f"Extracted {len(items)} navigation items using fallback method"
                    )
                    return {"items": items}

        # If no navigation is found, look for breadcrumbs as a last resort
        breadcrumbs = await page.query_selector(".breadcrumbs, .breadcrumb")
        if breadcrumbs:
            logger.info("Using breadcrumbs as fallback navigation")
            links = await breadcrumbs.query_selector_all("a")

            items = []
            base_url = await page.evaluate("window.location.origin")

            for link in links:
                text = await link.inner_text()
                href = await link.get_attribute("href")
                if href:
                    full_url = urljoin(base_url, href)
                    items.append(
                        {"title": text.strip(), "link": full_url, "children": []}
                    )

            return {"items": items}

        logger.warning("No fallback navigation found")
        return {"items": []}

    except Exception as e:
        logger.error(f"Error in fallback navigation extraction: {e}")
        return {"items": []}
