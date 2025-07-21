#!/bin/bash

echo "🔧 Quick Syntax Fix and Rebuild"
echo "==============================="

# Step 1: Fix the syntax error in workflow.py
echo "📝 Applying syntax fix to workflow.py..."

# Create a backup
cp src/agentic_worm/intelligence/workflow.py src/agentic_worm/intelligence/workflow.py.backup

# Use sed to fix the indentation issue around line 634
# The problem is that after the try: block, the code needs proper indentation
sed -i '' '634s/^                /                    /' src/agentic_worm/intelligence/workflow.py
sed -i '' '635s/^                /                    /' src/agentic_worm/intelligence/workflow.py
sed -i '' '636s/^                /                    /' src/agentic_worm/intelligence/workflow.py
sed -i '' '637s/^                /                    /' src/agentic_worm/intelligence/workflow.py
sed -i '' '638s/^                /                    /' src/agentic_worm/intelligence/workflow.py
sed -i '' '639s/^                /                    /' src/agentic_worm/intelligence/workflow.py
sed -i '' '640s/^                /                    /' src/agentic_worm/intelligence/workflow.py

# Step 2: Test the syntax
echo "🧪 Testing Python syntax..."
python3 -c "
import ast
try:
    with open('src/agentic_worm/intelligence/workflow.py', 'r') as f:
        ast.parse(f.read())
    print('✅ Syntax is valid!')
except SyntaxError as e:
    print(f'❌ Syntax error: Line {e.lineno}: {e.msg}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "⚠️ Syntax fix failed, restoring backup..."
    mv src/agentic_worm/intelligence/workflow.py.backup src/agentic_worm/intelligence/workflow.py
    exit 1
fi

echo "✅ Syntax fixed successfully!"

# Step 3: Rebuild Docker container
echo ""
echo "🔨 Rebuilding Docker container..."
docker-compose build --no-cache agentic-worm

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

# Step 4: Restart the application
echo ""
echo "🚀 Restarting application..."
docker-compose down
docker-compose up -d

# Step 5: Wait and test
echo ""
echo "⏳ Waiting for services to start..."
sleep 20

# Check if the error is resolved
echo ""
echo "🔍 Checking for workflow initialization..."
sleep 5

if docker-compose logs agentic-worm 2>&1 | grep -q "LangGraph workflow initialized"; then
    echo "✅ LangGraph workflow initialized successfully!"
elif docker-compose logs agentic-worm 2>&1 | grep -q "Failed to initialize LangGraph workflow"; then
    echo "❌ LangGraph workflow still failing"
    echo "📋 Recent logs:"
    docker-compose logs --tail=10 agentic-worm
else
    echo "⚠️ No clear workflow initialization status"
fi

# Check memory system
if docker-compose logs agentic-worm 2>&1 | grep -q "Memory manager initialized successfully"; then
    echo "✅ Memory manager initialized!"
else
    echo "⚠️ Memory manager not initialized yet"
fi

# Check dashboard
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Dashboard is healthy"
    echo "🌐 Access at: http://localhost:8000"
else
    echo "❌ Dashboard not accessible"
fi

echo ""
echo "==============================="
echo "🎯 Next Steps:"
echo "1. Open http://localhost:8000"
echo "2. Check Memory System widget"
echo "3. Verify motor commands are non-zero"
echo "4. Check ArangoDB for collections at http://localhost:8529"
echo "===============================" 