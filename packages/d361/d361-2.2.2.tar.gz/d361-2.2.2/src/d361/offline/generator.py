# this_file: src/d361/offline/generator.py

import os
import shutil
from pathlib import Path
from typing import Any

import aiofiles
from loguru import logger
from markdownify import markdownify


async def create_output_directory(
    output_dir: Path, css_file: Path | None = None
) -> None:
    """Create output directory structure and copy assets."""
    try:
        # Create main output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")

        # Create subdirectories
        md_dir = output_dir / "md"
        html_dir = output_dir / "html"
        assets_dir = html_dir / "assets"

        for directory in [md_dir, html_dir, assets_dir]:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

        # Copy CSS file if provided
        if css_file and css_file.exists():
            shutil.copy(css_file, assets_dir / css_file.name)
            logger.info(f"Copied CSS file to: {assets_dir / css_file.name}")

        # Create default CSS if not provided
        else:
            default_css = assets_dir / "style.css"
            async with aiofiles.open(default_css, "w") as f:
                await f.write("""
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }
                .container { max-width: 800px; margin: 0 auto; }
                nav { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                nav ul { list-style-type: none; padding-left: 15px; }
                h1 { color: #2c3e50; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
                """)
            logger.info(f"Created default CSS file: {default_css}")

    except Exception as e:
        logger.error(f"Error creating output directory structure: {e}")
        raise


async def generate_html_file(
    url: str,
    content: dict[str, str],
    output_dir: Path,
    nav_html: str,
    css_filename: str,
) -> Path:
    """Generate HTML file for a page."""
    try:
        html_dir = output_dir / "html"
        os.makedirs(html_dir, exist_ok=True)

        # Create safe filename from URL
        filename = url.split("/")[-1].replace(".html", "") or "index"
        filename = "".join(
            c if c.isalnum() or c in ["-", "_"] else "_" for c in filename
        )
        html_path = html_dir / f"{filename}.html"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.get("title", "Untitled")}</title>
    <link rel="stylesheet" href="assets/{css_filename}">
</head>
<body>
    <div class="container">
        <nav>{nav_html}</nav>
        <main>
            <h1>{content.get("title", "Untitled")}</h1>
            {content.get("content", "<p>No content available</p>")}
        </main>
    </div>
</body>
</html>"""

        async with aiofiles.open(html_path, "w") as f:
            await f.write(html_content)

        logger.info(f"Generated HTML file: {html_path}")
        return html_path

    except Exception as e:
        logger.error(f"Error generating HTML file for {url}: {e}")
        raise


async def generate_markdown_file(
    url: str, content: dict[str, str], output_dir: Path
) -> Path:
    """Generate Markdown file for a page."""
    try:
        md_dir = output_dir / "md"
        os.makedirs(md_dir, exist_ok=True)

        # Create safe filename from URL
        filename = url.split("/")[-1].replace(".html", "") or "index"
        filename = "".join(
            c if c.isalnum() or c in ["-", "_"] else "_" for c in filename
        )
        md_path = md_dir / f"{filename}.md"

        # Convert HTML to Markdown
        title = content.get("title", "Untitled")
        html_content = content.get("content", "<p>No content available</p>")
        markdown_content = markdownify(html_content)

        frontmatter = f"""---
title: "{title}"
url: "{url}"
---

# {title}

"""

        async with aiofiles.open(md_path, "w") as f:
            await f.write(frontmatter + markdown_content)

        logger.info(f"Generated Markdown file: {md_path}")
        return md_path

    except Exception as e:
        logger.error(f"Error generating Markdown file for {url}: {e}")
        raise


def generate_navigation_html(nav_structure: dict[str, Any]) -> str:
    """Generate HTML representation of the navigation structure.

    Args:
        nav_structure: A dictionary containing the navigation structure
            with 'items' key containing a list of navigation items.

    Returns:
        HTML representation of the navigation structure as a string.
    """
    html = ["<nav>", "<ul>"]

    def render_items(items: list[dict[str, Any]]) -> None:
        for item in items:
            title = item.get("title", "Untitled")
            link = item.get("link", "")

            html.append("<li>")
            if link:
                html.append(f'<a href="{link}">{title}</a>')
            else:
                html.append(f"<span>{title}</span>")

            children = item.get("children", [])
            if children:
                html.append("<ul>")
                render_items(children)
                html.append("</ul>")

            html.append("</li>")

    render_items(nav_structure.get("items", []))
    html.extend(["</ul>", "</nav>"])

    return "\n".join(html)
