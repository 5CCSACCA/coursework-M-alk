import os
import requests
import logging
from fastapi import APIRouter
from ..models import HealthResponse
from ..services import BitNetClient

router = APIRouter()
logger = logging.getLogger(__name__)

bitnet_client = BitNetClient()
YOLO_SERVICE_URL = os.getenv("YOLO_SERVICE_URL", "http://yolo-service:8001")


@router.get("/", response_model=dict, status_code=200)
async def root():
    return {
        "service": "Milo AI Unified API Gateway",
        "version": "1.0",
        "framework": "FastAPI",
        "endpoints": {
            "POST /bitnet/completion": "Generate text completion (BitNet)",
            "POST /yolo/detect": "Detect objects in image (YOLO)",
            "GET /health": "Check service health",
            "GET /docs": "Interactive API documentation"
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
    
    return HealthResponse(
        status="ok" if (bitnet_healthy and yolo_available) else "degraded",
        model_loaded=bitnet_healthy,
        llama_server_running=bitnet_healthy,
        yolo_available=yolo_available,
        database_connected=False,
        database_stats=None,
        firebase_connected=False,
        firebase_stats=None
    )

