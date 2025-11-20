import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.yolo_service import detect_objects
from services.bitnet_service import analyze_text



print("=== Testing YOLO ===")
try:
    test_image_path = os.path.join(os.path.dirname(__file__), "..", "test_image.jpg")
    with open(test_image_path, "rb") as f:
        yolo_result = detect_objects(f.read())
    print("YOLO Result:")
    print(yolo_result)
    print()
except FileNotFoundError:
    print("error: test_image.jpg not found")

# Testing BitNet
print("=== Testing BitNet ===")
print(analyze_text("Explain why fruits are healthy?"))


print("=== Test Complete ===")

