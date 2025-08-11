# Installation

This guide will help you install and set up the Zenodotos project.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) for dependency management
- Git

## Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/ifosch/zenodotos.git
cd zenodotos
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Setup

The project uses several tools to ensure code quality:

- **ruff**: For linting and formatting
- **ty**: For type checking
- **pytest**: For testing
- **pre-commit**: For automated checks before commits

### Pre-commit Hooks

The project includes pre-commit hooks that automatically run:
- Code formatting and linting with ruff
- Type checking with mypy
- Tests with pytest and coverage checks

These hooks run automatically before each commit. If any check fails, the commit will be blocked until the issues are fixed.

To manually run the pre-commit checks:
```bash
pre-commit run --all-files
```

## Verification

After installation, verify that everything is working:

1. Run the tests:
   ```bash
   pytest
   ```

2. Check code formatting:
   ```bash
   ruff format .
   ```

3. Run type checking:
   ```bash
   ty
   ```

## Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   - Ensure you're using the correct Python version
   - Try recreating the virtual environment
   - Check your PATH environment variable

2. **Dependency Installation Issues**
   - Clear uv cache: `uv cache clean`
   - Check your internet connection
   - Verify package names and versions

3. **Permission Issues**
   - Use `sudo` for system-wide installation (not recommended)
   - Check directory permissions
   - Use virtual environments to avoid permission problems

## Next Steps

- Read the [Quick Start Guide](quickstart.md)
- Review the [Contributing Guidelines](contributing.md)
- Check the [API Documentation](../api/index.html)
