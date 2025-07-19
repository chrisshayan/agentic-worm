"""
Tools for interfacing with sensory input and motor output systems.

These tools provide the interface between the AI intelligence layer
and the OpenWorm simulation environment.
"""

from typing import Dict, List, Any
from ..core.state import WormState


class SensoryTools:
    """Tools for processing sensory input from the OpenWorm simulation."""
    
    def __init__(self):
        self.name = "sensory_tools"
    
    async def get_chemotaxis_data(self, state: WormState) -> Dict[str, float]:
        """Get chemical gradient information from OpenWorm c302 neural model."""
        try:
            # Try to connect to OpenWorm API (default Docker container)
            import aiohttp
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1.0)) as session:
                async with session.get('http://localhost:9000/api/sensory/chemotaxis') as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "food_gradient": data.get("gradient_strength", 0.5),
                            "chemical_concentration": data.get("concentration", 0.3),
                            "gradient_direction": data.get("direction", 0.0)
                        }
        except (ImportError, Exception):
            # Fallback to enhanced simulation if OpenWorm/aiohttp not available
            pass
        
        # Enhanced simulation based on goal-directed behavior
        goal = state["decision_context"]["current_goal"]
        time_factor = state["simulation_time"] / 100.0
        
        if goal == "find_food":
            # Simulate approaching food source
            gradient = 0.3 + 0.4 * (time_factor % 1.0)
            concentration = 0.2 + 0.3 * (gradient - 0.3) / 0.4
        else:
            # Background chemical environment
            gradient = 0.2 + 0.1 * (time_factor % 1.0)
            concentration = 0.1 + 0.2 * gradient
            
        return {
            "food_gradient": min(1.0, gradient),
            "chemical_concentration": min(1.0, concentration), 
            "gradient_direction": (time_factor * 30) % 360  # Degrees
        }
    
    async def get_mechanosensory_data(self, state: WormState) -> Dict[str, float]:
        """Get mechanical/touch sensor data."""
        # Placeholder - will interface with OpenWorm touch sensors
        return {"pressure": 0.2, "touch_anterior": 0.0, "touch_posterior": 0.0}
    
    async def get_proprioception_data(self, state: WormState) -> Dict[str, float]:
        """Get body position and orientation data."""
        # Placeholder - will interface with OpenWorm body state
        return {"body_curvature": 0.1, "head_angle": 0.0, "movement_speed": 0.5}


class MotorTools:
    """Tools for sending motor commands to the OpenWorm simulation."""
    
    def __init__(self):
        self.name = "motor_tools"
    
    async def set_muscle_activation(self, muscle_commands: Dict[str, float]) -> bool:
        """Send muscle activation commands to OpenWorm Sibernetic physics engine."""
        try:
            # Try to send commands to OpenWorm motor API
            import aiohttp
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=0.5)) as session:
                payload = {
                    "dorsal_muscles": muscle_commands.get("dorsal", 0.0),
                    "ventral_muscles": muscle_commands.get("ventral", 0.0),
                    "timestamp": muscle_commands.get("timestamp", 0.0)
                }
                async with session.post('http://localhost:9000/api/motor/muscles', json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"🔧 OpenWorm Motor: {muscle_commands} → {result.get('status', 'applied')}")
                        return result.get("success", True)
        except (ImportError, Exception):
            # Fallback to simulation if OpenWorm not available
            pass
        
        # Enhanced simulation feedback
        print(f"🔧 Motor simulation: Dorsal={muscle_commands.get('dorsal', 0):.2f}, "
              f"Ventral={muscle_commands.get('ventral', 0):.2f}")
        
        # Simulate realistic motor response
        activation_sum = muscle_commands.get('dorsal', 0) + muscle_commands.get('ventral', 0)
        return activation_sum > 0.1  # Success if there's meaningful activation
    
    async def set_pharynx_pump(self, pump_rate: float) -> bool:
        """Control pharynx pumping for feeding."""
        # Placeholder - will interface with OpenWorm feeding system
        print(f"🍽️ Pharynx pump: {pump_rate}")
        return True
    
    async def trigger_egg_laying(self, should_lay: bool) -> bool:
        """Trigger egg laying behavior."""
        # Placeholder - will interface with OpenWorm reproductive system
        if should_lay:
            print("🥚 Egg laying triggered")
        return True 