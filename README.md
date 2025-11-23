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

## Stage 4: MongoDB Persistence

**Goal:** Store all requests in MongoDB and provide endpoints to retrieve past interactions.

### MongoDB Setup

The system uses MongoDB Atlas for cloud database storage. Connection details are configured via environment variables:

```bash
# MongoDB connection string (default provided)
export MONGO_URI="mongodb+srv://milo_user:strongpassword123@cluster0.o4dzo0k.mongodb.net/?appName=Cluster0"
```

### Features

1. **Automatic Request Logging**
   - Every BitNet and YOLO request is logged to MongoDB
   - Stores request data, response data, timestamp, and status
   - Non-blocking (failures don't affect API response)

2. **Request Retrieval Endpoints**
   - Get all requests (with pagination)
   - Filter by service (bitnet or yolo)
   - Retrieve specific request by ID

3. **Database Statistics**
   - Health endpoint shows DB connection status
   - Total request counts per service

### New Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/requests` | Get all past requests (paginated) |
| GET | `/requests?service=bitnet` | Filter requests by service |
| GET | `/requests/{id}` | Get specific request by ID |

### Query Parameters

- `service` (optional): Filter by "bitnet" or "yolo"
- `limit` (default 50): Max results per page
- `skip` (default 0): Skip N results (pagination)

### Test Stage 4

```bash
# Start API with database support
bash scripts/start_api.sh

# Run Stage 4 tests
python3 tests/test_stage4.py
```

### Example Usage

**Get all requests:**
```bash
curl http://localhost:8000/requests?limit=10
```

**Get BitNet requests only:**
```bash
curl http://localhost:8000/requests?service=bitnet&limit=5
```

**Get specific request:**
```bash
curl http://localhost:8000/requests/6745abc123def456789
```

**Check database stats:**
```bash
curl http://localhost:8000/health | jq '.database_stats'
```

### Example Response

```json
{
  "total": 2,
  "service_filter": "bitnet",
  "limit": 10,
  "skip": 0,
  "requests": [
    {
      "_id": "6745abc123def456789",
      "service": "bitnet",
      "timestamp": "2024-11-23T10:30:45.123456",
      "request": {
        "prompt": "What is AI?",
        "n_predict": 30
      },
      "response": {
        "content": "AI is artificial intelligence...",
        "tokens_predicted": 28
      },
      "status": "success"
    }
  ]
}
```

### Database Schema

**Collection:** `requests`

**Document Structure:**
```javascript
{
  _id: ObjectId,
  service: "bitnet" | "yolo",
  timestamp: ISODate,
  request: Object,      // Original request data
  response: Object,     // Model response data
  status: "success" | "error"
}
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
│   ├── bitnet/
│   │   └── bitnet_service.py   # BitNet client
│   └── database/
│       ├── __init__.py
│       └── mongo_service.py    # MongoDB operations
├── tests/
│   ├── test_stage1.py          # Stage 1 tests
│   ├── test_stage3.py          # API tests
│   ├── test_stage4.py          # Database tests
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
- `pymongo` - MongoDB database driver
- `requests` - HTTP client for BitNet
- `pillow`, `opencv-python-headless` - Image processing

Install all:
```bash
pip install -r requirements.txt
```

---

## Notes

- **CPU Only:** Designed for 4 vCPU, 16GB RAM (no GPU required)
- **BitNet Server:** Must be running for Stages 1-4 (`bash scripts/start_bitnet_server.sh`)
- **Mock Mode:** API supports lightweight mock (default) or real BitNet (`BITNET_MOCK=0`)
- **Model Size:** BitNet model is 1.1GB (not included in Docker image to keep it light)
- **Database:** MongoDB Atlas cloud database for request persistence (Stage 4+)
- **Non-blocking:** Database failures don't affect API responses
