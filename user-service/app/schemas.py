"""Pydantic v2 request and response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_\-\.]+$")
    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    is_active: bool = True


class UserCreate(UserBase):
    """Payload for creating a user."""


class UserUpdate(BaseModel):
    """Payload for full user updates (PUT)."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_\-\.]+$")
    full_name: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    is_active: bool = True


class UserResponse(UserBase):
    """Public user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Paginated list of users."""

    total: int
    items: list[UserResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str
