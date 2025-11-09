#!/bin/bash

echo "=========================================="
echo "Face Recognition System - Frontend Startup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: backend directory not found${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found${NC}"
    exit 1
fi

# Function to start backend
start_backend() {
    echo -e "${BLUE}Starting Flask Backend...${NC}"
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements if needed
    echo -e "${BLUE}Installing backend dependencies...${NC}"
    pip install -q flask flask-cors opencv-python deepface numpy tensorflow tf-keras
    
    # Start Flask
    echo -e "${GREEN}✓ Backend starting on http://localhost:5001${NC}"
    python3 app.py &
    BACKEND_PID=$!
    cd ..
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}Starting React Frontend...${NC}"
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}Installing frontend dependencies (this may take a few minutes)...${NC}"
        npm install
    fi
    
    # Start React
    echo -e "${GREEN}✓ Frontend starting on http://localhost:3000${NC}"
    npm start &
    FRONTEND_PID=$!
    cd ..
}

# Start both servers
start_backend
sleep 3
start_frontend

echo ""
echo -e "${GREEN}=========================================="
echo "Both servers are starting!"
echo "==========================================${NC}"
echo ""
echo "Backend:  http://localhost:5001"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
