# Version Management System

## Overview

The Zenodotos project uses a centralized version management system to ensure consistency across all environments (local development, CI/CD, and documentation). This system prevents version mismatches and simplifies maintenance.

## Problem Solved

Before this system, tool versions were scattered across multiple files:
- `pyproject.toml` (dependencies)
- `.pre-commit-config.yaml` (pre-commit hooks)
- CI workflows (hardcoded versions)
- Documentation

This led to:
- Version inconsistencies between environments
- Manual updates across multiple files
- CI failures due to version mismatches
- Maintenance overhead

## Solution

A single source of truth approach with:
1. **`.github/versions.env`** - Centralized version definitions
2. **`scripts/update-versions.sh`** - Automated update script
3. **CI workflows** - Load versions from `.env` file
4. **Documentation** - Clear usage guidelines

## Files Involved

### 1. `.github/versions.env`
Central file containing all tool versions:
```bash
# Python package manager
UV_VERSION=0.8.6

# Code quality tools
RUFF_VERSION=0.11.13
RADON_VERSION=6.0.1
PYDOCSTYLE_VERSION=6.3.0
BANDIT_VERSION=1.8.6

# Documentation tools
SPHINX_VERSION=7.4.7
SPHINX_RTD_THEME_VERSION=3.0.2
MYST_PARSER_VERSION=3.0.1

# Build tools
BUILD_VERSION=1.0.0

# Type checking
TY_VERSION=0.0.1a9

# Pre-commit
PRE_COMMIT_VERSION=4.2.0
```

### 2. `scripts/update-versions.sh`
Automated script that updates versions across all files:
- `.github/versions.env`
- `pyproject.toml`
- `.pre-commit-config.yaml`
- CI workflows

### 3. CI Workflows
Both `ci.yml` and `quality-checks.yml` load versions from `.env` file:
```yaml
- name: Load versions from .env file
  run: |
    source .github/versions.env
    echo "UV_VERSION=$UV_VERSION" >> $GITHUB_ENV
    echo "RUFF_VERSION=$RUFF_VERSION" >> $GITHUB_ENV
```

### 4. How It Works
1. **CI Workflow starts** and checks out the code
2. **Load step runs** and uses `source .github/versions.env` to load environment variables
3. **Environment variables are set** in `$GITHUB_ENV` for use in subsequent steps
4. **Subsequent steps use** `${{ env.VERSION_NAME }}` to access versions
5. **Fallback values** ensure workflows don't break if the file is missing

## How to Update Versions

### Option 1: Using the Automated Script (Recommended)

1. **Update a single tool**:
   ```bash
   ./scripts/update-versions.sh update ruff v0.12.0
   ```

2. **Available tools**:
   - `ruff` - Code linter and formatter
   - `uv` - Python package manager
   - `radon` - Code complexity analyzer
   - `bandit` - Security linter
   - `pydocstyle` - Docstring style checker
   - `sphinx` - Documentation generator
   - `build` - Package builder
   - `ty` - Type checker
   - `pre-commit` - Git hooks framework

### Option 2: Manual Updates

1. **Update `.github/versions.env`** with the new version
2. **Update `pyproject.toml`** dependencies
3. **Update `.pre-commit-config.yaml`** if applicable
4. **Update CI workflows** if hardcoded versions exist

## Best Practices

### 1. Always Use the Script
The automated script ensures all files are updated consistently.

### 2. Test Locally First
After updating versions:
```bash
# Test pre-commit hooks
pre-commit run --all-files

# Test CI workflow locally
act push

# Run tests
uv run pytest
```

### 3. Update One Tool at a Time
This makes it easier to identify issues if something breaks.

### 4. Commit Version Updates Separately
Keep version updates in separate commits for easier rollback.

### 5. Verify CI Passes
Always check that CI workflows pass after version updates.

## Troubleshooting

### Version Mismatch Errors
If you see version mismatch errors:

1. **Check all files** for hardcoded versions:
   ```bash
   grep -r "0.11.13" . --exclude-dir=.git --exclude-dir=__pycache__
   ```

2. **Use the script** to update all occurrences:
   ```bash
   ./scripts/update-versions.sh update ruff 0.11.13
   ```

### CI Environment Variable Issues
If CI can't find environment variables:

1. **Check the load step** is present in all jobs
2. **Verify variable names** match `.github/versions.env`
3. **Check file path** - ensure `.github/versions.env` exists
4. **Use hardcoded fallbacks** as temporary solution

## Future Improvements

1. **Automated Version Checking**: Script to detect version inconsistencies
2. **Dependency Updates**: Automated PR creation for dependency updates
3. **Version Locking**: Pin exact versions instead of using ranges
4. **Validation**: Add validation to ensure `.github/versions.env` is properly formatted
5. **Testing**: Add tests to verify version consistency across all environments

## Example Workflow

```bash
# 1. Update ruff to latest version
./scripts/update-versions.sh update ruff v0.12.0

# 2. Test locally
pre-commit run --all-files
uv run pytest

# 3. Commit changes
git add .
git commit -m "chore: update ruff to 0.12.0"

# 4. Push and verify CI
git push origin main

# 5. Check GitHub Actions tab
```

This system ensures that all environments use the same versions, reducing inconsistencies and maintenance overhead.

## Verification

To verify that the version management is working correctly:

1. **Check the CI logs** for the "Load versions from .env file" step
2. **Verify the output** shows the correct versions being loaded
3. **Confirm installation** uses the versions from `.github/versions.env`
4. **Test locally** by running the same commands

Example CI log output:
```
Run source .github/versions.env
  source .github/versions.env
  echo "UV_VERSION=$UV_VERSION" >> $GITHUB_ENV
  echo "RUFF_VERSION=$RUFF_VERSION" >> $GITHUB_ENV
  shell: /usr/bin/bash -e {0}
UV_VERSION=0.8.6
RUFF_VERSION=0.11.13
```

This confirms that the versions are being loaded correctly from the centralized file.
