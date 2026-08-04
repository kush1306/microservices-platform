"""Pydantic v2 request and response schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    """Allowed order status values."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderBase(BaseModel):
    """Shared order fields."""

    user_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unit_price: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    status: OrderStatus = OrderStatus.PENDING


class OrderCreate(OrderBase):
    """Payload for creating an order."""


class OrderUpdate(BaseModel):
    """Payload for full order updates (PUT)."""

    user_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unit_price: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    status: OrderStatus


class OrderStatusUpdate(BaseModel):
    """Payload for updating order status only."""

    status: OrderStatus


class OrderResponse(BaseModel):
    """Public order representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    """Paginated list of orders."""

    total: int
    items: list[OrderResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str
