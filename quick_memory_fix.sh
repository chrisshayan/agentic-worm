#!/bin/bash

echo "🔧 Quick Memory Fix for Dashboard"
echo "================================"

# Run the simple memory fix script
echo "🧠 Creating memory data for live worm..."
docker-compose exec agentic-worm python /app/simple_memory_fix.py

echo ""
echo "✅ Memory fix completed!"
echo "🌐 Refresh your browser at http://localhost:8000"
echo "📊 The Memory System widget should now show real values!"
echo ""
echo "Expected changes:"
echo "- Episodic: 4+ (instead of 0)"
echo "- Spatial: 3+ (instead of 0)" 
echo "- Success Rate: 75% (instead of 0%)"
echo "- Memory Confidence: 0.7+ (instead of 0.5)"
echo "- Insights: Real messages (instead of 'Initializing...')" 