#!/bin/bash
# start.sh — starts both servers for local development
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Kill any existing processes on ports 5001 and 8080
lsof -t -i:5001 | xargs kill -9 2>/dev/null || true
lsof -t -i:8080 | xargs kill -9 2>/dev/null || true
sleep 1

echo "🚀 Starting FastAPI backend on http://localhost:5001 ..."
# Use --no-access-log to reduce noise; watchfiles excluded for venv
WATCHFILES_IGNORE_PATHS="${PROJECT_DIR}/venv" \
    ./venv/bin/uvicorn backend_server:app \
    --host 0.0.0.0 --port 5001 --reload &

echo "🌐 Starting frontend server on http://localhost:8080 ..."
./venv/bin/python3.11 -m http.server 8080 &

echo ""
echo "✅ Both servers running!"
echo "   Frontend: http://localhost:8080"
echo "   API:      http://localhost:5001"
echo "   API Docs: http://localhost:5001/docs"
echo ""
echo "Press Ctrl+C to stop."
wait
