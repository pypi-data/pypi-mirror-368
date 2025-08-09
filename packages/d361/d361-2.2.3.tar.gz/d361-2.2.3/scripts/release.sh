#!/usr/bin/env bash
# this_file: scripts/release.sh
# Release script for d361 project

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

# Function to validate semver format
validate_semver() {
    local version="$1"
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*)?(\+[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*)?$ ]]; then
        print_error "Invalid semver format: $version"
        print_error "Expected format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]"
        return 1
    fi
    return 0
}

# Function to get current version from git tags
get_current_version() {
    local current_tag
    current_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    echo "${current_tag#v}"
}

# Function to check if version is newer than current
is_newer_version() {
    local new_version="$1"
    local current_version="$2"
    
    # Use Python to compare versions
    python3 -c "
import sys
from packaging import version
try:
    new_v = version.Version('$new_version')
    current_v = version.Version('$current_version')
    sys.exit(0 if new_v > current_v else 1)
except:
    sys.exit(1)
" 2>/dev/null || {
        print_warning "Could not compare versions, installing packaging..."
        pip install packaging
        python3 -c "
import sys
from packaging import version
new_v = version.Version('$new_version')
current_v = version.Version('$current_version')
sys.exit(0 if new_v > current_v else 1)
"
    }
}

# Function to generate changelog entry
generate_changelog_entry() {
    local version="$1"
    local previous_tag="$2"
    
    print_step "Generating changelog entry for v$version"
    
    echo "## [$version] - $(date +%Y-%m-%d)"
    echo ""
    
    # Get commits since last tag
    if [[ "$previous_tag" != "v0.0.0" ]]; then
        git log --oneline --no-merges "$previous_tag..HEAD" | while IFS= read -r commit; do
            echo "- $commit"
        done
    else
        echo "- Initial release"
    fi
    
    echo ""
}

# Function to update version in pyproject.toml (if needed)
update_version_files() {
    local version="$1"
    
    print_step "Updating version files"
    
    # Since we're using hatch-vcs, version is managed by git tags
    # But we can update other version references if needed
    
    print_success "Version files updated"
}

# Function to run pre-release checks
run_pre_release_checks() {
    print_step "Running pre-release checks"
    
    # Check if git working directory is clean
    if ! git diff-index --quiet HEAD --; then
        print_error "Git working directory is not clean"
        echo "Please commit or stash your changes before releasing"
        return 1
    fi
    
    # Check if we're on the main branch
    local current_branch
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$current_branch" != "main" ]]; then
        print_warning "Not on main branch (current: $current_branch)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Release cancelled"
            return 1
        fi
    fi
    
    # Run tests
    print_step "Running full test suite"
    if ! ./scripts/test.sh; then
        print_error "Tests failed"
        return 1
    fi
    
    # Run build
    print_step "Running build"
    if ! ./scripts/build.sh; then
        print_error "Build failed"
        return 1
    fi
    
    print_success "Pre-release checks passed"
    return 0
}

# Function to create and push tag
create_and_push_tag() {
    local version="$1"
    local tag_name="v$version"
    
    print_step "Creating git tag $tag_name"
    
    # Create annotated tag
    git tag -a "$tag_name" -m "Release $tag_name"
    
    print_step "Pushing tag to origin"
    git push origin "$tag_name"
    
    print_success "Tag $tag_name created and pushed"
}

# Function to create GitHub release
create_github_release() {
    local version="$1"
    local tag_name="v$version"
    
    print_step "Creating GitHub release"
    
    if ! command_exists gh; then
        print_warning "GitHub CLI not found, skipping GitHub release"
        print_warning "You can create the release manually at: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/releases/new?tag=$tag_name"
        return 0
    fi
    
    # Generate release notes
    local release_notes
    release_notes=$(generate_changelog_entry "$version" "$(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo "v0.0.0")")
    
    # Create release with artifacts
    gh release create "$tag_name" dist/* \
        --title "Release $tag_name" \
        --notes "$release_notes" \
        --latest
    
    print_success "GitHub release created"
}

# Function to publish to PyPI
publish_to_pypi() {
    local dry_run="${1:-false}"
    
    if [[ "$dry_run" == "true" ]]; then
        print_step "Publishing to PyPI (dry run)"
        python -m twine upload --repository testpypi dist/* --verbose
    else
        print_step "Publishing to PyPI"
        python -m twine upload dist/* --verbose
    fi
    
    print_success "Published to PyPI"
}

# Main release function
main() {
    local version=""
    local dry_run=false
    local skip_tests=false
    local skip_github=false
    local skip_pypi=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --version|-v)
                version="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --skip-github)
                skip_github=true
                shift
                ;;
            --skip-pypi)
                skip_pypi=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --version, -v VERSION  Version to release (required)"
                echo "  --dry-run             Perform a dry run (test PyPI)"
                echo "  --skip-tests          Skip running tests"
                echo "  --skip-github         Skip GitHub release"
                echo "  --skip-pypi           Skip PyPI publishing"
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
    
    # Check if version is provided
    if [[ -z "$version" ]]; then
        print_error "Version is required"
        echo "Use --version to specify the version to release"
        exit 1
    fi
    
    # Validate version format
    validate_semver "$version" || exit 1
    
    # Check if version is newer than current
    local current_version
    current_version=$(get_current_version)
    if ! is_newer_version "$version" "$current_version"; then
        print_error "Version $version is not newer than current version $current_version"
        exit 1
    fi
    
    print_step "Starting release process for v$version"
    print_step "Current version: $current_version"
    print_step "New version: $version"
    
    # Check for required tools
    if ! command_exists uv; then
        print_error "uv is required but not installed. Please install uv first."
        exit 1
    fi
    
    if ! command_exists git; then
        print_error "git is required but not installed."
        exit 1
    fi
    
    # Install twine if not present
    if ! command_exists twine; then
        print_warning "twine not found, installing..."
        uv pip install twine
    fi
    
    # Run pre-release checks unless skipped
    if [[ "$skip_tests" != "true" ]]; then
        run_pre_release_checks || exit 1
    fi
    
    # Update version files
    update_version_files "$version"
    
    # Create and push tag
    create_and_push_tag "$version"
    
    # Create GitHub release unless skipped
    if [[ "$skip_github" != "true" ]]; then
        create_github_release "$version"
    fi
    
    # Publish to PyPI unless skipped
    if [[ "$skip_pypi" != "true" ]]; then
        publish_to_pypi "$dry_run"
    fi
    
    print_success "Release v$version completed successfully!"
    
    if [[ "$dry_run" == "true" ]]; then
        print_warning "This was a dry run. The package was published to test PyPI."
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Check the GitHub release: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/releases/tag/v$version"
    if [[ "$skip_pypi" != "true" ]]; then
        echo "2. Check PyPI: https://pypi.org/project/d361/$version/"
    fi
    echo "3. Update documentation if needed"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo "Options:"
        echo "  --version, -v VERSION  Version to release (required)"
        echo "  --dry-run             Perform a dry run (test PyPI)"
        echo "  --skip-tests          Skip running tests"
        echo "  --skip-github         Skip GitHub release"
        echo "  --skip-pypi           Skip PyPI publishing"
        echo "  --help, -h            Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 --version 1.0.0"
        echo "  $0 --version 1.0.0 --dry-run"
        echo "  $0 --version 1.0.0 --skip-tests"
        exit 0
        ;;
    "")
        print_error "Version is required"
        echo "Use --version to specify the version to release"
        echo "Use --help for usage information"
        exit 1
        ;;
    *)
        main "$@"
        ;;
esac