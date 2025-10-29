# Milo – Nutrition API

FastAPI app that uses YOLOv11 for image recognition and BitNet for text analysis. Stores results in Firebase Firestore.

## Quick Start

```bash
docker-compose up --build
```

API runs at `http://localhost:8000`. API docs at `/docs`.

## Endpoints

All endpoints need auth except `/`.

- `GET /` - health check
- `POST /predict/image` - upload image, get food detection
- `POST /predict/text` - analyze text meal description
- `GET /me` - get current user info
- `GET /history` - get local SQLite history
- `GET /analyses` - get all Firebase analyses
- `GET /analyses/{id}` - get specific analysis
- `PUT /analyses/{id}` - update analysis
- `DELETE /analyses/{id}` - delete analysis

## Authentication

Get a Firebase ID token, then use it in the Authorization header:

```bash
curl http://127.0.0.1:8000/me -H "Authorization: Bearer YOUR_TOKEN"
```

## Architecture

- **Stage 1-3**: YOLO/BitNet inference, Docker, FastAPI
- **Stage 4**: SQLite persistence + `/history` endpoint
- **Stage 5**: Firebase Firestore integration
- **Stage 6**: RabbitMQ worker for async post-processing
- **Stage 7**: Firebase Auth on all endpoints

## Setup

Files you need:
- `firebase-service-account.json` - Firebase credentials
- `docker-compose.yml` - runs API, worker, RabbitMQ
- `app/` - main code and services

Services:
- `milo-api` - FastAPI on port 8000
- `milo-worker` - processes RabbitMQ messages
- `rabbitmq` - message broker (management UI on 15672)
