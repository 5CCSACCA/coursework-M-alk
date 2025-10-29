import json
import os
import pika


QUEUE_NAME = os.getenv("QUEUE_NAME", "postprocess")


def _get_connection_params():
    # broker url from environment variable
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    return pika.URLParameters(url)


def publish(payload: dict):
    # push a JSON message to QUEUE_NAME
    body = json.dumps(payload).encode("utf-8")
    try:
        conn = pika.BlockingConnection(_get_connection_params())
        ch = conn.channel()
        ch.queue_declare(queue=QUEUE_NAME, durable=True)
        ch.basic_publish(exchange="", routing_key=QUEUE_NAME, body=body, properties=pika.BasicProperties(delivery_mode=2))
        conn.close()
        return True
    except Exception as e:
        print(f"queue publish failed: {e}")
        return False


