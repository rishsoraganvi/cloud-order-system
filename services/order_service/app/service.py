from sqlalchemy.orm import Session
from . import repository, models
import httpx
from datetime import datetime

# State machine: valid transitions per status
VALID_TRANSITIONS = {
    "PENDING": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["SHIPPED"],
    "SHIPPED": ["DELIVERED"],
    "DELIVERED": [],
    "CANCELLED": [],
}


class InvalidStateTransitionException(Exception):
    pass


class PlaceOrderException(Exception):
    pass


def place_order(db: Session, product_id: int, qty: int, product_service_url: str = "http://product-service:8002"):
    """
    Place order: call Product Service to reserve stock, then create order and publish event.
    Raises PlaceOrderException if stock reservation fails or if Product Service is unavailable.
    """
    try:
        # Call Product Service to reserve stock
        async_client = httpx.Client(timeout=5.0)
        response = async_client.put(
            f"{product_service_url}/products/{product_id}/reserve",
            params={"qty": qty}
        )
        async_client.close()

        if response.status_code == 409:
            raise PlaceOrderException("Insufficient stock")
        if response.status_code == 404:
            raise PlaceOrderException("Product not found")
        if response.status_code != 200:
            raise PlaceOrderException(f"Stock reservation failed: {response.status_code}")

        # Create order with PENDING status
        order = repository.create_order(db, product_id=product_id, qty=qty, status="PENDING")

        # Publish event (will be implemented in events.py)
        from . import events
        events.publish_order_placed(order.id, product_id, qty)

        return order
    except httpx.RequestError as e:
        raise PlaceOrderException(f"Failed to connect to Product Service: {str(e)}")


def get_order(db: Session, order_id: int):
    """Get order by id, returns None if not found."""
    return repository.get_order(db, order_id)


def update_order_status(db: Session, order_id: int, new_status: str):
    """
    Update order status with state machine validation.
    Raises InvalidStateTransitionException if transition is not allowed.
    """
    order = repository.get_order(db, order_id)
    if not order:
        return None

    # Validate state transition
    if new_status not in VALID_TRANSITIONS.get(order.status, []):
        raise InvalidStateTransitionException(
            f"Invalid transition from {order.status} to {new_status}"
        )

    # Update status
    order = repository.update_order_status(db, order_id, new_status)
    return order
