#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["rich"]
# ///
# this_file: d361/docs/d364.py

"""
Process d364.md Markdown file to split it into records at H3 headings,
split headings into higher/lower parts, and insert H2 headings when heading_higher changes.
Outputs to d365.md.
"""

import re
from pathlib import Path
from rich import print
from typing import NamedTuple, List
from dataclasses import dataclass


@dataclass
class MarkdownSection:
    heading_higher: str
    heading_lower: str
    content: str
    is_h2: bool = False


def split_heading(heading: str) -> tuple[str, str]:
    """Split a heading into higher and lower parts on ':' character."""
    # Remove the ### prefix and any whitespace
    clean_heading = heading.lstrip("#").strip()

    if ":" in clean_heading:
        higher, lower = clean_heading.split(":", 1)
        return higher.strip(), lower.strip()
    return clean_heading, ""


def process_markdown(content: str) -> List[MarkdownSection]:
    """Process markdown content and split into sections at H3 headings."""
    # Split the content at H3 headings
    sections = []
    current_content: list[str] = []
    current_higher = None

    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("### "):
            # If we have accumulated content, save it
            if current_content:
                sections.append(
                    MarkdownSection(
                        heading_higher="",
                        heading_lower="",
                        content="\n".join(current_content).strip(),
                    )
                )
                current_content = []

            # Process the new heading
            higher, lower = split_heading(line)
            if current_higher != higher:
                # Add an H2 section when heading_higher changes
                if higher:
                    sections.append(
                        MarkdownSection(
                            heading_higher=higher,
                            heading_lower="",
                            content="",
                            is_h2=True,
                        )
                    )
                current_higher = higher

            # Start a new section
            sections.append(
                MarkdownSection(
                    heading_higher=higher, heading_lower=lower, content="", is_h2=False
                )
            )
        else:
            current_content.append(line)
        i += 1

    # Add any remaining content
    if current_content:
        sections.append(
            MarkdownSection(
                heading_higher="",
                heading_lower="",
                content="\n".join(current_content).strip(),
            )
        )

    return sections


def generate_output(sections: List[MarkdownSection]) -> str:
    """Generate the output markdown content from the sections."""
    output = []

    for section in sections:
        if section.is_h2:
            output.append(f"## {section.heading_higher}")
        elif section.heading_higher and section.heading_lower:
            output.append(f"### {section.heading_higher}: {section.heading_lower}")
        elif section.heading_higher:
            output.append(f"### {section.heading_higher}")

        if section.content:
            output.append(section.content)

        output.append("")  # Add blank line between sections

    return "\n".join(output)


def main():
    """Main function to process the markdown file."""
    docs_dir = Path(__file__).parent
    input_file = docs_dir / "d364.md"
    output_file = docs_dir / "d365.md"

    print(f"[bold blue]Reading from[/bold blue]: {input_file}")
    content = input_file.read_text(encoding="utf-8")

    print("[bold green]Processing markdown content...[/bold green]")
    sections = process_markdown(content)

    print("[bold green]Generating output...[/bold green]")
    output_content = generate_output(sections)

    print(f"[bold blue]Writing to[/bold blue]: {output_file}")
    output_file.write_text(output_content, encoding="utf-8")

    print("[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
