from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class FirebaseOutputRequest(BaseModel):
    service: str
    request_data: Dict[str, Any]
    response_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

