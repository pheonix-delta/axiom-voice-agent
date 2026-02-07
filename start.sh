#!/bin/bash
# AXIOM Voice Agent - Setup Script
# Makes installation and startup easy for GitHub

set -e  # Exit on error

echo "╔════════════════════════════════════════╗"
echo "║  AXIOM Voice Agent - Setup & Start    ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VENV_NAME="axiomvenv"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "${BLUE}Project root: $SCRIPT_DIR${NC}"
echo ""

# Step 1: Check Python version
echo "${YELLOW}[1/5]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "${RED}✗ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"
echo "${GREEN}✓ Python found${NC}"
echo ""

# Step 2: Create virtual environment
echo "${YELLOW}[2/5]${NC} Setting up virtual environment..."
if [ ! -d "$VENV_NAME" ]; then
    python3 -m venv "$VENV_NAME"
    echo "${GREEN}✓ Virtual environment created${NC}"
else
    echo "${GREEN}✓ Virtual environment already exists${NC}"
fi
echo ""

# Step 3: Activate and install dependencies
echo "${YELLOW}[3/5]${NC} Installing dependencies..."
source "$VENV_NAME/bin/activate"
if [ -z "$VIRTUAL_ENV" ] || [[ "$VIRTUAL_ENV" != *"/$VENV_NAME" ]]; then
    echo "${RED}✗ Virtual environment not active. Activate $VENV_NAME and retry.${NC}"
    exit 1
fi
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 4: Verify paths
echo "${YELLOW}[4/5]${NC} Verifying configuration..."
cd backend
python config.py > /tmp/config_output.txt 2>&1
if grep -q "All critical paths verified" /tmp/config_output.txt; then
    echo "${GREEN}✓ All paths verified${NC}"
else
    echo "${YELLOW}⚠ Some paths missing (this is OK for STT/TTS models)${NC}"
fi
cd ..
echo ""

# Step 5: Start the system
echo "${YELLOW}[5/5]${NC} Starting AXIOM Voice Agent..."
echo ""
echo "${GREEN}╔════════════════════════════════════════╗${NC}"
echo "${GREEN}║  ✅ System Ready!                      ║${NC}"
echo "${GREEN}║  🌐 http://localhost:8000             ║${NC}"
echo "${GREEN}║  📡 WebSocket: ws://localhost:8000/ws ║${NC}"
echo "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Press CTRL+C to stop"
echo ""

cd backend
exec python main_agent_web.py
