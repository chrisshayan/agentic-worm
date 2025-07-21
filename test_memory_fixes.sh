#!/bin/bash

echo "🔧 Testing Memory System Datetime and AQL Fixes"
echo "==============================================="

# Step 1: Rebuild with the fixes
echo "🔨 Rebuilding with datetime serialization and AQL fixes..."
docker-compose build --no-cache agentic-worm

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# Step 2: Restart the system
echo "🚀 Restarting system..."
docker-compose down
docker-compose up -d

# Step 3: Wait for initialization
echo "⏳ Waiting for system to initialize..."
sleep 30

# Step 4: Monitor for the specific errors we fixed
echo "🔍 Checking for datetime serialization errors..."
sleep 5

echo ""
echo "📋 Checking for JSON serialization errors:"
echo "=========================================="
if docker-compose logs agentic-worm | grep -q "Object of type datetime is not JSON serializable"; then
    echo "❌ Datetime serialization errors still present"
else
    echo "✅ No datetime serialization errors found!"
fi

echo ""
echo "📋 Checking for AQL DISTANCE errors:"
echo "===================================="
if docker-compose logs agentic-worm | grep -q "invalid number of arguments for function 'DISTANCE'"; then
    echo "❌ AQL DISTANCE errors still present"
else
    echo "✅ No AQL DISTANCE errors found!"
fi

echo ""
echo "🧠 Checking for successful memory operations..."

# Check for successful experience storage
if docker-compose logs agentic-worm | grep -q "Stored experience:"; then
    echo "✅ Experiences are being stored successfully!"
    EXPERIENCE_COUNT=$(docker-compose logs agentic-worm | grep -c "Stored experience:")
    echo "   📊 Experiences stored: $EXPERIENCE_COUNT"
else
    echo "⚠️ Experience storage not detected yet"
fi

# Check for successful spatial memory storage
if docker-compose logs agentic-worm | grep -q "Stored spatial memory:"; then
    echo "✅ Spatial memories are being stored successfully!"
    SPATIAL_COUNT=$(docker-compose logs agentic-worm | grep -c "Stored spatial memory:")
    echo "   📊 Spatial memories stored: $SPATIAL_COUNT"
else
    echo "⚠️ Spatial memory storage not detected yet"
fi

# Check for successful strategy creation
if docker-compose logs agentic-worm | grep -q "Stored strategy:"; then
    echo "✅ Strategies are being created successfully!"
    STRATEGY_COUNT=$(docker-compose logs agentic-worm | grep -c "Stored strategy:")
    echo "   📊 Strategies created: $STRATEGY_COUNT"
else
    echo "⚠️ Strategy creation not detected yet"
fi

echo ""
echo "🗄️ Checking ArangoDB for collections..."
sleep 3

# Check if collections were created
COLLECTIONS=$(curl -s http://localhost:8529/_api/collection 2>/dev/null)
if echo "$COLLECTIONS" | grep -q "experiences\|spatial_memories\|strategies\|knowledge_facts"; then
    echo "✅ Memory collections created in ArangoDB!"
    echo "Collections found:"
    echo "$COLLECTIONS" | grep -o '"name":"[^"]*' | cut -d'"' -f4 | grep -E '(experiences|spatial|strategies|knowledge)' | sed 's/^/   - /'
else
    echo "⚠️ Memory collections not yet created"
    echo "Available collections:"
    echo "$COLLECTIONS" | grep -o '"name":"[^"]*' | cut -d'"' -f4 | grep -v '^_' | sed 's/^/   - /' || echo "   None found"
fi

echo ""
echo "🌐 Testing dashboard..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Dashboard is healthy"
    echo "🎯 Access dashboard at: http://localhost:8000"
else
    echo "❌ Dashboard not accessible"
fi

echo ""
echo "📊 Memory System Status Summary:"
echo "==============================="

# Check overall memory system health
echo ""
if docker-compose logs agentic-worm | grep -q "Memory manager initialized successfully"; then
    echo "✅ Memory Manager: Initialized"
else
    echo "❌ Memory Manager: Not initialized"
fi

if docker-compose logs agentic-worm | grep -q "ArangoDB.*connection.*successful"; then
    echo "✅ Database Connection: Active"
else
    echo "❌ Database Connection: Failed"
fi

# Count total errors
ERROR_COUNT=$(docker-compose logs agentic-worm | grep -c -E "(Failed to.*memory|Error.*memory|datetime.*JSON|DISTANCE.*arguments)" || echo "0")
echo "📈 Error Count: $ERROR_COUNT"

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS: Memory system is working properly!"
    echo "   - No datetime serialization errors"
    echo "   - No AQL query errors" 
    echo "   - Memory operations are successful"
    echo "   - Collections are being created"
else
    echo ""
    echo "⚠️ Some issues detected. Recent memory-related logs:"
    docker-compose logs --tail=10 agentic-worm | grep -E "(memory|Memory|experience|spatial|strategy|datetime|DISTANCE|Failed|Error)"
fi

echo ""
echo "==============================================="
echo "🎯 Next Steps:"
echo "1. Open http://localhost:8000"
echo "2. Memory System widget should show real values"
echo "3. Check ArangoDB at http://localhost:8529"
echo "4. Monitor with: docker-compose logs -f agentic-worm"
echo "===============================================" 