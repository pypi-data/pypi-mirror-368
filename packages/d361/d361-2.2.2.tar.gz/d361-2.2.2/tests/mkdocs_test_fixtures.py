# this_file: external/int_folders/d361/tests/mkdocs_test_fixtures.py
"""
Test fixtures specifically for MkDocs export testing.

This module provides specialized fixtures and utilities for testing
MkDocs export functionality, including mock data, sample configurations,
and validation helpers.
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
import tempfile
import json
import yaml
from unittest.mock import Mock, AsyncMock

from d361.core.models import Article, Category, ProjectVersion
from d361.mkdocs.exporters.mkdocs_exporter import MkDocsExporter
from d361.mkdocs.exporters.config_generator import ConfigGenerator
from d361.providers.mock_provider import MockProvider


@pytest.fixture
def sample_mkdocs_articles() -> List[Article]:
    """Create sample articles optimized for MkDocs testing."""
    return [
        Article(
            id="getting-started",
            title="Getting Started Guide",
            slug="getting-started",
            content="""# Getting Started

Welcome to our documentation! This guide will help you get up and running quickly.

## Prerequisites

Before you begin, make sure you have:

- Python 3.8 or higher
- Git installed
- A text editor

## Installation

```bash
pip install our-package
```

## Quick Start

1. Create a new project
2. Configure your settings
3. Run the application

For more details, see the [Advanced Configuration](advanced-config.md) guide.

![Setup Diagram](images/setup-diagram.png)
""",
            category_id="guides",
            status="published",
            author="Documentation Team",
            order=1
        ),
        
        Article(
            id="advanced-config",
            title="Advanced Configuration",
            slug="advanced-config", 
            content="""# Advanced Configuration

This section covers advanced configuration options and best practices.

## Configuration File Structure

The configuration file uses YAML format:

```yaml
app:
  name: "My Application"
  debug: false
  database:
    url: "postgresql://localhost/mydb"
    pool_size: 10
```

## Environment Variables

You can override configuration using environment variables:

- `APP_DEBUG=true` - Enable debug mode
- `DATABASE_URL` - Database connection string

!!! warning "Security Note"
    Never commit sensitive configuration to version control.

## Advanced Topics

### Custom Plugins

You can extend functionality with custom plugins:

```python
from myapp import Plugin

class MyCustomPlugin(Plugin):
    def process(self, data):
        return modified_data
```

### Performance Tuning

For production deployments, consider:

1. **Database Connection Pooling**
2. **Caching Configuration** 
3. **Load Balancer Settings**

See also: [Deployment Guide](deployment.md) and [Monitoring](monitoring.md).
""",
            category_id="guides", 
            status="published",
            author="Engineering Team",
            order=2
        ),
        
        Article(
            id="api-reference",
            title="API Reference",
            slug="api-reference",
            content="""# API Reference

Complete reference for our REST API.

## Authentication

All API requests require authentication using API keys:

```http
GET /api/v1/users
Authorization: Bearer your-api-key-here
```

## Endpoints

### Users API

#### GET /api/v1/users

List all users.

**Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe", 
      "email": "john@example.com"
    }
  ],
  "pagination": {
    "page": 1,
    "total_pages": 5,
    "total_items": 100
  }
}
```

#### POST /api/v1/users

Create a new user.

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password"
}
```

### Error Handling

API errors return structured error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  }
}
```

## Rate Limiting

API requests are rate limited:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated requests
""",
            category_id="reference",
            status="published", 
            author="API Team",
            order=1
        ),
        
        Article(
            id="troubleshooting",
            title="Troubleshooting Common Issues",
            slug="troubleshooting",
            content="""# Troubleshooting

Solutions to common problems and error messages.

## Installation Issues

### Python Version Compatibility

**Problem:** `ImportError: No module named '_ctypes'`

**Solution:** 
Ensure you have Python 3.8+ installed and all required system dependencies.

```bash
# On Ubuntu/Debian
sudo apt-get install build-essential libffi-dev

# On macOS
xcode-select --install
```

### Package Conflicts

**Problem:** Conflicting package versions

**Solution:** Use a virtual environment:

```bash
python -m venv myproject
source myproject/bin/activate  # On Windows: myproject\\Scripts\\activate
pip install -r requirements.txt
```

## Runtime Issues

### Database Connection Errors

**Problem:** `connection refused` errors

**Solutions:**
1. Check database is running
2. Verify connection string
3. Check firewall settings
4. Ensure proper authentication

### Performance Issues

**Problem:** Slow response times

**Investigation steps:**

1. **Check System Resources**
   ```bash
   htop
   df -h
   ```

2. **Monitor Database Performance**
   ```sql
   SHOW PROCESSLIST;
   EXPLAIN ANALYZE SELECT ...;
   ```

3. **Review Application Logs**
   ```bash
   tail -f /var/log/myapp.log
   ```

## Configuration Problems

### SSL Certificate Issues

**Problem:** SSL verification failures

**Quick fix (development only):**
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**Proper solution:** Update certificates or configure proper SSL context.

### Environment Variable Issues  

**Problem:** Configuration not loading

**Checklist:**
- [ ] Environment variables are properly set
- [ ] Variable names match exactly (case-sensitive)
- [ ] No extra whitespace in values
- [ ] Proper quoting for complex values

!!! tip "Debugging Tip"
    Enable debug logging to see configuration loading:
    
    ```python
    import logging
    logging.basicConfig(level=logging.DEBUG)
    ```

## Getting Help

If you're still having issues:

1. Check the [FAQ](faq.md)
2. Search [existing issues](https://github.com/example/project/issues)
3. Join our [Discord community](https://discord.gg/example)
4. Contact [support](mailto:support@example.com)
""",
            category_id="help",
            status="published",
            author="Support Team",
            order=1
        ),
        
        Article(
            id="changelog",
            title="Changelog",
            slug="changelog", 
            content="""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-01-08

### Added
- New API endpoints for user management
- Support for PostgreSQL 15
- Advanced caching configuration options
- Prometheus metrics integration
- Docker Compose development environment

### Changed
- Updated Python requirement to 3.8+
- Improved error handling and logging
- Enhanced documentation with more examples
- Optimized database query performance

### Fixed
- Fixed memory leak in background tasks
- Resolved SSL certificate validation issues
- Fixed timezone handling in API responses
- Corrected pagination in list endpoints

### Security
- Updated all dependencies to latest versions
- Added input validation for API endpoints
- Implemented rate limiting for authentication endpoints

## [2.0.0] - 2024-12-01

### Added
- **BREAKING**: New authentication system
- Multi-tenant support
- Real-time WebSocket API
- Advanced search functionality
- Role-based access control (RBAC)

### Changed
- **BREAKING**: Database schema changes (migration required)
- **BREAKING**: API response format updated
- Moved to microservices architecture
- Updated UI framework to React 18

### Removed
- **BREAKING**: Deprecated v1 API endpoints
- Legacy authentication methods
- Old configuration format

### Migration Guide

To upgrade from v1.x to v2.0:

1. **Update configuration format**
   ```yaml
   # Old format (v1.x)
   database_url: "postgresql://..."
   
   # New format (v2.0)
   database:
     url: "postgresql://..."
     pool_size: 10
   ```

2. **Run database migrations**
   ```bash
   python manage.py migrate --from-version=1.5.0
   ```

3. **Update API calls**
   ```python
   # Old API (v1.x)
   response = client.get('/api/users')
   users = response.json()
   
   # New API (v2.0)
   response = client.get('/api/v2/users')
   data = response.json()
   users = data['users']
   ```

## [1.5.2] - 2024-11-15

### Fixed
- Critical security vulnerability in authentication
- Performance regression in list queries
- Memory usage optimization

### Security
- **IMPORTANT**: Upgrade immediately for security fix
- Updated JWT library to address CVE-2024-XXXX

## [1.5.1] - 2024-11-01

### Added
- Support for custom themes
- Improved error messages
- Additional logging options

### Fixed
- Fixed installation on Windows
- Resolved compatibility issues with Python 3.11
- Fixed configuration file parsing

## [1.5.0] - 2024-10-15

### Added
- Plugin system for extensibility
- Advanced configuration options
- Support for multiple databases
- Comprehensive test suite

### Changed
- Improved performance by 30%
- Better error handling
- Enhanced documentation

### Deprecated
- Old configuration format (will be removed in v2.0)
- Legacy API endpoints (will be removed in v2.0)

---

For older versions, see [CHANGELOG-ARCHIVE.md](changelog-archive.md).
""",
            category_id="meta",
            status="published",
            author="Release Team", 
            order=1
        )
    ]


@pytest.fixture  
def sample_mkdocs_categories() -> List[Category]:
    """Create sample categories optimized for MkDocs testing."""
    return [
        Category(
            id="guides",
            name="User Guides", 
            slug="guides",
            description="Step-by-step guides to help you get started and accomplish common tasks.",
            parent_id=None,
            order=1
        ),
        
        Category(
            id="reference",
            name="API Reference",
            slug="reference", 
            description="Complete technical reference for APIs, configuration options, and advanced features.",
            parent_id=None,
            order=2
        ),
        
        Category(
            id="help",
            name="Help & Support",
            slug="help",
            description="Troubleshooting guides, FAQ, and support resources.",
            parent_id=None, 
            order=3
        ),
        
        Category(
            id="meta", 
            name="Project Information",
            slug="meta",
            description="Changelog, release notes, and project information.",
            parent_id=None,
            order=4
        ),
        
        Category(
            id="advanced-guides",
            name="Advanced Topics",
            slug="advanced",
            description="Advanced configuration and customization guides.", 
            parent_id="guides",  # Subcategory of guides
            order=1
        )
    ]


@pytest.fixture
def sample_mkdocs_config_context() -> Dict[str, Any]:
    """Create sample context for MkDocs config generation."""
    return {
        "site_name": "Test Documentation Site",
        "site_url": "https://docs.example.com",
        "site_description": "Comprehensive documentation for our project",
        "site_author": "Documentation Team", 
        "repo_url": "https://github.com/example/project",
        "repo_name": "example/project",
        "edit_uri": "edit/main/docs/",
        "copyright": "Copyright &copy; 2025 Example Company",
        
        # Theme configuration
        "theme_name": "material",
        "primary_color": "indigo",
        "accent_color": "blue", 
        "color_scheme": "auto",  # auto, light, dark
        "text_font": "Roboto",
        "code_font": "Roboto Mono",
        "logo": "assets/logo.png",
        "favicon": "assets/favicon.ico",
        
        # Features
        "enable_plugins": True,
        "enable_autorefs": True,
        "enable_section_index": True,
        "enable_social_cards": True,
        "enable_tags": True, 
        "enable_redirects": True,
        "enable_minify": True,
        "enable_feedback": True,
        "enable_tabs": True,
        
        # Search
        "search_lang": ["en"],
        
        # Navigation
        "navigation": [
            {"Home": "index.md"},
            {
                "User Guides": [
                    "guides/getting-started.md",
                    "guides/advanced-config.md"
                ]
            },
            {
                "API Reference": [
                    "reference/api-reference.md" 
                ]
            },
            {
                "Help & Support": [
                    "help/troubleshooting.md"
                ]
            },
            {"Changelog": "meta/changelog.md"}
        ],
        
        # Redirects
        "redirects": {
            "old-page.html": "new-page.md",
            "legacy/guide.html": "guides/getting-started.md"
        },
        
        # Social links
        "social": [
            {
                "icon": "fontawesome/brands/github", 
                "link": "https://github.com/example/project",
                "name": "GitHub"
            },
            {
                "icon": "fontawesome/brands/discord",
                "link": "https://discord.gg/example", 
                "name": "Discord"
            },
            {
                "icon": "fontawesome/brands/twitter",
                "link": "https://twitter.com/example",
                "name": "Twitter"
            }
        ],
        
        # Analytics
        "analytics": {
            "provider": "google",
            "property": "G-XXXXXXXXXX",
            "feedback": {
                "title": "Was this page helpful?",
                "ratings": [
                    {
                        "icon": "material/emoticon-happy-outline",
                        "name": "This page was helpful", 
                        "data": 1,
                        "note": "Thanks for your feedback!"
                    },
                    {
                        "icon": "material/emoticon-sad-outline",
                        "name": "This page could be improved",
                        "data": 0,
                        "note": "Thanks for your feedback! Help us improve this page."
                    }
                ]
            }
        },
        
        # Extra configuration
        "extra_css": [
            "stylesheets/extra.css"
        ],
        "extra_javascript": [
            "javascripts/extra.js"
        ],
        
        # Development
        "dev_addr": "127.0.0.1:8000",
        "use_directory_urls": True,
        "strict_mode": False,
        
        # Export metadata
        "export_date": "2025-01-08T00:00:00Z",
        "export_version": "1.0.0"
    }


@pytest.fixture
def mock_mkdocs_provider(
    sample_mkdocs_articles: List[Article],
    sample_mkdocs_categories: List[Category]
) -> MockProvider:
    """Create mock provider with MkDocs-optimized test data."""
    provider = MockProvider(
        num_articles=0,  # Use custom articles
        num_categories=0,  # Use custom categories
        include_content=True
    )
    
    # Override with our custom test data
    provider._articles = sample_mkdocs_articles
    provider._categories = sample_mkdocs_categories
    
    return provider


@pytest.fixture
def mkdocs_config_templates_context() -> Dict[str, Dict[str, Any]]:
    """Context for testing all MkDocs config templates."""
    base_context = {
        "site_name": "Template Test Site",
        "site_url": "https://test.example.com",
        "docs_dir": "docs",
        "site_dir": "site"
    }
    
    return {
        "mkdocs_base.yml.j2": {
            **base_context,
            "theme_name": "mkdocs",
            "navigation": [{"Home": "index.md"}],
            "enable_task_lists": True,
            "enable_superfences": True
        },
        
        "material_theme.yml.j2": {
            **base_context,
            "primary_color": "teal",
            "accent_color": "orange",
            "color_scheme": "auto",
            "enable_social_cards": True,
            "enable_tags": True,
            "github_user": "testuser",
            "github_repo": "testrepo",
            "navigation": [
                {"Home": "index.md"},
                {"Guide": ["guide/intro.md", "guide/advanced.md"]}
            ]
        },
        
        "plugin_configs.yml.j2": {
            **base_context,
            "enable_autorefs": True,
            "enable_section_index": True,
            "enable_redirects": True,
            "redirects": {
                "old.html": "new.md"
            }
        }
    }


@pytest.fixture
def expected_mkdocs_config_structure() -> Dict[str, Any]:
    """Expected structure for generated MkDocs configurations."""
    return {
        "required_fields": [
            "site_name",
            "theme",
            "nav"
        ],
        
        "theme_fields": {
            "material": [
                "name",
                "features", 
                "palette",
                "font"
            ],
            "readthedocs": [
                "name",
                "highlightjs"
            ],
            "mkdocs": [
                "name"
            ]
        },
        
        "common_plugins": [
            "search",
            "autorefs",
            "section-index",
            "redirects",
            "minify"
        ],
        
        "material_plugins": [
            "social",
            "offline"
        ],
        
        "markdown_extensions": [
            "toc",
            "admonition", 
            "pymdownx.superfences",
            "pymdownx.tabbed",
            "pymdownx.highlight"
        ]
    }


@pytest.fixture
async def mkdocs_test_exporter(
    test_data_dir: Path,
    mock_mkdocs_provider: MockProvider
) -> MkDocsExporter:
    """Create MkDocsExporter configured for testing."""
    
    # Create mock archive file
    archive_path = test_data_dir / "test_mkdocs_archive.zip"
    
    # Create minimal archive content for testing
    import zipfile
    import json
    
    with zipfile.ZipFile(archive_path, 'w') as zf:
        zf.writestr("articles.json", json.dumps([
            {
                "id": "test-1",
                "title": "Test Article",
                "content": "Test content",
                "category_id": "test-cat"
            }
        ]))
        zf.writestr("categories.json", json.dumps([
            {
                "id": "test-cat", 
                "name": "Test Category",
                "slug": "test-category"
            }
        ]))
    
    # Create output directory
    output_dir = test_data_dir / "mkdocs_test_output"
    output_dir.mkdir(exist_ok=True)
    
    exporter = MkDocsExporter(
        source="archive",
        archive_path=archive_path,
        output_path=output_dir,
        theme="material",
        enable_plugins=True,
        parallel_processing=False,  # Disable for predictable testing
        max_workers=1
    )
    
    return exporter


class MkDocsTestHelpers:
    """Helper utilities for MkDocs testing."""
    
    @staticmethod
    def validate_mkdocs_config(config_yaml: str) -> Dict[str, Any]:
        """Validate MkDocs configuration YAML."""
        try:
            config = yaml.safe_load(config_yaml)
            
            results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "config": config
            }
            
            # Check required fields
            required_fields = ["site_name"]
            for field in required_fields:
                if field not in config:
                    results["valid"] = False
                    results["errors"].append(f"Missing required field: {field}")
            
            # Validate theme
            if "theme" in config:
                theme = config["theme"]
                if isinstance(theme, dict):
                    if "name" not in theme:
                        results["warnings"].append("Theme should specify 'name'")
                elif not isinstance(theme, str):
                    results["warnings"].append("Theme should be string or dict")
            
            # Check for navigation
            if "nav" not in config:
                results["warnings"].append("No navigation specified")
            
            return results
            
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "errors": [f"YAML syntax error: {e}"],
                "warnings": [],
                "config": None
            }
    
    @staticmethod
    def create_test_mkdocs_structure(base_dir: Path) -> Path:
        """Create a test MkDocs directory structure."""
        base_dir.mkdir(exist_ok=True)
        
        # Create docs directory
        docs_dir = base_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Create sample files
        (docs_dir / "index.md").write_text("# Welcome\n\nThis is the homepage.")
        
        guides_dir = docs_dir / "guides"
        guides_dir.mkdir(exist_ok=True)
        (guides_dir / "getting-started.md").write_text("# Getting Started\n\nQuick start guide.")
        
        # Create assets directory
        assets_dir = docs_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        (assets_dir / "style.css").write_text("/* Custom styles */")
        
        # Create mkdocs.yml
        config_content = """
site_name: Test Documentation
theme:
  name: material
nav:
  - Home: index.md
  - Guides:
    - Getting Started: guides/getting-started.md
"""
        (base_dir / "mkdocs.yml").write_text(config_content.strip())
        
        return base_dir
    
    @staticmethod
    def count_markdown_files(docs_dir: Path) -> int:
        """Count markdown files in docs directory."""
        return len(list(docs_dir.rglob("*.md")))
    
    @staticmethod
    def extract_navigation_items(config: Dict[str, Any]) -> List[str]:
        """Extract navigation item names from config."""
        nav_items = []
        nav = config.get("nav", [])
        
        def extract_items(items):
            for item in items:
                if isinstance(item, str):
                    nav_items.append(item)
                elif isinstance(item, dict):
                    for key, value in item.items():
                        nav_items.append(key)
                        if isinstance(value, list):
                            extract_items(value)
        
        extract_items(nav)
        return nav_items


@pytest.fixture
def mkdocs_test_helpers() -> MkDocsTestHelpers:
    """Provide MkDocs test helper utilities."""
    return MkDocsTestHelpers()