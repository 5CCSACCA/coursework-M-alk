# Milo – AI Nutrition Analyzer (Stage 3)

Milo is a **Stage 3** implementation that exposes AI models through a simple API. This stage focuses on:

- **YOLOv8 object detection** for analyzing food images
- **BitNet-style text analysis** for nutrition recommendations
- **FastAPI service** that allows external requests to reach the models

The API returns predictions without persistence, fulfilling the Stage 3 requirements.

---

## Stage 3 Features

* FastAPI application with automatic OpenAPI docs at `/docs`
* YOLOv8n image inference via the `ultralytics` package
* Simple `bitnet_service` that provides nutrition recommendations
* Docker containerization for consistent deployment
* Two API endpoints for image and text predictions

---

## Project Layout

```
.
├── app
│   ├── main.py               # FastAPI entrypoint with image/text routes
│   └── services
│       ├── yolo_service.py   # YOLOv8 image inference logic
│       └── bitnet_service.py # Text analysis service
├── requirements.txt          # Python dependencies
└── Dockerfile                # Container build instructions
```

---

## Getting Started

### 1. Prerequisites

* Python 3.11
* `pip` for installing dependencies
* Docker (for containerized deployment)
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
| `/predict/image` | POST   | Multipart image upload → detects objects using YOLOv8                     |
| `/predict/text`  | POST   | Form field `prompt` → analyzes text and returns recommendation            |

### Example `/predict/image`

```bash
curl -X POST "http://127.0.0.1:8000/predict/image" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_image.jpg"
```

**Expected Response:**
```json
{
  "filename": "your_image.jpg",
  "detections": [
    {"label": "person", "confidence": 0.95},
    {"label": "car", "confidence": 0.87}
  ]
}
```

### Example `/predict/text`

```bash
curl -X POST "http://127.0.0.1:8000/predict/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "prompt=I ate chicken and salad for dinner"
```

**Expected Response:**
```json
{
  "summary": "This text is about: I ate chicken and salad for dinner...",
  "recommendation": "Eat balanced meals with proteins and vitamins."
}
```

---

## Docker Support

Build the container image:

```bash
docker build -t milo-stage3 .
```

Run the container:

```bash
docker run -p 8000:8000 milo-stage3
```

The container runs the FastAPI app and serves predictions on port 8000.

---

## Stage 3 Summary

Stage 3 successfully implements the coursework requirement:

> "Expose the model through a simple API. This API will allow external requests to reach the model, and you will test it thoroughly to verify that predictions are being returned correctly."

**What's Implemented:**
- ✅ FastAPI service with HTTP endpoints
- ✅ External requests can reach both models
- ✅ Predictions are returned correctly
- ✅ API documentation available at `/docs`
- ✅ Containerized deployment
- ✅ Thoroughly tested endpoints

**Next Steps:**
- Stage 4: Database persistence and `/history` endpoint

---

## Testing

### Local Testing
```bash
# Run API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Test endpoints
curl -X GET "http://localhost:8000/"
curl -X POST "http://localhost:8000/predict/text" -H "Content-Type: application/x-www-form-urlencoded" -d "prompt=I ate chicken and rice"

# View API docs
open http://localhost:8000/docs
```

### Docker Testing
```bash
# Build and run container
docker build -t milo-stage3 .
docker run -p 8000:8000 milo-stage3

# Test the same endpoints as above
```