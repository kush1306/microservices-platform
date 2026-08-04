"""Pydantic v2 request and response schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ProductBase(BaseModel):
    """Shared product fields."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    category: str = Field(min_length=1, max_length=100)
    price: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    quantity: int = Field(ge=0)
    sku: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9\-_]{1,63}$")
    image_url: HttpUrl | None = None

    @field_validator("name", "description", "category", "sku")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Trim surrounding whitespace from string fields."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field must not be empty or whitespace only")
        return cleaned


class ProductCreate(ProductBase):
    """Payload for creating a product."""


class ProductUpdate(BaseModel):
    """Payload for full product updates (PUT)."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    category: str = Field(min_length=1, max_length=100)
    price: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    quantity: int = Field(ge=0)
    sku: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9\-_]{1,63}$")
    image_url: HttpUrl | None = None

    @field_validator("name", "description", "category", "sku")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Trim surrounding whitespace from string fields."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field must not be empty or whitespace only")
        return cleaned


class ProductResponse(BaseModel):
    """Public product representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    category: str
    price: Decimal
    quantity: int
    sku: str
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Paginated list of products."""

    total: int
    items: list[ProductResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str
