"""Tests for drive download functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from zenodotos.drive.client import DriveClient


@pytest.fixture
def mock_google_drive_service():
    """Mock Google Drive API service."""
    with patch("zenodotos.drive.client.DriveClient.get_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        # Set up the service chain properly
        mock_files = MagicMock()
        mock_service.files.return_value = mock_files
        yield mock_service


@pytest.fixture
def mock_google_file_metadata():
    """Mock Google Drive file metadata retrieval."""
    with patch("zenodotos.drive.client.DriveClient.get_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_get_request = MagicMock()
        mock_get_request.execute.return_value = {"name": "Test Document"}
        mock_service.files.return_value.get.return_value = mock_get_request
        yield mock_get_request.execute


class TestDriveClientDownload:
    """Tests for DriveClient download functionality."""

    def test_export_google_doc_to_html(self):
        """Test exporting a Google Doc to HTML format (ZIP file)."""
        # Test data
        file_id = "1test_google_doc_id"
        mock_google_export_content = b"fake_html_zip_content"

        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_document.zip"

            # Mock the Google Drive API service
            mock_google_drive_service = MagicMock()
            mock_google_export_request = MagicMock()
            mock_google_export_request.execute.return_value = mock_google_export_content
            mock_google_drive_service.files().export.return_value = (
                mock_google_export_request
            )

            # Setup client with mocked Google service
            client = DriveClient()
            client.service = mock_google_drive_service

            # This should fail initially - method doesn't exist yet
            client.export(file_id, str(output_path))

            # Verify the Google API was called correctly
            mock_google_drive_service.files().export.assert_called_once_with(
                fileId=file_id,
                mimeType="application/zip",  # HTML export format for Google Docs
            )

            # Verify the file was saved
            assert output_path.exists()
            assert output_path.read_bytes() == mock_google_export_content

    def test_export_google_doc_html_to_current_directory(self):
        """Test exporting Google Doc to HTML in current directory with auto-naming."""
        file_id = "1test_doc_id"
        mock_export_content = b"fake_zip_content"

        # Mock the file metadata to get the name
        mock_file_data = {
            "id": file_id,
            "name": "My Document",
            "mimeType": "application/vnd.google-apps.document",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory to simulate current directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Mock the Google Drive API service
                mock_google_drive_service = MagicMock()

                # Mock Google's get file metadata
                mock_google_get_request = MagicMock()
                mock_google_get_request.execute.return_value = mock_file_data
                mock_google_drive_service.files().get.return_value = (
                    mock_google_get_request
                )

                # Mock Google's export request
                mock_google_export_request = MagicMock()
                mock_google_export_request.execute.return_value = mock_export_content
                mock_google_drive_service.files().export.return_value = (
                    mock_google_export_request
                )

                # Setup client with mocked Google service
                client = DriveClient()
                client.service = mock_google_drive_service

                # This should fail - method doesn't exist yet
                result_path = client.export(file_id)

                # Verify file was created with expected name
                expected_path = Path("My Document.zip")
                assert expected_path.exists()
                assert expected_path.read_bytes() == mock_export_content
                assert result_path == str(expected_path)

                # Verify Google API calls - now we call get twice: once for mimeType (smart default), once for name
                assert mock_google_drive_service.files().get.call_count == 2
                # First call for mimeType (smart default)
                mock_google_drive_service.files().get.assert_any_call(
                    fileId=file_id, fields="mimeType"
                )
                # Second call for name
                mock_google_drive_service.files().get.assert_any_call(
                    fileId=file_id, fields="name"
                )
                mock_google_drive_service.files().export.assert_called_once_with(
                    fileId=file_id, mimeType="application/zip"
                )

            finally:
                os.chdir(original_cwd)

    def test_export_google_doc_html_file_not_found(self):
        """Test error handling when file doesn't exist."""
        from googleapiclient.errors import HttpError

        file_id = "nonexistent_file_id"

        # Mock HTTP 404 error
        mock_error_response = Mock()
        mock_error_response.status = 404
        mock_http_error = HttpError(mock_error_response, b"File not found")

        # Mock Google service to raise error
        mock_google_drive_service = MagicMock()
        mock_google_drive_service.files().get.side_effect = mock_http_error

        client = DriveClient()
        client.service = mock_google_drive_service

        # Should raise FileNotFoundError
        with pytest.raises(
            FileNotFoundError, match="File with ID nonexistent_file_id not found"
        ):
            client.export(file_id)

    def test_export_google_doc_html_permission_error(self):
        """Test error handling for permission denied."""
        from googleapiclient.errors import HttpError

        file_id = "restricted_file_id"

        # Mock HTTP 403 error
        mock_error_response = Mock()
        mock_error_response.status = 403
        mock_http_error = HttpError(mock_error_response, b"Permission denied")

        # Mock Google service to raise error on export
        mock_google_drive_service = MagicMock()
        mock_google_get_request = MagicMock()
        mock_google_get_request.execute.return_value = {
            "name": "Test Doc",
            "mimeType": "application/vnd.google-apps.document",
        }
        mock_google_drive_service.files().get.return_value = mock_google_get_request
        mock_google_drive_service.files().export.side_effect = mock_http_error

        client = DriveClient()
        client.service = mock_google_drive_service

        # Should raise PermissionError
        with pytest.raises(PermissionError, match="Insufficient permissions"):
            client.export(file_id)

    def test_export_google_doc_html_generic_error(self):
        """Test error handling for generic API errors."""
        from googleapiclient.errors import HttpError

        file_id = "error_file_id"

        # Mock HTTP 500 error (generic server error)
        mock_error_response = Mock()
        mock_error_response.status = 500
        mock_http_error = HttpError(mock_error_response, b"Internal server error")

        # Mock Google service to raise error on export
        mock_google_drive_service = MagicMock()
        mock_google_get_request = MagicMock()
        mock_google_get_request.execute.return_value = {
            "name": "Test Doc",
            "mimeType": "application/vnd.google-apps.document",
        }
        mock_google_drive_service.files().get.return_value = mock_google_get_request
        mock_google_drive_service.files().export.side_effect = mock_http_error

        client = DriveClient()
        client.service = mock_google_drive_service

        # Should raise RuntimeError for generic HTTP errors
        with pytest.raises(RuntimeError, match="Failed to export file"):
            client.export(file_id)

    def test_export_with_format_override(self):
        """Test export with explicit format override."""
        client = DriveClient()

        # Mock the Google Drive API service
        mock_google_drive_service = MagicMock()

        # Mock Google's export request
        mock_google_export_request = MagicMock()
        mock_google_export_request.execute.return_value = b"exported content"
        mock_google_drive_service.files().export.return_value = (
            mock_google_export_request
        )

        # Mock Google's file metadata call for output path
        mock_google_get_request = MagicMock()
        mock_google_get_request.execute.return_value = {"name": "Test Document"}
        mock_google_drive_service.files().get.return_value = mock_google_get_request

        # Setup client with mocked Google service
        client.service = mock_google_drive_service

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.pdf")
            result = client.export("test_id", output_path=output_path, format="pdf")

            # Verify the correct MIME type was used for PDF
            mock_google_drive_service.files().export.assert_called_with(
                fileId="test_id", mimeType="application/pdf"
            )
            assert result == output_path

    def test_export_smart_default_for_google_doc(self):
        """Test smart default format for Google Docs."""
        client = DriveClient()

        # Mock the Google Drive API service
        mock_google_drive_service = MagicMock()

        # Mock Google's export request
        mock_google_export_request = MagicMock()
        mock_google_export_request.execute.return_value = b"exported content"
        mock_google_drive_service.files().export.return_value = (
            mock_google_export_request
        )

        # Mock Google's file metadata call for smart default format detection
        mock_google_get_request = MagicMock()
        mock_google_get_request.execute.return_value = {
            "mimeType": "application/vnd.google-apps.document"
        }
        mock_google_drive_service.files().get.return_value = mock_google_get_request

        # Setup client with mocked Google service
        client.service = mock_google_drive_service

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.html")
            result = client.export("test_id", output_path=output_path)

            # Verify HTML format was used as default for docs
            mock_google_drive_service.files().export.assert_called_with(
                fileId="test_id", mimeType="application/zip"
            )
            assert result == output_path

    def test_export_smart_default_for_google_sheets(self):
        """Test smart default format for Google Sheets."""
        client = DriveClient()

        # Mock the Google Drive API service
        mock_google_drive_service = MagicMock()

        # Mock Google's export request
        mock_google_export_request = MagicMock()
        mock_google_export_request.execute.return_value = b"exported content"
        mock_google_drive_service.files().export.return_value = (
            mock_google_export_request
        )

        # Mock Google's file metadata call for smart default format detection
        mock_google_get_request = MagicMock()
        mock_google_get_request.execute.return_value = {
            "mimeType": "application/vnd.google-apps.spreadsheet"
        }
        mock_google_drive_service.files().get.return_value = mock_google_get_request

        # Setup client with mocked Google service
        client.service = mock_google_drive_service

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.xlsx")
            result = client.export("test_id", output_path=output_path)

            # Verify XLSX format was used as default for sheets
            mock_google_drive_service.files().export.assert_called_with(
                fileId="test_id",
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            assert result == output_path

    def test_export_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        client = DriveClient()

        # Mock the service to avoid authentication
        with patch.object(client, "get_service") as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service

            with pytest.raises(ValueError, match="Unsupported format: invalid_format"):
                client.export("test_id", format="invalid_format")

    @pytest.mark.parametrize("format_type", ["html", "pdf", "xlsx", "csv", "md"])
    def test_export_format_validation_valid_formats(self, format_type):
        """Test format validation for valid formats."""
        client = DriveClient()
        # Should not raise an error
        client._validate_format(format_type)

    def test_export_format_validation_invalid_format(self):
        """Test format validation for invalid format."""
        client = DriveClient()
        # Test invalid format
        with pytest.raises(ValueError, match="Unsupported format: invalid"):
            client._validate_format("invalid")

    @pytest.mark.parametrize(
        "mime_type,expected_format",
        [
            ("application/vnd.google-apps.document", "html"),
            ("application/vnd.google-apps.spreadsheet", "xlsx"),
            ("application/vnd.google-apps.presentation", "pdf"),
            ("application/vnd.google-apps.drawing", "png"),
            ("application/vnd.google-apps.form", "zip"),
            ("application/pdf", "pdf"),  # Non-native file
        ],
    )
    def test_get_smart_default_format(self, mime_type, expected_format):
        """Test smart default format detection for different MIME types."""
        client = DriveClient()

        # Mock the Google Drive API service
        mock_google_drive_service = MagicMock()
        mock_google_get_request = MagicMock()
        mock_google_get_request.execute.return_value = {"mimeType": mime_type}
        mock_google_drive_service.files().get.return_value = mock_google_get_request

        # Setup client with mocked Google service
        client.service = mock_google_drive_service

        result = client._get_smart_default_format("test_id")
        assert result == expected_format

    def test_export_google_doc_to_markdown(self):
        """Test export of Google Doc to markdown format."""
        client = DriveClient()

        # Mock the Google Drive API service
        mock_google_drive_service = MagicMock()

        # Mock Google's export request
        mock_google_export_request = MagicMock()
        mock_google_export_request.execute.return_value = (
            b"# Markdown content\n\nThis is a test document."
        )
        mock_google_drive_service.files().export.return_value = (
            mock_google_export_request
        )

        # Mock Google's file metadata call for output path
        mock_google_get_request = MagicMock()
        mock_google_get_request.execute.return_value = {"name": "Test Document"}
        mock_google_drive_service.files().get.return_value = mock_google_get_request

        # Setup client with mocked Google service
        client.service = mock_google_drive_service

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.md")
            result = client.export("test_id", output_path=output_path, format="md")

            # Verify the correct MIME type was used for markdown
            mock_google_drive_service.files().export.assert_called_with(
                fileId="test_id", mimeType="text/markdown"
            )
            assert result == output_path

            # Verify the content was written correctly
            with open(output_path, "rb") as f:
                content = f.read()
            assert content == b"# Markdown content\n\nThis is a test document."

    def test_get_mime_type_for_markdown_format(self):
        """Test MIME type mapping for markdown format."""
        client = DriveClient()
        mime_type = client._get_mime_type_for_format("md")
        assert mime_type == "text/markdown"

    def test_get_file_extension_for_markdown_format(self):
        """Test file extension mapping for markdown format."""
        client = DriveClient()
        extension = client._get_file_extension_for_format("md")
        assert extension == "md"
