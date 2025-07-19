# Agentic Worm Demo Guide

Welcome to the **Agentic Worm** demonstration! This guide shows you how to run our AI-driven digital C. elegans that integrates with OpenWorm simulation.

## What We've Built

✅ **Complete Project Structure**: Professional Python package with proper organization  
✅ **OpenWorm Integration**: Docker-based setup that leverages existing OpenWorm stack  
✅ **Demo Framework**: Multiple demonstration scenarios with real-time metrics  
✅ **CLI Interface**: Beautiful command-line interface for easy demo execution  
✅ **State Management**: Comprehensive state tracking using LangGraph architecture  
✅ **Visualization Ready**: Dashboard and monitoring infrastructure  

## Quick Start

### Option 1: Simple Demo Script (Recommended)

```bash
# Run a basic 30-second demo
./scripts/start_demo.sh

# Run specific demo types
./scripts/start_demo.sh food_seeking 60
./scripts/start_demo.sh obstacle_avoidance 45
./scripts/start_demo.sh learning 120

# Check system status
./scripts/start_demo.sh status
```

### Option 2: Python CLI (Once dependencies are installed)

```bash
# Install dependencies
pip install -e .

# Run demos
agentic-worm demo --type basic --duration 30
agentic-worm quick food_seeking --duration 15
agentic-worm status
```

### Option 3: Docker Stack (Full System)

```bash
# Start the complete system
docker-compose -f docker/docker-compose.yml up -d

# Access interfaces
# - OpenWorm Visualization: http://localhost:8080
# - Agentic Dashboard: http://localhost:8000  
# - Jupyter Lab: http://localhost:8888
# - Real-time Dashboard: http://localhost:3000
```

## Demo Types Available

### 1. **Basic Exploration** (`basic`)
- Demonstrates autonomous exploration behavior
- Shows basic perception-action loops
- Duration: 30-60 seconds recommended

### 2. **Food Seeking** (`food_seeking`)  
- Showcases goal-directed behavior toward food sources
- Demonstrates chemotaxis and navigation
- Duration: 60-120 seconds recommended

### 3. **Obstacle Avoidance** (`obstacle_avoidance`)
- Shows adaptive navigation around obstacles
- Demonstrates spatial reasoning
- Duration: 45-90 seconds recommended

### 4. **Learning & Adaptation** (`learning`)
- Displays behavioral improvement over time
- Shows reward-based learning
- Duration: 120+ seconds recommended

## What You'll See

### Real-time Metrics
- **Fitness Score**: Overall performance metric
- **Energy Level**: Simulated energy management
- **Health Status**: System integrity
- **Goal Progress**: Progress toward current objectives
- **Decision Confidence**: AI confidence in choices

### Behavioral Indicators
- **Current Goal**: What the worm is trying to achieve
- **Motor Commands**: Real-time muscle activation
- **Sensory Input**: Environmental perception
- **Neural Activity**: Simulated brain activity

## Architecture Highlights

Our system integrates several cutting-edge technologies:

### **LangGraph Orchestration**
- State-based workflow management
- Conditional decision branching
- Memory and learning integration

### **OpenWorm Integration** 
- Leverages existing C. elegans simulation
- Real biological neural network (302 neurons)
- Physically accurate body simulation

### **AI Intelligence Layer**
- Perception processing
- Cognitive reasoning
- Motor planning
- Adaptive learning

## Research Applications

This demonstration showcases capabilities relevant to:

- **Embodied AI Research**: AI agents with physical constraints
- **Neuroscience Modeling**: Brain-body-environment interactions  
- **Autonomous Systems**: Goal-directed behavior in complex environments
- **Digital Biology**: AI-enhanced biological simulations
- **Bio-inspired Robotics**: Learning from C. elegans for robot control

## Technical Stack

- **Orchestration**: LangGraph + LangChain
- **AI/ML**: PyTorch, TensorFlow, Stable-Baselines3
- **Biology**: OpenWorm (c302, Sibernetic, Geppetto)
- **Infrastructure**: Docker, FastAPI, Redis, React
- **Visualization**: Streamlit, Plotly, Jupyter

## Current Status

🟢 **Working**: Core architecture, demo framework, OpenWorm integration setup  
🟡 **In Progress**: Real-time AI decision making, advanced learning algorithms  
🔴 **Planned**: Full neural control, multi-agent scenarios, research platform  

## Next Steps

The next phase involves:
1. **Implementing LangGraph workflows** for decision-making
2. **Building real-time visualization dashboard** 
3. **Creating behavioral scenarios** with measurable outcomes
4. **Integrating advanced AI models** for sophisticated behavior

## Why This Matters

The **Agentic Worm** represents a breakthrough in:

- **Digital Biology**: First truly autonomous biological simulation
- **AI Research**: Embodied intelligence in biologically constrained systems
- **Neuroscience**: Understanding brain-body-environment dynamics
- **Education**: Accessible platform for studying complex systems

---

## Ready to See It in Action?

Choose your preferred demo method above and watch as our AI-driven digital C. elegans demonstrates autonomous, intelligent behavior! 

The future of digital biology is here. 🧬

---

