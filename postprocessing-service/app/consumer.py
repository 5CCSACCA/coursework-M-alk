import os
import json
import logging
import pika
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "model_outputs")

def process_output(message: Dict[str, Any]) -> Dict[str, Any]:
    service = message.get("service", "")
    response_data = message.get("response_data", {})
    
    processed = {
        "service": service,
        "original_output": response_data,
        "processed_at": message.get("timestamp", ""),
        "status": "processed"
    }
    
    if service == "bitnet":
        content = response_data.get("content", "") or response_data.get("generated_text", "")
        processed["word_count"] = len(content.split())
        processed["char_count"] = len(content)
        processed["has_content"] = len(content.strip()) > 0
    
    elif service == "yolo":
        detections = response_data.get("detections", [])
        processed["detection_count"] = len(detections)
        processed["unique_labels"] = list(set(d.get("label", "") for d in detections))
    
    logger.info(f"Processed {service} output")
    return processed

def on_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        logger.info(f"Received message: {message.get('service', 'unknown')}")
        
        processed = process_output(message)
        
        logger.info(f"Processing complete: {processed.get('status')}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"Processing error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()
        
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=RABBITMQ_QUEUE,
            on_message_callback=on_message
        )
        
        logger.info("Waiting for messages. Press CTRL+C to exit.")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("Stopping consumer")
        channel.stop_consuming()
        connection.close()
    except Exception as e:
        logger.error(f"Connection error: {e}")

if __name__ == "__main__":
    main()

