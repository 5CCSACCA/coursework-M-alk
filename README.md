# Milo AI Prediction Model

**Student:** Mohamed Ali Khalifa Alketbi  
**ID:** K22056537  
**Repository:** https://github.com/5CCSACCA/coursework-M-alk.git

## Overview

This project implements Stage 1 and Stage 2. Stage 1 has two models working together - YOLO for object detection and BitNet for text analysis. Both use default parameters.

## Models

- **YOLO (YOLOv11n)**: Detects objects in images
- **BitNet (Microsoft BitNet-b1.58-2B-4T)**: Text generation via HTTP API

## Project Structure

```
services/
├── yolo/
│   ├── yolo_service.py
│   └── yolo11n.pt
└── bitnet/
    └── bitnet_service.py

tests/
└── test_stage1.py

scripts/
├── start_bitnet_server.sh
├── deploy.sh
└── test_docker.sh

BitNet/              
├── models/
└── run_inference_server.py
```

## Stage 1

### YOLO Service

The YOLO service loads the model and processes image bytes:

```python
from ultralytics import YOLO
model = YOLO("yolo11n.pt")

def detect_objects(image_bytes: bytes):
    # Returns detections with labels and confidence scores
```

Input: Raw image bytes (JPEG, PNG, etc.)  
Output: JSON with detections list and total count

Example output:
```json
{
  "detections": [
    {"label": "apple", "confidence": 0.712},
    {"label": "orange", "confidence": 0.630},
    {"label": "banana", "confidence": 0.536}
  ],
  "total_objects": 3
}
```

### BitNet Service

BitNet connects to a server running on localhost:8080. The service sends prompts and gets text responses:

```python
def analyze_text(prompt: str):
    # Sends POST request to BitNet server
    # Returns input, output, and model name
```

Input: Text string  
Output: JSON with input prompt, generated text, and model identifier

Example:
```
Input: "Are apples healthy foods?"
Output: "Apples are generally considered healthy."
```

The service truncates output at sentence boundaries to avoid mid-sentence cuts.

### Running Stage 1

```bash
# Start BitNet server first
bash scripts/start_bitnet_server.sh

# Then run the test
source venv/bin/activate
python tests/test_stage1.py
```

The test script runs YOLO detection on an image, extracts food labels, then asks BitNet about their health impact.

Performance: YOLO takes ~60-80ms, BitNet takes ~3-4s per query.

## Stage 2

Stage 2 containerizes the Python code. The Dockerfile packages YOLO service and BitNet client. BitNet server runs on the host using Python.

The container uses `--network=host` so it can access localhost:8080 where the BitNet server runs. This works on Linux without any special host networking setup.

### Prerequisites

Start the BitNet server before running the container:

```bash
bash scripts/start_bitnet_server.sh
```

### Build

```bash
docker build -t milo-ai:stage2 .
```

### Run

```bash
docker run --rm --network=host -e BITNET_URL=http://localhost:8080/completion milo-ai:stage2
```

Or use docker-compose:

```bash
docker-compose up --build
```

Or use the deploy script:

```bash
bash scripts/deploy.sh
```


## Dependencies

See `requirements.txt` for Python packages. Main ones:
- ultralytics (YOLO)
- torch, torchvision
- requests (BitNet client)
- pillow, opencv-python-headless

## Notes

- BitNet server must be running before Stage 1 or Stage 2 tests
- The system is designed for 4 vCPU and 16GB RAM constraints
- BitNet model needs to be downloaded separately (see BitNet/ directory)
