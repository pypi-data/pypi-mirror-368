# Markdown Summarizer

This tool splits a Markdown file at H2 headings and summarizes each section using an LLM.

## 1. Features

- Splits Markdown documents at H2 headings
- Summarizes each section using LLM
- Preserves key information and technical details
- Outputs a new Markdown file with summaries
- Supports multiple LLM providers with fallback options
- Progress tracking with rich console output
- Resumable processing with intermediate JSON storage

## 2. Usage

The tool provides three separate commands for a flexible workflow:

### 2.1. Load Command

Splits a Markdown file at H2 headings and saves the sections to a JSON file:

```bash
# Basic usage
python summarize.py load input.md

# Specify output JSON file
python summarize.py load input.md --output_file=sections.json

# Enable verbose output
python summarize.py load input.md --verbose
```

### 2.2. Process Command

Processes the JSON file, summarizing each section and saving progress after each section:

```bash
# Basic usage
python summarize.py process sections.json

# Use a specific LLM model
python summarize.py process sections.json --model=gpt-4o-mini

# Enable verbose output
python summarize.py process sections.json --verbose
```

### 2.3. Save Command

Converts the processed JSON file back to a Markdown file with summaries:

```bash
# Basic usage
python summarize.py save sections.json

# Specify output Markdown file
python summarize.py save sections.json --output_file=summary.md

# Enable verbose output
python summarize.py save sections.json --verbose
```

### 2.4. All-in-One Command

Run the entire workflow in one command:

```bash
# Basic usage
python summarize.py all input.md

# Specify output file and model
python summarize.py all input.md --output_file=summary.md --model=gpt-4o-mini

# Enable verbose output
python summarize.py all input.md --verbose
```

### 2.5. Using with uv

The script includes a uv run header, so you can also run it directly with uv:

```bash
uv run summarize.py load input.md
```

## 3. Workflow Benefits

This three-step workflow provides several advantages:

1. **Resumable Processing**: If summarization is interrupted, you can restart from where you left off
2. **Selective Reprocessing**: You can edit the JSON file to clear specific summaries for reprocessing
3. **Progress Tracking**: The JSON file serves as a checkpoint for long-running processes
4. **Flexible Output**: You can modify the JSON before generating the final Markdown

## 4. LLM Support

The script uses the `llm` library to interact with various LLM providers. It will try the following models in order:

1. `gpt-4o-mini` (OpenAI)
2. `openrouter/google/gemini-flash-1.5`
3. `openrouter/openai/gpt-4o-mini`
4. `haiku` (Claude 3 Haiku)

You can specify a different model using the `--model` parameter.

## 5. Requirements

- Python 3.9+
- Dependencies: fire, rich, llm, tenacity, pathos

## 6. Example

If you have a Markdown file like:

```markdown
# My Document

## 7. Introduction
This is an introduction to my document.

## 8. Section 1
This is the first section with important details.

## 9. Section 2
This is the second section with more information.
```

Running the summarizer will create a new file with summaries of each section, preserving the H2 headings. 