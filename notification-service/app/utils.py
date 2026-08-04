"""Shared utility helpers."""

from __future__ import annotations

import logging

from app.schemas import NotificationType

VALID_TYPES = {notification_type.value for notification_type in NotificationType}


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


def is_valid_notification_type(notification_type: str) -> bool:
    """Return True when the type is a known notification type."""
    return notification_type in VALID_TYPES
