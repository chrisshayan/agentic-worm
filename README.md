# Agentic Worm: AI-Driven Digital Organism

> **A sophisticated artificial life simulation combining OpenWorm's C. elegans neural modeling with advanced AI decision-making and intelligent memory systems**

[![OpenWorm](https://img.shields.io/badge/Bio-OpenWorm-orange.svg)](http://openworm.org)
[![ArangoDB](https://img.shields.io/badge/ArangoDB-DDE072?logo=arangodb&logoColor=000)](#)
[![Redis](https://img.shields.io/badge/Redis-%23DD0031.svg?logo=redis&logoColor=white)](#)
[![LangGraph](https://img.shields.io/badge/AI-LangGraph-purple.svg)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-1c3c3c.svg?logo=langchain&logoColor=white)](#)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=000)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white)](#)
[![Scikit-learn](https://img.shields.io/badge/-scikit--learn-%23F7931E?logo=scikit-learn&logoColor=white)](#)


##  🧬 **What is Agentic Worm?**

Agentic Worm is a **groundbreaking fusion of computational neuroscience and artificial intelligence**. It creates an autonomous digital organism that:

- **Uses real C. elegans neural data** from the OpenWorm project (302 neurons, complete connectome)
- **Makes intelligent decisions** using LangGraph-powered AI workflows  
- **Exhibits goal-directed behavior** like food seeking, exploration, and obstacle avoidance
- **Learns and adapts** with advanced memory systems (episodic, spatial, semantic, procedural)
- **Visualizes everything live** through an interactive web dashboard with memory overlays

**This isn't just a simulation—it's an intelligent digital life form that learns and remembers.**

---

## **Quick Start**

### **Option 1: Docker (Recommended)** 
```bash
# One-command setup with full memory system
git clone https://github.com/your-username/agentic-worm.git
cd agentic-worm
docker-compose up -d

# Access dashboards:
# - Main Dashboard: http://localhost:8000
# - ArangoDB: http://localhost:8529
```

### **Option 2: Instant Demo** 
```bash
# Quick 30-second demonstration
python3 quick_start.py

# Specific demo scenarios
./scripts/start_demo.sh food_seeking 60
./scripts/start_demo.sh obstacle_avoidance 45
./scripts/start_demo.sh learning 120
```

---

## **🎮 Demo Scenarios**

Choose your adventure with **pre-built intelligent behaviors**:

| Scenario | Description | AI Features | Memory Impact | Duration |
|----------|-------------|-------------|---------------|----------|
| **Food Seeking** | Worm hunts for bacteria using chemotaxis | Goal planning, spatial navigation | Learns successful food locations | 2 min |
| **Exploration** | Autonomous environment mapping | Spatial cognition, curiosity-driven behavior | Builds comprehensive spatial memory | 3 min |
| **Obstacle Navigation** | Complex maze solving with learning | Problem solving, path optimization | Develops navigation strategies | 4 min |
| **Neural Showcase** | Real-time 302-neuron activity visualization | Connectome analysis, firing patterns | Demonstrates neural-memory integration | 5 min |
| **Memory Learning** | Demonstrates adaptive behavior from experience | Pattern recognition, strategy optimization | Full memory system showcase | 120+ sec |
| **Custom Behavior** | Design your own worm intelligence | Configurable goals, interactive training | Personalized learning patterns | ∞ |

### **Running Demos**
```bash
# CLI interface
agentic-worm demo --type food_seeking --duration 120
agentic-worm quick exploration --duration 180

# Python interface  
python launch_demo.py

# Script shortcuts
./scripts/start_demo.sh memory_learning 300
```

---

## **Advanced Memory System**

The worm features a sophisticated multi-layered memory architecture:

### **Memory Types**
- **Episodic Memory**: Records every experience with location, actions, outcomes
- **Spatial Memory**: Remembers locations and their success rates  
- **Semantic Memory**: Extracts knowledge patterns from experiences
- **Procedural Memory**: Learns and stores behavioral strategies

### **Memory Features**
- **Real-time Learning**: Adapts behavior based on past experiences
- **Spatial Intelligence**: Builds environmental maps with success heatmaps
- **Strategy Evolution**: Develops and refines behavioral approaches
- **Pattern Recognition**: Identifies successful behavior patterns
- **Memory Consolidation**: Automatic knowledge extraction from experiences

### **Memory Dashboard**
The interactive dashboard provides memory visualization:
- **Live Memory Counts**: Episodic, spatial, semantic, procedural
- **Confidence Meter**: Overall memory system reliability
- **Success Rate**: Performance metrics over time
- **Insights Panel**: Current memory-derived behavioral insights
- **Memory Overlays**: Interactive spatial memory heatmaps

---

## **Live Dashboard Features**

### **Neural Activity Monitor**
- **302 C. elegans neurons** firing in real-time
- **Connectome visualization** with synaptic connections  
- **Membrane potential graphs** (-70mV to -50mV range)
- **Neurotransmitter activity** tracking

### **AI Decision Pipeline** 
- **Perception** → Sensory input processing
- **Memory** → Experience and pattern retrieval
- **Cognition** → Goal evaluation and planning
- **Decision** → Action selection with confidence
- **Motor** → Muscle activation commands
- **Learning** → Behavioral pattern adaptation

### **Performance Metrics**
- **Fitness score** tracking survival success
- **Energy levels** and metabolic state
- **Goal achievement** progress bars
- **Memory confidence** and learning indicators
- **Behavioral analysis** with pattern recognition

### **Interactive Controls**
- **Switch scenarios** on-the-fly
- **Adjust AI parameters** in real-time
- **Set new goals** and watch adaptation
- **Toggle memory overlays** for spatial visualization
- **Pause/resume** simulation with detailed inspection

---

## **Memory System Setup**

### **Docker Setup (Recommended)**
The Docker configuration automatically includes:
- **ArangoDB** for persistent memory storage
- **Redis** for fast memory caching
- **Embedding models** for semantic search
- **WebSocket** real-time memory updates

### **Manual Local Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Install ArangoDB (macOS)
brew install arangodb

# Install ArangoDB (Ubuntu/Debian)  
curl -OL https://download.arangodb.com/arangodb311/DEBIAN/Release.key
sudo apt-key add - < Release.key
sudo apt-add-repository 'deb https://download.arangodb.com/arangodb311/DEBIAN/ /'
sudo apt-get update
sudo apt-get install arangodb3

# Start ArangoDB
sudo systemctl start arangodb3

# Configure environment
cat > .env << EOF
ARANGO_HOST=localhost
ARANGO_PORT=8529
ARANGO_DATABASE=agentic_worm_memory
ARANGO_USERNAME=root
ARANGO_PASSWORD=
EOF
```

### **Memory Configuration**
```python
memory_manager = WormMemoryManager(
    arango_config={
        "host": "localhost", 
        "port": 8529,
        "database_name": "agentic_worm_memory"
    },
    enable_consolidation=True,
    consolidation_interval_hours=24
)
```

---

## **Architecture**

### **Core Technologies**
- **Orchestration**: LangGraph + LangChain for AI workflows
- **AI/ML**: PyTorch, sentence-transformers for embeddings
- **Biology**: OpenWorm (c302, Sibernetic) for neural simulation
- **Storage**: ArangoDB for persistent memory, Redis for caching
- **Web**: FastAPI backend, WebSocket real-time updates
- **Visualization**: Interactive dashboard with memory overlays

### **AI Intelligence Pipeline**
1. **Perception Processing**: Environmental sensor data analysis
2. **Memory Retrieval**: Relevant experience and pattern lookup
3. **Cognitive Reasoning**: Goal evaluation and strategy selection
4. **Motor Planning**: Action sequence generation  
5. **Adaptive Learning**: Experience recording and pattern extraction

### **Memory Architecture**
- **Experience Recording**: Every action-outcome pair stored with context
- **Spatial Mapping**: Location-based success rate tracking
- **Pattern Extraction**: Automated knowledge fact generation
- **Strategy Learning**: Behavioral approach optimization
- **Memory Consolidation**: Background pattern analysis

---

## **🔍 Troubleshooting**

### **Common Issues**

**Memory showing 0 values**
```bash
# Check ArangoDB connection
curl http://localhost:8529/_api/version

# Restart ArangoDB
docker-compose restart arangodb

# Verify memory data generation
docker-compose logs -f agentic-worm | grep memory
```

**Docker container unhealthy**
```bash
# Check container status
docker-compose ps

# Restart all services
docker-compose restart

# Rebuild if needed
docker-compose up --build -d
```

**Dashboard not updating**
```bash
# Check WebSocket connection in browser console
# Restart application
docker-compose restart agentic-worm

# Refresh dashboard (Ctrl+R)
```

**Performance issues**
```bash
# Increase Docker memory limit to 8GB minimum
# Reduce memory consolidation frequency
# Use smaller embedding models
```

---

## **📚 API Reference**

### **Memory Manager Methods**
```python
# Record new experience
await memory_manager.record_experience(worm_id, location, actions, outcome)

# Retrieve relevant memories  
memories = await memory_manager.retrieve_relevant_memories(
    worm_id, location, goal, context, memory_types, limit=10
)

# Get spatial context
spatial_context = await memory_manager.get_spatial_context(
    worm_id, location, radius=50.0
)

# Find best strategies
strategies = await memory_manager.get_best_strategies_for_goal(
    worm_id, goal, context, limit=3
)
```

### **WebSocket Memory Data**
```json
{
  "memory_stats": {
    "episodic_count": 150,
    "spatial_count": 45, 
    "semantic_count": 12,
    "strategies_count": 8,
    "memory_confidence": 0.75,
    "success_rate": 0.68,
    "locations_visited": 45,
    "insights": ["familiar_area", "proven_strategy", "success_pattern"]
  }
}
```

---

## **🎓 Educational Value**

Perfect for demonstrating:

### **Computational Neuroscience**
- How 302 neurons create complex behavior
- Neural network simulation and analysis
- Connectome-based modeling approaches
- Memory-guided neural dynamics

### **Artificial Intelligence**
- Multi-agent reasoning systems
- Goal-oriented AI behavior
- Memory-enhanced decision making
- Real-time adaptive learning

### **Digital Biology**
- Emergent behavior from simple rules
- Evolution and adaptation in silico
- Bio-inspired memory architectures
- Synthetic life and artificial organisms

---

## **📁 Project Structure**
```
 src/agentic_worm/
├── intelligence/workflow.py    # LangGraph AI pipeline with memory integration
├── memory/manager.py          # Advanced memory system  
├── core/state.py              # Worm state with memory context
├── visualization/dashboard.py  # Live dashboard with memory overlays
└── integration/openworm.py    # OpenWorm interface

 Root Directory:
├── quick_start.py             # One-click demo launcher
├── launch_demo.py             # Interactive demo scenarios  
├── docker-compose.yml         # Full stack with memory services
├── requirements.txt           # Python dependencies
└── scripts/setup.sh          # Environment setup
```

---

## **🔬 Scientific References**
- [OpenWorm: open-science approach to modeling C. elegans](https://www.frontiersin.org/articles/10.3389/fncom.2014.00137/full) - *Frontiers in Computational Neuroscience*
- [C. elegans Connectome Database](https://www.wormatlas.org/neuronalindex.html)
- [LangGraph Framework Documentation](https://langchain-ai.github.io/langgraph/)
- [Memory Systems in Artificial Intelligence](https://www.nature.com/articles/s41586-019-1763-9)

---

## **🚀 Next Steps**

1. **🎮 Run Demos**: Try different scenarios to see memory-guided behavior
2. **🧠 Monitor Learning**: Watch how strategies evolve over time
3. **🔍 Explore Memory**: Use ArangoDB interface to analyze memory patterns
4. **⚙️ Tune Parameters**: Adjust learning rates and memory consolidation
5. **🌟 Contribute**: Add new behaviors, memory types, or analysis tools

---

**The future of digital biology is here - an intelligent, learning, remembering artificial organism! 🧬🤖**
