# Milo – AI Nutrition Analyzer (Stage 1)

Milo is a **Stage 1** implementation that demonstrates basic model functionality with predefined default parameters. This stage focuses on the core AI models:

- **YOLOv8 object detection** for analyzing food images
- **BitNet-style text analysis** for nutrition recommendations

The models can receive any type of input and produce predictions, fulfilling the Stage 1 requirements.

---

## Stage 1 Features

* YOLOv8n image inference via the `ultralytics` package
* Simple `bitnet_service` that provides nutrition recommendations
* Basic Python script to test both models
* Predefined default parameters for both models

---

## Project Layout

```
.
├── app
│   ├── main.py               # Stage 1 test script
│   └── services
│       ├── yolo_service.py   # YOLOv8 image inference logic
│       └── bitnet_service.py # Text analysis service
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## Getting Started

### 1. Prerequisites

* Python 3.11
* `pip` for installing dependencies
* (Optional) virtual environment

  ```bash
  python -m venv .venv && source .venv/bin/activate
  ```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> The first run of the YOLO model will download small weights (~6 MB).
> Make sure you have network access the first time you start the service.

### 3. Run Stage 1 Test

```bash
python app/main.py
```

This will demonstrate both models working with their predefined default parameters.

---

## Model Usage

### YOLO Object Detection

The YOLO service (`yolo_service.py`) can detect objects in images:

```python
from app.services.yolo_service import detect_objects

# Load image bytes
with open("food_image.jpg", "rb") as f:
    image_bytes = f.read()

# Get detections
detections = detect_objects(image_bytes)
print(detections)
```

**Expected Output:**
```json
[
    {"label": "person", "confidence": 0.95},
    {"label": "car", "confidence": 0.87},
    {"label": "dog", "confidence": 0.73}
]
```

### BitNet Text Analysis

The BitNet service (`bitnet_service.py`) analyzes nutrition-related text:

```python
from app.services.bitnet_service import analyze_text

# Analyze text input
result = analyze_text("I ate chicken and rice for lunch")
print(result)
```

**Expected Output:**
```json
{
    "summary": "This text is about: I ate chicken and rice for lunch...",
    "recommendation": "Eat balanced meals with proteins and vitamins."
}
```

---

## Stage 1 Summary

Stage 1 successfully implements the coursework requirement:

> "Begin with a model that comes with predefined default parameters. Write Python code that allows the model to receive any type of input and produce predictions."

**What's Implemented:**
- ✅ YOLOv8 model with default parameters for object detection
- ✅ BitNet-style model with default parameters for text analysis
- ✅ Python code that can receive any input type and produce predictions
- ✅ Test script demonstrating both models work correctly

**Next Steps:**
- Stage 2: Containerization with Docker
- Stage 3: API exposure with FastAPI
- Stage 4: Database persistence

---

## Testing

Run the test script to verify both models work:

```bash
python app/main.py
```

This will output:
- YOLO model loading confirmation
- Example detection results
- BitNet text analysis examples
- Confirmation that Stage 1 is complete