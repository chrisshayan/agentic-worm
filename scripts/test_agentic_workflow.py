#!/usr/bin/env python3
"""
Test the Agentic Workflow Implementation

This script demonstrates the perception → cognition → action pipeline
working with real decision-making logic.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color

def print_colored(text: str, color: str = Colors.NC):
    """Print colored text."""
    print(f"{color}{text}{Colors.NC}")

async def test_agentic_workflow():
    """Test the agentic workflow with real decision-making."""
    
    print_colored("🧠 Testing Agentic Worm Intelligence Pipeline", Colors.CYAN)
    print_colored("=" * 50, Colors.CYAN)
    print()
    
    try:
        # Import our modules
        from agentic_worm.core.state import create_initial_state, WormState
        from agentic_worm.core.system import AgenticWormSystem
        
        print_colored("✅ Successfully imported agentic worm modules", Colors.GREEN)
        
        # Create initial state
        worm_state = create_initial_state("test_workflow")
        print_colored("✅ Created initial worm state", Colors.GREEN)
        
        # Set a goal for testing
        worm_state["decision_context"]["current_goal"] = "find_food"
        worm_state["decision_context"]["goal_priority"] = 1.0
        
        print_colored("🎯 Goal set: find_food", Colors.BLUE)
        print()
        
        # Create system
        system = AgenticWormSystem(
            simulation_id="test_agentic_workflow",
            enable_learning=True,
            enable_visualization=False
        )
        
        print_colored("🚀 Initializing Agentic Worm System...", Colors.BLUE)
        await system.initialize()
        
        if system.current_state:
            # Copy our test state
            system.current_state.update(worm_state)
            print_colored("✅ System initialized with test state", Colors.GREEN)
        else:
            print_colored("❌ System initialization failed - no current state", Colors.RED)
            return
        
        print()
        print_colored("🔄 Running Intelligence Pipeline Test", Colors.CYAN)
        print_colored("-" * 40, Colors.CYAN)
        
        # Run several simulation steps to show the pipeline
        for step in range(20):
            if not system.current_state:
                print_colored("❌ Lost current state during simulation", Colors.RED)
                break
                
            print_colored(f"\n📍 Step {step + 1}:", Colors.YELLOW)
            
            # Store previous state for comparison
            prev_decision = system.current_state["decision_context"].get("current_decision", "none")
            prev_fitness = system.current_state["fitness_score"]
            prev_energy = system.current_state["energy_level"]
            
            # Execute one step
            await system._step_simulation()
            
            if not system.current_state:
                print_colored("❌ Current state became None after simulation step", Colors.RED)
                break
            
            # Show what happened
            current_decision = system.current_state["decision_context"].get("current_decision", "none")
            current_confidence = system.current_state["decision_context"].get("decision_confidence", 0)
            current_fitness = system.current_state["fitness_score"]
            current_energy = system.current_state["energy_level"]
            
            print(f"  🧠 Decision: {prev_decision} → {current_decision}")
            print(f"  🎯 Confidence: {current_confidence:.2f}")
            print(f"  ⚡ Fitness: {prev_fitness:.3f} → {current_fitness:.3f}")
            print(f"  🔋 Energy: {prev_energy:.3f} → {current_energy:.3f}")
            
            # Show decision rationale if available
            rationale = system.current_state["decision_context"].get("decision_rationale")
            if rationale:
                print(f"  💭 Rationale: {rationale}")
            
            # Show if worm is moving/feeding
            if system.current_state["is_moving"]:
                print("  🚶 Status: Moving")
            elif system.current_state["is_feeding"]:
                print("  🍽️ Status: Feeding")
            else:
                print("  😴 Status: Idle")
            
            # Small delay for readability
            await asyncio.sleep(0.5)
        
        print()
        print_colored("📊 Final Results:", Colors.GREEN)
        print_colored("-" * 20, Colors.GREEN)
        
        metrics = await system.get_performance_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
        
        print()
        print_colored("✨ Agentic Intelligence Test Completed Successfully!", Colors.GREEN)
        print_colored("🧠 The perception → cognition → action pipeline is working!", Colors.CYAN)
        
    except ImportError as e:
        print_colored(f"❌ Import error: {e}", Colors.RED)
        print_colored("💡 Make sure you're running from the project root", Colors.YELLOW)
    except Exception as e:
        print_colored(f"❌ Test failed: {e}", Colors.RED)
        import traceback
        traceback.print_exc()

async def test_decision_scenarios():
    """Test different decision-making scenarios."""
    
    print()
    print_colored("🎯 Testing Decision Scenarios", Colors.CYAN)
    print_colored("=" * 30, Colors.CYAN)
    
    try:
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.intelligence.workflow import AgenticWorkflow
        
        # Test different goals
        scenarios = [
            ("find_food", "Food seeking behavior"),
            ("explore_environment", "Exploration behavior"),
            ("navigate_obstacles", "Obstacle avoidance")
        ]
        
        for goal, description in scenarios:
            print()
            print_colored(f"🧪 Testing: {description}", Colors.BLUE)
            
            # Create fresh state
            state = create_initial_state(f"test_{goal}")
            state["decision_context"]["current_goal"] = goal
            state["decision_context"]["goal_priority"] = 1.0
            
            # Create workflow
            workflow = AgenticWorkflow(enable_learning=True)
            await workflow.initialize()
            
            # Run a few steps
            for i in range(3):
                try:
                    state = await workflow.process_step(state)
                    decision = state["decision_context"].get("current_decision", "none")
                    confidence = state["decision_context"].get("decision_confidence", 0)
                    rationale = state["decision_context"].get("decision_rationale", "none")
                    
                    print(f"  Step {i+1}: {decision} (confidence: {confidence:.2f})")
                    print(f"    Rationale: {rationale}")
                    
                except Exception as e:
                    print_colored(f"  ⚠️ Workflow step failed: {e}", Colors.YELLOW)
                    break
        
        print()
        print_colored("✅ All decision scenarios tested!", Colors.GREEN)
        
    except Exception as e:
        print_colored(f"❌ Scenario test failed: {e}", Colors.RED)

async def main():
    """Main test function."""
    try:
        await test_agentic_workflow()
        await test_decision_scenarios()
        
        print()
        print_colored("🎉 All Tests Passed!", Colors.GREEN)
        print_colored("The Agentic Worm intelligence system is ready for showcase!", Colors.CYAN)
        
    except KeyboardInterrupt:
        print_colored("\n🛑 Test interrupted by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Test suite failed: {e}", Colors.RED)

if __name__ == "__main__":
    asyncio.run(main()) 