import json
from urllib.parse import urljoin

import fire
from playwright.sync_api import sync_playwright

# Base URL for constructing absolute links
BASE_URL = "https://docs.document360.com"


def scroll_to_bottom(page, tree_view) -> None:
    """Scroll the tree view to the bottom to load all virtual scroll items."""
    page.evaluate(
        """
        (element) => {
            const viewport = element.querySelector('cdk-virtual-scroll-viewport');
            if (viewport) {
                viewport.scrollTop = viewport.scrollHeight;
            }
        }
    """,
        tree_view,
    )
    page.wait_for_timeout(1000)  # Wait for content to load


def expand_all_items(page, tree_view) -> None:
    """Recursively expand all items by clicking collapsed triangle icons."""
    while True:
        # Scroll to the bottom to ensure all items are loaded
        scroll_to_bottom(page, tree_view)

        # Re-query the DOM for collapsed icons each iteration
        collapsed_icons = tree_view.query_selector_all(".tree-arrow .fa-angle-right")
        if not collapsed_icons:
            break  # Exit when no more collapsed icons are found

        # Process each icon with error handling
        for icon in collapsed_icons:
            try:
                # Ensure the icon is in view and clickable
                icon.scroll_into_view_if_needed()
                icon.click()
                # Wait for the DOM to update after the click
                page.wait_for_timeout(1000)  # Increased to 1 second for stability
            except Exception:
                continue  # Skip to the next icon if an error occurs


def scroll_to_bottom(page, tree_view) -> None:
    """Scroll incrementally to load all virtual scroll items."""
    viewport = tree_view.query_selector("cdk-virtual-scroll-viewport") or tree_view
    scroll_height = page.evaluate("element => element.scrollHeight", viewport)
    client_height = page.evaluate("element => element.clientHeight", viewport)
    scroll_top = page.evaluate("element => element.scrollTop", viewport)

    while scroll_top + client_height < scroll_height:
        page.evaluate("element => element.scrollTop += element.clientHeight", viewport)
        page.wait_for_timeout(1000)  # Wait for content to load
        scroll_top = page.evaluate("element => element.scrollTop", viewport)
        scroll_height = page.evaluate("element => element.scrollHeight", viewport)


def extract_tree(tree_view):
    """Extract the hierarchical tree structure from the tree view."""
    nodes = tree_view.query_selector_all(".tree-wrapper")
    root = {"title": "Root", "link": None, "children": []}
    stack = [root]
    previous_level = -1

    for node in nodes:
        # Determine hierarchy level by counting filler divs
        fillers = node.query_selector_all(".filler")
        level = len(fillers)

        # Adjust stack to find the correct parent based on level
        while level <= previous_level:
            stack.pop()
            previous_level -= 1

        parent = stack[-1]

        # Extract title and link
        title_element = node.query_selector(".data-title")
        title = title_element.inner_text().strip() if title_element else "Untitled"
        href = title_element.get_attribute("href") if title_element else None
        link = urljoin(BASE_URL, href) if href else None

        # Create new node and add to parent's children
        new_node = {"title": title, "link": link, "children": []}
        parent["children"].append(new_node)
        stack.append(new_node)
        previous_level = level

    return root["children"]


def generate_markdown(tree, filepath) -> None:
    """Generate a Markdown file with a hierarchical list of links."""

    def build_md(node, level=0):
        indent = "  " * level
        lines = []
        title = node["title"]
        link = node["link"]
        if link:
            lines.append(f"{indent}- [{title}]({link})")
        else:
            lines.append(f"{indent}- {title}")
        for child in node["children"]:
            lines.extend(build_md(child, level + 1))
        return lines

    with open(filepath, "w", encoding="utf-8") as f:
        lines = []
        for node in tree:
            lines.extend(build_md(node))
        f.write("\n".join(lines))


def generate_html(tree, filepath) -> None:
    """Generate a static HTML file with a nested list of links."""

    def build_html(node):
        lines = ["<ul>"]
        title = node["title"]
        link = node["link"]
        if link:
            lines.append(f'  <li><a href="{link}">{title}</a>')
        else:
            lines.append(f"  <li>{title}")

        if node["children"]:
            for child in node["children"]:
                lines.append(build_html(child))
            lines.append("  </li>")
        else:
            lines.append("</li>")
        lines.append("</ul>")
        return "\n".join(lines[1:-1])

    with open(filepath, "w", encoding="utf-8") as f:
        html_content = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="UTF-8">',
            "  <title>Document360 Navigation Tree</title>",
            "</head>",
            "<body>",
            "<h1>Navigation Tree</h1>",
        ]
        for node in tree:
            html_content.append(build_html(node))
        html_content.extend(["</body>", "</html>"])
        f.write("\n".join(html_content))


def generate_json(tree, filepath) -> None:
    """Generate a JSON file representing the tree hierarchy."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)


def main(md_file="nav.md", html_file="nav.html", json_file="nav.json") -> None:
    """Main function to run the CLI tool."""
    with sync_playwright() as p:
        # Launch browser and navigate to the page
        browser = p.chromium.launch(headless=False)  # Set headless=True for no UI
        page = browser.new_page()
        page.goto("https://docs.document360.com/docs/")
        page.wait_for_load_state("networkidle")

        # Locate the tree view element
        tree_selector = "#left-panel > div.catergory-list > site-category-list-tree-view > d360-data-list-tree-view"
        tree_view = page.query_selector(tree_selector)
        if not tree_view:
            msg = f"Tree view element not found with selector: {tree_selector}"
            raise Exception(msg)

        # Expand all items and gather the tree structure
        expand_all_items(page, tree_view)
        tree = extract_tree(tree_view)

        # Generate output files
        generate_markdown(tree, md_file)
        generate_html(tree, html_file)
        generate_json(tree, json_file)

        # Clean up
        browser.close()


if __name__ == "__main__":
    fire.Fire(main)
