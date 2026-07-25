"""Authentication router - User management and sessions."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr

from ke.config import load_config
from ke.api.middleware.auth import create_access_token, get_current_user

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user account."""
    from ke.application.services import AuthService

    config = load_config()
    auth_service = AuthService(config)

    try:
        user = auth_service.create_account(
            user_data.username,
            user_data.email,
            user_data.password,
        )

        # Create access token
        access_token = create_access_token(data={"sub": user.user_id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                created_at=user.created_at.isoformat(),
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Authenticate user and return token."""
    from ke.application.services import AuthService

    config = load_config()
    auth_service = AuthService(config)

    user = auth_service.login(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.user_id})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            created_at=user.created_at.isoformat(),
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(**current_user)


@router.get("/users")
async def list_users(limit: int = 100):
    """List all users (admin only)."""
    from ke.application.services import AuthService

    config = load_config()
    auth_service = AuthService(config)

    users = auth_service.list_users(limit=limit)
    return [
        UserResponse(
            user_id=u.user_id,
            username=u.username,
            email=u.email,
            created_at=u.created_at.isoformat(),
        )
        for u in users
    ]
