#!/bin/bash

echo "Building Docker image..."
docker build -t milo-ai:stage2 .

echo ""
echo "Note: Make sure BitNet server is running on host (port 8080)"
echo "Start it with: bash scripts/start_bitnet_server.sh"
echo ""
read -p "Press enter when BitNet server is running..."

echo ""
echo "Running test in container..."
docker run --rm \
  --network=host \
  -e BITNET_URL=http://localhost:8080/completion \
  milo-ai:stage2

echo ""
echo "Test complete!"
