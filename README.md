# Milo AI - Stage 4: MongoDB Integration 

## Overview

Stage 4 adds MongoDB persistence to log all API requests. Users can retrieve their past interactions with the system through GET endpoints.

## Project Structure

```
coursework-MohamedAlketbi/
├── api-gateway/          # FastAPI Gateway
│   ├── app/
│   │   ├── routes/       # BitNet, YOLO, Database routes
│   │   ├── models/       # Request/response models
│   │   ├── services/     # Service clients (including DatabaseClient)
│   │   └── utils/        # Utility functions
│   ├── Dockerfile
│   └── requirements.txt
├── bitnet-service/       # BitNet microservice
│   ├── Dockerfile
│   └── model/
├── yolo-service/         # YOLO microservice
│   ├── Dockerfile
│   └── requirements.txt
├── database/                   # MongoDB 
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── __init__.py
│   └── mongo_service.py
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
- **MongoDB** (port 27017) - Local database running in Docker
- **BitNet Service** (port 8080) - Text generation model
- **YOLO Service** (port 8001) - Object detection model
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



## Testing the Setup

After starting services, verify everything is working:

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

# Check MongoDB logs are being created
curl http://localhost:8000/requests
```

## Stopping Services

```bash
docker-compose down
```
