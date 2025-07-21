#!/bin/bash

echo "🧠 Quick Fix for Memory System Connection Issues"
echo "=============================================="

# Step 1: Stop current containers
echo "🛑 Stopping current containers..."
docker-compose down --remove-orphans -v

# Step 2: Check ArangoDB configuration
echo ""
echo "🔍 Checking Docker configuration..."
echo "ArangoDB Auth Mode: No Authentication (ARANGO_NO_AUTH=1)"
echo "Expected Database: agentic_worm_memory"
echo "Connection: arangodb:8529 (internal Docker network)"

# Step 3: Build and start with verbose logging
echo ""
echo "🔨 Building with fresh containers..."
docker-compose build --no-cache agentic-worm

echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Step 4: Wait for ArangoDB to be ready
echo ""
echo "⏳ Waiting for ArangoDB to initialize..."
sleep 15

# Check ArangoDB health
if curl -s http://localhost:8529/_admin/echo > /dev/null; then
    echo "✅ ArangoDB is responding"
else
    echo "❌ ArangoDB not responding"
    echo "📋 ArangoDB logs:"
    docker-compose logs arangodb
    exit 1
fi

# Step 5: Wait for application to initialize
echo ""
echo "⏳ Waiting for application to connect to ArangoDB..."
sleep 10

# Step 6: Check application logs for connection success
echo ""
echo "🔍 Checking for memory system initialization..."

# Look for specific success indicators
echo "Looking for connection logs..."
if docker-compose logs agentic-worm | grep -i "ArangoDB connection established"; then
    echo "✅ ArangoDB connection successful"
else
    echo "⚠️ ArangoDB connection not found, checking detailed logs..."
fi

if docker-compose logs agentic-worm | grep -i "Memory manager initialized successfully"; then
    echo "✅ Memory manager initialized"
else
    echo "⚠️ Memory manager initialization failed"
fi

# Step 7: Check for database creation
echo ""
echo "🗄️ Checking ArangoDB databases..."
DB_LIST=$(curl -s http://localhost:8529/_api/database)
if echo "$DB_LIST" | grep -q "agentic_worm_memory"; then
    echo "✅ Database 'agentic_worm_memory' exists"
else
    echo "⚠️ Database 'agentic_worm_memory' not found"
    echo "Available databases: $DB_LIST"
fi

# Step 8: Test dashboard
echo ""
echo "🌐 Testing dashboard accessibility..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Dashboard is healthy"
    echo "🎯 Dashboard URL: http://localhost:8000"
else
    echo "❌ Dashboard health check failed"
fi

# Step 9: Show current logs with focus on memory system
echo ""
echo "📋 Recent Application Logs (last 30 lines):"
echo "=============================================="
docker-compose logs --tail=30 agentic-worm | grep -E "(Memory|ArangoDB|Error|Warning|memory_system|database|connection)"

echo ""
echo "=============================================="
echo "🔧 Troubleshooting Commands:"
echo ""
echo "View all logs:           docker-compose logs agentic-worm"
echo "Follow logs live:        docker-compose logs -f agentic-worm"
echo "Check ArangoDB:          curl http://localhost:8529/_admin/echo"
echo "Check dashboard:         curl http://localhost:8000/health"
echo "Restart everything:      docker-compose restart"
echo ""
echo "🎯 Expected Behavior:"
echo "1. ArangoDB connection should be established"
echo "2. Memory manager should initialize successfully"
echo "3. Database 'agentic_worm_memory' should be created"
echo "4. Memory System widget should show activity (not stuck on 'Initializing...')"
echo "==============================================" 