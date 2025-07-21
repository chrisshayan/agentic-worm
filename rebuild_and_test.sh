#!/bin/bash

echo "🔧 Complete Rebuild and ArangoDB Connection Test"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Step 1: Clean up everything
log_info "Cleaning up existing containers and images..."
docker-compose down -v --remove-orphans
docker system prune -f
docker volume prune -f

# Step 2: Build fresh containers
log_info "Building fresh containers..."
docker-compose build --no-cache --pull

if [ $? -ne 0 ]; then
    log_error "Docker build failed"
    exit 1
fi
log_success "Docker build completed"

# Step 3: Start ArangoDB first
log_info "Starting ArangoDB..."
docker-compose up -d arangodb redis

# Wait for ArangoDB to be ready
log_info "Waiting for ArangoDB to initialize..."
sleep 20

# Test ArangoDB connection
for i in {1..10}; do
    if curl -s http://localhost:8529/_admin/echo > /dev/null; then
        log_success "ArangoDB is responding"
        break
    else
        log_warning "ArangoDB not ready yet (attempt $i/10)"
        sleep 3
    fi
    
    if [ $i -eq 10 ]; then
        log_error "ArangoDB failed to start"
        docker-compose logs arangodb
        exit 1
    fi
done

# Check ArangoDB databases
log_info "Checking ArangoDB databases..."
DB_RESPONSE=$(curl -s http://localhost:8529/_api/database)
log_info "Available databases: $DB_RESPONSE"

# Step 4: Test ArangoDB connection from container
log_info "Testing ArangoDB connection from within Docker..."
docker-compose run --rm agentic-worm python test_arango_connection.py

if [ $? -eq 0 ]; then
    log_success "ArangoDB connection test PASSED"
else
    log_error "ArangoDB connection test FAILED"
    log_info "Checking network connectivity..."
    docker-compose exec agentic-worm ping -c 3 arangodb || log_error "Cannot ping ArangoDB from app container"
fi

# Step 5: Start the application
log_info "Starting the application..."
docker-compose up -d agentic-worm

# Wait for application to start
sleep 10

# Step 6: Check application health
log_info "Testing application health..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "Application is healthy"
        break
    else
        log_warning "Application not ready yet (attempt $i/15)"
        sleep 2
    fi
    
    if [ $i -eq 15 ]; then
        log_error "Application health check failed"
        log_info "Application logs:"
        docker-compose logs --tail=20 agentic-worm
        exit 1
    fi
done

# Step 7: Check for memory system initialization
log_info "Checking memory system initialization..."
sleep 5

# Look for success indicators in logs
if docker-compose logs agentic-worm | grep -i "ArangoDB.*connection.*successful"; then
    log_success "ArangoDB connection successful in application"
else
    log_warning "ArangoDB connection not found in application logs"
fi

if docker-compose logs agentic-worm | grep -i "Memory manager initialized successfully"; then
    log_success "Memory manager initialized successfully"
else
    log_warning "Memory manager initialization not found"
fi

if docker-compose logs agentic-worm | grep -i "Created database.*agentic_worm_memory"; then
    log_success "Database created successfully"
elif docker-compose logs agentic-worm | grep -i "Database.*agentic_worm_memory.*exists"; then
    log_success "Database already exists"
else
    log_warning "Database creation/existence not confirmed"
fi

# Step 8: Final verification
log_info "Final verification..."

# Check if database was created
DB_LIST=$(curl -s http://localhost:8529/_api/database)
if echo "$DB_LIST" | grep -q "agentic_worm_memory"; then
    log_success "Database 'agentic_worm_memory' exists in ArangoDB"
else
    log_warning "Database 'agentic_worm_memory' not found in ArangoDB"
    log_info "Available databases: $DB_LIST"
fi

# Test dashboard
if curl -s http://localhost:8000/ | grep -q "Memory System"; then
    log_success "Dashboard contains Memory System widget"
else
    log_warning "Dashboard Memory System widget not found"
fi

# Step 9: Show final status
echo ""
echo "==============================================="
log_info "FINAL STATUS REPORT"
echo "==============================================="

log_info "Services Status:"
docker-compose ps

echo ""
log_info "Container Health:"
echo "- ArangoDB: $(curl -s http://localhost:8529/_admin/echo > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")"
echo "- Dashboard: $(curl -s http://localhost:8000/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")"

echo ""
log_info "URLs to test:"
echo "🌐 Dashboard: http://localhost:8000"
echo "🗄️ ArangoDB Web UI: http://localhost:8529"
echo "🩺 Health Check: curl http://localhost:8000/health"

echo ""
log_info "Monitoring commands:"
echo "📋 Application logs: docker-compose logs -f agentic-worm"
echo "🔍 ArangoDB logs: docker-compose logs arangodb"
echo "🧠 Memory-specific logs: docker-compose logs agentic-worm | grep -i memory"

echo ""
log_info "Recent application logs (last 10 lines):"
docker-compose logs --tail=10 agentic-worm

echo ""
echo "==============================================="
if curl -s http://localhost:8000/health > /dev/null && curl -s http://localhost:8529/_admin/echo > /dev/null; then
    log_success "🎉 SYSTEM IS READY! Open http://localhost:8000 to see the dashboard"
else
    log_error "❌ System has issues. Check the logs above for details."
fi
echo "===============================================" 