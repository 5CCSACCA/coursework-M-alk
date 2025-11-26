#!/bin/bash

# Test runner for Milo AI project
# Runs all tests for Stages 1-5

set -e

echo "========================================="
echo "Running Milo AI Tests"
echo "========================================="
echo ""

# Stage 1 test
echo "=== Stage 1: Model Tests ==="
python3 tests/test_stage1.py
echo "✅ Stage 1 tests passed"
echo ""

# Check if API is running for Stage 3+ tests
echo "=== Checking API availability ==="
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is running"
    echo ""
    
    echo "=== Stage 3: API Tests ==="
    python3 tests/test_fastapi.py
    echo "✅ Stage 3 tests passed"
    echo ""
    
    echo "=== Stage 4: MongoDB Tests ==="
    python3 tests/test_stage4.py
    echo "✅ Stage 4 tests passed"
    echo ""
    
    echo "=== Stage 5: Firebase Tests ==="
    python3 tests/test_stage5.py
    echo "✅ Stage 5 tests passed"
else
    echo "⚠️  API not running, skipping Stage 3-5 tests"
    echo "   Start API with: bash scripts/start_api.sh"
fi

echo ""
echo "========================================="
echo "Test Summary: All available tests passed!"
echo "========================================="

