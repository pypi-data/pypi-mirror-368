"""Tests for export CLI commands."""

import tempfile
import os
from unittest.mock import patch, Mock
from click.testing import CliRunner

from zenodotos.cli import cli


class TestExportCommand:
    """Tests for export CLI command."""

    def test_export_with_file_id_only(self):
        """Test export command with only file ID (auto-naming)."""
        runner = CliRunner()

        # Mock the Zenodotos.export_file method
        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.return_value = "My Document.zip"

            result = runner.invoke(cli, ["export", "1abc123"])

            # Verify command executed successfully
            assert result.exit_code == 0
            assert "Successfully exported" in result.output
            assert "My Document.zip" in result.output

            # Verify Zenodotos was called correctly
            mock_zenodotos.export_file.assert_called_once_with(
                "1abc123", output_path=None, format=None
            )

    def test_export_with_output_path(self):
        """Test export command with custom output path."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "custom_name.zip")

            with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
                mock_zenodotos = Mock()
                mock_zenodotos_class.return_value = mock_zenodotos
                mock_zenodotos.export_file.return_value = output_path

                result = runner.invoke(
                    cli, ["export", "1abc123", "--output", output_path]
                )

                assert result.exit_code == 0
                assert "Successfully exported" in result.output
                assert "custom_name.zip" in result.output

                # Verify Zenodotos was called with output path
                mock_zenodotos.export_file.assert_called_once_with(
                    "1abc123", output_path=output_path, format=None
                )

    def test_export_file_not_found(self):
        """Test export command when file doesn't exist."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.side_effect = FileNotFoundError("File not found")

            result = runner.invoke(cli, ["export", "nonexistent123"])

            assert result.exit_code == 1
            assert "Error: File not found" in result.output

    def test_export_permission_error(self):
        """Test export command when user lacks permission."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.side_effect = PermissionError(
                "Permission denied"
            )

            result = runner.invoke(cli, ["export", "restricted123"])

            assert result.exit_code == 1
            assert "Error: Permission denied" in result.output

    def test_export_generic_error(self):
        """Test export command when a generic error occurs."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.side_effect = RuntimeError(
                "API connection failed"
            )

            result = runner.invoke(cli, ["export", "1abc123"])

            assert result.exit_code == 1
            assert "Error: API connection failed" in result.output

    def test_export_missing_file_id_and_query(self):
        """Test export command when neither file ID nor query is provided."""
        runner = CliRunner()

        result = runner.invoke(cli, ["export"])

        assert result.exit_code == 1  # Our custom validation error
        assert "Either FILE_ID or --query must be provided" in result.output

    def test_export_help(self):
        """Test export command help output."""
        runner = CliRunner()

        result = runner.invoke(cli, ["export", "--help"])

        assert result.exit_code == 0
        assert "Export a file from Google Drive" in result.output
        assert "FILE_ID" in result.output

    def test_export_verbose_output(self):
        """Test export command with verbose flag."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.return_value = "My Document.zip"

            result = runner.invoke(cli, ["export", "1abc123", "--verbose"])

            assert result.exit_code == 0
            assert "Exporting file with ID: 1abc123" in result.output
            assert "Successfully exported" in result.output

    def test_export_with_format_option(self):
        """Test export command with format option."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.return_value = "My Document.pdf"

            result = runner.invoke(cli, ["export", "1abc123", "--format", "pdf"])

            assert result.exit_code == 0
            assert "Successfully exported" in result.output

            # Verify Zenodotos was called with format
            mock_zenodotos.export_file.assert_called_once_with(
                "1abc123", output_path=None, format="pdf"
            )

    def test_export_with_invalid_format_option(self):
        """Test export command with invalid format option."""
        runner = CliRunner()

        result = runner.invoke(cli, ["export", "1abc123", "--format", "invalid"])

        assert result.exit_code == 2  # Click's invalid choice error
        assert "Invalid value for '--format'" in result.output

    def test_export_format_option_help(self):
        """Test that format option shows available choices in help."""
        runner = CliRunner()

        result = runner.invoke(cli, ["export", "--help"])

        assert result.exit_code == 0
        assert "html|pdf|xlsx|csv" in result.output

    def test_export_smart_default_no_format_specified(self):
        """Test export command uses smart defaults when no format specified."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.return_value = "My Document.zip"

            result = runner.invoke(cli, ["export", "1abc123"])

            assert result.exit_code == 0
            # Verify Zenodotos was called with format=None (smart default)
            mock_zenodotos.export_file.assert_called_once_with(
                "1abc123", output_path=None, format=None
            )

    # New tests for query-based export functionality
    def test_export_with_query_single_match(self):
        """Test export command with query that returns single match."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.search_and_export.return_value = "My Document.zip"

            result = runner.invoke(
                cli, ["export", "--query", 'name contains "My Document"']
            )

            assert result.exit_code == 0
            assert "Successfully exported" in result.output
            assert "My Document.zip" in result.output

            # Verify search_and_export was called with query
            mock_zenodotos.search_and_export.assert_called_once_with(
                'name contains "My Document"', output_path=None, format=None
            )

    def test_export_with_query_multiple_matches(self):
        """Test export command with query that returns multiple matches."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Create mock DriveFile objects for the exception
            mock_file1 = Mock()
            mock_file1.id = "1abc123def456ghi789jkl012mno345pqr678stu901vwx"
            mock_file1.name = "My Document 1"
            mock_file1.mime_type = "application/vnd.google-apps.document"

            mock_file2 = Mock()
            mock_file2.id = "2def456ghi789jkl012mno345pqr678stu901vwx"
            mock_file2.name = "My Document 2"
            mock_file2.mime_type = "application/vnd.google-apps.document"

            # Mock search_and_export to raise MultipleFilesFoundError
            from zenodotos.exceptions import MultipleFilesFoundError

            mock_zenodotos.search_and_export.side_effect = MultipleFilesFoundError(
                "Multiple files found", files=[mock_file1, mock_file2]
            )

            result = runner.invoke(
                cli, ["export", "--query", 'name contains "Document"']
            )

            assert result.exit_code == 1
            assert "Multiple files found" in result.output
            assert "My Document 1" in result.output
            assert "My Document 2" in result.output
            assert "1abc123def456ghi789jkl012mno345pqr678stu901vwx" in result.output
            assert "2def456ghi789jkl012mno345pqr678stu901vwx" in result.output

    def test_export_with_query_no_matches(self):
        """Test export command with query that returns no matches."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            # Mock search_and_export to raise NoFilesFoundError
            from zenodotos.exceptions import NoFilesFoundError

            mock_zenodotos.search_and_export.side_effect = NoFilesFoundError(
                "No files found"
            )

            result = runner.invoke(
                cli, ["export", "--query", 'name contains "Nonexistent"']
            )

            assert result.exit_code == 1
            assert "No files found" in result.output

            # Verify search_and_export was called
            mock_zenodotos.search_and_export.assert_called_once_with(
                'name contains "Nonexistent"', output_path=None, format=None
            )

    def test_export_mutually_exclusive_file_id_and_query(self):
        """Test that file ID and query options are mutually exclusive."""
        runner = CliRunner()

        result = runner.invoke(
            cli, ["export", "1abc123", "--query", 'name contains "test"']
        )

        assert result.exit_code == 1  # Our custom validation error
        assert "mutually exclusive" in result.output

    def test_export_query_option_help(self):
        """Test that query option is documented in help."""
        runner = CliRunner()

        result = runner.invoke(cli, ["export", "--help"])

        assert result.exit_code == 0
        assert "--query" in result.output
        assert "Search query" in result.output

    def test_export_verbose_single_match(self):
        """Test export command with query and verbose flag for single match."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos

            mock_zenodotos.search_and_export.return_value = "My Document.zip"

            result = runner.invoke(
                cli, ["export", "--query", 'name contains "My Document"', "--verbose"]
            )

            assert result.exit_code == 0
            assert "Searching for files with query" in result.output
            assert "Successfully exported" in result.output

    def test_export_verbose_file_id(self):
        """Test export command with file ID and verbose flag."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            mock_zenodotos.export_file.return_value = "My Document.zip"

            result = runner.invoke(cli, ["export", "1abc123", "--verbose"])

            assert result.exit_code == 0
            assert "Exporting file with ID: 1abc123" in result.output
            assert "Successfully exported" in result.output

    def test_export_generic_exception_handling(self):
        """Test export command handles generic exceptions."""
        runner = CliRunner()

        with patch("zenodotos.cli.commands.Zenodotos") as mock_zenodotos_class:
            mock_zenodotos = Mock()
            mock_zenodotos_class.return_value = mock_zenodotos
            # Raise a generic exception that's not FileNotFoundError, PermissionError, or ValueError
            mock_zenodotos.export_file.side_effect = ConnectionError("Network error")

            result = runner.invoke(cli, ["export", "1abc123"])

            assert result.exit_code == 1
            assert "Error: Network error" in result.output
            assert "Export failed" in result.output
