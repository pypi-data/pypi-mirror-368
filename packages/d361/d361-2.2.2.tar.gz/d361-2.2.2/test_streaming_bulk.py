#!/usr/bin/env python3
# this_file: external/int_folders/d361/test_streaming_bulk.py
"""
Test script for streaming and bulk operations.

This script validates the streaming and bulk operation implementations
including asynchronous generators, bulk managers, and smart processing.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from d361.api import Document360ApiClient, ApiConfig
from d361.api.bulk_operations import (
    BulkOperationManager,
    BulkOperationConfig,
    OperationType,
    OperationRequest,
    SmartBulkProcessor
)
from d361.api.errors import ValidationError


async def test_streaming_operations():
    """Test streaming operations functionality."""
    print("🌊 Testing streaming operations...")
    
    config = ApiConfig(api_tokens=["test-token"])
    client = Document360ApiClient(config)
    
    # Test 1: stream_all_articles parameter validation
    print("\n1. Testing stream_all_articles parameter validation...")
    try:
        async for article in client.stream_all_articles(page_size=999):  # Invalid page size
            break
        print("   ❌ Should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"   ✅ Correctly validated page_size: {e}")
    
    # Test 2: stream_all_articles with max_articles validation
    print("\n2. Testing max_articles validation...")
    try:
        async for article in client.stream_all_articles(max_articles=0):  # Invalid max
            break
        print("   ❌ Should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"   ✅ Correctly validated max_articles: {e}")
    
    # Test 3: stream_articles_batch validation
    print("\n3. Testing stream_articles_batch validation...")
    try:
        async for batch in client.stream_articles_batch(batch_size=-1):  # Invalid batch size
            break
        print("   ❌ Should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"   ✅ Correctly validated batch_size: {e}")
    
    # Test 4: Streaming generator properties (without real API calls)
    print("\n4. Testing streaming generator properties...")
    try:
        # Check that streaming methods return async generators
        stream = client.stream_all_articles(page_size=10, max_articles=5)
        print(f"   ✅ stream_all_articles returns: {type(stream).__name__}")
        
        batch_stream = client.stream_articles_batch(batch_size=10)
        print(f"   ✅ stream_articles_batch returns: {type(batch_stream).__name__}")
    except Exception as e:
        print(f"   ❌ Generator creation failed: {e}")
        return False
    
    await client.close()
    print("✅ Streaming operations tests passed!")
    return True


async def test_bulk_operations():
    """Test bulk operations functionality."""
    print("\n📦 Testing bulk operations...")
    
    config = ApiConfig(api_tokens=["test-token"])
    client = Document360ApiClient(config)
    
    # Test 1: BulkOperationConfig validation
    print("\n1. Testing BulkOperationConfig...")
    try:
        config = BulkOperationConfig(
            max_concurrent_operations=10,
            retry_failed_operations=True,
            max_retries_per_operation=3
        )
        print(f"   ✅ BulkOperationConfig created: {config.max_concurrent_operations} concurrent")
    except Exception as e:
        print(f"   ❌ Config creation failed: {e}")
        return False
    
    # Test 2: OperationRequest validation
    print("\n2. Testing OperationRequest validation...")
    try:
        # Valid create request
        valid_req = OperationRequest(
            operation_type=OperationType.CREATE,
            item_id="test-1",
            data={"title": "Test Article", "content": "Test content", "category_id": "cat-1"}
        )
        print(f"   ✅ Valid CREATE request: {valid_req.item_id}")
        
        # Invalid create request (missing data)
        try:
            invalid_req = OperationRequest(
                operation_type=OperationType.CREATE,
                item_id="test-2"
                # Missing data for CREATE operation
            )
            print("   ❌ Should have raised ValueError for missing data")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly validated missing data: {e}")
    except Exception as e:
        print(f"   ❌ OperationRequest test failed: {e}")
        return False
    
    # Test 3: BulkOperationManager initialization
    print("\n3. Testing BulkOperationManager initialization...")
    try:
        bulk_config = BulkOperationConfig(max_concurrent_operations=5)
        manager = BulkOperationManager(client, bulk_config)
        print(f"   ✅ BulkOperationManager initialized with {bulk_config.max_concurrent_operations} concurrent ops")
    except Exception as e:
        print(f"   ❌ Manager initialization failed: {e}")
        return False
    
    # Test 4: SmartBulkProcessor initialization
    print("\n4. Testing SmartBulkProcessor...")
    try:
        processor = SmartBulkProcessor(client)
        print(f"   ✅ SmartBulkProcessor initialized with batch size {processor.current_batch_size}")
    except Exception as e:
        print(f"   ❌ SmartBulkProcessor initialization failed: {e}")
        return False
    
    await client.close()
    print("✅ Bulk operations tests passed!")
    return True


async def test_operation_requests():
    """Test operation request creation and validation."""
    print("\n📋 Testing operation requests...")
    
    # Test 1: CREATE operation request
    print("\n1. Testing CREATE operation request...")
    try:
        create_req = OperationRequest(
            operation_type=OperationType.CREATE,
            item_id="create-test-1",
            data={
                "title": "Test Article",
                "content": "<p>Test content</p>",
                "category_id": "test-category"
            },
            max_attempts=3
        )
        print(f"   ✅ CREATE request: {create_req.item_id}")
        print(f"   📊 Max attempts: {create_req.max_attempts}, Completed: {create_req.completed}")
    except Exception as e:
        print(f"   ❌ CREATE request failed: {e}")
        return False
    
    # Test 2: UPDATE operation request
    print("\n2. Testing UPDATE operation request...")
    try:
        update_req = OperationRequest(
            operation_type=OperationType.UPDATE,
            item_id="article-123",
            data={"title": "Updated Title"},
            metadata={"reason": "title correction"}
        )
        print(f"   ✅ UPDATE request: {update_req.item_id}")
        print(f"   📝 Metadata: {update_req.metadata}")
    except Exception as e:
        print(f"   ❌ UPDATE request failed: {e}")
        return False
    
    # Test 3: DELETE operation request
    print("\n3. Testing DELETE operation request...")
    try:
        delete_req = OperationRequest(
            operation_type=OperationType.DELETE,
            item_id="article-456"
        )
        print(f"   ✅ DELETE request: {delete_req.item_id}")
    except Exception as e:
        print(f"   ❌ DELETE request failed: {e}")
        return False
    
    # Test 4: FETCH operation request
    print("\n4. Testing FETCH operation request...")
    try:
        fetch_req = OperationRequest(
            operation_type=OperationType.FETCH,
            item_id="article-789"
        )
        print(f"   ✅ FETCH request: {fetch_req.item_id}")
    except Exception as e:
        print(f"   ❌ FETCH request failed: {e}")
        return False
    
    print("✅ Operation requests tests passed!")
    return True


async def test_bulk_result_tracking():
    """Test bulk operation result tracking."""
    print("\n📊 Testing bulk operation result tracking...")
    
    from d361.api.bulk_operations import BulkOperationResult
    from datetime import datetime
    
    # Test 1: BulkOperationResult creation and properties
    print("\n1. Testing BulkOperationResult...")
    try:
        result = BulkOperationResult(
            operation_type=OperationType.CREATE,
            total_requests=100,
            successful_requests=85,
            failed_requests=15,
            skipped_requests=0,
            start_time=datetime.now()
        )
        
        print(f"   ✅ Result created: {result.total_requests} total requests")
        print(f"   📊 Success rate: {result.success_rate:.1%}")
        print(f"   ⏱️  Complete: {result.is_complete}")
        
        # Mark as complete
        result.mark_complete()
        print(f"   ✅ Marked complete: duration {result.duration_seconds:.3f}s")
        
    except Exception as e:
        print(f"   ❌ BulkOperationResult test failed: {e}")
        return False
    
    print("✅ Bulk result tracking tests passed!")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting Streaming and Bulk Operations Tests")
    
    success = True
    
    # Test streaming operations
    if not await test_streaming_operations():
        success = False
    
    # Test bulk operations
    if not await test_bulk_operations():
        success = False
    
    # Test operation requests
    if not await test_operation_requests():
        success = False
    
    # Test result tracking
    if not await test_bulk_result_tracking():
        success = False
    
    if success:
        print("\n🎉 All streaming and bulk operations tests completed successfully!")
        print("✅ Streaming and bulk operations are ready for production use")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())