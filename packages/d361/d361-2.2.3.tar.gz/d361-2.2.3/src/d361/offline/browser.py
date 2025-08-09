# this_file: src/d361/offline/browser.py


from loguru import logger
from playwright.async_api import Browser, BrowserContext, Page


async def setup_browser(headless: bool = True) -> tuple[Browser, BrowserContext]:
    """Set up browser for web scraping.

    Args:
        headless: Whether to run browser in headless mode

    Returns:
        Tuple of (Browser, BrowserContext)
    """
    from playwright.async_api import async_playwright

    playwright = await async_playwright().start()
    browser_type = playwright.chromium

    # Configure browser with more reliable settings
    browser = await browser_type.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",  # Hide automation flags
            "--disable-features=IsolateOrigins,site-per-process",  # Disable site isolation
            "--disable-web-security",  # Allow cross-origin requests
            "--disable-setuid-sandbox",  # For Linux compatibility
            "--no-sandbox",  # For Linux compatibility
            "--disable-dev-shm-usage",  # For Docker/CI systems
            "--disable-accelerated-2d-canvas",  # Reduce memory usage
            "--no-first-run",  # Skip first run dialogs
            "--no-default-browser-check",  # Skip default browser check
            "--disable-notifications",  # Disable notifications
            "--disable-extensions",  # Disable extensions
        ],
        ignore_default_args=["--enable-automation"],  # Avoid detection
    )

    logger.info(f"Browser setup complete (headless: {headless})")

    # Set up context with more realistic browser behavior
    context = await browser.new_context(
        viewport={
            "width": 1920,
            "height": 1080,
        },  # Larger viewport for better visibility
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        accept_downloads=True,
        java_script_enabled=True,
        bypass_csp=True,  # Bypass Content Security Policy
        ignore_https_errors=True,  # Ignore HTTPS errors
    )

    # Set default navigation timeout to prevent hanging
    context.set_default_navigation_timeout(60000)  # 60 seconds
    context.set_default_timeout(30000)  # 30 seconds for other operations

    return browser, context


async def scroll_to_bottom(page: Page, selector: str, max_scrolls: int = 30) -> None:
    """Scroll through a tree view to load all virtual scroll items.

    Args:
        page: Playwright page object
        selector: CSS selector for the scrollable element
        max_scrolls: Maximum number of scroll attempts
    """
    try:
        # Check if the element exists
        element = await page.query_selector(selector)
        if not element:
            logger.warning(f"Element not found with selector: {selector}")
            return

        logger.info(f"Starting to scroll element with selector: {selector}")

        # First attempt to find viewport element which is what we need to scroll in Document360
        viewport_selector = f"{selector} cdk-virtual-scroll-viewport"
        viewport = await page.query_selector(viewport_selector)

        # If viewport isn't found, fallback to the original selector
        scroll_target = viewport_selector if viewport else selector

        prev_height = 0
        same_height_count = 0
        scroll_position = 0

        for i in range(max_scrolls):
            # Get current scroll height
            current_height = await page.evaluate(f"""() => {{
                const element = document.querySelector('{scroll_target}');
                return element ? element.scrollHeight : 0;
            }}""")

            # Get current scroll position
            scroll_position = await page.evaluate(f"""() => {{
                const element = document.querySelector('{scroll_target}');
                return element ? element.scrollTop : 0;
            }}""")

            client_height = await page.evaluate(f"""() => {{
                const element = document.querySelector('{scroll_target}');
                return element ? element.clientHeight : 0;
            }}""")

            logger.debug(
                f"Scroll info: height={current_height}, position={scroll_position}, visible={client_height}"
            )

            if (
                current_height == prev_height
                and scroll_position + client_height >= current_height - 50
            ):
                same_height_count += 1
                if same_height_count >= 3:  # If height hasn't changed for 3 iterations
                    logger.info(
                        "Scroll height stabilized and reached bottom, assuming all items loaded"
                    )
                    break
            else:
                same_height_count = 0

            # Scroll further down
            await page.evaluate(f"""() => {{
                const element = document.querySelector('{scroll_target}');
                if (element) {{
                    // Scroll in larger increments to reach bottom faster
                    element.scrollTop += element.clientHeight * 2;
                }}
            }}""")

            logger.debug(
                f"Scroll attempt {i + 1}/{max_scrolls}, height: {current_height}"
            )
            prev_height = current_height
            await page.wait_for_timeout(800)  # Longer wait for items to load

        # Final scroll to very bottom to ensure everything is loaded
        await page.evaluate(f"""() => {{
            const element = document.querySelector('{scroll_target}');
            if (element) {{
                element.scrollTop = element.scrollHeight;
            }}
        }}""")
        await page.wait_for_timeout(1000)

        logger.info(f"Completed scrolling with {prev_height} final height")
    except Exception as e:
        logger.error(f"Error scrolling: {e}")


async def expand_all_items(page: Page, selector: str, max_attempts: int = 12) -> int:
    """Recursively expand all items in a tree view by clicking collapsed triangle icons.

    Args:
        page: Playwright page object
        selector: CSS selector for the tree view
        max_attempts: Maximum number of expansion iterations

    Returns:
        Number of nodes expanded
    """
    try:
        logger.info(
            f"Starting aggressive expansion of tree items using selector: {selector}"
        )
        expanded_count = 0
        total_expanded = 0

        # First, make sure all virtualized content is loaded by scrolling down thoroughly
        for i in range(3):  # Do multiple complete scroll-throughs
            logger.info(f"Initial scrolling pass {i + 1}/3 to reveal all content")
            await scroll_to_bottom(page, selector, max_scrolls=80)  # Increased from 50
            await page.wait_for_timeout(1000)  # Wait longer between passes

        # Now scroll back to the top to start expanding from the top
        await page.evaluate(f"""() => {{
            const element = document.querySelector('{selector} cdk-virtual-scroll-viewport') ||
                           document.querySelector('{selector}');
            if (element) {{
                element.scrollTop = 0;
            }}
        }}""")
        await page.wait_for_timeout(1000)

        # Try more rounds of expansion with smaller batches but more aggressive scrolling
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Expansion iteration {attempt}/{max_attempts}")
            expanded_in_this_attempt = 0  # Track expansions in this attempt

            # Look for collapsed arrows - may vary by Document360 version
            collapsed_selectors = [
                f"{selector} .tree-arrow .fa-angle-right",
                f"{selector} .expand-icon.collapsed",
                f"{selector} .collapsed-icon",
                f"{selector} .tree-arrow i.fa-caret-right",
                f"{selector} .tree-arrow i.fa-chevron-right",
                f"{selector} i.fa-angle-right",
                f"{selector} i.fa-caret-right",
                f"{selector} i.fa-chevron-right",
                ".tree-arrow .fa-angle-right",  # Fallback
                ".tree-arrow .fa-caret-right",  # Another common icon
                ".tree-arrow .fa-chevron-right",  # Another common icon
                ".fa-caret-right",  # Generic fallback
                ".fa-angle-right",  # Generic fallback
                ".fa-chevron-right",  # Generic fallback
                "[aria-expanded='false']",  # ARIA attribute for collapsed items
                ".collapsed",  # Generic class for collapsed items
                ".tree-node.collapsed",  # Common pattern
                ".nav-item.collapsed",  # Another common pattern
            ]

            for collapse_selector in collapsed_selectors:
                try:
                    # Count how many collapsed items exist before clicking
                    count = await page.evaluate(f"""() => {{
                        return document.querySelectorAll('{collapse_selector}').length;
                    }}""")

                    if count > 0:
                        logger.info(
                            f"Found {count} collapsed items with selector: {collapse_selector}"
                        )

                        # Click items in smaller batches for better reliability
                        for batch_start in range(
                            0, count, 2
                        ):  # Even smaller batches (2)
                            batch_end = min(batch_start + 2, count)
                            logger.debug(
                                f"Processing batch {batch_start}-{batch_end} of {count}"
                            )

                            # Scroll to ensure we can see elements in the current viewport
                            scroll_step = (
                                batch_start / count
                            ) * 0.8  # 80% of total scroll height
                            await page.evaluate(
                                f"""(scrollPercentage) => {{
                                const element = document.querySelector('{selector} cdk-virtual-scroll-viewport') ||
                                              document.querySelector('{selector}');
                                if (element) {{
                                    element.scrollTop = scrollPercentage * element.scrollHeight;
                                }}
                            }}""",
                                scroll_step,
                            )
                            await page.wait_for_timeout(
                                500
                            )  # Wait for scroll to settle

                            # Get fresh references to elements for each batch
                            collapsed_icons = await page.query_selector_all(
                                collapse_selector
                            )

                            # Process only this batch
                            for i in range(
                                batch_start, min(batch_end, len(collapsed_icons))
                            ):
                                if i < len(collapsed_icons):
                                    icon = collapsed_icons[i]
                                    try:
                                        # Check if element is still attached and visible
                                        is_visible = await icon.is_visible()
                                        if is_visible:
                                            await icon.scroll_into_view_if_needed()
                                            # Wait a bit before clicking for better stability
                                            await page.wait_for_timeout(
                                                200
                                            )  # Longer wait
                                            await icon.click(force=True)  # Force click
                                            expanded_count += 1
                                            expanded_in_this_attempt += 1
                                            total_expanded += 1
                                            # Short wait after each click
                                            await page.wait_for_timeout(
                                                300
                                            )  # Longer wait
                                    except Exception as e:
                                        _error_message = str(e).splitlines()[0] if str(e).splitlines() else str(e)
                                        logger.debug(
                                            f"Error expanding item: {_error_message}"
                                        )
                                        continue

                            # After each batch, wait a bit longer to let DOM settle
                            await page.wait_for_timeout(1000)  # Increased from 750
                except Exception as e:
                    _error_message = str(e).splitlines()[0] if str(e).splitlines() else str(e)
                    logger.debug(
                        f"Error processing selector {collapse_selector}: {_error_message}"
                    )
                    continue

            # Try alternative approach using JavaScript for every attempt
            try:
                logger.info("Trying JavaScript-based expansion...")
                # This attempts to click all arrow icons using JavaScript
                expanded_js_count = await page.evaluate("""() => {
                    let clicked = 0;
                    const selectors = [
                        '.tree-arrow .fa-angle-right',
                        '.tree-arrow .fa-caret-right',
                        '.tree-arrow .fa-chevron-right',
                        '.expand-icon.collapsed',
                        '.collapsed-icon',
                        'i.fa-angle-right',
                        'i.fa-caret-right',
                        'i.fa-chevron-right',
                        '[aria-expanded="false"]',
                        '.collapsed',
                        '.tree-node.collapsed',
                        '.nav-item.collapsed'
                    ];

                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (el.offsetParent !== null) {  // Check if visible
                                try {
                                    el.click();
                                    clicked++;
                                } catch (e) {
                                    // Ignore click errors
                                }
                            }
                        }
                    }
                    return clicked;
                }""")

                if expanded_js_count > 0:
                    logger.info(f"Expanded {expanded_js_count} items using JavaScript")
                    expanded_count += expanded_js_count
                    expanded_in_this_attempt += expanded_js_count
                    total_expanded += expanded_js_count
                    await page.wait_for_timeout(
                        1500
                    )  # Longer wait for expansions to complete
            except Exception as e:
                logger.debug(f"JavaScript expansion failed: {e}")

            # After an expansion iteration, do a complete scroll through
            logger.info(
                f"Completed expansion iteration {attempt} with {expanded_in_this_attempt} items expanded"
            )

            # No items expanded in this iteration and we're past halfway? Try a more aggressive approach
            if expanded_in_this_attempt == 0 and attempt > max_attempts // 2:
                logger.info(
                    "No items expanded in this attempt, trying more aggressive tactics"
                )

                # Try clicking any element that looks like it might be expandable
                try:
                    # Use a more generic selector for anything that might be clickable in a tree
                    click_count = await page.evaluate("""() => {
                        let clicked = 0;
                        // Target elements that might be part of a tree structure
                        const possibleItems = document.querySelectorAll('.tree-item, .tree-node, .nav-item, .toc-item, li.has-children, [role="treeitem"]');

                        for (const item of possibleItems) {
                            // Click the item itself and any icons/arrows within it
                            try {
                                item.click();
                                clicked++;

                                // Find and click any icon-like elements within
                                const icons = item.querySelectorAll('i, .icon, .arrow');
                                for (const icon of icons) {
                                    try {
                                        icon.click();
                                        clicked++;
                                    } catch(e) {}
                                }
                            } catch(e) {}
                        }
                        return clicked;
                    }""")

                    if click_count > 0:
                        logger.info(
                            f"Clicked {click_count} potentially expandable elements"
                        )
                        await page.wait_for_timeout(1500)
                except Exception as e:
                    logger.debug(f"Aggressive clicking failed: {e}")

            # Give up if nothing happened in last two attempts
            if attempt >= 3 and expanded_in_this_attempt == 0 and expanded_count == 0:
                logger.info(
                    "No progress in expansions for multiple attempts, may have reached limit"
                )
                break

            # Scroll through the entire content again to reveal any newly expanded items
            logger.info("Scrolling through content again to reveal new items...")
            await scroll_to_bottom(page, selector, max_scrolls=80)

            # Also try scrolling up from bottom in chunks to catch items that might have been missed
            await page.evaluate(f"""() => {{
                const element = document.querySelector('{selector} cdk-virtual-scroll-viewport') ||
                               document.querySelector('{selector}');
                if (element) {{
                    element.scrollTop = element.scrollHeight;  // Start at bottom
                }}
            }}""")

            # Scroll up in 5 steps
            for step in range(5):
                scroll_position = 1.0 - (step / 5)  # 0.8, 0.6, 0.4, 0.2, 0.0
                await page.evaluate(
                    f"""(scrollPercentage) => {{
                    const element = document.querySelector('{selector} cdk-virtual-scroll-viewport') ||
                                  document.querySelector('{selector}');
                    if (element) {{
                        element.scrollTop = scrollPercentage * element.scrollHeight;
                    }}
                }}""",
                    scroll_position,
                )
                await page.wait_for_timeout(800)  # Wait between scrolls

        logger.info(f"Expanded {total_expanded} navigation items in total")
        return total_expanded

    except Exception as e:
        logger.error(f"Error expanding items: {e}")
        return 0
