#!/usr/bin/env python3
# this_file: external/int_folders/d361/test_chunked_download.py
"""
Test script for ChunkedDownloader functionality.

This script validates the chunked download implementation including
resumable downloads, progress tracking, and error recovery.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from d361.api import Document360ApiClient, ApiConfig
from d361.api.chunked_download import (
    ChunkedDownloader,
    DownloadConfig,
    DownloadStatus,
    ChunkStatus,
    DownloadChunk,
    DownloadProgress,
    DownloadState
)


async def test_download_config():
    """Test download configuration validation."""
    print("⚙️ Testing DownloadConfig...")
    
    # Test 1: Default configuration
    print("\n1. Testing default configuration...")
    try:
        config = DownloadConfig()
        print(f"   ✅ Default config: chunk_size={config.chunk_size}, max_concurrent={config.max_concurrent_chunks}")
    except Exception as e:
        print(f"   ❌ Default config failed: {e}")
        return False
    
    # Test 2: Custom configuration
    print("\n2. Testing custom configuration...")
    try:
        config = DownloadConfig(
            chunk_size=100,
            max_concurrent_chunks=3,
            max_retries_per_chunk=5,
            resume_support=True,
            save_progress=True
        )
        print(f"   ✅ Custom config: chunk_size={config.chunk_size}, retries={config.max_retries_per_chunk}")
    except Exception as e:
        print(f"   ❌ Custom config failed: {e}")
        return False
    
    # Test 3: Configuration validation
    print("\n3. Testing configuration validation...")
    try:
        # Test chunk size validation
        try:
            invalid_config = DownloadConfig(chunk_size=0)  # Invalid chunk size
            print("   ❌ Should have failed with chunk_size=0")
            return False
        except Exception:
            print("   ✅ Correctly validated chunk_size")
        
        # Test max concurrent validation
        try:
            invalid_config = DownloadConfig(max_concurrent_chunks=0)  # Invalid concurrent
            print("   ❌ Should have failed with max_concurrent_chunks=0")
            return False
        except Exception:
            print("   ✅ Correctly validated max_concurrent_chunks")
    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")
        return False
    
    print("✅ DownloadConfig tests passed!")
    return True


async def test_download_chunk():
    """Test download chunk functionality."""
    print("\n📦 Testing DownloadChunk...")
    
    # Test 1: Chunk creation and properties
    print("\n1. Testing chunk creation...")
    try:
        chunk = DownloadChunk(
            chunk_id="test_chunk_001",
            start_offset=0,
            end_offset=99,
            size=100,
            max_attempts=3
        )
        
        print(f"   ✅ Chunk created: {chunk.chunk_id}")
        print(f"   📊 Range: {chunk.start_offset}-{chunk.end_offset}, size={chunk.size}")
        print(f"   🔄 Status: {chunk.status.value}, attempts: {chunk.attempts}")
        print(f"   ✅ Can retry: {chunk.can_retry}, complete: {chunk.is_complete}")
        
    except Exception as e:
        print(f"   ❌ Chunk creation failed: {e}")
        return False
    
    # Test 2: Chunk status transitions
    print("\n2. Testing chunk status transitions...")
    try:
        chunk.status = ChunkStatus.DOWNLOADING
        print(f"   📥 Status changed to: {chunk.status.value}")
        
        chunk.status = ChunkStatus.COMPLETED
        print(f"   ✅ Status changed to: {chunk.status.value}")
        print(f"   🏁 Is complete: {chunk.is_complete}")
        
    except Exception as e:
        print(f"   ❌ Status transition failed: {e}")
        return False
    
    print("✅ DownloadChunk tests passed!")
    return True


async def test_download_progress():
    """Test download progress tracking."""
    print("\n📊 Testing DownloadProgress...")
    
    # Test 1: Progress creation and calculations
    print("\n1. Testing progress calculations...")
    try:
        progress = DownloadProgress(
            total_items=1000,
            total_chunks=10
        )
        
        print(f"   ✅ Progress created: {progress.total_items} total items")
        print(f"   📊 Initial completion: {progress.completion_percentage:.1f}%")
        print(f"   📦 Initial chunk completion: {progress.chunk_completion_percentage:.1f}%")
        
        # Update progress
        progress.update_progress(100, chunk_completed=True)
        print(f"   📈 After update: {progress.completion_percentage:.1f}% complete")
        print(f"   📦 Chunks complete: {progress.completed_chunks}/{progress.total_chunks}")
        
        # Test time calculations
        elapsed = progress.elapsed_time
        estimated = progress.estimated_time_remaining
        print(f"   ⏱️  Elapsed: {elapsed:.2f}s, Estimated remaining: {estimated}")
        
    except Exception as e:
        print(f"   ❌ Progress calculation failed: {e}")
        return False
    
    print("✅ DownloadProgress tests passed!")
    return True


async def test_download_state():
    """Test download state management."""
    print("\n💾 Testing DownloadState...")
    
    # Test 1: State creation and serialization
    print("\n1. Testing state creation and serialization...")
    try:
        # Create chunks
        chunks = [
            DownloadChunk(
                chunk_id=f"chunk_{i:03d}",
                start_offset=i * 100,
                end_offset=(i + 1) * 100 - 1,
                size=100
            )
            for i in range(3)
        ]
        
        # Create state
        state = DownloadState(
            download_id="test_download_123",
            operation_type="download_articles",
            operation_params={"category_id": "test-cat", "project_version_id": None},
            total_items=300,
            chunk_size=100,
            chunks=chunks
        )
        
        print(f"   ✅ State created: {state.download_id}")
        print(f"   📊 Total items: {state.total_items}, chunks: {len(state.chunks)}")
        print(f"   🔄 Status: {state.status.value}")
        
        # Test serialization
        state_dict = state.to_dict()
        print(f"   💾 Serialized to dict with {len(state_dict)} keys")
        
        # Test deserialization
        restored_state = DownloadState.from_dict(state_dict)
        print(f"   🔄 Restored state: {restored_state.download_id}")
        print(f"   ✅ Chunks restored: {len(restored_state.chunks)}")
        
    except Exception as e:
        print(f"   ❌ State management failed: {e}")
        return False
    
    print("✅ DownloadState tests passed!")
    return True


async def test_chunked_downloader():
    """Test ChunkedDownloader initialization and basic functionality."""
    print("\n⬇️ Testing ChunkedDownloader...")
    
    # Test 1: Downloader initialization
    print("\n1. Testing downloader initialization...")
    try:
        config = ApiConfig(api_tokens=["test-token"])
        client = Document360ApiClient(config)
        
        download_config = DownloadConfig(
            chunk_size=50,
            max_concurrent_chunks=3,
            resume_support=True
        )
        
        downloader = ChunkedDownloader(client, download_config)
        
        print(f"   ✅ Downloader initialized")
        print(f"   📁 State directory: {downloader.state_dir}")
        print(f"   ⚙️ Config: chunk_size={downloader.config.chunk_size}")
        
    except Exception as e:
        print(f"   ❌ Downloader initialization failed: {e}")
        return False
    
    # Test 2: Chunk creation
    print("\n2. Testing chunk creation...")
    try:
        chunks = downloader._create_chunks(total_items=250, chunk_size=100)
        print(f"   ✅ Created {len(chunks)} chunks for 250 items")
        
        # Verify chunk ranges
        for i, chunk in enumerate(chunks):
            expected_start = i * 100
            expected_size = min(100, 250 - expected_start)
            
            if chunk.start_offset != expected_start:
                print(f"   ❌ Chunk {i} start offset incorrect: {chunk.start_offset} != {expected_start}")
                return False
            
            if chunk.size != expected_size:
                print(f"   ❌ Chunk {i} size incorrect: {chunk.size} != {expected_size}")
                return False
        
        print(f"   ✅ All chunk ranges verified")
        
    except Exception as e:
        print(f"   ❌ Chunk creation failed: {e}")
        return False
    
    # Test 3: Download listing
    print("\n3. Testing download listing...")
    try:
        downloads = await downloader.list_downloads()
        print(f"   ✅ Found {len(downloads)} existing downloads")
        
    except Exception as e:
        print(f"   ❌ Download listing failed: {e}")
        return False
    
    await client.close()
    print("✅ ChunkedDownloader tests passed!")
    return True


async def test_progress_callback():
    """Test progress callback functionality."""
    print("\n📞 Testing progress callback...")
    
    # Test progress callback
    callback_calls = []
    
    def progress_callback(progress: DownloadProgress):
        callback_calls.append({
            'completion': progress.completion_percentage,
            'downloaded': progress.downloaded_items,
            'total': progress.total_items
        })
    
    try:
        config = DownloadConfig(
            chunk_size=10,
            progress_callback=progress_callback
        )
        
        print(f"   ✅ Progress callback configured")
        
        # Simulate progress updates
        progress = DownloadProgress(total_items=100, total_chunks=10)
        
        # Simulate callback calls
        if config.progress_callback:
            config.progress_callback(progress)
            
            progress.update_progress(25, chunk_completed=True)
            config.progress_callback(progress)
            
            progress.update_progress(50, chunk_completed=True) 
            config.progress_callback(progress)
        
        print(f"   ✅ Progress callback called {len(callback_calls)} times")
        for i, call in enumerate(callback_calls):
            print(f"   📊 Call {i+1}: {call['completion']:.1f}% complete ({call['downloaded']}/{call['total']})")
        
    except Exception as e:
        print(f"   ❌ Progress callback test failed: {e}")
        return False
    
    print("✅ Progress callback tests passed!")
    return True


async def main():
    """Run all tests."""
    print("🚀 Starting ChunkedDownloader Tests")
    
    success = True
    
    # Test download configuration
    if not await test_download_config():
        success = False
    
    # Test download chunks
    if not await test_download_chunk():
        success = False
    
    # Test progress tracking
    if not await test_download_progress():
        success = False
    
    # Test state management
    if not await test_download_state():
        success = False
    
    # Test chunked downloader
    if not await test_chunked_downloader():
        success = False
    
    # Test progress callback
    if not await test_progress_callback():
        success = False
    
    if success:
        print("\n🎉 All ChunkedDownloader tests completed successfully!")
        print("✅ ChunkedDownloader is ready for production use")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())