import os
import requests
import logging
from fastapi import APIRouter
from ..models import HealthResponse
from ..services import BitNetClient, DatabaseClient, FirebaseClient, RabbitMQClient

router = APIRouter()
logger = logging.getLogger(__name__)

bitnet_client = BitNetClient()
YOLO_SERVICE_URL = os.getenv("YOLO_SERVICE_URL", "http://yolo-service:8001")
FIREBASE_SERVICE_URL = os.getenv("FIREBASE_SERVICE_URL", "http://firebase-service:8002")
db_client = DatabaseClient()
firebase_client = FirebaseClient()
rabbitmq_client = RabbitMQClient()


@router.get("/", response_model=dict, status_code=200)
async def root():
    return {
        "service": "Milo AI ",
        "version": "1.0",
        "framework": "FastAPI",
        "endpoints": {
            "POST /bitnet/completion": "Generate text completion (BitNet)",
            "POST /yolo/detect": "Detect objects in image (YOLO)",
            "GET /health": "Check service health",
            "GET /requests": "Get request history (MongoDB)",
            "GET /requests/{id}": "Get specific request (MongoDB)",
            "POST /firebase/outputs": "Create model output (Firebase)",
            "GET /firebase/outputs": "Get model outputs (Firebase)",
            "GET /firebase/outputs/{id}": "Get specific output (Firebase)",
            "PUT /firebase/outputs/{id}": "Update output (Firebase)",
            "DELETE /firebase/outputs/{id}": "Delete output (Firebase)",
            "GET /docs": "Interactive API documentation"
        },
        "storage": {
            "mongodb": "Request logging and history",
            "firebase": "Model outputs with CRUD operations"
        },
        "messaging": {
            "rabbitmq": "Message queue for post-processing",
            "postprocessing": "Async output processing service"
        },
        "models": {
            "bitnet": "BitNet-b1.58-2B-4T",
            "yolo": "YOLOv11n"
        }
    }


@router.get("/health", response_model=HealthResponse, status_code=200)
async def health_check():
    bitnet_healthy = bitnet_client.is_healthy()
    
    yolo_available = False
    try:
        response = requests.get(f"{YOLO_SERVICE_URL}/health", timeout=2)
        yolo_available = response.status_code == 200
    except Exception:
        pass
    
    db_connected = db_client.is_connected()
    db_stats = db_client.get_stats()
    
    firebase_connected = False
    firebase_stats = None
    try:
        response = requests.get(f"{FIREBASE_SERVICE_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            firebase_connected = data.get("connected", False)
            firebase_stats = data.get("stats")
    except Exception:
        firebase_connected = False
    
    rabbitmq_connected = rabbitmq_client.is_connected()
    
    return HealthResponse(
        status="ok" if (bitnet_healthy and yolo_available) else "degraded",
        model_loaded=bitnet_healthy,
        llama_server_running=bitnet_healthy,
        yolo_available=yolo_available,
        database_connected=db_connected,
        database_stats=db_stats,
        firebase_connected=firebase_connected,
        firebase_stats=firebase_stats,
        rabbitmq_connected=rabbitmq_connected
    )

