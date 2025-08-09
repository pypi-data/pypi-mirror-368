# this_file: external/int_folders/d361/src/d361/cli/__init__.py
"""
Command-line interface for the d361 library.

This package provides a modern CLI built with Fire and Rich for beautiful
terminal output and user-friendly commands.
"""

from .main import D361CLI, main_cli

__all__ = [
    "D361CLI",
    "main_cli",
]