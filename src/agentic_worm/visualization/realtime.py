"""
Real-time Visualizer for Agentic Worm System.

This module coordinates real-time visualization updates and provides
interfaces for different visualization backends.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from ..core.state import WormState
from .metrics import MetricsCollector

logger = logging.getLogger(__name__)


class RealtimeVisualizer:
    """
    Coordinates real-time visualization of the agentic worm system.
    
    Manages data flow between the worm system, metrics collection,
    and various visualization outputs (web dashboard, console, etc.).
    """
    
    def __init__(self, update_interval: float = 0.1):
        """
        Initialize the real-time visualizer.
        
        Args:
            update_interval: Interval between visualization updates in seconds
        """
        self.update_interval = update_interval
        self.metrics_collector = MetricsCollector()
        self.is_active = False
        
        # Visualization backends
        self.dashboard_server = None
        self.console_output = True
        
        # Update callbacks
        self.update_callbacks: List[Callable] = []
        
        # State tracking
        self.last_update_time = 0.0
        self.update_count = 0
        
    def connect_dashboard(self, dashboard_server) -> None:
        """Connect a dashboard server for web visualization."""
        self.dashboard_server = dashboard_server
        logger.info("🔗 Dashboard server connected to real-time visualizer")
    
    def add_update_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback function to be called on each update."""
        self.update_callbacks.append(callback)
        logger.info(f"📡 Update callback added: {callback.__name__}")
    
    def remove_update_callback(self, callback: Callable) -> None:
        """Remove an update callback."""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)
            logger.info(f"📡 Update callback removed: {callback.__name__}")
    
    async def start_visualization(self) -> None:
        """Start the real-time visualization loop."""
        if self.is_active:
            logger.warning("⚠️ Visualization already active")
            return
        
        self.is_active = True
        logger.info("🎬 Starting real-time visualization")
        
        try:
            await self._visualization_loop()
        except Exception as e:
            logger.error(f"❌ Visualization loop failed: {e}")
        finally:
            self.is_active = False
    
    async def stop_visualization(self) -> None:
        """Stop the real-time visualization."""
        self.is_active = False
        logger.info("🛑 Real-time visualization stopped")
    
    async def update_from_state(self, state: WormState) -> None:
        """
        Update visualization with new worm state.
        
        Args:
            state: Current worm state to visualize
        """
        current_time = datetime.now().timestamp()
        
        # Collect metrics
        self.metrics_collector.collect_metrics(state)
        
        # Get processed data for visualization
        viz_data = self._prepare_visualization_data(state)
        
        # Update console output
        if self.console_output:
            self._update_console_display(viz_data)
        
        # Update dashboard if connected
        if self.dashboard_server:
            await self._update_dashboard(viz_data)
        
        # Call registered callbacks
        for callback in self.update_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(viz_data)
                else:
                    callback(viz_data)
            except Exception as e:
                logger.error(f"⚠️ Update callback failed: {e}")
        
        # Update tracking
        self.last_update_time = current_time
        self.update_count += 1
    
    def get_visualization_status(self) -> Dict[str, Any]:
        """Get current visualization system status."""
        return {
            "is_active": self.is_active,
            "update_interval": self.update_interval,
            "update_count": self.update_count,
            "last_update_time": self.last_update_time,
            "dashboard_connected": self.dashboard_server is not None,
            "console_output": self.console_output,
            "callback_count": len(self.update_callbacks),
            "metrics_collector_status": "active" if self.metrics_collector else "inactive"
        }
    
    def set_console_output(self, enabled: bool) -> None:
        """Enable or disable console output."""
        self.console_output = enabled
        logger.info(f"📺 Console output {'enabled' if enabled else 'disabled'}")
    
    def reset_visualization(self) -> None:
        """Reset visualization state and metrics."""
        self.metrics_collector.reset_metrics()
        self.update_count = 0
        self.last_update_time = 0.0
        logger.info("🔄 Visualization state reset")
    
    async def _visualization_loop(self) -> None:
        """Main visualization update loop."""
        logger.info("🔄 Visualization loop started")
        
        while self.is_active:
            try:
                # Wait for next update interval
                await asyncio.sleep(self.update_interval)
                
                # Update visualization if there's new data
                # (State updates come from external calls to update_from_state)
                
            except asyncio.CancelledError:
                logger.info("🛑 Visualization loop cancelled")
                break
            except Exception as e:
                logger.error(f"⚠️ Visualization loop error: {e}")
                # Continue running despite errors
                await asyncio.sleep(1.0)
        
        logger.info("🔄 Visualization loop ended")
    
    def _prepare_visualization_data(self, state: WormState) -> Dict[str, Any]:
        """Prepare data for visualization from worm state."""
        # Get real-time metrics
        metrics = self.metrics_collector.get_real_time_metrics()
        
        # Prepare comprehensive visualization data
        viz_data = {
            "timestamp": datetime.now().isoformat(),
            "state": {
                "simulation_time": state["simulation_time"],
                "step_count": state["step_count"],
                "fitness_score": state["fitness_score"],
                "energy_level": state["energy_level"],
                "health_status": state["health_status"],
                "is_moving": state["is_moving"],
                "is_feeding": state["is_feeding"]
            },
            "decision": {
                "current_goal": state["decision_context"]["current_goal"],
                "current_decision": state["decision_context"].get("current_decision"),
                "decision_confidence": state["decision_context"]["decision_confidence"],
                "decision_rationale": state["decision_context"].get("decision_rationale"),
                "goal_progress": state["decision_context"]["goal_progress"]
            },
            "motor": {
                "muscle_activations": state["motor_commands"].get("muscle_activations", {}),
                "pharynx_pump": state["motor_commands"].get("pharynx_pump", 0.0),
                "egg_laying": state["motor_commands"].get("egg_laying", False)
            },
            "sensory": {
                "chemotaxis": state["sensory_data"].get("chemotaxis", {}),
                "mechanosensory": state["sensory_data"].get("mechanosensory", {}),
                "thermosensory": state["sensory_data"].get("thermosensory", 0.0),
                "photosensory": state["sensory_data"].get("photosensory", 0.0)
            },
            "neural": {
                "cognitive_assessment": state["neural_state"].get("cognitive_assessment"),
                "behavioral_strategy": state["neural_state"].get("behavioral_strategy"),
                "activation_patterns": state["neural_state"].get("activation_patterns", {})
            },
            "learning": {
                "recent_rewards": state["learning_state"]["recent_rewards"][-5:],  # Last 5 rewards
                "behavior_success_rates": state["learning_state"]["behavior_success_rates"],
                "adaptation_rate": state["learning_state"].get("adaptation_rate", 0.0)
            },
            "metrics": metrics,
            "performance": self.metrics_collector.get_performance_summary()
        }
        
        return viz_data
    
    def _update_console_display(self, viz_data: Dict[str, Any]) -> None:
        """Update console display with current data."""
        if not self.console_output:
            return
        
        state = viz_data["state"]
        decision = viz_data["decision"]
        
        # Create a concise status line
        status_line = (
            f"🧠 Step {state['step_count']:>4} | "
            f"Goal: {decision['current_goal']:<15} | "
            f"Action: {decision['current_decision']:<12} | "
            f"Confidence: {decision['decision_confidence']:.2f} | "
            f"Fitness: {state['fitness_score']:.3f} | "
            f"Energy: {state['energy_level']:.2f}"
        )
        
        # Only print every 10 updates to avoid spam
        if self.update_count % 10 == 0:
            print(f"\r{status_line}", end="", flush=True)
    
    async def _update_dashboard(self, viz_data: Dict[str, Any]) -> None:
        """Update dashboard with visualization data."""
        if not self.dashboard_server or not hasattr(self.dashboard_server, '_broadcast_update'):
            return
        
        try:
            # Send update to dashboard
            await self.dashboard_server._broadcast_update({
                "type": "visualization_update",
                "data": viz_data
            })
        except Exception as e:
            logger.error(f"⚠️ Dashboard update failed: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of collected metrics."""
        return self.metrics_collector.get_performance_summary()
    
    def get_behavioral_analysis(self) -> Dict[str, Any]:
        """Get behavioral pattern analysis."""
        return self.metrics_collector.get_behavioral_patterns()
    
    def export_metrics_data(self, format: str = "json") -> Dict[str, Any]:
        """
        Export collected metrics data.
        
        Args:
            format: Export format ('json', 'csv', etc.)
        
        Returns:
            Exported data in the specified format
        """
        if format == "json":
            return {
                "session_summary": self.metrics_collector.get_performance_summary(),
                "behavioral_patterns": self.metrics_collector.get_behavioral_patterns(),
                "time_series": {
                    "fitness": self.metrics_collector.get_time_series_data("fitness"),
                    "energy": self.metrics_collector.get_time_series_data("energy"),
                    "confidence": self.metrics_collector.get_time_series_data("confidence")
                },
                "decisions": self.metrics_collector.get_recent_decisions(100),  # Last 100 decisions
                "goal_switches": self.metrics_collector.goal_switches,
                "learning_events": self.metrics_collector.learning_events
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Convenience functions for quick visualization setup

def create_basic_visualizer(console_output: bool = True) -> RealtimeVisualizer:
    """Create a basic real-time visualizer with console output."""
    visualizer = RealtimeVisualizer()
    visualizer.set_console_output(console_output)
    return visualizer

def create_dashboard_visualizer(port: int = 8888) -> tuple[RealtimeVisualizer, Any]:
    """Create a visualizer with web dashboard."""
    from .dashboard import DashboardServer
    
    visualizer = RealtimeVisualizer()
    dashboard = DashboardServer(port=port)
    
    visualizer.connect_dashboard(dashboard)
    
    return visualizer, dashboard 