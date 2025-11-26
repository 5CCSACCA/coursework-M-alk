# Stage Files Organization Guide

This document lists all files needed for each stage of the project. Use this as a reference when creating branch-specific versions of the codebase.

---

## Stage 1: Local Inference

**Purpose**: Run BitNet and YOLO models locally without containers or API.

### Core Files Required:

```
services/
├── yolo/
│   ├── yolo_service.py          # YOLO detection logic
│   └── yolo11n.pt               # YOLO model file
│
bitnet-service/
├── model/
│   └── ggml-model-i2_s.gguf    # BitNet model (or BitNet repo setup)
│
requirements.txt                 # Python dependencies for local execution
.gitignore
README.md                        # Stage 1 specific README
```

### Optional Files:
- `tests/test_unified_api.py` (if you want basic tests)
- `scripts/start_api.sh` (for local BitNet server startup)

### Files to EXCLUDE:
- All Docker files (`Dockerfile`, `docker-compose.yml`)
- `api-gateway/` directory
- `yolo-service/` directory
- `firebase-service/` directory
- `firebase-key.json`
- `services/database/` (MongoDB/Firebase)
- Any API routes or FastAPI code

---

## Stage 2: Containerization

**Purpose**: Containerize BitNet and YOLO services using Docker.

### Core Files Required:

```
bitnet-service/
├── Dockerfile                   # BitNet container definition
├── model/
│   └── ggml-model-i2_s.gguf    # BitNet model
│
yolo-service/
├── Dockerfile                   # YOLO container definition
├── app/
│   ├── __init__.py
│   ├── yolo_service.py          # YOLO detection logic
│   └── yolo_server.py           # FastAPI server for YOLO
├── model/
│   └── yolo11n.pt               # YOLO model
└── requirements.txt             # YOLO service dependencies

docker-compose.yml               # Orchestration (basic version with bitnet + yolo only)

.gitignore
README.md                        # Stage 2 specific README
```

### Optional Files:
- `tests/test_unified_api.py` (for testing containerized services)
- `scripts/test_docker.sh`

### Files to EXCLUDE:
- `api-gateway/` directory
- `firebase-service/` directory
- `firebase-key.json`
- `services/database/` (MongoDB/Firebase)
- Unified API routes

---

## Stage 3: Unified API (FastAPI Gateway)

**Purpose**: Create a unified FastAPI API Gateway that routes to BitNet and YOLO services.

### Core Files Required:

```
api-gateway/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── bitnet_models.py     # BitNet request/response models
│   │   └── health_models.py     # Health check models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── bitnet.py            # BitNet endpoints
│   │   ├── yolo.py              # YOLO endpoints
│   │   └── health.py            # Health check endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bitnet_client.py     # BitNet service client
│   │   └── yolo_client.py       # YOLO service client
│   └── utils/
│       ├── __init__.py
│       └── response_utils.py    # Response cleaning utilities
├── Dockerfile
└── requirements.txt

bitnet-service/
├── Dockerfile
├── model/
│   └── ggml-model-i2_s.gguf
│
yolo-service/
├── Dockerfile
├── app/
│   ├── yolo_service.py
│   └── yolo_server.py
├── model/
│   └── yolo11n.pt
└── requirements.txt

docker-compose.yml               # Updated with api-gateway service

.gitignore
README.md                        # Stage 3 specific README
```

### Optional Files:
- `tests/test_unified_api.py`
- `scripts/start_api.sh`

### Files to EXCLUDE:
- `firebase-service/` directory
- `firebase-key.json`
- `services/database/` (MongoDB/Firebase)
- Database/Firebase routes

---

## Stage 4: MongoDB Integration (Request Logging)

**Purpose**: Log all API requests to MongoDB Atlas.

### Core Files Required:

```
api-gateway/
├── app/
│   ├── main.py
│   ├── models/
│   │   ├── bitnet_models.py
│   │   └── health_models.py
│   ├── routes/
│   │   ├── bitnet.py            # Updated: logs requests to MongoDB
│   │   ├── yolo.py              # Updated: logs requests to MongoDB
│   │   ├── database.py          # NEW: MongoDB request history endpoints
│   │   └── health.py            # Updated: includes MongoDB status
│   ├── services/
│   │   ├── bitnet_client.py
│   │   ├── yolo_client.py
│   │   └── database_client.py   # NEW: MongoDB client wrapper
│   └── utils/
│       └── response_utils.py
├── Dockerfile                   # Updated: includes MongoDB connection
└── requirements.txt             # Updated: includes pymongo

services/
└── database/
    ├── __init__.py
    └── mongo_service.py         # NEW: MongoDB service implementation

bitnet-service/
├── Dockerfile
└── model/
    └── ggml-model-i2_s.gguf

yolo-service/
├── Dockerfile
├── app/
│   └── yolo_server.py
├── model/
│   └── yolo11n.pt
└── requirements.txt

docker-compose.yml               # Updated: MongoDB env vars in api-gateway

.gitignore
README.md                        # Stage 4 specific README
```

### Optional Files:
- `tests/test_stage4.py` (MongoDB integration tests)

### Files to EXCLUDE:
- `firebase-service/` directory
- `firebase-key.json`
- `services/database/firebase_service.py`
- Firebase routes (`api-gateway/app/routes/firebase.py`)

---

## Stage 5: Firebase Integration (CRUD Operations)

**Purpose**: Store model outputs in Firebase with full CRUD operations.

### Core Files Required:

```
api-gateway/
├── app/
│   ├── main.py
│   ├── models/
│   │   ├── bitnet_models.py
│   │   ├── firebase_models.py   # NEW: Firebase request models
│   │   └── health_models.py     # Updated: includes Firebase status
│   ├── routes/
│   │   ├── bitnet.py            # Updated: stores outputs to Firebase
│   │   ├── yolo.py              # Updated: stores outputs to Firebase
│   │   ├── database.py          # MongoDB request history
│   │   ├── firebase.py          # NEW: Firebase CRUD endpoints
│   │   └── health.py            # Updated: includes Firebase status
│   ├── services/
│   │   ├── bitnet_client.py
│   │   ├── yolo_client.py
│   │   ├── database_client.py
│   │   └── firebase_client.py   # NEW: Firebase client wrapper
│   └── utils/
│       └── response_utils.py
├── Dockerfile                   # Updated: includes Firebase credentials
└── requirements.txt

firebase-service/                # NEW: Firebase microservice
├── app/
│   ├── __init__.py
│   └── firebase_server.py       # FastAPI server for Firebase CRUD
├── Dockerfile
└── requirements.txt

services/
└── database/
    ├── __init__.py
    ├── mongo_service.py
    └── firebase_service.py      # NEW: Firebase service implementation

bitnet-service/
├── Dockerfile
└── model/
    └── ggml-model-i2_s.gguf

yolo-service/
├── Dockerfile
├── app/
│   └── yolo_server.py
├── model/
│   └── yolo11n.pt
└── requirements.txt

docker-compose.yml               # Updated: includes firebase-service

firebase-key.json                # NEW: Firebase service account credentials

.gitignore                       # Updated: includes firebase-key.json
README.md                        # Stage 5 specific README
```

### Optional Files:
- `tests/test_stage5.py` (Firebase CRUD tests)
- `tests/test_unified_api.py`
- `tests/test_stage4.py`

---

## Common Files (All Stages)

These files should be present in all stages:

```
.gitignore
README.md                        # Stage-specific content
```

---

## Test Files by Stage

### Stage 1:
- None or basic local tests

### Stage 2:
- `tests/test_unified_api.py` (testing containerized services)

### Stage 3:
- `tests/test_unified_api.py`

### Stage 4:
- `tests/test_unified_api.py`
- `tests/test_stage4.py` (MongoDB tests)
- `tests/test_image.jpeg`

### Stage 5:
- `tests/test_unified_api.py`
- `tests/test_stage4.py`
- `tests/test_stage5.py` (Firebase tests)
- `tests/test_image.jpeg`

---

## Scripts by Stage

### Stage 1:
- `scripts/start_api.sh` (optional - for local BitNet server)

### Stage 2:
- `scripts/test_docker.sh`

### Stage 3+:
- `scripts/test_docker.sh`
- `scripts/start_api.sh`
- `scripts/run_tests.sh`

---

## Creating Stage-Specific Branches

### Step-by-Step Process:

1. **Create a new branch for each stage:**
   ```bash
   git checkout -b stage1-local-inference
   git checkout -b stage2-containerization
   git checkout -b stage3-unified-api
   git checkout -b stage4-mongodb
   git checkout -b stage5-firebase
   ```

2. **For each branch, remove unnecessary files:**
   ```bash
   # Example for Stage 1:
   git rm -r api-gateway/ firebase-service/ yolo-service/
   git rm docker-compose.yml
   git rm firebase-key.json
   git rm services/database/
   ```

3. **Update README.md** for each stage with stage-specific instructions

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "refactor: organize files for Stage X"
   ```

---

## Quick Reference Table

| Component | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 |
|-----------|---------|---------|---------|---------|---------|
| **BitNet Local** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **BitNet Docker** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **YOLO Local** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **YOLO Docker** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **API Gateway** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **MongoDB** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Firebase** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Docker Compose** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Test Files** | Optional | Optional | ✅ | ✅ | ✅ |

### Directory Inclusion Matrix

| Directory | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Stage 5 |
|-----------|---------|---------|---------|---------|---------|
| `bitnet-service/` | ❌ | ✅ | ✅ | ✅ | ✅ |
| `yolo-service/` | ❌ | ✅ | ✅ | ✅ | ✅ |
| `api-gateway/` | ❌ | ❌ | ✅ | ✅ | ✅ |
| `firebase-service/` | ❌ | ❌ | ❌ | ❌ | ✅ |
| `services/yolo/` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `services/database/mongo_service.py` | ❌ | ❌ | ❌ | ✅ | ✅ |
| `services/database/firebase_service.py` | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Notes

- **Shared Services**: The `services/` directory is shared across stages, so only include what's needed for each stage.
- **Docker Compose**: Each stage will have a different `docker-compose.yml` with only the relevant services.
- **Dependencies**: Update `requirements.txt` files to only include dependencies needed for that stage.
- **Tests**: Keep only relevant test files for each stage.
- **Scripts**: Keep only scripts that are useful for that stage.
- **Models**: Model files (`.gguf`, `.pt`) should be in `.gitignore` but structure should be maintained.

---

## Branch Creation Script Example

```bash
#!/bin/bash
# create-stage-branches.sh

# Stage 1: Local Inference
git checkout -b stage1-local-inference main
# Remove unnecessary files
git rm -r api-gateway/ firebase-service/ yolo-service/ bitnet-service/
git rm docker-compose.yml firebase-key.json
git rm -r services/database/
git commit -m "refactor: organize for Stage 1 - local inference"

# Stage 2: Containerization
git checkout -b stage2-containerization main
git rm -r api-gateway/ firebase-service/
git rm firebase-key.json
git rm -r services/database/
git commit -m "refactor: organize for Stage 2 - containerization"

# Stage 3: Unified API
git checkout -b stage3-unified-api main
git rm -r firebase-service/
git rm firebase-key.json
git rm -r services/database/
git commit -m "refactor: organize for Stage 3 - unified API"

# Stage 4: MongoDB
git checkout -b stage4-mongodb main
git rm -r firebase-service/
git rm firebase-key.json
git rm services/database/firebase_service.py
git commit -m "refactor: organize for Stage 4 - MongoDB integration"

# Stage 5: Firebase (current main/master)
git checkout main
# Already has all files

echo "✅ All stage branches created!"
```

