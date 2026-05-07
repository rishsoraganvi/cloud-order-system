"""
RabbitMQ consumer for order.placed events.

Listens to RabbitMQ queue, deserializes JSON events, and dispatches to appropriate notifier
based on the event's notification_channel field.

Demonstrates Observer Pattern: Notification Service reacts to Order Service events
without tight coupling.
"""

import json
import logging
import os
import asyncio
from typing import Dict, Any
from services.notification_service.app.factory import NotificationFactory

logger = logging.getLogger(__name__)


class OrderEventConsumer:
    """Consumes order.placed events from RabbitMQ."""

    def __init__(self, rabbitmq_url: str = None):
        """
        Initialize consumer.

        Args:
            rabbitmq_url: RabbitMQ connection string (default: env var RABBITMQ_URL)
        """
        self.rabbitmq_url = rabbitmq_url or os.environ.get(
            "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"
        )
        self.queue_name = "order.placed"
        self.exchange_name = "orders"
        self.running = False

    async def start(self):
        """Start consuming messages from RabbitMQ."""
        try:
            import aio_pika

            self.running = True
            logger.info(f"OrderEventConsumer.start(): connecting to {self.rabbitmq_url}")

            connection = await aio_pika.connect_robust(self.rabbitmq_url)
            channel = await connection.channel()

            # Declare exchange and queue
            exchange = await channel.declare_exchange(
                self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
            )
            queue = await channel.declare_queue(
                self.queue_name, durable=True, auto_delete=False
            )
            await queue.bind(exchange, "order.placed")

            logger.info(f"OrderEventConsumer: listening on queue '{self.queue_name}'")

            # Consume messages
            await queue.consume(self._process_message, no_ack=False)

            # Keep consumer running
            await asyncio.Event().wait()

        except ImportError:
            logger.warning("aio_pika not installed; running in stub mode")
            # Stub: just log instead of consuming
            while self.running:
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"OrderEventConsumer.start() failed: {e}")
            self.running = False

    async def _process_message(self, message):
        """
        Process a single message from the queue.

        Args:
            message: aio_pika IncomingMessage
        """
        try:
            event_data = json.loads(message.body.decode())
            logger.info(f"OrderEventConsumer: received event: {event_data}")

            # Dispatch to appropriate notifier based on channel config
            channel = event_data.get("notification_channel", "email")
            notifier = NotificationFactory.get_notifier(channel)

            # Send notification
            success = notifier.send(event_data)
            if success:
                logger.info(f"OrderEventConsumer: notification sent via {channel}")
                await message.ack()
            else:
                logger.error(f"OrderEventConsumer: notification failed for {channel}")
                await message.nack(requeue=True)

        except json.JSONDecodeError as e:
            logger.error(f"OrderEventConsumer: malformed JSON: {e}")
            await message.nack(requeue=False)  # Don't retry malformed messages
        except ValueError as e:
            logger.error(f"OrderEventConsumer: unknown channel: {e}")
            await message.nack(requeue=False)
        except Exception as e:
            logger.error(f"OrderEventConsumer: error processing message: {e}")
            await message.nack(requeue=True)  # Requeue on unexpected error

    def stop(self):
        """Stop the consumer."""
        self.running = False
        logger.info("OrderEventConsumer.stop(): stopping consumer")


async def run_consumer():
    """Run the consumer in standalone mode (for testing or background task)."""
    consumer = OrderEventConsumer()
    try:
        await consumer.start()
    except KeyboardInterrupt:
        consumer.stop()
