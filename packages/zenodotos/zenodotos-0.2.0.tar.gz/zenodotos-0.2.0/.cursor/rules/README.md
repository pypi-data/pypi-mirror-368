# Zenodotos Project Rules and Guidelines

This document outlines the specific rules and guidelines for the Zenodotos project. Following these rules ensures consistency, maintainability, and proper operation of the project.

## Project Structure

### File Operations
- All file operations (creation, modification, deletion) must be performed strictly within the project root directory (`/home/natx/src/github.com/ifosch/zenodotos`) and its subdirectories
- No files should be created, modified, or deleted outside this directory tree
- Any attempt to operate outside this directory is a violation of project policy

## Development Guidelines

### Code Quality
- All Python code must be linted and formatted using `ruff`
- All Python code must be type-checked using `ty`
- All Python tests must be written and executed using `pytest`
- Run `ruff check` for linting, `ruff format` for formatting, `ty check` for type checking, and `pytest` for testing
- Fix all linting, formatting, type errors, and test failures before committing
- Configure ruff, ty, and pytest settings in pyproject.toml
- Maintain high test coverage (minimum 80% coverage)
- Follow project-specific naming conventions and architectural patterns
- Ensure all new functions and classes include comprehensive tests

### Pre-commit Hooks
- Install pre-commit hooks after cloning the repository
- Run pre-commit checks before committing changes
- Fix all pre-commit check failures before proceeding
- Do not bypass pre-commit checks
- Keep pre-commit configuration up to date
- Pre-commit hooks run ruff, ty, and pytest automatically

### Documentation
- Use Sphinx for all documentation generation
- Write docstrings in Google style format
- Include type hints in docstrings
- Document all public APIs, classes, and functions
- Keep documentation up to date with code changes
- Use Markdown for additional documentation files
- Run documentation build before committing changes
- Fix all documentation warnings before proceeding

### Package Management
- Use `uv` for all Python package operations
- Use `uv add` to add dependencies
- Use `uv sync` to install dependencies
- Use `uv build` to build packages
- Use `uv publish` to publish packages to PyPI
- Set PYPI_TOKEN environment variable with your PyPI API token for publishing
- Follow semantic versioning for releases
- Test packages locally before publishing

### Testing Requirements
- Write tests for all main cases
- Include positive cases, negative cases, and edge cases
- Implement security checks where applicable
- Run tests before committing changes
- Fix all test failures before proceeding

### Code Verification Process
Before committing changes, ensure:
1. Python code passes ruff linting (`ruff check .`)
2. Python code is properly formatted (`ruff format .`)
3. Python code passes type checking (`ty check .`)
4. All tests pass (`pytest`)
5. Documentation builds without warnings (`sphinx-build -b html docs/source docs/build/html`)
6. Build process succeeds (`uv build`)
7. Package can be installed locally (`uv sync`)
8. Pre-commit checks pass (`pre-commit run --all-files`)

### Commit Guidelines
- Use multiline commit messages
- Start commit message title with appropriate prefix (feat, fix, perf)
- Use infinitive tense in commit message title
- Do not end commit message title with a period
- Include a detailed body explaining the change and relevant decisions

### Test Coverage
- Use `pytest-cov` to measure test coverage
- Ensure test coverage is at least 80% (enforced via `--cov-fail-under=80` in pyproject.toml)
- Generate coverage reports with `--cov-report=term-missing`
- Investigate and address uncovered code
- Coverage requirements are enforced by Cursor rules and pyproject.toml configuration

## Safety Guidelines

### High-Risk Operations
The following operations require explicit user approval:
- Permanent data deletion
- Production deployments without rollback capability
- Any irreversible actions
- Publishing packages to PyPI

### Autonomous Operations
The following operations can be performed autonomously:
- Code edits and additions
- Reversible changes
- Non-destructive tests
- Any changes under version control
- Building packages locally

## Best Practices

### Code Organization
- Maintain clear and logical file structure
- Follow established architectural patterns
- Keep related code together
- Use appropriate file naming conventions
- Document code organization decisions

### Error Handling
- Implement proper error handling
- Use appropriate exception types
- Provide meaningful error messages
- Log errors appropriately
- Handle edge cases gracefully

### Performance
- Write efficient code
- Profile when necessary
- Optimize critical paths
- Consider memory usage
- Document performance considerations

### Security
- Follow security best practices
- Handle sensitive data properly
- Validate input data
- Use secure defaults
- Document security considerations

## Continuous Improvement

### Code Review Process
- Review code for maintainability and extensibility
- Ensure adherence to project standards
- Verify test coverage and quality
- Check for potential security issues

### System Health
- Monitor test coverage
- Address technical debt
- Improve system robustness
- Enhance security measures
- Use the tooling defined for the project to test, lint, and check everything

## Getting Started

1. Clone the repository
2. Install dependencies
3. Review project structure
4. Follow the guidelines in this document
5. Start contributing!

## Support

For questions or clarifications about these rules, please open an issue in the project repository.
