"""
Main system orchestrator for the Agentic Worm.

This module contains the core AgenticWormSystem class that coordinates
the integration between OpenWorm simulation, AI intelligence layer,
and LangGraph workflow management.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import uuid

from .state import WormState, create_initial_state


logger = logging.getLogger(__name__)


class AgenticWormSystem:
    """
    Main orchestrator for the Agentic Worm system.
    
    This class manages the integration between:
    - OpenWorm simulation (c302, Sibernetic, Geppetto)
    - AI intelligence layer (perception, cognition, decision-making)
    - LangGraph workflow orchestration
    - Real-time visualization and monitoring
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        simulation_id: Optional[str] = None,
        enable_visualization: bool = True,
        enable_learning: bool = True
    ):
        """
        Initialize the Agentic Worm system.
        
        Args:
            config_path: Path to configuration file
            simulation_id: Unique identifier for this simulation run
            enable_visualization: Whether to enable real-time visualization
            enable_learning: Whether to enable learning and adaptation
        """
        self.simulation_id = simulation_id or str(uuid.uuid4())
        self.config_path = config_path
        self.enable_visualization = enable_visualization
        self.enable_learning = enable_learning
        
        # System components (will be initialized in setup)
        self.openworm_interface = None
        self.langgraph_workflow = None
        self.visualization_dashboard = None
        self.state_store = None
        
        # Current system state
        self.current_state: Optional[WormState] = None
        self.is_running = False
        self.is_initialized = False
        
        logger.info(f"AgenticWormSystem initialized with ID: {self.simulation_id}")
    
    async def initialize(self) -> None:
        """
        Initialize all system components.
        
        This sets up:
        1. OpenWorm simulation interface
        2. LangGraph workflow
        3. Visualization dashboard (if enabled)
        4. State management
        """
        try:
            logger.info("Initializing Agentic Worm system...")
            
            # Initialize state
            self.current_state = create_initial_state(self.simulation_id)
            
            # Initialize OpenWorm interface
            await self._initialize_openworm()
            
            # Initialize LangGraph workflow
            await self._initialize_langgraph()
            
            # Initialize visualization (if enabled)
            if self.enable_visualization:
                await self._initialize_visualization()
            
            # Initialize state store
            await self._initialize_state_store()
            
            self.is_initialized = True
            logger.info("Agentic Worm system initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise
    
    async def start_simulation(self) -> None:
        """Start the main simulation loop."""
        if not self.is_initialized:
            await self.initialize()
        
        logger.info("Starting Agentic Worm simulation...")
        self.is_running = True
        
        try:
            # Start the main control loop
            await self._run_main_loop()
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            raise
        finally:
            await self.stop_simulation()
    
    async def stop_simulation(self) -> None:
        """Stop the simulation and cleanup resources."""
        logger.info("Stopping Agentic Worm simulation...")
        self.is_running = False
        
        # Cleanup components
        # TODO: Implement proper cleanup once components are implemented
        pass
        
        logger.info("Simulation stopped")
    
    async def get_current_state(self) -> Optional[WormState]:
        """Get the current system state."""
        return self.current_state
    
    async def set_goal(self, goal: str, priority: float = 1.0) -> None:
        """
        Set a new behavioral goal for the worm.
        
        Args:
            goal: Goal description (e.g., "find_food", "avoid_obstacle")
            priority: Goal priority (0.0 to 1.0)
        """
        if self.current_state:
            self.current_state["decision_context"]["current_goal"] = goal
            self.current_state["decision_context"]["goal_priority"] = priority
            logger.info(f"New goal set: {goal} (priority: {priority})")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.current_state:
            return {}
        
        return {
            "fitness_score": self.current_state["fitness_score"],
            "energy_level": self.current_state["energy_level"],
            "health_status": self.current_state["health_status"],
            "simulation_time": self.current_state["simulation_time"],
            "step_count": self.current_state["step_count"],
            "current_goal": self.current_state["decision_context"]["current_goal"],
            "goal_progress": self.current_state["decision_context"]["goal_progress"]
        }
    
    # Private methods for component initialization
    
    async def _initialize_openworm(self) -> None:
        """Initialize OpenWorm simulation interface."""
        # This will be implemented to connect to OpenWorm Docker containers
        logger.info("Initializing OpenWorm interface...")
        # TODO: Implement OpenWorm Docker integration
        pass
    
    async def _initialize_langgraph(self) -> None:
        """Initialize LangGraph workflow."""
        logger.info("Initializing LangGraph workflow...")
        
        # Import and initialize the agentic workflow
        try:
            from ..intelligence.workflow import AgenticWorkflow
            
            self.agentic_workflow = AgenticWorkflow(enable_learning=self.enable_learning)
            await self.agentic_workflow.initialize()
            
            logger.info("✅ LangGraph workflow initialized with agentic intelligence")
        except ImportError as e:
            logger.warning(f"⚠️ Could not import LangGraph components: {e}")
            self.agentic_workflow = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize LangGraph workflow: {e}")
            self.agentic_workflow = None
    
    async def _initialize_visualization(self) -> None:
        """Initialize real-time visualization dashboard."""
        logger.info("Initializing visualization dashboard...")
        
        if not self.enable_visualization:
            logger.info("📊 Visualization disabled")
            return
        
        try:
            from ..visualization.realtime import RealtimeVisualizer
            from ..visualization.dashboard import DashboardServer
            
            # Create real-time visualizer
            self.visualizer = RealtimeVisualizer(update_interval=0.1)
            
            # Create dashboard server if FastAPI is available
            try:
                self.dashboard = DashboardServer(port=8888, host="localhost")
                self.visualizer.connect_dashboard(self.dashboard)
                self.dashboard.connect_worm_system(self)
                
                logger.info("✅ Web dashboard initialized at http://localhost:8888")
            except Exception as e:
                logger.warning(f"⚠️ Web dashboard unavailable: {e}")
                self.dashboard = None
                # Fall back to console visualization
                self.visualizer.set_console_output(True)
            
            logger.info("✅ Visualization system initialized")
            
        except ImportError as e:
            logger.warning(f"⚠️ Could not import visualization components: {e}")
            self.visualizer = None
            self.dashboard = None
    
    async def _initialize_state_store(self) -> None:
        """Initialize state management and persistence."""
        logger.info("Initializing state store...")
        # TODO: Implement state persistence
        pass
    
    async def _run_main_loop(self) -> None:
        """Run the main simulation control loop."""
        while self.is_running:
            try:
                # Step the simulation
                await self._step_simulation()
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.01)  # 100 Hz update rate
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                break
    
    async def _step_simulation(self) -> None:
        """Execute one step of the simulation."""
        if not self.current_state:
            return
        
        # Update step count and simulation time
        self.current_state["step_count"] += 1
        self.current_state["simulation_time"] += 0.01  # 10ms time step
        
        # Run the agentic intelligence pipeline
        if hasattr(self, 'agentic_workflow') and self.agentic_workflow:
            try:
                # Run the perception → cognition → action pipeline
                self.current_state = await self.agentic_workflow.process_step(self.current_state)
                
                # Update fitness score based on goal achievement
                self._update_fitness_score()
                
                # Log significant decisions (every 50 steps)
                if self.current_state["step_count"] % 50 == 0:
                    decision = self.current_state["decision_context"].get("current_decision", "none")
                    confidence = self.current_state["decision_context"].get("decision_confidence", 0)
                    logger.info(f"Step {self.current_state['step_count']}: Decision: {decision}, "
                              f"Confidence: {confidence:.2f}, Fitness: {self.current_state['fitness_score']:.3f}")
                
            except Exception as e:
                logger.error(f"⚠️ Agentic workflow step failed: {e}")
                # Fallback behavior
                self._fallback_behavior()
        else:
            # Fallback to basic simulation
            self._fallback_behavior()
            
        # Update energy and health (simple degradation over time)
        self._update_biological_metrics()
        
        # Update visualization if available
        if hasattr(self, 'visualizer') and self.visualizer:
            try:
                await self.visualizer.update_from_state(self.current_state)
            except Exception as e:
                logger.error(f"⚠️ Visualization update failed: {e}")
    
    def _update_fitness_score(self) -> None:
        """Update fitness score based on goal achievement and behavior."""
        if not self.current_state:
            return
            
        # Get current metrics
        goal = self.current_state["decision_context"]["current_goal"]
        goal_progress = self.current_state["decision_context"]["goal_progress"]
        energy = self.current_state["energy_level"]
        health = self.current_state["health_status"]
        
        # Calculate fitness based on multiple factors
        fitness_increment = 0.0
        
        # Reward goal progress
        if goal_progress > 0.5:
            fitness_increment += 0.001
        
        # Reward maintaining health and energy
        if energy > 0.5 and health > 0.5:
            fitness_increment += 0.0005
            
        # Reward making decisions (being active)
        if self.current_state["decision_context"].get("decision_confidence", 0) > 0.7:
            fitness_increment += 0.0003
            
        # Update fitness with bounds
        self.current_state["fitness_score"] = min(1.0, 
            self.current_state["fitness_score"] + fitness_increment)
    
    def _update_biological_metrics(self) -> None:
        """Update energy and health metrics."""
        if not self.current_state:
            return
            
        # Gradual energy consumption
        energy_consumption = 0.001 if self.current_state["is_moving"] else 0.0005
        self.current_state["energy_level"] = max(0.0, 
            self.current_state["energy_level"] - energy_consumption)
        
        # Health slightly affected by low energy
        if self.current_state["energy_level"] < 0.2:
            health_decline = 0.0002
            self.current_state["health_status"] = max(0.0,
                self.current_state["health_status"] - health_decline)
        
        # Feeding restores energy
        if self.current_state["is_feeding"]:
            energy_gain = 0.005
            self.current_state["energy_level"] = min(1.0,
                self.current_state["energy_level"] + energy_gain)
    
    def _fallback_behavior(self) -> None:
        """Fallback behavior when agentic workflow is not available."""
        if not self.current_state:
            return
            
        # Simple alternating movement pattern
        step = self.current_state["step_count"]
        if step % 30 < 20:
            action = "move_forward"
            self.current_state["is_moving"] = True
        elif step % 30 < 25:
            action = "turn_left" 
            self.current_state["is_moving"] = True
        else:
            action = "idle"
            self.current_state["is_moving"] = False
            
        # Update decision context
        self.current_state["decision_context"]["current_decision"] = action
        self.current_state["decision_context"]["decision_confidence"] = 0.3  # Low confidence for fallback


# Convenience function for quick demo setup
async def create_demo_system(enable_visualization: bool = True) -> AgenticWormSystem:
    """
    Create a pre-configured Agentic Worm system for demonstration.
    
    Args:
        enable_visualization: Whether to enable visualization
        
    Returns:
        Configured AgenticWormSystem ready for demo
    """
    system = AgenticWormSystem(
        simulation_id=f"demo_{uuid.uuid4().hex[:8]}",
        enable_visualization=enable_visualization,
        enable_learning=True
    )
    
    await system.initialize()
    return system 