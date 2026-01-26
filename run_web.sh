#!/bin/bash

# Kill existing processes on ports 8000 and 5173 to avoid conflicts
lsof -t -i :8000 | xargs kill -9 2>/dev/null
lsof -t -i :5173 | xargs kill -9 2>/dev/null

echo "Starting Backend (FastAPI)..."
# Start Backend in background
conda run -n mahjong uvicorn server.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "Starting Frontend (Vite)..."
# Start Frontend in background
cd web
conda run -n mahjong npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Services started!"
echo "Backend PID: $BACKEND_PID (Logs: backend.log)"
echo "Frontend PID: $FRONTEND_PID (Logs: frontend.log)"
echo ""
echo "Open http://localhost:5173 to play!"
echo ""
echo "Press CTRL+C to stop servers."

# Trap SIGINT to kill children
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

wait
