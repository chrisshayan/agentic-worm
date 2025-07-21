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
from ..memory import WormMemoryManager, MemoryType

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
        
        # Initialize memory manager for persistent learning
        try:
            import os
            arango_host = os.environ.get('ARANGO_HOST', 'localhost')
            arango_port = int(os.environ.get('ARANGO_PORT', '8529'))
            arango_database = os.environ.get('ARANGO_DATABASE', 'agentic_worm_memory')
            arango_username = os.environ.get('ARANGO_USERNAME', '')
            arango_password = os.environ.get('ARANGO_PASSWORD', '')
            
            # For no-auth ArangoDB, use empty credentials
            if not arango_username:
                arango_username = None
                arango_password = None
            
            logger.info(f"🔌 Connecting to ArangoDB at {arango_host}:{arango_port}")
            logger.info(f"🗄️ Database: {arango_database}")
            logger.info(f"👤 Auth mode: {'No authentication' if not arango_username else 'With authentication'}")
            
            self.memory_manager = WormMemoryManager(
                arango_config={
                    "host": arango_host,
                    "port": arango_port,
                    "database_name": arango_database,
                    "username": arango_username,
                    "password": arango_password
                },
                enable_consolidation=True,
                consolidation_interval_hours=24
            )
            
            # Test the memory manager initialization
            logger.info("🧪 Testing memory manager initialization...")
            initialization_success = await self.memory_manager.initialize()
            
            if initialization_success:
                logger.info("✅ Memory manager initialized successfully")
                
                # Test basic operations
                test_success = await self.memory_manager.test_basic_operations("test_worm_001")
                if test_success:
                    logger.info("🎉 Memory system fully operational!")
                else:
                    logger.warning("⚠️ Memory system initialized but basic operations failed")
            else:
                logger.error("❌ Memory manager initialization failed")
                self.memory_manager = None
                
        except Exception as e:
            logger.error(f"❌ Memory manager initialization failed: {e}")
            logger.error(f"💡 This will cause memory system to show 'Initializing...' status")
            self.memory_manager = None
        
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
        """LangGraph node for memory-enabled cognitive processing."""
        try:
            current_time = datetime.now().timestamp()
            
            # Analyze current situation
            goal = state["decision_context"].get("current_goal", "explore")
            fitness = state["fitness_score"]
            energy = state["energy_level"]
            current_location = state["position"]
            worm_id = state["worm_id"]
            
            # 🧠 Memory-Enhanced Cognition
            
            # 1. Retrieve relevant memories for current context (if memory available)
            relevant_memories = {}
            spatial_context = {"is_familiar": False, "average_success_rate": 0.5, "region_type": "unknown"}
            best_strategies = []
            
            if self.memory_manager:
                try:
                    relevant_memories = await self.memory_manager.retrieve_relevant_memories(
                        worm_id=worm_id,
                        current_location=current_location,
                        current_goal=goal,
                        context=f"fitness={fitness:.2f} energy={energy:.2f}",
                        memory_types=[MemoryType.EPISODIC, MemoryType.SPATIAL, MemoryType.PROCEDURAL],
                        limit=5
                    )
                    
                    # 2. Get spatial context for current location
                    spatial_context = await self.memory_manager.get_spatial_context(
                        worm_id=worm_id,
                        location=current_location,
                        radius=50.0
                    )
                    
                    # 3. Get best strategies for current goal
                    best_strategies = await self.memory_manager.get_best_strategies_for_goal(
                        worm_id=worm_id,
                        goal=goal,
                        context={"fitness": fitness, "energy": energy, "location": current_location},
                        limit=3
                    )
                except Exception as e:
                    logger.warning(f"Memory retrieval failed: {e}")
            else:
                logger.debug("Memory manager not available, using fallback cognition")
            
            # 4. Memory-informed cognitive assessment
            memory_insights = []
            
            # Spatial memory insights
            if spatial_context["is_familiar"]:
                if spatial_context["average_success_rate"] > 0.7:
                    memory_insights.append("familiar_successful_area")
                    cognitive_assessment = "location_optimistic"
                elif spatial_context["average_success_rate"] < 0.3:
                    memory_insights.append("familiar_challenging_area")
                    cognitive_assessment = "location_cautious"
                else:
                    cognitive_assessment = "location_neutral"
            else:
                memory_insights.append("unknown_territory")
                cognitive_assessment = "exploration_needed"
            
            # Strategy memory insights
            if best_strategies:
                top_strategy = best_strategies[0]
                if top_strategy.success_rate > 0.8:
                    memory_insights.append("proven_strategy_available")
                    strategy = top_strategy.name
                else:
                    strategy = "adaptive_approach"
            else:
                memory_insights.append("no_proven_strategies")
                strategy = "experimental_approach"
            
            # Episodic memory insights
            recent_experiences = relevant_memories.get("episodic", [])
            if recent_experiences:
                recent_outcomes = [exp.get("outcome", "unknown") for exp in recent_experiences]
                success_rate = recent_outcomes.count("success") / len(recent_outcomes)
                
                if success_rate > 0.7:
                    memory_insights.append("recent_success_pattern")
                elif success_rate < 0.3:
                    memory_insights.append("recent_failure_pattern")
                    
                # Adjust cognitive assessment based on recent performance
                if success_rate > 0.8:
                    cognitive_assessment = f"{cognitive_assessment}_confident"
                elif success_rate < 0.2:
                    cognitive_assessment = f"{cognitive_assessment}_adaptive"
            
            # 5. Combine baseline assessment with memory insights
            if goal == "find_food" and fitness < 0.5:
                if "familiar_successful_area" in memory_insights:
                    cognitive_assessment = "food_seeking_optimized"
                    strategy = "memory_guided_search"
                else:
                    cognitive_assessment = "food_seeking_urgent"
                    strategy = "aggressive_chemotaxis"
            elif goal == "explore" and energy > 0.7:
                if "unknown_territory" in memory_insights:
                    cognitive_assessment = "exploration_discovery"
                    strategy = "systematic_mapping"
                else:
                    cognitive_assessment = "exploration_optimization"
                    strategy = "efficiency_focused"
            
            # 6. Update decision context with memory-enhanced information
            state["decision_context"]["cognitive_assessment"] = cognitive_assessment
            state["decision_context"]["behavioral_strategy"] = strategy
            state["decision_context"]["memory_insights"] = memory_insights
            state["decision_context"]["spatial_context"] = spatial_context
            state["decision_context"]["available_strategies"] = len(best_strategies)
            state["decision_context"]["memory_confidence"] = min(
                spatial_context.get("average_success_rate", 0.5) + 0.3, 1.0
            )
            state["decision_context"]["analysis_time"] = current_time
            
            # 7. Create detailed cognition message
            memory_summary = f"Spatial: {spatial_context['region_type']} " + \
                           f"(success: {spatial_context['average_success_rate']:.2f}), " + \
                           f"Strategies: {len(best_strategies)}, " + \
                           f"Experiences: {len(recent_experiences)}"
            
            cognition_msg = AIMessage(
                content=f"🧠 MEMORY-ENHANCED COGNITION: {cognitive_assessment} | " + \
                       f"Strategy: {strategy} | Memory: {memory_summary} | " + \
                       f"Insights: {', '.join(memory_insights)}"
            )
            state["messages"].append(cognition_msg)
            state["current_step"] = "cognition_complete"
            
            return state
            
        except Exception as e:
            # Fallback to basic cognition if memory fails
            state["processing_errors"].append(f"Memory-cognition error: {e}")
            
            goal = state["decision_context"].get("current_goal", "explore")
            if goal == "find_food" and state["fitness_score"] < 0.5:
                cognitive_assessment = "food_seeking_basic"
                strategy = "basic_chemotaxis"
            else:
                cognitive_assessment = "standard_behavior"
                strategy = "balanced_approach"
            
            state["decision_context"]["cognitive_assessment"] = cognitive_assessment
            state["decision_context"]["behavioral_strategy"] = strategy
            state["decision_context"]["memory_insights"] = ["memory_unavailable"]
            
            fallback_msg = AIMessage(
                content=f"🤔 BASIC COGNITION: {cognitive_assessment} | Strategy: {strategy}"
            )
            state["messages"].append(fallback_msg)
            state["current_step"] = "cognition_complete"
            
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
        """LangGraph node for memory-enabled learning and experience recording."""
        if not self.enable_learning:
            return state
            
        try:
            current_time = datetime.now().timestamp()
            
            # Evaluate action success and collect experience data
            decision = state["decision_context"].get("current_decision", "")
            confidence = state["decision_context"].get("decision_confidence", 0.5)
            fitness_before = state.get("previous_fitness", state["fitness_score"])
            fitness_after = state["fitness_score"]
            energy_before = state.get("previous_energy", state["energy_level"])
            energy_after = state["energy_level"]
            
            # Calculate changes
            fitness_change = fitness_after - fitness_before
            energy_change = energy_after - energy_before
            
            # Get goal and strategy with proper null safety
            decision_context = state.get("decision_context", {})
            if decision_context is None:
                decision_context = {}
                
            goal = decision_context.get("current_goal") or "explore_environment"
            strategy = decision_context.get("behavioral_strategy") or "basic_movement"
            
            # Ensure goal and strategy are always strings
            if not isinstance(goal, str) or not goal.strip():
                goal = "explore_environment"
            if not isinstance(strategy, str) or not strategy.strip():
                strategy = "basic_movement"
            
            # Determine outcome
            if fitness_change > 0.01:
                outcome = "success"
                self.successful_actions += 1
                learning_outcome = "positive_reinforcement"
            elif fitness_change < -0.01:
                outcome = "failure"
                learning_outcome = "negative_feedback"
            else:
                outcome = "partial"
                learning_outcome = "neutral_feedback"
            
            # 🧠 Record Experience in Memory (if available)
            memory_status = "Memory system not available"
            
            if self.memory_manager:
                try:
                    worm_id = state["worm_id"]
                    location = state.get("position", {"x": 0.0, "y": 0.0, "z": 0.0})
                    motor_commands = state.get("motor_commands", {})
                
                    actions_taken = [
                        {
                            "type": "decision",
                            "decision": decision,
                            "confidence": confidence,
                            "timestamp": current_time
                        },
                        {
                            "type": "motor_action",
                            "commands": motor_commands,
                            "strategy": strategy,
                            "timestamp": current_time
                        }
                    ]
                    
                    # Fix motor_commands structure for Experience validation
                    safe_motor_commands = {}
                    if isinstance(motor_commands, dict):
                        # Extract muscle activations if they exist
                        if "muscle_activations" in motor_commands:
                            muscle_activations = motor_commands["muscle_activations"]
                            if isinstance(muscle_activations, dict):
                                safe_motor_commands["dorsal"] = float(muscle_activations.get("dorsal", 0.0))
                                safe_motor_commands["ventral"] = float(muscle_activations.get("ventral", 0.0))
                            else:
                                safe_motor_commands["dorsal"] = 0.0
                                safe_motor_commands["ventral"] = 0.0
                        else:
                            # Use direct values if available
                            safe_motor_commands["dorsal"] = float(motor_commands.get("dorsal", 0.0))
                            safe_motor_commands["ventral"] = float(motor_commands.get("ventral", 0.0))
                        
                        # Add other motor commands
                        safe_motor_commands["pharynx_pump"] = float(motor_commands.get("pharynx_pump", 0.0))
                    else:
                        # Default values if motor_commands is not a dict
                        safe_motor_commands = {"dorsal": 0.0, "ventral": 0.0, "pharynx_pump": 0.0}
                    
                    # Record the experience in episodic memory
                    experience_id = await self.memory_manager.record_experience(
                        worm_id=worm_id,
                        location=location,
                        goal=goal,
                        actions_taken=actions_taken,
                        motor_commands=safe_motor_commands,
                        outcome=outcome,
                        fitness_change=fitness_change,
                        energy_change=energy_change,
                        duration=1.0,  # Assume 1 second per cycle
                        environment_state={
                            "fitness": fitness_after,
                            "energy": energy_after,
                            "confidence": confidence
                        },
                        tags=[
                            str(strategy) if strategy else "basic_movement",
                            str(outcome) if outcome else "neutral", 
                            str(goal) if goal else "explore_environment",
                            f"confidence_{int((confidence or 0.5)*10)/10}"
                        ]
                    )
                    
                    memory_status = f"Experience {experience_id[:8]} recorded"
                    
                    # 🧠 Strategy Learning: Create or update strategies based on successful patterns
                    if outcome == "success" and confidence > 0.7:
                        try:
                            # Create a new strategy if this was particularly successful
                            strategy_name = f"{goal}_{strategy}_optimized"
                            strategy_description = f"Successful {strategy} for {goal} (fitness gain: {fitness_change:.3f})"
                            
                            trigger_conditions = {
                                "goal": goal,
                                "min_fitness": max(0.0, fitness_before - 0.1),
                                "min_energy": max(0.0, energy_before - 0.1),
                                "location_type": state["decision_context"].get("spatial_context", {}).get("region_type", "unknown")
                            }
                            
                            action_sequence = [
                                {"type": "cognitive_assessment", "strategy": strategy},
                                {"type": "motor_commands", "commands": motor_commands},
                                {"type": "evaluation", "expected_fitness_gain": fitness_change}
                            ]
                            
                            strategy_id = await self.memory_manager.create_or_update_strategy(
                                worm_id=worm_id,
                                name=strategy_name,
                                description=strategy_description,
                                trigger_conditions=trigger_conditions,
                                action_sequence=action_sequence,
                                context={
                                    "fitness_before": fitness_before,
                                    "energy_before": energy_before,
                                    "location": location,
                                    "outcome": outcome
                                },
                                tags=[goal, strategy, "auto_generated", "successful"]
                            )
                            
                            memory_status += f", Strategy {strategy_id[:8]} created"
                            
                        except Exception as strategy_error:
                            logger.warning(f"Failed to create strategy: {strategy_error}")
                    
                except Exception as memory_error:
                    logger.warning(f"Failed to record experience in memory: {memory_error}")
                    memory_status = "Memory recording failed"
            else:
                logger.debug("Memory manager not available, skipping experience recording")
            
            # Update learning metrics
            success_rate = self.successful_actions / self.decision_count if self.decision_count > 0 else 0
            
            # 🧠 Memory-Enhanced Learning Message
            memory_insights = state["decision_context"].get("memory_insights", [])
            memory_confidence = state["decision_context"].get("memory_confidence", 0.5)
            
            learning_msg = AIMessage(
                content=f"📚 MEMORY LEARNING: {learning_outcome} | " + \
                       f"Outcome: {outcome} | " + \
                       f"Fitness: {fitness_change:+.3f} | " + \
                       f"Success rate: {success_rate:.2f} | " + \
                       f"Memory: {memory_status} | " + \
                       f"Confidence: {memory_confidence:.2f} | " + \
                       f"Insights: {', '.join(memory_insights) if memory_insights else 'none'}"
            )
            state["messages"].append(learning_msg)
            state["current_step"] = "learning_complete"
            state["workflow_active"] = False
            
            # Store previous values for next iteration
            state["previous_fitness"] = fitness_after
            state["previous_energy"] = energy_after
            
            return state
            
        except Exception as e:
            state["processing_errors"].append(f"Memory-learning error: {e}")
            
            # Fallback to basic learning
            fitness_change = state["fitness_score"] - state.get("previous_fitness", state["fitness_score"])
            if fitness_change > 0:
                self.successful_actions += 1
                learning_outcome = "basic_positive"
            else:
                learning_outcome = "basic_negative"
            
            success_rate = self.successful_actions / self.decision_count if self.decision_count > 0 else 0
            
            fallback_msg = AIMessage(
                content=f"📚 BASIC LEARNING: {learning_outcome}, Success rate: {success_rate:.2f}"
            )
            state["messages"].append(fallback_msg)
            state["current_step"] = "learning_complete"
            state["workflow_active"] = False
            
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