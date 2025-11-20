from services.yolo_service import detect_objects
from services.bitnet_service import analyze_text



print("=== Testing YOLO ===")
try:
    with open("test_image.jpg", "rb") as f:
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

