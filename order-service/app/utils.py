"""Shared utility helpers."""

from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP

from app.schemas import OrderStatus

VALID_STATUSES = {status.value for status in OrderStatus}


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


def calculate_total_price(quantity: int, unit_price: Decimal) -> Decimal:
    """Compute total price as quantity × unit_price, rounded to 2 decimal places."""
    total = Decimal(quantity) * Decimal(unit_price)
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def is_valid_status(status: str) -> bool:
    """Return True when the status is a known order status."""
    return status in VALID_STATUSES
