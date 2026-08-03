"""Shared utility helpers."""

import re


USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{3,100}$")


def normalize_email(email: str) -> str:
    """Normalize an email address for storage and lookup."""
    return email.strip().lower()


def normalize_username(username: str) -> str:
    """Normalize a username for storage and lookup."""
    return username.strip().lower()


def is_valid_username(username: str) -> bool:
    """Return True when the username matches the allowed pattern."""
    return bool(USERNAME_PATTERN.match(username))


def mask_email(email: str) -> str:
    """Mask an email address for safe logging/display."""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}"
    return f"{masked_local}@{domain}"
