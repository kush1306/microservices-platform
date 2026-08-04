"""Pydantic v2 request and response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InventoryBase(BaseModel):
    """Shared inventory fields."""

    product_id: int = Field(gt=0)
    sku: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9\-_]{1,63}$")
    quantity: int = Field(ge=0)
    reserved_quantity: int = Field(default=0, ge=0)
    warehouse: str = Field(min_length=1, max_length=100)
    low_stock_threshold: int = Field(default=10, ge=0)

    @field_validator("sku", "warehouse")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Trim surrounding whitespace from string fields."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field must not be empty or whitespace only")
        return cleaned

    @model_validator(mode="after")
    def validate_reserved_against_quantity(self) -> InventoryBase:
        """Ensure reserved quantity does not exceed total quantity."""
        if self.reserved_quantity > self.quantity:
            raise ValueError("reserved_quantity cannot exceed quantity")
        return self


class InventoryCreate(InventoryBase):
    """Payload for creating an inventory record."""


class InventoryUpdate(BaseModel):
    """Payload for full inventory updates (PUT)."""

    product_id: int = Field(gt=0)
    sku: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9\-_]{1,63}$")
    quantity: int = Field(ge=0)
    reserved_quantity: int = Field(ge=0)
    warehouse: str = Field(min_length=1, max_length=100)
    low_stock_threshold: int = Field(ge=0)

    @field_validator("sku", "warehouse")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Trim surrounding whitespace from string fields."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("field must not be empty or whitespace only")
        return cleaned

    @model_validator(mode="after")
    def validate_reserved_against_quantity(self) -> InventoryUpdate:
        """Ensure reserved quantity does not exceed total quantity."""
        if self.reserved_quantity > self.quantity:
            raise ValueError("reserved_quantity cannot exceed quantity")
        return self


class StockAdjustRequest(BaseModel):
    """Payload for increase, decrease, reserve, and release operations."""

    amount: int = Field(gt=0, description="Positive amount to adjust")


class InventoryResponse(BaseModel):
    """Public inventory representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    sku: str
    quantity: int
    reserved_quantity: int
    warehouse: str
    low_stock_threshold: int
    created_at: datetime
    updated_at: datetime


class InventoryListResponse(BaseModel):
    """Paginated list of inventory records."""

    total: int
    items: list[InventoryResponse]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class MessageResponse(BaseModel):
    """Generic API message response."""

    message: str
