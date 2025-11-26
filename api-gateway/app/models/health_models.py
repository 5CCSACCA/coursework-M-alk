from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    llama_server_running: bool = False
    yolo_available: bool = False
    database_connected: bool = False
    database_stats: Optional[Dict[str, Any]] = None
    firebase_connected: bool = False
    firebase_stats: Optional[Dict[str, Any]] = None

