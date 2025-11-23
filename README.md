# Milo AI - Cloud Computing Coursework

**Student:** Mohamed Ali Khalifa Alketbi  
**ID:** K22056537  
**Repository:** https://github.com/5CCSACCA/coursework-M-alk.git

---

## Overview

Milo AI is a cloud-based SaaS application combining two AI models:
- **YOLO (YOLOv11n)** - Object detection in images
- **BitNet (2B parameters)** - Text generation with LLM

The system exposes both models through a REST API with FastAPI, containerized with Docker, and designed for CPU-only environments (4 cores, 16GB RAM).

---

## Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Start BitNet server (required for all stages)
bash scripts/start_bitnet_server.sh
```

---

## Stage 1: Local Python Inference

**Goal:** Run both models locally with default parameters.

### Run Test
```bash
python3 tests/test_stage1.py
```

### What It Does
1. YOLO detects objects in `test_image.jpeg` (21 objects: apples, oranges, bananas)
2. BitNet answers health questions about detected foods
3. Outputs JSON results with labels, confidence scores, and AI-generated text

### Example Output
```json
{
  "detections": [
    {"label": "apple", "confidence": 0.712},
    {"label": "orange", "confidence": 0.630}
  ],
  "total_objects": 21
}
```

**Performance:** YOLO ~60ms, BitNet ~3-4s per query

---

## Stage 2: Docker Containerization

**Goal:** Package the system in Docker with two-command deployment.

### Two Commands (As Required by Brief)

**1. Build:**
```bash
docker-compose build
```

**2. Run:**
```bash
docker-compose up
```

### What It Does
- Packages YOLO + BitNet client in lightweight container
- Container connects to BitNet server on host (keeps image small ~2GB vs 10GB+)
- Runs the same Stage 1 test inside Docker
- Outputs detection results and AI responses

### Alternative (Direct Docker)
```bash
# Build
docker build -t milo-ai:stage2 -f Dockerfile.yolo .

# Run
docker run --rm --network=host milo-ai:stage2
```

**Note:** BitNet server must be running on host before starting container.

---

## Stage 3: REST API with FastAPI

**Goal:** Expose both models through REST API endpoints.

### Start API
```bash
bash scripts/start_api.sh
```

API available at: `http://localhost:8000`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/yolo/detect` | Upload image for object detection |
| POST | `/bitnet/completion` | Generate text with LLM |
| GET | `/docs` | Interactive API documentation (Swagger UI) |

### Test API

**Interactive (Browser):**
```
http://localhost:8000/docs
```

**Command Line:**
```bash
# Health check
curl http://localhost:8000/health

# YOLO detection
curl -X POST http://localhost:8000/yolo/detect \
  -F "file=@test_image.jpeg"

# BitNet text generation
curl -X POST http://localhost:8000/bitnet/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is AI?", "n_predict": 30}'
```

### Run All Tests
```bash
bash scripts/run_tests.sh
```

---

## Project Structure

```
coursework-MohamedAlketbi/
├── api/
│   └── api.py                  # FastAPI unified server
├── services/
│   ├── yolo/
│   │   ├── yolo_service.py     # YOLO detection
│   │   └── yolo11n.pt          # Model weights (6MB)
│   └── bitnet/
│       └── bitnet_service.py   # BitNet client
├── tests/
│   ├── test_stage1.py          # Stage 1 tests
│   ├── test_stage3.py          # API tests
│   └── test_unified_api.py     # Comprehensive tests
├── scripts/
│   ├── start_api.sh            # Start unified API
│   ├── start_bitnet_server.sh  # Start BitNet server
│   └── run_tests.sh            # Run all tests
├── Dockerfile.yolo             # Container definition
├── docker-compose.yml          # Docker orchestration
├── requirements.txt            # Python dependencies 
├── requirements-docker.txt     # Docker dependencies 
└── README.md
```

---

## Dependencies

**Main packages:**
- `ultralytics` - YOLO object detection
- `torch`, `torchvision` - Deep learning framework
- `fastapi`, `uvicorn` - REST API server
- `requests` - HTTP client for BitNet
- `pillow`, `opencv-python-headless` - Image processing

Install all:
```bash
pip install -r requirements.txt
```

---

## Notes

- **CPU Only:** Designed for 4 vCPU, 16GB RAM (no GPU required)
- **BitNet Server:** Must be running for Stages 1-3 (`bash scripts/start_bitnet_server.sh`)
- **Mock Mode:** API supports lightweight mock (default) or real BitNet (`BITNET_MOCK=0`)
- **Model Size:** BitNet model is 1.1GB (not included in Docker image to keep it light)
