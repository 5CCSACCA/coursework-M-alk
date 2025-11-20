#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BITNET_DIR="$PROJECT_DIR/BitNet"
MODEL_PATH="$BITNET_DIR/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
SERVER_PORT="${BITNET_SERVER_PORT:-8080}"
SERVER_THREADS="${BITNET_SERVER_THREADS:-4}"
SERVER_CTX_SIZE="${BITNET_SERVER_CTX_SIZE:-1024}"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model not found at $MODEL_PATH"
    exit 1
fi

if [ ! -f "$BITNET_DIR/build/bin/llama-server" ]; then
    echo "Error: BitNet server binary not found. Please build it first."
    exit 1
fi

cd "$BITNET_DIR"
echo "Starting BitNet server on http://localhost:$SERVER_PORT"
echo "Model: $MODEL_PATH"
echo ""
python run_inference_server.py -m "$MODEL_PATH" --port "$SERVER_PORT" -t "$SERVER_THREADS" -c "$SERVER_CTX_SIZE"

