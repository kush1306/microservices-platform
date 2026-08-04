"""HTTP route handlers for the user microservice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    HealthResponse,
    MessageResponse,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services import UserService
from app.config import get_settings

settings = get_settings()

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Provide a UserService bound to the request DB session."""
    return UserService(db)


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check",
)
def health_check() -> HealthResponse:
    """Return service health information."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@router.get(
    "/users",
    response_model=UserListResponse,
    tags=["Users"],
    summary="List users",
)
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """Return a paginated list of users."""
    items, total = service.list_users(skip=skip, limit=limit)
    return UserListResponse(total=total, items=items)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Get user by id",
)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Return a single user by primary key."""
    return service.get_user(user_id)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Create user",
)
def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user."""
    return service.create_user(payload)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Update user",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Fully update an existing user."""
    return service.update_user(user_id, payload)


@router.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    tags=["Users"],
    summary="Delete user",
)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """Delete a user by primary key."""
    service.delete_user(user_id)
    return MessageResponse(message=f"User {user_id} deleted successfully")
