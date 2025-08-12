# Zenodotos Library API

Zenodotos is not just a CLI tool - it's also a powerful Python library for Google Drive operations. The CLI serves as a real-world example of how to use the library.

## Overview

The Zenodotos library provides a high-level interface for Google Drive operations, making it easy to integrate Google Drive functionality into your Python applications.

### Key Features

- **High-level API**: Simple interface for common Google Drive operations
- **Custom Exceptions**: Specific error types for robust error handling
- **Utility Functions**: Field parsing, file validation, and helper functions
- **Configuration Management**: Environment variables and config file support
- **Backward Compatibility**: All existing CLI functionality preserved

## Quick Start

### Basic Usage

```python
from zenodotos import Zenodotos

# Initialize the library
zenodotos = Zenodotos()

# List files with pagination
files, next_page_token = zenodotos.list_files_with_pagination(page_size=10)

# Get a specific file
file_info = zenodotos.get_file("file_id_here")

# Export a file
zenodotos.export_file("file_id_here", format="pdf")

# Search and export
zenodotos.search_and_export("name contains 'report'", format="pdf")
```

### Error Handling

```python
from zenodotos import Zenodotos, MultipleFilesFoundError, NoFilesFoundError

zenodotos = Zenodotos()

try:
    zenodotos.search_and_export("name = 'specific_file'")
except MultipleFilesFoundError as e:
    print(f"Multiple files found: {e}")
except NoFilesFoundError as e:
    print(f"No files found: {e}")
```

## API Reference

### Zenodotos Class

The main entry point for all library operations.

#### Constructor

```python
Zenodotos()
```

Creates a new Zenodotos instance with default configuration.

#### Methods

##### `list_files_with_pagination(page_size=10, page_token=None, query=None, fields=None)`

List files from Google Drive with pagination support.

**Parameters:**
- `page_size` (int): Number of files per page (default: 10)
- `page_token` (str, optional): Token for specific page access
- `query` (str, optional): Google Drive API query to filter files
- `fields` (str, optional): Comma-separated list of fields to retrieve

**Returns:**
- `tuple`: (files, next_page_token) where files is a list of DriveFile objects

**Example:**
```python
# Basic listing
files, next_token = zenodotos.list_files_with_pagination()

# With query
files, next_token = zenodotos.list_files_with_pagination(
    query="name contains 'report'",
    page_size=20
)

# With custom fields
files, next_token = zenodotos.list_files_with_pagination(
    fields="id,name,size,modifiedTime"
)
```

##### `get_file(file_id, fields=None)`

Get detailed information about a specific file.

**Parameters:**
- `file_id` (str): Google Drive file ID
- `fields` (str, optional): Comma-separated list of fields to retrieve

**Returns:**
- `DriveFile`: File information object

**Example:**
```python
file_info = zenodotos.get_file("1abc123def456ghi789jkl012mno345pqr678stu901vwx")
print(f"File: {file_info.name}, Size: {file_info.size}")
```

##### `export_file(file_id, format=None, output_path=None)`

Export a Google Workspace document.

**Parameters:**
- `file_id` (str): Google Drive file ID
- `format` (str, optional): Export format (html, pdf, xlsx, csv)
- `output_path` (str, optional): Output file path

**Returns:**
- `str`: Path to the exported file

**Example:**
```python
# Auto-detect format
output_file = zenodotos.export_file("1abc123def456ghi789jkl012mno345pqr678stu901vwx")

# Specify format
output_file = zenodotos.export_file(
    "1abc123def456ghi789jkl012mno345pqr678stu901vwx",
    format="pdf",
    output_path="my_document.pdf"
)
```

##### `search_and_export(query, format=None, output_path=None)`

Search for files and export them. Automatically handles single/multiple matches.

**Parameters:**
- `query` (str): Google Drive API query
- `format` (str, optional): Export format
- `output_path` (str, optional): Output file path

**Returns:**
- `str`: Path to the exported file

**Raises:**
- `MultipleFilesFoundError`: When query matches multiple files
- `NoFilesFoundError`: When query matches no files

**Example:**
```python
# Export single match
output_file = zenodotos.search_and_export("name = 'My Document'")

# Export with format
output_file = zenodotos.search_and_export(
    "name contains 'report'",
    format="pdf"
)
```

##### `search_and_get_file(query)`

Search for files and get detailed information about a single match.

**Parameters:**
- `query` (str): Google Drive API query

**Returns:**
- `DriveFile`: File information object

**Raises:**
- `FileNotFoundError`: When query matches no files
- `ValueError`: When query matches multiple files
- `PermissionError`: When user doesn't have permission
- `RuntimeError`: For other API errors

**Example:**
```python
# Get file details by search
file_info = zenodotos.search_and_get_file("name = 'My Document'")
print(f"File: {file_info.name}, Size: {file_info.size}")

# Get file by MIME type
file_info = zenodotos.search_and_get_file("mimeType = 'application/pdf'")
print(f"PDF file: {file_info.name}")
```

##### `get_field_parser()`

Get the FieldParser utility for field handling.

**Returns:**
- `FieldParser`: Field parsing utility

**Example:**
```python
field_parser = zenodotos.get_field_parser()
all_fields, requested_fields = field_parser.parse_fields("id,name,size")
```

## Utility Classes

### FieldParser

Helper class for parsing and validating field options.

#### Methods

##### `parse_fields(fields_str)`

Parse a comma-separated field string and return all fields including required ones.

**Parameters:**
- `fields_str` (str): Comma-separated field names

**Returns:**
- `tuple`: (all_fields, requested_fields) where all_fields includes required fields

**Example:**
```python
parser = FieldParser()
all_fields, requested_fields = parser.parse_fields("id,name,createdTime")
# all_fields: ['id', 'name', 'createdTime', 'mimeType', 'size']
# requested_fields: ['id', 'name', 'createdTime']
```

### DriveFile

Data model representing a Google Drive file.

#### Attributes

- `id`: File ID
- `name`: File name
- `mime_type`: MIME type
- `size`: File size in bytes
- `created_time`: Creation timestamp
- `modified_time`: Last modification timestamp
- `description`: File description
- `owners`: File owners information
- `web_view_link`: Link to view file in Google Drive

## Exception Classes

### ZenodotosException

Base exception for all Zenodotos library errors.

### MultipleFilesFoundError

Raised when a search query matches multiple files.

### NoFilesFoundError

Raised when a search query matches no files.

### FileNotFoundError

Raised when a specific file ID is not found.

### PermissionError

Raised when access to a file is denied.

## Configuration

The library supports configuration through environment variables and config files.

### Environment Variables

- `GOOGLE_DRIVE_CREDENTIALS`: Path to Google Drive API credentials file
- `ZENODOTOS_CONFIG_FILE`: Path to configuration file

### Configuration Files

Supported formats: YAML, TOML, JSON

**Example config.yaml:**
```yaml
google_drive:
  credentials_path: ~/.config/zenodotos/credentials.json
  page_size: 20
  default_fields: "id,name,mimeType,size"
```

## Advanced Usage

### Custom Field Selection

```python
from zenodotos import Zenodotos

zenodotos = Zenodotos()

# Get field parser for custom field handling
field_parser = zenodotos.get_field_parser()

# Parse user-specified fields
all_fields, requested_fields = field_parser.parse_fields("id,name,size,modifiedTime")

# Use in list operation
files, next_token = zenodotos.list_files_with_pagination(fields=",".join(all_fields))
```

### Batch Operations

```python
from zenodotos import Zenodotos

zenodotos = Zenodotos()

# List all files (handle pagination)
all_files = []
page_token = None

while True:
    files, page_token = zenodotos.list_files_with_pagination(
        page_size=100,
        page_token=page_token
    )
    all_files.extend(files)

    if not page_token:
        break

print(f"Total files: {len(all_files)}")
```

### Error Handling Patterns

```python
from zenodotos import Zenodotos, MultipleFilesFoundError, NoFilesFoundError

zenodotos = Zenodotos()

def export_report(report_name):
    try:
        return zenodotos.search_and_export(f"name = '{report_name}'")
    except MultipleFilesFoundError:
        print(f"Multiple reports found with name '{report_name}'")
        return None
    except NoFilesFoundError:
        print(f"No report found with name '{report_name}'")
        return None
    except Exception as e:
        print(f"Export failed: {e}")
        return None
```

## Integration Examples

### Web Application Integration

```python
from flask import Flask, jsonify
from zenodotos import Zenodotos, NoFilesFoundError

app = Flask(__name__)
zenodotos = Zenodotos()

@app.route('/files')
def list_files():
    try:
        files, _ = zenodotos.list_files_with_pagination(page_size=50)
        return jsonify([{
            'id': f.id,
            'name': f.name,
            'size': f.size,
            'modified': f.modified_time
        } for f in files])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export/<file_id>')
def export_file(file_id):
    try:
        output_path = zenodotos.export_file(file_id, format='pdf')
        return jsonify({'exported_to': output_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Data Processing Pipeline

```python
from zenodotos import Zenodotos
import pandas as pd

zenodotos = Zenodotos()

def process_spreadsheets():
    # Find all Google Sheets
    files, _ = zenodotos.list_files_with_pagination(
        query="mimeType='application/vnd.google-apps.spreadsheet'"
    )

    for file in files:
        try:
            # Export as CSV for processing
            csv_path = zenodotos.export_file(file.id, format='csv')

            # Process with pandas
            df = pd.read_csv(csv_path)
            # ... data processing ...

        except Exception as e:
            print(f"Failed to process {file.name}: {e}")
```

## Migration from CLI

If you're currently using the CLI and want to integrate Zenodotos into your Python code:

### Before (CLI)
```bash
zenodotos list-files --query "name contains 'report'" --fields "id,name,size"
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format pdf
```

### After (Library)
```python
from zenodotos import Zenodotos

zenodotos = Zenodotos()

# List files
files, _ = zenodotos.list_files_with_pagination(
    query="name contains 'report'",
    fields="id,name,size"
)

# Export file
output_path = zenodotos.export_file(
    "1abc123def456ghi789jkl012mno345pqr678stu901vwx",
    format="pdf"
)
```

## Best Practices

1. **Error Handling**: Always handle specific exceptions for robust applications
2. **Field Selection**: Use FieldParser for consistent field handling
3. **Pagination**: Handle pagination properly for large file lists
4. **Configuration**: Use environment variables for sensitive configuration
5. **Testing**: Test with real Google Drive files for integration testing

## Related Documentation

- [CLI Commands](commands.md) - Command-line interface documentation
- [Installation Guide](installation.md) - Setup and configuration
- [User Quick Start](user-quickstart.md) - Getting started with CLI
