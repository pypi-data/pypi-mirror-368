#!/usr/bin/env python3
# this_file: external/int_folders/d361/scripts/process_d360_archive.py
"""
Standalone script to process Document360 offline archives.

This script provides a CLI interface for processing Document360 offline
archives, extracting content, indexing with SQLite, and managing the cache.

Usage:
    python process_d360_archive.py [COMMAND] [OPTIONS]

Commands:
    parse       Parse an archive and extract content
    index       Index archive content in SQLite database
    search      Search indexed archive content
    cache       Manage archive cache
    schema      Database schema operations

Examples:
    # Parse an archive
    python process_d360_archive.py parse --archive_path my_docs.zip
    
    # Index content with full-text search
    python process_d360_archive.py index --archive_path my_docs.zip --enable_fts
    
    # Search indexed content
    python process_d360_archive.py search --query "installation guide"
    
    # Cache management
    python process_d360_archive.py cache stats
    python process_d360_archive.py cache cleanup
"""

import sys
import asyncio
from pathlib import Path

# Add the src directory to the path so we can import d361
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))


async def parse_archive(
    archive_path: str,
    output_format: str = "json",
    verbose: bool = False
):
    """Parse a Document360 archive."""
    from d361.archive import ArchiveParser, ArchiveParserConfig
    
    archive_path = Path(archive_path)
    
    if not archive_path.exists():
        print(f"❌ Archive file not found: {archive_path}")
        return
    
    print(f"📁 Parsing archive: {archive_path}")
    
    # Configure parser
    config = ArchiveParserConfig(
        extract_text_content=True,
        extract_metadata=True,
        validate_json=True
    )
    
    parser = ArchiveParser(config)
    
    try:
        # Parse the archive
        parsed_archive = await parser.parse_archive(archive_path)
        
        print(f"✅ Archive parsed successfully!")
        print(f"   📊 Statistics:")
        print(f"      Total entries: {parsed_archive.metadata.total_entries}")
        print(f"      Processed: {parsed_archive.metadata.processed_entries}")
        print(f"      Failed: {parsed_archive.metadata.failed_entries}")
        print(f"      Articles: {parsed_archive.metadata.articles_count}")
        print(f"      Categories: {parsed_archive.metadata.categories_count}")
        print(f"      Processing time: {parsed_archive.metadata.processing_time_seconds:.2f}s")
        print(f"      Success rate: {parsed_archive.success_rate:.2%}")
        
        if verbose:
            print(f"\n   📂 Archive Structure:")
            print(f"      Root directories: {parsed_archive.metadata.root_directories}")
            print(f"      File extensions: {parsed_archive.metadata.file_extensions}")
        
        if output_format == "json":
            import json
            output_file = archive_path.with_suffix('.parsed.json')
            with open(output_file, 'w') as f:
                json.dump(parsed_archive.dict(), f, indent=2, default=str)
            print(f"   💾 Results saved to: {output_file}")
        
        # Show sample entries if verbose
        if verbose and parsed_archive.entries:
            print(f"\n   📄 Sample Entries:")
            for entry in parsed_archive.entries[:3]:
                print(f"      - {entry.path} ({entry.content_type}, {entry.size} bytes)")
        
    except Exception as e:
        print(f"❌ Failed to parse archive: {e}")
        if verbose:
            import traceback
            traceback.print_exc()


async def index_archive(
    archive_path: str,
    db_path: str = None,
    enable_fts: bool = True,
    enable_cache: bool = True
):
    """Index archive content in SQLite database."""
    from d361.archive import ArchiveParser, SqliteCache, create_archive_schema, ArchiveSchema
    
    archive_path = Path(archive_path)
    
    if not archive_path.exists():
        print(f"❌ Archive file not found: {archive_path}")
        return
    
    # Configure database path
    if db_path is None:
        db_path = Path.home() / ".d361" / "archives" / f"{archive_path.stem}.db"
    else:
        db_path = Path(db_path)
    
    print(f"🗃️  Indexing archive: {archive_path}")
    print(f"   Database: {db_path}")
    
    try:
        # Create schema
        schema_config = ArchiveSchema(enable_fts=enable_fts)
        await create_archive_schema(db_path, schema_config)
        print(f"   ✅ Database schema created")
        
        # Initialize cache if enabled
        cache = None
        if enable_cache:
            from d361.archive import CacheConfig
            cache_config = CacheConfig(db_path=db_path.parent / "cache.db")
            cache = SqliteCache(cache_config)
            await cache.start()
            print(f"   ✅ Cache initialized")
        
        # Parse archive
        parser = ArchiveParser()
        parsed_archive = await parser.parse_archive(archive_path)
        print(f"   ✅ Archive parsed ({parsed_archive.metadata.processed_entries} entries)")
        
        # TODO: Index content in database
        # This would involve inserting parsed content into the SQLite tables
        print(f"   ⚠️  Database indexing not yet implemented")
        
        if cache:
            await cache.stop()
        
        print(f"✅ Archive indexing completed!")
        
    except Exception as e:
        print(f"❌ Failed to index archive: {e}")


async def search_content(query: str, db_path: str = None, limit: int = 10):
    """Search indexed archive content."""
    print(f"🔍 Searching for: '{query}'")
    
    # TODO: Implement search functionality
    print(f"   ⚠️  Search functionality not yet implemented")


async def manage_cache(action: str, cache_path: str = None):
    """Manage archive cache."""
    from d361.archive import SqliteCache, CacheConfig
    
    if cache_path:
        config = CacheConfig(db_path=Path(cache_path))
    else:
        config = CacheConfig()
    
    cache = SqliteCache(config)
    
    try:
        await cache.start()
        
        if action == "stats":
            stats = await cache.get_stats()
            print(f"📊 Cache Statistics:")
            print(f"   Entries: {stats.entry_count}")
            print(f"   Total size: {stats.total_size / 1024 / 1024:.2f} MB")
            print(f"   Hit rate: {stats.hit_rate:.2%}")
            print(f"   Miss rate: {stats.miss_rate:.2%}")
            print(f"   Hits: {stats.hits}")
            print(f"   Misses: {stats.misses}")
            print(f"   Evictions: {stats.evictions}")
            
        elif action == "cleanup":
            cleaned = await cache.cleanup_expired()
            print(f"🧹 Cleaned up {cleaned} expired entries")
            
        elif action == "clear":
            await cache.clear()
            print(f"🗑️  Cache cleared")
            
        else:
            print(f"❌ Unknown cache action: {action}")
            print(f"   Available actions: stats, cleanup, clear")
        
    finally:
        await cache.stop()


async def manage_schema(action: str, db_path: str = None):
    """Manage database schema."""
    from d361.archive import create_archive_schema, migrate_archive_schema, get_schema_info
    
    if db_path is None:
        db_path = Path.home() / ".d361" / "archives" / "default.db"
    else:
        db_path = Path(db_path)
    
    if action == "create":
        await create_archive_schema(db_path)
        print(f"✅ Schema created: {db_path}")
        
    elif action == "migrate":
        await migrate_archive_schema(db_path)
        print(f"✅ Schema migrated: {db_path}")
        
    elif action == "info":
        info = await get_schema_info(db_path)
        print(f"📋 Schema Information:")
        print(f"   Database: {info['db_path']}")
        print(f"   Version: {info['version']}")
        print(f"   Size: {info['db_size'] / 1024 / 1024:.2f} MB")
        print(f"   Tables: {len(info['tables'])}")
        print(f"   FTS tables: {len(info['fts_tables'])}")
        print(f"   Indexes: {len(info['indexes'])}")
        
        if info.get('tables'):
            print(f"   📊 Tables: {', '.join(info['tables'])}")
        
    else:
        print(f"❌ Unknown schema action: {action}")
        print(f"   Available actions: create, migrate, info")


def main():
    """Main CLI interface."""
    import fire
    
    class ArchiveProcessorCLI:
        """CLI interface for Document360 archive processing."""
        
        def parse(
            self,
            archive_path: str,
            output_format: str = "json",
            verbose: bool = False
        ):
            """Parse a Document360 archive."""
            return asyncio.run(parse_archive(archive_path, output_format, verbose))
        
        def index(
            self,
            archive_path: str,
            db_path: str = None,
            enable_fts: bool = True,
            enable_cache: bool = True
        ):
            """Index archive content in SQLite database."""
            return asyncio.run(index_archive(archive_path, db_path, enable_fts, enable_cache))
        
        def search(self, query: str, db_path: str = None, limit: int = 10):
            """Search indexed archive content."""
            return asyncio.run(search_content(query, db_path, limit))
        
        def cache(self, action: str, cache_path: str = None):
            """Manage archive cache (stats, cleanup, clear)."""
            return asyncio.run(manage_cache(action, cache_path))
        
        def schema(self, action: str, db_path: str = None):
            """Manage database schema (create, migrate, info)."""
            return asyncio.run(manage_schema(action, db_path))
    
    fire.Fire(ArchiveProcessorCLI)


if __name__ == "__main__":
    main()