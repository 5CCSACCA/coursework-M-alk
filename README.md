# Milo AI - Stage 2: Containerization

## Overview

Stage 2 focuses on containerizing BitNet (Text Generation) and YOLO (Object Detection) services using Docker and Docker Compose.

## Project Structure

```
coursework-MohamedAlketbi/
├── bitnet-service/
│   ├── Dockerfile              # BitNet container definition
│   ├── app/
│   │   └── bitnet_server.py    # BitNet server placeholder
│   └── model/
│       └── ggml-model-i2_s.gguf # BitNet model
├── yolo-service/
│   ├── Dockerfile              # YOLO container definition
│   ├── app/
│   │   ├── yolo_service.py     # YOLO detection logic
│   │   └── yolo_server.py      # FastAPI server for YOLO
│   ├── model/
│   │   └── yolo11n.pt          # YOLO model
│   └── requirements.txt        # YOLO service dependencies
├── docker-compose.yml          # Orchestration (bitnet + yolo only)
├── .gitignore
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
- Build the BitNet image from `bitnet-service/Dockerfile`
- Build the YOLO image from `yolo-service/Dockerfile`
- Start both containers

### 3. Access Services

- **BitNet Service**: http://localhost:8080
- **YOLO Service**: http://localhost:8001

## API Usage

### BitNet Health Check

```bash
curl http://localhost:8080/health
```

### YOLO Object Detection

```bash
curl -X POST http://localhost:8001/detect \
  -F "file=@tests/test_image.jpeg"
```

### YOLO Health Check

```bash
curl http://localhost:8001/health
```

## How It Works

- **BitNet Service**: Runs the BitNet LLM model inside a Docker container, exposing port 8080 for inference requests.
- **YOLO Service**: Runs YOLO object detection inside a Docker container, exposing port 8001 with a FastAPI server.

Both services communicate via Docker's internal network (`milo-network`).

## Stopping Services

```bash
docker-compose down
```
