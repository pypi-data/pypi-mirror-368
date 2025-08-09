# CI/CD Setup Guide

This document explains the GitHub Actions CI/CD setup for the Zenodotos project, which ensures code quality and maintains high standards across all contributions.

## Overview

The CI/CD pipeline consists of multiple workflows that run automatically on pushes and pull requests to ensure:

- **Code Quality**: Linting, formatting, and type checking
- **Test Coverage**: Comprehensive testing with 80% minimum coverage
- **Security**: Vulnerability scanning and secret detection
- **Documentation**: Build verification and link checking
- **Performance**: Code complexity and maintainability analysis

## Workflows

### 1. Main CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**

#### Test Job
- **Matrix Strategy**: Runs on Python 3.11, 3.12, and 3.13
- **Dependency Management**: Uses `uv` for fast, reliable dependency resolution
- **Caching**: Caches virtual environments and dependencies for faster builds
- **Quality Checks**:
  - Ruff linting and formatting
  - Type checking with `ty`
  - Test execution with coverage reporting
  - Coverage upload to Codecov

#### Quality Gates Job (PRs only)
- **TODO/FIXME Detection**: Prevents incomplete code from being merged
- **Print Statement Detection**: Ensures no debug prints in production code
- **Debugger Statement Detection**: Prevents debugger statements in production
- **Configuration Validation**: Ensures `pyproject.toml` is valid
- **Package Build Test**: Verifies the package can be built successfully

#### Security Job
- **Code Security Audit**: Uses `bandit` to check for common security issues
- **Secret Detection**: Scans for hardcoded secrets, passwords, or tokens
- **Security Best Practices**: Enforces security guidelines

#### Documentation Job
- **Sphinx Build**: Builds documentation to catch any build errors
- **Link Validation**: Checks for broken links in documentation
- **Documentation Quality**: Ensures documentation is up-to-date

#### Integration Job (Main branch only)
- **Integration Tests**: Runs any integration tests if they exist
- **CLI Testing**: Verifies all CLI commands work correctly
- **End-to-End Validation**: Ensures the application works as expected

### 2. Quality Checks Workflow (`.github/workflows/quality-checks.yml`)

**Triggers:**
- Manual dispatch (workflow_dispatch)
- Weekly schedule (every Monday at 2 AM)
- Push to main branch with changes to source code

**Jobs:**

#### Code Quality Analysis
- **Cyclomatic Complexity**: Measures code complexity using `radon`
- **Maintainability Index**: Calculates maintainability scores
- **Raw Metrics**: Lines of code, functions, classes analysis
- **Unused Code Detection**: Finds unused imports and variables
- **Docstring Analysis**: Checks for missing or malformed docstrings
- **Code Duplication**: Detects duplicate code patterns

#### Dependency Analysis
- **Outdated Dependencies**: Checks for newer versions of dependencies
- **License Compliance**: Generates dependency license report
- **Security Updates**: Identifies dependencies with security issues

#### Performance Checks
- **Performance Tests**: Runs any performance-specific tests
- **Import Performance**: Measures module import time
- **Performance Regression**: Detects performance degradation

## Quality Gates

### Required (Blocking)
- ✅ All tests must pass
- ✅ Minimum 80% test coverage
- ✅ No linting errors (ruff)
- ✅ Code is properly formatted (ruff format)
- ✅ No type checking errors (ty)
- ✅ No TODO/FIXME comments in source code
- ✅ No print statements in source code
- ✅ No debugger statements in source code
- ✅ Package must build successfully
- ✅ No security vulnerabilities in dependencies
- ✅ No obvious hardcoded secrets

### Recommended (Non-blocking)
- ⚠️ Docstring style compliance
- ⚠️ Code duplication below 5% threshold
- ⚠️ Maintainability index above 65
- ⚠️ Cyclomatic complexity below 10 for functions

## Local Development

### Pre-commit Hooks
The CI workflow mirrors the local pre-commit hooks. To ensure your code passes CI:

```bash
# Install pre-commit hooks
pre-commit install

# Run all checks locally
pre-commit run --all-files

# Run specific checks
pre-commit run ruff --all-files
pre-commit run ty --all-files
pre-commit run pytest --all-files
```

### Manual Quality Checks
You can run the same quality checks locally that the CI performs:

```bash
# Code quality
uv run ruff check .
uv run ruff format --check .
uv run ty check

# Tests with coverage
uv run pytest --cov=zenodotos --cov-report=term-missing --cov-fail-under=80

# Security audit
uv run bandit -r src/ -f txt

# Documentation build
cd docs/source && uv run sphinx-build -b html . ../build/html
```

## Configuration

### Python Versions
The CI tests against Python 3.11, 3.12, and 3.13 to ensure compatibility across supported versions.

### Dependency Management
The project uses `uv` for dependency management, which provides:
- Fast dependency resolution
- Reliable lock files
- Built-in security auditing
- Cross-platform compatibility

### Caching Strategy
The CI uses GitHub Actions caching to speed up builds:
- Virtual environment cache
- UV dependency cache
- Cache invalidation based on `pyproject.toml` and `uv.lock` changes

## Troubleshooting

### Common Issues

#### Test Failures
1. **Coverage Below 80%**: Add tests for uncovered code paths
2. **Import Errors**: Check for missing dependencies in `pyproject.toml`
3. **Type Errors**: Fix type annotations or add type ignores where appropriate

#### Linting Issues
1. **Ruff Errors**: Run `uv run ruff check --fix .` to auto-fix issues
2. **Formatting Issues**: Run `uv run ruff format .` to format code
3. **Type Errors**: Fix type annotations or use `# type: ignore` comments

#### Security Issues
1. **Security Vulnerabilities**: Fix issues reported by Bandit security scanner
2. **Hardcoded Secrets**: Remove any hardcoded credentials or tokens
3. **Debug Code**: Remove print statements and debugger calls

### Getting Help

If you encounter issues with the CI:

1. **Check the logs**: Review the detailed logs in GitHub Actions
2. **Run locally**: Use the local commands to reproduce issues
3. **Update dependencies**: Ensure your local environment matches CI
4. **Ask for help**: Create an issue with detailed error information

## Best Practices

### For Contributors
1. **Run checks locally**: Always run pre-commit hooks before pushing
2. **Write tests**: Ensure new code has adequate test coverage
3. **Follow style guides**: Use the established code formatting and style
4. **Document changes**: Update documentation when adding new features
5. **Security first**: Never commit secrets or credentials

### For Maintainers
1. **Monitor CI health**: Regularly check CI status and fix issues
2. **Update dependencies**: Keep dependencies up-to-date and secure
3. **Review quality metrics**: Monitor code quality trends over time
4. **Optimize performance**: Look for ways to improve CI build times
5. **Document changes**: Update this guide when modifying CI configuration

## Metrics and Monitoring

### Coverage Tracking
- **Codecov Integration**: Automatic coverage reporting and trend analysis
- **Coverage Thresholds**: Minimum 80% coverage enforced
- **Coverage Reports**: Detailed reports showing uncovered lines

### Quality Metrics
- **Maintainability Index**: Tracks code maintainability over time
- **Cyclomatic Complexity**: Monitors code complexity
- **Code Duplication**: Identifies duplicate code patterns

### Performance Metrics
- **Build Times**: Tracks CI build performance
- **Import Times**: Monitors module import performance
- **Test Execution**: Measures test suite performance

## Future Enhancements

### Planned Improvements
- [ ] **Parallel Testing**: Split test suite for faster execution
- [ ] **Dependency Graph**: Visualize dependency relationships
- [ ] **Performance Benchmarks**: Automated performance regression testing
- [ ] **Security Scanning**: Integration with security scanning tools
- [ ] **Deployment Pipeline**: Automated deployment to PyPI

### Monitoring and Alerting
- [ ] **CI Health Dashboard**: Visual dashboard for CI metrics
- [ ] **Slack Notifications**: Real-time notifications for CI failures
- [ ] **Quality Trend Analysis**: Track quality metrics over time
- [ ] **Automated Remediation**: Auto-fix common issues

This CI/CD setup ensures that Zenodotos maintains high code quality standards while providing a smooth development experience for contributors.
