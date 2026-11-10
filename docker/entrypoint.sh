#!/bin/sh
set -e

echo "=============================================================================="
echo "          e-BIS Sahayak — Unified Cloud Production Startup"
echo "=============================================================================="

# 1. Start FastAPI backend on internal port 8000
echo "[1/2] Starting FastAPI backend on 127.0.0.1:8000..."
cd /app/backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait for backend to respond on /health
echo "Waiting for backend healthcheck..."
max_attempts=30
attempt=0
until curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; do
    sleep 1
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "Error: Backend failed to initialize within 30 seconds."
        exit 1
    fi
done
echo "Backend is live and healthy!"

# 2. Start Next.js frontend on public PORT
PUBLIC_PORT="${PORT:-3000}"
echo "[2/2] Starting Next.js frontend portal on port ${PUBLIC_PORT}..."
cd /app/frontend
export BACKEND_INTERNAL_URL="http://127.0.0.1:8000"
export NEXT_PUBLIC_API_URL="/api/v1"
export NODE_ENV=production

exec npm start -- -p "${PUBLIC_PORT}"
