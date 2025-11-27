#!/bin/bash

BASE_URL="http://localhost:8000"

echo "Testing Milo AI API..."
echo ""

echo "1. Health check..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "2. BitNet completion..."
curl -s -X POST "$BASE_URL/bitnet/completion" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "n_predict": 50}' | python3 -m json.tool
echo ""

echo "3. MongoDB requests..."
curl -s "$BASE_URL/requests" | python3 -m json.tool
echo ""

echo "4. YOLO detect..."
if [ -f "tests/test_image.jpeg" ]; then
  curl -s -X POST "$BASE_URL/yolo/detect" \
    -F "file=@tests/test_image.jpeg" | python3 -m json.tool
else
  echo "Skipped (no test image)"
fi

echo ""
echo "Done"

