#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BITNET_DIR="$PROJECT_DIR/BitNet"
MODEL_PATH="$BITNET_DIR/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
SERVER_PORT="${BITNET_SERVER_PORT:-8080}"
SERVER_THREADS="${BITNET_SERVER_THREADS:-4}"
SERVER_CTX_SIZE="${BITNET_SERVER_CTX_SIZE:-1024}"
LLAMA_SERVER="$BITNET_DIR/build/bin/llama-server"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Error: Model not found at $MODEL_PATH"
    exit 1
fi

if [ ! -f "$LLAMA_SERVER" ]; then
    echo "Error: llama-server binary not found at $LLAMA_SERVER"
    echo "Please build BitNet first by running: cd BitNet && mkdir -p build && cd build && cmake .. && make -j"
    exit 1
fi

cd "$BITNET_DIR"
echo "Starting BitNet server on http://localhost:$SERVER_PORT"
echo "Model: $MODEL_PATH"
echo "Using: $LLAMA_SERVER"
echo ""

"$LLAMA_SERVER" \
    -m "$MODEL_PATH" \
    --port "$SERVER_PORT" \
    -t "$SERVER_THREADS" \
    -c "$SERVER_CTX_SIZE" \
    --host 127.0.0.1

