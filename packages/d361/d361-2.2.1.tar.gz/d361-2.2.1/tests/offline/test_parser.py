# this_file: tests/offline/test_parser.py
"""Test suite for d361.offline.parser module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from d361.offline.parser import parse_sitemap
from d361.offline.config import Config


@pytest.fixture
def mock_config(tmp_path: Path) -> Config:
    """Create a mock config for testing."""
    return Config(
        map_url="https://example.com/sitemap.xml",
        output_dir=tmp_path / "test_output"
    )


@pytest.fixture
def sample_sitemap_xml() -> str:
    """Sample sitemap XML content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
        <lastmod>2023-01-01T00:00:00+00:00</lastmod>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
        <lastmod>2023-01-02T00:00:00+00:00</lastmod>
    </url>
    <url>
        <loc>https://example.com/page3</loc>
        <lastmod>2023-01-03T00:00:00+00:00</lastmod>
    </url>
</urlset>"""


@pytest.mark.asyncio
async def test_parse_sitemap_success(mock_config: Config, sample_sitemap_xml: str) -> None:
    """Test successful sitemap parsing."""
    with patch('d361.offline.parser._parse_with_playwright_direct') as mock_parse:
        mock_parse.return_value = sample_sitemap_xml
        
        result = await parse_sitemap(mock_config)
        
        assert len(result) == 3
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result
        assert "https://example.com/page3" in result
        mock_parse.assert_called_once_with(mock_config)


@pytest.mark.asyncio
async def test_parse_sitemap_fallback_methods(mock_config: Config, sample_sitemap_xml: str) -> None:
    """Test that fallback methods are tried when primary method fails."""
    with patch('d361.offline.parser._parse_with_playwright_direct') as mock_direct, \
         patch('d361.offline.parser._parse_with_playwright_stealth') as mock_stealth:
        
        # First method fails
        mock_direct.side_effect = Exception("Direct method failed")
        # Second method succeeds
        mock_stealth.return_value = sample_sitemap_xml
        
        result = await parse_sitemap(mock_config)
        
        assert len(result) == 3
        mock_direct.assert_called_once()
        mock_stealth.assert_called_once()


@pytest.mark.asyncio
async def test_parse_sitemap_empty_result(mock_config: Config) -> None:
    """Test handling of empty sitemap."""
    empty_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>"""
    
    with patch('d361.offline.parser._parse_with_playwright_direct') as mock_parse:
        mock_parse.return_value = empty_sitemap
        
        result = await parse_sitemap(mock_config)
        
        assert len(result) == 0


@pytest.mark.asyncio
async def test_parse_sitemap_duplicate_urls(mock_config: Config) -> None:
    """Test that duplicate URLs are handled correctly."""
    duplicate_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://example.com/page1</loc>
    </url>
    <url>
        <loc>https://example.com/page1</loc>
    </url>
    <url>
        <loc>https://example.com/page2</loc>
    </url>
</urlset>"""
    
    with patch('d361.offline.parser._parse_with_playwright_direct') as mock_parse:
        mock_parse.return_value = duplicate_sitemap
        
        result = await parse_sitemap(mock_config)
        
        # Should deduplicate URLs
        assert len(result) == 2
        assert "https://example.com/page1" in result
        assert "https://example.com/page2" in result


@pytest.mark.asyncio
async def test_parse_sitemap_all_methods_fail(mock_config: Config) -> None:
    """Test behavior when all parsing methods fail."""
    with patch('d361.offline.parser._parse_with_playwright_direct') as mock_direct, \
         patch('d361.offline.parser._parse_with_playwright_stealth') as mock_stealth, \
         patch('d361.offline.parser._parse_with_aiohttp_direct') as mock_aiohttp, \
         patch('d361.offline.parser._parse_with_playwright_via_robots') as mock_robots:
        
        # All methods fail
        mock_direct.side_effect = Exception("Direct failed")
        mock_stealth.side_effect = Exception("Stealth failed")
        mock_aiohttp.side_effect = Exception("Aiohttp failed")
        mock_robots.side_effect = Exception("Robots failed")
        
        with pytest.raises(Exception):
            await parse_sitemap(mock_config)


@pytest.mark.asyncio
async def test_parse_sitemap_malformed_xml(mock_config: Config) -> None:
    """Test handling of malformed XML."""
    malformed_xml = "This is not valid XML"
    
    with patch('d361.offline.parser._parse_with_playwright_direct') as mock_parse:
        mock_parse.return_value = malformed_xml
        
        # Should handle malformed XML gracefully
        result = await parse_sitemap(mock_config)
        assert len(result) == 0