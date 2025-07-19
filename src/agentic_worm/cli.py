"""
Command-line interface for the Agentic Worm system.

This module provides easy-to-use commands for running demonstrations,
managing the system, and showcasing agentic behavior.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

from .demo import DemoRunner, run_quick_demo
from .core import create_demo_system

# Create CLI app
app = typer.Typer(
    name="agentic-worm",
    help="AI-driven autonomous digital C. elegans",
    add_completion=False
)

# Rich console for beautiful output
console = Console()

# Setup logging with Rich
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)


@app.command()
def demo(
    demo_type: str = typer.Option(
        "basic", 
        "--type", "-t",
        help="Type of demo: basic, food_seeking, obstacle_avoidance, learning"
    ),
    duration: float = typer.Option(
        30.0,
        "--duration", "-d", 
        help="Duration in seconds"
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output directory for demo results"
    ),
    no_recording: bool = typer.Option(
        False,
        "--no-recording",
        help="Disable recording of demo data"
    )
):
    """
    Run an Agentic Worm demonstration.
    
    This command showcases the autonomous behavior of the digital C. elegans,
    integrating OpenWorm simulation with AI-driven decision making.
    """
    console.print(f"🧠 [bold green]Agentic Worm Demo: {demo_type}[/bold green]")
    console.print(f"Duration: {duration} seconds")
    
    if output_dir:
        output_path = Path(output_dir)
        console.print(f"Output directory: {output_path}")
    
    try:
        # Run the demo
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Setting up demo...", total=None)
            
            # Run the demo asynchronously
            results = asyncio.run(_run_demo_async(
                demo_type, duration, output_dir, not no_recording, progress, task
            ))
        
        # Display results
        _display_demo_results(results)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Demo failed: {e}[/red]")
        sys.exit(1)


@app.command()
def quick(
    demo_type: str = typer.Argument("basic", help="Demo type to run"),
    duration: float = typer.Option(10.0, "--duration", "-d", help="Duration in seconds")
):
    """
    Run a quick demonstration (10-30 seconds).
    """
    console.print(f"🚀 [bold cyan]Quick Demo: {demo_type}[/bold cyan]")
    
    try:
        results = asyncio.run(run_quick_demo(demo_type, duration))
        _display_demo_results(results)
    except Exception as e:
        console.print(f"[red]Quick demo failed: {e}[/red]")
        sys.exit(1)


@app.command()
def status():
    """
    Check the status of OpenWorm integration and system components.
    """
    console.print("🔍 [bold blue]System Status Check[/bold blue]")
    
    # Check Python environment
    console.print(f"Python version: {sys.version}")
    
    # Check if dependencies are available
    try:
        import langchain
        import langgraph
        console.print("✅ LangChain/LangGraph: Available")
    except ImportError:
        console.print("❌ LangChain/LangGraph: Not installed")
    
    try:
        import torch
        console.print("✅ PyTorch: Available")
    except ImportError:
        console.print("❌ PyTorch: Not installed")
    
    # Check Docker containers (if running in Docker environment)
    console.print("\n📊 Ready to run Agentic Worm demonstrations!")


@app.command()
def install():
    """
    Install or verify system dependencies.
    """
    console.print("📦 [bold magenta]Installing Dependencies[/bold magenta]")
    
    # This would typically install OpenWorm dependencies
    # For now, just provide instructions
    console.print("""
To set up the complete Agentic Worm system:

1. 🐳 **Docker Setup** (Recommended):
   ```
   docker-compose -f docker/docker-compose.yml up -d
   ```

2. 🐍 **Python Dependencies**:
   ```
   pip install -e .
   ```

3. 🧬 **OpenWorm Integration**:
   The system will automatically connect to OpenWorm containers
   when running in Docker environment.

4. 🚀 **Quick Test**:
   ```
   agentic-worm demo --type basic --duration 10
   ```
    """)


async def _run_demo_async(
    demo_type: str,
    duration: float,
    output_dir: Optional[str],
    enable_recording: bool,
    progress: Progress,
    task_id
) -> dict:
    """Run demo asynchronously with progress tracking."""
    
    # Update progress
    progress.update(task_id, description="Initializing system...")
    
    # Create demo runner
    runner = DemoRunner(
        demo_name=f"cli_{demo_type}",
        duration_seconds=duration,
        enable_recording=enable_recording,
        output_dir=Path(output_dir) if output_dir else None
    )
    
    # Update progress
    progress.update(task_id, description="Starting simulation...")
    
    # Run the appropriate demo
    if demo_type == "food_seeking":
        results = await runner.run_food_seeking_demo()
    elif demo_type == "obstacle_avoidance":
        results = await runner.run_obstacle_avoidance_demo()
    elif demo_type == "learning":
        results = await runner.run_learning_demo()
    else:
        results = await runner.run_basic_demo()
    
    progress.update(task_id, description="Demo completed!", completed=True)
    return results


def _display_demo_results(results: dict):
    """Display demo results in a nice format."""
    console.print("\n📊 [bold green]Demo Results[/bold green]")
    console.print(f"Demo: {results.get('demo_name', 'Unknown')}")
    console.print(f"Duration: {results.get('duration', 0):.2f} seconds")
    console.print(f"Final fitness: {results.get('final_fitness_score', 0):.3f}")
    console.print(f"Final energy: {results.get('final_energy_level', 0):.3f}")
    console.print(f"Total steps: {results.get('total_steps', 0)}")
    console.print(f"Final goal: {results.get('final_goal', 'none')}")
    
    if results.get('total_metrics', 0) > 0:
        console.print(f"Metrics collected: {results['total_metrics']}")
    
    console.print("\n✨ [bold cyan]Demo completed successfully![/bold cyan]")


# Entry point for CLI
def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main() 