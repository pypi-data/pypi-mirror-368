# Test Fixtures

This directory contains high-value test data migrated from legacy Document360 implementations during Phase 9 consolidation (2025-08-08).

## Directory Structure

### `vexy-lines-archive/`
Complete real-world Document360 archive from Vexy Lines documentation:
- **`Vexy-Lines-2025-Mar-12-04-42-07.zip`**: Complete production archive with 1000+ files
- Use for integration testing, archive parsing validation, and performance benchmarking

### `markdown_samples/`
Representative markdown articles extracted from the Vexy Lines archive:
- **`about-this-guide.md`**: Introduction/guide type article
- **`adding-a-fill.md`**: How-to tutorial article  
- **`actions-6.md`**: Feature documentation article
- Use for markdown parsing, content conversion testing, and validation

## Data Directory

### `../data/`
- **`v1_categories_articles.json`**: 532KB structured JSON metadata from complete Vexy Lines export
- Contains categories hierarchy, articles metadata, and complete Document360 structure
- Use for performance testing, data model validation, and parser benchmarking

## Schemas Directory

### `../schemas/`
- **`d361.schema.json`**: JSON schema validation patterns for d361 configuration
- Use for configuration validation and schema testing

## Templates Directory

### `../templates/`
Configuration templates extracted from legacy implementations:
- **`d361.toml.example`**: Complete project configuration template
- **`d361api.toml.example`**: API client configuration examples
- Use for setup documentation and configuration validation

## Usage Notes

This test data represents:
- **Real-world production content** from FontLab's Vexy Lines documentation
- **Complete Document360 export structure** with all metadata
- **Diverse content types**: guides, tutorials, API docs, feature documentation
- **Large-scale data** for performance and scalability testing

## Migration Source

Migrated from:
- `external/int_folders/d362c/example/` (production archive and samples)
- `external/int_folders/d362c/` (configuration templates)

All migrated during Phase 9 consolidation to preserve valuable test data before cleanup.