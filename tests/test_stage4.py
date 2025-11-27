"""
Stage 4 tests - MongoDB request logging.
"""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_mongodb_connection():
    """Check MongoDB Atlas connection."""
    print("\n=== Testing MongoDB Connection ===")
    
    try:
        from database.mongo_service import get_db_service
        
        db = get_db_service()
        
        if db.is_connected():
            print("✓ MongoDB connected")
            stats = db.get_stats()
            print(f"  Total requests: {stats.get('total_requests', 0)}")
            print(f"  BitNet requests: {stats.get('bitnet_requests', 0)}")
            print(f"  YOLO requests: {stats.get('yolo_requests', 0)}")
            return True
        else:
            print("✗ MongoDB not connected")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_api_health():
    """Health check with database status."""
    print("\n=== Testing API Health (with DB) ===")
    
    try:
        import requests
        
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Database: {data.get('database_connected')}")
            
            if data.get('database_stats'):
                stats = data['database_stats']
                print(f"  Total requests: {stats.get('total_requests', 0)}")
            
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_bitnet_request_logging():
    """BitNet request logging."""
    print("\n=== Testing BitNet Request Logging ===")
    
    try:
        import requests
        
        # Make a BitNet request
        payload = {
            "prompt": "What is cloud computing?",
            "n_predict": 30
        }
        
        response = requests.post(
            "http://localhost:8000/bitnet/completion",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✓ BitNet request successful")
            
            # Wait a bit for DB write
            time.sleep(1)
            
            # Check if logged in DB
            requests_response = requests.get(
                "http://localhost:8000/requests?service=bitnet&limit=1",
                timeout=5
            )
            
            if requests_response.status_code == 200:
                data = requests_response.json()
                if data.get('total', 0) > 0:
                    print("✓ Request logged in database")
                    latest = data['requests'][0]
                    print(f"  Request ID: {latest.get('_id')}")
                    print(f"  Timestamp: {latest.get('timestamp')}")
                    return True
                else:
                    print("✗ No requests found in database")
                    return False
            else:
                print(f"✗ Failed to retrieve requests: {requests_response.status_code}")
                return False
        else:
            print(f"✗ BitNet request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_yolo_request_logging():
    """YOLO request logging."""
    print("\n=== Testing YOLO Request Logging ===")
    
    try:
        import requests
        
        test_image = Path(__file__).parent / "test_image.jpeg"
        
        if not test_image.exists():
            print("✗ test_image.jpeg not found")
            return False
        
        # Make a YOLO request
        with open(test_image, "rb") as f:
            files = {"file": ("test_image.jpeg", f, "image/jpeg")}
            response = requests.post(
                "http://localhost:8000/yolo/detect",
                files=files,
                timeout=10
            )
        
        if response.status_code == 200:
            print("✓ YOLO request successful")
            
            # Wait a bit for DB write
            time.sleep(1)
            
            # Check if logged in DB
            requests_response = requests.get(
                "http://localhost:8000/requests?service=yolo&limit=1",
                timeout=5
            )
            
            if requests_response.status_code == 200:
                data = requests_response.json()
                if data.get('total', 0) > 0:
                    print("✓ Request logged in database")
                    latest = data['requests'][0]
                    print(f"  Request ID: {latest.get('_id')}")
                    print(f"  Timestamp: {latest.get('timestamp')}")
                    return True
                else:
                    print("✗ No requests found in database")
                    return False
            else:
                print(f"✗ Failed to retrieve requests: {requests_response.status_code}")
                return False
        else:
            print(f"✗ YOLO request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_all_requests():
    """Get all requests."""
    print("\n=== Testing Get All Requests ===")
    
    try:
        import requests
        
        response = requests.get(
            "http://localhost:8000/requests?limit=10",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Retrieved {data.get('total', 0)} requests")
            print(f"  Service filter: {data.get('service_filter')}")
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_get_request_by_id():
    """Get request by ID."""
    print("\n=== Testing Get Request by ID ===")
    
    try:
        import requests
        
        # First get list of requests
        response = requests.get(
            "http://localhost:8000/requests?limit=1",
            timeout=5
        )
        
        if response.status_code != 200:
            print("✗ Failed to get requests list")
            return False
        
        data = response.json()
        if data.get('total', 0) == 0:
            print("⚠ No requests in database to test with")
            return True
        
        request_id = data['requests'][0]['_id']
        
        # Get specific request
        response = requests.get(
            f"http://localhost:8000/requests/{request_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            request_data = response.json()
            print(f"✓ Retrieved request {request_id}")
            print(f"  Service: {request_data.get('service')}")
            print(f"  Status: {request_data.get('status')}")
            return True
        else:
            print(f"✗ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run Stage 4 tests."""
    print("=" * 50)
    print("Stage 4 - MongoDB Persistence Tests")
    print("=" * 50)
    
    results = []
    
    # Test 1: MongoDB connection
    results.append(("MongoDB Connection", test_mongodb_connection()))
    
    # Test 2: API health with DB
    results.append(("API Health", test_api_health()))
    
    # Test 3: BitNet request logging
    results.append(("BitNet Logging", test_bitnet_request_logging()))
    
    # Test 4: YOLO request logging
    results.append(("YOLO Logging", test_yolo_request_logging()))
    
    # Test 5: Get all requests
    results.append(("Get All Requests", test_get_all_requests()))
    
    # Test 6: Get request by ID
    results.append(("Get Request by ID", test_get_request_by_id()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All Stage 4 tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

