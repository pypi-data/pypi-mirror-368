# Zenodotos

A command-line interface tool for interacting with Google Drive, providing a simple and efficient way to manage your files and folders.

## Features

- **Interactive file browsing** with intuitive pagination controls
- List files and folders in Google Drive with advanced filtering
- View detailed file information
- **Smart pagination** with next/previous page navigation
- Advanced search and query capabilities
- Beautiful, clean terminal output
- **Token-based pagination** support for large datasets
- Flexible field selection for customized output
- **Export Google Workspace documents** with smart format defaults
- **Format override options** for custom export preferences

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/zenodotos.git
   cd zenodotos
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Configuration

### Google Drive API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Download the credentials JSON file

### Credentials File

You can provide your Google Drive API credentials in two ways:

1. **Default Location:**
   Place the downloaded credentials file at:
   ```
   ~/.config/zenodotos/credentials.json
   ```

2. **Custom Location:**
   Set the `GOOGLE_DRIVE_CREDENTIALS` environment variable to point to your credentials file:
   ```bash
   # Linux/macOS
   export GOOGLE_DRIVE_CREDENTIALS="/path/to/your/credentials.json"

   # Windows (PowerShell)
   $env:GOOGLE_DRIVE_CREDENTIALS="C:\path\to\your\credentials.json"

   # Windows (Command Prompt)
   set GOOGLE_DRIVE_CREDENTIALS=C:\path\to\your\credentials.json
   ```

## Usage

### Interactive File Browsing

**New!** Zenodotos now provides an interactive pagination experience by default:

```bash
zenodotos list-files
```

This will show your files with a clean navigation interface:
```
My Document.pdf (1.2 MB) - PDF - Modified: 2024-01-15
Project Report.docx (856 KB) - Word - Modified: 2024-01-14
...
[P]rev [N]ext [Q]uit: _
```

**Navigation:**
- **N** or **n**: Go to next page
- **P** or **p**: Go to previous page
- **Q** or **q**: Quit and return to command line

### Non-Interactive Mode

For scripting or automated use, disable interactive mode:
```bash
zenodotos list-files --no-interactive
```

### List Files Options

All list-files options work in both interactive and non-interactive modes:

- `--page-size`: Number of files per page (default: 10)
- `--page-token`: Specific page token for direct page access
- `--query`: Search query to filter files
- `--fields`: Custom field selection for output
- `--no-interactive`: Disable interactive pagination

#### Advanced Search Examples

**Interactive search with pagination:**
```bash
# Search for PDFs interactively
zenodotos list-files --query "mimeType='application/pdf'"

# Find files modified in the last week (interactive)
zenodotos list-files --query "modifiedTime > '2024-01-01'"

# Complex search with multiple conditions
zenodotos list-files --query "name contains 'report' and mimeType='application/pdf'"
```

**Non-interactive with specific pages:**
```bash
# Get exactly 20 files, no interaction
zenodotos list-files --page-size 20 --no-interactive

# Use page token for specific page access
zenodotos list-files --page-token "ABC123token" --no-interactive
```

#### Field Customization

**Default fields:** `id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink`

Choose exactly what information you want to see:

```bash
# Use default fields (comprehensive output)
zenodotos list-files

# Minimal output - just names and sizes
zenodotos list-files --fields "name,size"

# Detailed output with timestamps and owners
zenodotos list-files --fields "name,size,modifiedTime,createdTime,owners"

# Full metadata output (same as default)
zenodotos list-files --fields "id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink"
```

#### Available Fields
The `--fields` option accepts any combination of these Google Drive API fields:
- `id`: File ID
- `name`: File name
- `mimeType`: MIME type of the file
- `size`: File size in bytes
- `createdTime`: Creation timestamp
- `modifiedTime`: Last modification timestamp
- `description`: File description
- `owners`: File owners information
- `webViewLink`: Link to view the file in Google Drive
- And many others supported by the Google Drive API

**Note:** The fields `name`, `mimeType`, and `size` are always included to ensure proper display formatting.

### View File Details

Get detailed information about a specific file. You can use either a file ID or a search query:

```bash
# Get file details by ID
zenodotos get-file <file_id>

# Get file details by search query
zenodotos get-file --query "name contains 'My Document'"
```

Example:
```bash
zenodotos get-file 1abc...xyz
```

#### Query-Based File Retrieval

Get file details by searching for them instead of using file IDs:

```bash
# Get file by exact name
zenodotos get-file --query "name = 'My Important Document'"

# Get file containing specific text
zenodotos get-file --query "name contains 'report'"

# Get file by MIME type
zenodotos get-file --query "mimeType = 'application/vnd.google-apps.document'"

# Get file modified recently
zenodotos get-file --query "modifiedTime > '2024-01-01'"
```

#### Customize Output Fields

Choose exactly what information you want to see:

```bash
# Use default fields (comprehensive output)
zenodotos get-file <file_id>

# Minimal output - just names and sizes
zenodotos get-file <file_id> --fields "name,size"

# Detailed output with timestamps and owners
zenodotos get-file <file_id> --fields "name,size,modifiedTime,createdTime,owners"

# Full metadata output (same as default)
zenodotos get-file <file_id> --fields "id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink"
```

#### Available Fields
The `--fields` option accepts any combination of these Google Drive API fields:
- `id`: File ID
- `name`: File name
- `mimeType`: MIME type of the file
- `size`: File size in bytes
- `createdTime`: Creation timestamp
- `modifiedTime`: Last modification timestamp
- `description`: File description
- `owners`: File owners information
- `webViewLink`: Link to view the file in Google Drive

**Note:** The fields `name`, `mimeType`, and `size` are always included to ensure proper display formatting.

### Export Files

Export Google Workspace documents with smart format defaults. You can export files using either a file ID or a search query:

```bash
# Export by file ID (automatic format selection)
zenodotos export <file_id>

# Export by search query (finds and exports single match)
zenodotos export --query "name contains 'My Document'"

# Export with custom format
zenodotos export <file_id> --format pdf

# Export to specific output path
zenodotos export <file_id> --output "my-document.pdf"

# Export with verbose output
zenodotos export <file_id> --verbose
```

#### Smart Format Defaults

Zenodotos automatically selects the optimal export format based on file type:

- **Google Docs** → HTML (ZIP file with embedded resources)
- **Google Sheets** → XLSX (Excel format)
- **Google Slides** → PDF
- **Google Drawings** → PNG
- **Google Forms** → ZIP (HTML export)

#### Query-Based Export

Export files by searching for them instead of using file IDs:

```bash
# Export a single file by name
zenodotos export --query "name = 'My Important Document'"

# Export files containing specific text
zenodotos export --query "name contains 'report'"

# Export files by MIME type
zenodotos export --query "mimeType = 'application/vnd.google-apps.document'"

# Export files modified recently
zenodotos export --query "modifiedTime > '2024-01-01'"
```

**Query Behavior:**
- **Single match**: Automatically exports the found file
- **Multiple matches**: Shows all matching files with IDs and names for you to choose
- **No matches**: Displays an appropriate error message

**Note:** File ID and query options are mutually exclusive - use one or the other.

#### Supported Formats

Override the default format with these options:
- `html`: HTML export (ZIP file for Google Docs)
- `pdf`: PDF export
- `xlsx`: Excel format (for spreadsheets)
- `csv`: CSV format (for spreadsheets)

#### Examples

```bash
# Export a Google Doc to HTML (default)
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx

# Export a Google Sheet to Excel
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format xlsx

# Export a presentation to PDF
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format pdf

# Export to a specific filename
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --output "My Report.pdf"
```

### Help

Get help on available commands:
```bash
zenodotos --help
```

Get help on specific commands:
```bash
zenodotos list-files --help
zenodotos get-file --help
zenodotos export --help
```

For detailed command documentation, see:
- [List Files Command](docs/source/list-command.md)
- [Get File Command](docs/source/get-file-command.md)
- [Export Command](docs/source/export-command.md)

## Architecture

Zenodotos features a clean, modular architecture with both CLI and library interfaces:

```
src/zenodotos/
├── cli/                    # Command-line interface
│   ├── __init__.py        # CLI registration and main entry
│   ├── commands.py        # Click command definitions
│   ├── pagination.py      # Pagination state management
│   └── navigation.py      # Interactive navigation logic
├── drive/                 # Google Drive integration
│   ├── client.py         # Drive API client
│   └── models.py         # Data models
├── formatters/           # Output formatting
│   └── display.py       # Terminal display formatters
├── auth.py              # Authentication handling
├── config.py            # Configuration management
├── client.py            # High-level library API (Zenodotos class)
├── exceptions.py        # Custom exception hierarchy
└── utils.py             # Utility functions (FieldParser, etc.)
```

This modular design ensures:
- **Separation of concerns** for maintainability
- **Easy testing** with focused unit tests
- **Extensibility** for future features
- **Clean interfaces** between components
- **Dual interface support** - both CLI and library usage
- **Backward compatibility** - CLI functionality preserved while adding library capabilities

## Library Usage

Zenodotos is not just a CLI tool - it's also a powerful Python library for Google Drive operations. The CLI serves as a real-world example of how to use the library.

### Basic Library Usage

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

### Advanced Library Features

```python
from zenodotos import Zenodotos, MultipleFilesFoundError, NoFilesFoundError

zenodotos = Zenodotos()

# Custom field selection
field_parser = zenodotos.get_field_parser()
all_fields, requested_fields = field_parser.parse_fields("id,name,size")

# Error handling
try:
    zenodotos.search_and_export("name = 'specific_file'")
except MultipleFilesFoundError as e:
    print(f"Multiple files found: {e}")
except NoFilesFoundError as e:
    print(f"No files found: {e}")
```

### Library Architecture

The library provides:
- **High-level API** - Simple interface for common operations
- **Custom exceptions** - Specific error types for better error handling
- **Utility functions** - Field parsing, file validation, and more
- **Configuration management** - Environment variables and config files
- **Backward compatibility** - All existing CLI functionality preserved

## Development

### Setup

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage (fails if coverage is less than 80%):
```bash
pytest --cov=zenodotos --cov-report=term-missing --cov-fail-under=80
```

**Current test coverage: 96%** ✅ (exceeds 80% requirement)

### Code Quality Checks

Run the complete verification suite:

```bash
# Format code
ruff format .

# Lint and auto-fix issues
ruff check . --fix

# Type checking
ty check .

# Run tests with coverage
pytest --cov=zenodotos --cov-report=term-missing --cov-fail-under=80
```

**All checks must pass before committing changes.**

### Documentation Generation

Generate HTML documentation using Sphinx:

```bash
# Build documentation
cd docs && sphinx-build -b html source build/html

# View documentation locally
# Open docs/build/html/index.html in your browser
```

**Documentation features:**
- **API documentation** - Automatically generated from docstrings
- **User guides** - Installation, quickstart, and usage examples
- **Command reference** - Detailed CLI documentation
- **Google-style docstrings** - Follow project conventions
- **Markdown support** - Write docs in Markdown format

The generated documentation includes comprehensive API reference, usage examples, and development guides.

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:
- **ruff**: Code formatting and linting
- **ty**: Type checking
- **pytest**: Test execution

Hooks run automatically on commit, or manually:
```bash
pre-commit run --all-files
```

### Project Standards

- **Test Coverage**: Minimum 80% (currently 95.93%)
- **Type Safety**: Full type annotation coverage with `ty`
- **Code Quality**: Enforced via `ruff` linting
- **Commit Messages**: Follow conventional commit format
- **Interactive Features**: Default to user-friendly interactive mode
- **Backward Compatibility**: Support non-interactive mode for automation

## Troubleshooting

### Common Issues

1. **Credentials File Not Found**
   - Ensure the credentials file exists at the default location or
   - Verify the `GOOGLE_DRIVE_CREDENTIALS` environment variable is set correctly
   - Check file permissions

2. **Authentication Errors**
   - Verify the credentials file is valid
   - Ensure the Google Drive API is enabled in your project
   - Check if the OAuth consent screen is configured correctly

3. **API Rate Limits**
   - The Google Drive API has rate limits
   - Consider implementing exponential backoff for retries
   - Monitor your API usage in the Google Cloud Console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
