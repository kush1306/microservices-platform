"""Pydantic v2 request and response schemas."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NotificationType(str, Enum):
    """Allowed notification delivery types."""

    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class NotificationBase(BaseModel):
    """Shared notification fields."""

    user_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=5000)
    type: NotificationType

    @field_validator("title", "message")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Trim surrounding whitespace from string fields."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field must not be empty or whitespace only")
        return cleaned


class NotificationCreate(NotificationBase):
    """Payload for creating a notification."""


class NotificationResponse(BaseModel):
    """Public notification representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    message: str
    type: NotificationType
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated list of notifications."""

    total: int
    items: list[NotificationResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str
