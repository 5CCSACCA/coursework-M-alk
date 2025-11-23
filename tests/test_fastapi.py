"""
FastAPI Server Test - Stage 3
"""
import requests
import json

FASTAPI_URL = "http://localhost:8000"


def test_root():
    """Root endpoint"""
    print("=== Testing Root Endpoint ===")
    response = requests.get(f"{FASTAPI_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_health():
    """Health check"""
    print("=== Testing Health Endpoint ===")
    response = requests.get(f"{FASTAPI_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_completion():
    """Text generation"""
    print("=== Testing Completion Endpoint ===")
    response = requests.post(
        f"{FASTAPI_URL}/completion",
        json={
            "prompt": "What is machine learning?",
            "n_predict": 30,
            "temperature": 0.7
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Generated Text: {result['content']}")
    print(f"Tokens: {result['tokens_predicted']}")
    print()


def main():
    """Run all tests"""
    print("FastAPI BitNet Server Test")
    print("=" * 50)
    print()
    
    try:
        # Check if server is running
        requests.get(f"{FASTAPI_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("Error: FastAPI server is not running!")
        print("Start it with: bash scripts/start_bitnet_fastapi.sh")
        return
    
    test_root()
    test_health()
    test_completion()
    
    print("=" * 50)
    print("✓ All tests passed!")
    print(f"\nInteractive API docs: {FASTAPI_URL}/docs")
    print(f"Alternative docs: {FASTAPI_URL}/redoc")


if __name__ == "__main__":
    main()

