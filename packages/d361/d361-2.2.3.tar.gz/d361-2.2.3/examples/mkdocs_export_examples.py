#!/usr/bin/env python3
"""
MkDocs Export Examples

Quick reference examples for using the d361 MkDocs export functionality.
Run any example by calling: python mkdocs_export_examples.py <example_name>
"""
# this_file: external/int_folders/d361/examples/mkdocs_export_examples.py

import asyncio
from pathlib import Path
from typing import Dict, Any
import sys

from d361.mkdocs import MkDocsExporter, ConfigGenerator
from d361.mkdocs.processors import ContentEnhancer, AssetManager


async def basic_archive_export():
    """Basic export from Document360 archive to MkDocs."""
    print("🚀 Basic Archive Export Example")
    
    exporter = MkDocsExporter(
        source="archive",
        archive_path=Path("docs-archive.zip"),
        output_path=Path("basic_mkdocs_site"),
        theme="material"
    )
    
    results = await exporter.export()
    
    if results["success"]:
        print(f"✅ Export successful!")
        print(f"📁 Output: {results['output_path']}")
        print(f"📊 Processed {results['statistics']['articles_processed']} articles")
    else:
        print("❌ Export failed")


async def api_export():
    """Export from Document360 API."""
    print("🌐 API Export Example")
    
    exporter = MkDocsExporter(
        source="api",
        api_token="your-document360-api-token",
        output_path=Path("api_mkdocs_site"),
        theme="material",
        parallel_processing=True
    )
    
    results = await exporter.export()
    print(f"API Export completed: {results['success']}")


async def custom_configuration():
    """Generate custom MkDocs configuration."""
    print("⚙️ Custom Configuration Example")
    
    generator = ConfigGenerator(theme="material", enable_plugins=True)
    
    # Generate from template with custom context
    config = await generator.generate_config_from_template(
        "material_theme.yml.j2",
        {
            "site_name": "My Custom Documentation",
            "site_url": "https://docs.example.com",
            "primary_color": "teal",
            "accent_color": "orange",
            "enable_social_cards": True,
            "social": [
                {"icon": "fontawesome/brands/github", "link": "https://github.com/user/repo"},
                {"icon": "fontawesome/brands/twitter", "link": "https://twitter.com/user"}
            ],
            "analytics": {
                "provider": "google", 
                "property": "G-XXXXXXXXXX"
            }
        }
    )
    
    # Save configuration
    config_path = Path("custom_mkdocs.yml")
    config_path.write_text(config)
    print(f"📋 Custom configuration saved: {config_path}")
    
    # Validate configuration
    validation = generator.validate_final_config(config)
    if validation["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration errors:")
        for error in validation["errors"]:
            print(f"   - {error}")


async def content_enhancement():
    """Content enhancement example."""
    print("✨ Content Enhancement Example")
    
    from d361.core.models import Article
    
    # Sample article
    article = Article(
        id="example",
        title="Example Article",
        content="""# Getting Started

This is a sample article with [internal links](../guide.html) and ![images](image.png).

## Code Example

```python
def hello():
    print("Hello, World!")
```

Visit [our website](https://example.com) for more info.
""",
        category_id="guides"
    )
    
    # Create content enhancer
    enhancer = ContentEnhancer(
        site_url="https://docs.example.com",
        enable_seo=True,
        validate_links=True
    )
    
    # Enhance the article
    enhanced = await enhancer.enhance_article(article)
    
    print("📝 Enhanced Article Components:")
    print(f"   Frontmatter keys: {list(enhanced['frontmatter'].keys())}")
    print(f"   Quality score: {enhanced['quality_metrics']['overall_score']}")
    print(f"   Reading time: {enhanced['quality_metrics']['estimated_reading_time']} min")
    print(f"   Word count: {enhanced['quality_metrics']['word_count']}")


async def asset_processing():
    """Asset processing example."""
    print("🖼️ Asset Processing Example")
    
    # Create asset manager
    manager = AssetManager(
        output_dir=Path("assets"),
        enable_optimization=True,
        generate_responsive=True,
        convert_to_webp=True
    )
    
    # Sample content with images
    content = """
# Sample Content

Here are some images:

![Local Image](images/local.jpg)
![External Image](https://example.com/external.png)
![Document360 Image](https://d360-uploads.s3.amazonaws.com/sample.png)
"""
    
    processed_content = await manager.process_assets(content, "sample-article")
    print("🔄 Processed content:")
    print(processed_content[:200] + "..." if len(processed_content) > 200 else processed_content)


async def hybrid_export():
    """Hybrid export using both archive and API."""
    print("🔄 Hybrid Export Example")
    
    exporter = MkDocsExporter(
        source="hybrid",
        archive_path=Path("base-archive.zip"),
        api_token="your-api-token",
        output_path=Path("hybrid_site"),
        theme="material",
        parallel_processing=True,
        max_workers=4
    )
    
    results = await exporter.export()
    
    if results["success"]:
        print("✅ Hybrid export successful!")
        print(f"📈 Performance metrics:")
        for metric, value in results["performance"].items():
            print(f"   {metric}: {value}")
    else:
        print("❌ Hybrid export failed")


async def advanced_template_usage():
    """Advanced template usage with validation."""
    print("🔧 Advanced Template Usage Example")
    
    generator = ConfigGenerator()
    
    # Test different templates
    templates = {
        "basic": ("mkdocs_base.yml.j2", {
            "site_name": "Basic Site",
            "theme_name": "readthedocs"
        }),
        "material": ("material_theme.yml.j2", {
            "site_name": "Material Site",
            "primary_color": "indigo",
            "enable_social_cards": True
        })
    }
    
    for template_type, (template_name, context) in templates.items():
        print(f"\n📋 Testing {template_type} template:")
        
        try:
            config = await generator.generate_config_from_template(template_name, context)
            validation = generator.validate_final_config(config)
            
            if validation["valid"]:
                print(f"   ✅ {template_type} template: Valid")
            else:
                print(f"   ❌ {template_type} template: Invalid")
                for error in validation["errors"]:
                    print(f"      - {error}")
                    
        except Exception as e:
            print(f"   ⚠️ {template_type} template error: {e}")


async def performance_optimization():
    """Performance optimization example."""
    print("⚡ Performance Optimization Example")
    
    # High-performance configuration
    exporter = MkDocsExporter(
        source="archive",
        archive_path=Path("large-archive.zip"),
        output_path=Path("optimized_site"),
        theme="material",
        parallel_processing=True,
        max_workers=8  # Increase for better performance
    )
    
    print("🚀 Starting optimized export...")
    results = await exporter.export()
    
    if results["success"]:
        print("✅ Optimized export completed!")
        
        # Show performance metrics
        performance = results["performance"]
        print(f"📊 Performance Summary:")
        print(f"   Total time: {performance.get('total_export', 'N/A')}s")
        print(f"   Articles processed: {results['statistics']['articles_processed']}")
        print(f"   Processing rate: ~{results['statistics']['articles_processed'] / performance.get('total_export', 1):.1f} articles/sec")


async def validation_and_quality():
    """Validation and quality assurance example."""
    print("🔍 Validation and Quality Example")
    
    generator = ConfigGenerator()
    
    # Generate configuration
    config = await generator.generate_config(
        site_name="Quality Test Site",
        navigation=[{"Home": "index.md"}],
        output_path=Path("test_site")
    )
    
    # Comprehensive validation
    validation = generator.validate_final_config(config)
    
    print(f"📋 Validation Results:")
    print(f"   Valid: {validation['valid']}")
    print(f"   Errors: {len(validation['errors'])}")
    print(f"   Warnings: {len(validation['warnings'])}")
    print(f"   Suggestions: {len(validation['suggestions'])}")
    
    if validation["errors"]:
        print("❌ Errors found:")
        for error in validation["errors"]:
            print(f"   - {error}")
    
    if validation["warnings"]:
        print("⚠️ Warnings:")
        for warning in validation["warnings"]:
            print(f"   - {warning}")
            
    if validation["suggestions"]:
        print("💡 Suggestions:")
        for suggestion in validation["suggestions"]:
            print(f"   - {suggestion}")


# Example registry
EXAMPLES = {
    "basic": basic_archive_export,
    "api": api_export,
    "config": custom_configuration,
    "content": content_enhancement,
    "assets": asset_processing,
    "hybrid": hybrid_export,
    "templates": advanced_template_usage,
    "performance": performance_optimization,
    "validation": validation_and_quality
}


async def main():
    """Main function to run examples."""
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        if example_name in EXAMPLES:
            await EXAMPLES[example_name]()
        else:
            print(f"❌ Unknown example: {example_name}")
            print(f"Available examples: {', '.join(EXAMPLES.keys())}")
    else:
        print("📚 MkDocs Export Examples")
        print("=" * 50)
        print("Available examples:")
        for name, func in EXAMPLES.items():
            doc = func.__doc__ or "No description"
            print(f"  {name:12} - {doc}")
        print("\nUsage: python mkdocs_export_examples.py <example_name>")
        print("Example: python mkdocs_export_examples.py basic")


if __name__ == "__main__":
    asyncio.run(main())