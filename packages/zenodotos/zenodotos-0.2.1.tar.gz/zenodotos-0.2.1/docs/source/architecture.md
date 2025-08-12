# Zenodotos Architecture

This document describes the architecture of Zenodotos, explaining how it provides both a command-line interface and a Python library for Google Drive operations.

## Overview

Zenodotos follows a **dual-interface architecture** where the CLI serves as a real-world example of how to use the underlying library. This design provides maximum flexibility for users while maintaining a clean, modular codebase.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Zenodotos Project                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   CLI Interface │    │        Library Interface        │ │
│  │                 │    │                                 │ │
│  │  zenodotos list-│    │ from zenodotos import Zenodotos │ │
│  │  files          │    │  zenodotos = Zenodotos()        │ │
│  │  zenodotos get- │    │  files, token = zenodotos.list_ │ │
│  │  file           │    │  files_with_pagination()        │ │
│  │  zenodotos export│   │                                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│           │                           │                     │
│           └───────────┬───────────────┘                     │
│                       │                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              High-Level Library API                    │ │
│  │                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │ │
│  │  │  Zenodotos  │  │ FieldParser │  │   Exceptions    │ │ │
│  │  │   Class     │  │             │  │                 │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Core Components                           │ │
│  │                                                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │ │
│  │  │   Drive     │  │   Config    │  │     Utils       │ │ │
│  │  │  Client     │  │             │  │                 │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘ │ │
│  └─────────│──────────────────────────────────────────────┘ │
│            │                                                │
└────────────│────────────────────────────────────────────────┘
             └──────────┐
                        │
   ┌────────────────────────────────────────────────────────┐
   │              Google Drive API                          │
   │                                                        │
   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
   │  │   Files     │  │   Export    │  │  Authentication │ │
   │  │   API       │  │    API      │  │                 │ │
   │  └─────────────┘  └─────────────┘  └─────────────────┘ │
   └────────────────────────────────────────────────────────┘
```

## Core Components

### 1. High-Level Library API

The library API provides a simplified interface for common Google Drive operations.

#### Zenodotos Class
- **Purpose**: Main entry point for all library operations
- **Location**: `src/zenodotos/client.py`
- **Key Methods**:
  - `list_files_with_pagination()`: List files with pagination
  - `get_file()`: Get file details
  - `export_file()`: Export Google Workspace documents
  - `search_and_export()`: Search and export files
  - `get_field_parser()`: Get field parsing utility

#### FieldParser
- **Purpose**: Parse and validate field options
- **Location**: `src/zenodotos/utils.py`
- **Key Features**:
  - Handles required fields automatically
  - Removes duplicates while preserving order
  - Supports custom field selection

#### Exception Hierarchy
- **Purpose**: Provide specific error types for robust error handling
- **Location**: `src/zenodotos/exceptions.py`
- **Key Exceptions**:
  - `ZenodotosException`: Base exception
  - `MultipleFilesFoundError`: Multiple files match query
  - `NoFilesFoundError`: No files match query
  - `FileNotFoundError`: Specific file not found

### 2. CLI Interface

The CLI provides a user-friendly command-line interface that uses the library.

#### Command Structure
- **Location**: `src/zenodotos/cli/`
- **Key Files**:
  - `commands.py`: Click command definitions
  - `navigation.py`: Interactive pagination logic
  - `pagination.py`: Pagination state management

#### Commands
- `list-files`: List files with interactive pagination
- `get-file`: Get detailed file information
- `export`: Export Google Workspace documents

### 3. Core Components

#### Drive Client
- **Purpose**: Low-level Google Drive API client
- **Location**: `src/zenodotos/drive/client.py`
- **Features**:
  - Handles authentication
  - Manages API requests
  - Provides data models

#### Configuration Management
- **Purpose**: Handle configuration from multiple sources
- **Location**: `src/zenodotos/config.py`
- **Features**:
  - Environment variables
  - Configuration files (YAML, TOML, JSON)
  - Default configuration
  - Configuration validation

#### Utilities
- **Purpose**: Common utility functions
- **Location**: `src/zenodotos/utils.py`
- **Features**:
  - File ID validation
  - Filename sanitization
  - File size formatting

## Module Structure

```
src/zenodotos/
├── __init__.py              # Library exports
├── client.py                # High-level Zenodotos class
├── exceptions.py            # Custom exception hierarchy
├── utils.py                 # Utility functions
├── auth.py                  # Authentication handling
├── config.py                # Configuration management
├── cli/                     # Command-line interface
│   ├── __init__.py         # CLI registration
│   ├── commands.py         # Click command definitions
│   ├── navigation.py       # Interactive navigation
│   └── pagination.py       # Pagination state
├── drive/                   # Google Drive integration
│   ├── __init__.py
│   ├── client.py           # Drive API client
│   └── models.py           # Data models
└── formatters/             # Output formatting
    ├── __init__.py
    └── display.py          # Terminal display
```

## Design Principles

### 1. Separation of Concerns

Each module has a specific responsibility:
- **Library API**: High-level interface for developers
- **CLI**: User-friendly command-line interface
- **Drive Client**: Low-level API communication
- **Configuration**: Settings management
- **Utilities**: Common helper functions

### 2. Backward Compatibility

The CLI maintains 100% backward compatibility:
- All existing commands work unchanged
- All options and arguments preserved
- User experience identical to before
- No breaking changes for CLI users

### 3. Dual Interface Benefits

#### For CLI Users
- Familiar command-line experience
- Interactive features (pagination, navigation)
- Comprehensive help and documentation
- Real-world example of library usage

#### For Library Users
- Clean, simple API
- Comprehensive error handling
- Flexible configuration options
- Easy integration into applications

### 4. Modularity

The architecture promotes:
- **Testability**: Each component can be tested independently
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new features
- **Reusability**: Components can be used in different contexts

## Data Flow

### CLI Command Execution

```
User Input → Click Commands → Zenodotos Library → Drive Client → Google Drive API
     ↑                                                              ↓
     └─────────────── Formatted Output ← Display Formatters ←──────┘
```

### Library Usage

```
Application Code → Zenodotos Class → Drive Client → Google Drive API
     ↑                                                      ↓
     └─────────────── Return Data ← Data Models ←──────────┘
```

## Configuration Flow

```
Environment Variables → Config Manager → Library/CLI Components
Config Files ─────────┘
Default Values ───────┘
```

## Error Handling Strategy

### Library Level
- **Specific Exceptions**: Custom exception types for different error scenarios
- **Graceful Degradation**: Handle errors without crashing
- **Detailed Error Messages**: Provide helpful error information

### CLI Level
- **User-Friendly Messages**: Convert technical errors to user-friendly messages
- **Helpful Suggestions**: Provide guidance on how to fix issues
- **Exit Codes**: Proper exit codes for scripting

## Testing Strategy

### Unit Tests
- **Library Components**: Test each module independently
- **Mock Dependencies**: Use mocks for external dependencies
- **Edge Cases**: Test error conditions and edge cases

### Integration Tests
- **CLI Commands**: Test complete command execution
- **Real API**: Test with actual Google Drive API
- **End-to-End**: Test complete workflows

### Coverage Requirements
- **Minimum Coverage**: 80% (currently 96%)
- **Critical Paths**: 100% coverage for critical functionality
- **Error Handling**: Comprehensive error scenario testing

## Future Architecture Considerations

### Async Support
- **AsyncZenodotos Class**: Async version of the Zenodotos class
- **Concurrent Operations**: Support for parallel operations
- **Background Tasks**: Long-running operation support

### Plugin System
- **Plugin Architecture**: Extensible plugin system
- **Custom Formatters**: User-defined output formats
- **Custom Commands**: User-defined CLI commands

### Event System
- **Event-Driven Architecture**: Event-based communication
- **Custom Events**: User-defined events
- **Event Listeners**: Event handling and processing

## Performance Considerations

### Caching
- **File Metadata**: Cache frequently accessed file information
- **Authentication**: Cache authentication tokens
- **Configuration**: Cache configuration values

### Batch Operations
- **Batch Requests**: Group multiple API requests
- **Progress Tracking**: Track operation progress
- **Resume Capability**: Resume interrupted operations

### Rate Limiting
- **API Limits**: Respect Google Drive API rate limits
- **Exponential Backoff**: Implement retry logic
- **Request Queuing**: Queue requests when limits are reached

## Security Considerations

### Authentication
- **OAuth 2.0**: Secure authentication flow
- **Token Management**: Secure token storage and refresh
- **Service Accounts**: Support for service account authentication

### Data Protection
- **Credential Security**: Secure credential storage
- **Data Encryption**: Encrypt sensitive data
- **Access Control**: Implement proper access controls

## Related Documentation

- [Library API](library.md) - Detailed library documentation
- [CLI Commands](commands.md) - Command-line interface documentation
- [Installation Guide](installation.md) - Setup and configuration
- [Contributing Guide](contributing.md) - Development guidelines
