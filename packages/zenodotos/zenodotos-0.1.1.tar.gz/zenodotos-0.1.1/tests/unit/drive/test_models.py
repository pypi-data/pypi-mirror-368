"""Unit tests for Google Drive models."""

from datetime import datetime, timezone
import pytest

from zenodotos.drive.models import DriveFile


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        # Test case 1: Basic creation with required fields
        (
            {"id": "123", "name": "test.txt", "mime_type": "text/plain"},
            {
                "id": "123",
                "name": "test.txt",
                "mime_type": "text/plain",
                "size": None,
                "created_time": None,
                "modified_time": None,
                "description": None,
                "owners": None,
                "web_view_link": None,
            },
        ),
        # Test case 2: Creation with all fields
        (
            {
                "id": "123",
                "name": "test.txt",
                "mime_type": "text/plain",
                "size": 1024,
                "created_time": datetime(2024, 1, 1, tzinfo=timezone.utc),
                "modified_time": datetime(2024, 1, 2, tzinfo=timezone.utc),
                "description": "Test file",
                "owners": [
                    {"emailAddress": "test@example.com", "displayName": "Test User"}
                ],
                "web_view_link": "https://drive.google.com/file/d/123/view",
            },
            {
                "id": "123",
                "name": "test.txt",
                "mime_type": "text/plain",
                "size": 1024,
                "created_time": datetime(2024, 1, 1, tzinfo=timezone.utc),
                "modified_time": datetime(2024, 1, 2, tzinfo=timezone.utc),
                "description": "Test file",
                "owners": [
                    {"emailAddress": "test@example.com", "displayName": "Test User"}
                ],
                "web_view_link": "https://drive.google.com/file/d/123/view",
            },
        ),
    ],
)
def test_drive_file_creation(kwargs, expected):
    """Test DriveFile creation with various field combinations.

    Args:
        kwargs: Dictionary of arguments to pass to DriveFile constructor
        expected: Dictionary of expected attribute values
    """
    assert all(k in kwargs for k in ["id", "name", "mime_type"]), (
        "Missing required fields in kwargs"
    )
    file = DriveFile(**kwargs)  # ty: ignore

    for attr, value in expected.items():
        assert getattr(file, attr) == value


@pytest.mark.parametrize(
    "api_data,expected",
    [
        # Test case 1: Complete API response
        (
            {
                "id": "123",
                "name": "test.txt",
                "mimeType": "text/plain",
                "size": "1024",
                "createdTime": "2024-01-01T00:00:00Z",
                "modifiedTime": "2024-01-02T00:00:00Z",
                "description": "Test file",
                "owners": [
                    {"emailAddress": "test@example.com", "displayName": "Test User"}
                ],
                "webViewLink": "https://drive.google.com/file/d/123/view",
            },
            {
                "id": "123",
                "name": "test.txt",
                "mime_type": "text/plain",
                "size": 1024,
                "created_time": datetime(2024, 1, 1, tzinfo=timezone.utc),
                "modified_time": datetime(2024, 1, 2, tzinfo=timezone.utc),
                "description": "Test file",
                "owners": [
                    {"emailAddress": "test@example.com", "displayName": "Test User"}
                ],
                "web_view_link": "https://drive.google.com/file/d/123/view",
            },
        ),
        # Test case 2: Minimal API response
        (
            {"id": "123", "name": "test.txt", "mimeType": "text/plain"},
            {
                "id": "123",
                "name": "test.txt",
                "mime_type": "text/plain",
                "size": None,
                "created_time": None,
                "modified_time": None,
                "description": None,
                "owners": None,
                "web_view_link": None,
            },
        ),
    ],
)
def test_drive_file_from_api_response(api_data, expected):
    """Test creating DriveFile from API response data.

    Args:
        api_data: Dictionary containing file data from the API
        expected: Dictionary of expected attribute values
    """
    file = DriveFile.from_api_response(api_data)

    for attr, value in expected.items():
        assert getattr(file, attr) == value


def test_drive_file_string_representation():
    """Test string representation of DriveFile."""
    file = DriveFile(id="123", name="test.txt", mime_type="text/plain")

    assert str(file) == "test.txt (text/plain)"


def test_drive_file_repr():
    """Test detailed string representation of DriveFile."""
    created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
    modified_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

    file = DriveFile(
        id="123",
        name="test.txt",
        mime_type="text/plain",
        size=1024,
        created_time=created_time,
        modified_time=modified_time,
    )

    expected_repr = (
        "DriveFile(id='123', name='test.txt', "
        "mime_type='text/plain', size=1024, "
        f"created_time={created_time}, modified_time={modified_time})"
    )

    assert repr(file) == expected_repr
