import logging
import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from database.firebase_service import get_firebase_service
    FIREBASE_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import Firebase service: {e}")
    FIREBASE_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Firebase CRUD Service",
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
    if not FIREBASE_AVAILABLE:
        return {"status": "unavailable", "firebase_available": False}

    try:
        firebase_service = get_firebase_service()
        if not firebase_service:
            return {"status": "unavailable", "firebase_available": True, "connected": False}
        
        connected = firebase_service.is_connected()
        stats = firebase_service.get_stats() if connected else None
        return {
            "status": "ok" if connected else "unavailable",
            "firebase_available": True,
            "connected": connected,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "firebase_available": True, "error": str(e)}


@app.post("/outputs", status_code=status.HTTP_201_CREATED)
async def create_output(request: Dict[str, Any]):
    if not FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )

    if request.get("service") not in ["bitnet", "yolo"]:
        raise HTTPException(
            status_code=400,
            detail="Service must be 'bitnet' or 'yolo'"
        )

    try:
        firebase_service = get_firebase_service()
        if not firebase_service:
            raise HTTPException(status_code=503, detail="Firebase not initialized")
        
        doc_id = firebase_service.create_output(
            service=request["service"],
            request_data=request["request_data"],
            response_data=request["response_data"],
            metadata=request.get("metadata")
        )

        if not doc_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to create output"
            )

        return {
            "id": doc_id,
            "message": "Output created successfully",
            "service": request["service"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outputs", status_code=200)
async def get_outputs(
    service: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    if not FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )

    if service:
        service = service.lower().strip()
        if service not in ["bitnet", "yolo"]:
            raise HTTPException(
                status_code=400,
                detail="Service must be 'bitnet' or 'yolo'"
            )

    try:
        firebase_service = get_firebase_service()
        if not firebase_service:
            raise HTTPException(status_code=503, detail="Firebase not initialized")
        
        outputs = firebase_service.get_outputs(
            service=service,
            limit=min(limit, 100),
            offset=offset
        )

        return {
            "total": len(outputs),
            "service_filter": service,
            "limit": limit,
            "offset": offset,
            "outputs": outputs
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Firebase outputs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outputs/{output_id}", status_code=200)
async def get_output(output_id: str):
    if not FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )

    try:
        firebase_service = get_firebase_service()
        if not firebase_service:
            raise HTTPException(status_code=503, detail="Firebase not initialized")
        
        output = firebase_service.get_output(output_id)

        if not output:
            raise HTTPException(
                status_code=404,
                detail=f"Output {output_id} not found"
            )

        return output

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/outputs/{output_id}", status_code=200)
async def update_output(
    output_id: str,
    updates: Dict[str, Any]
):
    if not FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No updates provided"
        )

    try:
        firebase_service = get_firebase_service()
        if not firebase_service:
            raise HTTPException(status_code=503, detail="Firebase not initialized")
        
        success = firebase_service.update_output(output_id, updates)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Output {output_id} not found"
            )

        return {
            "id": output_id,
            "message": "Output updated successfully",
            "updated_fields": list(updates.keys())
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/outputs/{output_id}", status_code=200)
async def delete_output(output_id: str):
    if not FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )

    try:
        firebase_service = get_firebase_service()
        if not firebase_service:
            raise HTTPException(status_code=503, detail="Firebase not initialized")
        
        success = firebase_service.delete_output(output_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Output {output_id} not found"
            )

        return {
            "id": output_id,
            "message": "Output deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))

