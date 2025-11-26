# Milo AI 

## Overview

This project sets up microservices using Docker Compose:

**BitNet Service** - Runs BitNet LLM model, exposes port 8080  
**YOLO Service** - Object detection, exposes port 8001  
**Firebase Service** - CRUD operations, exposes port 8002  
**API Gateway** - Unified FastAPI gateway, exposes port 8000

## Project Structure

```
coursework-MohamedAlketbi/
├── api-gateway/          # FastAPI gateway
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── bitnet-service/       # BitNet microservice
│   ├── model/
│   └── Dockerfile
├── yolo-service/         # YOLO microservice
│   ├── app/
│   ├── model/
│   └── Dockerfile
├── firebase-service/     # Firebase microservice
│   ├── app/
│   └── Dockerfile
└── docker-compose.yml
```

## Setup Instructions

### 1. Download the BitNet Model

```bash
cd bitnet-service/model
wget https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-gguf/resolve/main/ggml-model-i2_s.gguf
```

### 2. Build and Start Services

```bash
docker-compose build
docker-compose up
```

### 3. Access Services
- Main http://localhost:8000/docs
- API Gateway: http://localhost:8000
- BitNet: http://localhost:8080
- YOLO: http://localhost:8001
- Firebase: http://localhost:8002

## API Usage

### BitNet Text Generation

```bash
curl -X POST http://localhost:8000/bitnet/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "n_predict": 50}'
```

### YOLO Object Detection

```bash
curl -X POST http://localhost:8000/yolo/detect \
  -F "file=@test_image.jpeg"
```

### Get Request History

```bash
curl http://localhost:8000/requests
```

### Firebase Outputs

```bash
curl http://localhost:8000/firebase/outputs
```

## How It Works

The API Gateway routes requests to microservices:
- BitNet → `http://bitnet-service:8080/completion`
- YOLO → `http://yolo-service:8001/detect`
- Firebase → `http://firebase-service:8002/outputs`

Services communicate via Docker network (`milo-network`).

## Stopping Services

```bash
docker-compose down
```
