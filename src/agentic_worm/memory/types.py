"""
Memory Types and Data Structures for Agentic Worm.

Defines the different types of memory and their data structures:
- Episodic Memory: Experiences and events
- Semantic Memory: Facts and knowledge
- Spatial Memory: Location-based information
- Procedural Memory: Strategies and behaviors
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class MemoryType(Enum):
    """Types of memory in the agentic worm system."""
    EPISODIC = "episodic"      # Experiences and events
    SEMANTIC = "semantic"      # Facts and knowledge
    SPATIAL = "spatial"        # Location-based memory
    PROCEDURAL = "procedural"  # Strategies and behaviors


class Experience(BaseModel):
    """Episodic memory: A specific experience or event."""
    experience_id: str = Field(..., description="Unique identifier for the experience")
    worm_id: str = Field(..., description="ID of the worm that had this experience")
    timestamp: datetime = Field(..., description="When the experience occurred")
    
    # Context
    location: Dict[str, float] = Field(..., description="Location where experience occurred")
    goal: str = Field(..., description="Goal the worm was pursuing")
    environment_state: Dict[str, Any] = Field(..., description="State of environment")
    
    # Actions and outcomes
    actions_taken: List[Dict[str, Any]] = Field(..., description="Actions performed")
    motor_commands: Dict[str, float] = Field(..., description="Motor commands executed")
    outcome: str = Field(..., description="success/failure/partial")
    
    # Results
    fitness_change: float = Field(..., description="Change in fitness score")
    energy_change: float = Field(..., description="Change in energy level")
    duration: float = Field(..., description="Duration of experience in seconds")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    importance: float = Field(default=0.5, description="Importance score 0-1")


class KnowledgeFact(BaseModel):
    """Semantic memory: A fact or piece of knowledge."""
    fact_id: str = Field(..., description="Unique identifier for the fact")
    worm_id: str = Field(..., description="ID of the worm that learned this fact")
    
    # Content
    fact_type: str = Field(..., description="Type of fact (location, behavior, environment)")
    content: str = Field(..., description="The actual fact or knowledge")
    confidence: float = Field(..., description="Confidence in this fact 0-1")
    
    # Sources and evidence
    source_experiences: List[str] = Field(default_factory=list, description="Experience IDs that support this fact")
    evidence_count: int = Field(default=1, description="Number of supporting evidences")
    
    # Temporal info
    first_learned: datetime = Field(..., description="When first learned")
    last_updated: datetime = Field(..., description="When last updated")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class SpatialMemory(BaseModel):
    """Spatial memory: Location-based information."""
    location_id: str = Field(..., description="Unique identifier for the location")
    worm_id: str = Field(..., description="ID of the worm")
    
    # Location data
    coordinates: Dict[str, float] = Field(..., description="x, y, z coordinates")
    region_type: str = Field(..., description="Type of region (food_rich, obstacle, empty, etc.)")
    
    # Experience data
    visit_count: int = Field(default=1, description="Number of times visited")
    success_rate: float = Field(..., description="Success rate at this location 0-1")
    food_found_count: int = Field(default=0, description="Number of times food found here")
    obstacles_encountered: int = Field(default=0, description="Number of obstacles encountered")
    
    # Temporal data
    first_visited: datetime = Field(..., description="When first visited")
    last_visited: datetime = Field(..., description="When last visited")
    total_time_spent: float = Field(default=0.0, description="Total time spent here in seconds")
    
    # Environmental characteristics
    average_temperature: Optional[float] = Field(None, description="Average temperature observed")
    chemical_gradients: Dict[str, float] = Field(default_factory=dict, description="Chemical concentrations")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class Strategy(BaseModel):
    """Procedural memory: A behavioral strategy."""
    strategy_id: str = Field(..., description="Unique identifier for the strategy")
    worm_id: str = Field(..., description="ID of the worm")
    
    # Strategy definition
    name: str = Field(..., description="Name of the strategy")
    description: str = Field(..., description="Description of what the strategy does")
    
    # Conditions and actions
    trigger_conditions: Dict[str, Any] = Field(..., description="When to use this strategy")
    action_sequence: List[Dict[str, Any]] = Field(..., description="Steps to execute")
    
    # Performance metrics
    usage_count: int = Field(default=0, description="Number of times used")
    success_count: int = Field(default=0, description="Number of successful outcomes")
    failure_count: int = Field(default=0, description="Number of failed outcomes")
    success_rate: float = Field(default=0.0, description="Success rate 0-1")
    average_fitness_gain: float = Field(default=0.0, description="Average fitness gain")
    
    # Temporal data
    created: datetime = Field(..., description="When strategy was created")
    last_used: datetime = Field(..., description="When last used")
    last_updated: datetime = Field(..., description="When last modified")
    
    # Context
    effective_contexts: List[Dict[str, Any]] = Field(default_factory=list, description="Contexts where effective")
    ineffective_contexts: List[Dict[str, Any]] = Field(default_factory=list, description="Contexts where ineffective")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    importance: float = Field(default=0.5, description="Importance score 0-1")


class MemoryQuery(BaseModel):
    """Query structure for memory retrieval."""
    memory_types: List[MemoryType] = Field(..., description="Types of memory to search")
    query_text: Optional[str] = Field(None, description="Text query for semantic search")
    location: Optional[Dict[str, float]] = Field(None, description="Location for spatial queries")
    location_radius: Optional[float] = Field(None, description="Radius for spatial queries")
    time_range: Optional[Tuple[datetime, datetime]] = Field(None, description="Time range filter")
    tags: List[str] = Field(default_factory=list, description="Tag filters")
    limit: int = Field(default=10, description="Maximum results to return")
    min_relevance: float = Field(default=0.5, description="Minimum relevance score")


class MemoryConsolidationResult(BaseModel):
    """Result of memory consolidation process."""
    consolidated_count: int = Field(..., description="Number of memories consolidated")
    new_knowledge_count: int = Field(..., description="Number of new knowledge facts created")
    updated_strategies: List[str] = Field(..., description="Strategy IDs that were updated")
    processing_time: float = Field(..., description="Time taken for consolidation")
    summary: str = Field(..., description="Summary of consolidation results") 