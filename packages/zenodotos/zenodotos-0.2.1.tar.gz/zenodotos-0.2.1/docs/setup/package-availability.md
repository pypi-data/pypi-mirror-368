# Package Availability Checking

This document describes how to check if your Zenodotos package is available and ready for installation on PyPI and TestPyPI.

## Overview

The package availability checker (`scripts/check-package-availability.sh`) provides comprehensive verification of package availability on both PyPI and TestPyPI. It can:

- Check if a specific package version is available on PyPI/TestPyPI
- Verify that packages are actually installable via pip
- Provide timing information for deployment processes
- Show detailed package metadata when available
- Track upload times and propagation status

## Quick Start

### Check Current Version Availability

```bash
# Check current version on both PyPI and TestPyPI
./scripts/check-package-availability.sh

# Check only PyPI
./scripts/check-package-availability.sh --pypi

# Check only TestPyPI
./scripts/check-package-availability.sh --testpypi
```

### Check Specific Version

```bash
# Check specific version
./scripts/check-package-availability.sh zenodotos 0.2.0

# Check with pip installation test
./scripts/check-package-availability.sh --pip-test zenodotos 0.2.0
```

### View Deployment Time Information

```bash
# Show typical deployment times
./scripts/check-package-availability.sh --deployment-times
```

## Detailed Usage

### Basic Commands

```bash
# Check current version on both indexes
./scripts/check-package-availability.sh

# Check specific package and version
./scripts/check-package-availability.sh <package_name> <version>

# Check with detailed timing information
./scripts/check-package-availability.sh --timing

# Check with pip installation verification
./scripts/check-package-availability.sh --pip-test
```

### Options

#### Target Options (choose one)
| Option | Description |
|--------|-------------|
| `--pypi` | Check only PyPI availability |
| `--testpypi` | Check only TestPyPI availability |

#### Additional Options
| Option | Description |
|--------|-------------|
| `--pip-test` | Also test pip installation |
| `--timing` | Show detailed timing information |
| `--deployment-times` | Show typical deployment time information |
| `--help` | Show help message |

**Note**: Only one target option (`--pypi` or `--testpypi`) can be used at a time. If no target is specified, both indexes will be checked.

### Examples

```bash
# Check current version on both indexes (default)
./scripts/check-package-availability.sh

# Check current version with full verification
./scripts/check-package-availability.sh --pip-test --timing

# Check specific version on TestPyPI only
./scripts/check-package-availability.sh --testpypi --pip-test zenodotos 0.2.0

# Check production PyPI with timing
./scripts/check-package-availability.sh --pypi --timing zenodotos 0.2.0

# Just show deployment time information
./scripts/check-package-availability.sh --deployment-times

# Invalid: Cannot use both targets together
./scripts/check-package-availability.sh --pypi --testpypi  # This will fail
```

## Understanding the Output

### Availability Status

The script provides clear status indicators:

- ✅ **AVAILABLE**: Package is found on the index
- ❌ **NOT AVAILABLE**: Package is not found on the index
- ✅ **INSTALLABLE**: Package can be installed via pip
- ❌ **NOT INSTALLABLE**: Package cannot be installed via pip

### Timing Information

The script tracks various timing metrics:

- **Response time**: How long the API request took
- **Installation time**: How long pip installation took
- **Upload time**: When the package was uploaded (if available)
- **Time since upload**: How long ago the package was uploaded

### Package Metadata

When available, the script displays:

- **Summary**: Package description
- **Author**: Package author information
- **Upload time**: When the package was uploaded
- **Package info**: Detailed pip show information

## Deployment Times

### Typical Timeframes

#### TestPyPI
- **Upload completion**: Immediate
- **Index propagation**: 1-5 minutes
- **Package availability**: 2-10 minutes
- **Full propagation**: Up to 15 minutes

#### Production PyPI
- **Upload completion**: Immediate
- **Index propagation**: 5-15 minutes
- **Package availability**: 10-30 minutes
- **Full propagation**: Up to 1 hour

### Factors Affecting Timing

- **Package size and complexity**: Larger packages take longer
- **Server load and queue length**: Busy periods increase delays
- **Network conditions**: Connection speed affects response times
- **CDN cache propagation**: Global distribution takes time

### Recent Upload Detection

The script automatically detects recently uploaded packages and provides warnings:

- **Very recent (< 5 minutes)**: "Index propagation may still be in progress"
- **Recent (< 1 hour)**: Shows time since upload
- **Older**: Shows hours since upload

## Integration with Release Process

The package availability checker is integrated into the release script (`scripts/release.sh`):

### Automatic Checking

After publishing to TestPyPI or PyPI, the release script automatically:

1. Waits 5 seconds for upload completion
2. Checks package availability
3. Tests pip installation (if available)
4. Provides status feedback

### Manual Verification

You can manually verify package availability at any time:

```bash
# After TestPyPI release
./scripts/check-package-availability.sh --testpypi --pip-test

# After production release
./scripts/check-package-availability.sh --pypi --pip-test

# Check both indexes
./scripts/check-package-availability.sh --pip-test
```

## Troubleshooting

### Common Issues

#### Package Not Found

If a package is not found immediately after upload:

1. **Wait a few minutes**: Index propagation takes time
2. **Check again**: Use the availability checker
3. **Verify upload**: Check the upload response for errors
4. **Check version**: Ensure the version number is correct

#### Installation Failures

If a package is available but not installable:

1. **Check dependencies**: Verify all dependencies are available
2. **Check Python version**: Ensure compatibility
3. **Check package format**: Verify the package was built correctly
4. **Check index configuration**: Ensure correct index URLs

#### Slow Response Times

If the checker is slow:

1. **Check network**: Verify internet connection
2. **Check server status**: PyPI/TestPyPI may be experiencing issues
3. **Retry**: Network issues are often temporary
4. **Use timing option**: Get detailed timing information

### Error Messages

#### "curl is not installed"
```bash
# Install curl
sudo apt-get install curl  # Ubuntu/Debian
brew install curl          # macOS
```

#### "jq is not installed"
```bash
# Install jq (optional, for better JSON parsing)
sudo apt-get install jq    # Ubuntu/Debian
brew install jq            # macOS
```

#### "Package not found"
- Verify the package name and version
- Check if the package was actually uploaded
- Wait for index propagation
- Check for typos in package name or version

## Best Practices

### During Development

1. **Test frequently**: Check availability after each TestPyPI upload
2. **Use pip testing**: Verify packages are actually installable
3. **Monitor timing**: Track deployment times for your packages
4. **Document issues**: Note any unusual delays or problems

### During Release

1. **Pre-release verification**: Check current version availability
2. **Post-upload verification**: Verify upload success immediately
3. **Installation testing**: Test actual installation before announcing
4. **Monitoring**: Check periodically until fully propagated

### Automation

1. **CI/CD integration**: Include availability checks in release pipelines
2. **Scheduled checks**: Monitor package availability over time
3. **Alerting**: Set up notifications for availability issues
4. **Documentation**: Keep deployment time records

## Advanced Usage

### Custom Package Names

Check availability for any package:

```bash
# Check other packages
./scripts/check-package-availability.sh requests 2.31.0
./scripts/check-package-availability.sh click 8.1.7
```

### Batch Checking

Check multiple versions:

```bash
# Check multiple versions
for version in 0.1.0 0.2.0 0.3.0; do
    echo "Checking version $version..."
    ./scripts/check-package-availability.sh zenodotos $version
    echo ""
done
```

### Integration with CI/CD

```bash
# Example CI/CD script
#!/bin/bash
set -e

# Publish package
./scripts/release.sh --test

# Wait for propagation
sleep 60

# Verify availability
if ./scripts/check-package-availability.sh --testpypi --pip-test; then
    echo "Package is ready for testing"
    exit 0
else
    echo "Package not yet available"
    exit 1
fi
```

## API Endpoints

The script uses these PyPI/TestPyPI API endpoints:

- **PyPI JSON API**: `https://pypi.org/pypi/{package}/{version}/json`
- **TestPyPI JSON API**: `https://test.pypi.org/pypi/{package}/{version}/json`
- **PyPI Simple Index**: `https://pypi.org/simple/`
- **TestPyPI Simple Index**: `https://test.pypi.org/simple/`

## Environment Variables

The script respects these environment variables:

- `PYPI_TOKEN`: Your PyPI API token (for authenticated requests)
- `TEST_PYPI_TOKEN`: Your TestPyPI API token (for authenticated requests)

## Dependencies

Required:
- `curl`: For HTTP requests
- `bash`: Shell environment

Optional:
- `jq`: For JSON parsing (provides better output formatting)

## Related Scripts

- `scripts/release.sh`: Main release script with integrated availability checking
- `scripts/test-pypi-install.sh`: Comprehensive TestPyPI installation testing
- `scripts/update-versions.sh`: Version management utilities
