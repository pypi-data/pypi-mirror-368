# Commands Reference

This section contains detailed documentation for all Zenodotos CLI commands. The CLI serves as a real-world example of how to use the underlying Zenodotos library.

## Available Commands

```{toctree}
:maxdepth: 1

list-command
get-file-command
export-command
```

## Quick Reference

- [`zenodotos list-files`](list-command.md) - List files in your Google Drive with various options
- [`zenodotos get-file <file_id>`](get-file-command.md) - Get detailed information about a specific file
- [`zenodotos export <file_id>`](export-command.md) - Export Google Workspace documents with smart defaults
- `zenodotos --help` - Show general help information

## CLI vs Library

The CLI commands are built on top of the Zenodotos library, demonstrating how to use the library in practice:

- **CLI**: User-friendly command-line interface with interactive features
- **Library**: Programmatic interface for integration into Python applications

For library usage, see the [Library API](library.md) documentation.
