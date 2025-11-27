# Milo AI - Stage 5: Firebase Integration (CRUD)

## Overview

Stage 5 extends storage capabilities by integrating Firebase. Model outputs are stored in Firebase with full CRUD operations (Create, Read, Update, Delete).

## Project Structure

```
coursework-MohamedAlketbi/
├── api-gateway/          # FastAPI Gateway
│   ├── app/
│   │   ├── routes/       # BitNet, YOLO, Database, Firebase routes
│   │   ├── models/       # Request/response models
│   │   ├── services/     # Service clients
│   │   └── utils/        # Utility functions
│   ├── Dockerfile
│   └── requirements.txt
├── bitnet-service/       # BitNet microservice
│   ├── Dockerfile
│   └── model/
├── yolo-service/         # YOLO microservice
│   ├── Dockerfile
│   └── requirements.txt
├── firebase-service/     # Firebase microservice
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── database/             # MongoDB & Firebase services
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── mongo_service.py
│   └── firebase_service.py
├── docker-compose.yml
└── README.md
```

## Setup Instructions (Linux VM)

### 1. Clone the Repository

```bash
git clone https://github.com/5CCSACCA/coursework-M-alk.git
cd coursework-MohamedAlketbi
```

### 2. Download the BitNet Model

```bash
cd bitnet-service/model
wget https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-gguf/resolve/main/ggml-model-i2_s.gguf
cd ../..
```

### 3. Build and Start Services

```bash
docker-compose build
docker-compose up
```

This will start all services:
- **MongoDB** (port 27017) - Local database for request logging
- **BitNet Service** (port 8080) - Text generation model
- **YOLO Service** (port 8001) - Object detection model
- **Firebase Service** (port 8002) - Firebase CRUD operations
- **API Gateway** (port 8000) - Unified API endpoint

### 4. Verify Services

```bash
docker-compose ps
```

## API Usage

### BitNet Text Generation

```bash
curl -X POST http://localhost:8000/bitnet/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Is Banana Healthy?", "n_predict": 50}'
```

### YOLO Object Detection

```bash
curl -X POST http://localhost:8000/yolo/detect \
  -F "file=@tests/test_image.jpeg"
```

### MongoDB Request History

```bash
curl http://localhost:8000/requests
```

### Firebase CRUD Operations

```bash
# Get all outputs
curl http://localhost:8000/firebase/outputs

# Get outputs by service
curl http://localhost:8000/firebase/outputs?service=bitnet
curl http://localhost:8000/firebase/outputs?service=yolo

# Get specific output
curl http://localhost:8000/firebase/outputs/{output_id}

# Update output
curl -X PUT http://localhost:8000/firebase/outputs/{output_id} \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"updated": true}}'

# Delete output
curl -X DELETE http://localhost:8000/firebase/outputs/{output_id}
```

## Testing the Setup

```bash
# Check all services are running
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health

# Test BitNet
curl -X POST http://localhost:8000/bitnet/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "n_predict": 50}'

# Test YOLO
curl -X POST http://localhost:8000/yolo/detect \
  -F "file=@tests/test_image.jpeg"

# Check MongoDB logs
curl http://localhost:8000/requests

# Check Firebase outputs
curl http://localhost:8000/firebase/outputs
```

## Stopping Services

```bash
docker-compose down
```
