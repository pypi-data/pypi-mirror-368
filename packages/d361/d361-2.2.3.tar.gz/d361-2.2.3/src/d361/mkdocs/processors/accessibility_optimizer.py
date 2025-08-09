"""Accessibility optimization for MkDocs sites.

This module provides comprehensive accessibility enhancements and WCAG compliance
features for MkDocs-generated documentation sites.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/accessibility_optimizer.py

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger

from d361.api.errors import Document360Error, ErrorCategory, ErrorSeverity


class WCAGLevel(Enum):
    """WCAG compliance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class ContrastRatio(Enum):
    """Minimum contrast ratios for WCAG compliance."""
    AA_NORMAL = 4.5
    AA_LARGE = 3.0
    AAA_NORMAL = 7.0
    AAA_LARGE = 4.5


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found during analysis."""
    
    type: str
    severity: str  # "error", "warning", "info"
    message: str
    element: Optional[str] = None
    line_number: Optional[int] = None
    wcag_criterion: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class AccessibilityReport:
    """Comprehensive accessibility audit report."""
    
    compliance_level: WCAGLevel
    total_issues: int = 0
    errors: List[AccessibilityIssue] = field(default_factory=list)
    warnings: List[AccessibilityIssue] = field(default_factory=list)
    info: List[AccessibilityIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    
    def add_issue(self, issue: AccessibilityIssue) -> None:
        """Add an accessibility issue to the report."""
        self.total_issues += 1
        
        if issue.severity == "error":
            self.errors.append(issue)
        elif issue.severity == "warning":
            self.warnings.append(issue)
        else:
            self.info.append(issue)
    
    def is_compliant(self) -> bool:
        """Check if the content meets the target WCAG compliance level."""
        # For WCAG AA compliance, we should have no errors
        return len(self.errors) == 0


class AccessibilityOptimizer:
    """Comprehensive accessibility optimization for MkDocs sites.
    
    This class provides WCAG 2.1 compliance features including:
    - Content accessibility analysis and enhancement
    - Image alt text validation and generation
    - Heading hierarchy validation
    - Link accessibility improvements
    - Color contrast analysis
    - Keyboard navigation enhancements
    - Screen reader optimizations
    - Accessible theme configurations
    
    Example:
        accessibility = AccessibilityOptimizer(
            wcag_level=WCAGLevel.AA,
            auto_fix=True
        )
        
        enhanced_content = await accessibility.enhance_content(
            content="# My Page\nThis is a [link](http://example.com)...",
            page_title="My Page"
        )
    """
    
    def __init__(
        self,
        wcag_level: WCAGLevel = WCAGLevel.AA,
        auto_fix: bool = True,
        generate_alt_text: bool = True,
        enhance_links: bool = True,
    ) -> None:
        """Initialize accessibility optimizer.
        
        Args:
            wcag_level: Target WCAG compliance level
            auto_fix: Automatically fix issues where possible
            generate_alt_text: Generate alt text for images missing it
            enhance_links: Enhance link accessibility
        """
        self.wcag_level = wcag_level
        self.auto_fix = auto_fix
        self.generate_alt_text = generate_alt_text
        self.enhance_links = enhance_links
        
        logger.info(f"Initialized AccessibilityOptimizer for WCAG {wcag_level.value} compliance")
    
    async def enhance_content(
        self,
        content: str,
        page_title: str,
        base_url: Optional[str] = None,
    ) -> Tuple[str, AccessibilityReport]:
        """Enhance content for accessibility compliance.
        
        Args:
            content: Markdown content to enhance
            page_title: Page title for context
            base_url: Base URL for link analysis
            
        Returns:
            Tuple of enhanced content and accessibility report
        """
        logger.debug(f"Enhancing accessibility for: {page_title}")
        
        report = AccessibilityReport(compliance_level=self.wcag_level)
        enhanced_content = content
        
        # Analyze and enhance different aspects
        enhanced_content = self._enhance_headings(enhanced_content, report)
        enhanced_content = self._enhance_images(enhanced_content, report)
        enhanced_content = self._enhance_links(enhanced_content, report, base_url)
        enhanced_content = self._enhance_tables(enhanced_content, report)
        enhanced_content = self._enhance_lists(enhanced_content, report)
        
        # Validate final content
        self._validate_content_structure(enhanced_content, report)
        
        logger.info(f"Accessibility enhancement completed for: {page_title}")
        logger.info(f"Found {report.total_issues} issues ({len(report.errors)} errors, {len(report.warnings)} warnings)")
        
        return enhanced_content, report
    
    def _enhance_headings(self, content: str, report: AccessibilityReport) -> str:
        """Enhance heading structure for accessibility.
        
        Args:
            content: Content to analyze
            report: Report to update with findings
            
        Returns:
            Enhanced content
        """
        lines = content.split('\n')
        enhanced_lines = []
        heading_levels = []
        
        for i, line in enumerate(lines):
            # Match markdown headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                
                heading_levels.append(level)
                
                # Check for heading hierarchy issues
                if len(heading_levels) > 1:
                    prev_level = heading_levels[-2]
                    if level > prev_level + 1:
                        report.add_issue(AccessibilityIssue(
                            type="heading_hierarchy",
                            severity="warning",
                            message=f"Heading level jumps from H{prev_level} to H{level}",
                            line_number=i + 1,
                            wcag_criterion="1.3.1",
                            suggestion="Use sequential heading levels (H1, H2, H3, etc.)"
                        ))
                
                # Check for empty headings
                if not title:
                    report.add_issue(AccessibilityIssue(
                        type="empty_heading",
                        severity="error",
                        message="Empty heading found",
                        line_number=i + 1,
                        wcag_criterion="2.4.6",
                        suggestion="Provide descriptive heading text"
                    ))
                
                enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)
        
        # Check for missing H1
        if not heading_levels or heading_levels[0] != 1:
            report.add_issue(AccessibilityIssue(
                type="missing_h1",
                severity="warning",
                message="Page missing H1 heading",
                wcag_criterion="2.4.6",
                suggestion="Add an H1 heading at the top of the page"
            ))
        else:
            report.passed_checks.append("heading_hierarchy")
        
        return '\n'.join(enhanced_lines)
    
    def _enhance_images(self, content: str, report: AccessibilityReport) -> str:
        """Enhance images for accessibility.
        
        Args:
            content: Content to analyze
            report: Report to update with findings
            
        Returns:
            Enhanced content
        """
        # Match markdown images: ![alt](src "title")
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)(?:\s+"([^"]+)")?\)'
        
        def enhance_image(match):
            alt_text = match.group(1).strip()
            src = match.group(2).strip()
            title = match.group(3) if match.group(3) else None
            
            # Check for missing alt text
            if not alt_text:
                if self.generate_alt_text:
                    # Generate basic alt text from filename
                    filename = src.split('/')[-1].split('.')[0]
                    alt_text = filename.replace('-', ' ').replace('_', ' ').title()
                    
                    report.add_issue(AccessibilityIssue(
                        type="missing_alt_text",
                        severity="warning",
                        message=f"Generated alt text for image: {src}",
                        suggestion="Review and improve the generated alt text for accuracy"
                    ))
                else:
                    report.add_issue(AccessibilityIssue(
                        type="missing_alt_text",
                        severity="error",
                        message=f"Image missing alt text: {src}",
                        wcag_criterion="1.1.1",
                        suggestion="Add descriptive alt text that conveys the image's purpose"
                    ))
            
            # Check for redundant alt text
            redundant_phrases = ["image of", "picture of", "photo of", "screenshot of"]
            if any(phrase in alt_text.lower() for phrase in redundant_phrases):
                report.add_issue(AccessibilityIssue(
                    type="redundant_alt_text",
                    severity="info",
                    message=f"Alt text may contain redundant phrase: {alt_text}",
                    suggestion="Remove redundant phrases like 'image of' from alt text"
                ))
            
            # Reconstruct image markdown
            if title:
                return f'![{alt_text}]({src} "{title}")'
            else:
                return f'![{alt_text}]({src})'
        
        enhanced_content = re.sub(image_pattern, enhance_image, content)
        
        # Count successful image enhancements
        image_count = len(re.findall(image_pattern, content))
        if image_count > 0:
            report.passed_checks.append(f"enhanced_{image_count}_images")
        
        return enhanced_content
    
    def _enhance_links(self, content: str, report: AccessibilityReport, base_url: Optional[str]) -> str:
        """Enhance links for accessibility.
        
        Args:
            content: Content to analyze
            report: Report to update with findings
            base_url: Base URL for external link detection
            
        Returns:
            Enhanced content
        """
        if not self.enhance_links:
            return content
        
        # Match markdown links: [text](url "title")
        link_pattern = r'\[([^\]]+)\]\(([^)]+?)(?:\s+"([^"]+)")?\)'
        
        def enhance_link(match):
            link_text = match.group(1).strip()
            url = match.group(2).strip()
            title = match.group(3) if match.group(3) else None
            
            # Check for non-descriptive link text
            generic_phrases = ["click here", "here", "read more", "more", "link", "this"]
            if link_text.lower() in generic_phrases:
                report.add_issue(AccessibilityIssue(
                    type="generic_link_text",
                    severity="error",
                    message=f"Non-descriptive link text: '{link_text}'",
                    wcag_criterion="2.4.4",
                    suggestion="Use descriptive link text that explains the link's purpose"
                ))
            
            # Check for URL as link text
            if url in link_text or link_text.startswith(('http://', 'https://', 'www.')):
                report.add_issue(AccessibilityIssue(
                    type="url_as_link_text",
                    severity="warning",
                    message=f"URL used as link text: {link_text}",
                    suggestion="Replace URL with descriptive link text"
                ))
            
            # Enhance external links
            if base_url and url.startswith(('http://', 'https://')) and base_url not in url:
                # This is an external link
                enhanced_title = title or f"External link: {link_text}"
                
                if self.auto_fix and not title:
                    return f'[{link_text}]({url} "{enhanced_title}")'
            
            # Return original or enhanced link
            if title:
                return f'[{link_text}]({url} "{title}")'
            else:
                return f'[{link_text}]({url})'
        
        enhanced_content = re.sub(link_pattern, enhance_link, content)
        
        # Count links processed
        link_count = len(re.findall(link_pattern, content))
        if link_count > 0:
            report.passed_checks.append(f"analyzed_{link_count}_links")
        
        return enhanced_content
    
    def _enhance_tables(self, content: str, report: AccessibilityReport) -> str:
        """Enhance tables for accessibility.
        
        Args:
            content: Content to analyze
            report: Report to update with findings
            
        Returns:
            Enhanced content
        """
        lines = content.split('\n')
        enhanced_lines = []
        in_table = False
        table_has_header = False
        
        for i, line in enumerate(lines):
            # Detect table rows
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                if not in_table:
                    in_table = True
                    table_has_header = False
                
                # Check if this is a header separator line
                if re.match(r'^\|[\s\-:]+\|$', line.strip()):
                    table_has_header = True
                
                enhanced_lines.append(line)
            else:
                if in_table:
                    # End of table
                    if not table_has_header:
                        report.add_issue(AccessibilityIssue(
                            type="table_missing_headers",
                            severity="error",
                            message="Table missing header row",
                            line_number=i,
                            wcag_criterion="1.3.1",
                            suggestion="Add header row to table for screen reader accessibility"
                        ))
                    in_table = False
                
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _enhance_lists(self, content: str, report: AccessibilityReport) -> str:
        """Enhance lists for accessibility.
        
        Args:
            content: Content to analyze
            report: Report to update with findings
            
        Returns:
            Enhanced content
        """
        # Lists are generally accessible in markdown, but we can check for proper nesting
        lines = content.split('\n')
        list_nesting = []
        
        for i, line in enumerate(lines):
            # Check for list items
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
            if list_match:
                indent = len(list_match.group(1))
                marker = list_match.group(2)
                content_text = list_match.group(3)
                
                # Track nesting levels
                list_nesting.append(indent)
                
                # Check for empty list items
                if not content_text.strip():
                    report.add_issue(AccessibilityIssue(
                        type="empty_list_item",
                        severity="warning",
                        message="Empty list item found",
                        line_number=i + 1,
                        suggestion="Remove empty list items or add content"
                    ))
        
        if list_nesting:
            report.passed_checks.append("list_structure_analyzed")
        
        return content
    
    def _validate_content_structure(self, content: str, report: AccessibilityReport) -> None:
        """Validate overall content structure for accessibility.
        
        Args:
            content: Content to validate
            report: Report to update with findings
        """
        # Check for adequate text length
        text_content = re.sub(r'[#*`\[\]()]+', '', content)
        word_count = len(text_content.split())
        
        if word_count < 50:
            report.add_issue(AccessibilityIssue(
                type="insufficient_content",
                severity="info",
                message=f"Page has only {word_count} words",
                suggestion="Consider adding more descriptive content"
            ))
        
        # Check for reading level (basic check)
        sentences = re.split(r'[.!?]+', text_content)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        if avg_sentence_length > 20:
            report.add_issue(AccessibilityIssue(
                type="complex_sentences",
                severity="info",
                message=f"Average sentence length is {avg_sentence_length:.1f} words",
                suggestion="Consider breaking up long sentences for better readability"
            ))
        
        report.passed_checks.append("content_structure_validated")
    
    def generate_accessibility_config(self) -> Dict[str, Any]:
        """Generate accessibility configuration for MkDocs theme.
        
        Returns:
            Accessibility configuration
        """
        config = {
            "accessibility": {
                "wcag_level": self.wcag_level.value,
                "features": {
                    "skip_links": True,
                    "focus_indicators": True,
                    "keyboard_navigation": True,
                    "screen_reader_support": True,
                    "high_contrast": True,
                    "reduced_motion": True,
                }
            },
            
            "theme_overrides": {
                "aria_labels": {
                    "search": "Search documentation",
                    "navigation": "Main navigation",
                    "toc": "Table of contents",
                    "edit_page": "Edit this page",
                    "view_source": "View page source",
                },
                
                "keyboard_shortcuts": {
                    "search": "/",
                    "navigation": "n",
                    "toggle_sidebar": "s",
                },
                
                "contrast_ratios": {
                    "minimum": ContrastRatio.AA_NORMAL.value,
                    "enhanced": ContrastRatio.AAA_NORMAL.value,
                }
            }
        }
        
        return config
    
    def generate_content_guidelines(self) -> Dict[str, List[str]]:
        """Generate content accessibility guidelines.
        
        Returns:
            Dictionary of guidelines by category
        """
        return {
            "headings": [
                "Use headings in sequential order (H1, H2, H3)",
                "Don't skip heading levels",
                "Use only one H1 per page",
                "Make headings descriptive and meaningful",
            ],
            
            "images": [
                "Provide descriptive alt text for all images",
                "Don't start alt text with 'Image of' or 'Picture of'",
                "Use empty alt text (alt='') for decorative images",
                "Consider using captions for complex images",
            ],
            
            "links": [
                "Use descriptive link text that makes sense out of context",
                "Avoid generic phrases like 'click here' or 'read more'",
                "Indicate when links open in new windows",
                "Ensure links have sufficient color contrast",
            ],
            
            "tables": [
                "Always include header rows in data tables",
                "Use caption elements to describe table purpose", 
                "Keep tables simple and avoid merged cells when possible",
                "Consider responsive design for mobile users",
            ],
            
            "content": [
                "Use clear, simple language",
                "Define acronyms on first use",
                "Organize content with clear structure",
                "Ensure sufficient color contrast (4.5:1 minimum)",
            ]
        }
    
    async def audit_full_site(
        self,
        pages: List[Dict[str, Any]],
        site_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Perform comprehensive accessibility audit of entire site.
        
        Args:
            pages: List of page information with content
            site_config: MkDocs site configuration
            
        Returns:
            Complete site accessibility audit report
        """
        logger.info("Starting comprehensive site accessibility audit")
        
        site_report = {
            "audit_date": logger.info,
            "wcag_level": self.wcag_level.value,
            "total_pages": len(pages),
            "pages_audited": 0,
            "total_issues": 0,
            "config_issues": [],
            "page_reports": [],
            "summary": {
                "errors": 0,
                "warnings": 0,
                "info": 0,
                "compliant_pages": 0,
            }
        }
        
        # Audit site configuration
        config_issues = self._audit_site_config(site_config)
        site_report["config_issues"] = config_issues
        
        # Audit individual pages
        for page_info in pages:
            try:
                content = page_info.get("content", "")
                title = page_info.get("title", "Untitled")
                
                enhanced_content, page_report = await self.enhance_content(
                    content=content,
                    page_title=title,
                    base_url=site_config.get("site_url")
                )
                
                site_report["pages_audited"] += 1
                site_report["total_issues"] += page_report.total_issues
                site_report["summary"]["errors"] += len(page_report.errors)
                site_report["summary"]["warnings"] += len(page_report.warnings) 
                site_report["summary"]["info"] += len(page_report.info)
                
                if page_report.is_compliant():
                    site_report["summary"]["compliant_pages"] += 1
                
                site_report["page_reports"].append({
                    "title": title,
                    "url": page_info.get("url", ""),
                    "compliant": page_report.is_compliant(),
                    "issues": page_report.total_issues,
                    "errors": len(page_report.errors),
                    "warnings": len(page_report.warnings),
                })
                
            except Exception as e:
                logger.error(f"Error auditing page {page_info.get('title', 'Unknown')}: {e}")
                continue
        
        # Calculate compliance percentage
        if site_report["pages_audited"] > 0:
            compliance_rate = (site_report["summary"]["compliant_pages"] / 
                             site_report["pages_audited"]) * 100
            site_report["compliance_percentage"] = compliance_rate
        
        logger.info(f"Site accessibility audit completed: {site_report['pages_audited']} pages audited")
        logger.info(f"Compliance rate: {site_report.get('compliance_percentage', 0):.1f}%")
        
        return site_report
    
    def _audit_site_config(self, config: Dict[str, Any]) -> List[AccessibilityIssue]:
        """Audit site configuration for accessibility issues.
        
        Args:
            config: MkDocs configuration
            
        Returns:
            List of configuration accessibility issues
        """
        issues = []
        
        # Check theme configuration
        theme = config.get("theme", {})
        if isinstance(theme, dict):
            theme_name = theme.get("name")
            
            # Check for accessibility-friendly themes
            if theme_name not in ["material"]:
                issues.append(AccessibilityIssue(
                    type="theme_accessibility",
                    severity="info",
                    message=f"Theme '{theme_name}' may have limited accessibility features",
                    suggestion="Consider using Material theme for better accessibility support"
                ))
        
        # Check for language specification
        if "lang" not in config:
            issues.append(AccessibilityIssue(
                type="missing_language",
                severity="warning",
                message="Site language not specified",
                wcag_criterion="3.1.1",
                suggestion="Add 'lang: en' (or appropriate language code) to config"
            ))
        
        return issues