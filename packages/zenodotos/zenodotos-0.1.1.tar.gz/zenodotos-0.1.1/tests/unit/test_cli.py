"""Tests for CLI commands."""

from click.testing import CliRunner
from unittest.mock import Mock, patch
from zenodotos.cli import cli
from zenodotos.drive.models import DriveFile
from datetime import datetime


class TestListFiles:
    """Test the list-files command."""

    def test_basic_usage(self):
        """Test basic list-files command."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                ["id", "name", "mimeType", "size", "createdTime", "modifiedTime"],
                ["id", "name", "mimeType", "size", "createdTime", "modifiedTime"],
            )

            # Mock the list_files_with_pagination response
            mock_file = DriveFile(
                id="test123",
                name="test.txt",
                mime_type="text/plain",
                size=1024,
                created_time=datetime(2024, 1, 1),
                modified_time=datetime(2024, 1, 2),
            )
            mock_zenodotos.list_files_with_pagination.return_value = {
                "files": [mock_file],
                "next_page_token": None,
            }

            result = runner.invoke(cli, ["list-files", "--no-interactive"])

            assert result.exit_code == 0
            assert "test.txt" in result.output
            assert "text/plain" in result.output
            assert "1,024" in result.output

    def test_with_query(self):
        """Test list-files with query parameter."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                ["id", "name", "mimeType", "size"],
                ["id", "name", "mimeType", "size"],
            )

            mock_file = DriveFile(
                id="test123",
                name="report.pdf",
                mime_type="application/pdf",
                size=2048,
            )
            mock_zenodotos.list_files_with_pagination.return_value = {
                "files": [mock_file],
                "next_page_token": None,
            }

            result = runner.invoke(
                cli,
                ["list-files", "--query", "name contains 'report'", "--no-interactive"],
            )

            assert result.exit_code == 0
            mock_zenodotos.list_files_with_pagination.assert_called_once()
            call_args = mock_zenodotos.list_files_with_pagination.call_args
            assert call_args[1]["query"] == "name contains 'report'"

    def test_with_custom_fields(self):
        """Test list-files with custom fields."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                ["name", "size", "createdTime", "mimeType"],
                ["name", "size", "createdTime"],
            )

            mock_file = DriveFile(
                id="test123",
                name="test.txt",
                mime_type="text/plain",
                size=1024,
                created_time=datetime(2024, 1, 1),
            )
            mock_zenodotos.list_files_with_pagination.return_value = {
                "files": [mock_file],
                "next_page_token": None,
            }

            result = runner.invoke(
                cli,
                ["list-files", "--fields", "name,size,createdTime", "--no-interactive"],
            )

            assert result.exit_code == 0
            mock_zenodotos.list_files_with_pagination.assert_called_once()
            call_args = mock_zenodotos.list_files_with_pagination.call_args
            # Should include required fields (name, mimeType, size) plus requested fields
            expected_fields = ["name", "size", "createdTime", "mimeType"]
            assert all(field in call_args[1]["fields"] for field in expected_fields)


class TestGetFile:
    """Test the get-file command."""

    def test_basic_usage(self):
        """Test basic get-file command."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                [
                    "id",
                    "name",
                    "mimeType",
                    "size",
                    "createdTime",
                    "modifiedTime",
                    "description",
                    "owners",
                    "webViewLink",
                ],
                [
                    "id",
                    "name",
                    "mimeType",
                    "size",
                    "createdTime",
                    "modifiedTime",
                    "description",
                    "owners",
                    "webViewLink",
                ],
            )

            # Mock the get_file response
            mock_file = DriveFile(
                id="test123",
                name="test.txt",
                mime_type="text/plain",
                size=1024,
                created_time=datetime(2024, 1, 1),
                modified_time=datetime(2024, 1, 2),
                description="Test file",
                owners=[{"displayName": "Test User"}],
                web_view_link="https://drive.google.com/file/d/test123/view",
            )
            mock_zenodotos.get_file.return_value = mock_file

            result = runner.invoke(cli, ["get-file", "test123"])

            assert result.exit_code == 0
            assert "test.txt" in result.output
            assert "text/plain" in result.output
            assert "1,024" in result.output
            mock_zenodotos.get_file.assert_called_once_with("test123")

    def test_with_custom_fields(self):
        """Test get-file with custom fields."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                ["name", "description", "createdTime", "mimeType"],
                ["name", "description", "createdTime"],
            )

            mock_file = DriveFile(
                id="test123",
                name="test.txt",
                mime_type="text/plain",
                size=1024,
                created_time=datetime(2024, 1, 1),
                description="Test file",
            )
            mock_zenodotos.get_file.return_value = mock_file

            result = runner.invoke(
                cli, ["get-file", "test123", "--fields", "name,description,createdTime"]
            )

            assert result.exit_code == 0
            assert "test.txt" in result.output
            assert "Test file" in result.output
            mock_zenodotos.get_file.assert_called_once_with("test123")

    def test_file_not_found(self):
        """Test get-file with non-existent file."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                ["id", "name", "mimeType", "size"],
                ["id", "name", "mimeType", "size"],
            )

            mock_zenodotos.get_file.side_effect = FileNotFoundError(
                "File with ID test123 not found."
            )

            result = runner.invoke(cli, ["get-file", "test123"])

            assert result.exit_code == 1
            assert "File not found" in result.output
            assert "File with ID test123 not found" in result.output

    def test_permission_error(self):
        """Test get-file with permission error."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                ["id", "name", "mimeType", "size"],
                ["id", "name", "mimeType", "size"],
            )

            mock_zenodotos.get_file.side_effect = PermissionError(
                "Insufficient permissions to access the file."
            )

            result = runner.invoke(cli, ["get-file", "test123"])

            assert result.exit_code == 1
            assert "Permission denied" in result.output
            assert "Insufficient permissions to access the file" in result.output

    def test_general_error(self):
        """Test get-file with general error."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the field parser
            mock_field_parser = Mock()
            mock_zenodotos.get_field_parser.return_value = mock_field_parser
            mock_field_parser.parse_fields.return_value = (
                ["id", "name", "mimeType", "size"],
                ["id", "name", "mimeType", "size"],
            )

            mock_zenodotos.get_file.side_effect = Exception("Unexpected error")

            result = runner.invoke(cli, ["get-file", "test123"])

            assert result.exit_code == 1
            assert "Failed to get file" in result.output
            assert "Unexpected error" in result.output

    def test_missing_file_id(self):
        """Test get-file without file ID."""
        runner = CliRunner()
        result = runner.invoke(cli, ["get-file"])

        assert result.exit_code == 2  # Click error code for missing required argument
        assert "Missing argument 'FILE_ID'" in result.output

    def test_help(self):
        """Test get-file help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["get-file", "--help"])

        assert result.exit_code == 0
        assert "Get detailed information about a specific file" in result.output
        assert "--fields" in result.output


class TestExport:
    """Test the export command."""

    def test_basic_usage(self):
        """Test basic export command."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.export_file.return_value = "/path/to/exported/file.pdf"

            result = runner.invoke(cli, ["export", "test123"])

            assert result.exit_code == 0
            assert (
                "Successfully exported to: /path/to/exported/file.pdf" in result.output
            )
            mock_zenodotos.export_file.assert_called_once_with(
                "test123", output_path=None, format=None
            )

    def test_with_format(self):
        """Test export with specific format."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.export_file.return_value = "/path/to/exported/file.pdf"

            result = runner.invoke(cli, ["export", "test123", "--format", "pdf"])

            assert result.exit_code == 0
            mock_zenodotos.export_file.assert_called_once_with(
                "test123", output_path=None, format="pdf"
            )

    def test_with_output_path(self):
        """Test export with output path."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.export_file.return_value = "/custom/path/file.pdf"

            result = runner.invoke(
                cli, ["export", "test123", "--output", "/custom/path/file.pdf"]
            )

            assert result.exit_code == 0
            mock_zenodotos.export_file.assert_called_once_with(
                "test123", output_path="/custom/path/file.pdf", format=None
            )

    def test_with_query_single_match(self):
        """Test export with query that finds single match."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.search_and_export.return_value = "/path/to/exported/file.pdf"

            result = runner.invoke(cli, ["export", "--query", "name contains 'report'"])

            assert result.exit_code == 0
            assert (
                "Successfully exported to: /path/to/exported/file.pdf" in result.output
            )
            mock_zenodotos.search_and_export.assert_called_once_with(
                "name contains 'report'", output_path=None, format=None
            )

    def test_with_query_multiple_matches(self):
        """Test export with query that finds multiple matches."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock the MultipleFilesFoundError with files
            mock_file1 = DriveFile(
                id="test123", name="report1.pdf", mime_type="application/pdf"
            )
            mock_file2 = DriveFile(
                id="test456", name="report2.pdf", mime_type="application/pdf"
            )
            from zenodotos.exceptions import MultipleFilesFoundError

            mock_zenodotos.search_and_export.side_effect = MultipleFilesFoundError(
                "Multiple files found", files=[mock_file1, mock_file2]
            )

            result = runner.invoke(cli, ["export", "--query", "name contains 'report'"])

            assert result.exit_code == 1
            assert "Multiple files found" in result.output
            assert "test123 - report1.pdf" in result.output
            assert "test456 - report2.pdf" in result.output

    def test_with_query_no_matches(self):
        """Test export with query that finds no matches."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            from zenodotos.exceptions import NoFilesFoundError

            mock_zenodotos.search_and_export.side_effect = NoFilesFoundError(
                "No files found"
            )

            result = runner.invoke(
                cli, ["export", "--query", "name contains 'nonexistent'"]
            )

            assert result.exit_code == 1
            assert "No files found" in result.output

    def test_missing_file_id_and_query(self):
        """Test export without file ID or query."""
        runner = CliRunner()
        result = runner.invoke(cli, ["export"])

        assert result.exit_code == 1
        assert "Either FILE_ID or --query must be provided" in result.output

    def test_both_file_id_and_query(self):
        """Test export with both file ID and query."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["export", "test123", "--query", "name contains 'test'"]
        )

        assert result.exit_code == 1
        assert "FILE_ID and --query are mutually exclusive" in result.output

    def test_file_not_found(self):
        """Test export with non-existent file."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.export_file.side_effect = FileNotFoundError("File not found")

            result = runner.invoke(cli, ["export", "test123"])

            assert result.exit_code == 1
            assert "File not found" in result.output

    def test_permission_error(self):
        """Test export with permission error."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.export_file.side_effect = PermissionError(
                "Permission denied"
            )

            result = runner.invoke(cli, ["export", "test123"])

            assert result.exit_code == 1
            assert "Permission denied" in result.output

    def test_invalid_format(self):
        """Test export with invalid format."""
        runner = CliRunner()
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.export_file.side_effect = ValueError("Invalid format")

            result = runner.invoke(cli, ["export", "test123"])

            assert result.exit_code == 1
            assert "Invalid format" in result.output
