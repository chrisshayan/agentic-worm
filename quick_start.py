#!/usr/bin/env python3
"""
🚀 Agentic Worm: One-Click Quick Start Demo
===========================================

The fastest way to see intelligent digital life in action!

Usage:
    python3 quick_start.py

This script:
1. Checks dependencies and installs missing ones
2. Launches the most impressive demo scenario
3. Opens the live dashboard in your browser
4. Runs for 3 minutes of autonomous behavior

Perfect for:
- First-time demos
- Sharing with friends
- Quick showcases
- "Wow factor" moments
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

# Colors for beautiful output
class Colors:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    MAGENTA = '\033[35m'
    BOLD = '\033[1m'
    NC = '\033[0m'

def print_banner():
    """Print an impressive startup banner."""
    banner = f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║  {Colors.BOLD}🧠 AGENTIC WORM: AI-DRIVEN DIGITAL ORGANISM{Colors.NC}{Colors.CYAN}                           ║
║                                                                               ║
║  {Colors.YELLOW}✨ Intelligent digital life combining C. elegans neuroscience & AI{Colors.NC}{Colors.CYAN}      ║
║  {Colors.GREEN}🎯 Goal-directed behavior • 🧬 302-neuron simulation • 🤖 Real-time AI{Colors.NC}{Colors.CYAN}   ║
║                                                                               ║
║  {Colors.MAGENTA}🚀 QUICK START: Watch 3 minutes of autonomous intelligence!{Colors.NC}{Colors.CYAN}           ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.NC}
"""
    print(banner)

def check_python_version():
    """Ensure Python version is compatible."""
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Python 3.8+ required. You have {sys.version_info.major}.{sys.version_info.minor}{Colors.NC}")
        print(f"{Colors.YELLOW}💡 Please upgrade Python: https://python.org/downloads/{Colors.NC}")
        return False
    print(f"{Colors.GREEN}✅ Python {sys.version_info.major}.{sys.version_info.minor} - Compatible!{Colors.NC}")
    return True

def install_dependencies():
    """Install required packages quickly."""
    print(f"\n{Colors.BLUE}📦 Installing required packages...{Colors.NC}")
    
    # Essential packages for quick demo
    essential_packages = [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0", 
        "websockets>=11.0",
        "asyncio-mqtt>=0.11.0"
    ]
    
    for package in essential_packages:
        try:
            # Try importing first to see if already installed
            package_name = package.split(">=")[0].split("==")[0]
            if package_name == "uvicorn[standard]":
                package_name = "uvicorn"
            
            __import__(package_name.replace("-", "_"))
            print(f"  {Colors.GREEN}✓{Colors.NC} {package_name}")
            
        except ImportError:
            print(f"  {Colors.YELLOW}⬇️  Installing {package_name}...{Colors.NC}")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ], capture_output=True)
            
            if result.returncode == 0:
                print(f"  {Colors.GREEN}✅ {package_name} installed!{Colors.NC}")
            else:
                print(f"  {Colors.RED}❌ Failed to install {package_name}{Colors.NC}")
                return False
    
    return True

def setup_project_structure():
    """Ensure the project structure is ready."""
    print(f"\n{Colors.BLUE}🏗️  Checking project structure...{Colors.NC}")
    
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        print(f"  {Colors.GREEN}✓{Colors.NC} Source path configured")
    else:
        print(f"  {Colors.RED}❌ Source directory not found: {src_path}{Colors.NC}")
        return False
    
    # Check essential modules
    try:
        from agentic_worm.core.system import AgenticWormSystem
        from agentic_worm.visualization.dashboard import DashboardServer
        print(f"  {Colors.GREEN}✓{Colors.NC} Core modules available")
        return True
    except ImportError as e:
        print(f"  {Colors.RED}❌ Import error: {e}{Colors.NC}")
        return False

def launch_quick_demo():
    """Launch the most impressive 3-minute demo."""
    print(f"\n{Colors.MAGENTA}🎬 Launching Quick Demo Scenario...{Colors.NC}")
    print(f"{Colors.CYAN}📊 This demo showcases:{Colors.NC}")
    print(f"  • {Colors.GREEN}🧠 AI-driven decision making{Colors.NC}")
    print(f"  • {Colors.GREEN}🎯 Goal-directed food seeking{Colors.NC}")
    print(f"  • {Colors.GREEN}📈 Real-time learning adaptation{Colors.NC}")
    print(f"  • {Colors.GREEN}🌐 Live web dashboard{Colors.NC}")
    
    print(f"\n{Colors.YELLOW}⚡ Starting in 3 seconds...{Colors.NC}")
    time.sleep(3)
    
    try:
        # Import after path setup
        import asyncio
        from agentic_worm.core.system import AgenticWormSystem
        from agentic_worm.core.state import create_initial_state
        from agentic_worm.visualization.dashboard import DashboardServer
        
        # Run the demo
        asyncio.run(run_quick_demo_async())
        
    except Exception as e:
        print(f"{Colors.RED}❌ Demo failed: {e}{Colors.NC}")
        print(f"{Colors.YELLOW}💡 Try running: python3 scripts/demo_dashboard.py{Colors.NC}")
        return False
    
    return True

async def run_quick_demo_async():
    """Run the async demo scenario."""
    import asyncio
    from agentic_worm.core.state import create_initial_state
    from agentic_worm.intelligence.workflow import AgenticWorkflow
    
    print(f"{Colors.BLUE}🧠 Initializing agentic worm...{Colors.NC}")
    
    # Initialize workflow
    workflow = AgenticWorkflow(enable_learning=True)
    await workflow.initialize()
    
    # Create state with food-seeking goal
    state = create_initial_state("quick_demo")
    state["decision_context"]["current_goal"] = "find_food"
    
    print(f"\n{Colors.GREEN}🎯 DEMO RUNNING: Autonomous food-seeking behavior{Colors.NC}")
    print(f"{Colors.CYAN}📊 Watch the real-time console for AI decisions!{Colors.NC}")
    print(f"{Colors.YELLOW}⏱️  Demo duration: 180 seconds (3 minutes){Colors.NC}")
    print(f"{Colors.MAGENTA}🧠 AI Pipeline: Perception → Cognition → Decision → Action{Colors.NC}")
    
    try:
        # Try to open a simple dashboard (if available)
        webbrowser.open("http://localhost:8080")
        print(f"{Colors.GREEN}🌐 Dashboard attempt: http://localhost:8080{Colors.NC}")
    except Exception:
        print(f"{Colors.YELLOW}💻 Running console-only demo{Colors.NC}")
    
    # Run demo for 3 minutes
    demo_duration = 180  # 3 minutes
    steps_per_second = 2  # Slower for better observation
    total_steps = demo_duration * steps_per_second
    
    start_time = time.time()
    
    for step in range(total_steps):
        # Run workflow step with AI decision-making
        state = await workflow.process_step(state)
        
        # Show AI activity every few steps
        if step % 10 == 0:
            fitness = state.get("fitness_score", 0)
            decision = state.get("decision_context", {}).get("current_decision", "none")
            confidence = state.get("decision_context", {}).get("decision_confidence", 0)
            
            print(f"🧠 Step {step}: Decision={decision} | Fitness={fitness:.3f} | Confidence={confidence:.2f}")
        
        # Progress indicator every 30 seconds
        elapsed = time.time() - start_time
        if step % (30 * steps_per_second) == 0 and step > 0:
            remaining = demo_duration - elapsed
            fitness = state.get("fitness_score", 0)
            decision = state.get("decision_context", {}).get("current_decision", "none")
            
            print(f"\n{Colors.CYAN}📊 Progress: {elapsed:.0f}s | "
                  f"Fitness: {fitness:.3f} | "
                  f"Decision: {decision} | "
                  f"Remaining: {remaining:.0f}s{Colors.NC}")
        
        # Small delay for real-time feel
        await asyncio.sleep(0.5)
    
    # Demo complete
    print(f"\n{Colors.GREEN}🎉 DEMO COMPLETE!{Colors.NC}")
    print(f"{Colors.CYAN}📊 Final Statistics:{Colors.NC}")
    print(f"  • Steps: {total_steps}")
    print(f"  • Final Fitness: {state.get('fitness_score', 0):.3f}")
    print(f"  • Total Decisions: {len(state.get('messages', []))}")
    print(f"  • Runtime: {time.time() - start_time:.1f} seconds")
    
    print(f"\n{Colors.MAGENTA}🚀 Want more? Try these advanced demos:{Colors.NC}")
    print(f"  • {Colors.YELLOW}python3 scripts/demo_dashboard.py{Colors.NC} - Full interactive dashboard")
    print(f"  • {Colors.YELLOW}python3 scripts/test_openworm_integration.py{Colors.NC} - Real C. elegans neural data")
    print(f"  • {Colors.YELLOW}python3 launch_demo.py{Colors.NC} - Multiple scenario options")

def main():
    """Main quick start function."""
    print_banner()
    
    # Check requirements
    if not check_python_version():
        return 1
    
    if not install_dependencies():
        print(f"\n{Colors.RED}❌ Dependency installation failed{Colors.NC}")
        return 1
    
    if not setup_project_structure():
        print(f"\n{Colors.RED}❌ Project setup failed{Colors.NC}")
        return 1
    
    # Launch demo
    print(f"\n{Colors.GREEN}🎉 All systems ready!{Colors.NC}")
    
    if launch_quick_demo():
        print(f"\n{Colors.GREEN}✨ Quick start demo completed successfully!{Colors.NC}")
        print(f"{Colors.CYAN}🌟 Thank you for exploring Agentic Worm!{Colors.NC}")
        return 0
    else:
        print(f"\n{Colors.RED}❌ Demo failed to complete{Colors.NC}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Demo interrupted by user{Colors.NC}")
        print(f"{Colors.CYAN}👋 Thanks for trying Agentic Worm!{Colors.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.NC}")
        print(f"{Colors.YELLOW}💡 Try: python3 scripts/demo_dashboard.py{Colors.NC}")
        sys.exit(1) 