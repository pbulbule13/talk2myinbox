#!/bin/bash
# Communications App Startup Script for Unix/Linux/macOS

echo "========================================"
echo "Communications App Startup"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys."
    echo ""
    exit 1
fi

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Navigate to backend directory
cd backend

# Start the server
echo "Starting Communications App Server..."
echo ""
python server.py

# Return to root directory
cd ..
