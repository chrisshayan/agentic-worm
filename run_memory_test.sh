#!/bin/bash

echo "🧠 Running Memory System Test Inside Docker Container"
echo "===================================================="

# Copy the test script to the container and run it
docker-compose exec agentic-worm python /app/final_memory_fix.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Memory test completed successfully!"
    echo "🎯 The dashboard should now show real memory values"
    echo "🔗 Check ArangoDB collections at http://localhost:8529"
    echo "🌐 Check dashboard at http://localhost:8000"
else
    echo ""
    echo "❌ Memory test failed"
    echo "📋 Checking recent logs for errors..."
    echo ""
    docker-compose logs --tail=20 agentic-worm | grep -E "(Error|Failed|Exception|memory|Memory)"
fi

echo ""
echo "📊 Current container status:"
docker-compose ps agentic-worm 