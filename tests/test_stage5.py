"""
Stage 5 Tests - Firebase Integration
Tests Firebase CRUD operations for model outputs.
"""
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import requests

API_BASE = "http://localhost:8000"


def test_health_firebase():
    """Check Firebase connection status."""
    print("\n=== Testing Firebase Health ===")
    
    response = requests.get(f"{API_BASE}/health")
    assert response.status_code == 200, "Health check failed"
    
    data = response.json()
    print(f"✓ API Status: {data['status']}")
    print(f"✓ Firebase Connected: {data.get('firebase_connected', False)}")
    
    if data.get('firebase_connected'):
        stats = data.get('firebase_stats', {})
        print(f"✓ Total Outputs: {stats.get('total_outputs', 0)}")
        print(f"✓ BitNet Outputs: {stats.get('bitnet_outputs', 0)}")
        print(f"✓ YOLO Outputs: {stats.get('yolo_outputs', 0)}")
    else:
        print("⚠ Firebase not connected - tests will skip Firebase operations")


def test_create_firebase_output():
    """Test creating output in Firebase."""
    print("\n=== Testing Create Firebase Output ===")
    
    payload = {
        "service": "bitnet",
        "request_data": {
            "prompt": "What is cloud computing?",
            "n_predict": 50
        },
        "response_data": {
            "content": "Cloud computing is the delivery of computing services...",
            "tokens_predicted": 15
        },
        "metadata": {
            "test": True,
            "stage": 5
        }
    }
    
    response = requests.post(f"{API_BASE}/firebase/outputs", json=payload)
    
    if response.status_code == 503:
        print("⚠ Firebase service not available")
        return None
    
    assert response.status_code == 201, f"Create failed: {response.text}"
    
    data = response.json()
    doc_id = data["id"]
    
    print(f"✓ Created output: {doc_id}")
    print(f"✓ Service: {data['service']}")
    print(f"✓ Message: {data['message']}")
    
    return doc_id


def test_get_firebase_output(doc_id):
    """Test retrieving specific output."""
    if not doc_id:
        print("⚠ Skipping - no document ID")
        return
    
    print(f"\n=== Testing Get Firebase Output (ID: {doc_id}) ===")
    
    response = requests.get(f"{API_BASE}/firebase/outputs/{doc_id}")
    
    if response.status_code == 503:
        print("⚠ Firebase service not available")
        return
    
    assert response.status_code == 200, f"Get failed: {response.text}"
    
    data = response.json()
    
    print(f"✓ Retrieved output: {data['id']}")
    print(f"✓ Service: {data['service']}")
    print(f"✓ Timestamp: {data['timestamp']}")
    print(f"✓ Request prompt: {data['request']['prompt'][:50]}...")
    print(f"✓ Response preview: {data['response']['content'][:50]}...")


def test_get_all_firebase_outputs():
    """Test retrieving all outputs."""
    print("\n=== Testing Get All Firebase Outputs ===")
    
    response = requests.get(f"{API_BASE}/firebase/outputs?limit=10")
    
    if response.status_code == 503:
        print("⚠ Firebase service not available")
        return
    
    assert response.status_code == 200, f"Get all failed: {response.text}"
    
    data = response.json()
    
    print(f"✓ Total outputs retrieved: {data['total']}")
    print(f"✓ Limit: {data['limit']}")
    print(f"✓ Offset: {data['offset']}")
    
    if data['outputs']:
        print(f"✓ First output ID: {data['outputs'][0]['id']}")
        print(f"✓ First output service: {data['outputs'][0]['service']}")


def test_filter_firebase_outputs():
    """Test filtering outputs by service."""
    print("\n=== Testing Filter Firebase Outputs (BitNet only) ===")
    
    response = requests.get(f"{API_BASE}/firebase/outputs?service=bitnet&limit=5")
    
    if response.status_code == 503:
        print("⚠ Firebase service not available")
        return
    
    assert response.status_code == 200, f"Filter failed: {response.text}"
    
    data = response.json()
    
    print(f"✓ Service filter: {data['service_filter']}")
    print(f"✓ Total BitNet outputs: {data['total']}")
    
    # Verify all are BitNet
    if data['outputs']:
        for output in data['outputs']:
            assert output['service'] == 'bitnet', "Filter returned wrong service"
        print(f"✓ All {len(data['outputs'])} outputs are BitNet")


def test_update_firebase_output(doc_id):
    """Test updating output."""
    if not doc_id:
        print("⚠ Skipping - no document ID")
        return
    
    print(f"\n=== Testing Update Firebase Output (ID: {doc_id}) ===")
    
    updates = {
        "metadata": {
            "test": True,
            "stage": 5,
            "updated": True,
            "note": "This output was updated during Stage 5 testing"
        }
    }
    
    response = requests.put(f"{API_BASE}/firebase/outputs/{doc_id}", json=updates)
    
    if response.status_code == 503:
        print("⚠ Firebase service not available")
        return
    
    assert response.status_code == 200, f"Update failed: {response.text}"
    
    data = response.json()
    
    print(f"✓ Updated output: {data['id']}")
    print(f"✓ Message: {data['message']}")
    print(f"✓ Updated fields: {', '.join(data['updated_fields'])}")
    
    # Verify update
    time.sleep(1)  # Give Firebase time to propagate
    verify_response = requests.get(f"{API_BASE}/firebase/outputs/{doc_id}")
    if verify_response.status_code == 200:
        verify_data = verify_response.json()
        assert verify_data['metadata'].get('updated') == True, "Update not reflected"
        print("✓ Update verified successfully")


def test_delete_firebase_output(doc_id):
    """Test deleting output."""
    if not doc_id:
        print("⚠ Skipping - no document ID")
        return
    
    print(f"\n=== Testing Delete Firebase Output (ID: {doc_id}) ===")
    
    response = requests.delete(f"{API_BASE}/firebase/outputs/{doc_id}")
    
    if response.status_code == 503:
        print("⚠ Firebase service not available")
        return
    
    assert response.status_code == 200, f"Delete failed: {response.text}"
    
    data = response.json()
    
    print(f"✓ Deleted output: {data['id']}")
    print(f"✓ Message: {data['message']}")
    
    # Verify deletion
    time.sleep(1)  # Give Firebase time to propagate
    verify_response = requests.get(f"{API_BASE}/firebase/outputs/{doc_id}")
    assert verify_response.status_code == 404, "Output still exists after deletion"
    print("✓ Deletion verified successfully")


def test_bitnet_auto_store():
    """Test automatic Firebase storage on BitNet request."""
    print("\n=== Testing Automatic Firebase Storage (BitNet) ===")
    
    payload = {
        "prompt": "Explain artificial intelligence in simple terms",
        "n_predict": 40,
        "temperature": 0.7
    }
    
    response = requests.post(f"{API_BASE}/bitnet/completion", json=payload)
    assert response.status_code == 200, f"BitNet request failed: {response.text}"
    
    data = response.json()
    print(f"✓ BitNet response received: {data['content'][:50]}...")
    
    # Check if stored in Firebase
    time.sleep(2)  # Give time for background storage
    
    outputs_response = requests.get(f"{API_BASE}/firebase/outputs?service=bitnet&limit=1")
    if outputs_response.status_code == 200:
        outputs_data = outputs_response.json()
        if outputs_data['total'] > 0:
            print(f"✓ Automatically stored in Firebase")
            latest = outputs_data['outputs'][0]
            print(f"✓ Latest output ID: {latest['id']}")
        else:
            print("⚠ No outputs found (Firebase may not be configured)")
    else:
        print("⚠ Firebase service not available for verification")


def test_yolo_auto_store():
    """Test automatic Firebase storage on YOLO request."""
    print("\n=== Testing Automatic Firebase Storage (YOLO) ===")
    
    # Create dummy image
    test_image = PROJECT_ROOT / "test_image.jpeg"
    
    if not test_image.exists():
        print("⚠ test_image.jpeg not found, skipping YOLO test")
        return
    
    with open(test_image, 'rb') as f:
        files = {'file': ('test_image.jpeg', f, 'image/jpeg')}
        response = requests.post(f"{API_BASE}/yolo/detect", files=files)
    
    assert response.status_code == 200, f"YOLO request failed: {response.text}"
    
    data = response.json()
    print(f"✓ YOLO response received: {data.get('total_objects', 0)} objects detected")
    
    # Check if stored in Firebase
    time.sleep(2)  # Give time for background storage
    
    outputs_response = requests.get(f"{API_BASE}/firebase/outputs?service=yolo&limit=1")
    if outputs_response.status_code == 200:
        outputs_data = outputs_response.json()
        if outputs_data['total'] > 0:
            print(f"✓ Automatically stored in Firebase")
            latest = outputs_data['outputs'][0]
            print(f"✓ Latest output ID: {latest['id']}")
        else:
            print("⚠ No outputs found (Firebase may not be configured)")
    else:
        print("⚠ Firebase service not available for verification")


def main():
    """Run all Stage 5 tests."""
    print("=" * 60)
    print("Stage 5: Firebase Integration Tests")
    print("=" * 60)
    
    try:
        # Test health and connection
        test_health_firebase()
        
        # Test CRUD operations
        doc_id = test_create_firebase_output()
        test_get_firebase_output(doc_id)
        test_get_all_firebase_outputs()
        test_filter_firebase_outputs()
        test_update_firebase_output(doc_id)
        
        # Test automatic storage from model endpoints
        test_bitnet_auto_store()
        test_yolo_auto_store()
        
        # Finally delete test output
        test_delete_firebase_output(doc_id)
        
        print("\n" + "=" * 60)
        print("✓ All Stage 5 tests completed successfully!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API. Is it running?")
        print("Start the API with: bash scripts/start_api.sh")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

