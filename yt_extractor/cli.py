"""Command-line interface for YouTube extractor."""
import asyncio
import sys
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table

from .core.config import config
from .core.exceptions import ConfigurationError, YouTubeExtractorError
from .core.extractor import YouTubeExtractor
from .utils.cache import cache

console = Console()


@click.group()
@click.option("--config-file", help="Path to configuration file (.env)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config_file, verbose):
    """YouTube Value Extractor - Extract actionable insights from YouTube videos."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    
    if config_file:
        from .core.config import Config
        try:
            config.__dict__.update(Config(config_file).__dict__)
        except Exception as e:
            console.print(f"[red]Failed to load config file: {e}[/red]")
            sys.exit(1)


@cli.command()
@click.argument("urls", nargs=-1, required=True)
@click.option("--output-dir", "-o", help="Output directory for markdown files")
@click.option("--format", "output_format", type=click.Choice(["markdown", "json"]), 
              default="markdown", help="Output format")
@click.option("--dry-run", is_flag=True, help="Preview processing without saving files")
@click.pass_context
def process(ctx, urls, output_dir, output_format, dry_run):
    """Process one or more YouTube videos."""
    try:
        config.validate()
    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)
    
    if dry_run:
        console.print("[yellow]DRY RUN - No files will be saved[/yellow]")
        for url in urls:
            console.print(f"Would process: {url}")
        return
    
    extractor = YouTubeExtractor()
    
    try:
        if len(urls) == 1:
            result = extractor.process_video(urls[0], output_dir)
            console.print(f"[green]✅ Saved to: {result}[/green]")
        else:
            results = extractor.process_videos(list(urls), output_dir)
            console.print(f"[green]✅ Processed {len(results)} videos successfully[/green]")
            
    except YouTubeExtractorError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--output-dir", "-o", help="Output directory for markdown files")
@click.option("--concurrent", "-c", type=int, default=3, 
              help="Number of videos to process concurrently")
@click.pass_context
def batch(ctx, file, output_dir, concurrent):
    """Process multiple videos from a file (one URL per line)."""
    try:
        config.validate()
    except ConfigurationError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)
    
    try:
        urls = [line.strip() for line in file.read_text().splitlines() if line.strip()]
        if not urls:
            console.print("[yellow]No URLs found in file[/yellow]")
            return
        
        console.print(f"[blue]Processing {len(urls)} videos from {file}[/blue]")
        
        extractor = YouTubeExtractor()
        results = extractor.process_videos(urls, output_dir)
        
        console.print(f"[green]✅ Processed {len(results)}/{len(urls)} videos successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]Error processing batch: {e}[/red]")
        sys.exit(1)


@cli.group()
def config_cmd():
    """Configuration management commands."""
    pass


@config_cmd.command("check")
def config_check():
    """Check configuration validity."""
    try:
        config.validate()
        console.print("[green]✅ Configuration is valid[/green]")
        
        # Show current config
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("LLM Model", config.llm_model)
        table.add_row("Output Directory", config.default_output_dir)
        table.add_row("Cache Enabled", str(config.enable_cache))
        table.add_row("Chunk Size", str(config.default_chunk_chars))
        table.add_row("Timezone", config.report_timezone)
        
        console.print(table)
        
    except ConfigurationError as e:
        console.print(f"[red]❌ Configuration error: {e}[/red]")
        sys.exit(1)


@config_cmd.command("init")
@click.option("--force", is_flag=True, help="Overwrite existing .env file")
def config_init(force):
    """Initialize configuration file."""
    env_path = Path(".env")
    
    if env_path.exists() and not force:
        console.print("[yellow]⚠️ .env file already exists. Use --force to overwrite.[/yellow]")
        return
    
    try:
        example_path = Path(__file__).parent.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text())
            console.print(f"[green]✅ Created {env_path}[/green]")
            console.print("[dim]Edit the file to set your API keys and preferences[/dim]")
        else:
            console.print("[red]❌ .env.example not found[/red]")
            
    except Exception as e:
        console.print(f"[red]Error creating .env file: {e}[/red]")


@cli.group()
def cache_cmd():
    """Cache management commands."""
    pass


@cache_cmd.command("stats")
def cache_stats():
    """Show cache statistics."""
    stats = cache.stats()
    
    if not stats.get("enabled"):
        console.print("[yellow]Cache is disabled[/yellow]")
        return
    
    table = Table(title="Cache Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Status", "Enabled")
    table.add_row("Items", str(stats.get("size", "Unknown")))
    table.add_row("Disk Usage", f"{stats.get('disk_usage', 0) / 1024 / 1024:.1f} MB")
    table.add_row("Cache Directory", str(stats.get("cache_dir", "Unknown")))
    
    console.print(table)


@cache_cmd.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear the cache?")
def cache_clear():
    """Clear all cached data."""
    try:
        cache.clear()
        console.print("[green]✅ Cache cleared[/green]")
    except Exception as e:
        console.print(f"[red]Error clearing cache: {e}[/red]")


@cli.command()
@click.argument("url")
def info(url):
    """Show video information without processing."""
    try:
        extractor = YouTubeExtractor()
        meta = extractor.fetch_metadata(url)
        
        table = Table(title="Video Information")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Title", meta.title)
        table.add_row("Channel", meta.channel)
        table.add_row("Duration", meta.duration_formatted)
        table.add_row("Published", meta.published_at)
        table.add_row("Language", meta.language or "Unknown")
        table.add_row("Video ID", meta.id)
        table.add_row("Tags", ", ".join(meta.tags[:5]) + ("..." if len(meta.tags) > 5 else ""))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error fetching video info: {e}[/red]")
        sys.exit(1)


# Add aliases to the main cli group
cli.add_command(config_cmd, name="config")
cli.add_command(cache_cmd, name="cache")


def main():
    """Entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        if "--verbose" in sys.argv or "-v" in sys.argv:
            raise
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()