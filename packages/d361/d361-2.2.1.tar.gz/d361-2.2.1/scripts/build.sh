#!/usr/bin/env bash
# this_file: scripts/build.sh
# Build script for d361 project

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

# Main build function
main() {
    print_step "Starting build process for d361"
    
    # Check for required tools
    if ! command_exists uv; then
        print_error "uv is required but not installed. Please install uv first."
        exit 1
    fi
    
    if ! command_exists hatch; then
        print_warning "hatch not found, installing..."
        uv pip install hatch
    fi
    
    # Clean previous builds
    print_step "Cleaning previous builds"
    rm -rf dist/ build/ src/*.egg-info/
    print_success "Cleaned previous builds"
    
    # Install/update dependencies
    print_step "Installing dependencies"
    uv pip install --upgrade pip
    uv pip install --upgrade build hatchling hatch-vcs
    print_success "Dependencies installed"
    
    # Run code quality checks
    print_step "Running code quality checks"
    hatch run lint:style || {
        print_error "Code style checks failed"
        exit 1
    }
    print_success "Code quality checks passed"
    
    # Run type checking
    print_step "Running type checking"
    hatch run lint:typing || {
        print_error "Type checking failed"
        exit 1
    }
    print_success "Type checking passed"
    
    # Run tests
    print_step "Running tests"
    hatch run test:test-cov || {
        print_error "Tests failed"
        exit 1
    }
    print_success "All tests passed"
    
    # Build the package
    print_step "Building package"
    uv run python -m build --outdir dist || {
        print_error "Build failed"
        exit 1
    }
    print_success "Package built successfully"
    
    # Verify build artifacts
    print_step "Verifying build artifacts"
    if [ ! -f dist/*.whl ] || [ ! -f dist/*.tar.gz ]; then
        print_error "Build artifacts are missing"
        exit 1
    fi
    print_success "Build artifacts verified"
    
    # Show build results
    print_step "Build results"
    echo "Build artifacts:"
    ls -la dist/
    
    print_success "Build completed successfully!"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean        Clean build artifacts and exit"
        echo "  --quick        Skip tests and quality checks"
        exit 0
        ;;
    --clean)
        print_step "Cleaning build artifacts"
        rm -rf dist/ build/ src/*.egg-info/
        print_success "Cleaned build artifacts"
        exit 0
        ;;
    --quick)
        print_step "Quick build mode (skipping tests and quality checks)"
        rm -rf dist/ build/ src/*.egg-info/
        uv pip install --upgrade build hatchling hatch-vcs
        uv run python -m build --outdir dist
        print_success "Quick build completed"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac