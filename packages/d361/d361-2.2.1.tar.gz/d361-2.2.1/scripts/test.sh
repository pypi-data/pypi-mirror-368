#!/usr/bin/env bash
# this_file: scripts/test.sh
# Test script for d361 project

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}==> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run linting
run_lint() {
    print_step "Running code formatting and linting"
    
    # Check style
    if ! hatch run lint:style; then
        print_error "Code style check failed"
        return 1
    fi
    
    print_success "Code style check passed"
    return 0
}

# Function to run type checking
run_type_check() {
    print_step "Running type checking"
    
    if ! hatch run lint:typing; then
        print_error "Type checking failed"
        return 1
    fi
    
    print_success "Type checking passed"
    return 0
}

# Function to run unit tests
run_unit_tests() {
    print_step "Running unit tests"
    
    if ! hatch run test:test-cov; then
        print_error "Unit tests failed"
        return 1
    fi
    
    print_success "Unit tests passed"
    return 0
}

# Function to run integration tests
run_integration_tests() {
    print_step "Running integration tests"
    
    if ! hatch run test:test -k "integration"; then
        print_warning "Integration tests failed or not found"
        return 1
    fi
    
    print_success "Integration tests passed"
    return 0
}

# Function to install playwright browsers
install_playwright_browsers() {
    print_step "Installing Playwright browsers"
    
    if ! command_exists playwright; then
        print_warning "Playwright not found, installing..."
        uv pip install playwright
    fi
    
    if ! playwright install chromium; then
        print_error "Failed to install Playwright browsers"
        return 1
    fi
    
    print_success "Playwright browsers installed"
    return 0
}

# Main test function
main() {
    local run_lint=true
    local run_types=true
    local run_unit=true
    local run_integration=false
    local install_browsers=false
    local coverage=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-lint)
                run_lint=false
                shift
                ;;
            --no-types)
                run_types=false
                shift
                ;;
            --no-unit)
                run_unit=false
                shift
                ;;
            --integration)
                run_integration=true
                shift
                ;;
            --install-browsers)
                install_browsers=true
                shift
                ;;
            --no-coverage)
                coverage=false
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --no-lint           Skip linting checks"
                echo "  --no-types          Skip type checking"
                echo "  --no-unit           Skip unit tests"
                echo "  --integration       Run integration tests"
                echo "  --install-browsers  Install Playwright browsers"
                echo "  --no-coverage       Skip coverage reporting"
                echo "  --help, -h          Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    print_step "Starting test suite for d361"
    
    # Check for required tools
    if ! command_exists uv; then
        print_error "uv is required but not installed. Please install uv first."
        exit 1
    fi
    
    if ! command_exists hatch; then
        print_warning "hatch not found, installing..."
        uv pip install hatch
    fi
    
    # Install Playwright browsers if requested
    if [[ "$install_browsers" == "true" ]]; then
        install_playwright_browsers || exit 1
    fi
    
    # Run linting if enabled
    if [[ "$run_lint" == "true" ]]; then
        run_lint || exit 1
    fi
    
    # Run type checking if enabled
    if [[ "$run_types" == "true" ]]; then
        run_type_check || exit 1
    fi
    
    # Run unit tests if enabled
    if [[ "$run_unit" == "true" ]]; then
        if [[ "$coverage" == "true" ]]; then
            run_unit_tests || exit 1
        else
            print_step "Running unit tests (no coverage)"
            if ! hatch run test:test; then
                print_error "Unit tests failed"
                exit 1
            fi
            print_success "Unit tests passed"
        fi
    fi
    
    # Run integration tests if enabled
    if [[ "$run_integration" == "true" ]]; then
        run_integration_tests || {
            print_warning "Integration tests failed or not found (continuing)"
        }
    fi
    
    print_success "All tests completed successfully!"
}

# Quick test mode
quick_test() {
    print_step "Quick test mode (unit tests only)"
    
    if ! hatch run test:test; then
        print_error "Quick tests failed"
        exit 1
    fi
    
    print_success "Quick tests passed"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --quick             Run only unit tests (no coverage, no lint)"
        echo "  --fix               Fix linting issues"
        echo "  --no-lint           Skip linting checks"
        echo "  --no-types          Skip type checking"
        echo "  --no-unit           Skip unit tests"
        echo "  --integration       Run integration tests"
        echo "  --install-browsers  Install Playwright browsers"
        echo "  --no-coverage       Skip coverage reporting"
        exit 0
        ;;
    --quick)
        quick_test
        ;;
    --fix)
        print_step "Fixing linting issues"
        hatch run lint:fix
        print_success "Linting issues fixed"
        ;;
    "")
        main
        ;;
    *)
        main "$@"
        ;;
esac