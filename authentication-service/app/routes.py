"""HTTP route handlers for the authentication service."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    authenticate_user,
    create_user,
    get_current_user,
    issue_tokens,
    refresh_access_token,
    revoke_refresh_token,
    update_user,
)
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import (
    HealthResponse,
    MessageResponse,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)

settings = get_settings()

router = APIRouter()
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
users_router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Return service health information."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
    )


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    """Register a new user account."""
    return create_user(db, user_in)


@auth_router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate with username/email and password (OAuth2 password flow)."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return issue_tokens(db, user)


@auth_router.post("/refresh", response_model=Token)
def refresh_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Token:
    """Exchange a valid refresh token for a new token pair."""
    return refresh_access_token(db, body.refresh_token)


@auth_router.post("/logout", response_model=MessageResponse)
def logout(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> MessageResponse:
    """Revoke the provided refresh token."""
    revoke_refresh_token(db, body.refresh_token)
    return MessageResponse(message="Successfully logged out")


@users_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user's profile."""
    return current_user


@users_router.patch("/me", response_model=UserResponse)
def update_current_user(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Update the authenticated user's profile."""
    return update_user(db, current_user, user_in)


router.include_router(auth_router)
router.include_router(users_router)
