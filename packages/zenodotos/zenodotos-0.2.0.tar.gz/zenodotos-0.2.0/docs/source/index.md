# Zenodotos Documentation

Welcome to the Zenodotos project documentation. This documentation provides comprehensive information about the project, its architecture, and how to use it.

## Project Overview

Zenodotos is a **dual-interface tool** for interacting with Google Drive - both a powerful command-line interface and a comprehensive Python library. This design provides maximum flexibility for users while maintaining a clean, modular codebase.

### Key Features

- **Interactive file browsing** with intuitive pagination controls
- **Smart file export** with automatic format selection for Google Workspace documents
- **Advanced search and filtering** capabilities
- **Flexible field selection** for customized output
- **High-level library API** for easy integration into Python applications
- **Custom exception hierarchy** for robust error handling
- **Configuration management** with environment variables and config files

### Development Tools

- `ruff` for linting and formatting
- `ty` for type checking
- `pytest` for testing
- `uv` for package management
- `sphinx` for documentation

## Documentation Structure

```{toctree}
:maxdepth: 2
:caption: Contents:

installation
user-quickstart
quickstart
architecture
library
commands
contributing
tdd-practices
```

## Getting Started

### For CLI Users
To get started with Zenodotos CLI, please refer to the [Installation](installation.md) and [User Quick Start](user-quickstart.md) guides.

### For Library Users
To integrate Zenodotos into your Python applications, see the [Library API](library.md) documentation.

### For Developers
For development and contribution, see the [Development Quick Start](quickstart.md) guide and [Architecture](architecture.md) documentation.

## Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for more information.

## License

This project is licensed under the terms of the license specified in the project repository.
