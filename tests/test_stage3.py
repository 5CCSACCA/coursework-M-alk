"""
Stage 3: API Testing - BitNet server endpoints
"""
import requests
import json
import time
import sys


BITNET_API_URL = "http://localhost:8080"


def test_health_check():
    """Health check"""
    print("=== Testing Health Check ===")
    try:
        response = requests.get(f"{BITNET_API_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_api_info():
    """Root endpoint"""
    print("\n=== Testing API Info ===")
    try:
        response = requests.get(f"{BITNET_API_URL}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        # llama-server may return HTML not JSON
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response (text): {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_text_completion(prompt: str, n_predict: int = 50):
    """Text generation"""
    print(f"\n=== Testing Text Completion ===")
    print(f"Prompt: {prompt}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BITNET_API_URL}/completion",
            json={
                "prompt": prompt,
                "n_predict": n_predict,
                "temperature": 0.7
            },
            timeout=60
        )
        elapsed_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Generated Text: {result.get('content', '')}")
            print(f"Tokens Predicted: {result.get('tokens_predicted', 0)}")
            print(f"Time: {elapsed_time:.2f}s")
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_multiple_prompts():
    """Test with multiple different prompts."""
    test_prompts = [
        "What is artificial intelligence?",
        "Explain quantum computing in simple terms.",
        "What are the benefits of exercise?",
        "How does photosynthesis work?"
    ]
    
    print("\n=== Testing Multiple Prompts ===")
    results = []
    
    for prompt in test_prompts:
        print(f"\nTesting: {prompt}")
        success = test_text_completion(prompt, n_predict=30)
        results.append(success)
        time.sleep(1)  # Small delay between requests
    
    return all(results)


def main():
    """Run all API tests."""
    print("Stage 3: BitNet API Testing")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(f"{BITNET_API_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("Error: BitNet API server is not running!")
        print("Start it with: bash scripts/start_bitnet_server.sh")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("API Info", test_api_info),
        ("Single Prompt", lambda: test_text_completion("What is machine learning?", 50)),
        ("Multiple Prompts", test_multiple_prompts)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

