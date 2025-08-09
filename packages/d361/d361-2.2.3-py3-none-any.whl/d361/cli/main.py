# this_file: external/int_folders/d361/src/d361/cli/main.py
"""
Main CLI application for d361.

This module provides the primary command-line interface for the d361 library,
built with Fire for excellent CLI UX and Rich for beautiful terminal output.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Optional

import fire
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..plugins.manager import PluginManager
from ..providers.mock_provider import MockProvider

# Global console for rich output
console = Console()


class D361CLI:
    """Document360 unified toolkit CLI application."""

    def __init__(self):
        """Initialize CLI with global state."""
        self.verbose: bool = False
        self.debug: bool = False
        self.config_file: Optional[Path] = None
        self.plugin_manager: PluginManager = PluginManager()

    def _setup_logging(self, debug: bool = False, verbose: bool = False) -> None:
        """Set up logging based on debug/verbose flags."""
        self.debug = debug
        self.verbose = verbose
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        elif verbose:
            logging.basicConfig(level=logging.INFO)

    def sync(
        self,
        source: str = "api",
        tokens: Optional[str] = None,
        output: str = "./docs",
        format: str = "markdown",  # noqa: A002
        category_id: Optional[int] = None,
        verbose: bool = False,
        debug: bool = False,
        config: Optional[str] = None,
    ) -> None:
        """Sync content from Document360 to local files.
        
        Args:
            source: Data source: api, archive, or hybrid (default: api)
            tokens: API tokens (comma-separated)
            output: Output directory (default: ./docs)
            format: Output format: markdown, html, json (default: markdown)
            category_id: Sync specific category only
            verbose: Enable verbose output
            debug: Enable debug output  
            config: Configuration file path
        
        Examples:
            d361 sync --source api --tokens token1,token2 --output ./docs
            d361 sync --source archive --input archive.zip --output ./converted
            d361 sync --source hybrid --category 123
        """
        self._setup_logging(debug, verbose)
        if config:
            self.config_file = Path(config)
        
        output_path = Path(output)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing sync...", total=None)
            
            try:
                # For demonstration, use MockProvider
                if source == "mock":
                    provider = MockProvider()
                    progress.update(task, description="Using mock provider...")
                    
                    # Run the async sync operation
                    result = asyncio.run(self._sync_with_provider(provider, output_path, format, category_id))
                    
                    progress.update(task, description="Sync completed!")
                    rprint(f"[green]✓[/green] Synced {result['articles']} articles to {output}")
                    
                else:
                    rprint(f"[yellow]⚠[/yellow] Source '{source}' not yet implemented")
                    rprint("Available sources: mock")
                    return
                    
            except Exception as e:
                progress.update(task, description="Sync failed!")
                rprint(f"[red]✗[/red] Sync failed: {e}")
                if self.debug:
                    import traceback
                    traceback.print_exc()
                return

    async def _sync_with_provider(
        self,
        provider: Any,
        output_dir: Path,
        output_format: str,
        category_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """Perform sync operation with the given provider."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # List articles
        articles = await provider.list_articles(category_id=category_id)
        
        # Write articles to files
        for article in articles:
            filename = f"{article.id}_{article.slug or 'article'}.{output_format}"
            filepath = output_dir / filename
            
            content = article.content_markdown if output_format == "markdown" else article.content
            
            with open(filepath, "w", encoding="utf-8") as f:
                if output_format == "json":
                    f.write(json.dumps(article.model_dump(), indent=2))
                else:
                    f.write(content)
        
        return {"articles": len(articles), "output_dir": str(output_dir)}

    def convert(
        self,
        input_path: str,
        output: Optional[str] = None,
        from_format: str = "html",
        to_format: str = "markdown",
        plugin: Optional[str] = None,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Convert content between formats using plugins.
        
        Args:
            input_path: Input file or directory
            output: Output file or directory
            from_format: Source format (default: html)
            to_format: Target format (default: markdown)  
            plugin: Specific plugin to use
            verbose: Enable verbose output
            debug: Enable debug output
        
        Examples:
            d361 convert input.html --output output.md --from_format html --to_format markdown
            d361 convert ./docs --output ./converted --to_format confluence
        """
        self._setup_logging(debug, verbose)
        
        input_path_obj = Path(input_path)
        output_path = Path(output) if output else input_path_obj.with_suffix(f".{to_format}")
        
        try:
            if not input_path_obj.exists():
                rprint(f"[red]✗[/red] Input path not found: {input_path_obj}")
                return
                
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Converting content...", total=None)
                
                # Check for available plugins
                plugins = self.plugin_manager.get_plugins_for_format(from_format, to_format)
                
                if not plugins:
                    progress.update(task, description="No plugins available!")
                    rprint(f"[red]✗[/red] No plugins found for {from_format} -> {to_format} conversion")
                    rprint("Available converter plugins:")
                    for p in self.plugin_manager.list_converter_plugins():
                        rprint(f"  - {p}")
                    return
                    
                progress.update(task, description=f"Using plugin: {plugin or plugins[0]}")
                
                # For now, just show what would happen
                rprint(f"[green]✓[/green] Would convert {input_path_obj} to {output_path}")
                rprint(f"Format: {from_format} -> {to_format}")
                rprint(f"Plugin: {plugin or plugins[0]}")
                
        except Exception as e:
            rprint(f"[red]✗[/red] Conversion failed: {e}")
            if self.debug:
                import traceback
                traceback.print_exc()

    def status(
        self,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Show system status and health information.
        
        Args:
            verbose: Show detailed status
            debug: Enable debug output
        """
        self._setup_logging(debug, verbose)
        
        # Create status table
        table = Table(title="d361 System Status", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Details", style="dim")
        
        # Plugin system status
        converter_count = len(self.plugin_manager.list_converter_plugins())
        plugin_status = "[green]✓ Online[/green]" if converter_count > 0 else "[yellow]⚠ No plugins[/yellow]"
        table.add_row("Plugin System", plugin_status, f"{converter_count} converters loaded")
        
        # Mock provider status (for testing)
        try:
            provider = MockProvider()
            articles = asyncio.run(provider.list_articles())
            provider_status = "[green]✓ Online[/green]"
            provider_details = f"{len(articles)} mock articles available"
        except Exception as e:
            provider_status = "[red]✗ Offline[/red]"
            provider_details = f"Error: {e}"
        table.add_row("Mock Provider", provider_status, provider_details)
        
        # Configuration status
        config_status = "[green]✓ Loaded[/green]" if self.config_file else "[yellow]⚠ Default[/yellow]"
        config_details = str(self.config_file) if self.config_file else "Using default settings"
        table.add_row("Configuration", config_status, config_details)
        
        console.print(table)
        
        if verbose:
            console.print("\n[bold]Available Plugins:[/bold]")
            plugins = self.plugin_manager.list_converter_plugins()
            if plugins:
                for plugin_name in plugins:
                    console.print(f"  • {plugin_name}")
            else:
                console.print("  No plugins installed")

    def plugins(
        self,
        list_all: bool = False,
        show_formats: bool = False,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Manage and view information about plugins.
        
        Args:
            list_all: List all available plugins
            show_formats: Show supported format conversions
            verbose: Enable verbose output
            debug: Enable debug output
        """
        self._setup_logging(debug, verbose)
        
        if list_all or not show_formats:
            plugins = self.plugin_manager.list_converter_plugins()
            
            if not plugins:
                rprint("[yellow]No converter plugins installed[/yellow]")
                return
                
            table = Table(title="Converter Plugins", show_header=True, header_style="bold magenta")
            table.add_column("Plugin Name", style="cyan")
            table.add_column("Supported Formats", style="green")
            
            for plugin_name in plugins:
                try:
                    plugin_class = self.plugin_manager.get_converter_plugin(plugin_name)
                    if plugin_class:
                        instance = plugin_class()
                        formats = instance.supported_formats
                        format_str = f"{formats[0]} → {formats[1]}"
                    else:
                        format_str = "Unknown"
                except Exception:
                    format_str = "Error loading"
                    
                table.add_row(plugin_name, format_str)
                
            console.print(table)
            
        if show_formats:
            # Show format conversion matrix
            console.print("\n[bold]Available Format Conversions:[/bold]")
            console.print("(This feature will be implemented when plugins are available)")

    def migrate(
        self,
        from_system: str,
        config: Optional[str] = None,
        output: Optional[str] = None,
        dry_run: bool = False,
        verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Migrate from legacy Document360 implementations.
        
        Args:
            from_system: Source system: d361api, d362a, d362b, etc.
            config: Legacy configuration file
            output: Output configuration file
            dry_run: Show migration plan without applying
            verbose: Enable verbose output
            debug: Enable debug output
        
        Examples:
            d361 migrate d361api --config old_config.py --dry_run
            d361 migrate d362a --output new_config.yaml
        """
        self._setup_logging(debug, verbose)
        
        rprint(f"[yellow]⚠[/yellow] Migration from {from_system} not yet implemented")
        
        if config:
            rprint(f"Would migrate config from: {config}")
        if output:
            rprint(f"Would write new config to: {output}")
        if dry_run:
            rprint("This is a dry run - no changes would be made")
            
        # TODO: Implement migration logic
        rprint("Migration system will be implemented in a future release")


def main_cli() -> None:
    """Entry point for the CLI application."""
    fire.Fire(D361CLI, name="d361")


if __name__ == "__main__":
    main_cli()