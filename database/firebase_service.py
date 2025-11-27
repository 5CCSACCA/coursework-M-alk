"""
Firebase client for storing model outputs with CRUD operations.
"""
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

_initialized = False
_db = None

def _get_credentials_path():
    cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase-key.json")
    if os.path.exists(cred_path):
        return cred_path
    if os.path.exists(f"../{cred_path}"):
        return f"../{cred_path}"
    return cred_path

def _initialize_firebase():
    global _initialized, _db
    if _initialized:
        return _db
    
    if not FIREBASE_AVAILABLE:
        logger.error("firebase-admin not installed")
        return None
    
    try:
        cred_path = _get_credentials_path()
        if not os.path.exists(cred_path):
            logger.error(f"Firebase credentials not found at {cred_path}")
            return None
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        _db = firestore.client()
        _initialized = True
        logger.info("Firebase initialized")
        return _db
    except Exception as e:
        logger.error(f"Firebase initialization error: {e}")
        return None

def get_firebase_service():
    if not FIREBASE_AVAILABLE:
        return None
    return FirebaseService()

class FirebaseService:
    def __init__(self):
        self.db = _initialize_firebase()
        self.collection_name = "model_outputs"
    
    def is_connected(self) -> bool:
        return self.db is not None
    
    def create_output(
        self,
        service: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        if not self.is_connected():
            return None
        
        try:
            doc_data = {
                "service": service,
                "request_data": request_data,
                "response_data": response_data,
                "timestamp": datetime.utcnow(),
            }
            
            if metadata:
                doc_data["metadata"] = metadata
            
            doc_ref = self.db.collection(self.collection_name).add(doc_data)
            doc_id = doc_ref[1].id
            logger.info(f"Created Firebase output: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Error creating Firebase output: {e}")
            return None
    
    def get_outputs(
        self,
        service: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        if not self.is_connected():
            return []
        
        try:
            query = self.db.collection(self.collection_name)
            
            if service:
                service = service.lower().strip()
                query = query.where("service", "==", service)
            
            query = query.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).offset(offset)
            
            docs = query.stream()
            results = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                if "timestamp" in data and hasattr(data["timestamp"], "isoformat"):
                    data["timestamp"] = data["timestamp"].isoformat()
                results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"Error getting Firebase outputs: {e}")
            return []
    
    def get_output(self, output_id: str) -> Optional[Dict[str, Any]]:
        if not self.is_connected():
            return None
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(output_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                if "timestamp" in data and hasattr(data["timestamp"], "isoformat"):
                    data["timestamp"] = data["timestamp"].isoformat()
                return data
            return None
        except Exception as e:
            logger.error(f"Error getting Firebase output: {e}")
            return None
    
    def update_output(self, output_id: str, updates: Dict[str, Any]) -> bool:
        if not self.is_connected():
            return False
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(output_id)
            doc_ref.update(updates)
            logger.info(f"Updated Firebase output: {output_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating Firebase output: {e}")
            return False
    
    def delete_output(self, output_id: str) -> bool:
        if not self.is_connected():
            return False
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(output_id)
            doc_ref.delete()
            logger.info(f"Deleted Firebase output: {output_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting Firebase output: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        if not self.is_connected():
            return {}
        
        try:
            all_docs = self.db.collection(self.collection_name).stream()
            total = 0
            bitnet_count = 0
            yolo_count = 0
            
            for doc in all_docs:
                total += 1
                data = doc.to_dict()
                service = data.get("service", "").lower()
                if service == "bitnet":
                    bitnet_count += 1
                elif service == "yolo":
                    yolo_count += 1
            
            return {
                "connected": True,
                "total_outputs": total,
                "bitnet_outputs": bitnet_count,
                "yolo_outputs": yolo_count,
                "collection": self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting Firebase stats: {e}")
            return {"connected": False}

