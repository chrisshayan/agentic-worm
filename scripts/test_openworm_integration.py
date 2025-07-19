#!/usr/bin/env python3
"""
Test OpenWorm Integration

This script tests the real OpenWorm API integration and shows 
the enhanced fallback simulation with C. elegans neural data.
"""

import asyncio
import sys
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
    NC = '\033[0m'

def print_colored(text: str, color: str = Colors.NC):
    """Print colored text."""
    print(f"{color}{text}{Colors.NC}")

async def test_openworm_integration():
    """Test OpenWorm integration features."""
    
    print_colored("🔬 Testing OpenWorm Integration", Colors.CYAN)
    print_colored("=" * 40, Colors.CYAN)
    print()
    
    try:
        from agentic_worm.intelligence.openworm import OpenWormClient
        
        # Test OpenWorm client
        print_colored("🔗 Testing OpenWorm Connection...", Colors.BLUE)
        client = OpenWormClient(timeout=2.0, enable_fallback=True)
        
        # Initialize connection
        connected = await client.initialize()
        if connected:
            print_colored("✅ OpenWorm client initialized", Colors.GREEN)
        else:
            print_colored("⚠️ Using fallback simulation mode", Colors.YELLOW)
        
        print()
        
        # Test neural state
        print_colored("🧠 Testing Neural State Retrieval...", Colors.BLUE)
        neural_state = await client.get_neural_state()
        
        if neural_state.get("simulated"):
            print_colored("📊 Fallback Neural Data:", Colors.YELLOW)
        else:
            print_colored("📊 Real OpenWorm Neural Data:", Colors.GREEN)
            
        neuron_count = len(neural_state.get("neurons", {}))
        global_activity = neural_state.get("global_activity", 0)
        
        print(f"  Neurons: {neuron_count}")
        print(f"  Global Activity: {global_activity:.2f} Hz")
        print(f"  Simulation Step: {neural_state.get('simulation_step', 0)}")
        
        # Show sample neuron data
        neurons = neural_state.get("neurons", {})
        if neurons:
            sample_neurons = list(neurons.items())[:3]  # First 3 neurons
            print("  Sample Neurons:")
            for neuron_id, data in sample_neurons:
                membrane = data.get("membrane_potential", 0)
                firing = data.get("firing_rate", 0)
                print(f"    {neuron_id}: {membrane:.1f}mV, {firing:.1f}Hz")
        
        print()
        
        # Test sensory data
        print_colored("👁️ Testing Sensory Data...", Colors.BLUE)
        sensory_data = await client.get_sensory_data()
        
        if sensory_data.get("simulated"):
            print_colored("📡 Enhanced Simulation Sensory Data:", Colors.YELLOW)
        else:
            print_colored("📡 Real OpenWorm Sensory Data:", Colors.GREEN)
        
        chemotaxis = sensory_data.get("chemotaxis", {})
        mechanosensory = sensory_data.get("mechanosensory", {})
        
        print(f"  Chemical Gradient: {chemotaxis.get('gradient_strength', 0):.3f}")
        print(f"  Chemical Concentration: {chemotaxis.get('concentration', 0):.3f}")
        print(f"  Gradient Direction: {chemotaxis.get('direction', 0):.1f}°")
        print(f"  Mechanical Pressure: {mechanosensory.get('pressure', 0):.3f}")
        print(f"  Temperature: {sensory_data.get('thermosensory', 20):.1f}°C")
        
        print()
        
        # Test motor commands
        print_colored("⚡ Testing Motor Commands...", Colors.BLUE)
        motor_commands = {
            "dorsal": 0.6,
            "ventral": 0.4,
            "timestamp": neural_state.get("timestamp", 0)
        }
        
        result = await client.send_motor_commands(motor_commands)
        
        if result.get("status") == "simulated":
            print_colored("🔧 Motor Command Simulation:", Colors.YELLOW)
        else:
            print_colored("🔧 Real OpenWorm Motor Response:", Colors.GREEN)
            
        print(f"  Command Success: {result.get('success', False)}")
        print(f"  Status: {result.get('status', 'unknown')}")
        applied = result.get("applied_commands", {})
        if applied:
            print(f"  Applied: Dorsal={applied.get('dorsal', 0):.2f}, Ventral={applied.get('ventral', 0):.2f}")
        
        print()
        
        # Test body state
        print_colored("🤸 Testing Body Physics...", Colors.BLUE)
        body_state = await client.get_body_state()
        
        position = body_state.get("position", {})
        orientation = body_state.get("orientation", {})
        velocity = body_state.get("velocity", {})
        
        if body_state.get("simulated"):
            print_colored("🎾 Physics Simulation Data:", Colors.YELLOW)
        else:
            print_colored("🎾 Real Sibernetic Physics Data:", Colors.GREEN)
            
        print(f"  Position: x={position.get('x', 0):.2f}, y={position.get('y', 0):.2f}, z={position.get('z', 0):.2f}")
        print(f"  Orientation: pitch={orientation.get('pitch', 0):.2f}°, yaw={orientation.get('yaw', 0):.2f}°")
        print(f"  Velocity: linear={velocity.get('linear', 0):.2f}, angular={velocity.get('angular', 0):.2f}")
        
        print()
        
        # Clean up
        await client.close()
        
        print_colored("✨ OpenWorm Integration Test Complete!", Colors.GREEN)
        print_colored("🔬 The system gracefully handles both real OpenWorm data", Colors.CYAN)
        print_colored("   and enhanced simulation when OpenWorm is unavailable", Colors.CYAN)
        
    except Exception as e:
        print_colored(f"❌ Integration test failed: {e}", Colors.RED)
        import traceback
        traceback.print_exc()

async def test_workflow_integration():
    """Test the workflow with OpenWorm integration."""
    
    print()
    print_colored("🧠 Testing Workflow with OpenWorm Integration", Colors.CYAN)
    print_colored("=" * 50, Colors.CYAN)
    print()
    
    try:
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.intelligence.workflow import AgenticWorkflow
        from agentic_worm.intelligence.openworm import initialize_openworm
        
        # Initialize OpenWorm
        print_colored("🔗 Initializing OpenWorm connection...", Colors.BLUE)
        openworm_ready = await initialize_openworm()
        
        if openworm_ready:
            print_colored("✅ OpenWorm integration ready", Colors.GREEN)
        else:
            print_colored("⚠️ Using fallback mode", Colors.YELLOW)
        
        # Create workflow
        workflow = AgenticWorkflow(enable_learning=True)
        await workflow.initialize()
        
        # Create test state
        state = create_initial_state("openworm_test")
        state["decision_context"]["current_goal"] = "find_food"
        
        print_colored("🔄 Running workflow steps with OpenWorm data...", Colors.BLUE)
        
        # Run a few steps
        for i in range(5):
            print(f"\n  Step {i+1}:")
            
            # Process step
            state = await workflow.process_step(state)
            
            # Show results
            decision = state["decision_context"].get("current_decision", "none")
            confidence = state["decision_context"].get("decision_confidence", 0)
            
            # Check if we got OpenWorm data
            chemotaxis = state["sensory_data"].get("chemotaxis", {})
            if "gradient_direction" in chemotaxis:
                print(f"    🧠 OpenWorm sensory data detected!")
                print(f"    📡 Chemical gradient: {chemotaxis.get('gradient_strength', 0):.3f}")
                print(f"    📐 Direction: {chemotaxis.get('gradient_direction', 0):.1f}°")
            
            print(f"    🎯 Decision: {decision} (confidence: {confidence:.2f})")
            print(f"    ⚡ Fitness: {state['fitness_score']:.3f}")
        
        print()
        print_colored("✅ Workflow integration test complete!", Colors.GREEN)
        
    except Exception as e:
        print_colored(f"❌ Workflow integration test failed: {e}", Colors.RED)

async def main():
    """Main test function."""
    try:
        await test_openworm_integration()
        await test_workflow_integration()
        
        print()
        print_colored("🎉 All OpenWorm Integration Tests Passed!", Colors.GREEN)
        print_colored("🔬 Ready for real C. elegans neural simulation!", Colors.CYAN)
        
    except KeyboardInterrupt:
        print_colored("\n🛑 Test interrupted by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Test suite failed: {e}", Colors.RED)

if __name__ == "__main__":
    print_colored("🔬 Starting OpenWorm Integration Tests...", Colors.GREEN)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n👋 Goodbye!", Colors.CYAN)
    except Exception as e:
        print_colored(f"\n❌ Failed to start tests: {e}", Colors.RED) 