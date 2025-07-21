#!/bin/bash

echo "🧠 Testing Agentic Worm Memory System..."
echo "=================================================="

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️ Port $1 is already in use"
        return 1
    else
        echo "✅ Port $1 is available"
        return 0
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s $url > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start within timeout"
    return 1
}

# Step 1: Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "✅ Docker and docker-compose are available"

# Step 2: Check ports
echo ""
echo "🔍 Checking required ports..."
check_port 8000  # Dashboard
check_port 8529  # ArangoDB
check_port 6379  # Redis

# Step 3: Stop existing containers
echo ""
echo "🛑 Stopping existing containers..."
docker-compose down -v 2>/dev/null || echo "No existing containers to stop"

# Step 4: Build and start services
echo ""
echo "🔨 Building and starting services..."
docker-compose up --build -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker services"
    echo "📋 Showing logs:"
    docker-compose logs
    exit 1
fi

# Step 5: Wait for services to be ready
echo ""
echo "⏳ Waiting for services to initialize..."

# Wait for ArangoDB
if wait_for_service "http://localhost:8529/_admin/echo" "ArangoDB"; then
    echo "🗄️ ArangoDB Web UI: http://localhost:8529"
else
    echo "❌ ArangoDB failed to start"
    echo "📋 ArangoDB logs:"
    docker-compose logs arangodb
fi

# Wait for Dashboard
if wait_for_service "http://localhost:8000/health" "Dashboard"; then
    echo "🌐 Dashboard: http://localhost:8000"
else
    echo "❌ Dashboard failed to start"
    echo "📋 Application logs:"
    docker-compose logs agentic-worm
fi

# Step 6: Test API endpoints
echo ""
echo "🧪 Testing API endpoints..."

# Test health endpoint
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed"
fi

# Test dashboard HTML
if curl -s http://localhost:8000/ | grep -q "Memory System"; then
    echo "✅ Dashboard HTML contains Memory System"
else
    echo "❌ Dashboard HTML missing Memory System"
fi

# Step 7: Show container status
echo ""
echo "📊 Container Status:"
docker-compose ps

# Step 8: Show recent logs
echo ""
echo "📋 Recent Application Logs:"
docker-compose logs --tail=20 agentic-worm

# Step 9: Check for specific success indicators
echo ""
echo "🔍 Checking for success indicators..."

# Check for memory manager initialization
if docker-compose logs agentic-worm | grep -q "Memory manager initialized"; then
    echo "✅ Memory manager initialized successfully"
else
    echo "⚠️ Memory manager initialization not found in logs"
fi

# Check for ArangoDB connection
if docker-compose logs agentic-worm | grep -q "ArangoDB connection established"; then
    echo "✅ ArangoDB connection established"
else
    echo "⚠️ ArangoDB connection not established"
fi

# Check for motor commands
if docker-compose logs agentic-worm | grep -q "ACTION: Motor commands executed"; then
    echo "✅ Motor commands being executed"
else
    echo "⚠️ Motor commands not found in logs"
fi

echo ""
echo "=================================================="
echo "🎯 Test Summary:"
echo "- Dashboard: http://localhost:8000"
echo "- ArangoDB: http://localhost:8529"
echo "- Health Check: curl http://localhost:8000/health"
echo ""
echo "📋 To monitor logs:"
echo "  docker-compose logs -f agentic-worm"
echo ""
echo "🛑 To stop:"
echo "  docker-compose down"
echo ""
echo "🧠 Memory System Features to Test:"
echo "1. Check Memory System widget shows non-zero values"
echo "2. Click memory overlay buttons (Spatial, Experiences, etc.)"
echo "3. Verify ArangoDB collections are created"
echo "4. Monitor motor commands changing from 0"
echo "==================================================" 