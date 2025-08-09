# this_file: src/d361/offline/d361_offline.py

import asyncio
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger
from playwright.async_api import Browser, BrowserContext

from .browser import setup_browser
from .config import Config
from .content import extract_page_content
from .navigation import extract_navigation
from .parser import parse_sitemap


class D361Offline:
    """Main Document360 offline documentation generator class."""

    def __init__(self, config: Config) -> None:
        """Initialize with configuration."""
        self.config = config
        self.output_dir = config.output_dir
        self.prep_file = self.output_dir / "prep.json"
        logger.info(f"Initialized D361Offline with output directory: {self.output_dir}")

    async def prep(self) -> dict[str, Any]:
        """Prepare for documentation generation by extracting sitemap and navigation."""
        logger.info("Starting preparation phase")

        # Parse sitemap to get URLs
        urls = await parse_sitemap(
            sitemap_url=str(self.config.map_url),
            test=self.config.test,
            pause=self.config.pause,
        )
        if not urls:
            msg = "No URLs found in sitemap"
            raise ValueError(msg)

        logger.info(f"Found {len(urls)} URLs in sitemap")

        # Extract navigation structure
        # Use non-headless mode for navigation extraction
        browser, context = await setup_browser(headless=False)
        nav_structure: dict[str, Any] = {"items": []}
        try:
            nav_url = (
                str(self.config.nav_url) if self.config.nav_url else next(iter(urls))
            )
            logger.info(f"Using navigation URL: {nav_url}")

            nav_structure = await extract_navigation(
                page=await context.new_page(),
                nav_url=nav_url,
                test=self.config.test,
            )

            if not nav_structure:
                logger.warning(
                    "Failed to extract navigation structure, using empty structure"
                )
                nav_structure = {"items": []}

            # Generate and save navigation files as mentioned in FIXME
            try:
                # Create output directory if it doesn't exist
                os.makedirs(self.output_dir, exist_ok=True)

                # Save nav.json
                nav_json_path = self.output_dir / "nav.json"
                with open(nav_json_path, "w") as f:
                    json.dump(nav_structure, f, indent=2)
                logger.info(f"Saved navigation structure to {nav_json_path}")

                # Generate nav.html - simple standalone version for viewing
                nav_html_path = self.output_dir / "nav.html"
                with open(nav_html_path, "w") as f:
                    nav_html = self._generate_nav_html(nav_structure)
                    f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Navigation</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        nav {{ max-width: 800px; margin: 0 auto; }}
        ul {{ list-style-type: none; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        a {{ text-decoration: none; color: #0366d6; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    {nav_html}
</body>
</html>""")
                logger.info(f"Saved navigation HTML to {nav_html_path}")

                # Generate nav.md
                nav_md_path = self.output_dir / "nav.md"
                with open(nav_md_path, "w") as f:
                    f.write("# Navigation\n\n")

                    def write_items(
                        items: list[dict[str, Any]], level: int = 0
                    ) -> None:
                        for item in items:
                            indent = "  " * level
                            title = item.get("title", "Untitled")
                            link = item.get("link", "")
                            if link:
                                f.write(f"{indent}- [{title}]({link})\n")
                            else:
                                f.write(f"{indent}- {title}\n")

                            children = item.get("children", [])
                            if children:
                                write_items(children, level + 1)

                    write_items(nav_structure.get("items", []))

                logger.info(f"Saved navigation markdown to {nav_md_path}")

            except Exception as e:
                logger.error(f"Error generating navigation files: {e}")

        finally:
            await browser.close()

        # Prepare state
        state: dict[str, Any] = {
            "config": self.config.model_dump(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "urls": list(urls),
            "navigation": nav_structure,
        }

        # Save state to prep file
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.prep_file, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Saved preparation state to {self.prep_file}")
        return state

    def _generate_nav_html(self, nav_structure: dict[str, Any]) -> str:
        """Generate HTML navigation from navigation structure.

        Args:
            nav_structure: Navigation structure dictionary

        Returns:
            HTML string representing the navigation
        """
        html = ["<nav><ul>"]

        def process_items(items: list[dict[str, Any]]) -> None:
            for item in items:
                title = item.get("title", "Untitled")
                link = item.get("link", "")
                children = item.get("children", [])

                html.append("<li>")
                if link:
                    html.append(f'<a href="{link}">{title}</a>')
                else:
                    html.append(f"<span>{title}</span>")

                if children:
                    html.append("<ul>")
                    process_items(children)
                    html.append("</ul>")

                html.append("</li>")

        process_items(nav_structure.get("items", []))
        html.append("</ul></nav>")

        return "".join(html)

    async def process_url(
        self, url: str, browser: Browser, context: BrowserContext
    ) -> dict[str, Any] | None:
        """Process a single URL: fetch content and save to file.

        Args:
            url: URL to process
            browser: Playwright browser instance
            context: Playwright browser context

        Returns:
            Dictionary with extracted content or None if failed
        """
        # Determine the slug and file paths first
        slug = self._get_slug(url)
        html_dir = self.output_dir / "html"
        md_dir = self.output_dir / "md"
        html_dir.mkdir(parents=True, exist_ok=True)
        md_dir.mkdir(parents=True, exist_ok=True)
        html_path = html_dir / f"{slug}.html"

        # Check if HTML file already exists
        if html_path.exists():
            logger.info(f"HTML file for {url} already exists, skipping fetch")

            try:
                # Read existing HTML file
                with open(html_path) as f:
                    html_content = f.read()

                # Extract title from HTML (simple regex approach)
                import re

                title_match = re.search(
                    r"<title>(.*?)</title>", html_content, re.DOTALL
                )
                title = title_match.group(1) if title_match else "Untitled"

                # Extract body content (simple approach)
                body_match = re.search(r"<body>(.*?)</body>", html_content, re.DOTALL)
                body_html = body_match.group(1) if body_match else ""

                # Create content dictionary from existing file
                if not body_html:
                    logger.warning(
                        f"Could not extract body from existing HTML for {url}, file may be corrupted"
                    )

                content = {
                    "title": title,
                    "html": body_html,
                    "markdown": None,  # We'll generate this later if needed
                }

                return content
            except Exception as e:
                logger.warning(
                    f"Error reading existing HTML file for {url}: {e}. Will re-fetch content."
                )
                # Continue with normal fetching process if reading the file fails

        # If HTML file doesn't exist, proceed with fetching
        retries = self.config.retries
        for attempt in range(1, retries + 2):  # +1 for initial attempt
            try:
                logger.info(f"Fetching content for {url} (attempt {attempt})")
                page = await context.new_page()

                # Navigate to the URL
                await page.goto(url, timeout=self.config.timeout * 1000)

                # Extract content
                content_from_page: dict[str, Any] | None = await extract_page_content(
                    page
                )

                if (
                    content_from_page
                    and content_from_page.get("title")
                    and content_from_page.get("html")
                ):
                    # Generate and save HTML file - using simplified version for now
                    with open(html_path, "w") as f:
                        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content_from_page.get("title", "Untitled")}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        img {{ max-width: 100%; height: auto; }}
        pre {{ background-color: #f6f8fa; padding: 16px; overflow: auto; }}
        code {{ font-family: monospace; }}
    </style>
</head>
<body>
    <h1>{content_from_page.get("title", "Untitled")}</h1>
    {content_from_page.get("html", "")}
    <hr>
    <footer>
        <p>Source: <a href="{url}">{url}</a></p>
    </footer>
</body>
</html>""")

                    # Generate and save Markdown file
                    with open(md_dir / f"{slug}.md", "w") as f:
                        f.write(f"""---
title: {content_from_page.get("title", "Untitled")}
url: {url}
---

{content_from_page.get("markdown", "")}
""")

                    logger.info(f"Successfully processed and saved {url}")
                    logger.info(f"  HTML: {html_path}")
                    logger.info(f"  Markdown: {md_dir / f'{slug}.md'}")

                    await page.close()
                    return content_from_page
                else:
                    logger.warning(
                        f"Failed to extract content from {url}: Empty content"
                    )

                await page.close()
                return None

            except Exception as e:
                logger.error(f"Error processing {url} (attempt {attempt}): {e}")
                if attempt < retries + 1:
                    delay = 2**attempt  # Exponential backoff
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)

        return None

    def _get_slug(self, url: str) -> str:
        """Generate a slug from a URL for use in filenames.

        Args:
            url: URL to generate slug from

        Returns:
            Slug string
        """
        # Extract the path from the URL and clean it
        from urllib.parse import urlparse

        parsed = urlparse(url)
        path = parsed.path.strip("/")

        # Remove common prefixes like 'docs/'
        if path.startswith("docs/"):
            path = path[5:]

        # If path is empty, use the hostname
        if not path:
            return parsed.netloc.replace(".", "-")

        # Convert to slug: replace slashes and special chars
        slug = path.replace("/", "-")
        slug = re.sub(r"[^a-zA-Z0-9-]", "", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")

        return slug

    async def fetch(self, prep_file: Path | None = None) -> dict[str, Any]:
        """Fetch content for all URLs in the prep file.

        Args:
            prep_file: Path to the prep file

        Returns:
            Dictionary with fetch state
        """
        logger.info("Starting fetch phase")

        # If prep_file is not specified, use the default
        prep_file = prep_file or self.prep_file

        # Check if the prep file exists
        if not prep_file.exists():
            msg = f"Prep file not found: {prep_file}"
            raise FileNotFoundError(msg)

        # Load the preparation state
        with open(prep_file) as f:
            prep_state = json.load(f)

        # Extract URLs from the state
        if "urls" not in prep_state:
            msg = "No URLs found in prep state"
            raise ValueError(msg)

        urls = prep_state["urls"]

        # Always get the complete navigation structure from prep.json, even when using cached content
        navigation = prep_state.get("navigation", {"items": []})

        # Log information about the navigation structure
        nav_items_count = len(navigation.get("items", []))
        logger.info(
            f"Loaded navigation structure from prep file with {nav_items_count} top-level items"
        )

        # If test mode is enabled, limit the number of URLs
        if self.config.test:
            urls = urls[:5]
            logger.info(f"Test mode enabled, limiting to {len(urls)} URLs")

        # Set up browser in headless mode for fetching
        logger.info("Setting up browser for fetching in headless mode")
        browser, context = await setup_browser(headless=True)

        try:
            # Prepare to store content
            content_map: dict[str, Any] = {}

            # Create a semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(self.config.max_concurrent)

            async def process_with_semaphore(url: str) -> None:
                """Process a URL with a semaphore to limit concurrency."""
                async with semaphore:
                    content = await self.process_url(url, browser, context)
                    if content:
                        content_map[url] = content

            # Process all URLs concurrently
            logger.info(
                f"Processing {len(urls)} URLs (max concurrency: {self.config.max_concurrent})"
            )
            tasks = [process_with_semaphore(url) for url in urls]
            await asyncio.gather(*tasks)

            logger.info(
                f"Fetch completed: Processed {len(content_map)} of {len(urls)} URLs"
            )

            # Prepare the fetch state to save
            fetch_state = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "config": self.config.model_dump(),
                "urls": list(content_map.keys()),
                "content": content_map,
                "navigation": navigation,  # Include the complete navigation structure for build phase
            }

            # Save the fetch state to a file
            fetch_file = self.output_dir / "fetch.json"
            with open(fetch_file, "w") as f:
                json.dump(fetch_state, f)

            logger.info(f"Saved fetch state to {fetch_file}")
            return fetch_state

        finally:
            await browser.close()

    async def build(self, fetch_file: Path | None = None) -> None:
        """Build HTML and Markdown output from fetched content.

        Args:
            fetch_file: Path to the fetch file
        """
        logger.info("Starting build phase")

        # If fetch_file is not specified, use the default location
        fetch_file = fetch_file or (self.output_dir / "fetch.json")

        # Check if the fetch file exists
        if not fetch_file.exists():
            msg = f"Fetch file not found: {fetch_file}"
            raise FileNotFoundError(msg)

        # Load the fetch state
        with open(fetch_file) as f:
            fetch_state = json.load(f)

        # Extract content and navigation from the state
        content_map = fetch_state.get("content", {})
        navigation = fetch_state.get("navigation", {"items": []})

        if not content_map:
            logger.warning("No content found in fetch state")
            return

        # Create output directories
        html_dir = self.output_dir / "html"
        md_dir = self.output_dir / "md"
        html_dir.mkdir(parents=True, exist_ok=True)
        md_dir.mkdir(parents=True, exist_ok=True)

        # Copy CSS file if specified
        css_path = None
        if self.config.css_file and Path(self.config.css_file).exists():
            css_filename = os.path.basename(self.config.css_file)
            css_path = html_dir / css_filename
            shutil.copy(self.config.css_file, css_path)
            logger.info(f"Copied CSS file to {css_path}")

        # Regenerate individual files if needed
        generated_count = 0
        for url, content in content_map.items():
            try:
                # Skip if content is missing required fields
                if not content or not content.get("title") or not content.get("html"):
                    logger.warning(f"Skipping {url}: Missing required content")
                    continue

                # Individual files are already generated during fetch phase
                generated_count += 1
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")

        # Generate combined files with navigation structure integration
        await self._generate_combined_files(content_map, navigation, css_path)

        logger.info(f"Build completed: Processed {generated_count} URLs")
        logger.info(f"Output directory: {self.output_dir}")

    async def _generate_combined_files(
        self,
        content_map: dict[str, Any],
        navigation: dict[str, Any],
        css_path: Path | None = None,
    ) -> None:
        """
        Generate combined HTML and Markdown files from individual files.
        """
        logger.info("Generating combined files...")

        # Get URL to slug mapping for quick lookup
        url_to_slug = {url: self._get_slug(url) for url in content_map.keys()}
        if not url_to_slug:
            logger.warning(
                "No URL to slug mapping found. Cannot generate combined files."
            )
            return

        # Create reverse mapping - slug to URL
        {slug: url for url, slug in url_to_slug.items() if slug is not None}

        # Debug: Check a few URLs and their slugs
        sample_urls = list(url_to_slug.keys())[:5]
        logger.debug(
            f"Sample URLs and their slugs: {[(url, url_to_slug[url]) for url in sample_urls]}"
        )

        # Extract ordered URLs from nav structure
        ordered_urls = []

        def extract_urls_from_nav(items: list[dict[str, Any]]) -> None:
            for item in items:
                link = item.get("link", "")
                if link and link in content_map and link not in ordered_urls:
                    ordered_urls.append(link)

                # Process child items recursively
                children = item.get("children", [])
                if children:
                    extract_urls_from_nav(children)

        extract_urls_from_nav(navigation.get("items", []))
        logger.debug(f"Found {len(ordered_urls)} ordered URLs from navigation")

        # If navigation doesn't contain enough URLs, use all URLs from content_map
        if (
            len(ordered_urls) < len(content_map) * 0.5
        ):  # If less than 50% of URLs are in navigation
            logger.warning(
                f"Navigation only contains {len(ordered_urls)} URLs out of {len(content_map)}. Using all URLs from fetch.json."
            )
            # Add remaining URLs that weren't in the navigation, preserving the order from fetch.json
            remaining_urls = [
                url for url in content_map.keys() if url not in ordered_urls
            ]
            # Don't sort, preserve the original order from fetch.json
            ordered_urls.extend(remaining_urls)

            logger.debug(f"Final ordered URLs count: {len(ordered_urls)}")

        # Create combined HTML file with navigation
        combined_html_path = self.output_dir / "all_docs.html"
        combined_md_path = self.output_dir / "all_docs.md"

        # Look for .md files in md_dir
        md_files = []
        try:
            md_dir = self.output_dir / "md"
            if md_dir.exists() and md_dir.is_dir():
                logger.debug(f"Looking for Markdown files in {md_dir}")
                md_files = list(md_dir.glob("*.md"))
                logger.debug(f"Found {len(md_files)} Markdown files")
                if md_files and len(md_files) > 0:
                    logger.debug(f"Sample md files: {[f.name for f in md_files[:5]]}")
        except Exception as e:
            logger.error(f"Error finding Markdown files: {e}")

        # Create a map of slug to Markdown file path
        slug_to_md_file = {}
        for md_file in md_files:
            slug = md_file.stem
            slug_to_md_file[slug] = md_file

        logger.debug(
            f"Created mapping of {len(slug_to_md_file)} slugs to Markdown files"
        )

        # Debug: Check if slugs from URLs match the Markdown files
        matches = 0
        for _url, slug in url_to_slug.items():
            if slug in slug_to_md_file:
                matches += 1

        logger.debug(f"Found {matches} matches between URL slugs and Markdown files")

        # Debug: Check a few slugs from URL and if they exist in Markdown files
        sample_slugs = [url_to_slug[url] for url in sample_urls]
        for slug in sample_slugs:
            logger.debug(f"Slug {slug} exists in md files: {slug in slug_to_md_file}")

        # Generate HTML
        with open(combined_html_path, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n")
            f.write('<meta charset="UTF-8">\n')
            f.write(
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            )
            f.write("<title>Document360 Documentation</title>\n")

            # Include the CSS if specified
            if css_path and css_path.exists():
                with open(css_path, encoding="utf-8") as css_file:
                    f.write("<style>\n")
                    f.write(css_file.read())
                    f.write("\n</style>\n")

            f.write("</head>\n<body>\n")

            # Add navigation menu
            f.write('<div class="navigation">\n<ul>\n')
            for url in ordered_urls:
                if url in content_map and "title" in content_map[url]:
                    title = content_map[url]["title"]
                    slug = url_to_slug.get(url, "")
                    if slug:
                        f.write(f'<li><a href="#{slug}">{title}</a></li>\n')
            f.write("</ul>\n</div>\n")

            # Add content
            f.write('<div class="content">\n')
            for _idx, ordered_url in enumerate(ordered_urls):
                if ordered_url in content_map and "html" in content_map[ordered_url]:
                    title = content_map[ordered_url]["title"]
                    html = content_map[ordered_url]["html"]
                    slug = url_to_slug.get(ordered_url, "")
                    if slug:
                        f.write(f'<div class="section" id="{slug}">\n')
                        f.write(f"<h1>{title}</h1>\n")
                        f.write(f'<div class="article-content">\n{html}\n</div>\n')
                        f.write("</div>\n")
            f.write("</div>\n")

            f.write("</body>\n</html>\n")

        # Generate Markdown
        with open(combined_md_path, "w", encoding="utf-8") as f:
            f.write("# Combined Documentation\n\n")

            # Generate table of contents
            f.write("## Table of Contents\n\n")
            for url in ordered_urls:
                slug = url_to_slug.get(url, "")
                if slug in slug_to_md_file:
                    title = ""
                    # Try to extract title from frontmatter
                    try:
                        md_content = slug_to_md_file[slug].read_text(encoding="utf-8")
                        if md_content.startswith("---"):
                            # Extract frontmatter
                            frontmatter_end = md_content.find("---", 3)
                            if frontmatter_end != -1:
                                frontmatter = md_content[3:frontmatter_end].strip()
                                for line in frontmatter.split("\n"):
                                    if line.startswith("title:"):
                                        title = line[6:].strip()
                                        break
                    except Exception as e:
                        logger.warning(f"Error reading title from {slug}: {e}")

                    if not title and url in content_map and "title" in content_map[url]:
                        title = content_map[url]["title"]

                    if title:
                        f.write(f"- [{title}](#{slug})\n")

            f.write("\n---\n\n")

            # Add content from Markdown files
            md_count = 0
            for url in ordered_urls:
                slug = url_to_slug.get(url, "")
                if slug in slug_to_md_file:
                    try:
                        md_file = slug_to_md_file[slug]
                        md_content = md_file.read_text(encoding="utf-8")

                        # Extract frontmatter and title
                        title = ""
                        content = md_content
                        if md_content.startswith("---"):
                            frontmatter_end = md_content.find("---", 3)
                            if frontmatter_end != -1:
                                frontmatter = md_content[3:frontmatter_end].strip()
                                for line in frontmatter.split("\n"):
                                    if line.startswith("title:"):
                                        title = line[6:].strip()
                                        break
                                content = md_content[frontmatter_end + 3 :].strip()

                        if (
                            not title
                            and url in content_map
                            and "title" in content_map[url]
                        ):
                            title = content_map[url]["title"]

                        # Write the section with anchor
                        f.write(f'<a id="{slug}"></a>\n\n')
                        f.write(f"## {title}\n\n")
                        f.write(f"{content}\n\n")
                        md_count += 1
                    except Exception as e:
                        logger.warning(
                            f"Error processing Markdown file for {slug}: {e}"
                        )

            logger.info(f"Added {md_count} Markdown files to the combined document")

        logger.info(f"Generated combined HTML file: {combined_html_path}")
        logger.info(
            f"Generated combined Markdown file from individual md files: {combined_md_path}"
        )

    def _extract_ordered_urls_from_nav(
        self, navigation: dict[str, Any], content_map: dict[str, Any]
    ) -> list[str]:
        """
        Extract ordered URLs from navigation structure.

        Args:
            navigation: Navigation structure dictionary
            content_map: Dictionary mapping URLs to content

        Returns:
            List of ordered URLs
        """
        ordered_urls = []

        def extract_urls_from_nav(items: list[dict[str, Any]]) -> None:
            for item in items:
                link = item.get("link", "")
                if link and link in content_map and link not in ordered_urls:
                    ordered_urls.append(link)

                # Process child items recursively
                children = item.get("children", [])
                if children:
                    extract_urls_from_nav(children)

        extract_urls_from_nav(navigation.get("items", []))

        return ordered_urls

    async def all(self, prep_file: Path | None = None) -> None:
        """Run the entire process: prep, fetch, and build."""
        logger.info("Starting all phases: prep, fetch, build")

        # Run prep phase
        await self.prep()

        # Run fetch phase
        await self.fetch(self.prep_file)

        # Run build phase
        await self.build(self.output_dir / "fetch.json")

        logger.info("All phases completed successfully")
        logger.info(f"Output directory: {self.output_dir}")
