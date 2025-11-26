# Milo AI - Stage 3: Unified API Gateway

## Overview

Stage 3 creates a unified FastAPI API Gateway that routes requests to BitNet (Text Generation) and YOLO (Object Detection) microservices.

## Project Structure

```
coursework-MohamedAlketbi/
├── api-gateway/           # Unified FastAPI Gateway
│   ├── app/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── models/        # Request/response models
│   │   ├── routes/        # API endpoints (bitnet, yolo, health)
│   │   ├── services/      # Service clients
│   │   └── utils/         # Utility functions
│   ├── Dockerfile
│   └── requirements.txt
├── bitnet-service/        # BitNet microservice
│   ├── Dockerfile
│   └── model/
│       └── ggml-model-i2_s.gguf
├── yolo-service/          # YOLO microservice
│   ├── Dockerfile
│   ├── app/
│   │   ├── yolo_service.py
│   │   └── yolo_server.py
│   ├── model/
│   │   └── yolo11n.pt
│   └── requirements.txt
├── docker-compose.yml
└── README.md
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

This will:
- Build the BitNet image
- Build the YOLO image
- Build the API Gateway image
- Start all containers

### 3. Access Services

- **API Gateway**: http://localhost:8000/docs (Interactive API docs)
- **BitNet Service**: http://localhost:8080
- **YOLO Service**: http://localhost:8001

## API Usage

### BitNet Text Generation

```bash
curl -X POST http://localhost:8000/bitnet/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?", "n_predict": 50}'
```

### YOLO Object Detection

```bash
curl -X POST http://localhost:8000/yolo/detect \
  -F "file=@tests/test_image.jpeg"
```

### Health Check

```bash
curl http://localhost:8000/health
```

## How It Works

The API Gateway acts as a unified entry point:

1. **BitNet requests** → Gateway routes to `http://bitnet-service:8080/completion`
2. **YOLO requests** → Gateway routes to `http://yolo-service:8001/detect`
3. All services communicate via Docker's internal network (`milo-network`)

The Gateway provides:
- Unified API interface
- Request/response validation
- Error handling
- Health monitoring

## Stopping Services

```bash
docker-compose down
```

- For database integration, see Stage 4+ branches.
