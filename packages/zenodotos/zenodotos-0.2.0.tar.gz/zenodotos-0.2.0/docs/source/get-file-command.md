# Get File Command

The `get-file` command retrieves and displays detailed information about a specific file from Google Drive.

## Overview

```bash
zenodotos get-file [<file_id>] [OPTIONS]
```

The get-file command retrieves comprehensive metadata for a single file identified by its ID or search query. You can customize which information is displayed using the `--fields` option.

Either `file_id` or `--query` must be provided. Use `--query` to search for files by name or other criteria.

## Arguments

- `file_id` (optional): The Google Drive file ID of the file to retrieve information about. Required if `--query` is not provided.

## Options

- `--query TEXT`: Search query to find files to get details for (e.g., "name contains 'report'")
- `--fields TEXT`: Comma-separated list of fields to retrieve for the file
- `--help`: Show help message and exit

## Default Fields

When no `--fields` option is specified, the following fields are retrieved by default:
- `id`, `name`, `mimeType`, `size`, `createdTime`, `modifiedTime`, `description`, `owners`, `webViewLink`

## Available Fields

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

## Examples

### Basic Usage

Get detailed information about a file with default fields:
```bash
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx
```

### Query-Based File Retrieval

Get file details by searching for them instead of using file IDs:

```bash
# Get file by exact name
zenodotos get-file --query "name = 'My Important Document'"

# Get file containing specific text in the name
zenodotos get-file --query "name contains 'report'"

# Get file by MIME type
zenodotos get-file --query "mimeType = 'application/vnd.google-apps.document'"

# Get file modified recently
zenodotos get-file --query "modifiedTime > '2024-01-01'"
```

### Custom Fields

Get only basic information:
```bash
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx --fields "name,size"
```

Get file with creation and modification dates:
```bash
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx --fields "name,createdTime,modifiedTime"
```

Get complete metadata:
```bash
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx --fields "id,name,mimeType,size,createdTime,modifiedTime,description,owners,webViewLink"
```

## Error Handling

The command handles various error conditions gracefully:

- **File not found**: Displays "File not found" error when the file ID doesn't exist
- **Permission denied**: Shows "Permission denied" when you don't have access to the file
- **Missing file ID and query**: Displays error when neither file ID nor query is provided
- **Multiple files found**: Shows list of matching files when query matches multiple files
- **No files found**: Shows error when query matches no files
- **General errors**: Shows appropriate error messages for other issues

## Use Cases

### Get File Information for Export

Before exporting a file, you might want to check its details:
```bash
# Get file information by ID
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx

# Get file information by search
zenodotos get-file --query "name contains 'Project Report'"

# Then export with appropriate format
zenodotos export 1abc123def456ghi789jkl012mno345pqr678stu901vwx --format pdf
```

### Check File Ownership

Verify who owns a file:
```bash
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx --fields "name,owners"
```

### Get File Timestamps

Check when a file was created and last modified:
```bash
zenodotos get-file 1abc123def456ghi789jkl012mno345pqr678stu901vwx --fields "name,createdTime,modifiedTime"
```

## Related Commands

- `zenodotos list-files` - List multiple files with pagination
- `zenodotos export` - Export Google Workspace documents
- `zenodotos --help` - Show general help information
