#!/usr/bin/env bash
# ==============================================================================
# FormMind AI - Production Launch Script (Linux / macOS / Cloud)
# ==============================================================================
set -e

echo "========================================="
echo "  FormMind AI - Production Server"
echo "========================================="

export ENVIRONMENT=production
export DEBUG=false

# Activate virtualenv if available
if [ -d "./venv" ]; then
    echo "Activating virtualenv..."
    source ./venv/bin/activate
fi

# Run Uvicorn ASGI Server
PORT="${PORT:-8000}"
WORKERS="${WORKERS:-2}"

echo "Starting Uvicorn ASGI Server on port $PORT with $WORKERS workers..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT" --workers "$WORKERS"
