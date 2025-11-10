# Review: this module implements a RabbitMQ worker that listens for messages on a specified queue, it processes each message to perform post-processing based on the type of data (image or text), and updates a Firebase document with the results (in principle). It properly handles errors and acknowledges messages to ensure reliable processing. However, it would be good to document the code properly for better maintainability.
import json
import os
import time
import pika

from app.services.firebase_service import update_analysis


QUEUE_NAME = os.getenv("QUEUE_NAME", "postprocess")


def get_params():
    # env var used by the API to connect to the queue
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    return pika.URLParameters(url)


def post_process(msg: dict) -> dict:
    t = msg.get("type")
    data = msg.get("data", {})
    out = {"post_processed_at": int(time.time())}

    if t == "image":
        foods = data.get("food_items", [])
        out["food_count"] = len(foods)
        out["note"] = "looks balanced" if len(foods) >= 2 else "could use more variety"
    elif t == "text":
        rec = data.get("recommendation", "")
        out["summary_len"] = len(rec)
        out["note"] = "solid advice" if len(rec) > 40 else "short advice"
    else:
        out["note"] = "unknown type"

    return out


def main():
    # basic consumer loop
    params = get_params()
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def handle(ch, method, properties, body):
        # update firebase document with post-processing results
        try:
            msg = json.loads(body.decode("utf-8"))
            firebase_id = msg.get("firebase_id")
            extra = post_process(msg)

            if firebase_id:
                update_analysis(firebase_id, {"post_processing": extra})
            else:
                print("no firebase id, skipping update")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"worker failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=handle)
    print(f"worker listening on '{QUEUE_NAME}'")
    channel.start_consuming()


if __name__ == "__main__":
    main()


