# User Quick Start Guide

This guide will help you get started with Zenodotos CLI for common Google Drive tasks. The CLI provides a user-friendly interface to the underlying Zenodotos library.

## Prerequisites

Before using Zenodotos, make sure you have:

1. **Google Drive API credentials** - Follow the [Installation Guide](installation.md) to set up your credentials
2. **Zenodotos installed** - Install Zenodotos using `uv sync` or `pip install -e .`

## Basic Usage

### 1. List Your Files

Start by exploring your Google Drive files:

```bash
# Interactive browsing (default)
zenodotos list-files

# Non-interactive mode for scripting
zenodotos list-files --no-interactive
```

**Interactive Navigation:**
- Use `N` or `n` to go to the next page
- Use `P` or `p` to go to the previous page
- Use `Q` or `q` to quit

### 2. Search for Specific Files

Find files using Google Drive's search capabilities:

```bash
# Search for PDF files
zenodotos list-files --query "mimeType='application/pdf'"

# Search for files modified recently
zenodotos list-files --query "modifiedTime > '2024-01-01'"

# Search for files containing "report" in the name
zenodotos list-files --query "name contains 'report'"

# Complex search combining multiple conditions
zenodotos list-files --query "name contains 'report' and mimeType='application/pdf'"
```

### 3. Customize Output Fields

Choose exactly what information you want to see:

```bash
# Minimal output - just names and sizes
zenodotos list-files --fields "name,size"

# Detailed output with timestamps
zenodotos list-files --fields "name,size,modifiedTime,createdTime"

# Full metadata (default)
zenodotos list-files --fields "id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink"
```

### 4. Get File Details

Get detailed information about a specific file:

```bash
# Basic usage with default fields
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx

# Customize which fields to display
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx --fields "name,size,createdTime"

# Get complete metadata
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx --fields "id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink"
```

### 5. Export Google Workspace Documents

Export your Google Workspace documents with smart defaults. You can export using either a file ID or a search query:

```bash
# Export by file ID (automatic format selection)
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx

# Export by search query (finds and exports single match)
zenodotos export --query "name = 'My Important Document'"

# Export with custom format
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format pdf

# Export to specific location
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --output "My Document.pdf"

# Export with verbose output
zenodotos export --query "name contains 'report'" --verbose
```

## Common Workflows

## Beyond the CLI

While this guide focuses on CLI usage, Zenodotos also provides a powerful Python library for integration into your applications. The CLI commands you've learned demonstrate how the library works in practice.

### Library Usage Example

```python
from zenodotos import Zenodotos

# Initialize the library (same as CLI)
zenodotos = Zenodotos()

# List files (same as zenodotos list-files)
files, next_token = zenodotos.list_files_with_pagination(
    query="name contains 'report'",
    page_size=10
)

# Export file (same as zenodotos export)
output_path = zenodotos.export_file(
    "file_id_here",
    format="pdf"
)
```

For comprehensive library documentation, see the [Library API](library.md) guide.

### Workflow 1: Find and Export a Document

**Method 1: Traditional approach (search then export)**
```bash
# 1. Search for your document
zenodotos list-files --query "name contains 'Project Report'"

# 2. Copy the file ID from the output
# 3. Export the document
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format pdf
```

**Method 2: Direct query-based export (new!)**
```bash
# Export directly by searching for the document
zenodotos export --query "name contains 'Project Report'" --format pdf
```

### Workflow 2: Export Multiple Spreadsheets

```bash
# 1. Find all Google Sheets
zenodotos list-files --query "mimeType='application/vnd.google-apps.spreadsheet'"

# 2. Export each one to Excel format
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format xlsx --output "Sheet1.xlsx"
zenodotos export 2def456ghi789jkl012mno345pqr678stu901vwx --format xlsx --output "Sheet2.xlsx"
```

### Workflow 3: Query-Based Export Examples

**Export recent documents:**
```bash
# Export documents modified in the last week
zenodotos export --query "modifiedTime > '2024-01-01' and mimeType='application/vnd.google-apps.document'"

# Export files by owner
zenodotos export --query "'me' in owners and name contains 'report'"
```

**Export specific file types:**
```bash
# Export all Google Docs to HTML
zenodotos export --query "mimeType='application/vnd.google-apps.document'"

# Export all Google Sheets to Excel
zenodotos export --query "mimeType='application/vnd.google-apps.spreadsheet'" --format xlsx
```

**Handle multiple matches:**
```bash
# If multiple files match, Zenodotos will show you the options
zenodotos export --query "name contains 'report'"
# Output: Multiple files found matching the query:
#         1abc123... - Report 2024 (application/vnd.google-apps.document)
#         2def456... - Report 2023 (application/vnd.google-apps.document)
#         Please use the file ID to export a specific file.
```

### Workflow 4: Backup Presentations

```bash
# 1. Find all Google Slides presentations
zenodotos list-files --query "mimeType='application/vnd.google-apps.presentation'"

# 2. Export each to PDF for backup
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format pdf --output "Presentation1.pdf"
zenodotos export 2def456ghi789jkl012mno345pqr678stu901vwx --format pdf --output "Presentation2.pdf"
```

## Smart Format Defaults

Zenodotos automatically selects the best export format for each file type:

| File Type | Default Format | Use Case |
|-----------|----------------|----------|
| Google Docs | HTML (ZIP) | Web viewing, sharing |
| Google Sheets | XLSX | Excel compatibility |
| Google Slides | PDF | Presentation sharing |
| Google Drawings | PNG | Image viewing |
| Google Forms | ZIP (HTML) | Web deployment |

## Tips and Tricks

### 1. Use Verbose Mode for Debugging

```bash
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --verbose
```

### 2. Combine Search and Export

**Method 1: Traditional approach**
```bash
# Find and export in one workflow
zenodotos list-files --query "name contains 'report'" --fields "id,name" --no-interactive
# Copy the ID and export
zenodotos export <file_id> --format pdf
```

**Method 2: Direct query-based export (simpler!)**
```bash
# Export directly by searching
zenodotos export --query "name contains 'report'" --format pdf
```

### 3. Batch Export with Scripting

```bash
#!/bin/bash
# Export all Google Docs to HTML
zenodotos list-files --query "mimeType='application/vnd.google-apps.document'" --fields "id,name" --no-interactive | \
while read -r id name; do
    zenodotos export "$id" --output "${name}.zip"
done
```

### 4. Get Help When Needed

```bash
# General help
zenodotos --help

# Command-specific help
zenodotos list-files --help
zenodotos export --help
zenodotos get-file --help
```

## Troubleshooting

### Common Issues

1. **"File not found" error**
   - Verify the file ID is correct
   - Ensure you have access to the file
   - Check if the file still exists in Google Drive

2. **"Permission denied" error**
   - Verify your Google Drive API credentials
   - Check if you have permission to access the file
   - Ensure the Google Drive API is enabled in your project

3. **"Invalid format" error**
   - Use only supported formats: `html`, `pdf`, `xlsx`, `csv`
   - Check the format compatibility with your file type

4. **Export fails**
   - Try with `--verbose` for more details
   - Check your internet connection
   - Verify the file is a Google Workspace document

5. **"Multiple files found" error**
   - Your query matched multiple files
   - Use a more specific query to narrow down results
   - Or use the file ID approach for the specific file you want

6. **"No files found" error**
   - Check your query syntax
   - Verify the search terms are correct
   - Try a broader search query

## Next Steps

- Read the [Commands Reference](commands.md) for detailed command documentation
- Check the [Installation Guide](installation.md) for setup instructions
- Review the [Contributing Guidelines](contributing.md) if you want to contribute
