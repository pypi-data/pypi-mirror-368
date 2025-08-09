# Development Guide

This document provides detailed instructions for developing, testing, and releasing the d361 project.

## Table of Contents

- [Development Setup](#development-setup)
- [Build System](#build-system)
- [Testing](#testing)
- [Release Process](#release-process)
- [CI/CD Pipeline](#cicd-pipeline)
- [Binary Distribution](#binary-distribution)
- [Contributing](#contributing)

## Development Setup

### Prerequisites

- Python 3.10+ (3.12 recommended)
- [uv](https://github.com/astral-sh/uv) (fast Python package installer)
- [hatch](https://hatch.pypa.io/) (project management)
- Git

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/twardoch/d361.git
cd d361

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install hatch
uv pip install hatch

# Activate development environment
hatch shell

# Install Playwright browsers
playwright install chromium

# Run tests to verify setup
hatch run test:test
```

## Build System

### Local Build Scripts

The project includes convenient build scripts in the `scripts/` directory:

#### Build Script (`scripts/build.sh`)

```bash
# Full build with all checks
./scripts/build.sh

# Quick build (skip tests and quality checks)
./scripts/build.sh --quick

# Clean build artifacts
./scripts/build.sh --clean

# Show help
./scripts/build.sh --help
```

#### Test Script (`scripts/test.sh`)

```bash
# Run all tests
./scripts/test.sh

# Quick test (unit tests only)
./scripts/test.sh --quick

# Run with integration tests
./scripts/test.sh --integration

# Install Playwright browsers
./scripts/test.sh --install-browsers

# Fix linting issues
./scripts/test.sh --fix
```

#### Release Script (`scripts/release.sh`)

```bash
# Create a new release
./scripts/release.sh --version 1.0.0

# Dry run (publish to test PyPI)
./scripts/release.sh --version 1.0.0 --dry-run

# Skip certain steps
./scripts/release.sh --version 1.0.0 --skip-tests --skip-github
```

### Hatch Commands

The project uses Hatch for environment management:

```bash
# Run tests with coverage
hatch run test:test-cov

# Run linting and formatting
hatch run lint:fix

# Run type checking
hatch run lint:typing

# Run all quality checks
hatch run lint:all

# Build package
hatch run build
```

## Testing

### Test Structure

```
tests/
├── test_package.py           # Basic package tests
├── offline/
│   ├── test_offline_core.py  # Core offline functionality
│   ├── test_parser.py        # Sitemap parsing tests
│   ├── test_content.py       # Content extraction tests
│   ├── test_navigation.py    # Navigation extraction tests
│   └── test_integration.py   # Integration tests
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows

### Running Tests

```bash
# Run all tests
hatch run test:test

# Run with coverage
hatch run test:test-cov

# Run specific test file
hatch run test:test tests/offline/test_parser.py

# Run tests matching pattern
hatch run test:test -k "test_navigation"

# Run tests with verbose output
hatch run test:test -v
```

### Test Configuration

Tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "slow: slow tests"
]
```

## Release Process

### Semantic Versioning

The project uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Management

Versions are managed through Git tags using `hatch-vcs`:

- Version is automatically derived from Git tags
- Use `v` prefix for tags (e.g., `v1.0.0`)
- Pre-release versions supported (e.g., `v1.0.0-alpha.1`)

### Release Steps

1. **Prepare Release**
   ```bash
   # Ensure you're on main branch
   git checkout main
   git pull origin main
   
   # Run full test suite
   ./scripts/test.sh
   
   # Run build
   ./scripts/build.sh
   ```

2. **Create Release**
   ```bash
   # Create and push tag (triggers CI/CD)
   ./scripts/release.sh --version 1.0.0
   ```

3. **Verify Release**
   - Check GitHub Actions workflow
   - Verify PyPI package
   - Test binary downloads
   - Verify GitHub release

### Pre-release Testing

```bash
# Test with dry run
./scripts/release.sh --version 1.0.0-beta.1 --dry-run

# Test specific PyPI installation
pip install --index-url https://test.pypi.org/simple/ d361==1.0.0-beta.1
```

## CI/CD Pipeline

### GitHub Actions Workflows

#### Push Workflow (`.github/workflows/push.yml`)

Runs on every push to `main` and pull requests:

- **Code Quality**: Linting, formatting
- **Type Checking**: MyPy static analysis
- **Multi-platform Testing**: Ubuntu, Windows, macOS
- **Multi-version Testing**: Python 3.10, 3.11, 3.12
- **Build Verification**: Package building
- **Installation Testing**: Verify package installation

#### Release Workflow (`.github/workflows/release.yml`)

Runs on Git tag pushes (`v*`):

- **Full Testing**: All platforms and Python versions
- **Package Building**: Source and wheel distributions
- **Binary Building**: PyInstaller executables for all platforms
- **PyPI Publishing**: Automatic package publishing
- **GitHub Release**: Automated release with binaries
- **Post-release Testing**: Verify installation from PyPI

### Workflow Features

- **Concurrency Control**: Cancels outdated runs
- **Artifact Management**: Preserves build artifacts
- **Matrix Testing**: Comprehensive platform/version coverage
- **Caching**: Speeds up builds with UV caching
- **Security**: Uses trusted actions and proper permissions

## Binary Distribution

### PyInstaller Configuration

The project creates standalone executables using PyInstaller:

```bash
# Manual binary creation
pyinstaller --onefile --name d361-offline-linux \
    --add-data "src/d361/offline/d361_offline.css:d361/offline" \
    src/d361/offline/__main__.py
```

### Binary Artifacts

Each release includes:

- **Linux**: `d361-offline-ubuntu-latest`
- **Windows**: `d361-offline-windows-latest.exe`
- **macOS**: `d361-offline-macos-latest`

### Usage

```bash
# Download binary
curl -L -o d361-offline https://github.com/twardoch/d361/releases/latest/download/d361-offline-ubuntu-latest

# Make executable
chmod +x d361-offline

# Run
./d361-offline --help
```

## Contributing

### Code Quality

- **Linting**: Use Ruff for fast linting
- **Formatting**: Use Ruff for consistent formatting
- **Type Checking**: Use MyPy for static type analysis
- **Testing**: Maintain high test coverage

### Development Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/d361.git
   cd d361
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Develop and Test**
   ```bash
   # Make changes
   # Run tests
   ./scripts/test.sh
   
   # Run build
   ./scripts/build.sh
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Submit PR against `main` branch
   - Include clear description
   - Ensure all CI checks pass

### Code Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public APIs
- Include tests for new functionality
- Update documentation as needed

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add test coverage
refactor: improve code structure
```

## Troubleshooting

### Common Issues

1. **Playwright Browser Issues**
   ```bash
   # Reinstall browsers
   playwright install chromium
   ```

2. **Build Failures**
   ```bash
   # Clean and rebuild
   ./scripts/build.sh --clean
   ./scripts/build.sh
   ```

3. **Test Failures**
   ```bash
   # Run specific test
   hatch run test:test tests/offline/test_parser.py -v
   ```

4. **Version Issues**
   ```bash
   # Check current version
   git describe --tags --abbrev=0
   
   # Verify hatch-vcs
   hatch version
   ```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/twardoch/d361/issues)
- **Discussions**: [GitHub Discussions](https://github.com/twardoch/d361/discussions)
- **Documentation**: [README.md](README.md)

## Resources

- [Hatch Documentation](https://hatch.pypa.io/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Semantic Versioning](https://semver.org/)