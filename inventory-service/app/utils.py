"""Shared utility helpers."""

from __future__ import annotations

import logging
import re

SKU_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-_]{1,63}$")


def setup_logging(level: str = "INFO") -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


def normalize_sku(sku: str) -> str:
    """Normalize a SKU for storage and uniqueness checks."""
    return sku.strip().upper()


def normalize_warehouse(warehouse: str) -> str:
    """Normalize a warehouse string for consistent storage."""
    return " ".join(warehouse.strip().split())


def available_quantity(quantity: int, reserved_quantity: int) -> int:
    """Return the quantity available for reservation or sale."""
    return quantity - reserved_quantity


def is_valid_sku(sku: str) -> bool:
    """Return True when the SKU matches the allowed pattern."""
    return bool(SKU_PATTERN.match(sku))
