"""
OpenWorm Integration Client for Agentic Worm System.

This module provides direct integration with OpenWorm's c302 neural model
and Sibernetic physics engine for real biological simulation data.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenWormClient:
    """
    Client for communicating with OpenWorm simulation APIs.
    
    Provides interfaces to:
    - c302 neural model (302 neurons of C. elegans)
    - Sibernetic physics engine 
    - Geppetto visualization platform
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:9000",
                 timeout: float = 1.0,
                 enable_fallback: bool = True):
        """
        Initialize OpenWorm client.
        
        Args:
            base_url: Base URL for OpenWorm API server
            timeout: Request timeout in seconds
            enable_fallback: Whether to use simulated data when OpenWorm unavailable
        """
        self.base_url = base_url
        self.timeout = timeout
        self.enable_fallback = enable_fallback
        self.is_connected = False
        self.connection_attempts = 0
        self.last_connection_check = 0.0
        
        # Cache for performance
        self._neuron_cache: Dict[str, Any] = {}
        self._last_cache_update = 0.0
        
    async def initialize(self) -> bool:
        """Initialize connection to OpenWorm simulation."""
        logger.info("🔗 Initializing OpenWorm connection...")
        
        try:
            # Test connection
            health = await self.get_health_status()
            if health.get("status") == "healthy":
                self.is_connected = True
                logger.info("✅ Connected to OpenWorm simulation successfully")
                
                # Log simulation info
                sim_info = await self.get_simulation_info()
                logger.info(f"📊 OpenWorm: {sim_info.get('model', 'c302')} model, "
                          f"{sim_info.get('neurons', 302)} neurons")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ OpenWorm connection failed: {e}")
            if self.enable_fallback:
                logger.info("🔄 Falling back to enhanced simulation mode")
            
        self.is_connected = False
        return self.enable_fallback
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Check OpenWorm simulation health."""
        return await self._make_request("GET", "/api/health")
    
    async def get_simulation_info(self) -> Dict[str, Any]:
        """Get current simulation information."""
        return await self._make_request("GET", "/api/simulation/info")
    
    async def get_neural_state(self) -> Dict[str, Any]:
        """Get current neural network state from c302 model."""
        current_time = datetime.now().timestamp()
        
        # Use cache to avoid overwhelming the API
        if (current_time - self._last_cache_update) < 0.1:  # 100ms cache
            return self._neuron_cache
        
        try:
            data = await self._make_request("GET", "/api/neural/state")
            self._neuron_cache = data
            self._last_cache_update = current_time
            return data
            
        except Exception:
            # Return cached data if request fails
            return self._neuron_cache or self._generate_fallback_neural_state()
    
    async def get_sensory_data(self, sensor_type: str = "all") -> Dict[str, Any]:
        """
        Get sensory data from OpenWorm.
        
        Args:
            sensor_type: Type of sensor data ('chemotaxis', 'mechanosensory', 'all')
        """
        endpoint = f"/api/sensory/{sensor_type}" if sensor_type != "all" else "/api/sensory"
        return await self._make_request("GET", endpoint)
    
    async def send_motor_commands(self, commands: Dict[str, float]) -> Dict[str, Any]:
        """
        Send motor commands to Sibernetic physics engine.
        
        Args:
            commands: Motor activation commands
        """
        return await self._make_request("POST", "/api/motor/activate", data=commands)
    
    async def get_body_state(self) -> Dict[str, Any]:
        """Get current body position and physics state."""
        return await self._make_request("GET", "/api/physics/body")
    
    async def set_environment_conditions(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Set environmental conditions (food, obstacles, etc.)."""
        return await self._make_request("POST", "/api/environment/conditions", data=conditions)
    
    async def get_connectome_data(self) -> Dict[str, Any]:
        """Get C. elegans connectome data."""
        return await self._make_request("GET", "/api/neural/connectome")
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to OpenWorm API."""
        if not self.is_connected and not self.enable_fallback:
            raise ConnectionError("OpenWorm not connected")
        
        try:
            # Dynamic import to handle missing aiohttp gracefully
            import aiohttp
            
            url = f"{self.base_url}{endpoint}"
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if method == "GET":
                    async with session.get(url) as response:
                        return await self._handle_response(response)
                elif method == "POST":
                    async with session.post(url, json=data) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
        except ImportError:
            logger.warning("aiohttp not available - using fallback simulation")
            return self._generate_fallback_response(endpoint, data)
        except Exception as e:
            logger.debug(f"OpenWorm API request failed: {e}")
            if self.enable_fallback:
                return self._generate_fallback_response(endpoint, data)
            raise
    
    async def _handle_response(self, response) -> Dict[str, Any]:
        """Handle HTTP response from OpenWorm."""
        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            raise ValueError(f"OpenWorm API endpoint not found: {response.url}")
        else:
            raise ConnectionError(f"OpenWorm API error: {response.status}")
    
    def _generate_fallback_response(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate realistic fallback data when OpenWorm is unavailable."""
        current_time = datetime.now().timestamp()
        
        if "health" in endpoint:
            return {"status": "simulated", "uptime": current_time, "mode": "fallback"}
        
        elif "simulation/info" in endpoint:
            return {
                "model": "c302_simulated", 
                "neurons": 302,
                "version": "fallback_1.0",
                "physics_engine": "simulated"
            }
        
        elif "neural/state" in endpoint:
            return self._generate_fallback_neural_state()
        
        elif "sensory" in endpoint:
            return self._generate_fallback_sensory_data()
        
        elif "motor" in endpoint:
            return {"success": True, "status": "simulated", "applied_commands": data or {}}
        
        elif "physics/body" in endpoint:
            return {
                "position": {"x": 0.0, "y": 0.0, "z": 0.0},
                "orientation": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
                "velocity": {"linear": 0.1, "angular": 0.05},
                "simulated": True
            }
        
        else:
            return {"status": "simulated", "timestamp": current_time}
    
    def _generate_fallback_neural_state(self) -> Dict[str, Any]:
        """Generate realistic neural activity data."""
        import random
        current_time = datetime.now().timestamp()
        
        # Simulate realistic C. elegans neural activity
        neurons = {}
        for i in range(302):  # C. elegans has 302 neurons
            neuron_id = f"neuron_{i}"
            # Realistic membrane potential (-70 to -50 mV)
            membrane_potential = -70 + 20 * random.random()
            # Realistic firing rate (0-100 Hz)
            firing_rate = 50 * random.random() if membrane_potential > -60 else 0
            
            neurons[neuron_id] = {
                "membrane_potential": membrane_potential,
                "firing_rate": firing_rate,
                "synaptic_activity": random.random()
            }
        
        return {
            "neurons": neurons,
            "timestamp": current_time,
            "simulation_step": int(current_time * 1000) % 1000000,
            "global_activity": sum(n["firing_rate"] for n in neurons.values()) / 302,
            "simulated": True
        }
    
    def _generate_fallback_sensory_data(self) -> Dict[str, Any]:
        """Generate realistic sensory data."""
        current_time = datetime.now().timestamp()
        
        return {
            "chemotaxis": {
                "gradient_strength": 0.3 + 0.2 * (current_time % 10) / 10,
                "concentration": 0.1 + 0.3 * (current_time % 5) / 5,
                "direction": (current_time * 30) % 360
            },
            "mechanosensory": {
                "pressure": 0.2 + 0.1 * (current_time % 3) / 3,
                "touch_anterior": 0.0,
                "touch_posterior": 0.0
            },
            "thermosensory": 20.0 + 5 * (current_time % 20) / 20,  # 20-25°C
            "timestamp": current_time,
            "simulated": True
        }
    
    async def close(self):
        """Close OpenWorm connection."""
        self.is_connected = False
        logger.info("🔌 OpenWorm connection closed")


# Global client instance
_openworm_client: Optional[OpenWormClient] = None

def get_openworm_client() -> OpenWormClient:
    """Get global OpenWorm client instance."""
    global _openworm_client
    if _openworm_client is None:
        _openworm_client = OpenWormClient()
    return _openworm_client

async def initialize_openworm() -> bool:
    """Initialize global OpenWorm client."""
    client = get_openworm_client()
    return await client.initialize()

async def close_openworm():
    """Close global OpenWorm client."""
    global _openworm_client
    if _openworm_client:
        await _openworm_client.close()
        _openworm_client = None 