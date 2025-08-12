# Contributing Guide

Thank you for your interest in contributing to the Zenodotos project! This guide will help you understand how to contribute effectively.

## Development Environment

1. **Setup**
   - Follow the [Installation Guide](installation.md)
   - Ensure all development tools are installed
   - Configure your IDE with the recommended settings

2. **Code Style**
   - Follow PEP 8 guidelines
   - Use type hints
   - Write docstrings in Google style
   - Format code with ruff
   - Run type checking with ty

## Contribution Process

1. **Before You Start**
   - Check existing issues and pull requests
   - Discuss major changes in issues first
   - Ensure you have the latest code

2. **Making Changes**
   - Create a new branch for your changes
   - Make focused, atomic commits
   - Write clear commit messages
   - Update documentation as needed

3. **Testing**
   - Write tests for new features
   - Update tests for changed features
   - Ensure all tests pass
   - Maintain or improve test coverage
   - Use `pytest-cov` to measure coverage (minimum 80%)
   - Review coverage reports and address uncovered code
   - Follow [TDD Practices](tdd-practices.md) for bug fixes and feature development

4. **Documentation**
   - Update docstrings
   - Add or update examples
   - Update relevant documentation
   - Build and check documentation

## Pull Request Process

1. **Before Submitting**
   - Run all quality checks
   - Ensure tests pass
   - Update documentation
   - Check for type errors
   - Verify formatting

2. **Pull Request Guidelines**
   - Use the PR template
   - Link related issues
   - Describe changes clearly
   - Include test results
   - Update documentation

3. **Review Process**
   - Address review comments
   - Keep PRs focused and small
   - Respond to feedback promptly
   - Update PR as needed

## Code Review Guidelines

1. **What to Look For**
   - Code style and formatting
   - Type hints and annotations
   - Test coverage and quality (minimum 80%, enforced by pytest-cov)
   - Documentation updates
   - Performance considerations

2. **Review Process**
   - Be constructive and specific
   - Focus on the code, not the person
   - Suggest improvements clearly
   - Consider maintainability

## Best Practices

1. **Code Quality**
   - Write clean, maintainable code
   - Follow project conventions
   - Use appropriate abstractions
   - Consider edge cases

2. **Testing**
   - Write comprehensive tests
   - Include edge cases
   - Test error conditions
   - Maintain high coverage

3. **Documentation**
   - Keep docstrings up to date
   - Document public APIs
   - Include usage examples
   - Update README when needed

## Getting Help

- Open an issue for bugs
- Use discussions for questions
- Join the community chat
- Check existing documentation

## Next Steps

- Read the [Installation Guide](installation.md)
- Review the [Quick Start Guide](quickstart.md)
- Check the [TDD Practices Guide](tdd-practices.md) for development workflow
- Check the [API Documentation](../api/index.html)
