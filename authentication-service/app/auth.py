"""Authentication business logic and FastAPI dependencies."""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import RefreshToken, User
from app.schemas import Token, UserCreate, UserUpdate
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_subject,
    hash_password,
    verify_password,
)
from app.utils import normalize_email, normalize_username

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by email."""
    return db.query(User).filter(User.email == normalize_email(email)).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Fetch a user by username."""
    return db.query(User).filter(User.username == normalize_username(username)).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Fetch a user by primary key."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_login(db: Session, login: str) -> User | None:
    """Fetch a user by username or email."""
    normalized = login.strip().lower()
    user = get_user_by_username(db, normalized)
    if user is not None:
        return user
    return get_user_by_email(db, normalized)


def create_user(db: Session, user_in: UserCreate) -> User:
    """Register a new user account."""
    email = normalize_email(user_in.email)
    username = normalize_username(user_in.username)

    if get_user_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )
    if get_user_by_username(db, username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken",
        )

    user = User(
        email=email,
        username=username,
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, login: str, password: str) -> User | None:
    """Validate credentials and return the user when successful."""
    user = get_user_by_login(db, login)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def issue_tokens(db: Session, user: User) -> Token:
    """Create access and refresh tokens and persist the refresh token."""
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    db.add(
        RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
    )
    db.commit()

    return Token(access_token=access_token, refresh_token=refresh_token)


def refresh_access_token(db: Session, refresh_token: str) -> Token:
    """Rotate tokens using a valid, non-revoked refresh token."""
    subject = get_token_subject(refresh_token, expected_type="refresh")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stored = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked.is_(False),
        )
        .first()
    )
    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_at = stored.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        stored.revoked = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(db, int(subject))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive or does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stored.revoked = True
    db.commit()
    return issue_tokens(db, user)


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    """Revoke a refresh token if it exists."""
    stored = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if stored is not None and not stored.revoked:
        stored.revoked = True
        db.commit()


def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """Apply partial updates to a user profile."""
    if user_in.email is not None:
        email = normalize_email(user_in.email)
        existing = get_user_by_email(db, email)
        if existing is not None and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )
        user.email = email

    if user_in.full_name is not None:
        user.full_name = user_in.full_name

    if user_in.password is not None:
        user.hashed_password = hash_password(user_in.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Resolve the authenticated user from a Bearer access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError) as exc:
        raise credentials_exception from exc

    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure the authenticated user has superuser privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges",
        )
    return current_user
