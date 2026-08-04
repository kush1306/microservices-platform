"""HTTP route handlers for the order microservice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import (
    HealthResponse,
    MessageResponse,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdate,
    OrderUpdate,
)
from app.services import OrderService

settings = get_settings()

router = APIRouter()


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Provide an OrderService bound to the request DB session."""
    return OrderService(db)


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
)
def health_check() -> HealthResponse:
    """Return service health information."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/orders",
    response_model=OrderListResponse,
    tags=["Orders"],
    summary="List orders",
)
def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    """Return a paginated list of orders."""
    items, total = service.list_orders(skip=skip, limit=limit)
    return OrderListResponse(total=total, items=items)


@router.get(
    "/orders/user/{user_id}",
    response_model=OrderListResponse,
    tags=["Orders"],
    summary="List orders by user id",
)
def list_orders_by_user(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: OrderService = Depends(get_order_service),
) -> OrderListResponse:
    """Return orders belonging to a given user."""
    items, total = service.list_by_user(user_id=user_id, skip=skip, limit=limit)
    return OrderListResponse(total=total, items=items)


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Get order by id",
)
def get_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Return a single order by primary key."""
    return service.get_order(order_id)


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"],
    summary="Create order",
)
def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Create a new order."""
    return service.create_order(payload)


@router.put(
    "/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Update order",
)
def update_order(
    order_id: int,
    payload: OrderUpdate,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Fully update an existing order."""
    return service.update_order(order_id, payload)


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
    tags=["Orders"],
    summary="Update order status",
)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """Update only the status of an existing order."""
    return service.update_status(order_id, payload)


@router.delete(
    "/orders/{order_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    tags=["Orders"],
    summary="Delete order",
)
def delete_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
) -> MessageResponse:
    """Delete an order by primary key."""
    service.delete_order(order_id)
    return MessageResponse(message=f"Order {order_id} deleted successfully")
