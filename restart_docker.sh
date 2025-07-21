#!/bin/bash

echo "🐳 Rebuilding Agentic Worm Docker Setup..."

# Stop and remove containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Remove old volumes (optional - uncomment if you want fresh data)
# echo "🗑️ Removing old volumes..."
# docker-compose down -v

# Rebuild and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait a moment for startup
echo "⏳ Waiting for services to start..."
sleep 15

# Show status
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🌐 Dashboard should be available at: http://localhost:8000"
echo "🗄️ ArangoDB interface available at: http://localhost:8529"
echo ""
echo "📋 To view logs:"
echo "  docker-compose logs -f agentic-worm"
echo "  docker-compose logs -f arangodb"
echo ""
echo "🔍 To check if dashboard is responding:"
echo "  curl http://localhost:8000/health" 