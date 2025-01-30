# billing_service.py
import os
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import EmailStr, BaseModel
import pika
import threading
from typing import Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


# Pydantic models
class BillingRequest(BaseModel):
    username: str
    email: EmailStr
    amount: int
    currency: str = "eur"


def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "user"), os.getenv("RABBITMQ_PASS", "password")
    )
    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"), port=5672, credentials=credentials
    )
    return pika.BlockingConnection(parameters)


def publish_billing_event(event_type: str, data: dict):
    """Publish billing events to RabbitMQ"""
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    # Declare queues for different billing events
    channel.queue_declare(queue="billing_requests", durable=True)
    channel.queue_declare(queue="billing_results", durable=True)

    message = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
    }

    channel.basic_publish(
        exchange="",
        routing_key="billing_requests",
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2, content_type="application/json"
        ),
    )

    connection.close()


@app.post("/bill")
async def process_billing(
    billing_request: BillingRequest, background_tasks: BackgroundTasks
):
    """
    Process a billing transaction for a user via Stripe
    Now using message queue for asynchronous processing
    """
    try:
        # Publish billing request to queue
        background_tasks.add_task(
            publish_billing_event, "billing_request", billing_request.dict()
        )

        return {
            "status": "processing",
            "message": "Billing request queued for processing",
            "username": billing_request.username,
        }

    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health-check")
def health_check():
    try:
        # Test RabbitMQ connection as part of health check
        connection = get_rabbitmq_connection()
        connection.close()
        return {"status": "ok", "message": "Service healthy"}
    except Exception as e:
        return {"status": "error", "message": f"Service unhealthy: {str(e)}"}


# billing_worker.py (separate process)
def process_billing_request(ch, method, properties, body):
    try:
        message = json.loads(body)
        data = message["data"]

        # Create payment intent
        # payment_intent = stripe.PaymentIntent.create(
        #     amount=data["amount"],
        #     currency=data["currency"],
        #     customer=stripe.Customer.list(email=data["email"]).data[0].id,
        #     payment_method_types=["card"],
        #     description=f"Billing for {data['username']}",
        # )

        # Publish result
        result = {
            "status": "success",
            "customer_email": data["email"],
            "amount": data["amount"],
            "currency": data["currency"],
            "payment_intent_id": "xxxxx",
            "client_secret": "xxxxxx",
        }

        ch.basic_publish(
            exchange="", routing_key="billing_results", body=json.dumps(result)
        )

    except Exception as e:
        # Publish error result
        error_result = {
            "status": "error",
            "customer_email": data["email"],
            "error": str(e),
        }
        ch.basic_publish(
            exchange="", routing_key="billing_results", body=json.dumps(error_result)
        )

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


class BillingWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # Thread will exit when main program exits
        self._stop_event = threading.Event()
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None

    def stop(self):
        self._stop_event.set()
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def run(self):
        while not self._stop_event.is_set():
            try:
                self.connection = get_rabbitmq_connection()
                self.channel = self.connection.channel()

                self.channel.queue_declare(queue="billing_requests", durable=True)
                self.channel.queue_declare(queue="billing_results", durable=True)

                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(
                    queue="billing_requests",
                    on_message_callback=process_billing_request,
                )

                logger.info("Billing worker started. Waiting for billing requests...")
                self.channel.start_consuming()

            except pika.exceptions.AMQPConnectionError as e:
                logger.error(f"AMQP Connection error: {e}")
                if not self._stop_event.is_set():
                    logger.info("Attempting to reconnect in 5 seconds...")
                    self._stop_event.wait(timeout=5.0)
            except Exception as e:
                logger.error(f"Unexpected error in billing worker: {e}")
                if not self._stop_event.is_set():
                    logger.info("Restarting worker in 5 seconds...")
                    self._stop_event.wait(timeout=5.0)


worker = BillingWorker()


@app.on_event("startup")
async def startup_event():
    worker.start()
    logger.info("Billing worker thread started")


@app.on_event("shutdown")
async def shutdown_event():
    worker.stop()
    logger.info("Billing worker thread stopped")
