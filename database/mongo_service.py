"""
MongoDB client for logging API requests.
"""
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "milo_db")
REQUESTS_COLLECTION = "requests"

class MongoDBService:
    """MongoDB wrapper for request logging."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.requests_collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            self.requests_collection = self.db[REQUESTS_COLLECTION]
            logger.info(f"Connected to MongoDB: {DB_NAME}")
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None
        except Exception as e:
            logger.error(f"MongoDB setup error: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self.client is not None
    
    def log_request(
        self,
        service: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        status: str = "success"
    ) -> Optional[str]:
        """Store request in database."""
        if not self.is_connected():
            logger.warning("MongoDB not connected, skipping log")
            return None
        
        try:
            document = {
                "service": service,
                "timestamp": datetime.utcnow(),
                "request": request_data,
                "response": response_data,
                "status": status
            }
            
            result = self.requests_collection.insert_one(document)
            logger.info(f"Logged {service} request: {result.inserted_id}")
            return str(result.inserted_id)
            
        except OperationFailure as e:
            logger.error(f"MongoDB insert failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error logging request: {e}")
            return None
    
    def get_requests(
        self,
        service: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Get requests with optional service filter."""
        if not self.is_connected():
            logger.warning("MongoDB not connected")
            return []
        
        try:
            query = {}
            if service:
                query["service"] = service
            
            cursor = self.requests_collection.find(query).sort(
                "timestamp", DESCENDING
            ).skip(skip).limit(limit)
            
            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["timestamp"] = doc["timestamp"].isoformat()
                results.append(doc)
            
            logger.info(f"Retrieved {len(results)} requests")
            return results
            
        except OperationFailure as e:
            logger.error(f"MongoDB query failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving requests: {e}")
            return []
    
    def get_request_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single request by ID."""
        if not self.is_connected():
            return None
        
        try:
            from bson.objectid import ObjectId
            doc = self.requests_collection.find_one({"_id": ObjectId(request_id)})
            
            if doc:
                doc["_id"] = str(doc["_id"])
                doc["timestamp"] = doc["timestamp"].isoformat()
                return doc
            return None
            
        except Exception as e:
            logger.error(f"Error getting request by ID: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Request counts by service."""
        if not self.is_connected():
            return {"connected": False}
        
        try:
            total = self.requests_collection.count_documents({})
            bitnet_count = self.requests_collection.count_documents({"service": "bitnet"})
            yolo_count = self.requests_collection.count_documents({"service": "yolo"})
            
            return {
                "connected": True,
                "total_requests": total,
                "bitnet_requests": bitnet_count,
                "yolo_requests": yolo_count
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"connected": False, "error": str(e)}
    
    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Singleton
_db_service: Optional[MongoDBService] = None

def get_db_service() -> MongoDBService:
    """Get MongoDB service instance."""
    global _db_service
    if _db_service is None:
        _db_service = MongoDBService()
    return _db_service

