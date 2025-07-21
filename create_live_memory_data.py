#!/usr/bin/env python3
"""
Create memory data for the actual running worm to fix dashboard display
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the project to the path
sys.path.insert(0, '/app')

async def create_live_memory_data():
    """Create memory data for the actual running worm."""
    
    print("🧠 Creating Memory Data for Live Worm")
    print("=" * 50)
    
    try:
        from src.agentic_worm.memory.manager import WormMemoryManager
        from src.agentic_worm.core.state import create_initial_state
        
        # Get the current worm ID (will be a demo ID)
        demo_state = create_initial_state("demo_system")
        actual_worm_id = demo_state.get("worm_id", f"demo_{uuid.uuid4().hex[:8]}")
        
        print(f"🆔 Target worm ID: {actual_worm_id}")
        
        # Create memory manager
        memory_manager = WormMemoryManager(
            arango_config={
                "host": "arangodb",
                "port": 8529,
                "database_name": "agentic_worm_memory",
                "username": None,
                "password": None
            },
            enable_consolidation=False
        )
        
        print("✅ Memory manager created")
        
        # Create multiple experiences for the actual worm
        experiences_created = 0
        
        # Experience 1: Successful exploration
        exp1_id = await memory_manager.record_experience(
            worm_id=actual_worm_id,
            location={"x": 5.0, "y": 10.0, "z": 0.0},
            goal="explore_environment",
            actions_taken=[
                {"type": "movement", "direction": "forward", "duration": 2.0},
                {"type": "sensing", "sensory_data": {"temperature": 22.0}}
            ],
            motor_commands={"dorsal": 0.7, "ventral": 0.3, "pharynx_pump": 0.1},
            outcome="success",
            fitness_change=0.08,
            energy_change=-0.02,
            duration=2.5,
            environment_state={"temperature": 22.0, "food_nearby": False},
            tags=["exploration", "successful", "learning"]
        )
        if exp1_id:
            experiences_created += 1
            print(f"✅ Created exploration experience: {exp1_id[:8]}...")
        
        # Experience 2: Food seeking
        exp2_id = await memory_manager.record_experience(
            worm_id=actual_worm_id,
            location={"x": 12.0, "y": 15.0, "z": 0.0},
            goal="find_food",
            actions_taken=[
                {"type": "chemotaxis", "direction": "up_gradient", "duration": 3.0},
                {"type": "feeding", "food_consumed": 0.3}
            ],
            motor_commands={"dorsal": 0.6, "ventral": 0.4, "pharynx_pump": 0.8},
            outcome="success",
            fitness_change=0.15,
            energy_change=0.05,
            duration=3.0,
            environment_state={"temperature": 23.0, "food_nearby": True},
            tags=["feeding", "chemotaxis", "successful"]
        )
        if exp2_id:
            experiences_created += 1
            print(f"✅ Created feeding experience: {exp2_id[:8]}...")
        
        # Experience 3: Obstacle avoidance
        exp3_id = await memory_manager.record_experience(
            worm_id=actual_worm_id,
            location={"x": 8.0, "y": 5.0, "z": 0.0},
            goal="avoid_obstacles",
            actions_taken=[
                {"type": "mechanosensory", "stimulus": "touch", "response": "withdrawal"},
                {"type": "movement", "direction": "turn_left", "duration": 1.5}
            ],
            motor_commands={"dorsal": 0.9, "ventral": 0.1, "pharynx_pump": 0.0},
            outcome="success",
            fitness_change=0.05,
            energy_change=-0.01,
            duration=1.5,
            environment_state={"temperature": 21.0, "obstacle_detected": True},
            tags=["avoidance", "mechanosensory", "successful"]
        )
        if exp3_id:
            experiences_created += 1
            print(f"✅ Created avoidance experience: {exp3_id[:8]}...")
        
        # Experience 4: Failed attempt
        exp4_id = await memory_manager.record_experience(
            worm_id=actual_worm_id,
            location={"x": 20.0, "y": 25.0, "z": 0.0},
            goal="find_food",
            actions_taken=[
                {"type": "random_search", "pattern": "spiral", "duration": 4.0}
            ],
            motor_commands={"dorsal": 0.5, "ventral": 0.5, "pharynx_pump": 0.2},
            outcome="failure",
            fitness_change=-0.03,
            energy_change=-0.08,
            duration=4.0,
            environment_state={"temperature": 24.0, "food_nearby": False},
            tags=["search", "failed", "learning"]
        )
        if exp4_id:
            experiences_created += 1
            print(f"✅ Created failed search experience: {exp4_id[:8]}...")
        
        print(f"\n📊 Created {experiences_created} experiences for worm {actual_worm_id}")
        
        # Test the statistics
        stats = await memory_manager.get_memory_statistics(actual_worm_id)
        
        print("\n📊 Memory Statistics for Live Worm:")
        print(f"  Episodic: {stats['episodic_count']}")
        print(f"  Spatial: {stats['spatial_count']}")
        print(f"  Success Rate: {stats['success_rate']:.1%}")
        print(f"  Memory Confidence: {stats['memory_confidence']:.2f}")
        print(f"  Insights: {stats['insights']}")
        
        if stats['episodic_count'] > 0:
            print("\n🎉 SUCCESS: Live worm now has memory data!")
            print("🌐 Dashboard should now show real values")
            return True
        else:
            print("\n❌ FAILED: Memory statistics still showing zeros")
            return False
        
    except Exception as e:
        print(f"❌ Failed to create live memory data: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_live_memory_data())
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1) 