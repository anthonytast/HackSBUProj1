#!/bin/bash

# Study Planner Backend Startup Script

echo "================================"
echo "Study Planner Backend"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Virtual environment created!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
    echo "Dependencies installed!"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env with your API credentials before running the server."
    echo "You need:"
    echo "  - Canvas URL and Access Token"
    echo "  - Google Gemini API Key"
    echo "  - Google Calendar credentials (credentials.json)"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit and configure .env..."
fi

# Start the server
echo ""
echo "Starting FastAPI server..."
echo "API will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
