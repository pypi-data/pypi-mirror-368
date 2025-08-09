#!/usr/bin/env python3
# this_file: external/int_folders/d361/example_api_usage.py
"""
Document360 API Client Usage Examples.

This script demonstrates how to use the Document360ApiClient for common
operations including article management, error handling, and token management.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from d361 import Document360ApiClient, ApiConfig
from d361 import Document360Error, AuthenticationError, ValidationError


async def example_basic_usage():
    """Demonstrate basic API client usage."""
    print("📝 Basic Document360 API Client Usage Example")
    
    # Configuration for API client
    config = ApiConfig(
        api_tokens=[
            "your-api-token-1",  # Replace with real tokens
            "your-api-token-2"   # Multiple tokens for load balancing
        ],
        base_url="https://apihub.document360.io/v1",
        timeout=30.0,
        max_retries=3,
        calls_per_minute=60,
        enable_caching=True
    )
    
    print(f"🔧 Configuration: {len(config.api_tokens)} tokens, timeout={config.timeout}s")
    
    # Create API client using async context manager
    async with Document360ApiClient(config) as client:
        print("✅ API client initialized successfully")
        
        try:
            # Example 1: List articles with pagination
            print("\n1️⃣ Listing articles...")
            articles_response = await client.list_articles(limit=10, offset=0)
            print(f"   Found {len(articles_response.get('data', []))} articles")
            
        except AuthenticationError as e:
            print(f"   ⚠️  Authentication failed: {e}")
            print("   💡 Please check your API tokens")
            
        except ValidationError as e:
            print(f"   ⚠️  Validation error: {e}")
            
        except Document360Error as e:
            print(f"   ❌ API error: {e}")
            print(f"   📊 Error details: {e.category.value} | {e.severity.value}")
            
        # Example 2: Get project versions
        try:
            print("\n2️⃣ Getting project versions...")
            versions = await client.get_project_versions()
            print(f"   Found {len(versions.get('data', []))} project versions")
            
        except Document360Error as e:
            print(f"   ❌ Failed to get project versions: {e}")
        
        # Example 3: Get categories
        try:
            print("\n3️⃣ Getting categories...")
            categories = await client.get_categories()
            print(f"   Found {len(categories.get('data', []))} categories")
            
        except Document360Error as e:
            print(f"   ❌ Failed to get categories: {e}")
        
        # Example 4: Demonstrate validation
        print("\n4️⃣ Testing input validation...")
        try:
            await client.get_article("")  # Invalid empty ID
        except ValidationError as e:
            print(f"   ✅ Validation caught invalid input: {e}")
        
        # Example 5: Health check and statistics
        print("\n5️⃣ Checking client health...")
        health = await client.health_check()
        print(f"   Client status: {health['client']['status']}")
        print(f"   Total requests: {health['client']['total_requests']}")
        print(f"   Success rate: {health['client']['success_rate']:.2%}")
        print(f"   Available tokens: {health['tokens']['healthy_tokens']}")


async def example_article_management():
    """Demonstrate article creation, update, and deletion."""
    print("\n📄 Article Management Example")
    
    config = ApiConfig(api_tokens=["your-api-token"])
    
    async with Document360ApiClient(config) as client:
        try:
            # Create a new article
            article_data = {
                "title": "Test Article from API",
                "content": "<h1>Hello World</h1><p>This is a test article created via API.</p>",
                "category_id": "your-category-id",  # Replace with real category ID
                "status": "draft"
            }
            
            print("📝 Creating new article...")
            new_article = await client.create_article(article_data)
            article_id = new_article["data"]["id"]
            print(f"   ✅ Created article with ID: {article_id}")
            
            # Update the article
            update_data = {
                "title": "Updated Test Article",
                "content": "<h1>Updated Content</h1><p>This article has been updated.</p>"
            }
            
            print(f"✏️  Updating article {article_id}...")
            updated_article = await client.update_article(article_id, update_data)
            print(f"   ✅ Article updated successfully")
            
            # Get the article to verify updates
            print(f"🔍 Retrieving article {article_id}...")
            retrieved_article = await client.get_article(article_id)
            print(f"   📄 Article title: {retrieved_article['data']['title']}")
            
            # Delete the article
            print(f"🗑️  Deleting article {article_id}...")
            deleted = await client.delete_article(article_id)
            if deleted:
                print("   ✅ Article deleted successfully")
            
        except ValidationError as e:
            print(f"   ❌ Validation error: {e}")
        except Document360Error as e:
            print(f"   ❌ API error: {e}")
            print(f"   📊 Error details: {e.category.value} | {e.severity.value}")


async def example_error_handling():
    """Demonstrate comprehensive error handling."""
    print("\n🚨 Error Handling Examples")
    
    config = ApiConfig(api_tokens=["invalid-token"])
    
    async with Document360ApiClient(config) as client:
        # Example 1: Authentication error
        print("\n1️⃣ Testing authentication error...")
        try:
            await client.get_project_versions()
        except AuthenticationError as e:
            print(f"   ✅ Caught authentication error: {e}")
            print(f"   📊 Severity: {e.severity.value} | Retryable: {e.retryable}")
        
        # Example 2: Not found error  
        print("\n2️⃣ Testing not found error...")
        try:
            await client.get_article("non-existent-id")
        except Exception as e:
            print(f"   ℹ️  Expected not found error: {type(e).__name__}")
        
        # Example 3: Validation errors
        print("\n3️⃣ Testing validation errors...")
        validation_tests = [
            ("Empty article ID", lambda: client.get_article("")),
            ("Invalid limit", lambda: client.list_articles(limit=999)),
            ("Negative offset", lambda: client.list_articles(offset=-1)),
            ("Empty article data", lambda: client.create_article({})),
        ]
        
        for test_name, test_func in validation_tests:
            try:
                await test_func()
            except ValidationError as e:
                print(f"   ✅ {test_name}: {e}")


async def example_token_management():
    """Demonstrate token management features."""
    print("\n🔑 Token Management Example")
    
    # Multiple tokens for load balancing
    config = ApiConfig(
        api_tokens=["token-1", "token-2", "token-3"],
        calls_per_minute=60
    )
    
    client = Document360ApiClient(config)
    
    # Get token health report
    health_report = client.token_manager.get_health_report()
    print(f"📊 Token Report:")
    print(f"   Total tokens: {health_report['total_tokens']}")
    print(f"   Healthy tokens: {health_report['healthy_tokens']}")
    print(f"   Available tokens: {client.token_manager.available_tokens_count}")
    
    # Demonstrate token selection
    print("\n🎯 Token selection process:")
    for i in range(3):
        token = await client.token_manager.get_best_token()
        if token:
            token_hash = f"***{token[-4:]}"
            print(f"   Selection {i+1}: {token_hash}")
        else:
            print(f"   Selection {i+1}: No tokens available")
    
    await client.close()


async def main():
    """Run all examples."""
    print("🚀 Document360 API Client Examples")
    print("=" * 50)
    
    await example_basic_usage()
    print("\n" + "=" * 50)
    
    await example_article_management()
    print("\n" + "=" * 50)
    
    await example_error_handling()
    print("\n" + "=" * 50)
    
    await example_token_management()
    print("\n" + "=" * 50)
    
    print("\n✨ Examples completed!")
    print("\n💡 Notes:")
    print("   - Replace 'your-api-token' with real Document360 API tokens")
    print("   - Replace 'your-category-id' with a real category ID")
    print("   - Some examples will fail without valid credentials (this is expected)")


if __name__ == "__main__":
    asyncio.run(main())