"""Tests for the Zenodotos library components."""

import pytest
from unittest.mock import Mock, patch
from zenodotos import Zenodotos, FieldParser
from zenodotos.drive.models import DriveFile
from datetime import datetime


class TestZenodotos:
    """Test the high-level Zenodotos client."""

    def test_zenodotos_initialization(self):
        """Test Zenodotos client initialization."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            zenodotos = Zenodotos()
            assert zenodotos._client is not None
            assert isinstance(zenodotos._client, Mock)

    def test_zenodotos_initialization_with_credentials_path(self):
        """Test Zenodotos client initialization with custom credentials path."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            credentials_path = "/custom/path/credentials.json"
            zenodotos = Zenodotos(credentials_path=credentials_path)

            assert zenodotos._client is not None
            assert isinstance(zenodotos._client, Mock)
            mock_client_class.assert_called_once_with(credentials_path=credentials_path)

    def test_list_files_basic(self):
        """Test basic list_files functionality."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock the response
            mock_file = DriveFile(
                id="test123",
                name="test.txt",
                mime_type="text/plain",
                size=1024,
            )
            mock_client.list_files.return_value = {
                "files": [mock_file],
                "next_page_token": None,
            }

            zenodotos = Zenodotos()
            result = zenodotos.list_files(page_size=10)

            assert result == [mock_file]
            mock_client.list_files.assert_called_once_with(
                page_size=10, query=None, fields=None
            )

    def test_list_files_with_query(self):
        """Test list_files with query parameter."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_file = DriveFile(
                id="test123",
                name="report.pdf",
                mime_type="application/pdf",
                size=2048,
            )
            mock_client.list_files.return_value = {
                "files": [mock_file],
                "next_page_token": None,
            }

            zenodotos = Zenodotos()
            result = zenodotos.list_files(
                page_size=20, query="name contains 'report'", fields=["name", "size"]
            )

            assert result == [mock_file]
            mock_client.list_files.assert_called_once_with(
                page_size=20, query="name contains 'report'", fields=["name", "size"]
            )

    def test_list_files_with_pagination(self):
        """Test list_files_with_pagination returns full result."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_file = DriveFile(
                id="test123",
                name="test.txt",
                mime_type="text/plain",
                size=1024,
            )
            expected_result = {
                "files": [mock_file],
                "next_page_token": "next_token_123",
            }
            mock_client.list_files.return_value = expected_result

            zenodotos = Zenodotos()
            result = zenodotos.list_files_with_pagination(
                page_size=10, page_token="current_token", query="test query"
            )

            assert result == expected_result
            mock_client.list_files.assert_called_once_with(
                page_size=10,
                page_token="current_token",
                query="test query",
                fields=None,
            )

    def test_get_file(self):
        """Test get_file functionality."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_file = DriveFile(
                id="test123",
                name="test.txt",
                mime_type="text/plain",
                size=1024,
                created_time=datetime(2024, 1, 1),
                modified_time=datetime(2024, 1, 2),
            )
            mock_client.get_file.return_value = mock_file

            zenodotos = Zenodotos()
            result = zenodotos.get_file("test123")

            assert result == mock_file
            mock_client.get_file.assert_called_once_with("test123")

    def test_export_file(self):
        """Test export_file functionality."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_client.export.return_value = "/path/to/exported/file.pdf"

            zenodotos = Zenodotos()
            result = zenodotos.export_file(
                "test123", output_path="/custom/path.pdf", format="pdf"
            )

            assert result == "/path/to/exported/file.pdf"
            mock_client.export.assert_called_once_with(
                "test123", "/custom/path.pdf", "pdf"
            )

    def test_search_and_export_single_match(self):
        """Test search_and_export with single match."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock list_files response
            mock_file = DriveFile(
                id="test123",
                name="report.pdf",
                mime_type="application/pdf",
                size=2048,
            )
            mock_client.list_files.return_value = {
                "files": [mock_file],
                "next_page_token": None,
            }

            # Mock export response
            mock_client.export.return_value = "/path/to/exported/report.pdf"

            zenodotos = Zenodotos()
            result = zenodotos.search_and_export(
                "name contains 'report'", output_path="/custom/path.pdf", format="pdf"
            )

            assert result == "/path/to/exported/report.pdf"
            mock_client.list_files.assert_called_once_with(
                page_size=100, query="name contains 'report'", fields=None
            )
            mock_client.export.assert_called_once_with(
                "test123", "/custom/path.pdf", "pdf"
            )

    def test_search_and_export_no_matches(self):
        """Test search_and_export with no matches."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            mock_client.list_files.return_value = {"files": [], "next_page_token": None}

            zenodotos = Zenodotos()
            with pytest.raises(
                FileNotFoundError, match="No files found matching the query"
            ):
                zenodotos.search_and_export("name contains 'nonexistent'")

    def test_search_and_export_multiple_matches(self):
        """Test search_and_export with multiple matches."""
        with patch("zenodotos.client.DriveClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock multiple files
            mock_file1 = DriveFile(
                id="test123", name="report1.pdf", mime_type="application/pdf"
            )
            mock_file2 = DriveFile(
                id="test456", name="report2.pdf", mime_type="application/pdf"
            )
            mock_client.list_files.return_value = {
                "files": [mock_file1, mock_file2],
                "next_page_token": None,
            }

            zenodotos = Zenodotos()
            with pytest.raises(
                ValueError, match="Multiple files found \\(2 matches\\)"
            ):
                zenodotos.search_and_export("name contains 'report'")

    def test_get_field_parser(self):
        """Test get_field_parser returns FieldParser instance."""
        with patch("zenodotos.client.DriveClient"):
            zenodotos = Zenodotos()
            field_parser = zenodotos.get_field_parser()

            assert isinstance(field_parser, FieldParser)


class TestFieldParser:
    """Test the FieldParser utility class."""

    def test_field_parser_initialization(self):
        """Test FieldParser initialization."""
        parser = FieldParser()

        assert parser.required_fields == {"name", "mimeType", "size"}
        assert len(parser.default_fields) == 9
        assert "id" in parser.default_fields
        assert "name" in parser.default_fields
        assert "mimeType" in parser.default_fields

    def test_parse_fields_none(self):
        """Test parse_fields with None input."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields(None)

        assert all_fields == parser.default_fields
        assert requested_fields is None

    def test_parse_fields_empty_string(self):
        """Test parse_fields with empty string."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields("")

        assert all_fields == parser.default_fields
        assert requested_fields is None

    def test_parse_fields_single_field(self):
        """Test parse_fields with single field."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields("name")

        # Should include required fields
        assert "name" in all_fields
        assert "mimeType" in all_fields
        assert "size" in all_fields
        assert requested_fields == ["name"]

    def test_parse_fields_multiple_fields(self):
        """Test parse_fields with multiple fields."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields("id,name,size")

        # Should preserve order and include required fields
        assert all_fields == ["id", "name", "size", "mimeType"]
        assert requested_fields == ["id", "name", "size"]

    def test_parse_fields_with_duplicates(self):
        """Test parse_fields removes duplicates while preserving order."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields("name,id,name,size")

        # Should remove duplicate 'name' but preserve order
        assert all_fields == ["name", "id", "size", "mimeType"]
        assert requested_fields == ["name", "id", "size"]

    def test_parse_fields_with_whitespace(self):
        """Test parse_fields handles whitespace correctly."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields("  name  ,  id  ,  size  ")

        assert all_fields == ["name", "id", "size", "mimeType"]
        assert requested_fields == ["name", "id", "size"]

    def test_parse_fields_with_required_fields_already_present(self):
        """Test parse_fields when required fields are already in user input."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields("name,mimeType,size,id")

        # Should not duplicate required fields
        assert all_fields == ["name", "mimeType", "size", "id"]
        assert requested_fields == ["name", "mimeType", "size", "id"]

    def test_parse_fields_complex_scenario(self):
        """Test parse_fields with complex field combination."""
        parser = FieldParser()
        all_fields, requested_fields = parser.parse_fields(
            "createdTime,id,modifiedTime,name"
        )

        # Should preserve user order and add missing required fields
        # Check that user fields are in correct order
        assert all_fields[:4] == ["createdTime", "id", "modifiedTime", "name"]
        # Check that required fields are present (order may vary)
        assert "mimeType" in all_fields
        assert "size" in all_fields
        assert len(all_fields) == 6
        assert requested_fields == ["createdTime", "id", "modifiedTime", "name"]
