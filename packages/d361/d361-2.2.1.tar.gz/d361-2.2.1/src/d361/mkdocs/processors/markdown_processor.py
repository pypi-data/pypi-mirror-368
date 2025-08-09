"""Markdown processor for Document360 to MkDocs conversion.

This module provides enhanced Markdown processing capabilities specifically
optimized for MkDocs, including support for extensions, formatting, and
content structure optimization.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/markdown_processor.py

import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from loguru import logger


class MarkdownProcessor:
    """Process Document360 content for optimal MkDocs presentation.
    
    This class converts Document360 HTML content to optimized Markdown
    that works well with MkDocs themes, plugins, and extensions.
    
    Features:
    - HTML to Markdown conversion with MkDocs extensions support
    - Document360 specific formatting handling
    - Code block enhancement for syntax highlighting
    - Table formatting optimization
    - Link processing and normalization
    - Image processing with responsive features
    
    Example:
        processor = MarkdownProcessor()
        markdown_content = await processor.convert(html_content)
    """
    
    def __init__(
        self,
        enable_extensions: bool = True,
        code_highlighting: bool = True,
        responsive_images: bool = True,
        table_optimization: bool = True,
    ) -> None:
        """Initialize Markdown processor.
        
        Args:
            enable_extensions: Enable MkDocs extension formatting
            code_highlighting: Enable code syntax highlighting
            responsive_images: Enable responsive image handling
            table_optimization: Enable table formatting optimization
        """
        self.enable_extensions = enable_extensions
        self.code_highlighting = code_highlighting
        self.responsive_images = responsive_images
        self.table_optimization = table_optimization
        
        # Conversion statistics
        self.stats = {
            "html_elements_converted": 0,
            "code_blocks_processed": 0,
            "tables_processed": 0,
            "images_processed": 0,
            "links_processed": 0,
        }
        
        logger.info("Initialized MarkdownProcessor")
    
    async def convert(self, content: str) -> str:
        """Convert content to MkDocs-optimized Markdown.
        
        Args:
            content: Content to convert (HTML or mixed)
            
        Returns:
            Converted Markdown content
        """
        logger.debug("Processing content for MkDocs Markdown conversion")
        
        # Reset statistics
        self._reset_stats()
        
        # Apply conversion pipeline
        processed_content = content
        
        # Convert Document360 specific elements
        processed_content = await self._convert_d360_elements(processed_content)
        
        # Convert HTML to Markdown
        processed_content = await self._html_to_markdown(processed_content)
        
        # Process code blocks
        processed_content = await self._process_code_blocks(processed_content)
        
        # Process tables
        if self.table_optimization:
            processed_content = await self._process_tables(processed_content)
        
        # Process images
        if self.responsive_images:
            processed_content = await self._process_images(processed_content)
        
        # Process links
        processed_content = await self._process_links(processed_content)
        
        # Apply MkDocs extensions formatting
        if self.enable_extensions:
            processed_content = await self._apply_mkdocs_extensions(processed_content)
        
        # Final cleanup
        processed_content = await self._final_cleanup(processed_content)
        
        logger.debug(f"Markdown conversion complete: {self.stats}")
        return processed_content
    
    def _reset_stats(self) -> None:
        """Reset conversion statistics."""
        for key in self.stats:
            self.stats[key] = 0
    
    async def _convert_d360_elements(self, content: str) -> str:
        """Convert Document360 specific elements to Markdown."""
        # Convert Document360 callout boxes to admonitions
        content = self._convert_d360_callouts(content)
        
        # Convert Document360 code blocks
        content = self._convert_d360_code_blocks(content)
        
        # Convert Document360 tables
        content = self._convert_d360_tables(content)
        
        # Convert Document360 images
        content = self._convert_d360_images(content)
        
        return content
    
    def _convert_d360_callouts(self, content: str) -> str:
        """Convert Document360 callout boxes to MkDocs admonitions."""
        # Pattern for Document360 callouts
        callout_patterns = [
            (r'<div class="callout callout-info[^"]*"[^>]*>(.*?)</div>', 'note'),
            (r'<div class="callout callout-warning[^"]*"[^>]*>(.*?)</div>', 'warning'),
            (r'<div class="callout callout-danger[^"]*"[^>]*>(.*?)</div>', 'danger'),
            (r'<div class="callout callout-success[^"]*"[^>]*>(.*?)</div>', 'success'),
            (r'<div class="alert alert-info[^"]*"[^>]*>(.*?)</div>', 'note'),
            (r'<div class="alert alert-warning[^"]*"[^>]*>(.*?)</div>', 'warning'),
            (r'<div class="alert alert-danger[^"]*"[^>]*>(.*?)</div>', 'danger'),
            (r'<div class="alert alert-success[^"]*"[^>]*>(.*?)</div>', 'success'),
        ]
        
        for pattern, admonition_type in callout_patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                # Convert to MkDocs admonition
                admonition_content = re.sub(r'<[^>]+>', '', match).strip()
                admonition = f'\n!!! {admonition_type}\n\n    {admonition_content}\n\n'
                content = re.sub(pattern, admonition, content, flags=re.DOTALL | re.IGNORECASE)
                self.stats["html_elements_converted"] += 1
        
        return content
    
    def _convert_d360_code_blocks(self, content: str) -> str:
        """Convert Document360 code blocks to MkDocs format."""
        # Pattern for Document360 code blocks
        code_patterns = [
            r'<pre><code class="language-([^"]*)"[^>]*>(.*?)</code></pre>',
            r'<pre><code[^>]*>(.*?)</code></pre>',
            r'<code class="language-([^"]*)"[^>]*>(.*?)</code>',
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    language, code_content = match
                    # Format as MkDocs code block
                    if language and self.code_highlighting:
                        formatted_code = f'\n```{language}\n{code_content.strip()}\n```\n'
                    else:
                        formatted_code = f'\n```\n{code_content.strip()}\n```\n'
                else:
                    code_content = match if isinstance(match, str) else match[0]
                    formatted_code = f'\n```\n{code_content.strip()}\n```\n'
                
                content = content.replace(f'<pre><code{language if "language" in pattern else ""}>{code_content}</code></pre>', formatted_code)
                self.stats["code_blocks_processed"] += 1
        
        return content
    
    def _convert_d360_tables(self, content: str) -> str:
        """Convert Document360 tables to Markdown format."""
        # Basic table conversion (can be enhanced)
        table_pattern = r'<table[^>]*>(.*?)</table>'
        tables = re.findall(table_pattern, content, re.DOTALL)
        
        for table_content in tables:
            try:
                markdown_table = self._html_table_to_markdown(table_content)
                content = content.replace(f'<table{table_content}</table>', markdown_table)
                self.stats["tables_processed"] += 1
            except Exception as e:
                logger.warning(f"Failed to convert table: {e}")
        
        return content
    
    def _html_table_to_markdown(self, table_html: str) -> str:
        """Convert HTML table to Markdown table format."""
        # This is a simplified implementation
        # A more robust solution would use a proper HTML parser
        
        # Extract rows
        row_pattern = r'<tr[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, table_html, re.DOTALL)
        
        if not rows:
            return table_html  # Return original if parsing fails
        
        markdown_rows = []
        is_header = True
        
        for row_html in rows:
            # Extract cells
            cell_pattern = r'<t[hd][^>]*>(.*?)</t[hd]>'
            cells = re.findall(cell_pattern, row_html, re.DOTALL)
            
            if cells:
                # Clean cell content
                cleaned_cells = []
                for cell in cells:
                    cleaned = re.sub(r'<[^>]+>', '', cell).strip()
                    cleaned_cells.append(cleaned)
                
                # Create Markdown row
                markdown_row = '| ' + ' | '.join(cleaned_cells) + ' |'
                markdown_rows.append(markdown_row)
                
                # Add separator after header
                if is_header:
                    separator = '| ' + ' | '.join(['---'] * len(cleaned_cells)) + ' |'
                    markdown_rows.append(separator)
                    is_header = False
        
        return '\n' + '\n'.join(markdown_rows) + '\n'
    
    def _convert_d360_images(self, content: str) -> str:
        """Convert Document360 images to Markdown format."""
        img_pattern = r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>'
        matches = re.findall(img_pattern, content)
        
        for src, alt in matches:
            markdown_img = f'![{alt}]({src})'
            if self.responsive_images:
                markdown_img += '{: .d360-image }'
            
            # Replace the HTML img tag
            original_pattern = f'<img[^>]*src="{re.escape(src)}"[^>]*/?>'
            content = re.sub(original_pattern, markdown_img, content)
            self.stats["images_processed"] += 1
        
        return content
    
    async def _html_to_markdown(self, content: str) -> str:
        """Convert remaining HTML elements to Markdown."""
        # Convert headers
        for level in range(1, 7):
            pattern = f'<h{level}[^>]*>(.*?)</h{level}>'
            replacement = f'{"#" * level} \\1'
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Convert paragraphs
        content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert line breaks
        content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
        
        # Convert bold and italic
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert lists
        content = re.sub(r'<ul[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</ul>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<ol[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'</ol>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert links
        link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
        content = re.sub(link_pattern, r'[\2](\1)', content, flags=re.DOTALL | re.IGNORECASE)
        
        self.stats["html_elements_converted"] += 1
        return content
    
    async def _process_code_blocks(self, content: str) -> str:
        """Enhance code blocks for MkDocs."""
        if not self.code_highlighting:
            return content
        
        # Add title annotations to code blocks
        code_block_pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(code_block_pattern, content, re.DOTALL)
        
        for language, code in matches:
            if language:
                # Add copy button support
                enhanced_block = f'```{language}\n{code}```'
                original_block = f'```{language}\n{code}```'
                content = content.replace(original_block, enhanced_block)
        
        return content
    
    async def _process_tables(self, content: str) -> str:
        """Optimize tables for MkDocs."""
        if not self.table_optimization:
            return content
        
        # Add responsive table wrapper
        table_pattern = r'(\|.*?\|(?:\n\|.*?\|)*)'
        tables = re.findall(table_pattern, content, re.MULTILINE)
        
        for table in tables:
            enhanced_table = f'<div class="d360-table-wrapper">\n\n{table}\n\n</div>'
            content = content.replace(table, enhanced_table)
            self.stats["tables_processed"] += 1
        
        return content
    
    async def _process_images(self, content: str) -> str:
        """Process images for MkDocs."""
        if not self.responsive_images:
            return content
        
        # Add responsive classes to images
        img_pattern = r'!\[([^\]]*)\]\(([^)]*)\)'
        matches = re.findall(img_pattern, content)
        
        for alt, src in matches:
            original = f'![{alt}]({src})'
            enhanced = f'![{alt}]({src}){{: .d360-image .d360-image--center }}'
            content = content.replace(original, enhanced)
            self.stats["images_processed"] += 1
        
        return content
    
    async def _process_links(self, content: str) -> str:
        """Process and normalize links."""
        # This is where we would normalize Document360 links
        # For now, just count them
        link_pattern = r'\[([^\]]*)\]\(([^)]*)\)'
        matches = re.findall(link_pattern, content)
        self.stats["links_processed"] = len(matches)
        
        return content
    
    async def _apply_mkdocs_extensions(self, content: str) -> str:
        """Apply MkDocs extension formatting."""
        if not self.enable_extensions:
            return content
        
        # Convert to tabbed content where appropriate
        content = self._convert_to_tabs(content)
        
        # Enhance admonitions
        content = self._enhance_admonitions(content)
        
        return content
    
    def _convert_to_tabs(self, content: str) -> str:
        """Convert appropriate content to tabbed format."""
        # Look for patterns that should become tabs
        # This is a placeholder for more sophisticated tab detection
        return content
    
    def _enhance_admonitions(self, content: str) -> str:
        """Enhance admonitions with better formatting."""
        # Add custom titles to admonitions
        admonition_pattern = r'!!! (\w+)\n\n    (.*?)(?=\n\n|\n!!! |\Z)'
        matches = re.findall(admonition_pattern, content, re.DOTALL)
        
        for adm_type, adm_content in matches:
            # Add custom title based on type
            titles = {
                'note': 'Note',
                'warning': 'Warning', 
                'danger': 'Important',
                'success': 'Success',
            }
            
            title = titles.get(adm_type, adm_type.capitalize())
            enhanced = f'!!! {adm_type} "{title}"\n\n    {adm_content}'
            
            original = f'!!! {adm_type}\n\n    {adm_content}'
            content = content.replace(original, enhanced)
        
        return content
    
    async def _final_cleanup(self, content: str) -> str:
        """Perform final content cleanup."""
        # Remove extra whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Clean up line endings
        content = content.strip()
        
        # Ensure content ends with newline
        if not content.endswith('\n'):
            content += '\n'
        
        return content
    
    def get_conversion_stats(self) -> Dict[str, int]:
        """Get conversion statistics.
        
        Returns:
            Dictionary of conversion statistics
        """
        return self.stats.copy()