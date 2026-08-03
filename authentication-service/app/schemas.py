"""Pydantic request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user fields."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Payload for user registration."""

    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Payload for username/email + password login."""

    username: str = Field(description="Username or email address")
    password: str


class UserUpdate(BaseModel):
    """Payload for partial user profile updates."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserResponse(UserBase):
    """Public user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT claims."""

    sub: str | None = None
    exp: int | None = None
    type: str | None = None


class RefreshTokenRequest(BaseModel):
    """Payload for exchanging a refresh token."""

    refresh_token: str


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str
