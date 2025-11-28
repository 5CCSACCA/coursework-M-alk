# Milo AI - Stage 6: RabbitMQ Post-Processing

## Overview

Stage 6 adds a post-processing service that processes model outputs asynchronously via RabbitMQ message queue. All services run seamlessly with a single Docker Compose command.

## Project Structure

```
coursework-MohamedAlketbi/
├── api-gateway/          # FastAPI Gateway
│   ├── app/
│   │   ├── routes/       # BitNet, YOLO, Database, Firebase routes
│   │   ├── models/       # Request/response models
│   │   ├── services/     # Service clients (including RabbitMQ)
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
├── postprocessing-service/  # Post processing worker (RabbitMQ consumer)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       └── consumer.py
├── database/             # MongoDB & Firebase services
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── mongo_service.py
│   └── firebase_service.py
├── docker-compose.yml    # Orchestrates all services (includes RabbitMQ)
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


### 3. Build and Start All Services

```bash
docker-compose build
docker-compose up
```

This single command starts all services:
- **MongoDB** (port 27017) - Request logging
- **RabbitMQ** (ports 5672, 15672) - Message queue
- **BitNet Service** (port 8080) - Text generation
- **YOLO Service** (port 8001) - Object detection
- **Firebase Service** (port 8002) - CRUD operations
- **Post-Processing Service** - Processes outputs from queue
- **API Gateway** (port 8000) - Unified API endpoint

### 4. Verify Services

```bash
docker-compose ps
```

## How It Works

1. **API Gateway** receives requests and processes them (BitNet/YOLO)
2. **Outputs are stored** in MongoDB (logging) and Firebase (CRUD)
3. **Messages are published** to RabbitMQ queue
4. **Post-Processing Service** consumes messages and processes outputs:
   - BitNet: word count, character count, content analysis
   - YOLO: detection count, unique labels extraction
5. All services communicate via Docker network

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
```

## RabbitMQ Management

Access RabbitMQ management UI:
- URL: http://localhost:15672
- Default credentials: `guest` / `guest`

View queues, messages, and connections.

## Testing the Setup

```bash
# Check all services
docker-compose ps

# Test health
curl http://localhost:8000/health

# Test BitNet (triggers post-processing)
curl -X POST http://localhost:8000/bitnet/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "n_predict": 50}'

# Check post-processing logs
docker-compose logs postprocessing-service
```

## Stopping Services

```bash
docker-compose down
```
