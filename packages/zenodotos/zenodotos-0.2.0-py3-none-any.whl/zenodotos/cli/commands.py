"""CLI command definitions."""

import click
from zenodotos import Zenodotos
from zenodotos.exceptions import MultipleFilesFoundError, NoFilesFoundError
from zenodotos.formatters.display import format_file_list
from .navigation import interactive_pagination


@click.command()
@click.option(
    "--page-size",
    default=10,
    type=int,
    help="Number of files to display per page (default: 10)",
)
@click.option(
    "--page-token",
    default=None,
    help="Token for a specific page of results (for advanced use)",
)
@click.option(
    "--query",
    default=None,
    help="Search query to filter files (e.g., \"name contains 'report'\")",
)
@click.option(
    "--fields",
    default=None,
    help="Comma-separated list of fields to retrieve for each file. "
    "Defaults to: id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink. "
    "Note: name, mimeType, and size are always included for proper display.",
)
@click.option(
    "--no-interactive",
    is_flag=True,
    help="Disable interactive pagination and show only the first page",
)
def list_files(page_size, page_token, query, fields, no_interactive):
    """List files in your Google Drive with interactive pagination."""
    zenodotos = Zenodotos()

    # Use the library's field parser for consistent field handling
    field_parser = zenodotos.get_field_parser()
    all_fields, requested_fields = field_parser.parse_fields(fields)

    # If page_token is provided or no-interactive is set, use single page mode
    if page_token is not None or no_interactive:
        result = zenodotos.list_files_with_pagination(
            page_size=page_size, page_token=page_token, query=query, fields=all_fields
        )
        click.echo(format_file_list(result["files"], requested_fields))

        # Show next page token if available (for advanced users)
        if result.get("next_page_token"):
            click.echo(f"\nNext page token: {result['next_page_token']}")
            click.echo("Use --page-token option to get the next page")
    else:
        # Use interactive pagination by default
        interactive_pagination(
            zenodotos, page_size, query, all_fields, requested_fields
        )


@click.command()
@click.argument("file_id", required=False)
@click.option(
    "--query",
    help="Search query to find files to get details for (e.g., \"name contains 'report'\")",
)
@click.option(
    "--fields",
    default=None,
    help="Comma-separated list of fields to retrieve for the file. "
    "Defaults to: id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink. "
    "Note: name, mimeType, and size are always included for proper display.",
)
def get_file(file_id, query, fields):
    """Get detailed information about a specific file from Google Drive.

    Retrieves and displays comprehensive metadata for a single file identified by its ID or search query.
    Use --fields to customize which information is displayed.

    Either FILE_ID or --query must be provided. Use --query to search for files by name or other criteria.
    """
    # Validate that either file_id or query is provided
    if not file_id and not query:
        raise click.ClickException("Either FILE_ID or --query must be provided")

    if file_id and query:
        raise click.ClickException("FILE_ID and --query are mutually exclusive")

    zenodotos = Zenodotos()

    # Use the library's field parser for consistent field handling
    field_parser = zenodotos.get_field_parser()
    all_fields, requested_fields = field_parser.parse_fields(fields)

    try:
        # Handle query-based file retrieval
        if query:
            try:
                # Get the file using the library's search_and_get_file method
                file = zenodotos.search_and_get_file(query)

                # Display the file information using the existing formatter
                # Pass as a single-item list since format_file_list expects a list
                click.echo(format_file_list([file], requested_fields))

            except ValueError:
                # Multiple matches - show the options
                click.echo("Multiple files found matching the query:", err=True)
                click.echo("", err=True)

                # Get the list of matching files to show options
                files = zenodotos.list_files(query=query, page_size=100)
                for file in files:
                    click.echo(
                        f"  {file.id} - {file.name} ({file.mime_type})", err=True
                    )
                click.echo("", err=True)
                click.echo(
                    "Please use the file ID to get details for a specific file.",
                    err=True,
                )
                raise click.ClickException("Multiple files found")
            except FileNotFoundError:
                click.echo("No files found matching the query.", err=True)
                raise click.ClickException("No files found")

        # Handle file ID-based retrieval (existing functionality)
        else:
            # Get the file using the library interface
            file = zenodotos.get_file(file_id)

            # Display the file information using the existing formatter
            # Pass as a single-item list since format_file_list expects a list
            click.echo(format_file_list([file], requested_fields))

    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException("File not found")
    except PermissionError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException("Permission denied")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException("Failed to get file")


@click.command()
@click.argument("file_id", required=False)
@click.option(
    "--query",
    help="Search query to find files to export (e.g., \"name contains 'report'\")",
)
@click.option(
    "--output",
    default=None,
    help="Output path for the exported file. If not provided, saves to current directory with document name.",
)
@click.option(
    "--format",
    type=click.Choice(["html", "pdf", "xlsx", "csv"]),
    help="Export format (auto-detected if not specified)",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed progress information",
)
def export(file_id, query, output, format, verbose):
    """Export a file from Google Drive.

    Supports Google Workspace documents (Docs, Sheets, Slides) with smart format defaults:
    - Google Docs: HTML (ZIP file)
    - Google Sheets: XLSX
    - Google Slides: PDF
    - Google Drawings: PNG
    - Google Forms: ZIP

    Use --format to override the default format. Supported formats: html, pdf, xlsx, csv

    Either FILE_ID or --query must be provided. Use --query to search for files by name or other criteria.
    """
    # Validate that either file_id or query is provided
    if not file_id and not query:
        raise click.ClickException("Either FILE_ID or --query must be provided")

    if file_id and query:
        raise click.ClickException("FILE_ID and --query are mutually exclusive")

    try:
        zenodotos = Zenodotos()

        # Handle query-based export using the library's search_and_export method
        if query:
            if verbose:
                click.echo(f"Searching for files with query: {query}")

            try:
                result_path = zenodotos.search_and_export(
                    query, output_path=output, format=format
                )
                click.echo(f"Successfully exported to: {result_path}")
            except MultipleFilesFoundError as e:
                # Multiple matches - show the options
                click.echo("Multiple files found matching the query:", err=True)
                click.echo("", err=True)
                for file in e.files:
                    click.echo(
                        f"  {file.id} - {file.name} ({file.mime_type})", err=True
                    )
                click.echo("", err=True)
                click.echo(
                    "Please use the file ID to export a specific file.", err=True
                )
                raise click.ClickException("Multiple files found")
            except NoFilesFoundError:
                click.echo("No files found matching the query.", err=True)
                raise click.ClickException("No files found")

        # Handle file ID-based export (existing functionality)
        else:
            if verbose:
                click.echo(f"Exporting file with ID: {file_id}")

            result_path = zenodotos.export_file(
                file_id, output_path=output, format=format
            )
            click.echo(f"Successfully exported to: {result_path}")

    except FileNotFoundError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException("File not found")
    except PermissionError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException("Permission denied")
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException("Invalid format")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.ClickException("Export failed")
