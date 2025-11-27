import logging
import os
import requests
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from ..services import DatabaseClient, FirebaseClient, RabbitMQClient

router = APIRouter()
logger = logging.getLogger(__name__)

YOLO_SERVICE_URL = os.getenv("YOLO_SERVICE_URL", "http://yolo-service:8001")
db_client = DatabaseClient()
firebase_client = FirebaseClient()
rabbitmq_client = RabbitMQClient()


@router.post("/detect", status_code=200)
async def detect_objects_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        files = {"file": (file.filename or "image.jpg", contents, file.content_type)}
        
        response = requests.post(
            f"{YOLO_SERVICE_URL}/detect",
            files=files,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"YOLO service error: {response.text}"
            )
        
        result = response.json()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        db_client.log_request(
            service="yolo",
            request_data={"filename": file.filename, "content_type": file.content_type},
            response_data=result,
            status="success"
        )
        
        firebase_client.create_output(
            service="yolo",
            request_data={"filename": file.filename, "content_type": file.content_type},
            response_data=result,
            metadata={"image_processed": True}
        )
        
        rabbitmq_client.publish(
            service="yolo",
            request_data={"filename": file.filename, "content_type": file.content_type},
            response_data=result,
            metadata={"image_processed": True}
        )
        
        return result
        
    except HTTPException:
        raise
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YOLO service is not available"
        )
    except Exception as e:
        logger.error(f"YOLO processing error: {e}")
        raise HTTPException(status_code=500, detail=f"YOLO processing error: {str(e)}")

