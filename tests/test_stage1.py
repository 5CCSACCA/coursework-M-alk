import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.yolo_service import detect_objects
from services.bitnet_service import analyze_text
import json
import time

# Test YOLO
print("=== YOLO Detection ===")
with open("test_image.jpeg", "rb") as f:
    yolo_result = detect_objects(f.read())

print(json.dumps(yolo_result, indent=2))
print()

# Test BitNet
print("=== BitNet Analysis ===")
foods = list(set([d["label"] for d in yolo_result["detections"]]))
question = f"Are {', '.join(foods)} healthy or unhealthy foods?"

print(f"Question: {question}")
start = time.time()
result = analyze_text(question)

print(f"Answer: {result['output']}")
print(f"Time: {time.time() - start:.2f}s")
