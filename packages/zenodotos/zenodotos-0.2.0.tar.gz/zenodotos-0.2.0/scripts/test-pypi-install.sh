#!/bin/bash

# TestPyPI Installation Test Script
# This script tests installing and using the Zenodotos package from TestPyPI

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment
validate_environment() {
    print_info "Validating environment..."

    # Check if uv is installed
    if ! command_exists uv; then
        print_error "uv is not installed. Please install it first."
        exit 1
    fi

    print_success "Environment validation passed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [VERSION]"
    echo ""
    echo "Options:"
    echo "  --clean         Clean up test environment after testing"
    echo "  --keep          Keep test environment for inspection (default)"
    echo "  --help          Show this help message"
    echo ""
    echo "Arguments:"
    echo "  VERSION         Specific version to test (default: latest)"
    echo ""
    echo "Example:"
    echo "  $0                    # Test latest version"
    echo "  $0 0.1.0             # Test specific version"
    echo "  $0 --clean 0.1.0     # Test and clean up"
}

# Parse command line arguments
CLEAN_AFTER=false
VERSION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_AFTER=true
            shift
            ;;
        --keep)
            CLEAN_AFTER=false
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$VERSION" ]; then
                VERSION="$1"
            else
                print_error "Multiple versions specified: $VERSION and $1"
                exit 1
            fi
            shift
            ;;
    esac
done

# Main execution
print_info "Starting TestPyPI installation test..."

# Validate environment
validate_environment

# Create temporary directory for testing
TEST_DIR=$(mktemp -d)
print_info "Created test directory: $TEST_DIR"

# Function to clean up
cleanup() {
    if [ "$CLEAN_AFTER" = true ]; then
        print_info "Cleaning up test directory..."
        rm -rf "$TEST_DIR"
        print_success "Test directory cleaned up"
    else
        print_info "Test directory preserved at: $TEST_DIR"
        print_info "You can inspect it manually or run with --clean to remove it"
    fi
}

# Set up trap to clean up on exit
trap cleanup EXIT

# Change to test directory
cd "$TEST_DIR"
print_info "Changed to test directory: $(pwd)"

# Create virtual environment
print_info "Creating virtual environment..."
uv venv
print_success "Virtual environment created"

# Initialize uv project
print_info "Initializing uv project..."
uv init .
print_success "Project initialized"

# Install from TestPyPI
    print_info "Installing Zenodotos from TestPyPI..."
if [ -n "$VERSION" ]; then
    print_info "Installing specific version: $VERSION"
            uv add --index https://test.pypi.org/simple/ --index-strategy unsafe-best-match "zenodotos==$VERSION"
else
    print_info "Installing latest version"
            uv add --index https://test.pypi.org/simple/ --index-strategy unsafe-best-match zenodotos
fi

# Test basic functionality
print_info "Testing basic functionality..."

# Test help command
print_info "Testing 'zenodotos --help'..."
if uv run zenodotos --help > /dev/null 2>&1; then
    print_success "zenodotos --help works correctly"
else
    print_error "zenodotos --help failed"
    exit 1
fi

# Test list-files help
print_info "Testing 'zenodotos list-files --help'..."
if uv run zenodotos list-files --help > /dev/null 2>&1; then
    print_success "zenodotos list-files --help works correctly"
else
    print_error "zenodotos list-files --help failed"
    exit 1
fi

# Test get-file help
print_info "Testing 'zenodotos get-file --help'..."
if uv run zenodotos get-file --help > /dev/null 2>&1; then
    print_success "zenodotos get-file --help works correctly"
else
    print_error "zenodotos get-file --help failed"
    exit 1
fi

# Test export help
print_info "Testing 'zenodotos export --help'..."
if uv run zenodotos export --help > /dev/null 2>&1; then
    print_success "zenodotos export --help works correctly"
else
    print_error "zenodotos export --help failed"
    exit 1
fi

# Show installed package info
print_info "Installed package information:"
uv pip show zenodotos

# Test Python import
print_info "Testing Python import..."
if uv run python -c "import zenodotos; print('✅ Zenodotos imported successfully')" 2>/dev/null; then
    print_success "Python import test passed"
else
    print_error "Python import test failed"
    exit 1
fi

# Test library usage
print_info "Testing library usage..."
if uv run python -c "
from zenodotos import Zenodotos
print('✅ Zenodotos class imported successfully')
try:
    client = Zenodotos()
    print('✅ Zenodotos client created successfully')
except Exception as e:
    print(f'⚠️  Zenodotos client creation failed (expected without auth): {e}')
" 2>/dev/null; then
    print_success "Library usage test passed"
else
    print_error "Library usage test failed"
    exit 1
fi

print_success "All TestPyPI installation tests passed!"
print_info "Version tested: $(uv run pip show zenodotos | grep Version | cut -d' ' -f2)"

# Show what was tested
echo ""
print_info "Test Summary:"
echo "  ✅ Package installation from TestPyPI"
echo "  ✅ CLI help commands"
echo "  ✅ Python import"
echo "  ✅ Library usage"
echo "  ✅ All basic functionality"

if [ "$CLEAN_AFTER" = false ]; then
    echo ""
    print_info "Test environment preserved at: $TEST_DIR"
    print_info "You can inspect it or run additional tests manually"
fi
