#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich", "llm", "tenacity", "asyncio", "llm-openrouter"]
# ///
# this_file: d361/docs/summarize.py

from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any

from fire import Fire
from rich.console import Console  # type: ignore
from rich.progress import Progress, SpinnerColumn, TextColumn  # type: ignore
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import llm  # type: ignore

console = Console()


class LLMError(Exception):
    """Base exception class for LLM errors"""


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def _try_model(
    prompt: str, model_id: str, attachments: list[llm.Attachment] | None = None
) -> str:
    """Try a single model with retry logic"""
    model = llm.get_model(model_id)
    response = model.prompt(prompt, attachments=attachments)
    return str(response)


DEFAULT_FALLBACK_MODELS = [
    "openrouter/google/gemini-2.0-pro-exp-02-05:free",
    "openrouter/deepseek/deepseek-r1-zero:free",
    "openrouter/deepseek/deepseek-r1-distill-qwen-32b:free",
    "openrouter/deepseek/deepseek-r1-distill-llama-70b:free",
    "openrouter/google/gemini-flash-1.5-8b-exp",
    "openrouter/google/gemini-2.0-flash-exp:free",
    "openrouter/anthropic/claude-3-haiku",  # Not free but good quality
    "openrouter/openai/gpt-4o-mini",  # Not free but good quality
]


def ask(
    prompt: str,
    data: str | None = None,
    model_ids: list[str] | None = None,
) -> str:
    """
    Send a prompt to LLM with fallback models.

    Args:
        prompt: The text prompt to send
        data: Optional input data to include in the prompt
        model_ids: List of model IDs to try in order (falls back through the list)

    Returns:
        String response from the LLM

    Raises:
        LLMError: If all models fail
    """
    if data:
        prompt = (
            prompt.replace("$input", data)
            if "$input" in prompt
            else f"{prompt}:\n\n<input>{data}</input>"
        )
    models_to_try = model_ids if model_ids else DEFAULT_FALLBACK_MODELS

    # Try each model in sequence
    last_error = None
    for model_id in models_to_try:
        try:
            return _try_model(prompt, model_id, None)
        except Exception as e:
            last_error = e
            continue

    msg = f"All models failed. Last error: {last_error!s}"
    raise LLMError(msg)


def split_markdown_at_h2(content: str) -> list[dict[str, str]]:
    """
    Split a markdown file at H2 headings.

    Args:
        content: The markdown content as a string

    Returns:
        List of dictionaries with 'heading', 'text', and empty 'summary' fields
    """
    # Pattern to match H2 headings (## Heading)
    h2_pattern = re.compile(r"^## (.+)$", re.MULTILINE)

    # Find all H2 headings and their positions
    headings = [(m.group(1), m.start()) for m in h2_pattern.finditer(content)]

    if not headings:
        # If no H2 headings found, return the entire content as one section
        return [{"heading": "Document", "text": content, "summary": ""}]

    # Extract sections
    sections = []
    for i, (heading, pos) in enumerate(headings):
        # Section content goes from current heading position to next heading position
        # or end of file for the last heading
        start_pos = pos
        end_pos = headings[i + 1][1] if i < len(headings) - 1 else len(content)
        section_content = content[start_pos:end_pos].strip()
        sections.append({"heading": heading, "text": section_content, "summary": ""})

    return sections


def clean_llm_output(text: str) -> str:
    """
    Clean LLM output by extracting content between <output> and </output> tags.
    Also handles <o> and </o> tags for backward compatibility.
    If tags are not found, returns the original text.

    Args:
        text: The text to clean

    Returns:
        Cleaned text with only the content between output tags, or original text if tags not found
    """
    # First try <output> tags
    output_tag_start = "<output>"
    output_tag_end = "</output>"
    start_idx = text.find(output_tag_start)

    if start_idx >= 0:
        content_start = start_idx + len(output_tag_start)
        end_idx = text.find(output_tag_end, content_start)
        if end_idx >= 0:
            return text[content_start:end_idx].strip()

    # Fallback to <o> tags
    o_tag_start = "<o>"
    o_tag_end = "</o>"
    start_idx = text.find(o_tag_start)

    if start_idx >= 0:
        content_start = start_idx + len(o_tag_start)
        end_idx = text.find(o_tag_end, content_start)
        if end_idx >= 0:
            return text[content_start:end_idx].strip()

    # If no tags found, return original text
    return text.strip()


def summarize_section(
    heading: str, content: str, model_ids: list[str] | None = None
) -> str:
    """
    Summarize a section of markdown content using LLM.

    Args:
        heading: The section heading
        content: The section content
        model_ids: Optional list of model IDs to try

    Returns:
        Summarized content
    """
    prompt = f"""Open the tag <thinking>, print your reasoning, then close the tag </thinking>. Open the tag <output>, print the markdown heading `## {heading}` and then print an entity-dense TLDR of this document, keep key information, make it concise. Close the tag </output>. 

    $input"""

    try:
        response = ask(prompt, content, model_ids)
        return clean_llm_output(response)
    except LLMError as e:
        console.print(
            f"[bold red]Error summarizing section '{heading}': {e}[/bold red]"
        )
        return f"## {heading}\n\n*Error: Failed to summarize this section.*\n\n"


def load_markdown(
    input_file: str | Path,
    output_file: str | Path | None = None,
    *,
    verbose: bool = False,
) -> None:
    """
    Load a markdown file, split it at H2 headings, and save as JSON.

    Args:
        input_file: Path to the input markdown file
        output_file: Path to the output JSON file (defaults to input_file with .json suffix)
        verbose: Whether to print verbose output
    """
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(
            f"[bold red]Error: Input file '{input_file}' not found.[/bold red]"
        )
        sys.exit(1)

    if output_file is None:
        output_path = input_path.with_suffix(".json")
    else:
        output_path = Path(output_file)

    # Read input file
    console.print(f"Reading file: [bold]{input_path}[/bold]")
    content = input_path.read_text(encoding="utf-8")

    # Split content at H2 headings
    sections = split_markdown_at_h2(content)
    console.print(f"Found [bold]{len(sections)}[/bold] sections")

    # Save to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)

    console.print(f"\n[bold green]Sections saved to: {output_path}[/bold green]")


async def process_section_async(
    section: dict[str, Any], model: str | None = None, force: bool = False
) -> tuple[dict[str, Any], str | None, str | None]:
    """
    Process a single section asynchronously, returning the updated section, any error message, and the model used.

    Args:
        section: The section to process
        model: Optional specific LLM model to use
        force: Whether to reprocess if summary exists

    Returns:
        Tuple of (processed section, error message if any, model used if successful)
    """
    if section.get("summary") and not force:
        return section, None, None

    prompt_text = f"""Open the tag <thinking>, print your reasoning, then close the tag </thinking>. Open the tag <output>, print the markdown heading `## {section["heading"]}` and then print an entity-dense TLDR of this document, keep key information, make it concise. Close the tag </output>. 

{section["text"]}"""

    # If a specific model is provided, use it
    if model:
        try:
            async_model = llm.get_async_model(model)
            response = await async_model.prompt(prompt_text)
            summary = clean_llm_output(await response.text())
            section["summary"] = summary
            return section, None, model
        except Exception as e:
            return section, str(e), None

    # Otherwise, try each model in the fallback list
    last_error = None
    for model_id in DEFAULT_FALLBACK_MODELS:
        try:
            async_model = llm.get_async_model(model_id)
            response = await async_model.prompt(prompt_text)
            summary = clean_llm_output(await response.text())
            section["summary"] = summary
            return section, None, model_id
        except Exception as e:
            last_error = e
            continue

    # If all models failed, return the error
    return section, f"All models failed. Last error: {last_error!s}", None


async def process_sections_async(
    input_file: str | Path,
    output_file: str | Path | None = None,
    model: str | None = None,
    *,
    verbose: bool = False,
    force: bool = False,
    concurrency: int = 3,
) -> None:
    """
    Process JSON file with sections and summarize each section asynchronously.

    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output JSON file (defaults to input_file)
        model: Optional specific LLM model to use
        verbose: Whether to print verbose output
        force: Whether to reprocess sections that already have summaries
        concurrency: Maximum number of concurrent tasks
    """
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(
            f"[bold red]Error: Input file '{input_file}' not found.[/bold red]"
        )
        sys.exit(1)

    # Determine output path
    output_path = Path(output_file) if output_file else input_path

    # Read JSON file
    console.print(f"Reading sections from: [bold]{input_path}[/bold]")
    with open(input_path, encoding="utf-8") as f:
        sections = json.load(f)

    # Make a copy of the original sections to preserve them
    original_sections = sections.copy()

    # Count sections that need processing
    sections_to_process = sum(
        1 for section in sections if not section.get("summary") or force
    )
    if sections_to_process == 0:
        console.print(
            "[yellow]No sections need processing. Use --force to reprocess all sections.[/yellow]"
        )
        return

    # Determine which model to use
    model_to_use = model if model else "Using fallback models"
    console.print(f"Using model: [bold cyan]{model_to_use}[/bold cyan]")
    if not model:
        console.print(
            "[yellow]No specific model provided, will try these models in order:[/yellow]"
        )
        for fallback_model in DEFAULT_FALLBACK_MODELS:
            console.print(f"  - {fallback_model}")

    # List available models if verbose
    if verbose:
        console.print("[bold]Available models:[/bold]")
        for available_model in llm.get_async_models():
            console.print(f"  - {available_model.model_id}")

    console.print(f"Found [bold]{sections_to_process}[/bold] sections to process")
    if force:
        console.print("[yellow]Force mode enabled - reprocessing all sections[/yellow]")

    # Process sections with async
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task_id = progress.add_task("Processing sections", total=sections_to_process)

        # Process sections with limited concurrency
        semaphore = asyncio.Semaphore(concurrency)
        results = []
        successful_models = {}

        async def process_with_semaphore(section: dict[str, Any], idx: int) -> None:
            async with semaphore:
                # Create a copy of the section to process
                section_copy = section.copy()
                processed_section, error, model_used = await process_section_async(
                    section_copy, model, force
                )

                # Add the processed section to results
                results.append(processed_section)

                # Track which model was successful
                if not error and model_used:
                    successful_models[section["heading"]] = model_used

                if error:
                    console.print(
                        f"[bold red]Error processing section '{section['heading']}': {error}[/bold red]"
                    )
                    if verbose:
                        console.print(
                            "[yellow]Continuing with next section...[/yellow]"
                        )
                elif verbose:
                    model_info = f" using [cyan]{successful_models.get(section['heading'], model or 'unknown model')}[/cyan]"
                    console.print(
                        f"[green]✓[/green] Completed section {idx + 1}/{len(sections)}: [bold]{section['heading']}[/bold]{model_info}"
                    )

                # Save progress after each section
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)

                progress.update(task_id, advance=1)
                progress.update(
                    task_id, description=f"Processed: {len(results)}/{len(sections)}"
                )

        # Create tasks for all sections
        tasks = [
            process_with_semaphore(section, i) for i, section in enumerate(sections)
        ]

        # Run all tasks
        await asyncio.gather(*tasks)

    # Ensure we have all sections in the output
    if len(results) != len(original_sections):
        console.print(
            f"[bold yellow]Warning: Processed {len(results)} sections but original had {len(original_sections)} sections.[/bold yellow]"
        )
        console.print("[yellow]Restoring any missing sections...[/yellow]")

        # Create a map of headings to processed sections
        processed_headings = {section["heading"]: section for section in results}

        # Ensure all original sections are included
        final_results = []
        for original_section in original_sections:
            heading = original_section["heading"]
            if heading in processed_headings:
                final_results.append(processed_headings[heading])
            else:
                console.print(
                    f"[yellow]Restoring unprocessed section: {heading}[/yellow]"
                )
                final_results.append(original_section)

        # Save the final results
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False)

        console.print(
            f"[green]Restored all sections. Final count: {len(final_results)}[/green]"
        )

    if output_file:
        console.print(
            f"\n[bold green]All sections processed and saved to: {output_path}[/bold green]"
        )
    else:
        console.print(
            f"\n[bold green]All sections processed and saved to: {input_path}[/bold green]"
        )


def process_sections(
    input_file: str | Path,
    output_file: str | Path | None = None,
    model: str | None = None,
    *,
    verbose: bool = False,
    force: bool = False,
    concurrency: int = 3,
) -> None:
    """
    Process JSON file with sections and summarize each section.

    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output JSON file (defaults to input_file)
        model: Optional specific LLM model to use
        verbose: Whether to print verbose output
        force: Whether to reprocess sections that already have summaries
        concurrency: Maximum number of concurrent tasks
    """
    asyncio.run(
        process_sections_async(
            input_file,
            output_file,
            model,
            verbose=verbose,
            force=force,
            concurrency=concurrency,
        )
    )


def save_markdown(
    input_file: str | Path,
    output_file: str | Path | None = None,
    *,
    verbose: bool = False,
) -> None:
    """
    Load processed JSON sections and save as a markdown file.

    Args:
        input_file: Path to the input JSON file
        output_file: Path to the output markdown file (defaults to input_file with .summary.md suffix)
        verbose: Whether to print verbose output
    """
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(
            f"[bold red]Error: Input file '{input_file}' not found.[/bold red]"
        )
        sys.exit(1)

    if output_file is None:
        # Get the original markdown filename by removing .json and adding .summary.md
        original_name = input_path.stem
        if original_name.endswith(".md"):
            original_name = original_name[:-3]
        output_path = input_path.with_name(f"{original_name}.summary.md")
    else:
        output_path = Path(output_file)

    # Read JSON file
    console.print(f"Reading processed sections from: [bold]{input_path}[/bold]")
    with open(input_path, encoding="utf-8") as f:
        sections = json.load(f)

    # Combine summaries
    summaries = []
    for section in sections:
        if section.get("summary"):
            summaries.append(section["summary"])
        else:
            heading = section["heading"]
            summaries.append(
                f"## {heading}\n\n*No summary available for this section.*\n\n"
            )

    # Write to output file
    output_content = "\n\n".join(summaries)
    output_path.write_text(output_content, encoding="utf-8")

    console.print(f"\n[bold green]Summary written to: {output_path}[/bold green]")


class SummarizeCommands:
    """Commands for markdown summarization workflow."""

    def load(
        self,
        input_file: str,
        output_file: str | None = None,
        *,
        verbose: bool = False,
    ):
        """
        Load a markdown file, split it at H2 headings, and save as JSON.

        Args:
            input_file: Path to the input markdown file
            output_file: Path to the output JSON file (defaults to input_file with .json suffix)
            verbose: Whether to print verbose output
        """
        load_markdown(input_file, output_file, verbose=verbose)

    def process(
        self,
        input_file: str | None = None,
        output_file: str | None = None,
        model: str | None = None,
        *,
        verbose: bool = False,
        force: bool = False,
        concurrency: int = 3,
        list_models: bool = False,
    ):
        """
        Process JSON file with sections and summarize each section.

        Args:
            input_file: Path to the input JSON file (not required if list_models is True)
            output_file: Path to the output JSON file (defaults to input_file)
            model: Optional specific LLM model to use
            verbose: Whether to print verbose output
            force: Whether to reprocess sections that already have summaries
            concurrency: Maximum number of concurrent tasks
            list_models: Just list available models and exit
        """
        if list_models:
            console.print("[bold]Available models:[/bold]")
            for available_model in llm.get_async_models():
                console.print(f"  - {available_model.model_id}")
            return

        if input_file is None:
            console.print(
                "[bold red]Error: input_file is required when not listing models[/bold red]"
            )
            sys.exit(1)

        process_sections(
            input_file,
            output_file,
            model,
            verbose=verbose,
            force=force,
            concurrency=concurrency,
        )

    def save(
        self,
        input_file: str,
        output_file: str | None = None,
        *,
        verbose: bool = False,
    ):
        """
        Load processed JSON sections and save as a markdown file.

        Args:
            input_file: Path to the input JSON file
            output_file: Path to the output markdown file (defaults to input_file with .summary.md suffix)
            verbose: Whether to print verbose output
        """
        save_markdown(input_file, output_file, verbose=verbose)

    def all(
        self,
        input_file: str | None = None,
        output_file: str | None = None,
        model: str | None = None,
        *,
        verbose: bool = False,
        force: bool = False,
        concurrency: int = 3,
        list_models: bool = False,
    ):
        """
        Run the entire workflow: load, process, and save.

        Args:
            input_file: Path to the input markdown file (not required if list_models is True)
            output_file: Path to the output markdown file (defaults to input_file with .summary.md suffix)
            model: Optional specific LLM model to use
            verbose: Whether to print verbose output
            force: Whether to reprocess sections that already have summaries
            concurrency: Maximum number of concurrent tasks
            list_models: Just list available models and exit
        """
        if list_models:
            console.print("[bold]Available models:[/bold]")
            for available_model in llm.get_async_models():
                console.print(f"  - {available_model.model_id}")
            return

        if input_file is None:
            console.print(
                "[bold red]Error: input_file is required when not listing models[/bold red]"
            )
            sys.exit(1)

        # Generate temporary JSON files
        input_json_file = Path(input_file).with_suffix(".json")
        processed_json_file = Path(input_file).with_suffix(".processed.json")

        # Run the three steps
        load_markdown(input_file, input_json_file, verbose=verbose)
        process_sections(
            input_json_file,
            processed_json_file,
            model,
            verbose=verbose,
            force=force,
            concurrency=concurrency,
        )
        save_markdown(processed_json_file, output_file, verbose=verbose)


if __name__ == "__main__":
    Fire(SummarizeCommands)
