#!/bin/bash

echo "🔍 Running Memory Statistics Debug"
echo "=================================="

# Copy debug script to container and run it
docker-compose exec agentic-worm python /app/debug_memory_stats.py

echo ""
echo "Debug completed." 