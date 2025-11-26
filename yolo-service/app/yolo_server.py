import logging
from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

try:
    from .yolo_service import detect_objects
    YOLO_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import YOLO service: {e}")
    YOLO_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YOLO Object Detection Service",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok" if YOLO_AVAILABLE else "unavailable",
        "yolo_available": YOLO_AVAILABLE
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if not YOLO_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YOLO service is not available"
        )
    
    try:
        contents = await file.read()
        result = detect_objects(contents)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"YOLO processing error: {e}")
        raise HTTPException(status_code=500, detail=f"YOLO processing error: {str(e)}")

