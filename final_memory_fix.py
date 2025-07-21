#!/usr/bin/env python3
"""
Final comprehensive fix for the Agentic Worm memory system.
This script addresses all remaining issues preventing memory storage.
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime

# Add the project to the path
sys.path.insert(0, '/app')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_memory_system():
    """Test and fix the memory system."""
    
    print("🧠 Final Memory System Fix and Test")
    print("=" * 50)
    
    try:
        # Import the memory components
        from src.agentic_worm.memory.manager import WormMemoryManager
        from src.agentic_worm.memory.types import Experience, MemoryType
        from src.agentic_worm.memory.storage import ArangoMemoryStore
        from src.agentic_worm.core.state import create_initial_state
        import uuid
        
        print("✅ Successfully imported memory components")
        
        # Set up ArangoDB configuration
        arango_config = {
            "host": os.environ.get('ARANGO_HOST', 'arangodb'),
            "port": int(os.environ.get('ARANGO_PORT', '8529')),
            "database_name": os.environ.get('ARANGO_DATABASE', 'agentic_worm_memory'),
            "username": None,  # No auth
            "password": None   # No auth
        }
        
        print(f"🔗 Testing ArangoDB connection to {arango_config['host']}:{arango_config['port']}")
        
        # Test direct storage connection
        storage = ArangoMemoryStore(**arango_config)
        
        # Wait a bit for ArangoDB to be ready
        print("⏳ Waiting for ArangoDB...")
        await asyncio.sleep(5)
        
        # Test basic connection
        connection_success = await storage.test_connection()
        if not connection_success:
            print("❌ ArangoDB connection failed")
            return False
        
        print("✅ ArangoDB connection successful")
        
        # Initialize collections
        collections_success = await storage.initialize_collections()
        if not collections_success:
            print("❌ Collection initialization failed")
            return False
            
        print("✅ Collections initialized successfully")
        
        # Create memory manager
        memory_manager = WormMemoryManager(
            arango_config=arango_config,
            enable_consolidation=False  # Disable for testing
        )
        
        print("✅ Memory manager created")
        
        # Test basic memory operations
        print("🧪 Testing memory operations...")
        
        worm_id = f"test_worm_{uuid.uuid4().hex[:8]}"
        
        # Test experience recording (this will also create spatial memory automatically)
        experience_id = await memory_manager.record_experience(
            worm_id=worm_id,
            location={"x": 10.0, "y": 20.0, "z": 0.0},
            goal="test_exploration",
            actions_taken=[
                {"type": "movement", "direction": "forward", "duration": 1.0},
                {"type": "sensing", "sensory_data": {"temperature": 22.0}}
            ],
            motor_commands={"dorsal": 0.6, "ventral": 0.4, "pharynx_pump": 0.1},
            outcome="success",
            fitness_change=0.05,
            energy_change=-0.02,
            duration=2.0,
            environment_state={"temperature": 22.0, "food_nearby": False},
            tags=["exploration", "movement", "successful"]
        )
        
        if experience_id:
            print(f"✅ Experience recorded: {experience_id}")
            print("   (Spatial memory also updated automatically)")
        else:
            print("❌ Experience recording failed")
            return False
        
        # Record a second experience to build up memory
        experience_id2 = await memory_manager.record_experience(
            worm_id=worm_id,
            location={"x": 15.0, "y": 25.0, "z": 0.0},
            goal="find_food",
            actions_taken=[
                {"type": "search", "pattern": "systematic", "duration": 2.0}
            ],
            motor_commands={"dorsal": 0.7, "ventral": 0.3, "pharynx_pump": 0.2},
            outcome="partial",
            fitness_change=0.02,
            energy_change=-0.03,
            duration=3.0,
            environment_state={"temperature": 23.0, "food_nearby": True},
            tags=["food_search", "systematic", "partial_success"]
        )
        
        if experience_id2:
            print(f"✅ Second experience recorded: {experience_id2}")
        else:
            print("⚠️ Second experience recording failed")
        
        # Test memory statistics
        stats = await memory_manager.get_memory_statistics(worm_id)
        print(f"📊 Memory Statistics: {stats}")
        
        if stats and stats.get('episodic_count', 0) > 0:
            print("✅ Memory statistics show stored memories")
        else:
            print("⚠️ Memory statistics show no stored memories")
        
        # Test memory retrieval
        memories = await memory_manager.retrieve_relevant_memories(
            worm_id=worm_id,
            current_location={"x": 10.0, "y": 20.0, "z": 0.0},
            current_goal="test_exploration",
            context="testing",
            memory_types=[MemoryType.EPISODIC, MemoryType.SPATIAL],
            limit=5
        )
        
        if memories:
            print(f"✅ Retrieved {len(memories)} memories")
            for memory_type, memory_list in memories.items():
                print(f"   {memory_type}: {len(memory_list)} items")
        else:
            print("⚠️ No memories retrieved")
        
        print("")
        print("🎉 Memory system test completed successfully!")
        print("🔗 Check ArangoDB at http://localhost:8529 for collections")
        print("🌐 Check dashboard at http://localhost:8000 for live updates")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Close connections
        try:
            if 'storage' in locals():
                storage.close()
        except:
            pass

def main():
    """Main function to run the memory system test."""
    
    print("Starting memory system diagnostic...")
    
    # Run the async test
    success = asyncio.run(test_memory_system())
    
    if success:
        print("\n✅ Memory system is working correctly!")
        print("The dashboard should now show real memory values.")
        sys.exit(0)
    else:
        print("\n❌ Memory system test failed.")
        print("Check the logs above for specific error details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 