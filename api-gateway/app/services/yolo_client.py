import os
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class YOLOClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv("YOLO_SERVICE_URL", "http://yolo-service:8001")
        self.fallback_enabled = os.getenv("YOLO_FALLBACK", "1") == "1"
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            if self.fallback_enabled:
                try:
                    from services.yolo.yolo_service import detect_objects
                    return True
                except ImportError:
                    return False
            return False
    
    def detect(self, image_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
        try:
            files = {"file": (filename or "image.jpg", image_bytes, "image/jpeg")}
            response = requests.post(
                f"{self.base_url}/detect",
                files=files,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"YOLO service call failed: {e}")
        
        if self.fallback_enabled:
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
                from services.yolo.yolo_service import detect_objects
                return detect_objects(image_bytes)
            except ImportError:
                raise Exception("YOLO service unavailable and fallback not available")
        
        raise Exception("YOLO service unavailable")

