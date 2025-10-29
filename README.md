# Milo – AI Nutrition Analyzer 

Milo is a lightweight **FastAPI** service that combines **YOLOv11 object detection** and a **language-model-style text analyzer** for "what's on my plate?" nutrition projects.
Users can upload an image *or* enter a text description of a meal, and the service returns AI-generated detections or recommendations.
All interactions are **persisted in Firebase Firestore** with full CRUD capabilities for managing analysis data.

---

## Features

* FastAPI application with automatic OpenAPI docs at `/docs`
* YOLOv11n image inference via the `ultralytics` package
* BitNet model integration for text analysis
* **Firebase Firestore** for cloud storage and data management
* Full CRUD API endpoints for analysis management
* Docker image for consistent deployment

---

## Project Layout

```
.
├── app/
│   ├── main.py               # FastAPI entrypoint with CRUD endpoints
│   └── services/
│       ├── yolo_service.py      # YOLOv11 image inference logic
│       ├── bitnet_service.py    # BitNet text analysis 
│       └── firebase_service.py   # Firebase Firestore operations
├── requirements.txt              # Python dependencies
├── firebase-service-account.json  # Firebase credentials
├── docker-compose.yml             # Docker Compose config
├── Dockerfile                    # Container build instructions
└── .gitignore                   # Git ignore rules
```

---

## Getting Started

### 1. Prerequisites

* Python 3.11
* `pip` for installing dependencies
* (Optional) virtual environment

  ```bash
  python -m venv .venv && source .venv/bin/activate
  ```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> The first run of the YOLO model will download small weights (~6 MB).
> Make sure you have network access the first time you start the service.

### 3. Run the API Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

---

## API Usage

| Endpoint                    | Method | Description                                                                |
| --------------------------- | ------ | -------------------------------------------------------------------------- |
| `/`                         | GET    | Health-check message                                                       |
| `/predict/image`            | POST   | Multipart image upload → detects food items using YOLOv11 and saves to Firebase |
| `/predict/text`             | POST   | Form field `prompt` → analyzes text and saves to Firebase                  |
| `/analyses`                 | GET    | Get all analyses from Firebase                                             |
| `/analyses/{id}`            | GET    | Get specific analysis by ID                                                |
| `/analyses/{id}`            | PUT    | Update analysis in Firebase                                                |
| `/analyses/{id}`            | DELETE | Delete analysis from Firebase                                              |
| `/analyses/type/{type}`     | GET    | Get analyses filtered by type (image or text)                              |

### Example `/predict/image`

```bash
curl -X POST "http://127.0.0.1:8000/predict/image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/plate.jpg"
```

### Example `/predict/text`

```bash
curl -X POST "http://127.0.0.1:8000/predict/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "prompt=I ate chicken and salad for dinner"
```

### Example `/analyses` response

```json
{
  "analyses": [
    {
      "id": "abc123",
      "analysis_type": "text",
      "filename": "prompt_input",
      "data": {
        "summary": "BitNet analysis: This meal contains...",
        "recommendation": "Great choice! Continue with balanced meals...",
        "sentiment": "POSITIVE",
        "confidence": 0.95,
        "detected_foods": ["chicken", "salad"]
      },
      "prompt": "I ate chicken and salad for dinner",
      "timestamp": "2025-10-27T22:55:31.200027",
      "created_at": "2025-10-27T22:55:31.200Z"
    }
  ]
}
```

### Example CRUD Operations

**Get specific analysis:**
```bash
curl -X GET "http://127.0.0.1:8000/analyses/abc123"
```

**Update analysis:**
```bash
curl -X PUT "http://127.0.0.1:8000/analyses/abc123" \
  -H "Content-Type: application/json" \
  -d '{"data": {"summary": "Updated analysis"}}'
```

**Delete analysis:**
```bash
curl -X DELETE "http://127.0.0.1:8000/analyses/abc123"
```

**Get analyses by type:**
```bash
curl -X GET "http://127.0.0.1:8000/analyses/type/image"
```

---

## Docker Support

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```

This will build and run the service with proper volume mounting and health checks.

### Option 2: Manual Docker

Build the container image:

```bash
docker build -t milo-service .
```

Run the container:

```bash
docker run -p 8000:8000 milo-service
```

The container runs the same FastAPI app and persists the `detections.db` file inside the container (or a mounted volume if configured).

---

## Stage 5 Summary

Stage 5 extends storage capabilities by integrating **Firebase Firestore** for cloud-based data management:

