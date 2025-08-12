#!/bin/bash

# Package Availability Checker for Zenodotos
# This script checks if a package version is available on PyPI or TestPyPI
# and provides information about typical deployment times

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

print_debug() {
    echo -e "${PURPLE}🔍 $1${NC}"
}

print_timing() {
    echo -e "${CYAN}⏱️  $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment
validate_environment() {
    print_info "Validating environment..."

    # Check if curl is installed
    if ! command_exists curl; then
        print_error "curl is not installed. Please install it first."
        exit 1
    fi

    # Check if jq is installed (for JSON parsing)
    if ! command_exists jq; then
        print_warning "jq is not installed. JSON responses will be shown as raw text."
        JQ_AVAILABLE=false
    else
        JQ_AVAILABLE=true
    fi

    print_success "Environment validation passed"
}

# Function to get current version from pyproject.toml
get_current_version() {
    if [ -f "pyproject.toml" ]; then
        grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'
    else
        echo ""
    fi
}

# Function to check package availability on PyPI
check_pypi_availability() {
    local package_name="$1"
    local version="$2"
    local start_time=$(date +%s)

    print_info "Checking PyPI availability for $package_name==$version..."

    # Try to get package info from PyPI JSON API
    local response
    if response=$(curl -s -f "https://pypi.org/pypi/$package_name/$version/json" 2>/dev/null); then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        if [ "$JQ_AVAILABLE" = true ]; then
            local info=$(echo "$response" | jq -r '.info')
            local version_info=$(echo "$response" | jq -r '.releases["'"$version"'"]')

            print_success "Package $package_name==$version is AVAILABLE on PyPI"
            print_timing "Response time: ${duration}s"

            # Extract useful information
            local summary=$(echo "$info" | jq -r '.summary // "No summary"')
            local author=$(echo "$info" | jq -r '.author // "Unknown"')
            local upload_time=$(echo "$version_info" | jq -r '.[0].upload_time // "Unknown"')

            echo "  📦 Summary: $summary"
            echo "  👤 Author: $author"
            echo "  📅 Upload time: $upload_time"

            # Check if it's a recent upload
            if [ "$upload_time" != "Unknown" ]; then
                local upload_timestamp=$(date -d "$upload_time" +%s 2>/dev/null || echo "0")
                local current_timestamp=$(date +%s)
                local time_since_upload=$((current_timestamp - upload_timestamp))

                if [ $time_since_upload -lt 300 ]; then
                    print_warning "Package was uploaded very recently (${time_since_upload}s ago)"
                    print_info "Index propagation may still be in progress..."
                elif [ $time_since_upload -lt 3600 ]; then
                    print_info "Package was uploaded ${time_since_upload}s ago"
                else
                    local hours=$((time_since_upload / 3600))
                    print_info "Package was uploaded ${hours}h ago"
                fi
            fi

            return 0
        else
            print_success "Package $package_name==$version is AVAILABLE on PyPI"
            print_timing "Response time: ${duration}s"
            echo "Raw response: $response"
            return 0
        fi
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "Package $package_name==$version is NOT AVAILABLE on PyPI"
        print_timing "Response time: ${duration}s"
        return 1
    fi
}

# Function to check package availability on TestPyPI
check_testpypi_availability() {
    local package_name="$1"
    local version="$2"
    local start_time=$(date +%s)

    print_info "Checking TestPyPI availability for $package_name==$version..."

    # Try to get package info from TestPyPI JSON API
    local response
    if response=$(curl -s -f "https://test.pypi.org/pypi/$package_name/$version/json" 2>/dev/null); then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        if [ "$JQ_AVAILABLE" = true ]; then
            local info=$(echo "$response" | jq -r '.info')
            local version_info=$(echo "$response" | jq -r '.releases["'"$version"'"]')

            print_success "Package $package_name==$version is AVAILABLE on TestPyPI"
            print_timing "Response time: ${duration}s"

            # Extract useful information
            local summary=$(echo "$info" | jq -r '.summary // "No summary"')
            local author=$(echo "$info" | jq -r '.author // "Unknown"')
            local upload_time=$(echo "$version_info" | jq -r '.[0].upload_time // "Unknown"')

            echo "  📦 Summary: $summary"
            echo "  👤 Author: $author"
            echo "  📅 Upload time: $upload_time"

            # Check if it's a recent upload
            if [ "$upload_time" != "Unknown" ]; then
                local upload_timestamp=$(date -d "$upload_time" +%s 2>/dev/null || echo "0")
                local current_timestamp=$(date +%s)
                local time_since_upload=$((current_timestamp - upload_timestamp))

                if [ $time_since_upload -lt 300 ]; then
                    print_warning "Package was uploaded very recently (${time_since_upload}s ago)"
                    print_info "Index propagation may still be in progress..."
                elif [ $time_since_upload -lt 3600 ]; then
                    print_info "Package was uploaded ${time_since_upload}s ago"
                else
                    local hours=$((time_since_upload / 3600))
                    print_info "Package was uploaded ${hours}h ago"
                fi
            fi

            return 0
        else
            print_success "Package $package_name==$version is AVAILABLE on TestPyPI"
            print_timing "Response time: ${duration}s"
            echo "Raw response: $response"
            return 0
        fi
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "Package $package_name==$version is NOT AVAILABLE on TestPyPI"
        print_timing "Response time: ${duration}s"
        return 1
    fi
}

# Function to wait for package availability
wait_for_availability() {
    local package_name="$1"
    local version="$2"
    local index_type="$3"  # "pypi" or "testpypi"
    local timeout_seconds="$4"
    local interval_seconds="$5"

    local start_time=$(date +%s)
    local elapsed_time=0

    print_info "Waiting for $package_name==$version to become available on $index_type..."
    print_info "Timeout: ${timeout_seconds}s, Check interval: ${interval_seconds}s"
    echo ""

    while [ $elapsed_time -lt $timeout_seconds ]; do
        # Check availability
        if [ "$index_type" = "pypi" ]; then
            if check_pypi_availability "$package_name" "$version" >/dev/null 2>&1; then
                local end_time=$(date +%s)
                local total_wait_time=$((end_time - start_time))
                print_success "Package $package_name==$version is now AVAILABLE on PyPI!"
                print_timing "Total wait time: ${total_wait_time}s"
                return 0
            fi
        elif [ "$index_type" = "testpypi" ]; then
            if check_testpypi_availability "$package_name" "$version" >/dev/null 2>&1; then
                local end_time=$(date +%s)
                local total_wait_time=$((end_time - start_time))
                print_success "Package $package_name==$version is now AVAILABLE on TestPyPI!"
                print_timing "Total wait time: ${total_wait_time}s"
                return 0
            fi
        fi

        # Calculate remaining time
        local remaining_time=$((timeout_seconds - elapsed_time))
        local minutes=$((remaining_time / 60))
        local seconds=$((remaining_time % 60))

        # Show progress
        if [ $minutes -gt 0 ]; then
            print_info "Package not yet available. Waiting ${interval_seconds}s... (${elapsed_time}/${timeout_seconds}s, ~${minutes}m ${seconds}s remaining)"
        else
            print_info "Package not yet available. Waiting ${interval_seconds}s... (${elapsed_time}/${timeout_seconds}s, ${seconds}s remaining)"
        fi

        sleep $interval_seconds
        elapsed_time=$((elapsed_time + interval_seconds))
    done

    local end_time=$(date +%s)
    local total_wait_time=$((end_time - start_time))
    print_error "Package $package_name==$version did not become available on $index_type within ${timeout_seconds}s"
    print_timing "Total wait time: ${total_wait_time}s"
    return 1
}

# Function to check package availability via pip
check_pip_availability() {
    local package_name="$1"
    local version="$2"
    local index_url="$3"
    local index_name="$4"

    print_info "Checking $index_name availability via pip for $package_name==$version..."

    # Create temporary directory for testing
    local temp_dir=$(mktemp -d)
    local start_time=$(date +%s)

    # Function to clean up
    cleanup_pip_test() {
        rm -rf "$temp_dir"
    }

    # Set up trap to clean up on exit
    trap cleanup_pip_test EXIT

    # Change to temp directory
    cd "$temp_dir"

    # Try to install the package
    if uv add --index "$index_url" --index-strategy unsafe-best-match "$package_name==$version" >/dev/null 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        print_success "Package $package_name==$version is INSTALLABLE from $index_name"
        print_timing "Installation time: ${duration}s"

        # Get package info
        local package_info=$(uv pip show "$package_name" 2>/dev/null || echo "Package info not available")
        echo "Package information:"
        echo "$package_info" | sed 's/^/  /'

        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        print_error "Package $package_name==$version is NOT INSTALLABLE from $index_name"
        print_timing "Failed after: ${duration}s"
        return 1
    fi
}

# Function to show deployment time information
show_deployment_times() {
    echo ""
    print_info "📊 Typical Deployment Times:"
    echo ""
    echo "  🧪 TestPyPI:"
    echo "    • Upload completion: Immediate"
    echo "    • Index propagation: 1-5 minutes"
    echo "    • Package availability: 2-10 minutes"
    echo "    • Full propagation: Up to 15 minutes"
    echo ""
    echo "  🚀 Production PyPI:"
    echo "    • Upload completion: Immediate"
    echo "    • Index propagation: 5-15 minutes"
    echo "    • Package availability: 10-30 minutes"
    echo "    • Full propagation: Up to 1 hour"
    echo ""
    echo "  📈 Factors affecting timing:"
    echo "    • Package size and complexity"
    echo "    • Server load and queue length"
    echo "    • Network conditions"
    echo "    • CDN cache propagation"
    echo ""
    print_warning "Note: These are typical times. Actual times may vary significantly."
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [PACKAGE_NAME] [VERSION]"
    echo ""
    echo "Target Options (choose one):"
    echo "  --pypi              Check only PyPI availability"
    echo "  --testpypi          Check only TestPyPI availability"
    echo ""
    echo "Additional Options:"
    echo "  --pip-test          Also test pip installation"
    echo "  --wait              Wait for package to become available"
    echo "  --timeout SECONDS   Maximum wait time in seconds (default: 600 for PyPI, 300 for TestPyPI)"
    echo "  --interval SECONDS  Check interval in seconds (default: 30)"
    echo "  --timing            Show detailed timing information"
    echo "  --deployment-times  Show typical deployment time information"
    echo "  --help              Show this help message"
    echo ""
    echo "Arguments:"
    echo "  PACKAGE_NAME        Package name to check (default: zenodotos)"
    echo "  VERSION             Version to check (default: current version from pyproject.toml)"
    echo ""
    echo "Examples:"
    echo "  $0 --pypi                            # Check only PyPI"
    echo "  $0 --testpypi                        # Check only TestPyPI"
    echo "  $0 --pypi --pip-test                 # Check PyPI with pip installation test"
    echo "  $0 --testpypi --wait                 # Wait for TestPyPI availability (up to 5 minutes)"
    echo "  $0 --pypi --wait --timeout 1800      # Wait for PyPI availability (up to 30 minutes)"
    echo "  $0 --deployment-times                # Show deployment time information"
    echo ""
    echo "Note: Only one target option (--pypi or --testpypi) can be used at a time."
    echo "      If no target is specified, both indexes will be checked."
    echo ""
    echo "Environment variables:"
    echo "  PYPI_TOKEN          Your PyPI API token (for authenticated requests)"
    echo "  TEST_PYPI_TOKEN     Your TestPyPI API token (for authenticated requests)"
}

# Parse command line arguments
CHECK_PYPI=false
CHECK_TESTPYPI=false
CHECK_PIP=false
WAIT_FOR_AVAILABILITY=false
TIMEOUT_SECONDS=0
INTERVAL_SECONDS=30
SHOW_TIMING=false
SHOW_DEPLOYMENT_TIMES=false
PACKAGE_NAME="zenodotos"
VERSION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --pypi)
            if [ "$CHECK_TESTPYPI" = true ]; then
                print_error "Cannot use --pypi and --testpypi together. Use only one target."
                show_usage
                exit 1
            fi
            CHECK_PYPI=true
            shift
            ;;
        --testpypi)
            if [ "$CHECK_PYPI" = true ]; then
                print_error "Cannot use --pypi and --testpypi together. Use only one target."
                show_usage
                exit 1
            fi
            CHECK_TESTPYPI=true
            shift
            ;;

        --pip-test)
            CHECK_PIP=true
            shift
            ;;
        --wait)
            WAIT_FOR_AVAILABILITY=true
            shift
            ;;
        --timeout)
            if [ -z "$2" ] || [[ "$2" =~ ^- ]]; then
                print_error "--timeout requires a number of seconds"
                show_usage
                exit 1
            fi
            TIMEOUT_SECONDS="$2"
            shift 2
            ;;
        --interval)
            if [ -z "$2" ] || [[ "$2" =~ ^- ]]; then
                print_error "--interval requires a number of seconds"
                show_usage
                exit 1
            fi
            INTERVAL_SECONDS="$2"
            shift 2
            ;;
        --timing)
            SHOW_TIMING=true
            shift
            ;;
        --deployment-times)
            SHOW_DEPLOYMENT_TIMES=true
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
            if [ -z "$PACKAGE_NAME" ] || [ "$PACKAGE_NAME" = "zenodotos" ]; then
                PACKAGE_NAME="$1"
            elif [ -z "$VERSION" ]; then
                VERSION="$1"
            else
                print_error "Too many arguments: $1"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Set default behavior if no target specified
if [ "$CHECK_PYPI" = false ] && [ "$CHECK_TESTPYPI" = false ]; then
    CHECK_PYPI=true
    CHECK_TESTPYPI=true
fi

# Set default timeout if waiting is enabled but no timeout specified
if [ "$WAIT_FOR_AVAILABILITY" = true ] && [ "$TIMEOUT_SECONDS" = 0 ]; then
    if [ "$CHECK_TESTPYPI" = true ]; then
        TIMEOUT_SECONDS=300  # 5 minutes for TestPyPI
    elif [ "$CHECK_PYPI" = true ]; then
        TIMEOUT_SECONDS=600  # 10 minutes for PyPI
    fi
fi

# Set default version if not provided
if [ -z "$VERSION" ]; then
    VERSION=$(get_current_version)
    if [ -z "$VERSION" ]; then
        print_error "No version specified and could not determine current version from pyproject.toml"
        print_info "Please specify a version: $0 $PACKAGE_NAME <version>"
        exit 1
    fi
fi

# Show deployment times if requested
if [ "$SHOW_DEPLOYMENT_TIMES" = true ]; then
    show_deployment_times
    exit 0
fi

# Main execution
print_info "Starting package availability check..."
print_info "Package: $PACKAGE_NAME"
print_info "Version: $VERSION"
echo ""

# Validate environment
validate_environment

# Track overall start time
OVERALL_START_TIME=$(date +%s)

# Check PyPI availability
if [ "$CHECK_PYPI" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_info "🔍 CHECKING PRODUCTION PYPI"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ "$WAIT_FOR_AVAILABILITY" = true ]; then
        if wait_for_availability "$PACKAGE_NAME" "$VERSION" "pypi" "$TIMEOUT_SECONDS" "$INTERVAL_SECONDS"; then
            PYPI_AVAILABLE=true
        else
            PYPI_AVAILABLE=false
        fi
    else
        if check_pypi_availability "$PACKAGE_NAME" "$VERSION"; then
            PYPI_AVAILABLE=true
        else
            PYPI_AVAILABLE=false
        fi
    fi

    # Test pip installation if requested
    if [ "$CHECK_PIP" = true ] && [ "$PYPI_AVAILABLE" = true ]; then
        echo ""
        print_info "Testing pip installation from PyPI..."
        if check_pip_availability "$PACKAGE_NAME" "$VERSION" "https://pypi.org/simple/" "PyPI"; then
            PYPI_INSTALLABLE=true
        else
            PYPI_INSTALLABLE=false
        fi
    fi

    echo ""
fi

# Check TestPyPI availability
if [ "$CHECK_TESTPYPI" = true ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_info "🧪 CHECKING TEST PYPI"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ "$WAIT_FOR_AVAILABILITY" = true ]; then
        if wait_for_availability "$PACKAGE_NAME" "$VERSION" "testpypi" "$TIMEOUT_SECONDS" "$INTERVAL_SECONDS"; then
            TESTPYPI_AVAILABLE=true
        else
            TESTPYPI_AVAILABLE=false
        fi
    else
        if check_testpypi_availability "$PACKAGE_NAME" "$VERSION"; then
            TESTPYPI_AVAILABLE=true
        else
            TESTPYPI_AVAILABLE=false
        fi
    fi

    # Test pip installation if requested
    if [ "$CHECK_PIP" = true ] && [ "$TESTPYPI_AVAILABLE" = true ]; then
        echo ""
        print_info "Testing pip installation from TestPyPI..."
        if check_pip_availability "$PACKAGE_NAME" "$VERSION" "https://test.pypi.org/simple/" "TestPyPI"; then
            TESTPYPI_INSTALLABLE=true
        else
            TESTPYPI_INSTALLABLE=false
        fi
    fi

    echo ""
fi

# Calculate overall duration
OVERALL_END_TIME=$(date +%s)
OVERALL_DURATION=$((OVERALL_END_TIME - OVERALL_START_TIME))

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "📋 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$CHECK_PYPI" = true ]; then
    if [ "$PYPI_AVAILABLE" = true ]; then
        print_success "✅ PyPI: $PACKAGE_NAME==$VERSION is AVAILABLE"
        if [ "$CHECK_PIP" = true ]; then
            if [ "$PYPI_INSTALLABLE" = true ]; then
                print_success "✅ PyPI: Package is INSTALLABLE"
            else
                print_error "❌ PyPI: Package is NOT INSTALLABLE"
            fi
        fi
    else
        print_error "❌ PyPI: $PACKAGE_NAME==$VERSION is NOT AVAILABLE"
    fi
fi

if [ "$CHECK_TESTPYPI" = true ]; then
    if [ "$TESTPYPI_AVAILABLE" = true ]; then
        print_success "✅ TestPyPI: $PACKAGE_NAME==$VERSION is AVAILABLE"
        if [ "$CHECK_PIP" = true ]; then
            if [ "$TESTPYPI_INSTALLABLE" = true ]; then
                print_success "✅ TestPyPI: Package is INSTALLABLE"
            else
                print_error "❌ TestPyPI: Package is NOT INSTALLABLE"
            fi
        fi
    else
        print_error "❌ TestPyPI: $PACKAGE_NAME==$VERSION is NOT AVAILABLE"
    fi
fi

if [ "$SHOW_TIMING" = true ]; then
    echo ""
    print_timing "Total check duration: ${OVERALL_DURATION}s"
fi

echo ""
print_info "💡 Tips:"
echo "  • Use --pip-test to verify installation works"
echo "  • Use --deployment-times to see typical timing information"
echo "  • Check again in a few minutes if package was recently uploaded"
echo "  • Use --pypi or --testpypi to check only specific indexes"
