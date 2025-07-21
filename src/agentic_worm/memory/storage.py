"""
ArangoDB Storage Backend for Agentic Worm Memory.

This module provides ArangoDB-based storage for different types of memory,
with support for graph relationships and vector embeddings.
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

try:
    from arango import ArangoClient
    from arango.database import StandardDatabase
    from arango.collection import StandardCollection
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    ArangoClient = None
    StandardDatabase = None
    StandardCollection = None

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None

from .types import (
    MemoryType, Experience, KnowledgeFact, SpatialMemory, Strategy,
    MemoryQuery, MemoryConsolidationResult
)

logger = logging.getLogger(__name__)


class ArangoMemoryStore:
    """
    ArangoDB-based memory storage for the agentic worm.
    
    Provides storage and retrieval for:
    - Episodic memories (experiences)
    - Semantic memories (knowledge facts)
    - Spatial memories (location data)
    - Procedural memories (strategies)
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 8529,
        database_name: str = "agentic_worm_memory",
        username: Optional[str] = None,
        password: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the ArangoDB memory store.
        
        Args:
            host: ArangoDB host
            port: ArangoDB port
            database_name: Name of the database to use
            username: ArangoDB username
            password: ArangoDB password
            embedding_model: Name of the sentence transformer model
        """
        self.host = host
        self.port = port
        self.database_name = database_name
        self.username = username
        self.password = password
        
        # Log connection details (without password)
        auth_info = "No authentication" if not username else f"User: {username}"
        logger.info(f"🔗 ArangoDB Storage Config: {host}:{port}/{database_name} ({auth_info})")
        
        self.client = None
        self.db = None
        self.embeddings = None
        
        # Collection names
        self.collections = {
            MemoryType.EPISODIC: "experiences",
            MemoryType.SEMANTIC: "knowledge_facts", 
            MemoryType.SPATIAL: "spatial_memories",
            MemoryType.PROCEDURAL: "strategies"
        }
        
        # Edge collection names
        self.edge_collections = {
            "experience_to_location": "experience_location_edges",
            "experience_to_knowledge": "experience_knowledge_edges", 
            "knowledge_to_strategy": "knowledge_strategy_edges",
            "strategy_to_experience": "strategy_experience_edges"
        }
        
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embeddings = SentenceTransformer(embedding_model)
                logger.info(f"Loaded embedding model: {embedding_model}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
                self.embeddings = None
        
        if ARANGO_AVAILABLE:
            self._initialize_connection()
        else:
            logger.warning("ArangoDB not available - using fallback mode")
    
    def _initialize_connection(self) -> bool:
        """Initialize connection to ArangoDB with retry logic."""
        import time
        
        max_retries = 10
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to connect to ArangoDB at {self.host}:{self.port} (attempt {attempt + 1}/{max_retries})")
                
                # Create client with longer timeout
                self.client = ArangoClient(
                    hosts=f"http://{self.host}:{self.port}",
                    request_timeout=30
                )
                
                # Test connection first (handle no-auth ArangoDB)
                if self.username and self.password:
                    sys_db = self.client.db("_system", username=self.username, password=self.password)
                else:
                    # No authentication mode (ARANGO_NO_AUTH=1)
                    sys_db = self.client.db("_system")
                
                # Try a simple operation to verify connection
                sys_db.version()
                logger.info("✅ ArangoDB connection established")
                
                # Create database if it doesn't exist
                try:
                    if not sys_db.has_database(self.database_name):
                        sys_db.create_database(self.database_name)
                        logger.info(f"Created database: {self.database_name}")
                    else:
                        logger.info(f"Database {self.database_name} already exists")
                except Exception as db_error:
                    logger.warning(f"Database creation issue: {db_error}")
                
                # Connect to our database
                if self.username and self.password:
                    self.db = self.client.db(
                        self.database_name,
                        username=self.username, 
                        password=self.password
                    )
                else:
                    # No authentication mode
                    self.db = self.client.db(self.database_name)
                
                # Test our database connection
                try:
                    self.db.version()
                    logger.info(f"✅ Connected to database: {self.database_name}")
                except Exception as e:
                    logger.error(f"Failed to connect to database {self.database_name}: {e}")
                    return False
                
                # Initialize collections
                self._initialize_collections()
                
                logger.info("🧠 ArangoDB memory system initialized successfully")
                return True
                
            except Exception as e:
                logger.warning(f"ArangoDB connection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 30)  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to ArangoDB after {max_retries} attempts")
                    logger.error("💡 Tip: Ensure ArangoDB is running and accessible")
                    return False
        
        return False
    
    def _initialize_collections(self):
        """Initialize collections and indexes."""
        # Create document collections
        for memory_type, collection_name in self.collections.items():
            if not self.db.has_collection(collection_name):
                collection = self.db.create_collection(collection_name)
                logger.info(f"Created collection: {collection_name}")
            else:
                collection = self.db.collection(collection_name)
            
            # Create indexes based on memory type
            self._create_indexes(collection, memory_type)
        
        # Create edge collections
        for edge_name, edge_collection in self.edge_collections.items():
            if not self.db.has_collection(edge_collection):
                self.db.create_collection(edge_collection, edge=True)
                logger.info(f"Created edge collection: {edge_collection}")
    
    def _create_indexes(self, collection: StandardCollection, memory_type: MemoryType):
        """Create appropriate indexes for each memory type."""
        try:
            # Common indexes
            collection.add_hash_index(fields=["worm_id"])
            collection.add_skiplist_index(fields=["timestamp"])
            
            if memory_type == MemoryType.EPISODIC:
                collection.add_skiplist_index(fields=["outcome"])
                collection.add_skiplist_index(fields=["goal"])
                collection.add_geo_index(fields=["location"])
                
            elif memory_type == MemoryType.SEMANTIC:
                collection.add_hash_index(fields=["fact_type"])
                collection.add_skiplist_index(fields=["confidence"])
                
            elif memory_type == MemoryType.SPATIAL:
                collection.add_geo_index(fields=["coordinates"])
                collection.add_hash_index(fields=["region_type"])
                collection.add_skiplist_index(fields=["success_rate"])
                
            elif memory_type == MemoryType.PROCEDURAL:
                collection.add_skiplist_index(fields=["success_rate"])
                collection.add_skiplist_index(fields=["usage_count"])
                
        except Exception as e:
            logger.warning(f"Failed to create some indexes for {memory_type}: {e}")
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text."""
        if not self.embeddings:
            return None
        
        try:
            embedding = self.embeddings.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    async def store_experience(self, experience: Experience) -> str:
        """Store episodic memory (experience)."""
        if not self.db:
            logger.error("Database not initialized")
            return ""
        
        try:
            # Generate embedding
            exp_text = f"{experience.goal} {experience.outcome} {' '.join(experience.tags)}"
            embedding = self._generate_embedding(exp_text)
            
            # Prepare document - convert to dict first
            doc = experience.dict()
            
            # Serialize datetime objects to ISO format strings
            doc = self._serialize_datetime_fields(doc)
            
            doc["_key"] = experience.experience_id
            doc["memory_type"] = MemoryType.EPISODIC.value
            doc["embedding"] = embedding
            doc["created_at"] = datetime.now().isoformat()
            
            # Store in database
            collection = self.db.collection(self.collections[MemoryType.EPISODIC])
            result = collection.insert(doc, overwrite=True)
            
            logger.info(f"Stored experience: {experience.experience_id}")
            return result["_key"]
            
        except Exception as e:
            logger.error(f"Failed to store experience: {e}")
            return ""
    
    async def store_knowledge_fact(self, fact: KnowledgeFact) -> str:
        """Store semantic memory (knowledge fact)."""
        if not self.db:
            logger.error("Database not initialized")
            return ""
        
        try:
            # Generate embedding
            fact_text = f"{fact.fact_type} {fact.content} {' '.join(fact.tags)}"
            embedding = self._generate_embedding(fact_text)
            
            # Prepare document - convert to dict first
            doc = fact.dict()
            
            # Serialize datetime objects to ISO format strings
            doc = self._serialize_datetime_fields(doc)
            
            doc["_key"] = fact.fact_id
            doc["memory_type"] = MemoryType.SEMANTIC.value  
            doc["embedding"] = embedding
            doc["created_at"] = datetime.now().isoformat()
            
            # Store in database
            collection = self.db.collection(self.collections[MemoryType.SEMANTIC])
            result = collection.insert(doc, overwrite=True)
            
            # Create relationships to source experiences
            self._create_knowledge_experience_edges(fact)
            
            logger.info(f"Stored knowledge fact: {fact.fact_id}")
            return result["_key"]
            
        except Exception as e:
            logger.error(f"Failed to store knowledge fact: {e}")
            return ""
    
    async def store_spatial_memory(self, spatial: SpatialMemory) -> str:
        """Store spatial memory."""
        if not self.db:
            logger.error("Database not initialized") 
            return ""
        
        try:
            # Generate embedding for location description
            location_text = f"{spatial.region_type} {' '.join(spatial.tags)}"
            embedding = self._generate_embedding(location_text)
            
            # Prepare document - convert to dict first
            doc = spatial.dict()
            
            # Serialize datetime objects to ISO format strings
            doc = self._serialize_datetime_fields(doc)
            
            doc["_key"] = spatial.location_id
            doc["memory_type"] = MemoryType.SPATIAL.value
            doc["embedding"] = embedding
            doc["created_at"] = datetime.now().isoformat()
            
            # Store in database
            collection = self.db.collection(self.collections[MemoryType.SPATIAL])
            result = collection.insert(doc, overwrite=True)  # Allow updates
            
            logger.info(f"Stored spatial memory: {spatial.location_id}")
            return result["_key"]
            
        except Exception as e:
            logger.error(f"Failed to store spatial memory: {e}")
            return ""
    
    async def store_strategy(self, strategy: Strategy) -> str:
        """Store procedural memory (strategy)."""
        if not self.db:
            logger.error("Database not initialized")
            return ""
        
        try:
            # Generate embedding
            strategy_text = f"{strategy.name} {strategy.description} {' '.join(strategy.tags)}"
            embedding = self._generate_embedding(strategy_text)
            
            # Prepare document - convert to dict first
            doc = strategy.dict()
            
            # Serialize datetime objects to ISO format strings
            doc = self._serialize_datetime_fields(doc)
            
            doc["_key"] = strategy.strategy_id
            doc["memory_type"] = MemoryType.PROCEDURAL.value
            doc["embedding"] = embedding
            doc["created_at"] = datetime.now().isoformat()
            
            # Store in database
            collection = self.db.collection(self.collections[MemoryType.PROCEDURAL])
            result = collection.insert(doc, overwrite=True)
            
            logger.info(f"Stored strategy: {strategy.strategy_id}")
            return result["_key"]
            
        except Exception as e:
            logger.error(f"Failed to store strategy: {e}")
            return ""
    
    def _create_knowledge_experience_edges(self, fact: KnowledgeFact):
        """Create edges between knowledge facts and supporting experiences."""
        if not self.db or not fact.source_experiences:
            return
        
        try:
            edge_collection = self.db.collection(self.edge_collections["experience_to_knowledge"])
            
            for exp_id in fact.source_experiences:
                edge_doc = {
                    "_from": f"{self.collections[MemoryType.EPISODIC]}/{exp_id}",
                    "_to": f"{self.collections[MemoryType.SEMANTIC]}/{fact.fact_id}",
                    "relationship": "supports",
                    "created_at": datetime.now().isoformat()
                }
                edge_collection.insert(edge_doc)
                
        except Exception as e:
            logger.error(f"Failed to create knowledge-experience edges: {e}")
    
    async def query_memories(self, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Query memories based on criteria."""
        if not self.db:
            return []
        
        results = []
        
        for memory_type in query.memory_types:
            collection_results = await self._query_memory_type(memory_type, query)
            results.extend(collection_results)
        
        # Sort by relevance/recency
        results.sort(key=lambda x: (x.get("relevance_score", 0), x.get("timestamp", "")), reverse=True)
        
        return results[:query.limit]
    
    async def _query_memory_type(self, memory_type: MemoryType, query: MemoryQuery) -> List[Dict[str, Any]]:
        """Query a specific memory type."""
        try:
            collection = self.db.collection(self.collections[memory_type])
            
            # Build AQL query
            aql_parts = ["FOR doc IN @@collection"]
            bind_vars = {"@collection": collection.name}
            
            # Add filters
            filters = []
            
            # Time range filter
            if query.time_range:
                filters.append("doc.timestamp >= @start_time AND doc.timestamp <= @end_time")
                bind_vars["start_time"] = query.time_range[0].isoformat()
                bind_vars["end_time"] = query.time_range[1].isoformat()
            
            # Location filter for spatial queries
            if query.location and memory_type == MemoryType.SPATIAL:
                if query.location_radius:
                    # Use proper Euclidean distance calculation
                    distance_calc = self._calculate_distance_aql("doc.coordinates", "@location_obj")
                    filters.append(f"{distance_calc} <= @radius")
                    bind_vars["location_obj"] = {
                        "x": query.location.get("x", 0.0),
                        "y": query.location.get("y", 0.0),
                        "z": query.location.get("z", 0.0)
                    }
                    bind_vars["radius"] = query.location_radius
            
            # Tag filters
            if query.tags:
                for i, tag in enumerate(query.tags):
                    filters.append(f"@tag{i} IN doc.tags")
                    bind_vars[f"tag{i}"] = tag
            
            # Add filters to query
            if filters:
                aql_parts.append("FILTER " + " AND ".join(filters))
            
            # Add semantic search if query text provided
            if query.query_text and self.embeddings:
                query_embedding = self._generate_embedding(query.query_text)
                if query_embedding:
                    # Add similarity calculation
                    aql_parts.append("LET similarity = COSINE_SIMILARITY(doc.embedding, @query_embedding)")
                    aql_parts.append("FILTER similarity >= @min_relevance")
                    bind_vars["query_embedding"] = query_embedding
                    bind_vars["min_relevance"] = query.min_relevance
                    
                    # Sort by similarity
                    aql_parts.append("SORT similarity DESC")
            else:
                # Sort by timestamp if no semantic search
                aql_parts.append("SORT doc.timestamp DESC")
            
            # Limit results
            aql_parts.append("LIMIT @limit")
            bind_vars["limit"] = query.limit
            
            # Return documents
            aql_parts.append("RETURN MERGE(doc, {relevance_score: similarity || 1})")
            
            aql_query = " ".join(aql_parts)
            
            # Execute query
            cursor = self.db.aql.execute(aql_query, bind_vars=bind_vars)
            results = list(cursor)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query {memory_type}: {e}")
            return []
    
    async def get_spatial_memories_near_location(
        self, 
        location: Dict[str, float], 
        radius: float = 50.0,
        worm_id: str = None
    ) -> List[SpatialMemory]:
        """Get spatial memories near a specific location."""
        if not self.db:
            return []
        
        try:
            collection = self.db.collection(self.collections[MemoryType.SPATIAL])
            
            # Build query for nearby locations using Euclidean distance
            distance_calc = self._calculate_distance_aql("doc.coordinates", "@location_obj")
            
            aql_query = f"""
            FOR doc IN @@collection
            FILTER {distance_calc} <= @radius
            """
            
            bind_vars = {
                "@collection": collection.name,
                "location_obj": {
                    "x": location.get("x", 0.0),
                    "y": location.get("y", 0.0), 
                    "z": location.get("z", 0.0)
                },
                "radius": radius
            }
            
            if worm_id:
                aql_query += " AND doc.worm_id == @worm_id"
                bind_vars["worm_id"] = worm_id
            
            aql_query += f" SORT {distance_calc} ASC RETURN doc"
            
            cursor = self.db.aql.execute(aql_query, bind_vars=bind_vars)
            results = list(cursor)
            
            # Convert to SpatialMemory objects
            spatial_memories = []
            for result in results:
                try:
                    spatial_memory = SpatialMemory(**result)
                    spatial_memories.append(spatial_memory)
                except Exception as e:
                    logger.warning(f"Failed to parse spatial memory: {e}")
            
            return spatial_memories
            
        except Exception as e:
            logger.error(f"Failed to get spatial memories near location: {e}")
            return []
    
    async def consolidate_memories(self, worm_id: str) -> MemoryConsolidationResult:
        """Consolidate memories to extract patterns and create knowledge."""
        if not self.db:
            return MemoryConsolidationResult(
                consolidated_count=0,
                new_knowledge_count=0,
                updated_strategies=[],
                processing_time=0.0,
                summary="Database not available"
            )
        
        start_time = datetime.now()
        
        try:
            # Get recent experiences
            recent_experiences = await self._get_recent_experiences(worm_id, days=7)
            
            # Extract patterns and create knowledge
            new_knowledge = await self._extract_knowledge_from_experiences(recent_experiences)
            
            # Update strategies based on performance
            updated_strategies = await self._update_strategies(worm_id)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = MemoryConsolidationResult(
                consolidated_count=len(recent_experiences),
                new_knowledge_count=len(new_knowledge),
                updated_strategies=updated_strategies,
                processing_time=processing_time,
                summary=f"Consolidated {len(recent_experiences)} experiences, created {len(new_knowledge)} knowledge facts"
            )
            
            logger.info(f"Memory consolidation completed: {result.summary}")
            return result
            
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            return MemoryConsolidationResult(
                consolidated_count=0,
                new_knowledge_count=0, 
                updated_strategies=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                summary=f"Consolidation failed: {e}"
            )
    
    async def _get_recent_experiences(self, worm_id: str, days: int = 7) -> List[Experience]:
        """Get recent experiences for consolidation."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = MemoryQuery(
            memory_types=[MemoryType.EPISODIC],
            time_range=(cutoff_date, datetime.now()),
            limit=100
        )
        
        results = await self._query_memory_type(MemoryType.EPISODIC, query)
        
        experiences = []
        for result in results:
            try:
                if result.get("worm_id") == worm_id:
                    experience = Experience(**result)
                    experiences.append(experience)
            except Exception as e:
                logger.warning(f"Failed to parse experience: {e}")
        
        return experiences
    
    async def _extract_knowledge_from_experiences(self, experiences: List[Experience]) -> List[KnowledgeFact]:
        """Extract knowledge facts from experiences."""
        knowledge_facts = []
        
        # Group experiences by location to find patterns
        location_groups = {}
        for exp in experiences:
            loc_key = f"{exp.location['x']:.0f},{exp.location['y']:.0f}"
            if loc_key not in location_groups:
                location_groups[loc_key] = []
            location_groups[loc_key].append(exp)
        
        # Create knowledge about successful locations
        for loc_key, group in location_groups.items():
            if len(group) >= 3:  # Need multiple experiences
                success_rate = sum(1 for exp in group if exp.outcome == "success") / len(group)
                
                if success_rate >= 0.7:  # High success rate
                    fact = KnowledgeFact(
                        fact_id=str(uuid.uuid4()),
                        worm_id=group[0].worm_id,
                        fact_type="location",
                        content=f"Location {loc_key} has high success rate ({success_rate:.2f}) for goal {group[0].goal}",
                        confidence=min(success_rate, 0.95),
                        source_experiences=[exp.experience_id for exp in group],
                        evidence_count=len(group),
                        first_learned=datetime.now(),
                        last_updated=datetime.now(),
                        tags=["high_success", "location_knowledge"]
                    )
                    
                    # Store the fact
                    await self.store_knowledge_fact(fact)
                    knowledge_facts.append(fact)
        
        return knowledge_facts
    
    async def _update_strategies(self, worm_id: str) -> List[str]:
        """Update strategy performance based on recent experiences."""
        # This would implement strategy updates based on performance
        # For now, return empty list
        return []
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("Closed ArangoDB connection") 

    def _serialize_datetime_fields(self, doc: dict) -> dict:
        """Convert datetime objects to ISO format strings for JSON serialization."""
        serialized_doc = doc.copy()
        
        # Convert datetime fields to ISO format strings
        for key, value in serialized_doc.items():
            if isinstance(value, datetime):
                serialized_doc[key] = value.isoformat()
            elif isinstance(value, dict):
                # Recursively handle nested dictionaries
                serialized_doc[key] = self._serialize_datetime_fields(value)
            elif isinstance(value, list):
                # Handle lists that might contain datetime objects
                serialized_doc[key] = [
                    item.isoformat() if isinstance(item, datetime) else 
                    self._serialize_datetime_fields(item) if isinstance(item, dict) else item
                    for item in value
                ]
        
        return serialized_doc
    
    def _calculate_distance_aql(self, coord1_key: str, coord2_key: str) -> str:
        """Generate AQL for calculating Euclidean distance between 3D coordinates."""
        return f"""SQRT(
            POW({coord1_key}.x - {coord2_key}.x, 2) + 
            POW({coord1_key}.y - {coord2_key}.y, 2) + 
            POW({coord1_key}.z - {coord2_key}.z, 2)
        )""" 

    async def test_connection(self) -> bool:
        """Test the ArangoDB connection."""
        try:
            if not self.db:
                logger.error("Database not initialized")
                return False
            
            # Test with a simple operation
            self.db.version()
            logger.info("✅ ArangoDB connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ ArangoDB connection test failed: {e}")
            return False
    
    async def initialize_collections(self) -> bool:
        """Initialize all required collections."""
        try:
            if not self.db:
                logger.error("Database not initialized")
                return False
            
            logger.info("🔧 Initializing ArangoDB collections...")
            
            # Initialize collections with better error handling
            collections_created = 0
            for memory_type, collection_name in self.collections.items():
                try:
                    if not self.db.has_collection(collection_name):
                        self.db.create_collection(collection_name)
                        logger.info(f"✅ Created collection: {collection_name}")
                        collections_created += 1
                    else:
                        logger.info(f"✅ Collection exists: {collection_name}")
                        
                    # Test collection access
                    collection = self.db.collection(collection_name)
                    collection.count()  # Simple test operation
                    
                except Exception as e:
                    logger.error(f"❌ Failed to initialize collection {collection_name}: {e}")
                    return False
            
            if collections_created > 0:
                logger.info(f"✅ Created {collections_created} new collections")
            
            logger.info("✅ All collections initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Collection initialization failed: {e}")
            return False 