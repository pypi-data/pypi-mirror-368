#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["loguru", "fire", "pydantic", "playwright", "beautifulsoup4", "aiohttp", "aiofiles", "markdownify"]
# ///
# this_file: src/d361/offline/__init__.py

"""
D361Offline: A tool for generating offline documentation from Document360 sites.

This package provides functionality to:
- Extract URLs from a sitemap
- Extract navigation structure from Document360 pages
- Fetch and process HTML content
- Generate static HTML and Markdown documentation
"""

__version__ = "0.1.0"

from .__main__ import CLI, main
from .config import Config
from .d361_offline import D361Offline

__all__ = ["CLI", "Config", "D361Offline", "main"]
