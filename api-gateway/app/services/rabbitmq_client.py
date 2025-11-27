import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "model_outputs")

class RabbitMQClient:
    def __init__(self):
        self.available = RABBITMQ_AVAILABLE
        self.connection = None
        self.channel = None
    
    def _connect(self):
        if not self.available:
            return False
        
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            return True
        except Exception as e:
            logger.warning(f"RabbitMQ connection failed: {e}")
            return False
    
    def publish(self, service: str, request_data: Dict, response_data: Dict, metadata: Optional[Dict] = None):
        if not self.available:
            return
        
        try:
            if not self.channel or self.channel.is_closed:
                if not self._connect():
                    return
            
            message = {
                "service": service,
                "request_data": request_data,
                "response_data": response_data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            if metadata:
                message["metadata"] = metadata
            
            self.channel.basic_publish(
                exchange="",
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            logger.info(f"Published {service} output to RabbitMQ")
        except Exception as e:
            logger.warning(f"Failed to publish to RabbitMQ: {e}")
    
    def is_connected(self) -> bool:
        if not self.available:
            return False
        try:
            if not self.channel or self.channel.is_closed:
                return self._connect()
            return True
        except Exception:
            return False
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

