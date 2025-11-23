from ultralytics import YOLO
from PIL import Image
import io
import os
from pathlib import Path

os.environ["TORCH_WEIGHTS_ONLY"] = "False"

# Use model from services/yolo directory
MODEL_PATH = Path(__file__).parent / "yolo11n.pt"
model = YOLO(str(MODEL_PATH))

def detect_objects(image_bytes: bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception:
        return {"error": "invalid image", "detections": [], "total_objects": 0}
    
    results = model(image)
    
    detections = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])
        
        detections.append({
            "label": label,
            "confidence": round(conf, 3)
        })
    
    return {
        "detections": detections,
        "total_objects": len(detections)
    }

