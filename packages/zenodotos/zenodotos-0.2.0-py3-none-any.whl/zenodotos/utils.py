"""Utility functions and classes for the Zenodotos library."""

from typing import Any, List, Optional


class FieldParser:
    """Helper for parsing and validating field options."""

    def __init__(self):
        self.required_fields = {"name", "mimeType", "size"}
        self.default_fields = [
            "id",
            "name",
            "mimeType",
            "size",
            "createdTime",
            "modifiedTime",
            "description",
            "owners",
            "webViewLink",
        ]

    def parse_fields(
        self, fields_str: Optional[str]
    ) -> tuple[List[str], Optional[List[str]]]:
        """Parse fields string and return (all_fields, requested_fields).

        Args:
            fields_str: Comma-separated string of field names

        Returns:
            Tuple of (all_fields, requested_fields) where:
                - all_fields: Complete list including required fields
                - requested_fields: Original user-requested fields (for display)
        """
        if not fields_str:
            return self.default_fields, None

        user_fields = [f.strip() for f in fields_str.split(",") if f.strip()]

        # Remove duplicates while preserving order
        seen = set()
        unique_fields = []
        for field in user_fields:
            if field not in seen:
                seen.add(field)
                unique_fields.append(field)

        # Combine with required fields
        all_fields = unique_fields.copy()
        for field in self.required_fields:
            if field not in all_fields:
                all_fields.append(field)

        return all_fields, unique_fields


def validate_file_id(file_id: Any) -> bool:
    """Validate if a string looks like a valid Google Drive file ID.

    Args:
        file_id: The file ID to validate

    Returns:
        True if the file ID appears valid, False otherwise
    """
    if not file_id or not isinstance(file_id, str):
        return False

    # Google Drive file IDs are typically 33-44 characters long
    # and contain alphanumeric characters, hyphens, and underscores
    if len(file_id) < 10 or len(file_id) > 50:
        return False

    # Check if it contains only valid characters
    valid_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    )
    return all(c in valid_chars for c in file_id)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe file system operations.

    Args:
        filename: The original filename

    Returns:
        Sanitized filename safe for file system operations
    """
    if not filename:
        return "untitled"

    # Remove or replace problematic characters
    import re

    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]

    return sanitized or "untitled"


def format_file_size(size_bytes: Optional[int]) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Human-readable file size string
    """
    if size_bytes is None:
        return "Unknown"

    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"
