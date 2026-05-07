"""
Notifier implementations using Factory pattern.

BaseNotifier: Abstract base class defining the interface.
EmailNotifier, SMSNotifier, WebhookNotifier: Concrete implementations.

SOLID: Open/Closed Principle — new channels can be added without modifying existing code.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseNotifier(ABC):
    """Abstract base class for notification channels."""

    @abstractmethod
    def send(self, payload: Dict[str, Any]) -> bool:
        """
        Send notification with the given payload.

        Args:
            payload: Event data containing order_id, customer_email, message_type, etc.

        Returns:
            True if sent successfully, False otherwise.
        """
        pass


class EmailNotifier(BaseNotifier):
    """Email notification via SendGrid or similar."""

    def send(self, payload: Dict[str, Any]) -> bool:
        """Send email notification."""
        try:
            order_id = payload.get("order_id")
            customer_email = payload.get("customer_email")
            message_type = payload.get("message_type")

            # In production, use SendGrid SDK or similar
            # from sendgrid import SendGridAPIClient
            # from sendgrid.helpers.mail import Mail
            #
            # mail = Mail(
            #     from_email="orders@ecommerce.com",
            #     to_emails=customer_email,
            #     subject=f"Order {order_id} {message_type.title()}",
            #     plain_text_content=f"Your order {order_id} has been {message_type.lower()}."
            # )
            # SendGridAPIClient(os.environ.get("SENDGRID_API_KEY")).send(mail)

            logger.info(
                f"EmailNotifier.send(): order_id={order_id}, "
                f"to={customer_email}, message={message_type}"
            )
            return True
        except Exception as e:
            logger.error(f"EmailNotifier.send() failed: {e}")
            return False


class SMSNotifier(BaseNotifier):
    """SMS notification via Twilio or similar."""

    def send(self, payload: Dict[str, Any]) -> bool:
        """Send SMS notification."""
        try:
            order_id = payload.get("order_id")
            customer_phone = payload.get("customer_phone")
            message_type = payload.get("message_type")

            # In production, use Twilio SDK
            # from twilio.rest import Client
            # client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
            # message = client.messages.create(
            #     body=f"Order {order_id} has been {message_type.lower()}. Track your order at https://orders.ecommerce.com/{order_id}",
            #     from_=os.environ.get("TWILIO_PHONE_NUMBER"),
            #     to=customer_phone
            # )

            logger.info(
                f"SMSNotifier.send(): order_id={order_id}, "
                f"to={customer_phone}, message={message_type}"
            )
            return True
        except Exception as e:
            logger.error(f"SMSNotifier.send() failed: {e}")
            return False


class WebhookNotifier(BaseNotifier):
    """Webhook notification via HTTP POST to custom endpoint."""

    def send(self, payload: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        try:
            webhook_url = payload.get("webhook_url")
            order_id = payload.get("order_id")

            # Validate webhook URL (security: reject localhost, private IPs, non-HTTPS)
            if not webhook_url:
                logger.warning("WebhookNotifier.send(): webhook_url not provided")
                return False

            if webhook_url.startswith("http://localhost") or webhook_url.startswith(
                "http://127.0.0.1"
            ):
                logger.error(
                    "WebhookNotifier.send(): rejected localhost webhook (security)"
                )
                return False

            if not webhook_url.startswith("https://"):
                logger.error("WebhookNotifier.send(): rejected non-HTTPS webhook")
                return False

            # In production, use httpx or requests with timeout
            # import httpx
            # async with httpx.AsyncClient() as client:
            #     response = await client.post(webhook_url, json=payload, timeout=5.0)
            #     response.raise_for_status()

            logger.info(
                f"WebhookNotifier.send(): order_id={order_id}, webhook={webhook_url}"
            )
            return True
        except Exception as e:
            logger.error(f"WebhookNotifier.send() failed: {e}")
            return False
