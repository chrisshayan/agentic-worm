#!/usr/bin/env python3
"""
Debug script to test memory statistics method
"""

import asyncio
import sys
import os

# Add the project to the path
sys.path.insert(0, '/app')

async def debug_memory_stats():
    """Debug the memory statistics method."""
    
    print("🔍 Debugging Memory Statistics Method")
    print("=" * 50)
    
    try:
        from src.agentic_worm.memory.manager import WormMemoryManager
        from src.agentic_worm.memory.types import MemoryType
        
        print("✅ Imported memory components")
        
        # Create memory manager
        memory_manager = WormMemoryManager(
            arango_config={
                "host": os.environ.get('ARANGO_HOST', 'arangodb'),
                "port": int(os.environ.get('ARANGO_PORT', '8529')),
                "database_name": os.environ.get('ARANGO_DATABASE', 'agentic_worm_memory'),
                "username": None,
                "password": None
            },
            enable_consolidation=False
        )
        
        print("✅ Memory manager created")
        
        # Check storage and database connection
        if not memory_manager.storage:
            print("❌ Storage not initialized")
            return False
            
        if not memory_manager.storage.db:
            print("❌ Database not connected")
            return False
            
        print("✅ Storage and database connected")
        
        # Test direct database queries
        print("\n🔍 Testing direct database queries...")
        
        # List all collections
        try:
            collections = memory_manager.storage.db.collections()
            print(f"📋 Available collections: {[c['name'] for c in collections if not c['name'].startswith('_')]}")
        except Exception as e:
            print(f"❌ Failed to list collections: {e}")
            return False
        
        # Test each collection individually
        worm_id = "test_worm_395b710b"  # Use the same test worm ID
        
        for memory_type, collection_name in memory_manager.storage.collections.items():
            try:
                print(f"\n📊 Testing collection: {collection_name}")
                
                # Check if collection exists
                if not memory_manager.storage.db.has_collection(collection_name):
                    print(f"⚠️ Collection {collection_name} does not exist")
                    continue
                
                collection = memory_manager.storage.db.collection(collection_name)
                
                # Count all documents
                cursor1 = memory_manager.storage.db.aql.execute(
                    f"FOR doc IN {collection_name} COLLECT WITH COUNT INTO length RETURN length"
                )
                total_count = list(cursor1)[0] if cursor1 else 0
                print(f"   Total documents: {total_count}")
                
                # Count documents for specific worm
                cursor2 = memory_manager.storage.db.aql.execute(
                    f"FOR doc IN {collection_name} FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                worm_count = list(cursor2)[0] if cursor2 else 0
                print(f"   Documents for {worm_id}: {worm_count}")
                
                # Show sample documents
                if total_count > 0:
                    cursor3 = memory_manager.storage.db.aql.execute(
                        f"FOR doc IN {collection_name} LIMIT 1 RETURN doc"
                    )
                    sample = list(cursor3)
                    if sample:
                        print(f"   Sample document keys: {list(sample[0].keys())}")
                
            except Exception as e:
                print(f"❌ Error testing {collection_name}: {e}")
        
        # Test the statistics method
        print(f"\n📊 Testing statistics method for worm: {worm_id}")
        stats = await memory_manager.get_memory_statistics(worm_id)
        
        print("Statistics returned:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Check if we got real values
        if stats["episodic_count"] > 0 or stats["spatial_count"] > 0:
            print("\n✅ Statistics method is working - returning real values!")
            return True
        else:
            print("\n⚠️ Statistics method still returning zeros")
            
            # Additional debugging - check what's in the database directly
            print("\n🔍 Direct database check...")
            try:
                cursor = memory_manager.storage.db.aql.execute(
                    "FOR doc IN experiences LIMIT 5 RETURN {worm_id: doc.worm_id, goal: doc.goal, outcome: doc.outcome}"
                )
                docs = list(cursor)
                print(f"Sample experiences: {docs}")
            except Exception as e:
                print(f"Failed to query experiences directly: {e}")
                
            return False
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_memory_stats())
    print(f"\nDebug result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1) 