"""Asset management for Document360 → MkDocs conversion.

This module provides comprehensive asset management including image processing,
CDN URL optimization, responsive image generation, and asset bundling.
"""
# this_file: external/int_folders/d361/src/d361/mkdocs/processors/asset_manager.py

import asyncio
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
import re

from loguru import logger

try:
    import httpx
    from PIL import Image, ImageOps, ImageDraw, ImageFont
    IMAGING_AVAILABLE = True
except ImportError:
    IMAGING_AVAILABLE = False
    logger.warning("PIL/Pillow not available - image processing will be limited")

# Optional imports for Phase 2 social cards generation
try:
    from PIL import ImageFilter
    import textwrap
    import io
    import base64
    SOCIAL_CARDS_AVAILABLE = True
except ImportError:
    SOCIAL_CARDS_AVAILABLE = False
    logger.warning("Social cards dependencies not available - some PIL features may be limited")


@dataclass
class AssetReference:
    """Represents an asset reference in content."""
    
    original_url: str
    asset_type: str  # image, video, document, etc.
    local_path: Optional[str] = None
    optimized_url: Optional[str] = None
    file_size: Optional[int] = None
    dimensions: Optional[Tuple[int, int]] = None
    mime_type: Optional[str] = None
    is_external: bool = False
    needs_download: bool = False
    optimization_applied: bool = False
    alt_text: Optional[str] = None
    title: Optional[str] = None


@dataclass
class OptimizationResult:
    """Results of asset optimization."""
    
    original_size: int
    optimized_size: int
    compression_ratio: float
    format_changed: bool = False
    original_format: Optional[str] = None
    optimized_format: Optional[str] = None
    responsive_variants: List[str] = None


class AssetManager:
    """Manage assets for Document360 → MkDocs conversion.
    
    This class handles comprehensive asset management including image processing,
    CDN URL optimization, responsive image generation, and asset bundling.
    
    Features:
    - Image downloading and optimization
    - CDN URL rewriting and optimization
    - Responsive image variant generation
    - Asset bundling and organization
    - Broken asset detection and reporting
    - Image format conversion (WebP, AVIF)
    - Lazy loading metadata
    
    Example:
        manager = AssetManager(
            output_dir=Path("docs/assets"),
            enable_optimization=True,
            generate_responsive=True,
            cdn_prefix="https://cdn.example.com"
        )
        assets = await manager.process_assets(content, article)
        optimized_content = manager.update_asset_references(content, assets)
    """
    
    def __init__(
        self,
        output_dir: Path,
        enable_optimization: bool = True,
        generate_responsive: bool = False,
        cdn_prefix: Optional[str] = None,
        max_image_width: int = 1200,
        image_quality: int = 85,
        convert_to_webp: bool = False,
        enable_lazy_loading: bool = True,
        download_external_assets: bool = False,
        # Phase 2 enhancements
        generate_social_cards: bool = False,
        social_card_template: str = "material",
        social_card_size: Tuple[int, int] = (1200, 630),
        social_card_background_color: str = "#ffffff",
        social_card_text_color: str = "#333333",
        social_card_accent_color: str = "#1976d2",
        social_card_font_family: Optional[str] = None,
        social_card_logo_path: Optional[str] = None,
        enable_social_card_caching: bool = True,
    ) -> None:
        """Initialize asset manager.
        
        Args:
            output_dir: Directory to store processed assets
            enable_optimization: Enable image optimization
            generate_responsive: Generate responsive image variants
            cdn_prefix: CDN prefix for optimized URLs
            max_image_width: Maximum image width for optimization
            image_quality: Image quality for compression (1-100)
            convert_to_webp: Convert images to WebP format
            enable_lazy_loading: Add lazy loading attributes
            download_external_assets: Download external assets locally
            # Phase 2 enhancements
            generate_social_cards: Enable social cards generation for articles
            social_card_template: Template style for social cards ('material', 'minimal', 'custom')
            social_card_size: Social card dimensions (width, height) in pixels
            social_card_background_color: Background color for social cards
            social_card_text_color: Text color for social cards
            social_card_accent_color: Accent color for highlights and borders
            social_card_font_family: Font family for text rendering
            social_card_logo_path: Path to logo image for social cards
            enable_social_card_caching: Enable caching for generated social cards
        """
        self.output_dir = Path(output_dir)
        self.enable_optimization = enable_optimization and IMAGING_AVAILABLE
        self.generate_responsive = generate_responsive and IMAGING_AVAILABLE
        self.cdn_prefix = cdn_prefix.rstrip('/') if cdn_prefix else None
        self.max_image_width = max_image_width
        self.image_quality = image_quality
        self.convert_to_webp = convert_to_webp and IMAGING_AVAILABLE
        self.enable_lazy_loading = enable_lazy_loading
        self.download_external_assets = download_external_assets
        
        # Phase 2 enhancements
        self.generate_social_cards = generate_social_cards and SOCIAL_CARDS_AVAILABLE and IMAGING_AVAILABLE
        self.social_card_template = social_card_template
        self.social_card_size = social_card_size
        self.social_card_background_color = social_card_background_color
        self.social_card_text_color = social_card_text_color
        self.social_card_accent_color = social_card_accent_color
        self.social_card_font_family = social_card_font_family
        self.social_card_logo_path = social_card_logo_path
        self.enable_social_card_caching = enable_social_card_caching
        
        # Create output directories
        self.images_dir = self.output_dir / "images"
        self.documents_dir = self.output_dir / "documents"
        self.videos_dir = self.output_dir / "videos"
        self.social_cards_dir = self.output_dir / "social_cards" if self.generate_social_cards else None
        
        for dir_path in [self.images_dir, self.documents_dir, self.videos_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        if self.social_cards_dir:
            self.social_cards_dir.mkdir(parents=True, exist_ok=True)
        
        # Asset tracking
        self.processed_assets: Dict[str, AssetReference] = {}
        self.broken_assets: List[AssetReference] = []
        self.optimization_stats: Dict[str, OptimizationResult] = {}
        
        # Phase 2: Social cards tracking
        self.social_cards_generated: Dict[str, str] = {}  # article_id -> social_card_path
        self.social_cards_cache: Dict[str, Dict[str, Any]] = {}  # Cache for social card metadata
        
        # HTTP client for downloading
        self._http_client: Optional[httpx.AsyncClient] = None
        
        # Compile regex patterns
        self._image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self._link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|tar|gz))\)', re.IGNORECASE)
        
        logger.debug(f"Initialized AssetManager with output_dir={output_dir}, optimization={enable_optimization}")
    
    async def process_assets(self, content: str, article_context: Optional[Dict] = None) -> List[AssetReference]:
        """Process all assets in content.
        
        Args:
            content: Content to process assets from
            article_context: Context information for the article
            
        Returns:
            List of processed asset references
        """
        logger.debug("Processing assets in content")
        
        # Initialize HTTP client if needed
        if not self._http_client and (self.download_external_assets or self.enable_optimization):
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "d361-mkdocs-exporter/1.0"}
            )
        
        assets = []
        
        # Extract and process images
        image_assets = await self._extract_and_process_images(content, article_context)
        assets.extend(image_assets)
        
        # Extract and process document links
        document_assets = await self._extract_and_process_documents(content, article_context)
        assets.extend(document_assets)
        
        # Phase 2: Generate social card if enabled and article context is provided
        social_card_asset = None
        if self.generate_social_cards and article_context:
            social_card_asset = await self._generate_social_card(article_context, content)
            if social_card_asset:
                assets.append(social_card_asset)
        
        logger.debug(f"Processed {len(assets)} assets ({len(image_assets)} images, {len(document_assets)} documents{', 1 social card' if social_card_asset else ''})")
        return assets
    
    def update_asset_references(self, content: str, assets: List[AssetReference]) -> str:
        """Update content with optimized asset references.
        
        Args:
            content: Original content
            assets: Processed asset references
            
        Returns:
            Content with updated asset references
        """
        logger.debug(f"Updating asset references for {len(assets)} assets")
        
        # Create URL mapping
        url_mapping = {asset.original_url: asset for asset in assets}
        
        # Update image references
        def replace_image(match):
            alt_text = match.group(1)
            original_url = match.group(2)
            
            asset = url_mapping.get(original_url)
            if asset and asset.optimized_url:
                # Build enhanced image tag
                img_attrs = []
                
                if self.enable_lazy_loading:
                    img_attrs.append('loading="lazy"')
                
                if asset.dimensions:
                    width, height = asset.dimensions
                    img_attrs.append(f'width="{width}" height="{height}"')
                
                # Add responsive image attributes if available
                if self.generate_responsive and hasattr(asset, 'responsive_variants'):
                    # This would be used with picture elements or srcset
                    pass
                
                attrs_str = f' {{{": ".join(img_attrs)}}}' if img_attrs else ''
                return f"![{alt_text}]({asset.optimized_url}){attrs_str}"
            
            return match.group(0)
        
        content = self._image_pattern.sub(replace_image, content)
        
        # Update document references
        def replace_document(match):
            text = match.group(1)
            original_url = match.group(2)
            
            asset = url_mapping.get(original_url)
            if asset and asset.optimized_url:
                # Add download attributes for documents
                attrs = '{ target="_blank" download }'
                return f"[{text}]({asset.optimized_url}){attrs}"
            
            return match.group(0)
        
        content = self._link_pattern.sub(replace_document, content)
        
        return content
    
    async def _extract_and_process_images(self, content: str, article_context: Optional[Dict] = None) -> List[AssetReference]:
        """Extract and process image assets."""
        images = []
        
        for match in self._image_pattern.finditer(content):
            alt_text = match.group(1)
            image_url = match.group(2).strip()
            
            # Skip if already processed
            if image_url in self.processed_assets:
                images.append(self.processed_assets[image_url])
                continue
            
            asset = AssetReference(
                original_url=image_url,
                asset_type="image",
                alt_text=alt_text,
                is_external=self._is_external_url(image_url)
            )
            
            try:
                # Process the image
                processed_asset = await self._process_single_image(asset, article_context)
                images.append(processed_asset)
                self.processed_assets[image_url] = processed_asset
                
            except Exception as e:
                logger.warning(f"Failed to process image {image_url}: {e}")
                asset.needs_download = False
                self.broken_assets.append(asset)
                images.append(asset)
        
        return images
    
    async def _extract_and_process_documents(self, content: str, article_context: Optional[Dict] = None) -> List[AssetReference]:
        """Extract and process document assets."""
        documents = []
        
        for match in self._link_pattern.finditer(content):
            link_text = match.group(1)
            doc_url = match.group(2).strip()
            
            # Skip if already processed
            if doc_url in self.processed_assets:
                documents.append(self.processed_assets[doc_url])
                continue
            
            asset = AssetReference(
                original_url=doc_url,
                asset_type="document",
                title=link_text,
                is_external=self._is_external_url(doc_url)
            )
            
            try:
                # Process the document
                processed_asset = await self._process_single_document(asset, article_context)
                documents.append(processed_asset)
                self.processed_assets[doc_url] = processed_asset
                
            except Exception as e:
                logger.warning(f"Failed to process document {doc_url}: {e}")
                asset.needs_download = False
                self.broken_assets.append(asset)
                documents.append(asset)
        
        return documents
    
    async def _process_single_image(self, asset: AssetReference, article_context: Optional[Dict] = None) -> AssetReference:
        """Process a single image asset."""
        original_url = asset.original_url
        
        # Handle CDN URL optimization first
        if self._is_document360_url(original_url):
            asset.optimized_url = self._optimize_d360_image_url(original_url)
        
        # Download and process if needed
        if (self.download_external_assets and asset.is_external) or self.enable_optimization:
            downloaded_path = await self._download_asset(asset, self.images_dir)
            
            if downloaded_path and self.enable_optimization:
                optimized_path = await self._optimize_image(downloaded_path, asset)
                if optimized_path:
                    asset.local_path = str(optimized_path)
                    asset.optimized_url = self._generate_asset_url(optimized_path)
                    asset.optimization_applied = True
        
        # Generate responsive variants if enabled
        if self.generate_responsive and asset.local_path:
            responsive_variants = await self._generate_responsive_variants(Path(asset.local_path), asset)
            if responsive_variants:
                asset.responsive_variants = responsive_variants
        
        return asset
    
    async def _process_single_document(self, asset: AssetReference, article_context: Optional[Dict] = None) -> AssetReference:
        """Process a single document asset."""
        original_url = asset.original_url
        
        # Handle CDN URL optimization
        if self._is_document360_url(original_url):
            asset.optimized_url = self._optimize_d360_document_url(original_url)
        
        # Download if configured to do so
        if self.download_external_assets and asset.is_external:
            downloaded_path = await self._download_asset(asset, self.documents_dir)
            if downloaded_path:
                asset.local_path = str(downloaded_path)
                asset.optimized_url = self._generate_asset_url(downloaded_path)
        
        return asset
    
    async def _download_asset(self, asset: AssetReference, target_dir: Path) -> Optional[Path]:
        """Download asset to local storage."""
        if not self._http_client:
            return None
        
        try:
            logger.debug(f"Downloading asset: {asset.original_url}")
            response = await self._http_client.get(asset.original_url)
            response.raise_for_status()
            
            # Determine filename
            filename = self._generate_filename(asset.original_url, response.headers.get('content-type'))
            file_path = target_dir / filename
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Update asset metadata
            asset.file_size = len(response.content)
            asset.mime_type = response.headers.get('content-type')
            
            logger.debug(f"Downloaded asset to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to download asset {asset.original_url}: {e}")
            return None
    
    async def _optimize_image(self, image_path: Path, asset: AssetReference) -> Optional[Path]:
        """Optimize image file."""
        if not IMAGING_AVAILABLE:
            return image_path
        
        try:
            with Image.open(image_path) as img:
                # Store original dimensions
                asset.dimensions = img.size
                original_size = image_path.stat().st_size
                
                # Apply optimizations
                optimized_img = img.copy()
                
                # Resize if too large
                if img.width > self.max_image_width:
                    ratio = self.max_image_width / img.width
                    new_height = int(img.height * ratio)
                    optimized_img = optimized_img.resize((self.max_image_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert format if configured
                output_path = image_path
                output_format = img.format
                
                if self.convert_to_webp and img.format != 'WebP':
                    output_path = image_path.with_suffix('.webp')
                    output_format = 'WebP'
                
                # Save optimized image
                save_kwargs = {'optimize': True}
                if output_format in ['JPEG', 'WebP']:
                    save_kwargs['quality'] = self.image_quality
                
                optimized_img.save(output_path, format=output_format, **save_kwargs)
                
                # Record optimization stats
                optimized_size = output_path.stat().st_size
                self.optimization_stats[str(image_path)] = OptimizationResult(
                    original_size=original_size,
                    optimized_size=optimized_size,
                    compression_ratio=(original_size - optimized_size) / original_size,
                    format_changed=output_format != img.format,
                    original_format=img.format,
                    optimized_format=output_format
                )
                
                logger.debug(f"Optimized image: {image_path} -> {output_path} ({original_size} -> {optimized_size} bytes)")
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to optimize image {image_path}: {e}")
            return image_path
    
    async def _generate_responsive_variants(self, image_path: Path, asset: AssetReference) -> List[str]:
        """Generate responsive image variants."""
        if not IMAGING_AVAILABLE:
            return []
        
        try:
            variants = []
            breakpoints = [480, 768, 1024]  # Common responsive breakpoints
            
            with Image.open(image_path) as img:
                for breakpoint in breakpoints:
                    if img.width <= breakpoint:
                        continue
                    
                    # Generate variant filename
                    variant_name = f"{image_path.stem}_{breakpoint}w{image_path.suffix}"
                    variant_path = image_path.parent / variant_name
                    
                    # Resize image
                    ratio = breakpoint / img.width
                    new_height = int(img.height * ratio)
                    variant_img = img.resize((breakpoint, new_height), Image.Resampling.LANCZOS)
                    
                    # Save variant
                    save_kwargs = {'optimize': True}
                    if img.format in ['JPEG', 'WebP']:
                        save_kwargs['quality'] = self.image_quality
                    
                    variant_img.save(variant_path, **save_kwargs)
                    variant_url = self._generate_asset_url(variant_path)
                    variants.append(f"{variant_url} {breakpoint}w")
                    
                    logger.debug(f"Generated responsive variant: {variant_path}")
            
            return variants
            
        except Exception as e:
            logger.error(f"Failed to generate responsive variants for {image_path}: {e}")
            return []
    
    def _optimize_d360_image_url(self, url: str) -> str:
        """Optimize Document360 image URL with CDN parameters."""
        if not self._is_document360_url(url):
            return url
        
        # Add optimization parameters to Document360 URLs
        separator = '&' if '?' in url else '?'
        optimizations = []
        
        if self.max_image_width < 1920:
            optimizations.append(f"w={self.max_image_width}")
        
        if self.image_quality < 95:
            optimizations.append(f"q={self.image_quality}")
        
        if self.convert_to_webp:
            optimizations.append("fm=webp")
        
        if optimizations:
            url += separator + '&'.join(optimizations)
        
        return url
    
    def _optimize_d360_document_url(self, url: str) -> str:
        """Optimize Document360 document URL."""
        # For documents, we typically don't modify URLs much
        # But we could add download parameters or CDN optimization
        return url
    
    def _generate_filename(self, url: str, content_type: Optional[str] = None) -> str:
        """Generate appropriate filename from URL."""
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        if path and '.' in Path(path).name:
            # Use original filename
            filename = Path(path).name
        else:
            # Generate filename from URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            
            # Determine extension from content type
            extension = '.bin'  # Default
            if content_type:
                ext = mimetypes.guess_extension(content_type)
                if ext:
                    extension = ext
            
            filename = f"asset_{url_hash}{extension}"
        
        # Sanitize filename
        filename = re.sub(r'[^\w\-_.]', '_', filename)
        return filename
    
    def _generate_asset_url(self, file_path: Path) -> str:
        """Generate URL for asset file."""
        # Generate relative path from docs directory
        try:
            relative_path = file_path.relative_to(self.output_dir.parent)
        except ValueError:
            relative_path = file_path.relative_to(self.output_dir)
        
        # Convert to URL format
        url_path = str(relative_path).replace('\\', '/')
        
        # Add CDN prefix if configured
        if self.cdn_prefix:
            return f"{self.cdn_prefix}/{url_path}"
        
        return url_path
    
    def _is_external_url(self, url: str) -> bool:
        """Check if URL is external."""
        return url.startswith(('http://', 'https://'))
    
    def _is_document360_url(self, url: str) -> bool:
        """Check if URL is a Document360 CDN URL."""
        return 'document360' in url.lower() and ('cdn' in url.lower() or 'assets' in url.lower())
    
    def get_asset_report(self) -> Dict[str, Any]:
        """Generate comprehensive asset processing report."""
        total_assets = len(self.processed_assets)
        optimized_assets = sum(1 for asset in self.processed_assets.values() if asset.optimization_applied)
        broken_assets = len(self.broken_assets)
        
        # Calculate optimization savings
        total_savings = 0
        for result in self.optimization_stats.values():
            total_savings += result.original_size - result.optimized_size
        
        return {
            'summary': {
                'total_assets_processed': total_assets,
                'assets_optimized': optimized_assets,
                'broken_assets': broken_assets,
                'total_size_saved_bytes': total_savings,
                'average_compression_ratio': sum(r.compression_ratio for r in self.optimization_stats.values()) / len(self.optimization_stats) if self.optimization_stats else 0,
            },
            'optimization_stats': {
                str(path): {
                    'original_size': result.original_size,
                    'optimized_size': result.optimized_size,
                    'compression_ratio': result.compression_ratio,
                    'format_changed': result.format_changed,
                }
                for path, result in self.optimization_stats.items()
            },
            'broken_assets': [
                {
                    'url': asset.original_url,
                    'type': asset.asset_type,
                    'is_external': asset.is_external,
                }
                for asset in self.broken_assets
            ],
            'asset_types': {
                asset_type: len([a for a in self.processed_assets.values() if a.asset_type == asset_type])
                for asset_type in set(asset.asset_type for asset in self.processed_assets.values())
            }
        }
    
    # Phase 2: Social Cards Generation Methods
    
    async def _generate_social_card(self, article_context: Dict[str, Any], content: str) -> Optional[AssetReference]:
        """Generate a social card for the article.
        
        Args:
            article_context: Article metadata and context
            content: Article content for description extraction
            
        Returns:
            AssetReference for the generated social card, or None if generation failed
        """
        if not self.generate_social_cards or not self.social_cards_dir:
            return None
        
        try:
            article_id = article_context.get('id', 'unknown')
            article_title = article_context.get('title', 'Untitled')
            article_description = self._extract_social_description(content, article_context)
            
            # Check cache first
            cache_key = f"{article_id}_{hash(article_title + article_description)}"
            if self.enable_social_card_caching and cache_key in self.social_cards_cache:
                cached_card = self.social_cards_cache[cache_key]
                logger.debug(f"Using cached social card for article: {article_title}")
                return AssetReference(
                    original_url=cached_card['url'],
                    asset_type='social_card',
                    local_path=cached_card['path'],
                    optimized_url=cached_card['url']
                )
            
            # Generate social card image
            card_path = await self._create_social_card_image(
                title=article_title,
                description=article_description,
                article_context=article_context,
                cache_key=cache_key
            )
            
            if card_path:
                # Generate URL for the social card
                card_url = self._generate_asset_url(card_path)
                
                # Cache the result
                if self.enable_social_card_caching:
                    self.social_cards_cache[cache_key] = {
                        'url': card_url,
                        'path': str(card_path),
                        'title': article_title,
                        'description': article_description,
                        'generated_at': asyncio.get_event_loop().time()
                    }
                
                # Track the generated social card
                self.social_cards_generated[article_id] = str(card_path)
                
                logger.debug(f"Generated social card for article: {article_title}")
                
                return AssetReference(
                    original_url=card_url,
                    asset_type='social_card',
                    local_path=str(card_path),
                    optimized_url=card_url,
                    dimensions=self.social_card_size
                )
            
        except Exception as e:
            logger.error(f"Failed to generate social card for article '{article_context.get('title', 'Unknown')}': {e}")
        
        return None
    
    def _extract_social_description(self, content: str, article_context: Dict[str, Any]) -> str:
        """Extract description for social card from content.
        
        Args:
            content: Article content
            article_context: Article metadata
            
        Returns:
            Description text for social card
        """
        # Try to get description from article context first
        if 'description' in article_context and article_context['description']:
            return article_context['description'][:150]
        
        # Extract first paragraph from content
        # Remove markdown formatting
        clean_content = re.sub(r'[#*`\[\]()!]', '', content)
        clean_content = re.sub(r'\n+', ' ', clean_content)
        
        # Take first sentence or 150 characters
        sentences = re.split(r'[.!?]+', clean_content)
        if sentences and len(sentences[0]) > 20:
            description = sentences[0].strip()
        else:
            description = clean_content[:150].strip()
        
        # Ensure we have a reasonable description
        if len(description) < 20:
            description = f"Learn about {article_context.get('title', 'this topic')} in our comprehensive guide."
        
        return description[:150] + ('...' if len(description) > 150 else '')
    
    async def _create_social_card_image(
        self,
        title: str,
        description: str,
        article_context: Dict[str, Any],
        cache_key: str
    ) -> Optional[Path]:
        """Create the actual social card image.
        
        Args:
            title: Article title
            description: Article description
            article_context: Article metadata
            cache_key: Cache key for the image
            
        Returns:
            Path to the generated image file
        """
        if not IMAGING_AVAILABLE or not SOCIAL_CARDS_AVAILABLE:
            return None
        
        try:
            # Create image with specified dimensions
            width, height = self.social_card_size
            img = Image.new('RGB', (width, height), self.social_card_background_color)
            draw = ImageDraw.Draw(img)
            
            # Load fonts
            title_font = self._load_font(size=48)
            description_font = self._load_font(size=24)
            brand_font = self._load_font(size=18)
            
            # Define layout parameters
            padding = 60
            content_width = width - (padding * 2)
            
            # Draw background pattern/gradient if using material template
            if self.social_card_template == "material":
                self._draw_material_background(draw, width, height)
            
            # Draw logo if provided
            logo_height = 0
            if self.social_card_logo_path and Path(self.social_card_logo_path).exists():
                logo_height = self._draw_logo(draw, Path(self.social_card_logo_path), padding, padding, max_height=80)
            
            # Calculate positions
            title_y = padding + logo_height + (20 if logo_height > 0 else 0)
            
            # Draw title (wrapped)
            title_lines = self._wrap_text(title, content_width, title_font, draw)
            current_y = title_y
            
            for line in title_lines:
                draw.text((padding, current_y), line, fill=self.social_card_text_color, font=title_font)
                current_y += title_font.getsize(line)[1] + 5
            
            # Draw description (wrapped)
            description_y = current_y + 30
            description_lines = self._wrap_text(description, content_width, description_font, draw)
            
            for line in description_lines[:3]:  # Max 3 lines for description
                draw.text((padding, description_y), line, fill=self._lighten_color(self.social_card_text_color), font=description_font)
                description_y += description_font.getsize(line)[1] + 3
            
            # Draw brand/site name at bottom
            brand_text = article_context.get('site_name', 'Documentation')
            brand_y = height - padding - brand_font.getsize(brand_text)[1]
            draw.text((padding, brand_y), brand_text, fill=self.social_card_accent_color, font=brand_font)
            
            # Draw accent line
            line_width = 4
            line_y = brand_y - 20
            draw.rectangle([padding, line_y, padding + 100, line_y + line_width], fill=self.social_card_accent_color)
            
            # Save image
            filename = f"social_card_{cache_key}.png"
            card_path = self.social_cards_dir / filename
            
            img.save(card_path, format='PNG', optimize=True)
            
            logger.debug(f"Created social card image: {card_path}")
            return card_path
            
        except Exception as e:
            logger.error(f"Failed to create social card image: {e}")
            return None
    
    def _load_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load font for text rendering.
        
        Args:
            size: Font size
            
        Returns:
            Font object
        """
        try:
            if self.social_card_font_family:
                return ImageFont.truetype(self.social_card_font_family, size)
            else:
                # Try to load a system font
                font_paths = [
                    "/System/Library/Fonts/Arial.ttf",  # macOS
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                    "C:/Windows/Fonts/arial.ttf",  # Windows
                ]
                
                for font_path in font_paths:
                    if Path(font_path).exists():
                        return ImageFont.truetype(font_path, size)
                
                # Fallback to default font
                return ImageFont.load_default()
        except Exception:
            # Fallback to default font
            return ImageFont.load_default()
    
    def _wrap_text(self, text: str, max_width: int, font: ImageFont.FreeTypeFont, draw: ImageDraw.Draw) -> List[str]:
        """Wrap text to fit within specified width.
        
        Args:
            text: Text to wrap
            max_width: Maximum width in pixels
            font: Font to use for measurement
            draw: ImageDraw object for text measurement
            
        Returns:
            List of text lines that fit within max_width
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_width = draw.textsize(test_line, font=font)[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, break it
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _draw_material_background(self, draw: ImageDraw.Draw, width: int, height: int) -> None:
        """Draw Material Design inspired background.
        
        Args:
            draw: ImageDraw object
            width: Image width
            height: Image height
        """
        # Draw subtle geometric shapes
        accent_color_light = self._lighten_color(self.social_card_accent_color, 0.9)
        
        # Draw circles in corners
        circle_size = 120
        circle_alpha = 20
        
        # Create overlay for shapes
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Top right circle
        overlay_draw.ellipse(
            [width - circle_size, -circle_size//2, width + circle_size//2, circle_size//2],
            fill=(*self._hex_to_rgb(accent_color_light), circle_alpha)
        )
        
        # Bottom left circle  
        overlay_draw.ellipse(
            [-circle_size//2, height - circle_size//2, circle_size//2, height + circle_size//2],
            fill=(*self._hex_to_rgb(accent_color_light), circle_alpha)
        )
        
        # Convert overlay to RGB and paste
        base = Image.new('RGB', (width, height), self.social_card_background_color)
        composite = Image.alpha_composite(base.convert('RGBA'), overlay)
        draw._image.paste(composite.convert('RGB'))
    
    def _draw_logo(self, draw: ImageDraw.Draw, logo_path: Path, x: int, y: int, max_height: int = 80) -> int:
        """Draw logo on social card.
        
        Args:
            draw: ImageDraw object
            logo_path: Path to logo image
            x: X position
            y: Y position
            max_height: Maximum height for logo
            
        Returns:
            Actual height of drawn logo
        """
        try:
            logo_img = Image.open(logo_path)
            
            # Resize logo to fit max_height while maintaining aspect ratio
            logo_width, logo_height = logo_img.size
            if logo_height > max_height:
                ratio = max_height / logo_height
                new_width = int(logo_width * ratio)
                logo_img = logo_img.resize((new_width, max_height), Image.Resampling.LANCZOS)
                logo_height = max_height
            
            # Convert to RGB if needed
            if logo_img.mode in ('RGBA', 'LA', 'P'):
                logo_img = logo_img.convert('RGB')
            
            # Paste logo
            draw._image.paste(logo_img, (x, y))
            
            return logo_height
            
        except Exception as e:
            logger.warning(f"Failed to load logo from {logo_path}: {e}")
            return 0
    
    def _lighten_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Lighten a hex color.
        
        Args:
            hex_color: Hex color string
            factor: Lightening factor (0.0 to 1.0)
            
        Returns:
            Lightened hex color
        """
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r, g, b = self._hex_to_rgb(hex_color)
        
        # Lighten
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple.
        
        Args:
            hex_color: Hex color string
            
        Returns:
            RGB tuple
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_social_cards_report(self) -> Dict[str, Any]:
        """Get report on generated social cards.
        
        Returns:
            Dictionary with social cards statistics
        """
        if not self.generate_social_cards:
            return {'enabled': False}
        
        return {
            'enabled': True,
            'cards_generated': len(self.social_cards_generated),
            'cached_cards': len(self.social_cards_cache),
            'template': self.social_card_template,
            'dimensions': f"{self.social_card_size[0]}x{self.social_card_size[1]}",
            'background_color': self.social_card_background_color,
            'text_color': self.social_card_text_color,
            'accent_color': self.social_card_accent_color,
            'generated_cards': [
                {
                    'article_id': article_id,
                    'path': path,
                    'url': self._generate_asset_url(Path(path)) if Path(path).exists() else None
                }
                for article_id, path in self.social_cards_generated.items()
            ]
        }
    
    async def cleanup(self):
        """Clean up resources."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None