# Milo – AI Nutrition Analyzer

Milo is a lightweight **FastAPI** service that combines **YOLOv8 object detection** and a **language-model-style text analyzer** for “what’s on my plate?” nutrition projects.
Users can upload an image *or* enter a text description of a meal, and the service returns AI-generated detections or recommendations.
All interactions are **persisted in an SQLite database** so that past analyses can be retrieved later.

---

## Features

* FastAPI application with automatic OpenAPI docs at `/docs`
* YOLOv8n image inference via the `ultralytics` package
* Simple `bitnet_service` with real transformer-based text analysis
* **SQLite persistence layer** that records every `/predict` request
* `/history` endpoint to retrieve previous image and text analyses
* Docker image for consistent deployment

---

## Project Layout

```
.
├── app
│   ├── main.py               # FastAPI entrypoint with image/text routes and /history
│   └── services
│       ├── yolo_service.py   # YOLOv8 image inference logic
│       ├── bitnet_service.py # Transformer-based text analysis service
│       └── database.py       # SQLite persistence functions
├── requirements.txt          # Python dependencies
└── Dockerfile                # Container build instructions
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

| Endpoint         | Method | Description                                                                |
| ---------------- | ------ | -------------------------------------------------------------------------- |
| `/`              | GET    | Health-check message                                                       |
| `/predict/image` | POST   | Multipart image upload → detects food items using YOLOv8 and saves results |
| `/predict/text`  | POST   | Form field `prompt` → analyzes text and saves recommendation               |
| `/history`       | GET    | Returns persisted records of all previous image + text analyses            |

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

### Example `/history` response

```json
{
  "history": [
    {
      "id": 4,
      "type": "text",
      "filename": "prompt_input",
      "detections": {
        "summary": "This text is about: I ate chicken and salad for dinner...",
        "recommendation": "Eat balanced meals with proteins and vitamins."
      },
      "prompt": "I ate chicken and salad for dinner",
      "timestamp": "2025-10-26T20:55:31.200027"
    }
  ]
}
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

## Stage 4 Summary

Stage 4 added the **persistence layer** and **GET /history endpoint**, fulfilling the coursework goal:

> “Add persistence by setting up a database that records all incoming requests and implement a GET endpoint to retrieve past interactions.”

