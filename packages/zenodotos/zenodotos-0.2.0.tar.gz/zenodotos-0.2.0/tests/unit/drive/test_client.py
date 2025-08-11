"""Unit tests for Google Drive client."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch
from googleapiclient.errors import HttpError

import pytest

from zenodotos.drive.client import DriveClient
from zenodotos.drive.models import DriveFile


@pytest.fixture
def mock_credentials():
    """Mock Google API credentials."""
    return Mock()


@pytest.fixture
def mock_service():
    """Create a mock Drive API service."""
    service = Mock()
    files = Mock()
    service.files.return_value = files
    return service


@pytest.fixture
def mock_auth(mock_credentials):
    """Mock Auth class."""
    with patch("zenodotos.drive.client.Auth") as mock_auth_class:
        mock_auth_instance = Mock()
        mock_auth_instance.get_credentials.return_value = mock_credentials
        mock_auth_class.return_value = mock_auth_instance
        yield mock_auth_instance


@pytest.fixture
def drive_client(mock_auth, mock_service):
    """Create a DriveClient instance with mocked dependencies."""
    with patch("zenodotos.drive.client.build", return_value=mock_service):
        client = DriveClient()
        client.service = mock_service
        return client


def test_get_service_creates_service_once(drive_client, mock_credentials, mock_service):
    """Test that get_service creates the service only once."""
    # First call should create the service
    service1 = drive_client.get_service()
    assert service1 == mock_service

    # Second call should return the same service instance
    service2 = drive_client.get_service()
    assert service2 == mock_service
    assert service1 == service2


@pytest.mark.parametrize(
    "page_size,page_token,query,fields,expected_fields",
    [
        # Test case 1: Default parameters
        (
            10,
            None,
            None,
            None,
            "nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, description, owners, webViewLink)",
        ),
        # Test case 2: Custom page size and token
        (
            20,
            "next_page_token",
            None,
            None,
            "nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, description, owners, webViewLink)",
        ),
        # Test case 3: With query and custom fields
        (
            10,
            None,
            "name contains 'test'",
            ["id", "name"],
            "nextPageToken, files(id, name)",
        ),
    ],
)
def test_list_files_parameters(
    drive_client, mock_service, page_size, page_token, query, fields, expected_fields
):
    """Test list_files with different parameter combinations."""
    # Mock the API response
    mock_response = {
        "files": [{"id": "123", "name": "test.txt", "mimeType": "text/plain"}],
        "nextPageToken": "next_page_token",
    }

    # Set up the mock chain
    list_mock = Mock()
    execute_mock = Mock(return_value=mock_response)
    list_mock.execute = execute_mock
    mock_service.files().list = Mock(return_value=list_mock)

    # Call the method
    result = drive_client.list_files(
        page_size=page_size, page_token=page_token, query=query, fields=fields
    )

    # Verify the API call
    mock_service.files().list.assert_called_once_with(
        pageSize=page_size,
        pageToken=page_token,
        q=query,
        fields=expected_fields,
        orderBy="modifiedTime desc",
    )

    # Verify the response
    assert len(result["files"]) == 1
    assert isinstance(result["files"][0], DriveFile)
    assert result["next_page_token"] == "next_page_token"


def test_list_files_handles_empty_response(drive_client, mock_service):
    """Test list_files handles empty response."""
    # Mock empty response
    mock_response = {"files": []}

    # Set up the mock chain
    list_mock = Mock()
    execute_mock = Mock(return_value=mock_response)
    list_mock.execute = execute_mock
    mock_service.files().list = Mock(return_value=list_mock)

    result = drive_client.list_files()
    assert result["files"] == []
    assert result["next_page_token"] is None


@pytest.mark.parametrize(
    "status_code,error_class,error_message",
    [
        (401, PermissionError, "Authentication failed. Please check your credentials."),
        (403, PermissionError, "Insufficient permissions to access Google Drive."),
        (500, RuntimeError, "Failed to list files:"),
    ],
)
def test_list_files_error_handling(
    drive_client, mock_service, status_code, error_class, error_message
):
    """Test list_files error handling."""
    # Mock API error
    resp = Mock()
    resp.status = status_code
    resp.reason = "Test error"
    error = HttpError(resp, b"error")

    # Set up the mock chain
    list_mock = Mock()
    list_mock.execute.side_effect = error
    mock_service.files().list = Mock(return_value=list_mock)

    with pytest.raises(error_class, match=error_message):
        drive_client.list_files()


@pytest.mark.parametrize(
    "file_id,api_response,expected_attrs",
    [
        # Test case 1: Complete file data
        (
            "123",
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
    ],
)
def test_get_file(drive_client, mock_service, file_id, api_response, expected_attrs):
    """Test get_file with different file data."""
    # Set up the mock chain
    get_mock = Mock()
    execute_mock = Mock(return_value=api_response)
    get_mock.execute = execute_mock
    mock_service.files().get = Mock(return_value=get_mock)

    # Call the method
    file = drive_client.get_file(file_id)

    # Verify the API call
    mock_service.files().get.assert_called_once_with(
        fileId=file_id,
        fields="id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink",
    )

    # Verify the response
    for attr, value in expected_attrs.items():
        assert getattr(file, attr) == value


@pytest.mark.parametrize(
    "status_code,error_class,error_message",
    [
        (404, FileNotFoundError, "File with ID 123 not found."),
        (401, PermissionError, "Insufficient permissions to access the file."),
        (403, PermissionError, "Insufficient permissions to access the file."),
        (500, RuntimeError, "Failed to get file:"),
    ],
)
def test_get_file_error_handling(
    drive_client, mock_service, status_code, error_class, error_message
):
    """Test get_file error handling."""
    # Mock API error
    resp = Mock()
    resp.status = status_code
    resp.reason = "Test error"
    error = HttpError(resp, b"error")

    # Set up the mock chain
    get_mock = Mock()
    get_mock.execute.side_effect = error
    mock_service.files().get = Mock(return_value=get_mock)

    with pytest.raises(error_class, match=error_message):
        drive_client.get_file("123")
