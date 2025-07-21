# 🧠 Agentic Worm Memory System Setup Guide

## Overview

This guide will help you set up the complete **memory-enabled agentic worm system** with:

- 🧠 **Episodic Memory**: Records experiences and learns from them
- 🗺️ **Spatial Memory**: Remembers locations and their success rates
- 💡 **Semantic Memory**: Extracts knowledge facts from experiences
- 🎯 **Procedural Memory**: Learns and stores behavioral strategies
- 📊 **Real-time Memory Visualization**: Interactive dashboard with memory overlays

## Quick Start (Docker - Recommended)

### 1. Prerequisites
- Docker and Docker Compose installed
- 8GB RAM minimum (for ArangoDB and embeddings)
- Python 3.11+ (if running locally)

### 2. Start the System
```bash
# Clone and start all services
git clone <repository-url>
cd agentic-worm

# Start ArangoDB, Redis, and the application
docker-compose up -d

# View logs
docker-compose logs -f agentic-worm
```

### 3. Access the Dashboard
- **Agentic Worm Dashboard**: http://localhost:8000
- **ArangoDB Web Interface**: http://localhost:8529
- **Memory Statistics**: Visible in the dashboard's Memory System widget

## Manual Setup (Local Development)

### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install ArangoDB (macOS)
brew install arangodb

# Install ArangoDB (Ubuntu/Debian)
curl -OL https://download.arangodb.com/arangodb311/DEBIAN/Release.key
sudo apt-key add - < Release.key
sudo apt-add-repository 'deb https://download.arangodb.com/arangodb311/DEBIAN/ /'
sudo apt-get update
sudo apt-get install arangodb3
```

### 2. Start ArangoDB
```bash
# Start ArangoDB service
sudo systemctl start arangodb3

# Or run directly
arangod --server.endpoint tcp://0.0.0.0:8529
```

### 3. Configure Environment
```bash
# Create .env file
cat > .env << EOF
ARANGO_HOST=localhost
ARANGO_PORT=8529
ARANGO_DATABASE=agentic_worm_memory
ARANGO_USERNAME=root
ARANGO_PASSWORD=
REDIS_HOST=localhost
REDIS_PORT=6379
PYTHON_ENV=development
EOF
```

### 4. Launch the Application
```bash
python launch_demo.py
```

## Memory System Features

### 🧠 Episodic Memory
Records every worm experience with:
- **Location**: Where the experience occurred
- **Actions**: What the worm did (motor commands, decisions)
- **Outcome**: Success/failure/partial
- **Context**: Environment state, goal, fitness changes
- **Embeddings**: Semantic search capability

### 🗺️ Spatial Memory
Tracks location-based information:
- **Success Rates**: How successful each location has been
- **Visit Counts**: How often locations are visited
- **Environmental Data**: Temperature, chemical gradients
- **Region Types**: food_rich, obstacle, neutral zones

### 💡 Semantic Memory (Knowledge Facts)
Automatically extracts patterns:
- **Location Success Patterns**: "Location X has 85% success rate for food finding"
- **Behavioral Insights**: "Strategy Y works best in environment Z"
- **Confidence Scores**: How reliable each fact is

### 🎯 Procedural Memory (Strategies)
Learns behavioral strategies:
- **Trigger Conditions**: When to use each strategy
- **Action Sequences**: What steps to take
- **Performance Tracking**: Success rates and contexts
- **Adaptive Learning**: Strategies improve over time

## Dashboard Memory Features

### Memory System Widget
- **Live Memory Counts**: Episodic, spatial, semantic, procedural
- **Confidence Meter**: Overall memory system confidence
- **Success Rate**: Recent performance metrics
- **Insights Panel**: Current memory-derived insights

### Interactive Memory Overlays
Click the memory overlay buttons to visualize:

1. **🗺️ Spatial Memory**: 
   - Success rate heatmaps
   - Location visit frequencies
   - Region type classifications

2. **📚 Experiences**: 
   - Recent experience locations
   - Success/failure patterns
   - Experience density maps

3. **🎯 Strategies**: 
   - Strategy effectiveness zones
   - Trigger condition mappings
   - Performance indicators

4. **💡 Knowledge**: 
   - Knowledge fact networks
   - Confidence relationships
   - Semantic connections

## Memory Consolidation

The system automatically runs memory consolidation:

- **Frequency**: Every 24 hours (configurable)
- **Process**: Analyzes recent experiences to extract patterns
- **Output**: New knowledge facts and updated strategies
- **Background**: Runs without interrupting the main simulation

## Advanced Configuration

### Memory Manager Settings
```python
memory_manager = WormMemoryManager(
    arango_config={
        "host": "localhost",
        "port": 8529,
        "database_name": "agentic_worm_memory",
        "username": "root",
        "password": ""
    },
    enable_consolidation=True,
    consolidation_interval_hours=24  # Adjust as needed
)
```

### Embedding Model Configuration
```python
# Change the embedding model for semantic search
embedding_model="all-MiniLM-L6-v2"  # Fast, good quality
# embedding_model="sentence-transformers/all-mpnet-base-v2"  # Higher quality
```

### Memory Query Examples
```python
# Find relevant memories for current context
memories = await memory_manager.retrieve_relevant_memories(
    worm_id="worm_001",
    current_location={"x": 100, "y": 150, "z": 0},
    current_goal="find_food",
    context="low_energy_state",
    memory_types=[MemoryType.EPISODIC, MemoryType.SPATIAL],
    limit=10
)

# Get spatial context for decision making
spatial_context = await memory_manager.get_spatial_context(
    worm_id="worm_001",
    location={"x": 100, "y": 150, "z": 0},
    radius=50.0
)

# Find best strategies for current goal
strategies = await memory_manager.get_best_strategies_for_goal(
    worm_id="worm_001",
    goal="find_food",
    context={"energy": 0.3, "fitness": 0.7},
    limit=3
)
```

## Database Schema

### ArangoDB Collections
- **experiences**: Episodic memories with embeddings
- **spatial_memories**: Location-based data with geo-indexing
- **knowledge_facts**: Extracted patterns and insights
- **strategies**: Learned behavioral procedures
- **experience_knowledge_edges**: Links experiences to knowledge
- **strategy_experience_edges**: Links strategies to outcomes

### Indexes
- **Geo-spatial**: For location-based queries
- **Hash**: For worm_id and type filtering
- **Skiplist**: For temporal and confidence queries
- **Fulltext**: For content search

## Monitoring and Debugging

### Dashboard Insights
Monitor memory system health via:
- Memory confidence scores
- Recent success rates
- Knowledge fact growth
- Strategy effectiveness

### ArangoDB Web Interface
Access http://localhost:8529 to:
- Browse memory collections
- Execute AQL queries
- Monitor database performance
- Visualize memory graphs

### Log Monitoring
```bash
# View memory system logs
tail -f logs/memory.log

# Docker logs
docker-compose logs -f agentic-worm
```

## Troubleshooting

### Common Issues

1. **ArangoDB Connection Failed**
   ```bash
   # Check if ArangoDB is running
   curl http://localhost:8529/_api/version
   
   # Restart ArangoDB
   docker-compose restart arangodb
   ```

2. **Memory Updates Not Showing**
   - Check WebSocket connection in browser console
   - Verify memory data is being generated in logs
   - Refresh dashboard (Ctrl+R)

3. **Embedding Model Loading Fails**
   ```bash
   # Install sentence transformers manually
   pip install sentence-transformers
   
   # Try a smaller model
   embedding_model="all-MiniLM-L6-v2"
   ```

4. **Docker Out of Memory**
   ```bash
   # Increase Docker memory limit to 8GB
   # Or run without Docker using local setup
   ```

### Performance Optimization

1. **Memory Consolidation**
   - Increase interval for less frequent consolidation
   - Reduce experience retention period
   - Limit memory query results

2. **Database Performance**
   - Monitor ArangoDB memory usage
   - Optimize query patterns
   - Use appropriate indexes

3. **Embedding Performance**
   - Use smaller embedding models
   - Cache embeddings in Redis
   - Batch embedding generation

## API Reference

### Memory Manager Methods
- `record_experience()`: Store new episodic memory
- `retrieve_relevant_memories()`: Query memories by context
- `get_spatial_context()`: Analyze location-based data
- `get_best_strategies_for_goal()`: Find optimal strategies
- `consolidate_memories()`: Extract patterns and knowledge

### WebSocket Memory Data
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
    "insights": [
      "familiar_successful_area",
      "proven_strategy_available",
      "recent_success_pattern"
    ]
  }
}
```

## Next Steps

1. **Experiment with Goals**: Try different behavioral goals to see how memory affects decision-making
2. **Monitor Learning**: Watch how strategies and knowledge evolve over time
3. **Analyze Patterns**: Use the ArangoDB interface to explore memory relationships
4. **Tune Parameters**: Adjust consolidation intervals and confidence thresholds
5. **Scale Up**: Add multiple worms to test multi-agent memory interactions

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Test with minimal configuration first
4. Verify all dependencies are installed correctly

The memory system transforms the agentic worm from a reactive system into a truly learning, adaptive agent that gets smarter over time! 🧠✨ 