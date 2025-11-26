# Milo AI - Stage 1: Local Inference

## Overview

Stage 1 focuses on running BitNet (Text Generation) and YOLO (Object Detection) models locally without containers or API servers.

## Project Structure

```
coursework-MohamedAlketbi/
├── services/
│   └── yolo/
│       ├── yolo_service.py      # YOLO detection logic
│       └── yolo11n.pt           # YOLO model file
├── bitnet-service/
│   └── model/
│       └── ggml-model-i2_s.gguf # BitNet model
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download Models

#### YOLO Model

The YOLO model should already be in `services/yolo/yolo11n.pt`. If missing, Ultralytics will auto-download it on first use.

#### BitNet Model

```bash
cd bitnet-service/model
wget https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-gguf/resolve/main/ggml-model-i2_s.gguf
```

## Usage

### YOLO Object Detection

```python
from services.yolo.yolo_service import detect_objects

# Read image
with open("path/to/image.jpg", "rb") as f:
    image_bytes = f.read()

# Detect objects
result = detect_objects(image_bytes)
print(result)
# Output: {"detections": [...], "total_objects": 5}
```

### BitNet Text Generation

For BitNet, you'll need to set up the BitNet inference server separately or use the BitNet repository directly.

## Requirements

- Python 3.11+
- PyTorch
- Ultralytics (for YOLO)
- PIL/Pillow

See `requirements.txt` for full dependency list.

## Notes

- This stage does NOT include:
  - Docker containers
  - FastAPI servers
  - MongoDB/Firebase integration
  - Unified API Gateway

- For containerized deployment, see Stage 2+ branches.
