# this_file: src/d361/offline/__main__.py

import asyncio
import sys
from pathlib import Path
from typing import Any

import fire
from loguru import logger

from .config import Config
from .d361_offline import D361Offline


class CLI:
    """Command-line interface for D361Offline."""

    def __init__(self) -> None:
        """Initialize CLI."""
        # Configure logger
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
        )

    def prep(
        self,
        map_url: str = "https://docs.document360.com/sitemap-en.xml",
        nav_url: str = "",
        output_dir: str = "",
        style: str = "",
        effort: int = 1,
        parallel: int = 3,
        retries: int = 2,
        timeout: int = 60,
        verbose: bool = False,
        test: bool = False,
        wait: int = 0,
    ) -> dict[str, Any]:
        """Prepare for documentation generation by extracting sitemap and navigation.

        Args:
            map_url: URL of the sitemap.xml file
            nav_url: URL of the page to extract navigation from (if different from sitemap URLs)
            output_dir: Output directory path (defaults to domain name in current directory)
            css_file: Custom CSS file path
            effort: Effort level (1-3, higher means more processing)
            max_concurrent: Maximum number of concurrent requests
            retries: Number of retries for failed requests
            timeout: Timeout in seconds for page loads
            verbose: Enable verbose logging
            test: Run in test mode with limited output
            pause: Pause between requests in seconds

        Returns:
            Dictionary with prepared state
        """
        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")

        # Create config
        config = Config(
            map_url=map_url,
            nav_url=nav_url or None,
            output_dir=Path(output_dir) if output_dir else Path("."),
            css_file=Path(style) if style else None,
            effort=effort,
            max_concurrent=parallel,
            retries=retries,
            timeout=timeout,
            verbose=verbose,
            test=test,
            pause=wait,
        )

        # Initialize and run
        offline = D361Offline(config)
        return asyncio.run(offline.prep())

    def fetch(
        self,
        prep_file: str = "",
        output_dir: str = "",
        parallel: int = 3,
        retries: int = 2,
        timeout: int = 60,
        verbose: bool = False,
        test: bool = False,
        wait: int = 0,
    ) -> dict[str, Any]:
        """Fetch content for all URLs in the prep file.

        Args:
            prep_file: Path to the prep.json file (defaults to "prep.json" in output_dir)
            output_dir: Output directory path (defaults to directory containing prep_file)
            max_concurrent: Maximum number of concurrent requests
            retries: Number of retries for failed requests
            timeout: Timeout in seconds for page loads
            verbose: Enable verbose logging
            test: Run in test mode with limited output
            pause: Pause between requests in seconds

        Returns:
            Dictionary with fetch state
        """
        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")

        # Determine paths
        if prep_file:
            prep_path = Path(prep_file)
            output_dir_path = Path(output_dir) if output_dir else prep_path.parent
        else:
            output_dir_path = Path(output_dir) if output_dir else Path.cwd()
            prep_path = output_dir_path / "prep.json"

        if not prep_path.exists():
            msg = f"Prep file not found: {prep_path}"
            raise FileNotFoundError(msg)

        # Get map URL from prep file for config
        map_url = ""
        try:
            import json

            with open(prep_path) as f:
                prep_data = json.load(f)
                if (
                    prep_data
                    and "config" in prep_data
                    and "map_url" in prep_data["config"]
                ):
                    map_url = prep_data["config"]["map_url"]
                    logger.debug(f"Using map_url from prep file: {map_url}")
        except Exception as e:
            logger.warning(f"Could not extract map_url from prep file: {e}")

        # Create config
        config = Config(
            map_url=map_url,
            output_dir=str(output_dir_path),
            max_concurrent=parallel,
            retries=retries,
            timeout=timeout,
            verbose=verbose,
            test=test,
            pause=wait,
        )

        # Initialize and run
        offline = D361Offline(config)
        return asyncio.run(offline.fetch(prep_path))

    def build(
        self,
        fetch_file: str = "",
        output_dir: str = "",
        style: str = "",
        verbose: bool = False,
    ) -> None:
        """Build HTML and Markdown output from fetched content.

        Args:
            fetch_file: Path to the fetch.json file (defaults to "fetch.json" in output_dir)
            output_dir: Output directory path (defaults to directory containing fetch_file)
            css_file: Custom CSS file path
            verbose: Enable verbose logging
        """
        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")

        # Determine paths
        if fetch_file:
            fetch_path = Path(fetch_file)
            output_dir_path = Path(output_dir) if output_dir else fetch_path.parent
        else:
            output_dir_path = Path(output_dir) if output_dir else Path.cwd()
            fetch_path = output_dir_path / "fetch.json"

        if not fetch_path.exists():
            msg = f"Fetch file not found: {fetch_path}"
            raise FileNotFoundError(msg)

        # Get map URL from fetch file for config
        map_url = ""
        try:
            import json

            with open(fetch_path) as f:
                fetch_data = json.load(f)
                if (
                    fetch_data
                    and "config" in fetch_data
                    and "map_url" in fetch_data["config"]
                ):
                    map_url = fetch_data["config"]["map_url"]
                    logger.debug(f"Using map_url from fetch file: {map_url}")
        except Exception as e:
            logger.warning(f"Could not extract map_url from fetch file: {e}")

        # Create config
        config = Config(
            map_url=map_url,
            output_dir=str(output_dir_path),
            css_file=style or None,
            verbose=verbose,
        )

        # Initialize and run
        offline = D361Offline(config)
        asyncio.run(offline.build(fetch_path))

    def all(
        self,
        map_url: str = "https://docs.document360.com/sitemap-en.xml",
        nav_url: str = "",
        output_dir: str = "",
        style: str = "",
        effort: int = 1,
        parallel: int = 3,
        retries: int = 2,
        timeout: int = 60,
        verbose: bool = False,
        test: bool = False,
        pause: int = 0,
    ) -> None:
        """Run the entire process: prep, fetch, and build.

        Args:
            map_url: URL of the sitemap.xml file
            nav_url: URL of the page to extract navigation from (if different from sitemap URLs)
            output_dir: Output directory path (defaults to domain name in current directory)
            css_file: Custom CSS file path
            effort: Effort level (1-3, higher means more processing)
            max_concurrent: Maximum number of concurrent requests
            retries: Number of retries for failed requests
            timeout: Timeout in seconds for page loads
            verbose: Enable verbose logging
            test: Run in test mode with limited output
            pause: Pause between requests in seconds
        """
        if verbose:
            logger.remove()
            logger.add(sys.stderr, level="DEBUG")

        # Create config
        config = Config(
            map_url=map_url,
            nav_url=nav_url or None,
            output_dir=str(Path(output_dir) if output_dir else Path(".")),
            css_file=str(Path(style)) if style else None,
            effort=effort,
            max_concurrent=parallel,
            retries=retries,
            timeout=timeout,
            verbose=verbose,
            test=test,
            pause=pause,
        )

        # Initialize and run
        offline = D361Offline(config)
        asyncio.run(offline.all())


def main() -> None:
    """Entry point for the CLI."""
    try:
        fire.Fire(CLI)
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        if logger.level("DEBUG").no <= logger.level("INFO").no:
            import traceback

            logger.debug(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
