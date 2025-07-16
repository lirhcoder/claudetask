#!/bin/bash

# Claude Code Web Application Startup Script

echo "Starting Claude Code Web Application..."

# Check if running in development or production
ENV=${1:-development}

if [ "$ENV" = "development" ]; then
    echo "Running in development mode..."
    
    # Start backend
    echo "Starting Flask backend..."
    cd backend
    python3 app.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 3
    
    # Start frontend
    echo "Starting React frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "Application is running!"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:5000"
    echo ""
    echo "Press Ctrl+C to stop..."
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID" INT
    wait
    
elif [ "$ENV" = "production" ]; then
    echo "Running in production mode..."
    
    # Build frontend
    echo "Building frontend..."
    cd frontend
    npm run build
    cd ..
    
    # Start backend with gunicorn
    echo "Starting production server..."
    cd backend
    gunicorn "app:app" \
        --worker-class eventlet \
        --workers 4 \
        --bind 0.0.0.0:5000 \
        --timeout 300
else
    echo "Unknown environment: $ENV"
    echo "Usage: ./start.sh [development|production]"
    exit 1
fi