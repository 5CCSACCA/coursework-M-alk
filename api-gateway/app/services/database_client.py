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
    from services.database.mongo_service import get_db_service
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class DatabaseClient:
    def __init__(self):
        self.available = DB_AVAILABLE
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
    
    def log_request(self, service: str, request_data: Dict, response_data: Dict, status: str):
        if not self.available:
            return
        try:
            db_service = self._get_service()
            db_service.log_request(service, request_data, response_data, status)
        except Exception as e:
            logger.warning(f"Failed to log request: {e}")
    
    def get_requests(self, service: Optional[str] = None, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        if not self.available:
            return []
        try:
            db_service = self._get_service()
            return db_service.get_requests(service=service, limit=limit, skip=skip)
        except Exception as e:
            logger.error(f"Error getting requests: {e}")
            return []
    
    def get_request_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        if not self.available:
            return None
        try:
            db_service = self._get_service()
            return db_service.get_request_by_id(request_id)
        except Exception as e:
            logger.error(f"Error getting request: {e}")
            return None
    
    def _get_service(self):
        if self._service is None:
            self._service = get_db_service()
        return self._service

