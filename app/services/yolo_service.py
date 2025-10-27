from ultralytics import YOLO
from PIL import Image
import io, os

os.environ["TORCH_WEIGHTS_ONLY"] = "False"

model = YOLO("yolov8n.pt")

def detect_objects(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes))
    results = model(image)
    detections = []
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])
        detections.append({"label": label, "confidence": round(conf, 3)})
    return detections
