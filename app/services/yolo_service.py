from ultralytics import YOLO
from PIL import Image
import io, os

os.environ["TORCH_WEIGHTS_ONLY"] = "False"

model = YOLO("yolo11n.pt")

# Food lists for classification
healthy_foods = ["apple", "banana", "broccoli", "carrot", "salad", "chicken", "fish", "orange", "grape", "strawberry", "tomato", "cucumber", "lettuce", "spinach"]
unhealthy_foods = ["pizza", "burger", "donut", "cake", "candy", "cookie", "ice cream", "hot dog", "sandwich", "fries"]

def detect_objects(image_bytes: bytes):
    """Detect objects and classify food/non-food"""
    image = Image.open(io.BytesIO(image_bytes))
    results = model(image)
    
    detections = []
    food_items = []
    non_food_items = []
    
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])
        
        is_food = label.lower() in healthy_foods or label.lower() in unhealthy_foods
        
        health_status = "unknown"
        if label.lower() in healthy_foods:
            health_status = "healthy"
            food_items.append(label)
        elif label.lower() in unhealthy_foods:
            health_status = "unhealthy"
            food_items.append(label)
        else:
            non_food_items.append(label)
        
        detections.append({
            "label": label, 
            "confidence": round(conf, 3),
            "is_food": is_food,
            "health_status": health_status
        })
    
    nutrition_summary = generate_nutrition_summary(food_items, non_food_items)
    
    return {
        "detections": detections,
        "food_items": food_items,
        "non_food_items": non_food_items,
        "nutrition_summary": nutrition_summary,
        "total_foods": len(food_items),
        "total_objects": len(detections)
    }

def generate_nutrition_summary(food_items, non_food_items):
    """Create nutrition advice from detected foods"""
    if not food_items:
        return "No food items detected. Try uploading a clearer image of food."
    
    healthy_count = sum(1 for food in food_items if food.lower() in healthy_foods)
    unhealthy_count = len(food_items) - healthy_count
    
    if healthy_count > unhealthy_count:
        return f"Great! Detected {healthy_count} healthy foods. Keep up the good nutrition choices!"
    elif unhealthy_count > healthy_count:
        return f"Consider adding more fruits and vegetables. Detected {unhealthy_count} less healthy options."
    else:
        return f"Mixed meal detected. Balance is key - try adding more vegetables."
