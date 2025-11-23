#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BITNET_DIR="$PROJECT_DIR/BitNet"
MODEL_PATH="$BITNET_DIR/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
FASTAPI_PORT="${FASTAPI_PORT:-8000}"
LLAMA_PORT="${LLAMA_SERVER_PORT:-8080}"
SERVER_THREADS="${BITNET_SERVER_THREADS:-4}"
SERVER_CTX_SIZE="${BITNET_SERVER_CTX_SIZE:-1024}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model not found at $MODEL_PATH"
    exit 1
fi

cd "$PROJECT_DIR"
echo "Starting BitNet FastAPI server on http://localhost:$FASTAPI_PORT"
echo "Model: $MODEL_PATH"
echo "llama-server port: $LLAMA_PORT"
echo ""

# Try to use python3, fallback to python, or venv python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
elif [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_DIR/venv/bin/python"
else
    echo "Error: Python not found. Please install Python 3 or activate your virtual environment."
    exit 1
fi

# Note: This script now uses the unified API (api/api.py)
# The old fastapi_server.py has been removed in favor of the unified API
$PYTHON_CMD "$PROJECT_DIR/api/api.py" \
    -m "$MODEL_PATH" \
    --port "$FASTAPI_PORT" \
    --llama-port "$LLAMA_PORT"

