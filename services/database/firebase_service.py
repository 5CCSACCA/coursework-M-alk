"""
Firebase client for model outputs storage with CRUD operations.
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, initialize_app
    FIREBASE_AVAILABLE = True
except ImportError:
    logger.warning("Firebase Admin SDK not installed")
    FIREBASE_AVAILABLE = False


class FirebaseService:
    """Firebase wrapper for model output storage."""
    
    def __init__(self):
        self.db = None
        self.outputs_collection = "model_outputs"
        self._connect()
    
    def _connect(self):
        """Initialize Firebase connection."""
        if not FIREBASE_AVAILABLE:
            logger.error("Firebase SDK not available")
            return
        
        try:
            # Check if already initialized
            try:
                firebase_admin.get_app()
                logger.info("Using existing Firebase app")
            except ValueError:
                # Need to initialize
                creds_path = os.getenv("FIREBASE_CREDENTIALS")
                
                if not creds_path:
                    # Try default locations
                    project_root = Path(__file__).parent.parent.parent
                    possible_paths = [
                        project_root / "firebase-key.json",
                        project_root / "firebase-credentials.json"
                    ]
                    
                    for default_path in possible_paths:
                        if default_path.exists():
                            creds_path = str(default_path)
                            break
                    
                    if not creds_path:
                        logger.warning("Firebase credentials not found. Set FIREBASE_CREDENTIALS env var.")
                        return
                
                if not os.path.exists(creds_path):
                    logger.error(f"Firebase credentials file not found: {creds_path}")
                    return
                
                cred = credentials.Certificate(creds_path)
                initialize_app(cred)
                logger.info("Firebase initialized successfully")
            
            self.db = firestore.client()
            logger.info(f"Connected to Firestore collection: {self.outputs_collection}")
            
        except Exception as e:
            logger.error(f"Firebase setup error: {e}")
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if Firebase is ready."""
        return self.db is not None
    
    def create_output(
        self,
        service: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Store model output in Firebase.
        
        Args:
            service: "bitnet" or "yolo"
            request_data: Original request
            response_data: Model response
            metadata: Additional metadata (optional)
        
        Returns:
            Document ID or None if failed
        """
        if not self.is_connected():
            logger.warning("Firebase not connected, skipping storage")
            return None
        
        try:
            document = {
                "service": service,
                "timestamp": datetime.utcnow(),
                "request": request_data,
                "response": response_data,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            doc_ref = self.db.collection(self.outputs_collection).document()
            doc_ref.set(document)
            
            doc_id = doc_ref.id
            logger.info(f"Stored {service} output: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error storing output: {e}")
            return None
    
    def get_output(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve model output by ID.
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document data or None
        """
        if not self.is_connected():
            return None
        
        try:
            doc_ref = self.db.collection(self.outputs_collection).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                
                # Convert timestamps to ISO format
                for field in ["timestamp", "created_at", "updated_at"]:
                    if field in data and data[field]:
                        data[field] = data[field].isoformat()
                
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving output: {e}")
            return None
    
    def get_outputs(
        self,
        service: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get multiple outputs with optional filtering.
        
        Args:
            service: Filter by service type (optional, case-insensitive)
            limit: Max results
            offset: Skip first N results
        
        Returns:
            List of documents
        """
        if not self.is_connected():
            return []
        
        try:
            # Fetch all documents and filter client-side for case-insensitive matching
            query = self.db.collection(self.outputs_collection)
            query = query.order_by("timestamp", direction=firestore.Query.DESCENDING)
            
            docs = query.stream()
            results = []
            
            # Normalize service filter to lowercase for comparison
            service_filter = service.lower().strip() if service else None
            
            for doc in docs:
                data = doc.to_dict()
                
                # Apply service filter with case-insensitive comparison
                if service_filter:
                    doc_service = data.get("service", "").lower().strip()
                    if doc_service != service_filter:
                        continue
                
                # Add document ID
                data["id"] = doc.id
                
                # Convert timestamps
                for field in ["timestamp", "created_at", "updated_at"]:
                    if field in data and data[field]:
                        data[field] = data[field].isoformat()
                
                results.append(data)
            
            # Apply offset and limit after filtering
            total_filtered = len(results)
            results = results[offset:offset + limit]
            
            logger.info(f"Retrieved {len(results)} outputs (filtered from {total_filtered} total)")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving outputs: {e}")
            return []
    
    def update_output(
        self,
        doc_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update existing model output.
        
        Args:
            doc_id: Document ID
            updates: Fields to update
        
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            doc_ref = self.db.collection(self.outputs_collection).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Document {doc_id} not found")
                return False
            
            # Add updated timestamp
            updates["updated_at"] = datetime.utcnow()
            
            doc_ref.update(updates)
            logger.info(f"Updated output: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating output: {e}")
            return False
    
    def delete_output(self, doc_id: str) -> bool:
        """
        Delete model output.
        
        Args:
            doc_id: Document ID
        
        Returns:
            True if successful
        """
        if not self.is_connected():
            return False
        
        try:
            doc_ref = self.db.collection(self.outputs_collection).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"Document {doc_id} not found")
                return False
            
            doc_ref.delete()
            logger.info(f"Deleted output: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting output: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Stats dictionary
        """
        if not self.is_connected():
            return {"connected": False}
        
        try:
            # Get counts per service
            all_docs = list(self.db.collection(self.outputs_collection).stream())
            total = len(all_docs)
            
            bitnet_count = sum(1 for doc in all_docs if doc.to_dict().get("service") == "bitnet")
            yolo_count = sum(1 for doc in all_docs if doc.to_dict().get("service") == "yolo")
            
            return {
                "connected": True,
                "total_outputs": total,
                "bitnet_outputs": bitnet_count,
                "yolo_outputs": yolo_count,
                "collection": self.outputs_collection
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"connected": False, "error": str(e)}


# Singleton instance
_firebase_service: Optional[FirebaseService] = None


def get_firebase_service() -> FirebaseService:
    """Get Firebase service singleton."""
    global _firebase_service
    if _firebase_service is None:
        _firebase_service = FirebaseService()
    return _firebase_service

