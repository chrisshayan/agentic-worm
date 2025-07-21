#!/bin/bash

echo "🔧 Applying Memory System Validation Fixes"
echo "==========================================="

# Step 1: Rebuild with the fixes
echo "🔨 Rebuilding container with validation fixes..."
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
sleep 25

# Step 4: Monitor for validation errors
echo "🔍 Checking for validation errors..."
sleep 5

echo ""
echo "📋 Recent logs (checking for validation errors):"
echo "================================================"
docker-compose logs --tail=20 agentic-worm | grep -E "(validation|error|Error|Failed|Memory|Experience|goal|tags)" || echo "No validation errors found in recent logs!"

echo ""
echo "🧠 Checking for memory system success indicators..."

# Check for successful experience recording
if docker-compose logs agentic-worm | grep -q "Experience.*recorded"; then
    echo "✅ Experiences are being recorded successfully!"
else
    echo "⚠️ Experience recording not detected yet"
fi

# Check for memory manager initialization
if docker-compose logs agentic-worm | grep -q "Memory manager initialized successfully"; then
    echo "✅ Memory manager initialized successfully!"
else
    echo "⚠️ Memory manager not initialized"
fi

# Check if validation errors are gone
if docker-compose logs agentic-worm | grep -q "Input should be a valid string.*NoneType"; then
    echo "❌ Validation errors still present"
else
    echo "✅ No validation errors found!"
fi

# Check for visualization formatting errors
if docker-compose logs agentic-worm | grep -q "unsupported format string passed to NoneType"; then
    echo "❌ Visualization formatting errors still present"
else
    echo "✅ No visualization formatting errors!"
fi

echo ""
echo "🗄️ Checking ArangoDB for collections..."
sleep 2

# Check if collections were created
COLLECTIONS=$(curl -s http://localhost:8529/_api/collection)
if echo "$COLLECTIONS" | grep -q "experiences\|spatial_memories\|strategies\|knowledge_facts"; then
    echo "✅ Memory collections created in ArangoDB!"
    echo "Collections found: $(echo "$COLLECTIONS" | grep -o '"name":"[^"]*' | cut -d'"' -f4 | grep -E '(experiences|spatial|strategies|knowledge)' | tr '\n' ' ')"
else
    echo "⚠️ Memory collections not yet created"
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
echo "==========================================="
echo "🎯 Summary:"
echo "1. Open dashboard: http://localhost:8000"
echo "2. Check Memory System widget - should show real values"
echo "3. Motor commands should be non-zero"
echo "4. Memory counts should increase over time"
echo "5. ArangoDB collections: http://localhost:8529"
echo ""
echo "📊 To monitor live:"
echo "   docker-compose logs -f agentic-worm"
echo "===========================================" 