#!/bin/bash
set -e

echo "Starting TrendPulse application..."

# Start backend in background
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Start frontend in background
cd ../frontend
npm start &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
