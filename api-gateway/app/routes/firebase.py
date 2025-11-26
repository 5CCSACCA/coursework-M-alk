import os
import logging
import requests
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from ..models import FirebaseOutputRequest

router = APIRouter()
logger = logging.getLogger(__name__)

FIREBASE_SERVICE_URL = os.getenv("FIREBASE_SERVICE_URL", "http://firebase-service:8002")


@router.post("/outputs", status_code=status.HTTP_201_CREATED)
async def create_firebase_output(request: FirebaseOutputRequest):
    if request.service not in ["bitnet", "yolo"]:
        raise HTTPException(
            status_code=400,
            detail="Service must be 'bitnet' or 'yolo'"
        )
    
    try:
        response = requests.post(
            f"{FIREBASE_SERVICE_URL}/outputs",
            json={
                "service": request.service,
                "request_data": request.request_data,
                "response_data": request.response_data,
                "metadata": request.metadata
            },
            timeout=10
        )
        
        if response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Firebase service error: {response.text}"
            )
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outputs", status_code=200)
async def get_firebase_outputs(
    service: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    if service:
        service = service.lower().strip()
        if service not in ["bitnet", "yolo"]:
            raise HTTPException(
                status_code=400,
                detail="Service must be 'bitnet' or 'yolo'"
            )
    
    try:
        params = {"limit": limit, "offset": offset}
        if service:
            params["service"] = service
        
        response = requests.get(
            f"{FIREBASE_SERVICE_URL}/outputs",
            params=params,
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Firebase service error: {response.text}"
            )
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Firebase outputs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outputs/{output_id}", status_code=200)
async def get_firebase_output(output_id: str):
    try:
        response = requests.get(
            f"{FIREBASE_SERVICE_URL}/outputs/{output_id}",
            timeout=10
        )
        
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Output {output_id} not found"
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Firebase service error: {response.text}"
            )
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/outputs/{output_id}", status_code=200)
async def update_firebase_output(
    output_id: str,
    updates: Dict[str, Any]
):
    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No updates provided"
        )
    
    try:
        response = requests.put(
            f"{FIREBASE_SERVICE_URL}/outputs/{output_id}",
            json=updates,
            timeout=10
        )
        
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Output {output_id} not found"
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Firebase service error: {response.text}"
            )
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/outputs/{output_id}", status_code=200)
async def delete_firebase_output(output_id: str):
    try:
        response = requests.delete(
            f"{FIREBASE_SERVICE_URL}/outputs/{output_id}",
            timeout=10
        )
        
        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Output {output_id} not found"
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Firebase service error: {response.text}"
            )
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Firebase service not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Firebase output: {e}")
        raise HTTPException(status_code=500, detail=str(e))
