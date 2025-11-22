#!/bin/bash
set -e

BITNET_DIR="BitNet"
MODEL_DIR="models/BitNet-b1.58-2B-4T"
MODEL_FILE="$MODEL_DIR/ggml-model-i2_s.gguf"

echo "=== BitNet Server Setup ==="

if [ ! -d "$BITNET_DIR" ]; then
    echo "Cloning BitNet repo..."
    git clone --recursive https://github.com/microsoft/BitNet.git
    echo "✓ Cloned"
else
    echo "✓ BitNet repo exists"
fi

cd "$BITNET_DIR"

if [ ! -f ".deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -q huggingface-hub requests
    touch .deps_installed
    echo "✓ Installed"
else
    echo "✓ Dependencies OK"
fi

if [ ! -f "$MODEL_FILE" ]; then
    echo "Downloading model (~1.2GB)..."
    mkdir -p "$MODEL_DIR"
    huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf \
        ggml-model-i2_s.gguf \
        --local-dir "$MODEL_DIR" \
        --local-dir-use-symlinks False
    echo "✓ Downloaded"
else
    echo "✓ Model exists"
fi

echo "Setting up i2_s quantization..."
python3 setup_env.py -md "$MODEL_DIR" -q i2_s

echo ""
echo "Starting BitNet server on http://localhost:8080"
echo "Press Ctrl+C to stop"
echo ""

python3 run_inference_server.py -m "$MODEL_FILE" --port 8080
