"""
Memory Systems for Agentic Worm.

This module implements episodic, semantic, spatial, and procedural memory
using ArangoDB for graph storage and embeddings for semantic search.
"""

from .manager import WormMemoryManager
from .types import MemoryType, Experience, KnowledgeFact, SpatialMemory, Strategy
from .storage import ArangoMemoryStore

__all__ = [
    "WormMemoryManager",
    "MemoryType", 
    "Experience",
    "KnowledgeFact",
    "SpatialMemory", 
    "Strategy",
    "ArangoMemoryStore"
] 