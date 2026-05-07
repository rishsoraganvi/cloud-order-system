import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# RabbitMQ publisher stub
# In production, this would connect to RabbitMQ and publish messages
# For now, we'll just log events


def publish_order_placed(order_id: int, product_id: int, qty: int):
    """
    Publish order.placed event to RabbitMQ.
    Observer Pattern: Order Service publishes, Notification Service subscribes.
    """
    event = {
        "event_type": "order.placed",
        "order_id": order_id,
        "product_id": product_id,
        "qty": qty
    }
    
    try:
        # In production, this would use pika to publish to RabbitMQ
        # For now, just log
        logger.info(f"Publishing event: {json.dumps(event)}")
        
        # TODO: Implement actual RabbitMQ publisher
        # import pika
        # connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        # channel = connection.channel()
        # channel.queue_declare(queue='orders', durable=True)
        # channel.basic_publish(exchange='', routing_key='orders', body=json.dumps(event))
        # connection.close()
        
    except Exception as e:
        logger.error(f"Failed to publish event: {str(e)}")
