#!/bin/bash

set -e

echo "Building and starting YOLO container..."
echo "Note: BitNet server must be running on host (localhost:8080)"
echo ""
docker-compose up --build
