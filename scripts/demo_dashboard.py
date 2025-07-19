#!/usr/bin/env python3
"""
Demo: Agentic Worm with Live Visualization Dashboard

This script demonstrates the complete agentic worm system with real-time
visualization dashboard, showcasing AI decision-making in action.
"""

import asyncio
import sys
import signal
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
    NC = '\033[0m'

def print_colored(text: str, color: str = Colors.NC):
    """Print colored text."""
    print(f"{color}{text}{Colors.NC}")

class DashboardDemo:
    """Demo controller for the agentic worm dashboard."""
    
    def __init__(self):
        self.system = None
        self.dashboard = None
        self.running = False
        self.demo_scenarios = [
            ("find_food", "🍽️ Food Seeking", 60),
            ("explore_environment", "🔍 Environment Exploration", 45),
            ("navigate_obstacles", "🚧 Obstacle Navigation", 30)
        ]
        self.current_scenario = 0
    
    async def initialize(self):
        """Initialize the agentic worm system and dashboard."""
        print_colored("🧠 Agentic Worm Live Dashboard Demo", Colors.CYAN)
        print_colored("=" * 50, Colors.CYAN)
        print()
        
        try:
            from agentic_worm.core.system import AgenticWormSystem
            from agentic_worm.core.state import create_initial_state
            
            print_colored("🚀 Initializing Agentic Worm System...", Colors.BLUE)
            
            # Create system with visualization enabled
            self.system = AgenticWormSystem(
                simulation_id="dashboard_demo",
                enable_learning=True,
                enable_visualization=True  # This enables the dashboard!
            )
            
            await self.system.initialize()
            
            if self.system.current_state:
                # Set initial goal
                goal, desc, _ = self.demo_scenarios[0]
                self.system.current_state["decision_context"]["current_goal"] = goal
                self.system.current_state["decision_context"]["goal_priority"] = 1.0
                
                print_colored(f"✅ System initialized with goal: {desc}", Colors.GREEN)
            
            # Check if dashboard is available
            if hasattr(self.system, 'dashboard') and self.system.dashboard:
                self.dashboard = self.system.dashboard
                print_colored("🌐 Web dashboard available at: http://localhost:8888", Colors.GREEN)
                print_colored("📊 Open your browser to see real-time visualization!", Colors.YELLOW)
            else:
                print_colored("📺 Running in console mode (FastAPI not available)", Colors.YELLOW)
                
            print()
            return True
            
        except Exception as e:
            print_colored(f"❌ Initialization failed: {e}", Colors.RED)
            import traceback
            traceback.print_exc()
            return False
    
    async def run_demo(self):
        """Run the interactive demonstration."""
        if not await self.initialize():
            return
        
        print_colored("🎬 Starting Live Demo - Press Ctrl+C to stop", Colors.CYAN)
        print_colored("-" * 50, Colors.CYAN)
        print()
        
        # Setup signal handler for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(sig, self.signal_handler)
        
        self.running = True
        
        try:
            # Start dashboard server if available
            if self.dashboard:
                # Run dashboard and simulation concurrently
                await asyncio.gather(
                    self._run_dashboard_server(),
                    self._run_simulation_demo(),
                    return_exceptions=True
                )
            else:
                # Run just the simulation
                await self._run_simulation_demo()
                
        except KeyboardInterrupt:
            print_colored("\n🛑 Demo stopped by user", Colors.YELLOW)
        except Exception as e:
            print_colored(f"\n❌ Demo failed: {e}", Colors.RED)
        finally:
            await self.cleanup()
    
    async def _run_dashboard_server(self):
        """Run the dashboard server."""
        if not self.dashboard:
            return
        
        try:
            print_colored("🌐 Starting dashboard server...", Colors.BLUE)
            await self.dashboard.start_server()
        except Exception as e:
            print_colored(f"⚠️ Dashboard server error: {e}", Colors.YELLOW)
    
    async def _run_simulation_demo(self):
        """Run the simulation demonstration."""
        print_colored("🧠 AI Intelligence Demo Running", Colors.GREEN)
        print_colored("Watch the real-time decision-making process!", Colors.CYAN)
        print()
        
        scenario_start_time = asyncio.get_event_loop().time()
        scenario_steps = 0
        
        while self.running and self.system:
            try:
                # Run simulation step
                await self.system._step_simulation()
                scenario_steps += 1
                
                # Check for scenario switching
                goal, desc, duration = self.demo_scenarios[self.current_scenario]
                elapsed = asyncio.get_event_loop().time() - scenario_start_time
                
                if elapsed >= duration:
                    # Switch to next scenario
                    await self._switch_scenario()
                    scenario_start_time = asyncio.get_event_loop().time()
                    scenario_steps = 0
                
                # Progress update every 100 steps
                if scenario_steps % 100 == 0 and self.system.current_state:
                    progress = min(100, (elapsed / duration) * 100)
                    state = self.system.current_state
                    decision = state["decision_context"].get("current_decision", "none")
                    confidence = state["decision_context"].get("decision_confidence", 0)
                    fitness = state["fitness_score"]
                    
                    print_colored(f"📊 {desc}: {progress:.0f}% | Decision: {decision} | "
                                f"Confidence: {confidence:.2f} | Fitness: {fitness:.3f}", Colors.BLUE)
                
                # Small delay to control simulation speed
                await asyncio.sleep(0.05)  # 20 FPS
                
            except Exception as e:
                print_colored(f"⚠️ Simulation step error: {e}", Colors.YELLOW)
                await asyncio.sleep(1.0)
    
    async def _switch_scenario(self):
        """Switch to the next demonstration scenario."""
        # Move to next scenario (cycle through)
        self.current_scenario = (self.current_scenario + 1) % len(self.demo_scenarios)
        goal, desc, duration = self.demo_scenarios[self.current_scenario]
        
        # Update system goal
        if self.system and self.system.current_state:
            old_goal = self.system.current_state["decision_context"]["current_goal"]
            self.system.current_state["decision_context"]["current_goal"] = goal
            self.system.current_state["decision_context"]["goal_priority"] = 1.0
            self.system.current_state["decision_context"]["goal_progress"] = 0.0
            
            print_colored(f"\n🎯 Scenario Switch: {desc} (duration: {duration}s)", Colors.MAGENTA)
            print_colored(f"   Previous goal: {old_goal} → New goal: {goal}", Colors.CYAN)
            
            # Track goal switch in metrics if visualizer available
            if hasattr(self.system, 'visualizer') and self.system.visualizer:
                self.system.visualizer.metrics_collector.track_goal_switch(
                    old_goal or "none", goal, "demo_scenario"
                )
    
    def signal_handler(self):
        """Handle shutdown signals gracefully."""
        print_colored("\n🛑 Shutdown signal received...", Colors.YELLOW)
        self.running = False
    
    async def cleanup(self):
        """Clean up resources."""
        print_colored("🧹 Cleaning up...", Colors.BLUE)
        
        if self.dashboard:
            try:
                await self.dashboard.stop_server()
            except Exception as e:
                print_colored(f"⚠️ Dashboard cleanup warning: {e}", Colors.YELLOW)
        
        print_colored("✅ Cleanup complete", Colors.GREEN)
    
    def print_instructions(self):
        """Print usage instructions."""
        print_colored("📖 Instructions:", Colors.CYAN)
        print_colored("-" * 15, Colors.CYAN)
        print("1. 🌐 Open your browser to http://localhost:8888")
        print("2. 👁️  Watch real-time AI decision-making")
        print("3. 🎮 Use dashboard controls to change goals")
        print("4. 📊 Monitor performance metrics and learning")
        print("5. ⏹️  Press Ctrl+C to stop the demo")
        print()

async def main():
    """Main demo function."""
    demo = DashboardDemo()
    
    # Print instructions
    demo.print_instructions()
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print_colored("\n👋 Demo ended", Colors.CYAN)
    except Exception as e:
        print_colored(f"\n❌ Demo error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print_colored("🎉 Starting Agentic Worm Dashboard Demo...", Colors.GREEN)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_colored("\n👋 Goodbye!", Colors.CYAN)
    except Exception as e:
        print_colored(f"\n❌ Failed to start demo: {e}", Colors.RED) 