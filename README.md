# Agentic Worm: AI-Driven Digital Organism

> **A sophisticated artificial life simulation combining OpenWorm's C. elegans neural modeling with advanced AI decision-making**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/AI-LangGraph-purple.svg)](https://github.com/langchain-ai/langgraph)
[![OpenWorm](https://img.shields.io/badge/Bio-OpenWorm-orange.svg)](http://openworm.org)

## **What is Agentic Worm?**

Agentic Worm is a **groundbreaking fusion of computational neuroscience and artificial intelligence**. It creates an autonomous digital organism that:

- 🧬 **Uses real C. elegans neural data** from the OpenWorm project (302 neurons, complete connectome)
- **Makes intelligent decisions** using LangGraph-powered AI workflows  
- **Exhibits goal-directed behavior** like food seeking, exploration, and obstacle avoidance
- **Learns and adapts** in real-time with behavioral pattern analysis
- **Visualizes everything live** through an interactive web dashboard

**This isn't just a simulation—it's an intelligent digital life form.**

---

## **Quick Start (One-Click Demo)**

### **Option 1: Instant Demo** ⚡
```bash
# Clone and run in 30 seconds
git clone https://github.com/your-username/agentic-worm.git
cd agentic-worm
python3 quick_start.py
```

### **Option 2: Full Installation** 🔧
```bash
# Complete setup with all features
./scripts/setup.sh
python3 launch_demo.py
```

### **Option 3: Docker (Bulletproof)** 🐳
```bash
# Zero-dependency Docker setup
docker-compose up --build
# Open http://localhost:8080 for live dashboard
```

---

## **Demo Scenarios**

Choose your adventure with our **pre-built intelligent behaviors**:

| Scenario | Description | AI Features | Duration |
|----------|-------------|-------------|----------|
| 🍔 **Food Seeking** | Worm hunts for bacteria using chemotaxis | Goal planning, memory formation | 2 min |
| 🗺️ **Exploration** | Autonomous environment mapping | Spatial cognition, curiosity-driven | 3 min |
| 🚧 **Obstacle Navigation** | Complex maze solving with learning | Problem solving, path optimization | 4 min |
| 🧠 **Neural Showcase** | Real-time 302-neuron activity visualization | Connectome analysis, firing patterns | 5 min |
| 🎯 **Custom Behavior** | Design your own worm intelligence | Configurable goals, interactive training | ∞ |

---

## **Live Dashboard Features**

Our **real-time web interface** shows everything happening inside the worm's "mind":

### **Neural Activity Monitor**
- **302 C. elegans neurons** firing in real-time
- **Connectome visualization** with synaptic connections  
- **Membrane potential graphs** (-70mV to -50mV range)
- **Neurotransmitter activity** tracking

### **AI Decision Pipeline** 
- **Perception** → Sensory input processing
- **Cognition** → Goal evaluation and planning
- **Decision** → Action selection with confidence
- **Motor** → Muscle activation commands
- **Learning** → Behavioral pattern adaptation

### **Performance Metrics**
- **Fitness score** tracking survival success
- **Energy levels** and metabolic state
- **Goal achievement** progress bars
- **Behavioral analysis** with pattern recognition

### **Interactive Controls**
- **Switch scenarios** on-the-fly
- **Adjust AI parameters** in real-time
- **Set new goals** and watch adaptation
- **Pause/resume** simulation with detailed inspection

---

## **Educational Value**

Perfect for demonstrating:

### **Computational Neuroscience**
- How 302 neurons create complex behavior
- Neural network simulation and analysis
- Connectome-based modeling approaches
- Biophysically realistic neural dynamics

### **Artificial Intelligence**
- Multi-agent reasoning systems
- Goal-oriented AI behavior
- Reinforcement learning in biological contexts
- Real-time decision making under uncertainty

### 🧬 **Digital Biology**
- Emergent behavior from simple rules
- Evolution and adaptation in silico
- Biomimetic AI architectures
- Synthetic life and artificial organisms

### **Documentation & Project Structure**
- **Installation**: See [Quick Start](#-quick-start) section above
- **API Reference**: Explore `src/agentic_worm/` for core modules and interfaces
- **Architecture**: LangGraph workflow in `src/agentic_worm/intelligence/workflow.py`
- **Custom Behaviors**: Modify demo scenarios in `launch_demo.py`

### **Key Files**
```
 src/agentic_worm/
├── intelligence/workflow.py    # Real LangGraph AI pipeline
├── core/state.py              # Worm state management
├── visualization/dashboard.py  # Live web dashboard
└── integration/openworm.py    # OpenWorm interface

 Root Directory:
├── quick_start.py             # One-click demo launcher
├── launch_demo.py             # Interactive demo scenarios
├── requirements.txt           # Python dependencies
└── scripts/setup.sh          # Environment setup
```

### **Scientific References**
- [OpenWorm: open-science approach to modeling C. elegans](https://www.frontiersin.org/articles/10.3389/fncom.2014.00137/full) - *Frontiers in Computational Neuroscience*
- [C. elegans Connectome Database](https://www.wormatlas.org/neuronalindex.html)
- [LangGraph Framework Documentation](https://langchain-ai.github.io/langgraph/)

---

[⬆️ Back to Top](#-agentic-worm-ai-driven-digital-organism)
