import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from ..services import DatabaseClient

router = APIRouter()
logger = logging.getLogger(__name__)

db_client = DatabaseClient()


@router.get("", status_code=200)
async def get_all_requests(
    service: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    if not db_client.available:
        raise HTTPException(
            status_code=503,
            detail="Database service not available"
        )
    
    try:
        if service and service not in ["bitnet", "yolo"]:
            raise HTTPException(
                status_code=400,
                detail="Service must be 'bitnet' or 'yolo'"
            )
        
        requests = db_client.get_requests(
            service=service,
            limit=min(limit, 100),
            skip=skip
        )
        
        return {
            "total": len(requests),
            "service_filter": service,
            "limit": limit,
            "skip": skip,
            "requests": requests
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{request_id}", status_code=200)
async def get_request_by_id(request_id: str):
    if not db_client.available:
        raise HTTPException(
            status_code=503,
            detail="Database service not available"
        )
    
    try:
        request = db_client.get_request_by_id(request_id)
        
        if not request:
            raise HTTPException(
                status_code=404,
                detail=f"Request {request_id} not found"
            )
        
        return request
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

