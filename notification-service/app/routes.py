"""HTTP route handlers for the notification microservice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import (
    HealthResponse,
    MessageResponse,
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
)
from app.services import NotificationService

settings = get_settings()

router = APIRouter()


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Provide a NotificationService bound to the request DB session."""
    return NotificationService(db)


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
    "/notifications",
    response_model=NotificationListResponse,
    tags=["Notifications"],
    summary="List notifications",
)
def list_notifications(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    """Return a paginated list of notifications."""
    items, total = service.list_notifications(skip=skip, limit=limit)
    return NotificationListResponse(total=total, items=items)


@router.get(
    "/notifications/user/{user_id}",
    response_model=NotificationListResponse,
    tags=["Notifications"],
    summary="List notifications by user id",
)
def list_notifications_by_user(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    """Return notifications belonging to a given user."""
    items, total = service.list_by_user(user_id=user_id, skip=skip, limit=limit)
    return NotificationListResponse(total=total, items=items)


@router.get(
    "/notifications/{notification_id}",
    response_model=NotificationResponse,
    tags=["Notifications"],
    summary="Get notification by id",
)
def get_notification(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    """Return a single notification by primary key."""
    return service.get_notification(notification_id)


@router.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Notifications"],
    summary="Create notification",
)
def create_notification(
    payload: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    """Create and store a new notification."""
    return service.create_notification(payload)


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
    tags=["Notifications"],
    summary="Mark notification as read",
)
def mark_notification_as_read(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    """Mark an existing notification as read."""
    return service.mark_as_read(notification_id)


@router.delete(
    "/notifications/{notification_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    tags=["Notifications"],
    summary="Delete notification",
)
def delete_notification(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
) -> MessageResponse:
    """Delete a notification by primary key."""
    service.delete_notification(notification_id)
    return MessageResponse(message=f"Notification {notification_id} deleted successfully")
