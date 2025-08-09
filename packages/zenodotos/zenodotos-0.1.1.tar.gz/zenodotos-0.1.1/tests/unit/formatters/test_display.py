"""Test cases for the display formatters module."""

from datetime import datetime

from zenodotos.formatters.display import format_file_list
from zenodotos.drive.models import DriveFile


def test_format_file_list_empty():
    """Test formatting an empty list of files."""
    result = format_file_list([])
    assert result == "No files found."


def test_format_file_list_single_file():
    """Test formatting a single file."""
    file = DriveFile(
        id="1",
        name="test.txt",
        mime_type="text/plain",
        size=100,
    )
    result = format_file_list([file])

    lines = result.split("\n")
    assert len(lines) == 3  # header, separator, file
    assert "Name" in lines[0]
    assert "Type" in lines[0]
    assert "Size" in lines[0]
    assert "test.txt" in lines[2]
    assert "text/plain" in lines[2]
    assert "100" in lines[2]


def test_format_file_list_multiple_files():
    """Test formatting multiple files."""
    files = [
        DriveFile(
            id="1",
            name="file1.txt",
            mime_type="text/plain",
            size=100,
        ),
        DriveFile(
            id="2",
            name="file2.pdf",
            mime_type="application/pdf",
            size=200,
        ),
    ]
    result = format_file_list(files)

    lines = result.split("\n")
    assert len(lines) == 4  # header, separator, file1, file2
    assert "file1.txt" in result
    assert "file2.pdf" in result
    assert "text/plain" in result
    assert "application/pdf" in result


def test_format_file_list_with_requested_fields_default():
    """Test formatting with None requested fields (default behavior)."""
    file = DriveFile(
        id="1",
        name="test.txt",
        mime_type="text/plain",
        size=100,
    )
    result = format_file_list([file], requested_fields=None)

    # Should use default 3-column layout
    lines = result.split("\n")
    assert "Name" in lines[0]
    assert "Type" in lines[0]
    assert "Size" in lines[0]


def test_format_file_list_with_custom_fields():
    """Test formatting with custom requested fields."""
    file = DriveFile(
        id="test123",
        name="test.txt",
        mime_type="text/plain",
        size=100,
    )
    result = format_file_list([file], requested_fields=["id", "name"])

    lines = result.split("\n")
    # Should show ID and Name columns
    assert "ID" in lines[0]
    assert "Name" in lines[0]
    assert "test123" in result
    assert "test.txt" in result
    # Should not show Type or Size columns in header
    assert "Type" not in lines[0]
    assert "Size" not in lines[0]


def test_format_file_list_respects_field_order():
    """Test that column ordering respects the user-specified field order."""
    file = DriveFile(
        id="test123",
        name="test.txt",
        mime_type="text/plain",
        size=100,
    )

    # Test order: id, name, size
    result1 = format_file_list([file], requested_fields=["id", "name", "size"])
    lines1 = result1.split("\n")
    header1 = lines1[0]

    # Test order: name, id, size
    result2 = format_file_list([file], requested_fields=["name", "id", "size"])
    lines2 = result2.split("\n")
    header2 = lines2[0]

    # Test order: size, name, id
    result3 = format_file_list([file], requested_fields=["size", "name", "id"])
    lines3 = result3.split("\n")
    header3 = lines3[0]

    # The header order should match the requested field order
    # For ["id", "name", "size"] -> "ID" should come before "Name" which should come before "Size"
    id_pos1 = header1.find("ID")
    name_pos1 = header1.find("Name")
    size_pos1 = header1.find("Size")
    assert id_pos1 < name_pos1 < size_pos1, (
        f"Expected ID < Name < Size in header: '{header1}'"
    )

    # For ["name", "id", "size"] -> "Name" should come before "ID" which should come before "Size"
    id_pos2 = header2.find("ID")
    name_pos2 = header2.find("Name")
    size_pos2 = header2.find("Size")
    assert name_pos2 < id_pos2 < size_pos2, (
        f"Expected Name < ID < Size in header: '{header2}'"
    )

    # For ["size", "name", "id"] -> "Size" should come before "Name" which should come before "ID"
    id_pos3 = header3.find("ID")
    name_pos3 = header3.find("Name")
    size_pos3 = header3.find("Size")
    assert size_pos3 < name_pos3 < id_pos3, (
        f"Expected Size < Name < ID in header: '{header3}'"
    )


def test_format_file_list_with_complete_google_drive_id():
    """Test formatting with realistic Google Drive ID length (should not be truncated)."""
    # Realistic Google Drive ID (44 characters) - fake but same length as actual Google Drive IDs
    full_drive_id = "1ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqr"
    file = DriveFile(
        id=full_drive_id,
        name="test.txt",
        mime_type="text/plain",
        size=100,
    )
    result = format_file_list([file], requested_fields=["id", "name"])

    lines = result.split("\n")
    # Should show complete ID without truncation
    assert "ID" in lines[0]
    assert "Name" in lines[0]
    assert full_drive_id in result
    # Should NOT contain truncation indicator
    assert "..." not in result
    assert "test.txt" in result


def test_format_file_list_with_timestamps():
    """Test formatting with timestamp fields."""
    file = DriveFile(
        id="1",
        name="test.txt",
        mime_type="text/plain",
        created_time=datetime(2023, 1, 1, 12, 0, 0),
        modified_time=datetime(2023, 1, 2, 13, 0, 0),
    )
    result = format_file_list(
        [file], requested_fields=["name", "createdTime", "modifiedTime"]
    )

    lines = result.split("\n")
    assert "Created" in lines[0]
    assert "Modified" in lines[0]
    assert "2023-01-01" in result
    assert "2023-01-02" in result


def test_format_file_list_with_empty_fields():
    """Test formatting with empty requested fields list."""
    file = DriveFile(name="test.txt", mime_type="text/plain", size=100)
    result = format_file_list([file], requested_fields=[])

    # Should fall back to default display
    lines = result.split("\n")
    assert "Name" in lines[0]
    assert "Type" in lines[0]
    assert "Size" in lines[0]


def test_format_file_list_with_unsupported_fields():
    """Test formatting with unsupported field names."""
    file = DriveFile(name="test.txt", mime_type="text/plain", size=100)
    result = format_file_list([file], requested_fields=["unsupported_field"])

    # Should fall back to default display when no valid fields
    lines = result.split("\n")
    assert "Name" in lines[0]
    assert "Type" in lines[0]
    assert "Size" in lines[0]


def test_format_file_list_with_owners():
    """Test formatting with owners field."""
    file = DriveFile(
        name="test.txt",
        mime_type="text/plain",
        owners=[{"displayName": "John Doe", "emailAddress": "john@example.com"}],
    )
    result = format_file_list([file], requested_fields=["name", "owners"])

    assert "Owners" in result
    assert "John Doe" in result


def test_format_file_list_with_missing_data():
    """Test formatting when some fields are missing."""
    file = DriveFile(name="test.txt")  # Only name provided
    result = format_file_list([file], requested_fields=["id", "name", "size"])

    lines = result.split("\n")
    assert "ID" in lines[0]
    assert "Name" in lines[0]
    assert "Size" in lines[0]
    assert "N/A" in result  # Should show N/A for missing fields
