"""Tests for utility functions."""

from zenodotos.utils import (
    FieldParser,
    validate_file_id,
    sanitize_filename,
    format_file_size,
)


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


class TestValidateFileId:
    """Test the validate_file_id function."""

    def test_valid_file_id(self):
        """Test valid Google Drive file ID."""
        valid_ids = [
            "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            "1abc123def456ghi789jkl012mno345pqr678stu901vwx",
            "1abc-def_ghi-jkl_mno-pqr_stu-vwx_yz",
        ]

        for file_id in valid_ids:
            assert validate_file_id(file_id) is True

    def test_invalid_file_id_too_short(self):
        """Test file ID that's too short."""
        assert validate_file_id("123") is False
        assert validate_file_id("abc123") is False

    def test_invalid_file_id_too_long(self):
        """Test file ID that's too long."""
        long_id = "1" + "a" * 50  # 51 characters
        assert validate_file_id(long_id) is False

    def test_invalid_file_id_invalid_characters(self):
        """Test file ID with invalid characters."""
        invalid_ids = [
            "1abc@def",
            "1abc#def",
            "1abc$def",
            "1abc%def",
            "1abc^def",
            "1abc&def",
            "1abc*def",
            "1abc(def",
            "1abc)def",
            "1abc+def",
            "1abc=def",
            "1abc[def",
            "1abc]def",
            "1abc{def",
            "1abc}def",
            "1abc|def",
            "1abc\\def",
            "1abc;def",
            "1abc:def",
            "1abc'def",
            '1abc"def',
            "1abc,def",
            "1abc.def",
            "1abc<def",
            "1abc>def",
            "1abc/def",
            "1abc?def",
        ]

        for file_id in invalid_ids:
            assert validate_file_id(file_id) is False

    def test_invalid_file_id_none(self):
        """Test file ID that's None."""
        assert validate_file_id(None) is False

    def test_invalid_file_id_empty(self):
        """Test empty file ID."""
        assert validate_file_id("") is False

    def test_invalid_file_id_not_string(self):
        """Test file ID that's not a string."""
        assert validate_file_id(123) is False
        assert validate_file_id([]) is False
        assert validate_file_id({}) is False


class TestSanitizeFilename:
    """Test the sanitize_filename function."""

    def test_valid_filename(self):
        """Test filename that doesn't need sanitization."""
        valid_names = [
            "document.pdf",
            "my_file.txt",
            "report-2024.xlsx",
            "presentation.pptx",
            "image.jpg",
        ]

        for filename in valid_names:
            assert sanitize_filename(filename) == filename

    def test_filename_with_invalid_characters(self):
        """Test filename with invalid characters."""
        test_cases = [
            ("file<name>.txt", "file_name_.txt"),
            ("file:name.txt", "file_name.txt"),
            ("file/name.txt", "file_name.txt"),
            ("file\\name.txt", "file_name.txt"),
            ("file|name.txt", "file_name.txt"),
            ("file?name.txt", "file_name.txt"),
            ("file*name.txt", "file_name.txt"),
            ('file"name.txt', "file_name.txt"),
        ]

        for input_name, expected in test_cases:
            assert sanitize_filename(input_name) == expected

    def test_filename_with_leading_trailing_spaces(self):
        """Test filename with leading/trailing spaces."""
        assert sanitize_filename("  filename.txt  ") == "filename.txt"

    def test_filename_with_leading_trailing_dots(self):
        """Test filename with leading/trailing dots."""
        assert sanitize_filename("...filename.txt...") == "filename.txt"

    def test_filename_too_long(self):
        """Test filename that's too long."""
        long_name = "a" * 250
        sanitized = sanitize_filename(long_name)
        assert len(sanitized) == 200
        assert sanitized == "a" * 200

    def test_empty_filename(self):
        """Test empty filename."""
        assert sanitize_filename("") == "untitled"
        assert sanitize_filename("   ") == "untitled"

    def test_filename_with_only_invalid_characters(self):
        """Test filename with only invalid characters."""
        assert sanitize_filename('<>:"/\\|?*') == "_________"
        assert sanitize_filename("...") == "untitled"


class TestFormatFileSize:
    """Test the format_file_size function."""

    def test_zero_size(self):
        """Test zero file size."""
        assert format_file_size(0) == "0 B"

    def test_none_size(self):
        """Test None file size."""
        assert format_file_size(None) == "Unknown"

    def test_bytes(self):
        """Test file sizes in bytes."""
        assert format_file_size(1) == "1 B"
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"

    def test_kilobytes(self):
        """Test file sizes in kilobytes."""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"
        assert format_file_size(2048) == "2.0 KB"
        assert format_file_size(1048575) == "1024.0 KB"

    def test_megabytes(self):
        """Test file sizes in megabytes."""
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(1572864) == "1.5 MB"
        assert format_file_size(2097152) == "2.0 MB"
        assert format_file_size(1073741823) == "1024.0 MB"

    def test_gigabytes(self):
        """Test file sizes in gigabytes."""
        assert format_file_size(1073741824) == "1.0 GB"
        assert format_file_size(1610612736) == "1.5 GB"
        assert format_file_size(2147483648) == "2.0 GB"

    def test_terabytes(self):
        """Test file sizes in terabytes."""
        assert format_file_size(1099511627776) == "1.0 TB"
        assert format_file_size(1649267441664) == "1.5 TB"
        assert format_file_size(2199023255552) == "2.0 TB"

    def test_large_sizes(self):
        """Test very large file sizes."""
        # 5 TB
        assert format_file_size(5497558138880) == "5.0 TB"
        # 10 GB
        assert format_file_size(10737418240) == "10.0 GB"
        # 100 MB
        assert format_file_size(104857600) == "100.0 MB"
