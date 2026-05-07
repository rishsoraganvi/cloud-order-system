"""
NotificationFactory — Factory Pattern implementation.

Instantiates appropriate notifier based on channel string.
Demonstrates SOLID: Open/Closed Principle.
New channels can be added by implementing BaseNotifier and registering in the factory.
"""

from typing import Dict
from services.notification_service.app.notifiers import (
    BaseNotifier,
    EmailNotifier,
    SMSNotifier,
    WebhookNotifier,
)


class NotificationFactory:
    """Factory for creating notifier instances based on channel type."""

    _notifiers: Dict[str, type] = {
        "email": EmailNotifier,
        "sms": SMSNotifier,
        "webhook": WebhookNotifier,
    }

    @staticmethod
    def get_notifier(channel: str) -> BaseNotifier:
        """
        Get a notifier instance for the given channel.

        Args:
            channel: Notification channel type (email, sms, webhook, etc.)

        Returns:
            An instance of the appropriate notifier.

        Raises:
            ValueError: If the channel is not supported.
        """
        if channel not in NotificationFactory._notifiers:
            raise ValueError(f"Unknown notification channel: {channel}")

        notifier_class = NotificationFactory._notifiers[channel]
        return notifier_class()

    @staticmethod
    def register_notifier(channel: str, notifier_class: type) -> None:
        """
        Register a new notifier type (extensibility point).

        Args:
            channel: Channel name.
            notifier_class: A class implementing BaseNotifier.
        """
        NotificationFactory._notifiers[channel] = notifier_class

    @staticmethod
    def supported_channels() -> list:
        """Return list of supported notification channels."""
        return list(NotificationFactory._notifiers.keys())
