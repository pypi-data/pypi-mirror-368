# Quick Start Guide

This guide will help you get started with the Zenodotos project quickly.

## Basic Usage

1. **Code Quality Checks**
   ```bash
   # Run linting
   ruff check .

   # Format code
   ruff format .

   # Type checking
   ty check .
   ```

2. **Running Tests**
   ```bash
   # Run all tests
   pytest

   # Run specific test file
   pytest tests/test_specific.py

   # Run tests with coverage
   pytest --cov=zenodotos --cov-report=term-missing --cov-fail-under=80
   ```
   - The coverage report will show which lines are not covered by tests.
   - The build will fail if coverage is below 80%.

3. **Building Documentation**
   ```bash
   # Build HTML documentation
   sphinx-build -b html docs/source docs/build/html

   # Check documentation links
   sphinx-build -b linkcheck docs/source docs/build/linkcheck
   ```

## Development Workflow

1. **Starting a New Feature**
   ```bash
   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate

   # Install dependencies
   uv sync

   # Run all checks
   ruff check . && ruff format . && ty check . && pytest
   ```

2. **Code Review Process**
   - Run all quality checks
   - Ensure tests pass
   - Build documentation
   - Check for type errors
   - Verify formatting

3. **Common Commands**
   ```bash
   # Add a new dependency
   uv add package-name

   # Add a development dependency
   uv add --dev package-name

   # Update dependencies
   uv sync --upgrade

   # Build the package
   uv build
   ```

## Best Practices

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints
   - Write docstrings in Google style
   - Keep functions small and focused

2. **Testing**
   - Write tests for new features
   - Maintain high test coverage (minimum 80%)
   - Include edge cases
   - Test error conditions
   - Use `pytest-cov` for coverage and review uncovered lines

3. **Documentation**
   - Keep docstrings up to date
   - Document public APIs
   - Include usage examples
   - Update README when needed

## Next Steps

- Read the [Installation Guide](installation.md) for detailed setup instructions
- Review the [Contributing Guidelines](contributing.md) for project standards
- Check the [API Documentation](../api/index.html) for detailed API reference
