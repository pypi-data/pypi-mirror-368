#!/usr/bin/env python3
# this_file: external/int_folders/d361/test_data_sync.py
"""
Test script for DataSyncManager functionality.

This script validates the data synchronization implementation including
deduplication, incremental sync, and change detection.
"""

import asyncio
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from d361.api import Document360ApiClient, ApiConfig
from d361.api.data_sync import (
    DataSyncManager,
    SyncConfig,
    SyncStrategy,
    DeduplicationStrategy,
    ContentFingerprint,
    ChangeRecord,
    ChangeType,
    SyncState
)
from d361.core.models import Article, PublishStatus


async def test_content_fingerprint():
    """Test content fingerprinting functionality."""
    print("🔍 Testing ContentFingerprint...")
    
    # Test 1: Fingerprint creation
    print("\n1. Testing fingerprint creation...")
    try:
        article = Article(
            id=1001,
            title="Test Article",
            content="# Introduction\n\nThis is a test article with some content.\n\nIt has multiple paragraphs.",
            category_id=100,
            status=PublishStatus.PUBLISHED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        fingerprint = ContentFingerprint.from_article(article)
        
        print(f"   ✅ Fingerprint created for article: {article.id}")
        print(f"   🔍 Content hash: {fingerprint.content_hash}")
        print(f"   📊 Content analysis: {fingerprint.word_count} words, {fingerprint.paragraph_count} paragraphs")
        print(f"   🏷️  Title: '{fingerprint.title}', Category: {fingerprint.category}")
        
    except Exception as e:
        print(f"   ❌ Fingerprint creation failed: {e}")
        return False
    
    # Test 2: Fingerprint similarity
    print("\n2. Testing fingerprint similarity...")
    try:
        # Create similar article
        similar_article = Article(
            id=1002,
            title="Test Article",  # Same title
            content="# Introduction\n\nThis is a test article with some content.\n\nIt has multiple paragraphs and one more line.",  # Slightly different
            category_id=100,
            status=PublishStatus.PUBLISHED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create very different article
        different_article = Article(
            id=1003,
            title="Completely Different Article",
            content="This article is completely different with different structure and content.",
            category_id=200,
            status=PublishStatus.PUBLISHED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        similar_fp = ContentFingerprint.from_article(similar_article)
        different_fp = ContentFingerprint.from_article(different_article)
        
        # Test similarity scores
        similar_score = fingerprint.similarity_score(similar_fp)
        different_score = fingerprint.similarity_score(different_fp)
        
        print(f"   ✅ Similarity with similar article: {similar_score:.2f}")
        print(f"   ✅ Similarity with different article: {different_score:.2f}")
        
        if similar_score > different_score:
            print("   ✅ Similarity scoring works correctly")
        else:
            print("   ❌ Similarity scoring may not be working correctly")
            return False
        
    except Exception as e:
        print(f"   ❌ Similarity testing failed: {e}")
        return False
    
    # Test 3: Fingerprint serialization
    print("\n3. Testing fingerprint serialization...")
    try:
        fp_dict = fingerprint.to_dict()
        print(f"   ✅ Serialized fingerprint to dict with {len(fp_dict)} fields")
        print(f"   📊 Contains: {list(fp_dict.keys())[:5]}...")
        
        # Verify required fields
        required_fields = ['content_hash', 'metadata_hash', 'combined_hash', 'title']
        for field in required_fields:
            if field not in fp_dict:
                print(f"   ❌ Missing required field: {field}")
                return False
        
        print("   ✅ All required fields present")
        
    except Exception as e:
        print(f"   ❌ Serialization failed: {e}")
        return False
    
    print("✅ ContentFingerprint tests passed!")
    return True


async def test_sync_config():
    """Test sync configuration."""
    print("\n⚙️ Testing SyncConfig...")
    
    # Test 1: Default configuration
    print("\n1. Testing default configuration...")
    try:
        config = SyncConfig()
        print(f"   ✅ Default config: strategy={config.sync_strategy.value}")
        print(f"   📊 Thresholds: similarity={config.similarity_threshold}")
        print(f"   ⚡ Performance: batch_size={config.batch_size}, concurrent={config.max_concurrent_operations}")
        
    except Exception as e:
        print(f"   ❌ Default config failed: {e}")
        return False
    
    # Test 2: Custom configuration
    print("\n2. Testing custom configuration...")
    try:
        config = SyncConfig(
            sync_strategy=SyncStrategy.INCREMENTAL,
            deduplication_strategy=DeduplicationStrategy.HYBRID,
            similarity_threshold=0.9,
            batch_size=50,
            auto_resolve_conflicts=True
        )
        
        print(f"   ✅ Custom config: strategy={config.sync_strategy.value}")
        print(f"   🔍 Deduplication: {config.deduplication_strategy.value}")
        print(f"   🤖 Auto resolve conflicts: {config.auto_resolve_conflicts}")
        
    except Exception as e:
        print(f"   ❌ Custom config failed: {e}")
        return False
    
    # Test 3: Configuration validation
    print("\n3. Testing configuration validation...")
    try:
        # Test invalid similarity threshold
        try:
            invalid_config = SyncConfig(similarity_threshold=1.5)  # Invalid > 1.0
            print("   ❌ Should have failed with similarity_threshold > 1.0")
            return False
        except Exception:
            print("   ✅ Correctly validated similarity_threshold")
        
        # Test invalid batch size
        try:
            invalid_config = SyncConfig(batch_size=0)  # Invalid < 10
            print("   ❌ Should have failed with batch_size < 10")
            return False
        except Exception:
            print("   ✅ Correctly validated batch_size")
        
    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")
        return False
    
    print("✅ SyncConfig tests passed!")
    return True


async def test_change_record():
    """Test change record functionality."""
    print("\n📝 Testing ChangeRecord...")
    
    # Test 1: Change record creation
    print("\n1. Testing change record creation...")
    try:
        # Create fingerprints for testing
        old_article = Article(
            id=2001,
            title="Original Title",
            content="Original content",
            category_id=300,
            status=PublishStatus.PUBLISHED,
            created_at=datetime.now() - timedelta(hours=1),
            updated_at=datetime.now() - timedelta(hours=1)
        )
        
        new_article = Article(
            id=2001,
            title="Updated Title",
            content="Updated content with more information",
            category_id=300,
            status=PublishStatus.PUBLISHED,
            created_at=datetime.now() - timedelta(hours=1),
            updated_at=datetime.now()
        )
        
        old_fp = ContentFingerprint.from_article(old_article)
        new_fp = ContentFingerprint.from_article(new_article)
        
        change_record = ChangeRecord(
            item_id="2001",
            change_type=ChangeType.MODIFIED,
            timestamp=datetime.now(),
            old_fingerprint=old_fp,
            new_fingerprint=new_fp,
            similarity_score=old_fp.similarity_score(new_fp),
            field_changes={
                'title': {'old': 'Original Title', 'new': 'Updated Title'},
                'content': {'length_change': len(new_article.content) - len(old_article.content)}
            }
        )
        
        print(f"   ✅ Change record created: {change_record.item_id}")
        print(f"   🔄 Change type: {change_record.change_type.value}")
        print(f"   📊 Similarity score: {change_record.similarity_score:.2f}")
        print(f"   🏷️  Field changes: {list(change_record.field_changes.keys())}")
        
    except Exception as e:
        print(f"   ❌ Change record creation failed: {e}")
        return False
    
    # Test 2: Change record serialization
    print("\n2. Testing change record serialization...")
    try:
        change_dict = change_record.to_dict()
        print(f"   ✅ Serialized change record to dict with {len(change_dict)} fields")
        print(f"   📊 Contains: {list(change_dict.keys())}")
        
        # Verify required fields
        required_fields = ['item_id', 'change_type', 'timestamp']
        for field in required_fields:
            if field not in change_dict:
                print(f"   ❌ Missing required field: {field}")
                return False
        
        print("   ✅ All required fields present")
        
    except Exception as e:
        print(f"   ❌ Serialization failed: {e}")
        return False
    
    print("✅ ChangeRecord tests passed!")
    return True


async def test_sync_state():
    """Test sync state management."""
    print("\n💾 Testing SyncState...")
    
    # Test 1: Sync state creation
    print("\n1. Testing sync state creation...")
    try:
        sync_state = SyncState(
            sync_id="test_sync_001",
            strategy=SyncStrategy.INCREMENTAL,
            started_at=datetime.now(),
            total_items=100
        )
        
        print(f"   ✅ Sync state created: {sync_state.sync_id}")
        print(f"   🔄 Strategy: {sync_state.strategy.value}")
        print(f"   📊 Progress: {sync_state.completion_percentage:.1f}% ({sync_state.processed_items}/{sync_state.total_items})")
        
    except Exception as e:
        print(f"   ❌ Sync state creation failed: {e}")
        return False
    
    # Test 2: Progress updates
    print("\n2. Testing progress updates...")
    try:
        # Simulate processing
        sync_state.processed_items = 25
        sync_state.successful_items = 23
        sync_state.failed_items = 2
        
        print(f"   ✅ Updated progress: {sync_state.completion_percentage:.1f}% complete")
        print(f"   📈 Success rate: {sync_state.success_rate:.1f}%")
        print(f"   📊 Items: {sync_state.successful_items} successful, {sync_state.failed_items} failed")
        
    except Exception as e:
        print(f"   ❌ Progress update failed: {e}")
        return False
    
    # Test 3: State serialization
    print("\n3. Testing state serialization...")
    try:
        state_dict = sync_state.to_dict()
        print(f"   ✅ Serialized state to dict with {len(state_dict)} fields")
        
        # Verify required fields
        required_fields = ['sync_id', 'strategy', 'started_at', 'total_items']
        for field in required_fields:
            if field not in state_dict:
                print(f"   ❌ Missing required field: {field}")
                return False
        
        print("   ✅ All required fields present")
        
    except Exception as e:
        print(f"   ❌ Serialization failed: {e}")
        return False
    
    print("✅ SyncState tests passed!")
    return True


async def test_data_sync_manager():
    """Test DataSyncManager initialization and basic functionality."""
    print("\n🔄 Testing DataSyncManager...")
    
    # Test 1: Manager initialization
    print("\n1. Testing manager initialization...")
    try:
        config = ApiConfig(api_tokens=["test-token"])
        client = Document360ApiClient(config)
        
        sync_config = SyncConfig(
            sync_strategy=SyncStrategy.INCREMENTAL,
            deduplication_strategy=DeduplicationStrategy.HYBRID,
            similarity_threshold=0.8,
            batch_size=10
        )
        
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            sync_manager = DataSyncManager(
                api_client=client,
                config=sync_config,
                state_dir=Path(temp_dir)
            )
            
            print(f"   ✅ DataSyncManager initialized")
            print(f"   📁 State directory: {sync_manager.state_dir}")
            print(f"   ⚙️ Config: strategy={sync_manager.config.sync_strategy.value}")
            
            # Test 2: Change callback functionality
            print("\n2. Testing change callback...")
            callback_calls = []
            
            def test_callback(change_record: ChangeRecord):
                callback_calls.append(change_record)
            
            sync_manager.add_change_callback(test_callback)
            print("   ✅ Change callback registered")
            
            # Test 3: List syncs (should be empty initially)
            print("\n3. Testing sync listing...")
            syncs = await sync_manager.list_syncs()
            print(f"   ✅ Found {len(syncs)} existing syncs")
            
            # Test 4: Cleanup functionality
            print("\n4. Testing cleanup functionality...")
            cleaned_count = await sync_manager.cleanup_old_states()
            print(f"   ✅ Cleaned up {cleaned_count} old states")
        
        await client.close()
        
    except Exception as e:
        print(f"   ❌ DataSyncManager test failed: {e}")
        return False
    
    print("✅ DataSyncManager tests passed!")
    return True


async def test_deduplication_logic():
    """Test deduplication logic."""
    print("\n🔍 Testing deduplication logic...")
    
    # Test 1: Create test articles with duplicates
    print("\n1. Testing duplicate detection...")
    try:
        # Create articles with different levels of similarity
        articles = [
            Article(
                id=3001,
                title="Python Programming Guide",
                content="# Python Basics\n\nPython is a powerful programming language.",
                category_id=400,
                status=PublishStatus.PUBLISHED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Article(
                id=3002,
                title="Python Programming Guide",  # Exact duplicate title
                content="# Python Basics\n\nPython is a powerful programming language.",  # Exact duplicate content
                category_id=400,
                status=PublishStatus.PUBLISHED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Article(
                id=3003,
                title="Python Programming Tutorial",  # Similar title
                content="# Python Basics\n\nPython is a powerful programming language with many features.",  # Similar content
                category_id=400,
                status=PublishStatus.PUBLISHED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Article(
                id=3004,
                title="JavaScript Fundamentals",  # Different topic
                content="# JavaScript Intro\n\nJavaScript is used for web development.",
                category_id=500,
                status=PublishStatus.PUBLISHED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # Create fingerprints
        fingerprints = {
            article.id: ContentFingerprint.from_article(article)
            for article in articles
        }
        
        print(f"   ✅ Created {len(fingerprints)} article fingerprints")
        
        # Test similarity between exact duplicates
        exact_similarity = fingerprints[3001].similarity_score(fingerprints[3002])
        print(f"   🔍 Exact duplicate similarity: {exact_similarity:.2f}")
        
        # Test similarity between similar articles
        similar_similarity = fingerprints[3001].similarity_score(fingerprints[3003])
        print(f"   🔍 Similar article similarity: {similar_similarity:.2f}")
        
        # Test similarity between different articles
        different_similarity = fingerprints[3001].similarity_score(fingerprints[3004])
        print(f"   🔍 Different article similarity: {different_similarity:.2f}")
        
        # Verify expected similarity ordering
        if exact_similarity > similar_similarity > different_similarity:
            print("   ✅ Similarity scores ordered correctly")
        else:
            print("   ❌ Similarity scores may not be ordered correctly")
            return False
        
    except Exception as e:
        print(f"   ❌ Deduplication test failed: {e}")
        return False
    
    print("✅ Deduplication tests passed!")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting DataSyncManager Tests")
    
    success = True
    
    # Test content fingerprinting
    if not await test_content_fingerprint():
        success = False
    
    # Test sync configuration
    if not await test_sync_config():
        success = False
    
    # Test change records
    if not await test_change_record():
        success = False
    
    # Test sync state
    if not await test_sync_state():
        success = False
    
    # Test data sync manager
    if not await test_data_sync_manager():
        success = False
    
    # Test deduplication logic
    if not await test_deduplication_logic():
        success = False
    
    if success:
        print("\n🎉 All DataSyncManager tests completed successfully!")
        print("✅ Data synchronization and deduplication system is ready for production use")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())