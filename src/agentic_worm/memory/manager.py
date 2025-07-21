"""
Memory Manager for Agentic Worm.

This module provides the high-level interface for memory operations,
coordinating between different memory types and the LangGraph workflow.
"""

import uuid
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from .types import (
    MemoryType, Experience, KnowledgeFact, SpatialMemory, Strategy,
    MemoryQuery, MemoryConsolidationResult
)
from .storage import ArangoMemoryStore

logger = logging.getLogger(__name__)


class WormMemoryManager:
    """
    High-level memory manager for the agentic worm.
    
    Coordinates memory storage, retrieval, and consolidation across
    all memory types (episodic, semantic, spatial, procedural).
    """
    
    def __init__(
        self,
        arango_config: Optional[Dict[str, Any]] = None,
        enable_consolidation: bool = True,
        consolidation_interval_hours: int = 24
    ):
        """
        Initialize the memory manager.
        
        Args:
            arango_config: ArangoDB connection configuration
            enable_consolidation: Whether to enable automatic memory consolidation
            consolidation_interval_hours: How often to run consolidation
        """
        # Set up ArangoDB configuration with proper defaults
        if arango_config:
            self.arango_config = arango_config.copy()
        else:
            self.arango_config = {
                "host": "localhost",
                "port": 8529,
                "database_name": "agentic_worm_memory",
                "username": None,  # No auth by default
                "password": None   # No auth by default
            }
        
        # Clean up config - remove None values for no-auth mode
        if not self.arango_config.get("username"):
            self.arango_config.pop("username", None)
            self.arango_config.pop("password", None)
        
        logger.info(f"🔧 ArangoDB config: {dict(self.arango_config)}")
        
        self.enable_consolidation = enable_consolidation
        self.consolidation_interval_hours = consolidation_interval_hours
        
        # Initialize storage
        self.storage = ArangoMemoryStore(**self.arango_config)
        
        # Memory caches for fast access
        self.memory_cache = {
            MemoryType.EPISODIC: {},
            MemoryType.SEMANTIC: {},
            MemoryType.SPATIAL: {},
            MemoryType.PROCEDURAL: {}
        }
        
        # Consolidation tracking
        self.last_consolidation = {}  # worm_id -> timestamp
        
        logger.info("WormMemoryManager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the memory manager and verify everything is working."""
        try:
            logger.info("🧠 Initializing WormMemoryManager...")
            
            # Test storage connection
            if not self.storage:
                logger.error("❌ Storage not initialized")
                return False
            
            # Test database connection
            if not await self.storage.test_connection():
                logger.error("❌ Storage connection test failed")
                return False
            
            # Initialize collections
            success = await self.storage.initialize_collections()
            if not success:
                logger.error("❌ Failed to initialize storage collections")
                return False
            
            logger.info("✅ WormMemoryManager initialization successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ WormMemoryManager initialization failed: {e}")
            return False
    
    async def test_basic_operations(self, worm_id: str) -> bool:
        """Test basic memory operations to verify system is working."""
        try:
            logger.info("🧪 Testing basic memory operations...")
            
            # Test experience storage
            from .types import Experience
            from datetime import datetime
            import uuid
            
            test_experience = Experience(
                experience_id=f"test_{uuid.uuid4().hex[:8]}",
                worm_id=worm_id,
                timestamp=datetime.now(),
                location={"x": 0.0, "y": 0.0, "z": 0.0},
                goal="test_goal",
                environment_state={"test": True},
                actions_taken=[{"type": "test", "action": "test_action"}],
                motor_commands={"dorsal": 0.5, "ventral": 0.3, "pharynx_pump": 0.1},
                outcome="success",
                fitness_change=0.1,
                energy_change=-0.05,
                duration=1.0,
                tags=["test", "initialization"]
            )
            
            experience_id = await self.record_experience(
                worm_id=test_experience.worm_id,
                location=test_experience.location,
                goal=test_experience.goal,
                actions_taken=test_experience.actions_taken,
                motor_commands=test_experience.motor_commands,
                outcome=test_experience.outcome,
                fitness_change=test_experience.fitness_change,
                energy_change=test_experience.energy_change,
                duration=test_experience.duration,
                environment_state=test_experience.environment_state,
                tags=test_experience.tags
            )
            
            if experience_id:
                logger.info("✅ Test experience recorded successfully")
                return True
            else:
                logger.error("❌ Test experience recording failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Basic operations test failed: {e}")
            return False
    
    async def record_experience(
        self,
        worm_id: str,
        location: Dict[str, float],
        goal: str,
        actions_taken: List[Dict[str, Any]],
        motor_commands: Dict[str, float],
        outcome: str,
        fitness_change: float,
        energy_change: float = 0.0,
        duration: float = 1.0,
        environment_state: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Record a new experience in episodic memory.
        
        Args:
            worm_id: ID of the worm
            location: Location where experience occurred
            goal: Goal the worm was pursuing
            actions_taken: List of actions performed
            motor_commands: Motor commands executed
            outcome: Result (success/failure/partial)
            fitness_change: Change in fitness
            energy_change: Change in energy
            duration: Duration of experience
            environment_state: State of environment
            tags: Optional tags for categorization
            
        Returns:
            Experience ID
        """
        experience = Experience(
            experience_id=str(uuid.uuid4()),
            worm_id=worm_id,
            timestamp=datetime.now(),
            location=location,
            goal=goal,
            environment_state=environment_state or {},
            actions_taken=actions_taken,
            motor_commands=motor_commands,
            outcome=outcome,
            fitness_change=fitness_change,
            energy_change=energy_change,
            duration=duration,
            tags=tags or [],
            importance=self._calculate_experience_importance(outcome, fitness_change)
        )
        
        # Store in database
        exp_id = await self.storage.store_experience(experience)
        
        # Update spatial memory
        await self._update_spatial_memory(worm_id, location, outcome, duration)
        
        # Cache recent experience
        self.memory_cache[MemoryType.EPISODIC][exp_id] = experience
        
        # Check if consolidation is needed
        if self.enable_consolidation:
            await self._check_consolidation_needed(worm_id)
        
        logger.info(f"Recorded experience {exp_id} for worm {worm_id}")
        return exp_id
    
    def _calculate_experience_importance(self, outcome: str, fitness_change: float) -> float:
        """Calculate importance score for an experience."""
        base_importance = 0.5
        
        # Outcome influence
        if outcome == "success":
            base_importance += 0.3
        elif outcome == "failure":
            base_importance += 0.2  # Failures are also important for learning
        
        # Fitness change influence
        fitness_importance = min(abs(fitness_change), 0.2)
        base_importance += fitness_importance
        
        return min(base_importance, 1.0)
    
    async def _update_spatial_memory(
        self,
        worm_id: str,
        location: Dict[str, float],
        outcome: str,
        duration: float
    ):
        """Update or create spatial memory for a location."""
        # Find existing spatial memory near this location
        nearby_memories = await self.storage.get_spatial_memories_near_location(
            location, radius=20.0, worm_id=worm_id
        )
        
        if nearby_memories:
            # Update existing spatial memory
            spatial = nearby_memories[0]
            spatial.visit_count += 1
            spatial.last_visited = datetime.now()
            spatial.total_time_spent += duration
            
            # Update success rate
            if outcome == "success":
                spatial.food_found_count += 1
            
            # Recalculate success rate
            spatial.success_rate = spatial.food_found_count / spatial.visit_count
            
            await self.storage.store_spatial_memory(spatial)
            
        else:
            # Create new spatial memory
            spatial = SpatialMemory(
                location_id=str(uuid.uuid4()),
                worm_id=worm_id,
                coordinates=location,
                region_type=self._classify_region_type(outcome),
                visit_count=1,
                success_rate=1.0 if outcome == "success" else 0.0,
                food_found_count=1 if outcome == "success" else 0,
                first_visited=datetime.now(),
                last_visited=datetime.now(),
                total_time_spent=duration,
                tags=self._generate_spatial_tags(outcome)
            )
            
            await self.storage.store_spatial_memory(spatial)
    
    def _classify_region_type(self, outcome: str) -> str:
        """Classify region type based on outcome."""
        if outcome == "success":
            return "food_rich"
        elif outcome == "failure":
            return "obstacle"
        else:
            return "neutral"
    
    def _generate_spatial_tags(self, outcome: str) -> List[str]:
        """Generate tags for spatial memory."""
        tags = ["auto_generated"]
        if outcome == "success":
            tags.append("successful_location")
        elif outcome == "failure":
            tags.append("challenging_location")
        return tags
    
    async def retrieve_relevant_memories(
        self,
        worm_id: str,
        current_location: Dict[str, float],
        current_goal: str,
        context: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve relevant memories for current context.
        
        Args:
            worm_id: ID of the worm
            current_location: Current location
            current_goal: Current goal
            context: Additional context for semantic search
            memory_types: Types of memory to search
            limit: Maximum results per memory type
            
        Returns:
            Dictionary with memory type as key and list of memories as value
        """
        if memory_types is None:
            memory_types = [MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.SPATIAL, MemoryType.PROCEDURAL]
        
        results = {}
        
        for memory_type in memory_types:
            query = MemoryQuery(
                memory_types=[memory_type],
                query_text=f"{current_goal} {context or ''}",
                location=current_location,
                location_radius=50.0,
                time_range=(datetime.now() - timedelta(days=30), datetime.now()),
                limit=limit
            )
            
            memories = await self.storage.query_memories(query)
            
            # Filter by worm_id
            filtered_memories = [m for m in memories if m.get("worm_id") == worm_id]
            
            results[memory_type.value] = filtered_memories
        
        logger.info(f"Retrieved {sum(len(v) for v in results.values())} relevant memories for worm {worm_id}")
        return results
    
    async def get_spatial_context(
        self,
        worm_id: str,
        location: Dict[str, float],
        radius: float = 50.0
    ) -> Dict[str, Any]:
        """
        Get spatial context for a location.
        
        Args:
            worm_id: ID of the worm
            location: Location to analyze
            radius: Search radius
            
        Returns:
            Spatial context information
        """
        nearby_memories = await self.storage.get_spatial_memories_near_location(
            location, radius=radius, worm_id=worm_id
        )
        
        if not nearby_memories:
            return {
                "is_familiar": False,
                "visit_count": 0,
                "average_success_rate": 0.0,
                "region_type": "unknown",
                "recommendations": []
            }
        
        # Calculate aggregate statistics
        total_visits = sum(mem.visit_count for mem in nearby_memories)
        weighted_success_rate = sum(
            mem.success_rate * mem.visit_count for mem in nearby_memories
        ) / total_visits if total_visits > 0 else 0.0
        
        # Determine dominant region type
        region_counts = {}
        for mem in nearby_memories:
            region_counts[mem.region_type] = region_counts.get(mem.region_type, 0) + mem.visit_count
        
        dominant_region = max(region_counts.items(), key=lambda x: x[1])[0] if region_counts else "unknown"
        
        # Generate recommendations
        recommendations = []
        if weighted_success_rate > 0.7:
            recommendations.append("This area has been successful before")
        elif weighted_success_rate < 0.3:
            recommendations.append("This area has been challenging")
        
        if total_visits < 3:
            recommendations.append("Limited experience in this area")
        
        return {
            "is_familiar": total_visits > 0,
            "visit_count": total_visits,
            "average_success_rate": weighted_success_rate,
            "region_type": dominant_region,
            "recommendations": recommendations,
            "nearby_locations": len(nearby_memories)
        }
    
    async def get_best_strategies_for_goal(
        self,
        worm_id: str,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 3
    ) -> List[Strategy]:
        """
        Get the best strategies for a specific goal.
        
        Args:
            worm_id: ID of the worm
            goal: Target goal
            context: Current context
            limit: Maximum strategies to return
            
        Returns:
            List of best strategies
        """
        query = MemoryQuery(
            memory_types=[MemoryType.PROCEDURAL],
            query_text=goal,
            limit=limit * 2  # Get more to filter
        )
        
        results = await self.storage.query_memories(query)
        
        # Filter and convert to Strategy objects
        strategies = []
        for result in results:
            if result.get("worm_id") == worm_id:
                try:
                    strategy = Strategy(**result)
                    strategies.append(strategy)
                except Exception as e:
                    logger.warning(f"Failed to parse strategy: {e}")
        
        # Sort by success rate and usage
        strategies.sort(
            key=lambda s: (s.success_rate, s.usage_count),
            reverse=True
        )
        
        return strategies[:limit]
    
    async def create_or_update_strategy(
        self,
        worm_id: str,
        name: str,
        description: str,
        trigger_conditions: Dict[str, Any],
        action_sequence: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Create a new strategy or update an existing one.
        
        Args:
            worm_id: ID of the worm
            name: Strategy name
            description: Strategy description
            trigger_conditions: When to use this strategy
            action_sequence: Steps to execute
            context: Context where this strategy was effective
            tags: Optional tags
            
        Returns:
            Strategy ID
        """
        strategy = Strategy(
            strategy_id=str(uuid.uuid4()),
            worm_id=worm_id,
            name=name,
            description=description,
            trigger_conditions=trigger_conditions,
            action_sequence=action_sequence,
            usage_count=0,
            success_count=0,
            failure_count=0,
            success_rate=0.0,
            average_fitness_gain=0.0,
            created=datetime.now(),
            last_used=datetime.now(),
            last_updated=datetime.now(),
            effective_contexts=[context] if context else [],
            ineffective_contexts=[],
            tags=tags or [],
            importance=0.5
        )
        
        strategy_id = await self.storage.store_strategy(strategy)
        
        # Cache the strategy
        self.memory_cache[MemoryType.PROCEDURAL][strategy_id] = strategy
        
        logger.info(f"Created strategy {strategy_id}: {name}")
        return strategy_id
    
    async def update_strategy_performance(
        self,
        strategy_id: str,
        success: bool,
        fitness_gain: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Update strategy performance based on usage outcome."""
        # This would update strategy statistics
        logger.info(f"Updated strategy {strategy_id} performance: success={success}")
    
    async def _check_consolidation_needed(self, worm_id: str):
        """Check if memory consolidation is needed for a worm."""
        now = datetime.now()
        last_consolidation = self.last_consolidation.get(worm_id)
        
        if (not last_consolidation or 
            (now - last_consolidation).total_seconds() > self.consolidation_interval_hours * 3600):
            
            # Run consolidation in background
            asyncio.create_task(self._run_consolidation(worm_id))
    
    async def _run_consolidation(self, worm_id: str):
        """Run memory consolidation for a worm."""
        try:
            logger.info(f"Starting memory consolidation for worm {worm_id}")
            
            result = await self.storage.consolidate_memories(worm_id)
            
            self.last_consolidation[worm_id] = datetime.now()
            
            logger.info(f"Consolidation completed for worm {worm_id}: {result.summary}")
            
        except Exception as e:
            logger.error(f"Memory consolidation failed for worm {worm_id}: {e}")
    
    async def get_memory_statistics(self, worm_id: str) -> Dict[str, Any]:
        """Get real memory statistics for a worm from the database."""
        stats = {
            "episodic_count": 0,
            "semantic_count": 0,
            "spatial_count": 0,
            "procedural_count": 0,
            "total_experiences": 0,
            "success_rate": 0.0,
            "locations_visited": 0,
            "strategies_learned": 0,
            "knowledge_facts": 0,
            "memory_confidence": 0.5,
            "insights": ["Loading memory statistics..."]
        }
        
        try:
            if not self.storage or not self.storage.db:
                stats["insights"] = ["Memory system not connected"]
                return stats
            
            # Simple direct queries for each collection
            try:
                # Count experiences
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN experiences FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                results = list(cursor)
                episodic_count = results[0] if results and results[0] else 0
                stats["episodic_count"] = episodic_count
                stats["total_experiences"] = episodic_count
                
                # Count spatial memories
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN spatial_memories FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                results = list(cursor)
                stats["spatial_count"] = results[0] if results and results[0] else 0
                
                # Count semantic memories  
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN knowledge_facts FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                results = list(cursor)
                stats["semantic_count"] = results[0] if results and results[0] else 0
                
                # Count strategies
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN strategies FILTER doc.worm_id == @worm_id COLLECT WITH COUNT INTO length RETURN length",
                    bind_vars={"worm_id": worm_id}
                )
                results = list(cursor)
                stats["procedural_count"] = results[0] if results and results[0] else 0
                
                # Calculate success rate from experiences
                if episodic_count > 0:
                    cursor = self.storage.db.aql.execute(
                        "FOR doc IN experiences FILTER doc.worm_id == @worm_id AND doc.outcome == 'success' COLLECT WITH COUNT INTO length RETURN length",
                        bind_vars={"worm_id": worm_id}
                    )
                    results = list(cursor)
                    success_count = results[0] if results and results[0] else 0
                    stats["success_rate"] = (success_count / episodic_count) * 100
                
                # Count unique locations
                cursor = self.storage.db.aql.execute(
                    "FOR doc IN spatial_memories FILTER doc.worm_id == @worm_id RETURN DISTINCT doc.location",
                    bind_vars={"worm_id": worm_id}
                )
                results = list(cursor)
                stats["locations_visited"] = len(results)
                
                # Update insights based on data
                insights = []
                if episodic_count > 0:
                    insights.append(f"Learned from {episodic_count} experiences")
                    if stats["success_rate"] > 70:
                        insights.append("High success rate - learning effectively")
                    elif stats["success_rate"] > 40:
                        insights.append("Moderate success - adapting strategies")
                    else:
                        insights.append("Learning from failures - building resilience")
                else:
                    insights.append("No experiences recorded yet")
                
                if stats["spatial_count"] > 0:
                    insights.append(f"Remembers {stats['spatial_count']} spatial locations")
                
                if stats["procedural_count"] > 0:
                    insights.append(f"Developed {stats['procedural_count']} strategies")
                
                stats["insights"] = insights if insights else ["Memory system active"]
                
                # Calculate memory confidence based on data richness
                confidence = 0.5  # Base confidence
                if episodic_count > 0:
                    confidence += min(0.3, episodic_count * 0.05)  # More experiences
                if stats["success_rate"] > 50:
                    confidence += 0.2  # Good success rate
                if stats["spatial_count"] > 0:
                    confidence += 0.1  # Spatial awareness
                stats["memory_confidence"] = min(1.0, confidence)
                
                logger.debug(f"Memory statistics for {worm_id}: {stats}")
                
            except Exception as e:
                logger.error(f"Failed to query memory statistics: {e}")
                stats["insights"] = [f"Query error: {str(e)[:50]}..."]
                
        except Exception as e:
            logger.error(f"Memory statistics failed: {e}")
            stats["insights"] = ["Memory system error"]
            
        return stats
    def close(self):
        """Close memory manager and cleanup resources."""
        if self.storage:
            self.storage.close()
        
        logger.info("WormMemoryManager closed") 