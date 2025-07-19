"""
Real LangGraph Workflow for Agentic Worm Intelligence.

This module implements the core AI decision-making pipeline using LangGraph's
StateGraph system. It processes sensory input through multiple nodes
to generate intelligent behavior in a proper LangGraph workflow.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, TypedDict, Literal, Annotated
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.graph.message import add_messages
    from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
    from langchain_core.runnables import RunnableConfig
    LANGGRAPH_AVAILABLE = True
    print("✅ LangGraph imported successfully")
except ImportError:
    print("⚠️ LangGraph not available - using fallback implementation")
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = "END"
    START = "START"

from ..core.state import WormState

logger = logging.getLogger(__name__)


class LangGraphWormState(TypedDict):
    """
    LangGraph-compatible state structure for the agentic worm.
    
    This extends our base WormState with LangGraph-specific fields
    for proper message passing and workflow coordination.
    """
    # Core worm state
    worm_id: str
    simulation_time: float
    fitness_score: float
    energy_level: float
    
    # Sensory information
    sensory_data: Dict[str, Any]
    
    # Neural activity
    neural_state: Dict[str, Any]
    
    # Motor commands
    motor_commands: Dict[str, float]
    
    # Decision making
    decision_context: Dict[str, Any]
    
    # LangGraph workflow fields
    messages: Annotated[list[BaseMessage], add_messages]
    current_step: str
    workflow_active: bool
    last_decision_time: float
    decision_rationale: str
    next_action: str
    processing_errors: list[str]


class AgenticWorkflow:
    """
    Real LangGraph workflow orchestrator for the Agentic Worm.
    
    This class implements a proper LangGraph StateGraph with nodes for:
    - Perception processing
    - Cognitive analysis  
    - Decision making
    - Motor control
    - Learning adaptation
    """
    
    def __init__(self, enable_learning: bool = True):
        """
        Initialize the LangGraph agentic workflow.
        
        Args:
            enable_learning: Whether to enable learning and adaptation
        """
        self.enable_learning = enable_learning
        self.workflow_graph = None
        self.is_initialized = False
        
        # Performance tracking
        self.decision_count = 0
        self.successful_actions = 0
        self.learning_rate = 0.01 if enable_learning else 0.0
        
        # Initialize the graph
        if LANGGRAPH_AVAILABLE:
            self._build_langgraph_workflow()
        else:
            print("⚠️ Using fallback workflow (LangGraph not available)")
    
    def _build_langgraph_workflow(self) -> None:
        """Build the actual LangGraph StateGraph workflow."""
        if not LANGGRAPH_AVAILABLE:
            return
            
        try:
            # Create the StateGraph
            workflow = StateGraph(LangGraphWormState)
            
            # Add nodes for each processing step
            workflow.add_node("perception", self._perception_node)
            workflow.add_node("cognition", self._cognition_node)
            workflow.add_node("decision", self._decision_node)
            workflow.add_node("action", self._action_node)
            
            if self.enable_learning:
                workflow.add_node("learning", self._learning_node)
            
            # Define the workflow edges (perception → cognition → decision → action → learning)
            workflow.add_edge(START, "perception")
            workflow.add_edge("perception", "cognition")
            workflow.add_edge("cognition", "decision")
            workflow.add_edge("action", "learning" if self.enable_learning else END)
            
            # Add conditional edge for decision → action
            workflow.add_conditional_edges(
                "decision",
                self._should_take_action,
                {
                    "take_action": "action",
                    "skip_action": "learning" if self.enable_learning else END
                }
            )
            
            if self.enable_learning:
                workflow.add_edge("learning", END)
            
            # Compile the workflow
            self.workflow_graph = workflow.compile()
            print("✅ Real LangGraph workflow compiled successfully")
            
        except Exception as e:
            print(f"❌ Failed to build LangGraph workflow: {e}")
            self.workflow_graph = None
    
    async def initialize(self) -> None:
        """Initialize the LangGraph workflow system."""
        if LANGGRAPH_AVAILABLE and self.workflow_graph is not None:
            self.is_initialized = True
            print("✅ LangGraph workflow initialized successfully")
        else:
            print("⚠️ Using fallback workflow initialization")
            self.is_initialized = True
    
    async def process_step(self, state: WormState) -> WormState:
        """
        Process one step using the LangGraph workflow.
        
        Args:
            state: Current worm state
            
        Returns:
            Updated worm state after LangGraph processing
        """
        if not self.is_initialized:
            await self.initialize()
        
        if LANGGRAPH_AVAILABLE and self.workflow_graph is not None:
            return await self._process_with_langgraph(state)
        else:
            return await self._process_with_fallback(state)
    
    async def _process_with_langgraph(self, state: WormState) -> WormState:
        """Process using real LangGraph StateGraph."""
        try:
            # Convert WormState to LangGraphWormState
            langgraph_state = self._convert_to_langgraph_state(state)
            
            # Add initial message to trigger workflow
            initial_message = HumanMessage(
                content=f"Process worm step - Goal: {state['decision_context'].get('current_goal', 'explore')}"
            )
            langgraph_state["messages"] = [initial_message]
            langgraph_state["current_step"] = "starting"
            langgraph_state["workflow_active"] = True
            
            # Run the LangGraph workflow
            config = RunnableConfig({"thread_id": state["worm_id"]})
            result = await self.workflow_graph.ainvoke(langgraph_state, config=config)
            
            # Convert back to WormState
            updated_state = self._convert_from_langgraph_state(result, state)
            
            self.decision_count += 1
            print(f"🧠 LangGraph step {self.decision_count} completed successfully")
            
            return updated_state
            
        except Exception as e:
            print(f"⚠️ LangGraph processing failed: {e}")
            return await self._process_with_fallback(state)
    
    async def _process_with_fallback(self, state: WormState) -> WormState:
        """Fallback processing when LangGraph is not available."""
        try:
            # Simple perception → decision → action pipeline
            current_time = datetime.now().timestamp()
            
            # Update simulation time
            state["simulation_time"] = current_time
            
            # Basic decision making
            goal = state["decision_context"].get("current_goal", "explore")
            fitness_change = 0.001 * (1.0 if goal == "find_food" else 0.5)
            state["fitness_score"] = min(1.0, state["fitness_score"] + fitness_change)
            
            # Update decision context
            state["decision_context"]["current_decision"] = f"fallback_{goal}"
            state["decision_context"]["decision_confidence"] = 0.7
            state["decision_context"]["last_decision_time"] = current_time
            
            # Add message for tracking
            if "messages" not in state:
                state["messages"] = []
            
            state["messages"].append({
                "role": "system",
                "content": f"Fallback processing: {goal}",
                "timestamp": current_time
            })
            
            self.decision_count += 1
            return state
            
        except Exception as e:
            print(f"❌ Fallback processing failed: {e}")
            return state
    
    # LangGraph Node Functions
    async def _perception_node(self, state: LangGraphWormState) -> LangGraphWormState:
        """LangGraph node for perception processing."""
        try:
            current_time = datetime.now().timestamp()
            
            # Try to get OpenWorm sensory data
            try:
                from .openworm import get_openworm_client
                client = get_openworm_client()
                
                if client.is_connected:
                    sensory_data = await client.get_sensory_data()
                    state["sensory_data"]["chemotaxis"] = sensory_data.get("chemotaxis", {})
                    state["sensory_data"]["mechanosensory"] = sensory_data.get("mechanosensory", {})
                    
                    perception_msg = AIMessage(
                        content=f"🧠 PERCEPTION (OpenWorm): Chemical gradient detected"
                    )
                else:
                    # Enhanced simulation
                    goal = state["decision_context"].get("current_goal", "explore")
                    chemical_strength = 0.3 + 0.2 * (current_time % 10) / 10
                    
                    state["sensory_data"]["chemotaxis"] = {
                        "food_gradient": chemical_strength,
                        "timestamp": current_time
                    }
                    
                    perception_msg = AIMessage(
                        content=f"🧠 PERCEPTION (Simulated): Chemical={chemical_strength:.2f}"
                    )
                    
            except Exception:
                # Basic fallback
                perception_msg = AIMessage(content="🧠 PERCEPTION: Basic sensory processing")
            
            state["messages"].append(perception_msg)
            state["current_step"] = "perception_complete"
            return state
            
        except Exception as e:
            state["processing_errors"].append(f"Perception error: {e}")
            return state
    
    async def _cognition_node(self, state: LangGraphWormState) -> LangGraphWormState:
        """LangGraph node for cognitive processing."""
        try:
            current_time = datetime.now().timestamp()
            
            # Analyze current situation
            goal = state["decision_context"].get("current_goal", "explore")
            fitness = state["fitness_score"]
            energy = state["energy_level"]
            
            # Cognitive assessment
            if goal == "find_food" and fitness < 0.5:
                cognitive_assessment = "food_seeking_urgent"
                strategy = "aggressive_chemotaxis"
            elif goal == "explore" and energy > 0.7:
                cognitive_assessment = "exploration_optimal"
                strategy = "systematic_mapping"
            else:
                cognitive_assessment = "standard_behavior"
                strategy = "balanced_approach"
            
            # Update decision context
            state["decision_context"]["cognitive_assessment"] = cognitive_assessment
            state["decision_context"]["behavioral_strategy"] = strategy
            state["decision_context"]["analysis_time"] = current_time
            
            cognition_msg = AIMessage(
                content=f"🤔 COGNITION: Assessment={cognitive_assessment}, Strategy={strategy}"
            )
            state["messages"].append(cognition_msg)
            state["current_step"] = "cognition_complete"
            
            return state
            
        except Exception as e:
            state["processing_errors"].append(f"Cognition error: {e}")
            return state
    
    async def _decision_node(self, state: LangGraphWormState) -> LangGraphWormState:
        """LangGraph node for decision making."""
        try:
            current_time = datetime.now().timestamp()
            
            # Get cognitive assessment
            assessment = state["decision_context"].get("cognitive_assessment", "standard_behavior")
            strategy = state["decision_context"].get("behavioral_strategy", "balanced_approach")
            
            # Make decision based on assessment
            if assessment == "food_seeking_urgent":
                decision = "seek_food_aggressively"
                confidence = 0.9
                action_type = "motor_activation"
            elif assessment == "exploration_optimal":
                decision = "explore_systematically"
                confidence = 0.8
                action_type = "navigation"
            else:
                decision = "maintain_current_behavior"
                confidence = 0.6
                action_type = "continue"
            
            # Update decision context
            state["decision_context"]["current_decision"] = decision
            state["decision_context"]["decision_confidence"] = confidence
            state["decision_context"]["last_decision_time"] = current_time
            state["decision_rationale"] = f"Based on {assessment} using {strategy}"
            state["next_action"] = action_type
            
            decision_msg = AIMessage(
                content=f"🎯 DECISION: {decision} (confidence: {confidence:.2f})"
            )
            state["messages"].append(decision_msg)
            state["current_step"] = "decision_complete"
            
            return state
            
        except Exception as e:
            state["processing_errors"].append(f"Decision error: {e}")
            return state
    
    def _should_take_action(self, state: LangGraphWormState) -> Literal["take_action", "skip_action"]:
        """Conditional edge function to determine if action should be taken."""
        confidence = state["decision_context"].get("decision_confidence", 0.0)
        action_type = state.get("next_action", "continue")
        
        # Take action if confidence is high enough and action is needed
        if confidence > 0.5 and action_type != "continue":
            return "take_action"
        else:
            return "skip_action"
    
    async def _action_node(self, state: LangGraphWormState) -> LangGraphWormState:
        """LangGraph node for motor action execution."""
        try:
            current_time = datetime.now().timestamp()
            
            decision = state["decision_context"].get("current_decision", "maintain_current_behavior")
            confidence = state["decision_context"].get("decision_confidence", 0.5)
            
            # Generate motor commands based on decision
            if "food" in decision:
                # Food-seeking motor pattern
                dorsal_activation = 0.6 + 0.2 * confidence
                ventral_activation = 0.4 + 0.1 * confidence
            elif "explore" in decision:
                # Exploration motor pattern
                dorsal_activation = 0.5
                ventral_activation = 0.5
            else:
                # Default motor pattern
                dorsal_activation = 0.3
                ventral_activation = 0.3
            
            # Update motor commands in correct structure
            if "muscle_activations" not in state["motor_commands"]:
                state["motor_commands"]["muscle_activations"] = {}
            
            state["motor_commands"]["muscle_activations"]["dorsal"] = min(1.0, dorsal_activation)
            state["motor_commands"]["muscle_activations"]["ventral"] = min(1.0, ventral_activation)
            state["motor_commands"]["timestamp"] = current_time
            
            # Try to send to OpenWorm motor interface
            try:
                from .openworm import get_openworm_client
                client = get_openworm_client()
                await client.send_motor_commands(state["motor_commands"])
                action_status = "sent_to_openworm"
            except Exception:
                action_status = "simulated"
            
            action_msg = AIMessage(
                content=f"⚡ ACTION: Motor commands executed ({action_status})"
            )
            state["messages"].append(action_msg)
            state["current_step"] = "action_complete"
            
            # Update fitness based on action
            fitness_gain = 0.01 * confidence
            state["fitness_score"] = min(1.0, state["fitness_score"] + fitness_gain)
            
            return state
            
        except Exception as e:
            state["processing_errors"].append(f"Action error: {e}")
            return state
    
    async def _learning_node(self, state: LangGraphWormState) -> LangGraphWormState:
        """LangGraph node for learning and adaptation."""
        if not self.enable_learning:
            return state
            
        try:
            current_time = datetime.now().timestamp()
            
            # Evaluate action success
            decision = state["decision_context"].get("current_decision", "")
            confidence = state["decision_context"].get("decision_confidence", 0.5)
            fitness_before = state.get("previous_fitness", state["fitness_score"])
            fitness_after = state["fitness_score"]
            
            # Simple learning: adjust based on fitness change
            fitness_change = fitness_after - fitness_before
            
            if fitness_change > 0:
                # Successful action - reinforce
                self.successful_actions += 1
                learning_outcome = "positive_reinforcement"
            else:
                # Unsuccessful action - adjust
                learning_outcome = "negative_feedback"
            
            # Update learning metrics
            success_rate = self.successful_actions / self.decision_count if self.decision_count > 0 else 0
            
            learning_msg = AIMessage(
                content=f"📚 LEARNING: {learning_outcome}, Success rate: {success_rate:.2f}"
            )
            state["messages"].append(learning_msg)
            state["current_step"] = "learning_complete"
            state["workflow_active"] = False
            
            return state
            
        except Exception as e:
            state["processing_errors"].append(f"Learning error: {e}")
            return state
    
    def _convert_to_langgraph_state(self, worm_state: WormState) -> LangGraphWormState:
        """Convert WormState to LangGraphWormState."""
        return {
            "worm_id": worm_state["worm_id"],
            "simulation_time": worm_state["simulation_time"],
            "fitness_score": worm_state["fitness_score"],
            "energy_level": worm_state["energy_level"],
            "sensory_data": dict(worm_state["sensory_data"]),  # Convert to Dict[str, Any]
            "neural_state": dict(worm_state["neural_state"]),  # Convert to Dict[str, Any]
            "motor_commands": dict(worm_state["motor_commands"]),  # Convert to Dict[str, float]
            "decision_context": dict(worm_state["decision_context"]),  # Convert to Dict[str, Any]
            "messages": [],
            "current_step": "initialized",
            "workflow_active": True,
            "last_decision_time": datetime.now().timestamp(),
            "decision_rationale": "",
            "next_action": "",
            "processing_errors": []
        }
    
    def _convert_from_langgraph_state(self, langgraph_state: LangGraphWormState, original_state: WormState) -> WormState:
        """Convert LangGraphWormState back to WormState."""
        # Update the original state with processed values
        original_state["simulation_time"] = langgraph_state["simulation_time"]
        original_state["fitness_score"] = langgraph_state["fitness_score"]
        original_state["energy_level"] = langgraph_state["energy_level"]
        original_state["sensory_data"] = langgraph_state["sensory_data"]
        original_state["neural_state"] = langgraph_state["neural_state"]
        original_state["motor_commands"] = langgraph_state["motor_commands"]
        original_state["decision_context"] = langgraph_state["decision_context"]
        
        # Convert LangGraph messages to simple format
        if "messages" not in original_state:
            original_state["messages"] = []
        
        for msg in langgraph_state["messages"]:
            if hasattr(msg, 'content'):
                original_state["messages"].append({
                    "role": "assistant" if isinstance(msg, AIMessage) else "user",
                    "content": msg.content,
                    "timestamp": datetime.now().timestamp()
                })
        
        # Update movement status flags based on motor commands
        motor_commands = original_state.get("motor_commands", {})
        muscle_activations = motor_commands.get("muscle_activations", {})
        
        dorsal = muscle_activations.get("dorsal", 0.0)
        ventral = muscle_activations.get("ventral", 0.0)
        pharynx = motor_commands.get("pharynx_pump", 0.0)
        
        # Set movement flags based on motor activity
        original_state["is_moving"] = (dorsal > 0.1 or ventral > 0.1)
        original_state["is_feeding"] = (pharynx > 0.1)
        
        return original_state 