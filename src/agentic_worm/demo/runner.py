"""
Demo runner for showcasing the Agentic Worm system.

This module provides an easy-to-use interface for running demonstrations
and showcases of the agentic worm behavior, with built-in visualization
and metrics collection.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

from ..core import AgenticWormSystem


logger = logging.getLogger(__name__)


class DemoRunner:
    """
    Demo runner for showcasing Agentic Worm capabilities.
    
    This class provides a high-level interface for running demonstrations,
    collecting metrics, and visualizing the agentic behavior in action.
    """
    
    def __init__(
        self,
        demo_name: str = "default_demo",
        duration_seconds: float = 60.0,
        enable_recording: bool = True,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize the demo runner.
        
        Args:
            demo_name: Name for this demo run
            duration_seconds: How long to run the demo
            enable_recording: Whether to record demo data
            output_dir: Directory to save demo outputs
        """
        self.demo_name = demo_name
        self.duration_seconds = duration_seconds
        self.enable_recording = enable_recording
        self.output_dir = output_dir or Path("demo_outputs")
        
        # Demo state
        self.system: Optional[AgenticWormSystem] = None
        self.start_time: Optional[float] = None
        self.metrics_history: List[Dict[str, Any]] = []
        self.is_running = False
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"DemoRunner initialized: {demo_name}")
    
    async def run_basic_demo(self) -> Dict[str, Any]:
        """
        Run a basic demonstration of the agentic worm.
        
        Returns:
            Demo results and metrics
        """
        logger.info(f"Starting basic demo: {self.demo_name}")
        
        try:
            # Initialize the system
            await self._initialize_system()
            
            # Set initial goal
            if self.system:
                await self.system.set_goal("explore_environment", priority=0.8)
            
            # Run the demo
            results = await self._run_demo_loop()
            
            # Generate summary
            summary = await self._generate_demo_summary(results)
            
            logger.info("Basic demo completed successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def run_food_seeking_demo(self) -> Dict[str, Any]:
        """
        Run a demonstration of food-seeking behavior.
        
        Returns:
            Demo results showing food-seeking capabilities
        """
        logger.info("Starting food-seeking demo")
        
        try:
            await self._initialize_system()
            
            # Set food-seeking goal
            await self.system.set_goal("find_food", priority=1.0)
            
            # TODO: Add food to the environment
            # await self._add_food_to_environment()
            
            results = await self._run_demo_loop()
            summary = await self._generate_demo_summary(results)
            
            return summary
            
        except Exception as e:
            logger.error(f"Food-seeking demo failed: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def run_obstacle_avoidance_demo(self) -> Dict[str, Any]:
        """
        Run a demonstration of obstacle avoidance behavior.
        
        Returns:
            Demo results showing obstacle avoidance capabilities
        """
        logger.info("Starting obstacle avoidance demo")
        
        try:
            await self._initialize_system()
            
            # Set navigation goal with obstacles
            await self.system.set_goal("navigate_obstacles", priority=0.9)
            
            # TODO: Add obstacles to the environment
            # await self._add_obstacles_to_environment()
            
            results = await self._run_demo_loop()
            summary = await self._generate_demo_summary(results)
            
            return summary
            
        except Exception as e:
            logger.error(f"Obstacle avoidance demo failed: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def run_learning_demo(self) -> Dict[str, Any]:
        """
        Run a demonstration of learning and adaptation.
        
        Returns:
            Demo results showing learning capabilities
        """
        logger.info("Starting learning demo")
        
        try:
            await self._initialize_system()
            
            # Enable learning
            if self.system.current_state:
                self.system.current_state["is_learning_enabled"] = True
            
            # Set learning goal
            await self.system.set_goal("learn_optimal_foraging", priority=1.0)
            
            results = await self._run_demo_loop()
            summary = await self._generate_demo_summary(results)
            
            return summary
            
        except Exception as e:
            logger.error(f"Learning demo failed: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics during demo."""
        if not self.system:
            return {}
        
        metrics = await self.system.get_performance_metrics()
        
        # Add demo-specific metrics
        if self.start_time:
            metrics["demo_elapsed_time"] = time.time() - self.start_time
            metrics["demo_progress"] = min(1.0, metrics["demo_elapsed_time"] / self.duration_seconds)
        
        return metrics
    
    # Private methods
    
    async def _initialize_system(self) -> None:
        """Initialize the agentic worm system for demo."""
        self.system = AgenticWormSystem(
            simulation_id=f"demo_{self.demo_name}_{int(time.time())}",
            enable_visualization=True,
            enable_learning=True
        )
        
        await self.system.initialize()
        logger.info("Demo system initialized")
    
    async def _run_demo_loop(self) -> Dict[str, Any]:
        """Run the main demo loop."""
        self.start_time = time.time()
        self.is_running = True
        
        # Start the simulation in the background
        simulation_task = asyncio.create_task(self.system.start_simulation())
        
        # Collect metrics during the demo
        metrics_task = asyncio.create_task(self._collect_metrics())
        
        try:
            # Wait for demo duration or simulation completion
            await asyncio.wait_for(
                asyncio.gather(simulation_task, metrics_task),
                timeout=self.duration_seconds
            )
        except asyncio.TimeoutError:
            logger.info("Demo completed - time limit reached")
        except Exception as e:
            logger.error(f"Demo loop error: {e}")
        finally:
            self.is_running = False
            
            # Stop the simulation
            await self.system.stop_simulation()
            
            # Cancel remaining tasks
            for task in [simulation_task, metrics_task]:
                if not task.done():
                    task.cancel()
        
        return {
            "duration": time.time() - self.start_time,
            "metrics_collected": len(self.metrics_history),
            "final_state": await self.system.get_current_state()
        }
    
    async def _collect_metrics(self) -> None:
        """Collect metrics during the demo run."""
        while self.is_running:
            try:
                metrics = await self.get_real_time_metrics()
                metrics["timestamp"] = time.time()
                
                self.metrics_history.append(metrics)
                
                # Save metrics if recording is enabled
                if self.enable_recording and len(self.metrics_history) % 100 == 0:
                    await self._save_metrics_checkpoint()
                
                await asyncio.sleep(0.1)  # Collect metrics every 100ms
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(1.0)  # Wait longer on error
    
    async def _save_metrics_checkpoint(self) -> None:
        """Save a checkpoint of metrics data."""
        if not self.enable_recording:
            return
        
        metrics_file = self.output_dir / f"{self.demo_name}_metrics.json"
        
        try:
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics checkpoint: {e}")
    
    async def _generate_demo_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the demo results."""
        summary = {
            "demo_name": self.demo_name,
            "duration": results.get("duration", 0),
            "total_metrics": len(self.metrics_history),
            "start_time": self.start_time,
            "end_time": time.time()
        }
        
        # Add performance statistics
        if self.metrics_history:
            final_metrics = self.metrics_history[-1]
            summary.update({
                "final_fitness_score": final_metrics.get("fitness_score", 0),
                "final_energy_level": final_metrics.get("energy_level", 0),
                "final_health_status": final_metrics.get("health_status", 0),
                "total_steps": final_metrics.get("step_count", 0),
                "final_goal": final_metrics.get("current_goal", "none")
            })
        
        # Save summary
        if self.enable_recording:
            summary_file = self.output_dir / f"{self.demo_name}_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
        
        return summary
    
    async def _cleanup(self) -> None:
        """Clean up demo resources."""
        if self.system:
            await self.system.stop_simulation()
        
        # Final metrics save
        if self.enable_recording and self.metrics_history:
            await self._save_metrics_checkpoint()
        
        logger.info("Demo cleanup completed")


# Convenience functions for quick demos

async def run_quick_demo(demo_type: str = "basic", duration: float = 30.0) -> Dict[str, Any]:
    """
    Run a quick demonstration.
    
    Args:
        demo_type: Type of demo ("basic", "food_seeking", "obstacle_avoidance", "learning")
        duration: Duration in seconds
        
    Returns:
        Demo results
    """
    runner = DemoRunner(
        demo_name=f"quick_{demo_type}",
        duration_seconds=duration,
        enable_recording=True
    )
    
    if demo_type == "food_seeking":
        return await runner.run_food_seeking_demo()
    elif demo_type == "obstacle_avoidance":
        return await runner.run_obstacle_avoidance_demo()
    elif demo_type == "learning":
        return await runner.run_learning_demo()
    else:
        return await runner.run_basic_demo() 