#!/bin/bash

# Version Management Script for Zenodotos Project
# This script updates tool versions across all configuration files

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

# Function to validate version format (supports v prefix)
validate_version() {
    local version=$1
    # Support both v1.2.3 and 1.2.3 formats
    if [[ $version =~ ^v?[0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9]*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to strip v prefix for internal processing
strip_v_prefix() {
    local version=$1
    echo "${version#v}"
}

# Function to update version in a file
update_version() {
    local file=$1
    local tool=$2
    local new_version=$3
    local pattern=$4

    if [ -f "$file" ]; then
        # Handle different patterns for different file types
        if [[ $pattern == *"$tool"* ]]; then
            # For patterns that include the tool name
            sed -i "s/$pattern/$tool=$new_version/g" "$file"
        else
            # For patterns that are just the tool name
            sed -i "s/$tool[[:space:]]*=[[:space:]]*[^[:space:]]*/$tool=$new_version/g" "$file"
        fi
        print_success "Updated $tool to $new_version in $file"
    else
        print_warning "File $file not found, skipping"
    fi
}

# Function to update pre-commit config
update_pre_commit() {
    local tool=$1
    local new_version=$2

    case $tool in
        "ruff")
            update_version ".pre-commit-config.yaml" "ruff-pre-commit" "v$new_version" "rev:[[:space:]]*v[^[:space:]]*"
            ;;
        "pre-commit")
            update_version ".pre-commit-config.yaml" "pre-commit-hooks" "v$new_version" "rev:[[:space:]]*v[^[:space:]]*"
            ;;
    esac
}

# Function to update pyproject.toml
update_pyproject() {
    local tool=$1
    local new_version=$2

    case $tool in
        "ruff"|"radon"|"bandit"|"pydocstyle"|"sphinx"|"sphinx-rtd-theme"|"myst-parser"|"build"|"ty"|"pre-commit"|"pytest"|"pytest-cov")
            # Update in dependency-groups.dev
            sed -i "/$tool[[:space:]]*>=/s/>=[^[:space:]]*/>=$new_version/g" pyproject.toml
            # Update in optional-dependencies.dev
            sed -i "/$tool[[:space:]]*>=/s/>=[^[:space:]]*/>=$new_version/g" pyproject.toml
            print_success "Updated $tool to $new_version in pyproject.toml"
            ;;
    esac
}

# Function to update CI workflows
update_ci_workflows() {
    local tool=$1
    local new_version=$2

    case $tool in
        "uv")
            # Update in .github/versions.env
            update_version ".github/versions.env" "UV_VERSION" "$new_version"
            # Update in CI workflows (matrix values)
            sed -i "s/uv-version:[[:space:]]*\[\"[^[:space:]]*\"/uv-version: [\"$new_version\"/g" .github/workflows/*.yml
            ;;
        "ruff")
            # Update in .github/versions.env
            update_version ".github/versions.env" "RUFF_VERSION" "$new_version"
            # Update hardcoded ruff versions in CI
            sed -i "s/ruff==[^[:space:]]*/ruff==$new_version/g" .github/workflows/*.yml
            ;;
        "radon"|"bandit"|"pydocstyle")
            # Update in .github/versions.env
            update_version ".github/versions.env" "${tool^^}_VERSION" "$new_version"
            ;;
    esac
}

# Function to update all versions for a tool
update_all_versions() {
    local tool=$1
    local new_version=$2

    print_info "Updating $tool to version $new_version..."

    # Validate version format
    if ! validate_version "$new_version"; then
        print_error "Invalid version format: $new_version"
        print_info "Expected format: v1.2.3 or 1.2.3"
        exit 1
    fi

    # Strip v prefix for processing
    local clean_version=$(strip_v_prefix "$new_version")

    # Update .github/versions.env
    update_version ".github/versions.env" "${tool^^}_VERSION" "$clean_version"

    # Update pyproject.toml
    update_pyproject "$tool" "$clean_version"

    # Update pre-commit config
    update_pre_commit "$tool" "$clean_version"

    # Update CI workflows
    update_ci_workflows "$tool" "$clean_version"

    print_success "Successfully updated $tool to $new_version across all files"
}

# Function to sync pre-commit versions from .github/versions.env
sync_pre_commit_versions() {
    print_info "Syncing pre-commit hook versions from .github/versions.env..."

    # Read versions from .env file
    source .github/versions.env

    # Update ruff-pre-commit
    if [ -n "$RUFF_VERSION" ]; then
        update_version ".pre-commit-config.yaml" "ruff-pre-commit" "v$RUFF_VERSION" "rev:[[:space:]]*v[^[:space:]]*"
    fi

    # Update pre-commit-hooks (use PRE_COMMIT_VERSION)
    if [ -n "$PRE_COMMIT_VERSION" ]; then
        update_version ".pre-commit-config.yaml" "pre-commit-hooks" "v$PRE_COMMIT_VERSION" "rev:[[:space:]]*v[^[:space:]]*"
    fi

    print_success "Pre-commit versions synced successfully"
}

# Main script logic
main() {
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <command> [tool] [version]"
        echo ""
        echo "Commands:"
        echo "  update <tool> <version>  Update version for a specific tool"
        echo "  sync                     Sync pre-commit versions from .github/versions.env"
        echo ""
        echo "Available tools:"
        echo "  ruff, uv, radon, bandit, pydocstyle, sphinx, build, ty, pre-commit, pytest"
        echo ""
        echo "Examples:"
        echo "  $0 update ruff v0.12.0"
        echo "  $0 update uv 0.9.0"
        echo "  $0 sync"
        exit 1
    fi

    case $1 in
        "update")
            if [ $# -ne 3 ]; then
                print_error "Usage: $0 update <tool> <version>"
                exit 1
            fi
            update_all_versions "$2" "$3"
            ;;
        "sync")
            sync_pre_commit_versions
            ;;
        *)
            print_error "Unknown command: $1"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
