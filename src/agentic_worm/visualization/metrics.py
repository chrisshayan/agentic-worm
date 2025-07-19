"""
Metrics Collector for Agentic Worm Visualization.

This module collects and processes real-time metrics from the agentic worm
system for visualization and analysis.
"""

import time
from typing import Dict, List, Any, Optional
from collections import deque
from datetime import datetime
import logging

from ..core.state import WormState

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and processes real-time metrics from the agentic worm system.
    
    Tracks performance indicators, behavioral patterns, and learning progress
    for visualization and analysis purposes.
    """
    
    def __init__(self, history_size: int = 1000):
        """
        Initialize the metrics collector.
        
        Args:
            history_size: Maximum number of historical data points to keep
        """
        self.history_size = history_size
        
        # Time series data
        self.timestamps = deque(maxlen=history_size)
        self.fitness_history = deque(maxlen=history_size)
        self.energy_history = deque(maxlen=history_size)
        self.confidence_history = deque(maxlen=history_size)
        self.decision_history = deque(maxlen=history_size)
        
        # Behavioral metrics
        self.decision_counts: Dict[str, int] = {}
        self.goal_switches: List[Dict[str, Any]] = []
        self.learning_events: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.session_start_time = time.time()
        self.total_steps = 0
        self.total_decisions = 0
        self.successful_behaviors = 0
        
        # Current state cache
        self.current_metrics: Optional[Dict[str, Any]] = None
        
    def collect_metrics(self, state: WormState) -> None:
        """
        Collect metrics from the current worm state.
        
        Args:
            state: Current worm state to extract metrics from
        """
        current_time = time.time()
        
        # Add timestamp
        self.timestamps.append(current_time)
        
        # Collect core metrics
        self.fitness_history.append(state["fitness_score"])
        self.energy_history.append(state["energy_level"])
        
        decision_confidence = state["decision_context"].get("decision_confidence", 0.0)
        self.confidence_history.append(decision_confidence)
        
        # Track decisions
        current_decision = state["decision_context"].get("current_decision")
        if current_decision:
            self.decision_history.append({
                "decision": current_decision,
                "timestamp": current_time,
                "confidence": decision_confidence,
                "goal": state["decision_context"]["current_goal"]
            })
            
            # Count decision types
            self.decision_counts[current_decision] = self.decision_counts.get(current_decision, 0) + 1
            self.total_decisions += 1
        
        # Track behavioral success
        if decision_confidence > 0.8:
            self.successful_behaviors += 1
        
        # Update counters
        self.total_steps = state["step_count"]
        
        # Cache current metrics
        self.current_metrics = self._calculate_current_metrics(state)
        
        logger.debug(f"Metrics collected: {self.current_metrics}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of system performance."""
        if not self.current_metrics:
            return {}
        
        session_duration = time.time() - self.session_start_time
        
        return {
            "session_duration": session_duration,
            "total_steps": self.total_steps,
            "total_decisions": self.total_decisions,
            "successful_behaviors": self.successful_behaviors,
            "success_rate": self.successful_behaviors / max(1, self.total_decisions),
            "steps_per_second": self.total_steps / max(1, session_duration),
            "current_fitness": self.current_metrics.get("fitness_score", 0),
            "current_energy": self.current_metrics.get("energy_level", 0),
            "decision_distribution": self.decision_counts.copy()
        }
    
    def get_time_series_data(self, metric: str, last_n: Optional[int] = None) -> List[float]:
        """
        Get time series data for a specific metric.
        
        Args:
            metric: Name of the metric ('fitness', 'energy', 'confidence')
            last_n: Number of recent data points to return (all if None)
        
        Returns:
            List of metric values
        """
        data_map = {
            "fitness": list(self.fitness_history),
            "energy": list(self.energy_history),
            "confidence": list(self.confidence_history)
        }
        
        data = data_map.get(metric, [])
        
        if last_n is not None and len(data) > last_n:
            data = data[-last_n:]
        
        return data
    
    def get_recent_decisions(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent decisions made by the worm."""
        return list(self.decision_history)[-count:] if self.decision_history else []
    
    def get_behavioral_patterns(self) -> Dict[str, Any]:
        """Analyze behavioral patterns from collected data."""
        patterns = {
            "most_common_decision": self._get_most_common_decision(),
            "decision_consistency": self._calculate_decision_consistency(),
            "learning_trend": self._calculate_learning_trend(),
            "energy_efficiency": self._calculate_energy_efficiency(),
            "goal_switching_frequency": len(self.goal_switches)
        }
        
        return patterns
    
    def track_goal_switch(self, old_goal: str, new_goal: str, reason: str = "user_input") -> None:
        """Track when behavioral goals are switched."""
        event = {
            "timestamp": time.time(),
            "old_goal": old_goal,
            "new_goal": new_goal,
            "reason": reason
        }
        
        self.goal_switches.append(event)
        logger.info(f"🎯 Goal switch tracked: {old_goal} → {new_goal}")
    
    def track_learning_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Track significant learning events."""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "details": details
        }
        
        self.learning_events.append(event)
        logger.info(f"📚 Learning event tracked: {event_type}")
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics for dashboard display."""
        if not self.current_metrics:
            return {}
        
        # Calculate rates and trends
        recent_fitness = self.get_time_series_data("fitness", last_n=10)
        recent_energy = self.get_time_series_data("energy", last_n=10)
        recent_confidence = self.get_time_series_data("confidence", last_n=10)
        
        fitness_trend = self._calculate_trend(recent_fitness)
        energy_trend = self._calculate_trend(recent_energy)
        
        return {
            **self.current_metrics,
            "fitness_trend": fitness_trend,
            "energy_trend": energy_trend,
            "average_confidence": sum(recent_confidence) / len(recent_confidence) if recent_confidence else 0,
            "decision_frequency": len(self.get_recent_decisions(5)),
            "behavioral_patterns": self.get_behavioral_patterns()
        }
    
    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self.timestamps.clear()
        self.fitness_history.clear()
        self.energy_history.clear()
        self.confidence_history.clear()
        self.decision_history.clear()
        
        self.decision_counts.clear()
        self.goal_switches.clear()
        self.learning_events.clear()
        
        self.session_start_time = time.time()
        self.total_steps = 0
        self.total_decisions = 0
        self.successful_behaviors = 0
        self.current_metrics = None
        
        logger.info("📊 Metrics collector reset")
    
    def _calculate_current_metrics(self, state: WormState) -> Dict[str, Any]:
        """Calculate current metrics from state."""
        return {
            "fitness_score": state["fitness_score"],
            "energy_level": state["energy_level"],
            "health_status": state["health_status"],
            "simulation_time": state["simulation_time"],
            "step_count": state["step_count"],
            "is_moving": state["is_moving"],
            "is_feeding": state["is_feeding"],
            "current_goal": state["decision_context"]["current_goal"],
            "current_decision": state["decision_context"].get("current_decision"),
            "decision_confidence": state["decision_context"]["decision_confidence"],
            "goal_progress": state["decision_context"]["goal_progress"]
        }
    
    def _get_most_common_decision(self) -> str:
        """Get the most frequently made decision."""
        if not self.decision_counts:
            return "none"
        
        return max(self.decision_counts, key=lambda x: self.decision_counts[x])
    
    def _calculate_decision_consistency(self) -> float:
        """Calculate how consistent decisions are."""
        if len(self.decision_history) < 2:
            return 1.0
        
        recent_decisions = [d["decision"] for d in list(self.decision_history)[-10:]]
        if not recent_decisions:
            return 1.0
        
        # Calculate consistency as ratio of most common decision
        decision_counts = {}
        for decision in recent_decisions:
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        max_count = max(decision_counts.values())
        return max_count / len(recent_decisions)
    
    def _calculate_learning_trend(self) -> str:
        """Calculate overall learning trend."""
        recent_fitness = self.get_time_series_data("fitness", last_n=20)
        
        if len(recent_fitness) < 5:
            return "insufficient_data"
        
        # Simple trend calculation
        first_half = recent_fitness[:len(recent_fitness)//2]
        second_half = recent_fitness[len(recent_fitness)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.05:
            return "improving"
        elif second_avg < first_avg * 0.95:
            return "declining"
        else:
            return "stable"
    
    def _calculate_energy_efficiency(self) -> float:
        """Calculate energy efficiency (fitness gained per energy spent)."""
        if not self.fitness_history or not self.energy_history:
            return 0.0
        
        fitness_gained = self.fitness_history[-1] - (self.fitness_history[0] if self.fitness_history else 0)
        energy_spent = (self.energy_history[0] if self.energy_history else 1.0) - self.energy_history[-1]
        
        if energy_spent <= 0:
            return float('inf')  # Perfect efficiency
        
        return fitness_gained / energy_spent
    
    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate trend direction for a data series."""
        if len(data) < 3:
            return "stable"
        
        # Simple linear trend
        recent = data[-3:]
        if recent[-1] > recent[0] * 1.02:
            return "increasing"
        elif recent[-1] < recent[0] * 0.98:
            return "decreasing"
        else:
            return "stable" 