"""Command-line interface for Zenodotos."""

import click
from .commands import list_files, get_file, export


@click.group()
@click.version_option()
def cli():
    """Zenodotos - Google Drive CLI Tool."""
    pass


# Register commands
cli.add_command(list_files)
cli.add_command(get_file)
cli.add_command(export)

# Export the main CLI for external use
__all__ = ["cli"]
