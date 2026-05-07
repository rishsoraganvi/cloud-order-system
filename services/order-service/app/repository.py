from sqlalchemy.orm import Session
from . import models


def create_order(db: Session, product_id: int, qty: int, status: str = "PENDING") -> models.Order:
    order = models.Order(product_id=product_id, qty=qty, status=status)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> models.Order | None:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def update_order_status(db: Session, order_id: int, new_status: str) -> models.Order | None:
    order = get_order(db, order_id)
    if order:
        order.status = new_status
        db.commit()
        db.refresh(order)
    return order
