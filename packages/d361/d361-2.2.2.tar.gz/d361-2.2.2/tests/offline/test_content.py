# this_file: tests/offline/test_content.py
"""Test suite for d361.offline.content module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from d361.offline.content import extract_page_content
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
def sample_page_content() -> dict[str, str]:
    """Sample page content for testing."""
    return {
        "title": "Test Page Title",
        "html": "<h1>Test Page Title</h1><p>This is test content.</p>",
        "markdown": "# Test Page Title\n\nThis is test content.\n"
    }


@pytest.mark.asyncio
async def test_extract_page_content_success(
    mock_config: Config, 
    mock_page: MagicMock, 
    sample_page_content: dict[str, str]
) -> None:
    """Test successful page content extraction."""
    url = "https://example.com/test-page"
    
    # Mock the title element
    title_element = MagicMock()
    title_element.text_content = AsyncMock(return_value=sample_page_content["title"])
    mock_page.query_selector.return_value = title_element
    
    # Mock the content element
    content_element = MagicMock()
    content_element.inner_html = AsyncMock(return_value=sample_page_content["html"])
    mock_page.query_selector.side_effect = [title_element, content_element]
    
    with patch('d361.offline.content.markdownify') as mock_markdownify:
        mock_markdownify.return_value = sample_page_content["markdown"]
        
        result = await extract_page_content(mock_page, url, mock_config)
        
        assert result["title"] == sample_page_content["title"]
        assert result["html"] == sample_page_content["html"]
        assert result["markdown"] == sample_page_content["markdown"]
        
        mock_page.goto.assert_called_once_with(url)
        mock_page.wait_for_load_state.assert_called()


@pytest.mark.asyncio
async def test_extract_page_content_no_title(
    mock_config: Config, 
    mock_page: MagicMock
) -> None:
    """Test page content extraction when no title is found."""
    url = "https://example.com/no-title-page"
    
    # Mock no title element found
    mock_page.query_selector.side_effect = [None, None]
    
    result = await extract_page_content(mock_page, url, mock_config)
    
    assert result["title"] == ""
    assert result["html"] == ""
    assert result["markdown"] == ""


@pytest.mark.asyncio
async def test_extract_page_content_no_content(
    mock_config: Config, 
    mock_page: MagicMock
) -> None:
    """Test page content extraction when no content is found."""
    url = "https://example.com/no-content-page"
    
    # Mock title but no content
    title_element = MagicMock()
    title_element.text_content = AsyncMock(return_value="Title Only")
    mock_page.query_selector.side_effect = [title_element, None]
    
    result = await extract_page_content(mock_page, url, mock_config)
    
    assert result["title"] == "Title Only"
    assert result["html"] == ""
    assert result["markdown"] == ""


@pytest.mark.asyncio
async def test_extract_page_content_with_retries(
    mock_config: Config, 
    mock_page: MagicMock
) -> None:
    """Test that retries work when extraction fails initially."""
    url = "https://example.com/retry-page"
    
    # Mock initial failure then success
    title_element = MagicMock()
    title_element.text_content = AsyncMock(return_value="Retry Test")
    content_element = MagicMock()
    content_element.inner_html = AsyncMock(return_value="<p>Content after retry</p>")
    
    # First call fails, second succeeds
    mock_page.query_selector.side_effect = [
        Exception("First attempt fails"),
        title_element,
        content_element
    ]
    
    with patch('d361.offline.content.markdownify') as mock_markdownify:
        mock_markdownify.return_value = "Content after retry"
        
        # The tenacity decorator should retry
        result = await extract_page_content(mock_page, url, mock_config)
        
        # Should eventually succeed
        assert result["title"] == "Retry Test"
        assert result["html"] == "<p>Content after retry</p>"


@pytest.mark.asyncio
async def test_extract_page_content_navigation_error(
    mock_config: Config, 
    mock_page: MagicMock
) -> None:
    """Test handling of navigation errors."""
    url = "https://example.com/error-page"
    
    # Mock navigation error
    mock_page.goto.side_effect = Exception("Navigation failed")
    
    with pytest.raises(Exception):
        await extract_page_content(mock_page, url, mock_config)


@pytest.mark.asyncio
async def test_extract_page_content_cookie_dismissal(
    mock_config: Config, 
    mock_page: MagicMock
) -> None:
    """Test cookie banner dismissal functionality."""
    url = "https://example.com/cookie-page"
    
    # Mock cookie banner elements
    cookie_button = MagicMock()
    cookie_button.click = AsyncMock()
    mock_page.query_selector_all.return_value = [cookie_button]
    
    # Mock successful content extraction
    title_element = MagicMock()
    title_element.text_content = AsyncMock(return_value="Cookie Test")
    content_element = MagicMock()
    content_element.inner_html = AsyncMock(return_value="<p>Content</p>")
    mock_page.query_selector.side_effect = [title_element, content_element]
    
    with patch('d361.offline.content.markdownify') as mock_markdownify:
        mock_markdownify.return_value = "Content"
        
        result = await extract_page_content(mock_page, url, mock_config)
        
        # Should dismiss cookies and extract content
        cookie_button.click.assert_called_once()
        assert result["title"] == "Cookie Test"