#!/bin/bash

# 🚀 Agentic Worm: Complete Setup Script
# ======================================
# 
# This script sets up everything needed to run the agentic worm demonstrations.
# It handles dependencies, virtual environments, and system preparation.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                               ║"
    echo "║  🧠 AGENTIC WORM: COMPLETE SETUP                                             ║"
    echo "║                                                                               ║"
    echo "║  🎯 Preparing your system for intelligent digital life demonstrations        ║"
    echo "║                                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print colored message
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check Python version
check_python() {
    print_status $BLUE "🐍 Checking Python installation..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status $GREEN "✅ Python $PYTHON_VERSION - Compatible!"
            PYTHON_CMD="python3"
        else
            print_status $RED "❌ Python 3.8+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    elif command_exists python; then
        PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_status $GREEN "✅ Python $PYTHON_VERSION - Compatible!"
            PYTHON_CMD="python"
        else
            print_status $RED "❌ Python 3.8+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_status $RED "❌ Python not found. Please install Python 3.8+"
        print_status $YELLOW "💡 Visit: https://python.org/downloads/"
        exit 1
    fi
}

# Check if we're in the project directory
check_project_directory() {
    print_status $BLUE "📁 Checking project structure..."
    
    if [ ! -f "README.md" ] || [ ! -d "src" ] || [ ! -f "requirements.txt" ]; then
        print_status $RED "❌ Please run this script from the agentic-worm project root directory"
        exit 1
    fi
    
    print_status $GREEN "✅ Project structure verified"
}

# Setup virtual environment
setup_virtual_environment() {
    print_status $BLUE "🔧 Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_status $YELLOW "📦 Creating new virtual environment..."
        $PYTHON_CMD -m venv venv
        print_status $GREEN "✅ Virtual environment created"
    else
        print_status $GREEN "✅ Virtual environment already exists"
    fi
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        print_status $BLUE "🔄 Activating virtual environment..."
        source venv/bin/activate
        print_status $GREEN "✅ Virtual environment activated"
    elif [ -f "venv/Scripts/activate" ]; then
        print_status $BLUE "🔄 Activating virtual environment (Windows)..."
        source venv/Scripts/activate
        print_status $GREEN "✅ Virtual environment activated"
    else
        print_status $RED "❌ Could not find virtual environment activation script"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status $BLUE "📦 Installing Python dependencies..."
    
    # Upgrade pip first
    print_status $YELLOW "⬆️ Upgrading pip..."
    pip install --upgrade pip --quiet
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        print_status $YELLOW "📥 Installing from requirements.txt..."
        pip install -r requirements.txt --quiet
        print_status $GREEN "✅ Dependencies installed successfully"
    else
        print_status $YELLOW "📥 Installing essential packages..."
        pip install fastapi uvicorn websockets aiohttp --quiet
        print_status $GREEN "✅ Essential packages installed"
    fi
}

# Verify installation
verify_installation() {
    print_status $BLUE "🧪 Verifying installation..."
    
    # Test basic imports
    $PYTHON_CMD -c "
import sys
sys.path.insert(0, 'src')

try:
    from agentic_worm.core.state import create_initial_state
    from agentic_worm.intelligence.workflow import AgenticWorkflow
    print('✅ Core modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)

try:
    import fastapi
    import uvicorn
    print('✅ Web server dependencies available')
except ImportError as e:
    print(f'❌ Web dependency error: {e}')
    sys.exit(1)

print('🎉 Installation verification completed!')
"
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Installation verified successfully"
    else
        print_status $RED "❌ Installation verification failed"
        exit 1
    fi
}

# Make scripts executable
setup_scripts() {
    print_status $BLUE "🔧 Setting up demo scripts..."
    
    # Make Python scripts executable
    chmod +x quick_start.py 2>/dev/null || true
    chmod +x launch_demo.py 2>/dev/null || true
    chmod +x scripts/*.py 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true
    
    print_status $GREEN "✅ Scripts configured"
}

# Show completion message
show_completion() {
    print_status $GREEN "🎉 SETUP COMPLETE!"
    echo ""
    print_status $CYAN "🚀 Ready to run agentic worm demonstrations!"
    echo ""
    print_status $BOLD "Quick Start Options:"
    print_status $YELLOW "  • ${BOLD}python3 quick_start.py${NC}${YELLOW}     - 30-second instant demo"
    print_status $YELLOW "  • ${BOLD}python3 launch_demo.py${NC}${YELLOW}     - Full interactive launcher"
    print_status $YELLOW "  • ${BOLD}python3 scripts/demo_dashboard.py${NC}${YELLOW} - Live web dashboard"
    echo ""
    print_status $MAGENTA "🔬 Advanced Options:"
    print_status $CYAN "  • ${BOLD}python3 scripts/test_openworm_integration.py${NC}${CYAN} - Neural simulation test"
    print_status $CYAN "  • ${BOLD}python3 scripts/test_agentic_workflow.py${NC}${CYAN}     - AI workflow test"
    echo ""
    print_status $GREEN "📚 For detailed documentation, see: README.md"
    echo ""
    print_status $BOLD "🌟 Enjoy exploring intelligent digital life!"
}

# Main setup function
main() {
    print_banner
    
    echo ""
    print_status $BLUE "🏁 Starting complete system setup..."
    echo ""
    
    check_python
    check_project_directory
    setup_virtual_environment
    install_dependencies
    verify_installation
    setup_scripts
    
    echo ""
    show_completion
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}🛑 Setup interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@" 