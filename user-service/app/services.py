"""Business logic layer for user operations."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.utils import get_logger, mask_email, normalize_email, normalize_username

logger = get_logger(__name__)


class UserService:
    """Service encapsulating user CRUD business logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """Return a page of users and the total count."""
        query = self.db.query(User)
        total = query.count()
        items = query.order_by(User.id.asc()).offset(skip).limit(limit).all()
        logger.info("Listed users skip=%s limit=%s total=%s", skip, limit, total)
        return items, total

    def get_user(self, user_id: int) -> User:
        """Fetch a user by id or raise 404."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.warning("User not found id=%s", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return user

    def get_by_email(self, email: str) -> User | None:
        """Fetch a user by normalized email."""
        return (
            self.db.query(User)
            .filter(User.email == normalize_email(email))
            .first()
        )

    def get_by_username(self, username: str) -> User | None:
        """Fetch a user by normalized username."""
        return (
            self.db.query(User)
            .filter(User.username == normalize_username(username))
            .first()
        )

    def create_user(self, payload: UserCreate) -> User:
        """Create a new user after uniqueness checks."""
        email = normalize_email(str(payload.email))
        username = normalize_username(payload.username)

        if self.get_by_email(email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )
        if self.get_by_username(username) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken",
            )

        user = User(
            email=email,
            username=username,
            full_name=payload.full_name,
            phone=payload.phone,
            is_active=payload.is_active,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error while creating user email=%s", mask_email(email))
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with the same email or username already exists",
            ) from exc

        self.db.refresh(user)
        logger.info("Created user id=%s email=%s", user.id, mask_email(user.email))
        return user

    def update_user(self, user_id: int, payload: UserUpdate) -> User:
        """Replace an existing user's fields."""
        user = self.get_user(user_id)
        email = normalize_email(str(payload.email))
        username = normalize_username(payload.username)

        existing_email = self.get_by_email(email)
        if existing_email is not None and existing_email.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        existing_username = self.get_by_username(username)
        if existing_username is not None and existing_username.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken",
            )

        user.email = email
        user.username = username
        user.full_name = payload.full_name
        user.phone = payload.phone
        user.is_active = payload.is_active

        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error while updating user id=%s", user_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with the same email or username already exists",
            ) from exc

        self.db.refresh(user)
        logger.info("Updated user id=%s", user.id)
        return user

    def delete_user(self, user_id: int) -> None:
        """Delete a user by id."""
        user = self.get_user(user_id)
        self.db.delete(user)
        self.db.commit()
        logger.info("Deleted user id=%s", user_id)
