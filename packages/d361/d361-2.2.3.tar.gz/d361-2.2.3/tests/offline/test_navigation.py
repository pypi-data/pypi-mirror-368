# this_file: tests/offline/test_navigation.py
"""Test suite for d361.offline.navigation module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from d361.offline.navigation import extract_navigation, extract_tree_structure
from d361.offline.config import Config


@pytest.fixture
def mock_config(tmp_path: Path) -> Config:
    """Create a mock config for testing."""
    return Config(
        map_url="https://example.com/sitemap.xml",
        output_dir=tmp_path / "test_output"
    )


@pytest.fixture
def mock_page() -> MagicMock:
    """Create a mock Playwright page."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.query_selector = MagicMock()
    page.query_selector_all = MagicMock(return_value=[])
    page.evaluate = AsyncMock()
    page.close = AsyncMock()
    return page


@pytest.fixture
def sample_navigation_data() -> list[dict]:
    """Sample navigation data for testing."""
    return [
        {
            "title": "Getting Started",
            "url": "https://example.com/getting-started",
            "children": [
                {
                    "title": "Installation",
                    "url": "https://example.com/installation",
                    "children": []
                },
                {
                    "title": "Configuration",
                    "url": "https://example.com/configuration",
                    "children": []
                }
            ]
        },
        {
            "title": "API Reference",
            "url": "https://example.com/api-reference",
            "children": []
        }
    ]


@pytest.mark.asyncio
async def test_extract_navigation_success(
    mock_config: Config, 
    mock_page: MagicMock, 
    sample_navigation_data: list[dict]
) -> None:
    """Test successful navigation extraction."""
    url = "https://example.com/nav-page"
    
    # Mock the tree container
    tree_container = MagicMock()
    mock_page.query_selector.return_value = tree_container
    
    with patch('d361.offline.navigation.expand_navigation_tree') as mock_expand, \
         patch('d361.offline.navigation.extract_tree_structure') as mock_extract:
        
        mock_expand.return_value = None
        mock_extract.return_value = sample_navigation_data
        
        result = await extract_navigation(mock_page, url, mock_config)
        
        assert result == sample_navigation_data
        mock_page.goto.assert_called_once_with(url)
        mock_expand.assert_called_once()
        mock_extract.assert_called_once()


@pytest.mark.asyncio
async def test_extract_navigation_no_tree_found(
    mock_config: Config, 
    mock_page: MagicMock
) -> None:
    """Test navigation extraction when no tree container is found."""
    url = "https://example.com/no-nav-page"
    
    # Mock no tree container found
    mock_page.query_selector.return_value = None
    
    result = await extract_navigation(mock_page, url, mock_config)
    
    assert result == []


@pytest.mark.asyncio
async def test_extract_navigation_with_cookie_dismissal(
    mock_config: Config, 
    mock_page: MagicMock
) -> None:
    """Test navigation extraction with cookie banner dismissal."""
    url = "https://example.com/cookie-nav-page"
    
    # Mock cookie banner elements
    cookie_button = MagicMock()
    cookie_button.click = AsyncMock()
    mock_page.query_selector_all.return_value = [cookie_button]
    
    # Mock tree container
    tree_container = MagicMock()
    mock_page.query_selector.return_value = tree_container
    
    with patch('d361.offline.navigation.expand_navigation_tree') as mock_expand, \
         patch('d361.offline.navigation.extract_tree_structure') as mock_extract:
        
        mock_expand.return_value = None
        mock_extract.return_value = []
        
        result = await extract_navigation(mock_page, url, mock_config)
        
        # Should dismiss cookies
        cookie_button.click.assert_called_once()
        assert result == []


def test_extract_tree_structure_simple() -> None:
    """Test tree structure extraction with simple navigation."""
    # Mock DOM elements
    root_element = MagicMock()
    
    # Mock child elements
    child1 = MagicMock()
    child1.query_selector.return_value = MagicMock()
    child1.query_selector.return_value.text_content = "Item 1"
    child1.query_selector.return_value.get_attribute.return_value = "https://example.com/item1"
    child1.query_selector_all.return_value = []  # No children
    
    child2 = MagicMock()
    child2.query_selector.return_value = MagicMock()
    child2.query_selector.return_value.text_content = "Item 2"
    child2.query_selector.return_value.get_attribute.return_value = "https://example.com/item2"
    child2.query_selector_all.return_value = []  # No children
    
    root_element.query_selector_all.return_value = [child1, child2]
    
    result = extract_tree_structure(root_element)
    
    assert len(result) == 2
    assert result[0]["title"] == "Item 1"
    assert result[0]["url"] == "https://example.com/item1"
    assert result[0]["children"] == []
    assert result[1]["title"] == "Item 2"
    assert result[1]["url"] == "https://example.com/item2"
    assert result[1]["children"] == []


def test_extract_tree_structure_nested() -> None:
    """Test tree structure extraction with nested navigation."""
    # Mock DOM elements
    root_element = MagicMock()
    
    # Mock parent element
    parent = MagicMock()
    parent_link = MagicMock()
    parent_link.text_content = "Parent Item"
    parent_link.get_attribute.return_value = "https://example.com/parent"
    parent.query_selector.return_value = parent_link
    
    # Mock child element
    child = MagicMock()
    child_link = MagicMock()
    child_link.text_content = "Child Item"
    child_link.get_attribute.return_value = "https://example.com/child"
    child.query_selector.return_value = child_link
    child.query_selector_all.return_value = []  # No grandchildren
    
    parent.query_selector_all.return_value = [child]
    root_element.query_selector_all.return_value = [parent]
    
    result = extract_tree_structure(root_element)
    
    assert len(result) == 1
    assert result[0]["title"] == "Parent Item"
    assert result[0]["url"] == "https://example.com/parent"
    assert len(result[0]["children"]) == 1
    assert result[0]["children"][0]["title"] == "Child Item"
    assert result[0]["children"][0]["url"] == "https://example.com/child"


def test_extract_tree_structure_empty() -> None:
    """Test tree structure extraction with empty navigation."""
    root_element = MagicMock()
    root_element.query_selector_all.return_value = []
    
    result = extract_tree_structure(root_element)
    
    assert result == []


def test_extract_tree_structure_malformed() -> None:
    """Test tree structure extraction with malformed elements."""
    root_element = MagicMock()
    
    # Mock element with no link
    malformed_element = MagicMock()
    malformed_element.query_selector.return_value = None
    
    root_element.query_selector_all.return_value = [malformed_element]
    
    result = extract_tree_structure(root_element)
    
    # Should handle malformed elements gracefully
    assert result == []