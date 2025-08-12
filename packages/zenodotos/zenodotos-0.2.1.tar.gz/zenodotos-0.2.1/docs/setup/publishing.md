# PyPI Publishing Guide

This guide covers the process of publishing the Zenodotos package to PyPI, including both TestPyPI for testing and production PyPI for releases.

## Overview

The Zenodotos project uses a manual publishing process with automated testing to ensure package quality and reliability. The process includes:

1. **TestPyPI Publishing** - For testing package installation and functionality
2. **TestPyPI Validation** - Automated testing of the published package
3. **Production PyPI Publishing** - Final release to production PyPI

## Prerequisites

### 1. PyPI Accounts

You need accounts on both PyPI registries:

- **TestPyPI**: https://test.pypi.org (for testing)
- **Production PyPI**: https://pypi.org (for releases)

### 2. API Tokens

Generate API tokens for both registries:

1. **TestPyPI Token**:
   - Go to https://test.pypi.org/manage/account/token/
   - Create a new token with "Entire account" scope
   - Copy the token (it starts with `pypi-`)

2. **Production PyPI Token**:
   - Go to https://pypi.org/manage/account/token/
   - Create a new token with "Entire account" scope
   - Copy the token (it starts with `pypi-`)

### 3. Environment Setup

Set up your environment variables using one of these methods:

#### Option A: Environment Variables (Recommended for CI/CD)
```bash
# Required for TestPyPI publishing
export TEST_PYPI_TOKEN="pypi-your-test-token-here"

# Required for production PyPI publishing
export PYPI_TOKEN="pypi-your-production-token-here"
```

#### Option B: Local .env File (Recommended for local development)
1. Copy the example file: `cp env.example .env`
2. Edit `.env` and add your actual tokens:
   ```bash
   TEST_PYPI_TOKEN=pypi-your-actual-test-token
   PYPI_TOKEN=pypi-your-actual-production-token
   ```

**Security Note**: Never commit these tokens to version control. The `.env` file is already in `.gitignore` to prevent accidental commits.

## Publishing Process

### Step 1: Prepare for Release

1. **Update version** in `pyproject.toml`:
   ```bash
   # Edit pyproject.toml and update the version
   version = "0.1.1"  # or whatever version you're releasing
   ```

2. **Run tests** to ensure everything works:
   ```bash
   uv run pytest
   ```

3. **Check package metadata**:
   ```bash
   uv build --dry-run
   ```

### Step 2: Manual Publishing

Use the provided release script for the complete publishing process:

```bash
# TestPyPI release only
./scripts/release.sh --testpypi

# Production PyPI release only
./scripts/release.sh --pypi

# To publish to both indexes, run the script twice:
./scripts/release.sh --testpypi && ./scripts/release.sh --pypi
```

The script will:
1. Validate your environment
2. Build the package
3. Publish to the specified target (TestPyPI or PyPI)
4. Automatically check package availability after upload
5. Test pip installation when available
6. Provide clear status feedback and next steps

### Step 3: Verify the Release

After publishing, verify the package works correctly:

```bash
# Check package availability and test installation
./scripts/check-package-availability.sh --testpypi --pip-test  # For TestPyPI
./scripts/check-package-availability.sh --pypi --pip-test      # For production PyPI

# Test installation from TestPyPI
./scripts/test-pypi-install.sh

# Test installation from production PyPI
pip install zenodotos
zenodotos --help
```

**Note**: The release script automatically checks package availability after upload, but you can manually verify at any time using the availability checker.

## Manual Steps (Alternative)

If you prefer to run the steps manually:

### 1. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build package
uv build
```

### 2. Publish to TestPyPI

```bash
# Publish to TestPyPI
uv publish --repository testpypi --token "$TEST_PYPI_TOKEN"
```

### 3. Test TestPyPI Installation

```bash
# Use the test script
./scripts/test-pypi-install.sh

# Or test manually
mkdir test-install
cd test-install
uv venv
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ zenodotos
uv run zenodotos --help
```

### 4. Publish to Production PyPI

```bash
# Publish to production PyPI
uv publish --repository pypi --token "$PYPI_TOKEN"
```

## Version Management

### Version Format

Use semantic versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Update Process

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.1.1"  # Package version (without v prefix)
   ```
2. **Commit changes** with conventional commit message:
   ```bash
   git add pyproject.toml
   git commit -m "feat: bump version to 0.1.1"
   ```
3. **Create and push tag**:
   ```bash
   git tag v0.1.1  # Git tag (with v prefix for semantic versioning)
   git push origin v0.1.1
   ```
4. **Publish to PyPI** using the release script

**Versioning Convention**:
- **Package version** (pyproject.toml): `0.1.0` (without `v` prefix)
- **Git tag**: `v0.1.0` (with `v` prefix for semantic versioning)
- **Release name**: `v0.1.0` (matches git tag)

## Testing and Validation

### Pre-Publishing Tests

Before publishing, ensure:

1. **All tests pass**:
   ```bash
   uv run pytest
   ```

2. **Code quality checks pass**:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```

3. **Package builds successfully**:
   ```bash
   uv build
   ```

### Post-Publishing Tests

After publishing, verify:

1. **Check package availability**:
   ```bash
   # For TestPyPI
   ./scripts/check-package-availability.sh --testpypi --pip-test

   # For production PyPI
   ./scripts/check-package-availability.sh --pypi --pip-test
   ```

2. **Package installs correctly**:
   ```bash
   ./scripts/test-pypi-install.sh
   ```

3. **CLI commands work**:
   ```bash
   zenodotos --help
   zenodotos list-files --help
   ```

4. **Library imports work**:
   ```bash
   python -c "import zenodotos; print('Success')"
   ```

### Package Availability Monitoring

The package availability checker provides comprehensive verification:

- **Availability Status**: Check if packages are found on the index
- **Installation Testing**: Verify packages are actually installable
- **Timing Information**: Track response times and deployment durations
- **Upload Time Detection**: Identify recently uploaded packages
- **Deployment Guidance**: Understand typical timeframes

For detailed information about package availability checking, see [Package Availability Checking](package-availability.md).

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify your API tokens are correct
   - Ensure tokens have the right permissions
   - Check that environment variables are set

2. **Package Already Exists**:
   - PyPI doesn't allow overwriting existing versions
   - Increment the version number in `pyproject.toml`

3. **Build Failures**:
   - Check that all dependencies are correctly specified
   - Verify `pyproject.toml` syntax
   - Run `uv build --dry-run` to see detailed errors

4. **Installation Failures**:
   - Check that all dependencies are available on PyPI
   - Verify package metadata is correct
   - Test with a clean virtual environment
   - Use availability checker: `./scripts/check-package-availability.sh --pip-test`

5. **Package Not Available**:
   - Check if package was uploaded successfully
   - Wait for index propagation (see deployment times)
   - Use availability checker: `./scripts/check-package-availability.sh`
   - Verify version number matches uploaded package

### Getting Help

If you encounter issues:

1. **Check the logs** from the release script
2. **Verify your environment** setup
3. **Test with a minimal example**
4. **Check PyPI documentation** for specific errors

## Security Best Practices

1. **Never commit tokens** to version control
2. **Use environment variables** for sensitive data
3. **Rotate tokens regularly** for security
4. **Use separate tokens** for TestPyPI and production PyPI
5. **Limit token permissions** to minimum required

## Future Improvements

Planned enhancements to the publishing process:

1. **Automated GitHub Actions** workflow for tag-based releases
2. **Automated version management** from git tags
3. **Release notes generation** from conventional commits
4. **Package signing** with GPG keys
5. **Automated testing** in isolated environments

## Related Documentation

- [Version Management](./version-management.md) - Managing tool versions
- [Development Setup](./installation.md) - Setting up the development environment
- [Contributing Guide](../contributing.md) - Contributing to the project
