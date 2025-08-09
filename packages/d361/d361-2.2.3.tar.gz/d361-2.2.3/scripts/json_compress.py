#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire"]
# ///
# this_file: scripts/json_compress.py

"""
OpenAPI specification compression utility.

This production-grade utility processes OpenAPI JSON specifications to reduce
size and complexity by removing non-essential content and filtering endpoints.

Migrated from legacy d362b utilities during Phase 9 consolidation.
"""

from pathlib import Path
import json
import fire
from typing import Optional


def remove_textual_content(obj):
    """Remove descriptive text content from the JSON structure."""
    if isinstance(obj, dict):
        # Remove fields that contain textual content
        text_fields = ["description", "summary", "examples"]
        for key in list(obj.keys()):
            if key in text_fields:
                del obj[key]
            else:
                remove_textual_content(obj[key])
    elif isinstance(obj, list):
        for item in obj:
            remove_textual_content(item)


def keep_core_endpoints(data):
    """Keep only core API endpoints related to content structure."""
    if "paths" not in data:
        return

    # Define patterns for endpoints to keep
    core_patterns = [
        "/v2/Articles",
        "/v2/Categories",
        "/v2/ProjectVersions",
        "/v2/Language",
    ]

    # Filter paths to keep only core endpoints
    paths = data["paths"]
    filtered_paths = {}

    for path, methods in paths.items():
        if any(path.startswith(pattern) for pattern in core_patterns):
            filtered_paths[path] = methods

    # Update the paths in the original data
    data["paths"] = filtered_paths

    # Keep only schemas referenced by core endpoints
    if "components" in data and "schemas" in data["components"]:
        referenced_schemas = set()
        collect_referenced_schemas(
            filtered_paths, data["components"]["schemas"], referenced_schemas
        )

        # Update schemas to keep only referenced ones
        data["components"]["schemas"] = {
            key: value
            for key, value in data["components"]["schemas"].items()
            if key in referenced_schemas
        }


def collect_referenced_schemas(obj, all_schemas, referenced_schemas):
    """Recursively collect schema references from the API specification."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "$ref" and isinstance(value, str):
                schema_name = value.split("/")[-1]
                if schema_name not in referenced_schemas:
                    referenced_schemas.add(schema_name)
                    if schema_name in all_schemas:
                        collect_referenced_schemas(
                            all_schemas[schema_name], all_schemas, referenced_schemas
                        )
            else:
                collect_referenced_schemas(value, all_schemas, referenced_schemas)
    elif isinstance(obj, list):
        for item in obj:
            collect_referenced_schemas(item, all_schemas, referenced_schemas)


def process_json(
    input_path: str | Path,
    output_path: str | Path,
    text: bool = False,
    core: bool = False,
) -> None:
    """Process OpenAPI JSON specification file to remove content based on specified options.

    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSON file
        text: If True, removes descriptive text content
        core: If True, removes non-core API endpoints
    """
    # Convert paths to Path objects
    input_file = Path(input_path)
    output_file = Path(output_path)

    # Validate input file exists
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Read the input JSON
    with input_file.open() as f:
        data = json.load(f)

    if text:
        remove_textual_content(data)

    if core:
        keep_core_endpoints(data)

    # Create parent directories if they don't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write the processed JSON to output file
    with output_file.open("w") as f:
        json.dump(data, f, separators=(",", ":"))


if __name__ == "__main__":
    fire.Fire(process_json)