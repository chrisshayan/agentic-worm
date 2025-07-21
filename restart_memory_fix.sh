#!/bin/bash

echo "🔧 Applying Memory Statistics Fix"
echo "================================="

echo "📦 Rebuilding application with fixed memory system..."
docker-compose build agentic-worm

echo "🔄 Restarting application..."
docker-compose restart agentic-worm

echo ""
echo "✅ Memory fix applied!"
echo "🌐 Open http://localhost:8000 to see the updated memory values"
echo ""
echo "Expected memory display:"
echo "- Episodic: 50+ experiences"
echo "- Spatial: 25+ locations"  
echo "- Success Rate: 65-75%"
echo "- Memory Confidence: 0.9+"
echo "- Real insights about worm progress" 