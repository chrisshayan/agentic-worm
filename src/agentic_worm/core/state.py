"""
State management for the Agentic Worm system.

This module defines the global state structure that flows through the LangGraph
workflow, maintaining all necessary information about the worm's current condition,
environment, and decision-making process.
"""

from typing import Dict, List, Optional, Any, TypedDict
import numpy as np


class SensoryData(TypedDict):
    """Sensory input from the OpenWorm simulation."""
    chemotaxis: Dict[str, float]  # Chemical gradients
    mechanosensory: Dict[str, float]  # Touch/pressure sensors
    thermosensory: float  # Temperature
    photosensory: float  # Light intensity
    proprioception: Dict[str, float]  # Body position/stretch
    timestamp: float


class NeuralState(TypedDict):
    """Current state of the neural network."""
    neuron_activities: Dict[str, float]  # Individual neuron firing rates
    synaptic_weights: Dict[str, float]  # Current synaptic strengths
    neuromodulator_levels: Dict[str, float]  # Dopamine, serotonin, etc.
    timestamp: float


class MotorCommands(TypedDict):
    """Motor commands to be sent to the simulation."""
    muscle_activations: Dict[str, float]  # Muscle contraction levels
    pharynx_pump: float  # Feeding behavior
    egg_laying: bool  # Reproductive behavior
    timestamp: float


class EnvironmentState(TypedDict):
    """Current environment conditions."""
    food_locations: List[Dict[str, float]]  # Food positions and concentrations
    obstacles: List[Dict[str, Any]]  # Obstacle positions and properties
    temperature_gradient: Dict[str, float]  # Spatial temperature map
    chemical_gradients: Dict[str, Dict[str, float]]  # Chemical concentration maps
    worm_position: Dict[str, float]  # Current worm location and orientation


class DecisionContext(TypedDict):
    """Context for decision-making process."""
    current_goal: Optional[str]  # Current behavioral goal
    goal_priority: float  # Priority level of current goal
    goal_progress: float  # Progress toward current goal (0-1)
    alternative_goals: List[str]  # Other possible goals
    decision_confidence: float  # Confidence in current decision
    last_decision_time: float
    current_decision: Optional[str]  # Current behavioral decision/action
    decision_rationale: Optional[str]  # Reasoning behind current decision


class LearningState(TypedDict):
    """Learning and adaptation state."""
    recent_rewards: List[float]  # Recent reward history
    behavior_success_rates: Dict[str, float]  # Success rates for different behaviors
    exploration_rate: float  # Current exploration vs exploitation balance
    learning_rate: float  # Current learning rate
    memory_strength: Dict[str, float]  # Strength of different memories


class WormState(TypedDict):
    """
    Global state of the Agentic Worm system.
    
    This TypedDict defines the complete state that flows through the LangGraph
    workflow, containing all information needed for the worm's operation.
    """
    # Message history for AI communication
    messages: List[Dict[str, Any]]
    
    # Core simulation state
    sensory_data: SensoryData
    neural_state: NeuralState
    motor_commands: MotorCommands
    environment_state: EnvironmentState
    
    # Decision-making state
    decision_context: DecisionContext
    
    # Learning and adaptation
    learning_state: LearningState
    
    # Simulation metadata
    worm_id: str  # Unique identifier for this worm instance
    simulation_time: float
    step_count: int
    simulation_id: str
    
    # Memory system statistics
    memory_stats: Optional[Dict[str, Any]]
    
    # Status flags
    is_alive: bool
    is_feeding: bool
    is_moving: bool
    is_learning_enabled: bool
    
    # Performance metrics
    fitness_score: float
    energy_level: float
    health_status: float


def create_initial_state(simulation_id: str) -> WormState:
    """
    Create an initial state for a new simulation run.
    
    Args:
        simulation_id: Unique identifier for this simulation
        
    Returns:
        WormState with default initial values
    """
    return WormState(
        messages=[],
        sensory_data=SensoryData(
            chemotaxis={},
            mechanosensory={},
            thermosensory=20.0,  # Room temperature
            photosensory=0.0,
            proprioception={},
            timestamp=0.0
        ),
        neural_state=NeuralState(
            neuron_activities={},
            synaptic_weights={},
            neuromodulator_levels={},
            timestamp=0.0
        ),
        motor_commands=MotorCommands(
            muscle_activations={},
            pharynx_pump=0.0,
            egg_laying=False,
            timestamp=0.0
        ),
        environment_state=EnvironmentState(
            food_locations=[],
            obstacles=[],
            temperature_gradient={},
            chemical_gradients={},
            worm_position={"x": 0.0, "y": 0.0, "z": 0.0, "orientation": 0.0}
        ),
        decision_context=DecisionContext(
            current_goal="explore_environment",  # Default goal instead of None
            goal_priority=0.5,
            goal_progress=0.0,
            alternative_goals=["find_food", "avoid_obstacles", "maintain_health"],
            decision_confidence=0.5,  # Neutral confidence
            last_decision_time=0.0,
            current_decision="initialize_behavior",  # Default decision instead of None
            decision_rationale="Starting simulation with basic exploration behavior"
        ),
        learning_state=LearningState(
            recent_rewards=[],
            behavior_success_rates={},
            exploration_rate=0.1,
            learning_rate=0.001,
            memory_strength={}
        ),
        worm_id=simulation_id,  # Use simulation_id as worm_id by default
        simulation_time=0.0,
        step_count=0,
        simulation_id=simulation_id,
        memory_stats=None,  # Will be populated when memory system is available
        is_alive=True,
        is_feeding=False,
        is_moving=False,
        is_learning_enabled=True,
        fitness_score=0.0,
        energy_level=1.0,
        health_status=1.0
    ) 