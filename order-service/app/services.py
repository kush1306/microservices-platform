"""Business logic layer for order operations."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Order
from app.schemas import OrderCreate, OrderStatusUpdate, OrderUpdate
from app.utils import calculate_total_price, get_logger

logger = get_logger(__name__)


class OrderService:
    """Service encapsulating order CRUD and status business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_orders(self, skip: int = 0, limit: int = 100) -> tuple[list[Order], int]:
        """Return a page of orders and the total count."""
        query = self.db.query(Order)
        total = query.count()
        items = query.order_by(Order.id.asc()).offset(skip).limit(limit).all()
        logger.info("Listed orders skip=%s limit=%s total=%s", skip, limit, total)
        return items, total

    def get_order(self, order_id: int) -> Order:
        """Fetch an order by id or raise 404."""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order is None:
            logger.warning("Order not found id=%s", order_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found",
            )
        return order

    def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Order], int]:
        """List orders belonging to a user."""
        query = self.db.query(Order).filter(Order.user_id == user_id)
        total = query.count()
        items = query.order_by(Order.id.asc()).offset(skip).limit(limit).all()
        logger.info(
            "Listed orders by user_id=%s skip=%s limit=%s total=%s",
            user_id,
            skip,
            limit,
            total,
        )
        return items, total

    def create_order(self, payload: OrderCreate) -> Order:
        """Create a new order and compute total_price."""
        total_price = calculate_total_price(payload.quantity, payload.unit_price)
        order = Order(
            user_id=payload.user_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            total_price=total_price,
            status=payload.status.value,
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        logger.info(
            "Created order id=%s user_id=%s total_price=%s",
            order.id,
            order.user_id,
            order.total_price,
        )
        return order

    def update_order(self, order_id: int, payload: OrderUpdate) -> Order:
        """Replace an existing order's fields and recalculate total_price."""
        order = self.get_order(order_id)
        order.user_id = payload.user_id
        order.product_id = payload.product_id
        order.quantity = payload.quantity
        order.unit_price = payload.unit_price
        order.total_price = calculate_total_price(payload.quantity, payload.unit_price)
        order.status = payload.status.value

        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        logger.info("Updated order id=%s", order.id)
        return order

    def update_status(self, order_id: int, payload: OrderStatusUpdate) -> Order:
        """Update only the status of an existing order."""
        order = self.get_order(order_id)
        order.status = payload.status.value
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        logger.info("Updated order id=%s status=%s", order.id, order.status)
        return order

    def delete_order(self, order_id: int) -> None:
        """Delete an order by id."""
        order = self.get_order(order_id)
        self.db.delete(order)
        self.db.commit()
        logger.info("Deleted order id=%s", order_id)
