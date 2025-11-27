from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class FirebaseOutputRequest(BaseModel):
    service: str = Field(...)
    request_data: Dict[str, Any] = Field(...)
    response_data: Dict[str, Any] = Field(...)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

