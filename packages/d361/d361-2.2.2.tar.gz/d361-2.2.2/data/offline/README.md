# D361Offline

A tool for generating offline documentation from Document360 sites.

## Features

- Extract URLs from a sitemap
- Extract navigation structure from Document360 pages
- Fetch and process HTML content
- Generate static HTML and Markdown documentation

## Installation

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

## Usage

### Command Line Interface

```bash
# Prepare by extracting sitemap and navigation
d361-offline prep --map-url=https://docs.document360.com/sitemap-en.xml --output-dir=docs

# Fetch content for all URLs found
d361-offline fetch --prep-file=docs/prep.json

# Build HTML and Markdown output
d361-offline build --fetch-file=docs/fetch.json

# Or run all steps at once
d361-offline all --map-url=https://docs.document360.com/sitemap-en.xml --output-dir=docs
```

### Python API

```python
import asyncio
from d361_offline import D361Offline
from d361_offline.config import Config

# Create configuration
config = Config(
    map_url="https://docs.document360.com/sitemap-en.xml",
    output_dir="docs"
)

# Initialize
offline = D361Offline(config)

# Run the process
async def main():
    # Prepare
    await offline.prep()
    
    # Fetch
    await offline.fetch()
    
    # Build
    await offline.build()
    
    # Or run all at once
    # await offline.all()

# Run asynchronously
asyncio.run(main())
```

## Options

| Option | Description |
|--------|-------------|
| `--map-url` | URL of the sitemap.xml file |
| `--nav-url` | URL of the page to extract navigation from (if different from sitemap URLs) |
| `--output-dir` | Output directory path (defaults to domain name in current directory) |
| `--css-file` | Custom CSS file path |
| `--effort` | Effort level (1-3, higher means more processing) |
| `--max-concurrent` | Maximum number of concurrent requests |
| `--retries` | Number of retries for failed requests |
| `--timeout` | Timeout in seconds for page loads |
| `--verbose` | Enable verbose logging |
| `--test` | Run in test mode with limited output |
| `--pause` | Pause between requests in seconds |

## Development

Requires Python 3.11+ and Playwright.

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Run tests
pytest

# Format code
ruff check --fix . && ruff format .
```

## License

MIT 