#!/usr/bin/env bash
# this_file: scripts/install.sh
# Installation script for d361

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

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to get latest release version
get_latest_version() {
    local repo="twardoch/d361"
    local api_url="https://api.github.com/repos/$repo/releases/latest"
    
    if command_exists curl; then
        curl -s "$api_url" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | sed 's/^v//'
    elif command_exists wget; then
        wget -qO- "$api_url" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | sed 's/^v//'
    else
        print_error "curl or wget is required to fetch latest version"
        return 1
    fi
}

# Function to install via pip
install_via_pip() {
    local version="${1:-}"
    
    print_step "Installing d361 via pip"
    
    if [[ -n "$version" ]]; then
        python -m pip install "d361==$version"
    else
        python -m pip install d361
    fi
    
    print_success "d361 installed via pip"
}

# Function to install via uv
install_via_uv() {
    local version="${1:-}"
    
    print_step "Installing d361 via uv"
    
    if ! command_exists uv; then
        print_step "Installing uv first"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    if [[ -n "$version" ]]; then
        uv pip install "d361==$version"
    else
        uv pip install d361
    fi
    
    print_success "d361 installed via uv"
}

# Function to download binary
download_binary() {
    local os="$1"
    local version="${2:-latest}"
    local install_dir="${3:-$HOME/.local/bin}"
    
    print_step "Downloading d361 binary for $os"
    
    # Create install directory if it doesn't exist
    mkdir -p "$install_dir"
    
    # Determine binary name based on OS
    local binary_name
    case "$os" in
        "linux")
            binary_name="d361-offline-ubuntu-latest"
            ;;
        "macos")
            binary_name="d361-offline-macos-latest"
            ;;
        "windows")
            binary_name="d361-offline-windows-latest.exe"
            ;;
        *)
            print_error "Unsupported OS: $os"
            return 1
            ;;
    esac
    
    # Construct download URL
    local download_url
    if [[ "$version" == "latest" ]]; then
        download_url="https://github.com/twardoch/d361/releases/latest/download/$binary_name"
    else
        download_url="https://github.com/twardoch/d361/releases/download/v$version/$binary_name"
    fi
    
    # Download binary
    local target_file="$install_dir/d361-offline"
    if [[ "$os" == "windows" ]]; then
        target_file="$install_dir/d361-offline.exe"
    fi
    
    if command_exists curl; then
        curl -L -o "$target_file" "$download_url"
    elif command_exists wget; then
        wget -O "$target_file" "$download_url"
    else
        print_error "curl or wget is required to download binary"
        return 1
    fi
    
    # Make executable (not needed on Windows)
    if [[ "$os" != "windows" ]]; then
        chmod +x "$target_file"
    fi
    
    print_success "Binary downloaded to $target_file"
    
    # Check if install_dir is in PATH
    if [[ ":$PATH:" != *":$install_dir:"* ]]; then
        print_warning "Note: $install_dir is not in your PATH"
        print_warning "Add it to your PATH or move the binary to a directory in your PATH"
        print_warning "To add to PATH, add this line to your shell profile:"
        print_warning "export PATH=\"$install_dir:\$PATH\""
    fi
}

# Function to install playwright browsers
install_playwright_browsers() {
    print_step "Installing Playwright browsers"
    
    if command_exists playwright; then
        playwright install chromium
        print_success "Playwright browsers installed"
    else
        print_warning "Playwright not found, skipping browser installation"
        print_warning "Install d361 first, then run: playwright install chromium"
    fi
}

# Function to test installation
test_installation() {
    print_step "Testing d361 installation"
    
    # Test CLI
    if command_exists d361-offline; then
        if d361-offline --help > /dev/null 2>&1; then
            print_success "d361-offline CLI working"
        else
            print_error "d361-offline CLI not working"
            return 1
        fi
    else
        print_warning "d361-offline CLI not found in PATH"
    fi
    
    # Test Python import
    if command_exists python; then
        if python -c "import d361; print(f'd361 version: {d361.__version__}')" > /dev/null 2>&1; then
            print_success "d361 Python package working"
        else
            print_warning "d361 Python package not working or not installed"
        fi
    fi
}

# Main installation function
main() {
    local method="auto"
    local version=""
    local install_dir="$HOME/.local/bin"
    local install_browsers=false
    local test_install=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --method|-m)
                method="$2"
                shift 2
                ;;
            --version|-v)
                version="$2"
                shift 2
                ;;
            --install-dir|-d)
                install_dir="$2"
                shift 2
                ;;
            --install-browsers|-b)
                install_browsers=true
                shift
                ;;
            --no-test)
                test_install=false
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --method, -m METHOD    Installation method: auto, pip, uv, binary"
                echo "  --version, -v VERSION  Specific version to install"
                echo "  --install-dir, -d DIR  Directory for binary installation (default: ~/.local/bin)"
                echo "  --install-browsers, -b Install Playwright browsers"
                echo "  --no-test             Skip installation testing"
                echo "  --help, -h            Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    print_step "Starting d361 installation"
    
    # Detect OS
    local os
    os=$(detect_os)
    print_step "Detected OS: $os"
    
    # Get latest version if not specified
    if [[ -z "$version" ]]; then
        print_step "Getting latest version"
        version=$(get_latest_version)
        print_step "Latest version: $version"
    fi
    
    # Determine installation method
    case "$method" in
        "auto")
            if command_exists python; then
                if command_exists uv; then
                    method="uv"
                else
                    method="pip"
                fi
            else
                method="binary"
            fi
            print_step "Auto-detected installation method: $method"
            ;;
        "pip"|"uv"|"binary")
            # Method explicitly specified
            ;;
        *)
            print_error "Invalid installation method: $method"
            echo "Valid methods: auto, pip, uv, binary"
            exit 1
            ;;
    esac
    
    # Perform installation
    case "$method" in
        "pip")
            if ! command_exists python; then
                print_error "Python not found. Please install Python first."
                exit 1
            fi
            install_via_pip "$version"
            ;;
        "uv")
            if ! command_exists python; then
                print_error "Python not found. Please install Python first."
                exit 1
            fi
            install_via_uv "$version"
            ;;
        "binary")
            download_binary "$os" "$version" "$install_dir"
            ;;
    esac
    
    # Install Playwright browsers if requested
    if [[ "$install_browsers" == "true" ]]; then
        install_playwright_browsers
    fi
    
    # Test installation
    if [[ "$test_install" == "true" ]]; then
        test_installation
    fi
    
    print_success "d361 installation completed!"
    
    # Show usage information
    echo ""
    echo "Usage:"
    echo "  d361-offline --help"
    echo "  d361-offline all --map-url='https://docs.example.com/sitemap.xml'"
    echo ""
    echo "For more information, see: https://github.com/twardoch/d361"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo "Options:"
        echo "  --method, -m METHOD    Installation method: auto, pip, uv, binary"
        echo "  --version, -v VERSION  Specific version to install"
        echo "  --install-dir, -d DIR  Directory for binary installation (default: ~/.local/bin)"
        echo "  --install-browsers, -b Install Playwright browsers"
        echo "  --no-test             Skip installation testing"
        echo "  --help, -h            Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                                    # Auto-detect method and install latest"
        echo "  $0 --method pip --version 1.0.0      # Install specific version via pip"
        echo "  $0 --method binary --install-browsers # Install binary and browsers"
        echo ""
        echo "Installation methods:"
        echo "  auto   - Auto-detect best method (default)"
        echo "  pip    - Install via pip"
        echo "  uv     - Install via uv (faster)"
        echo "  binary - Download pre-built binary"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        main "$@"
        ;;
esac