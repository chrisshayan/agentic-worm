"""
Agentic Worm: AI-driven autonomous digital C. elegans

This package provides an intelligent, autonomous digital C. elegans that demonstrates
goal-directed behavior through the integration of OpenWorm's biological simulation
with AI-driven agentic control via LangGraph.
"""

__version__ = "0.1.0"
__author__ = "Agentic Worm Team"
__email__ = "team@agentic-worm.org"

from .core import AgenticWormSystem
from .demo import DemoRunner

__all__ = ["AgenticWormSystem", "DemoRunner", "__version__"] 