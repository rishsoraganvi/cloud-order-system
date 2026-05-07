from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from . import schemas, service
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

router = APIRouter(prefix="/orders", tags=["orders"])


def get_db(request: Request) -> Session:
    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", status_code=HTTP_201_CREATED, response_model=schemas.OrderResponse)
def place_order(order: schemas.OrderCreate, request: Request, db: Session = Depends(get_db)):
    try:
        created = service.place_order(db, order.product_id, order.qty)
        return created
    except service.PlaceOrderException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, payload: schemas.OrderUpdate, request: Request, db: Session = Depends(get_db)):
    try:
        order = service.update_order_status(db, order_id, payload.status)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except service.InvalidStateTransitionException as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail={"error": str(e)})
