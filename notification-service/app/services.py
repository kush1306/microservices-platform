"""Business logic layer for notification operations."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Notification
from app.schemas import NotificationCreate
from app.utils import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Service encapsulating notification CRUD business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_notifications(self, skip: int = 0, limit: int = 100) -> tuple[list[Notification], int]:
        """Return a page of notifications and the total count."""
        query = self.db.query(Notification)
        total = query.count()
        items = query.order_by(Notification.id.asc()).offset(skip).limit(limit).all()
        logger.info("Listed notifications skip=%s limit=%s total=%s", skip, limit, total)
        return items, total

    def get_notification(self, notification_id: int) -> Notification:
        """Fetch a notification by id or raise 404."""
        notification = (
            self.db.query(Notification).filter(Notification.id == notification_id).first()
        )
        if notification is None:
            logger.warning("Notification not found id=%s", notification_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification with id {notification_id} not found",
            )
        return notification

    def list_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Notification], int]:
        """List notifications belonging to a user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        total = query.count()
        items = query.order_by(Notification.id.asc()).offset(skip).limit(limit).all()
        logger.info(
            "Listed notifications by user_id=%s skip=%s limit=%s total=%s",
            user_id,
            skip,
            limit,
            total,
        )
        return items, total

    def create_notification(self, payload: NotificationCreate) -> Notification:
        """Create and store a notification (no external provider)."""
        notification = Notification(
            user_id=payload.user_id,
            title=payload.title.strip(),
            message=payload.message.strip(),
            type=payload.type.value,
            is_read=False,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        logger.info(
            "Created notification id=%s user_id=%s type=%s",
            notification.id,
            notification.user_id,
            notification.type,
        )
        return notification

    def mark_as_read(self, notification_id: int) -> Notification:
        """Mark a notification as read."""
        notification = self.get_notification(notification_id)
        notification.is_read = True
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        logger.info("Marked notification id=%s as read", notification.id)
        return notification

    def delete_notification(self, notification_id: int) -> None:
        """Delete a notification by id."""
        notification = self.get_notification(notification_id)
        self.db.delete(notification)
        self.db.commit()
        logger.info("Deleted notification id=%s", notification_id)
