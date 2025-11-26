import sys
import os
import requests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.yolo.yolo_service import detect_objects
import json
import time

# Test YOLO
print("=== YOLO Detection ===")
with open("test_image.jpeg", "rb") as f:
    yolo_result = detect_objects(f.read())

print(json.dumps(yolo_result, indent=2))
print()

# Test BitNet (via API endpoint)
print("=== BitNet Analysis ===")
foods = list(set([d["label"] for d in yolo_result["detections"]]))
question = f"Are {', '.join(foods)} healthy or unhealthy foods?"

print(f"Question: {question}")
start = time.time()

# Use API endpoint instead of service wrapper
try:
    response = requests.post(
        "http://localhost:8000/bitnet/completion",
        json={"prompt": question, "n_predict": 50, "temperature": 0.7},
        timeout=30
    )
    if response.status_code == 200:
        result_data = response.json()
        answer = result_data.get("content", "No response")
        print(f"Answer: {answer}")
    else:
        print(f"Error: HTTP {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

print(f"Time: {time.time() - start:.2f}s")
