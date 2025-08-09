# List Files Command

The `list-files` command displays files from your Google Drive.

## Usage

```bash
zenodotos list-files [OPTIONS]
```

## Options

- `--page-size INTEGER`: Number of files to display (default: 10)
- `--page-token TEXT`: Token for the next page of results
- `--query TEXT`: Search query to filter files
- `--fields TEXT`: Comma-separated list of fields to retrieve for each file

### Default Fields

When no `--fields` option is specified, the following fields are retrieved by default:
- `id`, `name`, `mimeType`, `size`, `createdTime`, `modifiedTime`, `description`, `owners`, `webViewLink`

### Available Fields

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
- `parents`: Parent folder IDs
- `permissions`: File permissions
- `thumbnailLink`: Thumbnail image link
- And many others supported by the Google Drive API

**Note:** The fields `name`, `mimeType`, and `size` are always included to ensure proper display formatting.

## Examples

### Basic Usage

List the first 10 files with default fields:
```bash
zenodotos list-files
```

List 20 files:
```bash
zenodotos list-files --page-size 20
```

### Custom Fields

List files with only basic information:
```bash
zenodotos list-files --fields "id,name,size"
```

List files with creation and modification dates:
```bash
zenodotos list-files --fields "name,createdTime,modifiedTime"
```

### Search and Filter

Search for files containing "report" in the name:
```bash
zenodotos list-files --query "name contains 'report'"
```

List only PDF files:
```bash
zenodotos list-files --query "mimeType='application/pdf'"
```

Search for files modified in the last week:
```bash
zenodotos list-files --query "modifiedTime > '2023-01-01'"
```

### Combined Options

List PDF files with specific fields:
```bash
zenodotos list-files --fields "id,name,size,modifiedTime" --query "mimeType='application/pdf'"
```

Search with pagination:
```bash
zenodotos list-files --page-size 50 --query "name contains 'project'"
```

## Output Format

The command displays files in a table format with the following columns:
- **Name**: The name of the file
- **Type**: The MIME type of the file
- **Size**: The size of the file in bytes (if available, otherwise "N/A")

## Google Drive Query Syntax

The `--query` option supports Google Drive's query syntax:
- `name contains 'text'`: Files containing specific text in the name
- `mimeType = 'type'`: Files of specific MIME type
- `modifiedTime > 'date'`: Files modified after specific date
- `parents in 'folder_id'`: Files in specific folder
- `trashed = false`: Non-deleted files (default)

For more query options, see the [Google Drive API Query documentation](https://developers.google.com/drive/api/guides/search-files).
