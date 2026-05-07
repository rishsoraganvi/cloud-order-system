from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    qty: int = Field(..., gt=0)


class OrderUpdate(BaseModel):
    status: str = Field(..., min_length=1)


class OrderResponse(BaseModel):
    id: int
    product_id: int
    qty: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
