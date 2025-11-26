#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BITNET_DIR="$PROJECT_DIR/BitNet"
MODEL_PATH="$BITNET_DIR/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
API_PORT="${API_PORT:-8000}"
LLAMA_PORT="${LLAMA_SERVER_PORT:-8080}"
BITNET_MOCK="${BITNET_MOCK:-0}"

if [ "$BITNET_MOCK" != "1" ] && [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model not found at $MODEL_PATH"
    echo "Set BITNET_MOCK=1 to run with the lightweight mock BitNet for testing."
    exit 1
fi

cd "$PROJECT_DIR"
echo "Starting Milo AI Unified API on http://localhost:$API_PORT"
if [ "$BITNET_MOCK" = "1" ]; then
    echo "⚠️  BITNET_MOCK=1 (mock LLM mode - for testing only)"
else
    echo "✅ Real AI mode enabled"
    echo "Model: $MODEL_PATH"
    echo "llama-server port: $LLAMA_PORT"
fi
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

BITNET_MOCK="$BITNET_MOCK" $PYTHON_CMD "$PROJECT_DIR/api/api.py" \
    -m "$MODEL_PATH" \
    --port "$API_PORT" \
    --llama-port "$LLAMA_PORT"
