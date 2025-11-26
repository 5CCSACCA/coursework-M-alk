import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from services.database.firebase_service import get_firebase_service
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class FirebaseClient:
    def __init__(self):
        self.available = FIREBASE_AVAILABLE
        self._service = None
    
    def is_connected(self) -> bool:
        if not self.available:
            return False
        try:
            service = self._get_service()
            return service.is_connected()
        except Exception:
            return False
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        if not self.is_connected():
            return None
        try:
            service = self._get_service()
            return service.get_stats()
        except Exception:
            return None
    
    def create_output(self, service: str, request_data: Dict, response_data: Dict, metadata: Optional[Dict] = None) -> Optional[str]:
        if not self.available:
            return None
        try:
            firebase_service = self._get_service()
            return firebase_service.create_output(service, request_data, response_data, metadata)
        except Exception as e:
            logger.warning(f"Failed to store in Firebase: {e}")
            return None
    
    def get_outputs(self, service: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if not self.available:
            return []
        try:
            firebase_service = self._get_service()
            return firebase_service.get_outputs(service=service, limit=limit, offset=offset)
        except Exception as e:
            logger.error(f"Error getting outputs: {e}")
            return []
    
    def get_output(self, output_id: str) -> Optional[Dict[str, Any]]:
        if not self.available:
            return None
        try:
            firebase_service = self._get_service()
            return firebase_service.get_output(output_id)
        except Exception as e:
            logger.error(f"Error getting output: {e}")
            return None
    
    def update_output(self, output_id: str, updates: Dict[str, Any]) -> bool:
        if not self.available:
            return False
        try:
            firebase_service = self._get_service()
            return firebase_service.update_output(output_id, updates)
        except Exception as e:
            logger.error(f"Error updating output: {e}")
            return False
    
    def delete_output(self, output_id: str) -> bool:
        if not self.available:
            return False
        try:
            firebase_service = self._get_service()
            return firebase_service.delete_output(output_id)
        except Exception as e:
            logger.error(f"Error deleting output: {e}")
            return False
    
    def _get_service(self):
        if self._service is None:
            self._service = get_firebase_service()
        return self._service

