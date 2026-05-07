"""
Tests for NotificationFactory and notifier implementations (TDD: RED phase).

These tests define the expected behavior. They will fail until implementations are complete.
"""

import pytest
from services.notification_service.app.notifiers import (
    BaseNotifier,
    EmailNotifier,
    SMSNotifier,
    WebhookNotifier,
)
from services.notification_service.app.factory import NotificationFactory


class TestNotifiers:
    """Test notifier implementations."""

    def test_email_notifier_send(self):
        """Test 1: EmailNotifier.send() formats email and logs."""
        notifier = EmailNotifier()
        payload = {
            "order_id": "ORD-12345",
            "customer_email": "customer@example.com",
            "message_type": "placed",
        }
        result = notifier.send(payload)
        assert result is True
        # Verify it's a BaseNotifier subclass
        assert isinstance(notifier, BaseNotifier)

    def test_sms_notifier_send(self):
        """Test 2: SMSNotifier.send() formats SMS and logs."""
        notifier = SMSNotifier()
        payload = {
            "order_id": "ORD-12345",
            "customer_phone": "+1234567890",
            "message_type": "shipped",
        }
        result = notifier.send(payload)
        assert result is True
        # Verify it's a BaseNotifier subclass
        assert isinstance(notifier, BaseNotifier)

    def test_webhook_notifier_send_valid_https(self):
        """Test 3: WebhookNotifier.send() accepts HTTPS URLs."""
        notifier = WebhookNotifier()
        payload = {
            "order_id": "ORD-12345",
            "webhook_url": "https://webhook.example.com/events",
        }
        result = notifier.send(payload)
        assert result is True

    def test_webhook_notifier_rejects_localhost(self):
        """Test 3b: WebhookNotifier.send() rejects localhost (security)."""
        notifier = WebhookNotifier()
        payload = {
            "order_id": "ORD-12345",
            "webhook_url": "http://localhost:8000/webhook",
        }
        result = notifier.send(payload)
        assert result is False

    def test_webhook_notifier_rejects_http(self):
        """Test 3c: WebhookNotifier.send() rejects non-HTTPS."""
        notifier = WebhookNotifier()
        payload = {
            "order_id": "ORD-12345",
            "webhook_url": "http://example.com/webhook",
        }
        result = notifier.send(payload)
        assert result is False


class TestNotificationFactory:
    """Test NotificationFactory."""

    def test_factory_get_email_notifier(self):
        """Test 4: NotificationFactory.get_notifier('email') returns EmailNotifier."""
        notifier = NotificationFactory.get_notifier("email")
        assert isinstance(notifier, EmailNotifier)
        assert isinstance(notifier, BaseNotifier)

    def test_factory_get_sms_notifier(self):
        """Test 5: NotificationFactory.get_notifier('sms') returns SMSNotifier."""
        notifier = NotificationFactory.get_notifier("sms")
        assert isinstance(notifier, SMSNotifier)
        assert isinstance(notifier, BaseNotifier)

    def test_factory_get_webhook_notifier(self):
        """Test 6: NotificationFactory.get_notifier('webhook') returns WebhookNotifier."""
        notifier = NotificationFactory.get_notifier("webhook")
        assert isinstance(notifier, WebhookNotifier)
        assert isinstance(notifier, BaseNotifier)

    def test_factory_unknown_channel_raises_error(self):
        """Test 7: NotificationFactory.get_notifier('unknown') raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            NotificationFactory.get_notifier("unknown")
        assert "Unknown notification channel" in str(exc_info.value)

    def test_factory_supported_channels(self):
        """Test 8: NotificationFactory.supported_channels() returns list of channels."""
        channels = NotificationFactory.supported_channels()
        assert "email" in channels
        assert "sms" in channels
        assert "webhook" in channels


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
