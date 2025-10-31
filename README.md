# Milo – Nutrition API
Mohamed Ali Khalifa Alketbi
K22056537
https://github.com/5CCSACCA/coursework-M-alk.git


FastAPI app that uses YOLOv11 for image recognition and BitNet for text analysis. Stores results in Firebase Firestore.

## Quick Start

```bash
docker-compose up --build
```

API runs at `http://localhost:8000`. API docs at `/docs`.

## Endpoints

All endpoints are public (no authentication required).

- `GET /` - health check
- `POST /predict/image` - upload image, get food detection
- `POST /predict/text` - analyze text meal description
- `GET /history` - get local SQLite history
- `GET /analyses` - get all Firebase analyses
- `GET /analyses/{id}` - get specific analysis
- `PUT /analyses/{id}` - update analysis
- `DELETE /analyses/{id}` - delete analysis
- `GET /stats` - simple stats (total analyses count)

### Example Usage

```bash
# Health check
curl http://localhost:8000/

# Analyze text
curl -X POST http://localhost:8000/predict/text -F "prompt=I ate salad and chicken"

# Upload image
curl -X POST http://localhost:8000/predict/image -F "file=@meal.jpg"

# Get history
curl http://localhost:8000/history

# Get stats
curl http://localhost:8000/stats
```

## Architecture

- **Stage 1-3**: YOLO/BitNet inference, Docker, FastAPI
- **Stage 4**: SQLite persistence + `/history` endpoint
- **Stage 5**: Firebase Firestore integration
- **Stage 6**: RabbitMQ worker for async post-processing

- **Stage 7**: User authentication (still not implemented)

## Setup

Files you need:
- `firebase-service-account.json` - Firebase credentials
- `docker-compose.yml` - runs API, worker, RabbitMQ
- `app/` - main code and services

Env quickstart (create a `.env` or export vars):

```bash
export FIREBASE_PROJECT_ID=milo-xxxxx
export RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
export QUEUE_NAME=postprocess
```

Services:
- `milo-api` - FastAPI on port 8000
- `milo-worker` - processes RabbitMQ messages
- `rabbitmq` - message broker (management UI on 15672)

## Run tests

```bash
# Inside container
docker-compose exec milo-api python -m pytest -q

# Or locally (need Python 3.11)
pytest -q
```

## Notes

- All API endpoints are open (Stage 7 authentication not implemented)
- Uses SQLite for local persistence and Firebase Firestore for cloud storage
- RabbitMQ handles async post-processing between services
- Test coverage includes predict endpoints and history.
