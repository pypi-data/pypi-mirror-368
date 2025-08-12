"""Formatting functions for CLI output."""

from typing import List, Optional
from ..drive.models import DriveFile


def format_file_list(
    files: List[DriveFile], requested_fields: Optional[List[str]] = None
) -> str:
    """Format a list of files for display.

    Args:
        files: List of DriveFile objects to display
        requested_fields: List of field names that were requested (for dynamic display)
    """
    if not files:
        return "No files found."

    # If no requested fields specified, use default display (backward compatibility)
    if not requested_fields:
        return _format_default_display(files)

    # For dynamic display, show requested fields that are available
    return _format_dynamic_display(files, requested_fields)


def _format_default_display(files: List[DriveFile]) -> str:
    """Format files using the default 3-column layout (Name, Type, Size)."""
    # Calculate column widths
    name_width = max(len(f.name) for f in files)
    type_width = max(len(f.mime_type) for f in files)

    # Create header
    header = f"{'Name':<{name_width}}  {'Type':<{type_width}}  {'Size':>10}"
    separator = "-" * (name_width + type_width + 15)

    # Format each file
    rows = [header, separator]
    for file in files:
        size = f"{file.size:,}" if file.size else "N/A"
        rows.append(
            f"{file.name:<{name_width}}  {file.mime_type:<{type_width}}  {size:>10}"
        )

    return "\n".join(rows)


def _format_dynamic_display(files: List[DriveFile], requested_fields: List[str]) -> str:
    """Format files showing only the requested fields in a dynamic layout."""
    # Define field display configuration
    field_config = {
        "id": {"header": "ID", "width": 45, "align": "<"},
        "name": {"header": "Name", "width": 40, "align": "<"},
        "mimeType": {"header": "Type", "width": 25, "align": "<"},
        "size": {"header": "Size", "width": 10, "align": ">"},
        "createdTime": {"header": "Created", "width": 20, "align": "<"},
        "modifiedTime": {"header": "Modified", "width": 20, "align": "<"},
        "description": {"header": "Description", "width": 30, "align": "<"},
        "owners": {"header": "Owners", "width": 25, "align": "<"},
        "webViewLink": {"header": "Link", "width": 30, "align": "<"},
    }

    # Filter requested fields to only those we can display
    displayable_fields = [f for f in requested_fields if f in field_config]

    if not displayable_fields:
        return _format_default_display(files)

    # Calculate actual column widths based on content
    field_widths = {}
    for field in displayable_fields:
        max_width = len(field_config[field]["header"])
        for file in files:
            value = _get_field_value(file, field)
            max_width = max(max_width, len(str(value)))
        field_widths[field] = min(max_width, field_config[field]["width"])

    # Create header
    header_parts = []
    separator_parts = []
    for field in displayable_fields:
        width = field_widths[field]
        align = field_config[field]["align"]
        header_text = field_config[field]["header"]
        header_parts.append(f"{header_text:{align}{width}}")
        separator_parts.append("-" * width)

    header = "  ".join(header_parts)
    separator = "  ".join(separator_parts)

    # Format each file
    rows = [header, separator]
    for file in files:
        row_parts = []
        for field in displayable_fields:
            width = field_widths[field]
            align = field_config[field]["align"]
            value = _get_field_value(file, field)
            # Truncate long values
            if len(str(value)) > width:
                value = str(value)[: width - 3] + "..."
            row_parts.append(f"{value:{align}{width}}")
        rows.append("  ".join(row_parts))

    return "\n".join(rows)


def _get_field_value(file: DriveFile, field: str) -> str:
    """Get the display value for a field from a DriveFile object."""
    if field == "size":
        return f"{file.size:,}" if file.size else "N/A"
    elif field == "mimeType":
        return file.mime_type if file.mime_type else "N/A"
    elif field == "owners":
        owners = getattr(file, "owners", None)
        if owners is not None:
            # Show first owner's display name if available
            if isinstance(owners, list) and owners:
                first_owner = owners[0]
                if isinstance(first_owner, dict) and "displayName" in first_owner:
                    return first_owner["displayName"]
                return str(first_owner)
            elif isinstance(owners, dict) and "displayName" in owners:
                return owners["displayName"]
            return str(owners)
        return "N/A"
    elif field == "createdTime" or field == "modifiedTime":
        # Map field names to DriveFile attributes
        attr_name = "created_time" if field == "createdTime" else "modified_time"
        value = getattr(file, attr_name, None)
        if value:
            # Format timestamp to readable format (just date part)
            return str(value)[:10] if len(str(value)) > 10 else str(value)
        return "N/A"
    else:
        value = getattr(file, field, None)
        return str(value) if value is not None else "N/A"
