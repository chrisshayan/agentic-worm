"""
Real-time Dashboard Server for Agentic Worm Visualization.

This module provides a FastAPI-based web dashboard that visualizes the AI 
decision-making process, neural activity, and worm behavior in real-time.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ..core.state import WormState
from ..core.system import AgenticWormSystem

logger = logging.getLogger(__name__)


class DashboardServer:
    """
    Real-time dashboard server for visualizing agentic worm behavior.
    
    Provides a web interface showing:
    - Real-time decision-making process
    - Neural activity visualization  
    - Motor commands and muscle activation
    - Performance metrics and learning progress
    - Interactive controls for goals and parameters
    """
    
    def __init__(self, port: int = 8888, host: str = "localhost"):
        """
        Initialize the dashboard server.
        
        Args:
            port: Port to run the server on
            host: Host address to bind to
        """
        self.port = port
        self.host = host
        self.app = None
        self.worm_system: Optional[AgenticWormSystem] = None
        self.active_connections: List[WebSocket] = []
        self.is_running = False
        
        if not FASTAPI_AVAILABLE:
            logger.warning("⚠️ FastAPI not available - dashboard will use console mode")
            self.console_mode = True
        else:
            self.console_mode = False
            self._setup_fastapi()
    
    def _setup_fastapi(self) -> None:
        """Setup FastAPI application with routes and WebSocket endpoints."""
        self.app = FastAPI(
            title="Agentic Worm Dashboard",
            description="Real-time visualization of AI-driven digital organism",
            version="1.0.0"
        )
        
        # Enable CORS for development
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Routes
        self.app.get("/")(self.get_dashboard)
        self.app.websocket("/ws")(self.websocket_endpoint)
        self.app.get("/api/state")(self.get_current_state)
        self.app.post("/api/goal")(self.set_goal)
        self.app.get("/api/metrics")(self.get_metrics)
        self.app.get("/api/status")(self.get_system_status)
    
    async def get_dashboard(self) -> HTMLResponse:
        """Serve the main dashboard HTML page."""
        html_content = self._generate_dashboard_html()
        return HTMLResponse(content=html_content)
    
    async def websocket_endpoint(self, websocket: WebSocket):
        """WebSocket endpoint for real-time data streaming."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            while True:
                # Send real-time state updates
                if self.worm_system and self.worm_system.current_state:
                    state_data = self._serialize_state(self.worm_system.current_state)
                    await websocket.send_json({
                        "type": "state_update",
                        "data": state_data,
                        "timestamp": datetime.now().isoformat()
                    })
                
                await asyncio.sleep(0.1)  # 10 FPS update rate
                
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
    
    async def get_current_state(self) -> Dict[str, Any]:
        """API endpoint to get current worm state."""
        if not self.worm_system or not self.worm_system.current_state:
            raise HTTPException(status_code=404, detail="No active worm system")
        
        return self._serialize_state(self.worm_system.current_state)
    
    async def set_goal(self, goal_data: Dict[str, Any]) -> Dict[str, str]:
        """API endpoint to set a new behavioral goal."""
        if not self.worm_system or not self.worm_system.current_state:
            raise HTTPException(status_code=404, detail="No active worm system")
        
        goal = goal_data.get("goal", "explore_environment")
        priority = goal_data.get("priority", 1.0)
        
        # Update the worm's goal
        self.worm_system.current_state["decision_context"]["current_goal"] = goal
        self.worm_system.current_state["decision_context"]["goal_priority"] = priority
        self.worm_system.current_state["decision_context"]["goal_progress"] = 0.0
        
        logger.info(f"🎯 Goal updated to: {goal} (priority: {priority})")
        
        # Broadcast update to all connected clients
        await self._broadcast_update({
            "type": "goal_changed",
            "goal": goal,
            "priority": priority
        })
        
        return {"status": "success", "message": f"Goal set to {goal}"}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """API endpoint to get performance metrics."""
        if not self.worm_system:
            raise HTTPException(status_code=404, detail="No active worm system")
        
        metrics = await self.worm_system.get_performance_metrics()
        return metrics
    
    async def get_system_status(self) -> Dict[str, Any]:
        """API endpoint to get system status."""
        status = {
            "dashboard_running": self.is_running,
            "worm_system_active": self.worm_system is not None,
            "active_connections": len(self.active_connections),
            "console_mode": self.console_mode
        }
        
        if self.worm_system:
            status["system_initialized"] = self.worm_system.is_initialized
            if hasattr(self.worm_system, 'agentic_workflow'):
                status["ai_workflow_active"] = self.worm_system.agentic_workflow is not None
        
        return status
    
    def connect_worm_system(self, worm_system: AgenticWormSystem) -> None:
        """Connect a worm system to the dashboard for visualization."""
        self.worm_system = worm_system
        logger.info("🔗 Worm system connected to dashboard")
    
    async def start_server(self) -> None:
        """Start the dashboard server."""
        if self.console_mode:
            logger.info("📊 Starting dashboard in console mode (FastAPI not available)")
            self.is_running = True
            await self._console_dashboard()
        else:
            logger.info(f"🚀 Starting dashboard server at http://{self.host}:{self.port}")
            self.is_running = True
            
            try:
                config = uvicorn.Config(
                    app=self.app,
                    host=self.host,
                    port=self.port,
                    log_level="info"
                )
                server = uvicorn.Server(config)
                await server.serve()
            except Exception as e:
                logger.error(f"❌ Failed to start dashboard server: {e}")
                self.is_running = False
    
    async def stop_server(self) -> None:
        """Stop the dashboard server."""
        self.is_running = False
        logger.info("🛑 Dashboard server stopped")
    
    async def _console_dashboard(self) -> None:
        """Run dashboard in console mode when FastAPI is not available."""
        logger.info("📊 Console Dashboard Active - Real-time metrics:")
        logger.info("=" * 50)
        
        try:
            while self.is_running:
                if self.worm_system and self.worm_system.current_state:
                    state = self.worm_system.current_state
                    
                    # Display key metrics in console
                    decision = state["decision_context"].get("current_decision", "none")
                    confidence = state["decision_context"].get("decision_confidence", 0)
                    fitness = state["fitness_score"]
                    energy = state["energy_level"]
                    step = state["step_count"]
                    
                    print(f"\r🧠 Step {step}: {decision} | "
                          f"Confidence: {confidence:.2f} | "
                          f"Fitness: {fitness:.3f} | "
                          f"Energy: {energy:.3f}", end="", flush=True)
                
                await asyncio.sleep(1.0)  # Update every second in console mode
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Console dashboard stopped by user")
            self.is_running = False
    
    async def _broadcast_update(self, data: Dict[str, Any]) -> None:
        """Broadcast update to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)
    
    def _serialize_state(self, state: WormState) -> Dict[str, Any]:
        """Serialize worm state for JSON transmission."""
        return {
            "simulation_time": state["simulation_time"],
            "step_count": state["step_count"],
            "fitness_score": state["fitness_score"],
            "energy_level": state["energy_level"],
            "health_status": state["health_status"],
            "is_moving": state["is_moving"],
            "is_feeding": state["is_feeding"],
            "decision_context": {
                "current_goal": state["decision_context"]["current_goal"],
                "current_decision": state["decision_context"].get("current_decision"),
                "decision_confidence": state["decision_context"]["decision_confidence"],
                "decision_rationale": state["decision_context"].get("decision_rationale"),
                "goal_progress": state["decision_context"]["goal_progress"]
            },
            "motor_commands": {
                "muscle_activations": state["motor_commands"].get("muscle_activations", {}),
                "pharynx_pump": state["motor_commands"].get("pharynx_pump", 0.0)
            },
            "sensory_data": {
                "chemotaxis": state["sensory_data"].get("chemotaxis", {}),
                "mechanosensory": state["sensory_data"].get("mechanosensory", {})
            },
            "neural_activity": {
                "cognitive_assessment": state["neural_state"].get("cognitive_assessment"),
                "behavioral_strategy": state["neural_state"].get("behavioral_strategy")
            },
            "learning_metrics": {
                "recent_rewards": state["learning_state"]["recent_rewards"][-10:],  # Last 10 rewards
                "behavior_success_rates": state["learning_state"]["behavior_success_rates"]
            }
        }
    
    def _generate_dashboard_html(self) -> str:
        """Generate the dashboard HTML page."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Agentic Worm Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-size: 1.2em;
            opacity: 0.8;
            margin-top: 10px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .widget {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .widget h3 {
            margin: 0 0 15px 0;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .metric-value {
            font-weight: bold;
            color: #4ade80;
        }
        .decision-display {
            font-size: 1.1em;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .confidence-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981);
            transition: width 0.3s ease;
        }
        .controls {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .control-group {
            margin-bottom: 20px;
        }
        .control-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        select, button {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.9);
            color: #333;
        }
        button {
            background: linear-gradient(135deg, #4ade80, #10b981);
            color: white;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-connected { background: #10b981; }
        .status-disconnected { background: #ef4444; }
        .log-display {
            height: 200px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            font-family: 'SF Mono', Consolas, monospace;
            font-size: 14px;
            line-height: 1.4;
        }
        .neural-visualization {
            grid-column: span 2;
        }
        
        /* 3D Worm Visualization Styles */
        .worm-3d-container {
            grid-column: span 2;
        }
        
        .worm-viewer {
            text-align: center;
        }
        
        #wormCanvas {
            background: linear-gradient(45deg, #0a1a2a, #1a2a3a);
            border: 2px solid #333;
            border-radius: 12px;
            cursor: grab;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }
        
        #wormCanvas:active {
            cursor: grabbing;
        }
        
        #wormCanvas:hover {
            transform: scale(1.02);
        }
        
        .worm-controls button {
            background: #4a9eff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
            margin: 0 3px;
        }
        
        .worm-controls button:hover {
            background: #357abd;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            .neural-visualization, .worm-3d-container {
                grid-column: span 1;
            }
            #wormCanvas {
                width: 100%;
                height: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Agentic Worm Dashboard</h1>
            <div class="subtitle">Real-time AI-driven Digital Organism Visualization</div>
            <div style="margin-top: 15px;">
                <span class="status-indicator" id="connectionStatus"></span>
                <span id="connectionText">Connecting...</span>
            </div>
        </div>

        <div class="dashboard-grid">
            <!-- Current Decision Widget -->
            <div class="widget">
                <h3>🎯 Current Decision</h3>
                <div class="decision-display">
                    <div><strong>Action:</strong> <span id="currentAction">-</span></div>
                    <div><strong>Goal:</strong> <span id="currentGoal">-</span></div>
                    <div><strong>Confidence:</strong> <span id="confidence">0%</span></div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" id="confidenceBar" style="width: 0%"></div>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                        <strong>Rationale:</strong> <span id="rationale">-</span>
                    </div>
                </div>
            </div>

            <!-- Performance Metrics Widget -->
            <div class="widget">
                <h3>📊 Performance Metrics</h3>
                <div class="metric">
                    <span>Fitness Score</span>
                    <span class="metric-value" id="fitness">0.000</span>
                </div>
                <div class="metric">
                    <span>Energy Level</span>
                    <span class="metric-value" id="energy">100%</span>
                </div>
                <div class="metric">
                    <span>Health Status</span>
                    <span class="metric-value" id="health">100%</span>
                </div>
                <div class="metric">
                    <span>Simulation Time</span>
                    <span class="metric-value" id="simTime">0.00s</span>
                </div>
                <div class="metric">
                    <span>Steps Taken</span>
                    <span class="metric-value" id="steps">0</span>
                </div>
            </div>

            <!-- Motor Commands Widget -->
            <div class="widget">
                <h3>⚡ Motor Commands</h3>
                <div class="metric">
                    <span>Dorsal Muscles</span>
                    <span class="metric-value" id="dorsalMuscle">0.0</span>
                </div>
                <div class="metric">
                    <span>Ventral Muscles</span>
                    <span class="metric-value" id="ventralMuscle">0.0</span>
                </div>
                <div class="metric">
                    <span>Pharynx Pump</span>
                    <span class="metric-value" id="pharynxPump">0.0</span>
                </div>
                <div class="metric">
                    <span>Movement Status</span>
                    <span class="metric-value" id="movementStatus">Idle</span>
                </div>
            </div>

            <!-- Neural Visualization Widget -->
            <div class="widget neural-visualization">
                <h3>🧠 Neural Activity & Learning</h3>
                <div style="height: 200px;">
                    <canvas id="neuralChart"></canvas>
                </div>
            </div>

            <!-- 3D Worm Visualization Widget -->
            <div class="widget worm-3d-container">
                <h3>🐛 3D Worm Simulation</h3>
                <div class="worm-viewer">
                    <canvas id="wormCanvas" width="450" height="350"></canvas>
                    <div class="worm-controls" style="margin-top: 10px; text-align: center;">
                        <button onclick="resetWormView()" style="margin: 5px;">🔄 Reset View</button>
                        <button onclick="addFood()" style="margin: 5px;">🍎 Add Food</button>
                        <button onclick="toggleWormMovement()" style="margin: 5px;">⏯️ Pause/Play</button>
                        <div style="margin-top: 8px; font-size: 0.9em;">
                            <span id="wormPosition">Position: (0.0, 0.0)</span> | 
                            <span id="wormSpeed">Speed: 0.0</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Controls Widget -->
            <div class="widget">
                <h3>🎮 Controls</h3>
                <div class="control-group">
                    <label for="goalSelect">Set Behavioral Goal:</label>
                    <select id="goalSelect">
                        <option value="find_food">🍽️ Find Food</option>
                        <option value="explore_environment">🔍 Explore Environment</option>
                        <option value="navigate_obstacles">🚧 Navigate Obstacles</option>
                        <option value="social_interaction">👥 Social Interaction</option>
                    </select>
                </div>
                <button onclick="updateGoal()">Update Goal</button>
                <button onclick="resetSystem()" style="margin-top: 10px; background: linear-gradient(135deg, #f59e0b, #dc2626);">Reset System</button>
            </div>
        </div>

        <!-- Activity Log -->
        <div class="controls">
            <h3>📝 Activity Log</h3>
            <div class="log-display" id="activityLog">
                <div>🚀 Dashboard initialized...</div>
            </div>
        </div>
    </div>

    <script>
        let socket;
        let neuralChart;
        let isConnected = false;

        // Initialize dashboard
        function initDashboard() {
            connectWebSocket();
            setupNeuralChart();
            initWormVisualization();
            logActivity('🔗 Connecting to agentic worm system...');
        }

        // WebSocket connection
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(event) {
                isConnected = true;
                updateConnectionStatus(true);
                logActivity('✅ Connected to agentic worm system');
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleRealtimeUpdate(data);
            };
            
            socket.onclose = function(event) {
                isConnected = false;
                updateConnectionStatus(false);
                logActivity('❌ Connection lost - attempting to reconnect...');
                
                // Attempt to reconnect after 3 seconds
                setTimeout(connectWebSocket, 3000);
            };
            
            socket.onerror = function(error) {
                logActivity('⚠️ WebSocket error occurred');
            };
        }

        // Handle real-time updates
        function handleRealtimeUpdate(data) {
            if (data.type === 'state_update') {
                updateDashboard(data.data);
            } else if (data.type === 'goal_changed') {
                logActivity(`🎯 Goal changed to: ${data.goal}`);
            }
        }

        // Update dashboard with new data
        function updateDashboard(state) {
            // Decision info
            document.getElementById('currentAction').textContent = state.decision_context.current_decision || 'none';
            document.getElementById('currentGoal').textContent = state.decision_context.current_goal || 'none';
            
            const confidence = Math.round((state.decision_context.decision_confidence || 0) * 100);
            document.getElementById('confidence').textContent = confidence + '%';
            document.getElementById('confidenceBar').style.width = confidence + '%';
            document.getElementById('rationale').textContent = state.decision_context.decision_rationale || 'none';

            // Performance metrics
            document.getElementById('fitness').textContent = (state.fitness_score || 0).toFixed(3);
            document.getElementById('energy').textContent = Math.round((state.energy_level || 0) * 100) + '%';
            document.getElementById('health').textContent = Math.round((state.health_status || 0) * 100) + '%';
            document.getElementById('simTime').textContent = (state.simulation_time || 0).toFixed(2) + 's';
            document.getElementById('steps').textContent = state.step_count || 0;

            // Motor commands
            const dorsal = (state.motor_commands.muscle_activations?.dorsal || 0).toFixed(1);
            const ventral = (state.motor_commands.muscle_activations?.ventral || 0).toFixed(1);
            document.getElementById('dorsalMuscle').textContent = dorsal;
            document.getElementById('ventralMuscle').textContent = ventral;
            document.getElementById('pharynxPump').textContent = (state.motor_commands.pharynx_pump || 0).toFixed(1);
            
            const status = state.is_moving ? '🚶 Moving' : (state.is_feeding ? '🍽️ Feeding' : '😴 Idle');
            document.getElementById('movementStatus').textContent = status;

            // Update neural chart
            updateNeuralChart(state);
        }

        // Setup neural activity chart
        function setupNeuralChart() {
            const ctx = document.getElementById('neuralChart').getContext('2d');
            neuralChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Decision Confidence',
                        data: [],
                        borderColor: '#4ade80',
                        backgroundColor: 'rgba(74, 222, 128, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Fitness Score',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: 'white' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: {
                            ticks: { color: 'white' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    }
                }
            });
        }

        // Update neural chart with new data
        function updateNeuralChart(state) {
            const time = (state.simulation_time || 0).toFixed(1);
            const confidence = state.decision_context.decision_confidence || 0;
            const fitness = state.fitness_score || 0;

            neuralChart.data.labels.push(time);
            neuralChart.data.datasets[0].data.push(confidence);
            neuralChart.data.datasets[1].data.push(fitness);

            // Keep only last 50 data points
            if (neuralChart.data.labels.length > 50) {
                neuralChart.data.labels.shift();
                neuralChart.data.datasets[0].data.shift();
                neuralChart.data.datasets[1].data.shift();
            }

            neuralChart.update('none');
        }

        // Update connection status
        function updateConnectionStatus(connected) {
            const statusEl = document.getElementById('connectionStatus');
            const textEl = document.getElementById('connectionText');
            
            if (connected) {
                statusEl.className = 'status-indicator status-connected';
                textEl.textContent = 'Connected';
            } else {
                statusEl.className = 'status-indicator status-disconnected';
                textEl.textContent = 'Disconnected';
            }
        }

        // Log activity
        function logActivity(message) {
            const logEl = document.getElementById('activityLog');
            const timestamp = new Date().toLocaleTimeString();
            logEl.innerHTML += `<div>[${timestamp}] ${message}</div>`;
            logEl.scrollTop = logEl.scrollHeight;
        }

        // Update goal
        async function updateGoal() {
            const goal = document.getElementById('goalSelect').value;
            
            try {
                const response = await fetch('/api/goal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ goal: goal, priority: 1.0 })
                });
                
                if (response.ok) {
                    logActivity(`🎯 Goal updated to: ${goal}`);
                } else {
                    logActivity('❌ Failed to update goal');
                }
            } catch (error) {
                logActivity('❌ Error updating goal');
            }
        }

        // Reset system
        async function resetSystem() {
            logActivity('🔄 System reset requested');
            // Implement reset functionality
        }

        // 3D Worm Visualization System
        let wormRenderer = null;
        let wormAnimationId = null;
        let wormPaused = false;
        
        function initWormVisualization() {
            const canvas = document.getElementById('wormCanvas');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            if (!ctx) return;
            
            wormRenderer = new WormRenderer(canvas, ctx);
            wormRenderer.init();
            startWormAnimation();
            logActivity('🐛 3D Worm visualization initialized');
        }
        
        class WormRenderer {
            constructor(canvas, ctx) {
                this.canvas = canvas;
                this.ctx = ctx;
                this.width = canvas.width;
                this.height = canvas.height;
                
                // Worm state
                this.worm = {
                    segments: [],
                    x: this.width / 2,
                    y: this.height / 2,
                    angle: 0,
                    speed: 0,
                    targetX: this.width / 2,
                    targetY: this.height / 2
                };
                
                // Environment
                this.food = [];
                
                // Visual settings
                this.segmentCount = 12;
                this.segmentLength = 8;
                this.wormWidth = 12;
                
                this.initWormSegments();
                this.spawnFood();
            }
            
            init() {
                this.canvas.addEventListener('click', (e) => this.onCanvasClick(e));
            }
            
            initWormSegments() {
                this.worm.segments = [];
                for (let i = 0; i < this.segmentCount; i++) {
                    this.worm.segments.push({
                        x: this.worm.x - i * this.segmentLength,
                        y: this.worm.y,
                        angle: 0
                    });
                }
            }
            
            spawnFood() {
                for (let i = 0; i < 3; i++) {
                    this.food.push({
                        x: Math.random() * (this.width - 40) + 20,
                        y: Math.random() * (this.height - 40) + 20,
                        size: 6 + Math.random() * 4,
                        eaten: false
                    });
                }
            }
            
            onCanvasClick(e) {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                // Set new target for worm
                this.worm.targetX = x;
                this.worm.targetY = y;
            }
            
            update() {
                if (wormPaused) return;
                
                // Update worm movement
                this.updateWormMovement();
                this.updateWormSegments();
                this.checkFoodCollision();
                this.updateUI();
            }
            
            updateWormMovement() {
                // Calculate direction to target
                const dx = this.worm.targetX - this.worm.x;
                const dy = this.worm.targetY - this.worm.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance > 5) {
                    const targetAngle = Math.atan2(dy, dx);
                    
                    // Smooth angle transition
                    let angleDiff = targetAngle - this.worm.angle;
                    if (angleDiff > Math.PI) angleDiff -= 2 * Math.PI;
                    if (angleDiff < -Math.PI) angleDiff += 2 * Math.PI;
                    
                    this.worm.angle += angleDiff * 0.05;
                    this.worm.speed = Math.min(2.5, distance * 0.02);
                    
                    // Move worm
                    this.worm.x += Math.cos(this.worm.angle) * this.worm.speed;
                    this.worm.y += Math.sin(this.worm.angle) * this.worm.speed;
                    
                    // Keep in bounds
                    this.worm.x = Math.max(20, Math.min(this.width - 20, this.worm.x));
                    this.worm.y = Math.max(20, Math.min(this.height - 20, this.worm.y));
                } else {
                    this.worm.speed *= 0.95;
                }
            }
            
            updateWormSegments() {
                if (this.worm.segments.length > 0) {
                    this.worm.segments[0].x = this.worm.x;
                    this.worm.segments[0].y = this.worm.y;
                    this.worm.segments[0].angle = this.worm.angle;
                }
                
                // Body segments follow
                for (let i = 1; i < this.worm.segments.length; i++) {
                    const prev = this.worm.segments[i - 1];
                    const curr = this.worm.segments[i];
                    
                    const dx = prev.x - curr.x;
                    const dy = prev.y - curr.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    
                    if (distance > this.segmentLength) {
                        const angle = Math.atan2(dy, dx);
                        curr.x = prev.x - Math.cos(angle) * this.segmentLength;
                        curr.y = prev.y - Math.sin(angle) * this.segmentLength;
                        curr.angle = angle;
                    }
                }
            }
            
            checkFoodCollision() {
                this.food.forEach(food => {
                    if (!food.eaten) {
                        const dx = food.x - this.worm.x;
                        const dy = food.y - this.worm.y;
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        
                        if (distance < 20) {
                            food.eaten = true;
                            this.findNewFoodTarget();
                            logActivity('🍽️ Worm found food!');
                        }
                    }
                });
                
                // Respawn food if needed
                const activeFood = this.food.filter(f => !f.eaten);
                if (activeFood.length < 2) {
                    this.spawnFood();
                }
            }
            
            findNewFoodTarget() {
                const availableFood = this.food.filter(f => !f.eaten);
                if (availableFood.length > 0) {
                    const nearest = availableFood[Math.floor(Math.random() * availableFood.length)];
                    this.worm.targetX = nearest.x;
                    this.worm.targetY = nearest.y;
                } else {
                    // Explore randomly
                    this.worm.targetX = Math.random() * (this.width - 40) + 20;
                    this.worm.targetY = Math.random() * (this.height - 40) + 20;
                }
            }
            
            updateUI() {
                document.getElementById('wormPosition').textContent = 
                    `Position: (${this.worm.x.toFixed(1)}, ${this.worm.y.toFixed(1)})`;
                document.getElementById('wormSpeed').textContent = 
                    `Speed: ${this.worm.speed.toFixed(2)}`;
            }
            
            render() {
                // Clear canvas
                this.ctx.fillStyle = 'rgba(10, 26, 42, 0.1)';
                this.ctx.fillRect(0, 0, this.width, this.height);
                
                // Render environment
                this.renderGrid();
                this.renderFood();
                this.renderWorm();
                this.renderTarget();
            }
            
            renderGrid() {
                this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                this.ctx.lineWidth = 1;
                
                for (let x = 0; x < this.width; x += 50) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(x, 0);
                    this.ctx.lineTo(x, this.height);
                    this.ctx.stroke();
                }
                
                for (let y = 0; y < this.height; y += 50) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, y);
                    this.ctx.lineTo(this.width, y);
                    this.ctx.stroke();
                }
            }
            
            renderFood() {
                this.food.forEach(food => {
                    if (!food.eaten) {
                        this.ctx.fillStyle = '#ff6b35';
                        this.ctx.beginPath();
                        this.ctx.arc(food.x, food.y, food.size, 0, Math.PI * 2);
                        this.ctx.fill();
                        
                        // Food glow
                        this.ctx.fillStyle = 'rgba(255, 107, 53, 0.3)';
                        this.ctx.beginPath();
                        this.ctx.arc(food.x, food.y, food.size * 2, 0, Math.PI * 2);
                        this.ctx.fill();
                    }
                });
            }
            
            renderWorm() {
                // Render worm segments
                for (let i = this.worm.segments.length - 1; i >= 0; i--) {
                    const segment = this.worm.segments[i];
                    const isHead = i === 0;
                    
                    // Segment color
                    const intensity = isHead ? 1.0 : 0.8 - (i / this.worm.segments.length) * 0.3;
                    const red = Math.floor(74 * intensity);
                    const green = Math.floor(158 * intensity);
                    const blue = Math.floor(255 * intensity);
                    
                    this.ctx.fillStyle = `rgb(${red}, ${green}, ${blue})`;
                    
                    // Draw segment
                    this.ctx.beginPath();
                    const radius = isHead ? this.wormWidth : this.wormWidth * (0.8 - i * 0.03);
                    this.ctx.arc(segment.x, segment.y, radius, 0, Math.PI * 2);
                    this.ctx.fill();
                    
                    // Outline
                    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                    this.ctx.lineWidth = 1;
                    this.ctx.stroke();
                }
                
                // Head features (eyes)
                if (this.worm.segments.length > 0) {
                    const head = this.worm.segments[0];
                    const eyeOffset = 6;
                    
                    this.ctx.fillStyle = '#ffffff';
                    
                    const eyeAngle1 = head.angle + 0.5;
                    const eye1X = head.x + Math.cos(eyeAngle1) * eyeOffset;
                    const eye1Y = head.y + Math.sin(eyeAngle1) * eyeOffset;
                    this.ctx.beginPath();
                    this.ctx.arc(eye1X, eye1Y, 2, 0, Math.PI * 2);
                    this.ctx.fill();
                    
                    const eyeAngle2 = head.angle - 0.5;
                    const eye2X = head.x + Math.cos(eyeAngle2) * eyeOffset;
                    const eye2Y = head.y + Math.sin(eyeAngle2) * eyeOffset;
                    this.ctx.beginPath();
                    this.ctx.arc(eye2X, eye2Y, 2, 0, Math.PI * 2);
                    this.ctx.fill();
                }
            }
            
            renderTarget() {
                // Movement target
                this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                this.ctx.lineWidth = 2;
                this.ctx.setLineDash([5, 5]);
                this.ctx.beginPath();
                this.ctx.arc(this.worm.targetX, this.worm.targetY, 15, 0, Math.PI * 2);
                this.ctx.stroke();
                this.ctx.setLineDash([]);
            }
        }
        
        function startWormAnimation() {
            if (wormRenderer && !wormAnimationId) {
                function animate() {
                    wormRenderer.update();
                    wormRenderer.render();
                    wormAnimationId = requestAnimationFrame(animate);
                }
                animate();
            }
        }
        
        // Control functions
        function resetWormView() {
            if (wormRenderer) {
                wormRenderer.worm.x = wormRenderer.width / 2;
                wormRenderer.worm.y = wormRenderer.height / 2;
                wormRenderer.worm.targetX = wormRenderer.width / 2;
                wormRenderer.worm.targetY = wormRenderer.height / 2;
                wormRenderer.initWormSegments();
                logActivity('🔄 Worm view reset');
            }
        }
        
        function addFood() {
            if (wormRenderer) {
                wormRenderer.food.push({
                    x: Math.random() * (wormRenderer.width - 40) + 20,
                    y: Math.random() * (wormRenderer.height - 40) + 20,
                    size: 6 + Math.random() * 4,
                    eaten: false
                });
                wormRenderer.findNewFoodTarget();
                logActivity('🍎 Food added to environment');
            }
        }
        
        function toggleWormMovement() {
            wormPaused = !wormPaused;
            const btn = event.target;
            btn.textContent = wormPaused ? '▶️ Play' : '⏸️ Pause';
            logActivity(wormPaused ? '⏸️ Worm paused' : '▶️ Worm resumed');
        }

        // Initialize when page loads
        window.addEventListener('load', initDashboard);
    </script>
</body>
</html>
        """ 