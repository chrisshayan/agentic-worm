#!/usr/bin/env python3
"""
🎬 Agentic Worm: Interactive Demo Launcher
==========================================

Choose from multiple demonstration scenarios showcasing different aspects
of intelligent digital life and AI-driven behavior.

Usage:
    python3 launch_demo.py

Features:
- Multiple behavioral scenarios
- Real-time dashboard options  
- OpenWorm integration tests
- Custom parameter tuning
- Performance benchmarking
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Beautiful console output
class Colors:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NC = '\033[0m'

def print_title():
    """Print the main title screen."""
    title = f"""
{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║  {Colors.MAGENTA}🧠 AGENTIC WORM: INTERACTIVE DEMO LAUNCHER{Colors.CYAN}                               ║
║                                                                               ║
║  {Colors.GREEN}🎯 Choose your adventure in intelligent digital life{Colors.CYAN}                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.NC}

{Colors.YELLOW}Select a demonstration scenario:{Colors.NC}
"""
    print(title)

def print_scenarios():
    """Print available demo scenarios."""
    scenarios = [
        {
            "id": "1",
            "name": "🍔 Food Seeking Behavior",
            "description": "Watch the worm hunt for food using chemotaxis and memory",
            "features": ["Goal-directed behavior", "Sensory processing", "Memory formation"],
            "duration": "3 minutes",
            "complexity": "Beginner"
        },
        {
            "id": "2", 
            "name": "🗺️ Exploration & Mapping",
            "description": "Autonomous environment exploration with spatial cognition",
            "features": ["Curiosity-driven behavior", "Spatial mapping", "Adaptive planning"],
            "duration": "5 minutes",
            "complexity": "Intermediate"
        },
        {
            "id": "3",
            "name": "🚧 Obstacle Navigation",
            "description": "Complex maze solving with learning and adaptation",
            "features": ["Problem solving", "Path optimization", "Dynamic learning"],
            "duration": "7 minutes", 
            "complexity": "Advanced"
        },
        {
            "id": "4",
            "name": "🧠 Neural Activity Showcase",
            "description": "Real-time 302-neuron C. elegans brain simulation",
            "features": ["OpenWorm integration", "Neural visualization", "Connectome analysis"],
            "duration": "4 minutes",
            "complexity": "Expert"
        },
        {
            "id": "5",
            "name": "🌐 Live Dashboard Demo", 
            "description": "Interactive web dashboard with real-time AI monitoring",
            "features": ["Web interface", "Real-time charts", "Interactive controls"],
            "duration": "10 minutes",
            "complexity": "Showcase"
        },
        {
            "id": "6",
            "name": "🔬 OpenWorm Integration Test",
            "description": "Test real C. elegans neural connectivity and fallback systems",
            "features": ["Real biological data", "API connectivity", "Fallback simulation"],
            "duration": "2 minutes",
            "complexity": "Technical"
        },
        {
            "id": "7",
            "name": "🎯 Custom Behavior Designer",
            "description": "Create your own worm behavior with custom goals",
            "features": ["Interactive configuration", "Goal customization", "Parameter tuning"],
            "duration": "Variable",
            "complexity": "Creative"
        },
        {
            "id": "8",
            "name": "📊 Performance Benchmark",
            "description": "Stress test the AI system with rapid decision cycles",
            "features": ["Performance metrics", "Speed testing", "System analysis"],
            "duration": "1 minute",
            "complexity": "Technical"
        }
    ]
    
    for scenario in scenarios:
        complexity_color = {
            "Beginner": Colors.GREEN,
            "Intermediate": Colors.CYAN,
            "Advanced": Colors.YELLOW,
            "Expert": Colors.MAGENTA,
            "Showcase": Colors.BOLD + Colors.BLUE,
            "Technical": Colors.RED,
            "Creative": Colors.BOLD + Colors.GREEN
        }.get(scenario["complexity"], Colors.NC)
        
        print(f"{Colors.BOLD}[{scenario['id']}]{Colors.NC} {scenario['name']}")
        print(f"    {Colors.CYAN}{scenario['description']}{Colors.NC}")
        print(f"    {Colors.GREEN}Features:{Colors.NC} {', '.join(scenario['features'])}")
        print(f"    {Colors.YELLOW}Duration:{Colors.NC} {scenario['duration']} | "
              f"{complexity_color}Complexity:{Colors.NC} {scenario['complexity']}")
        print()
    
    print(f"{Colors.BOLD}[0]{Colors.NC} {Colors.RED}Exit{Colors.NC}")
    print()

def get_user_choice():
    """Get user's scenario choice."""
    while True:
        try:
            choice = input(f"{Colors.YELLOW}Enter your choice (0-8): {Colors.NC}").strip()
            if choice in ['0', '1', '2', '3', '4', '5', '6', '7', '8']:
                return choice
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 0-8.{Colors.NC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Goodbye!{Colors.NC}")
            sys.exit(0)

async def run_food_seeking_demo():
    """Run the food seeking behavior demo."""
    print(f"\n{Colors.GREEN}🍔 Starting Food Seeking Behavior Demo...{Colors.NC}")
    
    try:
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.intelligence.workflow import AgenticWorkflow
        
        # Initialize workflow
        workflow = AgenticWorkflow(enable_learning=True)
        await workflow.initialize()
        
        # Create state with food-seeking goal
        state = create_initial_state("food_seeking_demo")
        state["decision_context"]["current_goal"] = "find_food"
        
        print(f"{Colors.CYAN}🎯 Goal: Find and consume food using chemotaxis{Colors.NC}")
        print(f"{Colors.YELLOW}🧠 AI Features: Sensory processing → Goal planning → Motor control{Colors.NC}")
        
        # Run for 3 minutes
        duration = 180
        steps = 200
        
        for i in range(steps):
            state = await workflow.process_step(state)
            
            if i % 20 == 0:
                fitness = state.get("fitness_score", 0)
                decision = state.get("decision_context", {}).get("current_decision", "none")
                print(f"📊 Step {i}: Decision={decision} | Fitness={fitness:.3f}")
            
            await asyncio.sleep(duration / steps)
        
        print(f"\n{Colors.GREEN}✅ Food seeking demo completed!{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Demo failed: {e}{Colors.NC}")

async def run_exploration_demo():
    """Run the exploration and mapping demo."""
    print(f"\n{Colors.GREEN}🗺️ Starting Exploration & Mapping Demo...{Colors.NC}")
    
    try:
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.intelligence.workflow import AgenticWorkflow
        
        workflow = AgenticWorkflow(enable_learning=True)
        await workflow.initialize()
        
        state = create_initial_state("exploration_demo")
        state["decision_context"]["current_goal"] = "explore"
        
        print(f"{Colors.CYAN}🎯 Goal: Explore and map unknown environment{Colors.NC}")
        print(f"{Colors.YELLOW}🧠 AI Features: Curiosity → Spatial memory → Adaptive planning{Colors.NC}")
        
        # Run for 5 minutes
        duration = 300
        steps = 250
        
        exploration_areas = ["north_quadrant", "east_region", "south_boundary", "west_territory", "central_hub"]
        
        for i in range(steps):
                                      # Change exploration target periodically
             if i % 50 == 0 and i > 0:
                 area = exploration_areas[i // 50 % len(exploration_areas)]
                 print(f"{Colors.MAGENTA}🗺️ New exploration target: {area}{Colors.NC}")
             
             state = await workflow.process_step(state)
             
             if i % 25 == 0:
                 fitness = state.get("fitness_score", 0)
                 decision = state.get("decision_context", {}).get("current_decision", "none")
                 current_target = exploration_areas[i // 50 % len(exploration_areas)] if i >= 50 else "initial_area"
                 print(f"📊 Step {i}: Decision={decision} | Target={current_target} | Fitness={fitness:.3f}")
             await asyncio.sleep(duration / steps)
        
        print(f"\n{Colors.GREEN}✅ Exploration demo completed!{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Demo failed: {e}{Colors.NC}")

async def run_obstacle_navigation_demo():
    """Run the obstacle navigation demo."""
    print(f"\n{Colors.GREEN}🚧 Starting Obstacle Navigation Demo...{Colors.NC}")
    
    try:
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.intelligence.workflow import AgenticWorkflow
        
        workflow = AgenticWorkflow(enable_learning=True)
        await workflow.initialize()
        
        state = create_initial_state("navigation_demo")
        state["decision_context"]["current_goal"] = "navigate_maze"
        
        print(f"{Colors.CYAN}🎯 Goal: Navigate complex maze with obstacles{Colors.NC}")
        print(f"{Colors.YELLOW}🧠 AI Features: Problem solving → Path planning → Learning from mistakes{Colors.NC}")
        
        # Simulate maze with obstacles
        obstacles = ["wall_barrier", "dead_end", "narrow_passage", "moving_obstacle", "hidden_trap"]
        
        duration = 420  # 7 minutes
        steps = 300
        
        for i in range(steps):
            # Introduce obstacles periodically
            if i % 60 == 0 and i > 0:
                obstacle = obstacles[i // 60 % len(obstacles)]
                state["environment"] = state.get("environment", {})
                state["environment"]["current_obstacle"] = obstacle
                print(f"{Colors.RED}🚧 Obstacle encountered: {obstacle}{Colors.NC}")
            
            state = await workflow.process_step(state)
            
            if i % 30 == 0:
                fitness = state.get("fitness_score", 0)
                decision = state.get("decision_context", {}).get("current_decision", "none")
                obstacle = state.get("environment", {}).get("current_obstacle", "none")
                print(f"📊 Step {i}: Decision={decision} | Obstacle={obstacle} | Fitness={fitness:.3f}")
            
            await asyncio.sleep(duration / steps)
        
        print(f"\n{Colors.GREEN}✅ Obstacle navigation demo completed!{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Demo failed: {e}{Colors.NC}")

async def run_neural_showcase_demo():
    """Run the neural activity showcase demo."""
    print(f"\n{Colors.GREEN}🧠 Starting Neural Activity Showcase Demo...{Colors.NC}")
    
    try:
        from agentic_worm.intelligence.openworm import get_openworm_client, initialize_openworm
        
        print(f"{Colors.BLUE}🔗 Initializing OpenWorm connection...{Colors.NC}")
        
        # Try to connect to real OpenWorm
        connected = await initialize_openworm()
        
        if connected:
            print(f"{Colors.GREEN}✅ Connected to OpenWorm simulation{Colors.NC}")
        else:
            print(f"{Colors.YELLOW}⚠️ Using enhanced 302-neuron simulation{Colors.NC}")
        
        client = get_openworm_client()
        
        print(f"{Colors.CYAN}🎯 Goal: Visualize C. elegans neural activity{Colors.NC}")
        print(f"{Colors.YELLOW}🧠 Features: 302 neurons → Connectome → Real-time firing patterns{Colors.NC}")
        
        # Run neural showcase for 4 minutes
        duration = 240
        steps = 120
        
        for i in range(steps):
            # Get neural state
            neural_state = await client.get_neural_state()
            
            if i % 10 == 0:
                neuron_count = len(neural_state.get("neurons", {}))
                global_activity = neural_state.get("global_activity", 0)
                simulation_step = neural_state.get("simulation_step", 0)
                
                print(f"🧠 Neural State {i}: Neurons={neuron_count} | "
                      f"Activity={global_activity:.2f}Hz | Step={simulation_step}")
                
                # Show sample neuron activity
                neurons = neural_state.get("neurons", {})
                if neurons:
                    sample_neurons = list(neurons.items())[:3]
                    for neuron_id, data in sample_neurons:
                        membrane = data.get("membrane_potential", 0)
                        firing = data.get("firing_rate", 0)
                        print(f"  🔬 {neuron_id}: {membrane:.1f}mV, {firing:.1f}Hz")
            
            await asyncio.sleep(duration / steps)
        
        print(f"\n{Colors.GREEN}✅ Neural showcase demo completed!{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Demo failed: {e}{Colors.NC}")

async def run_dashboard_demo():
    """Run the live dashboard demo."""
    print(f"\n{Colors.GREEN}🌐 Starting Live Dashboard Demo...{Colors.NC}")
    print(f"{Colors.CYAN}📊 This will launch the full interactive web interface{Colors.NC}")
    print(f"{Colors.YELLOW}💡 For best experience, use a modern browser{Colors.NC}")
    
    try:
        # Import and run the existing dashboard demo
        import subprocess
        import webbrowser
        
        print(f"{Colors.BLUE}🚀 Launching dashboard server...{Colors.NC}")
        
        # Try to run the dashboard demo script
        result = subprocess.run([
            sys.executable, "scripts/demo_dashboard.py"
        ], capture_output=False)
        
        if result.returncode == 0:
            print(f"\n{Colors.GREEN}✅ Dashboard demo completed!{Colors.NC}")
        else:
            print(f"\n{Colors.YELLOW}⚠️ Dashboard demo ended{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Dashboard demo failed: {e}{Colors.NC}")
        print(f"{Colors.YELLOW}💡 Try running manually: python3 scripts/demo_dashboard.py{Colors.NC}")

async def run_openworm_test():
    """Run the OpenWorm integration test."""
    print(f"\n{Colors.GREEN}🔬 Starting OpenWorm Integration Test...{Colors.NC}")
    
    try:
        import subprocess
        
        print(f"{Colors.BLUE}🧪 Running comprehensive OpenWorm tests...{Colors.NC}")
        
        result = subprocess.run([
            sys.executable, "scripts/test_openworm_integration.py"
        ], capture_output=False)
        
        if result.returncode == 0:
            print(f"\n{Colors.GREEN}✅ OpenWorm integration test completed!{Colors.NC}")
        else:
            print(f"\n{Colors.YELLOW}⚠️ OpenWorm test ended{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ OpenWorm test failed: {e}{Colors.NC}")

async def run_custom_behavior_designer():
    """Run the custom behavior designer."""
    print(f"\n{Colors.GREEN}🎯 Starting Custom Behavior Designer...{Colors.NC}")
    
    try:
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.intelligence.workflow import AgenticWorkflow
        
        print(f"{Colors.CYAN}🎨 Design your own worm behavior!{Colors.NC}")
        
        # Get user preferences
        print(f"\n{Colors.YELLOW}Choose a goal for your worm:{Colors.NC}")
        print("1. Find food")
        print("2. Explore environment") 
        print("3. Avoid obstacles")
        print("4. Custom goal")
        
        goal_choice = input(f"{Colors.YELLOW}Enter choice (1-4): {Colors.NC}").strip()
        
        goal_map = {
            "1": "find_food",
            "2": "explore", 
            "3": "avoid_obstacles",
            "4": "custom"
        }
        
        goal = goal_map.get(goal_choice, "find_food")
        
        if goal == "custom":
            custom_goal = input(f"{Colors.YELLOW}Enter custom goal: {Colors.NC}").strip()
            goal = custom_goal or "explore"
        
        # Get duration
        try:
            duration = int(input(f"{Colors.YELLOW}Duration in seconds (30-600): {Colors.NC}").strip())
            duration = max(30, min(600, duration))
        except:
            duration = 120
        
        print(f"\n{Colors.GREEN}🎯 Goal: {goal}{Colors.NC}")
        print(f"{Colors.GREEN}⏱️ Duration: {duration} seconds{Colors.NC}")
        
        # Run custom behavior
        workflow = AgenticWorkflow(enable_learning=True)
        await workflow.initialize()
        
        state = create_initial_state("custom_behavior")
        state["decision_context"]["current_goal"] = goal
        
        steps = duration // 2  # One step every 2 seconds
        
        for i in range(steps):
            state = await workflow.process_step(state)
            
            if i % 5 == 0:
                fitness = state.get("fitness_score", 0)
                decision = state.get("decision_context", {}).get("current_decision", "none")
                print(f"🎯 Step {i}: Decision={decision} | Goal={goal} | Fitness={fitness:.3f}")
            
            await asyncio.sleep(2)
        
        print(f"\n{Colors.GREEN}✅ Custom behavior completed!{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Custom behavior failed: {e}{Colors.NC}")

async def run_performance_benchmark():
    """Run the performance benchmark."""
    print(f"\n{Colors.GREEN}📊 Starting Performance Benchmark...{Colors.NC}")
    
    try:
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.intelligence.workflow import AgenticWorkflow
        
        print(f"{Colors.CYAN}⚡ Testing AI decision-making speed and efficiency{Colors.NC}")
        
        workflow = AgenticWorkflow(enable_learning=True)
        await workflow.initialize()
        
        state = create_initial_state("benchmark")
        state["decision_context"]["current_goal"] = "optimize_performance"
        
        # Rapid-fire benchmark
        steps = 100
        start_time = time.time()
        
        print(f"{Colors.YELLOW}🏃 Running {steps} rapid AI decision cycles...{Colors.NC}")
        
        for i in range(steps):
            state = await workflow.process_step(state)
            
            if i % 20 == 0:
                elapsed = time.time() - start_time
                steps_per_sec = i / elapsed if elapsed > 0 else 0
                print(f"⚡ Step {i}: {steps_per_sec:.1f} steps/sec")
        
        total_time = time.time() - start_time
        avg_steps_per_sec = steps / total_time
        
        print(f"\n{Colors.GREEN}📊 Benchmark Results:{Colors.NC}")
        print(f"  • Total Steps: {steps}")
        print(f"  • Total Time: {total_time:.2f} seconds") 
        print(f"  • Average Speed: {avg_steps_per_sec:.1f} steps/second")
        print(f"  • Final Fitness: {state.get('fitness_score', 0):.3f}")
        
        print(f"\n{Colors.GREEN}✅ Performance benchmark completed!{Colors.NC}")
        
    except Exception as e:
        print(f"{Colors.RED}❌ Benchmark failed: {e}{Colors.NC}")

async def main():
    """Main demo launcher function."""
    print_title()
    
    while True:
        print_scenarios()
        choice = get_user_choice()
        
        if choice == "0":
            print(f"{Colors.CYAN}👋 Thanks for exploring Agentic Worm!{Colors.NC}")
            break
        
        # Run selected demo
        try:
            if choice == "1":
                await run_food_seeking_demo()
            elif choice == "2":
                await run_exploration_demo()
            elif choice == "3":
                await run_obstacle_navigation_demo()
            elif choice == "4":
                await run_neural_showcase_demo()
            elif choice == "5":
                await run_dashboard_demo()
            elif choice == "6":
                await run_openworm_test()
            elif choice == "7":
                await run_custom_behavior_designer()
            elif choice == "8":
                await run_performance_benchmark()
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}🛑 Demo interrupted{Colors.NC}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Demo error: {e}{Colors.NC}")
        
        # Ask if user wants to run another demo
        print(f"\n{Colors.YELLOW}Would you like to run another demo? (y/n): {Colors.NC}", end="")
        try:
            continue_choice = input().strip().lower()
            if continue_choice not in ['y', 'yes']:
                print(f"{Colors.CYAN}👋 Thanks for exploring Agentic Worm!{Colors.NC}")
                break
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.NC}")
            break
        
        print()  # Add spacing between demos

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}👋 Thanks for trying Agentic Worm!{Colors.NC}")
    except Exception as e:
        print(f"\n{Colors.RED}💥 Launcher error: {e}{Colors.NC}")
        sys.exit(1) 