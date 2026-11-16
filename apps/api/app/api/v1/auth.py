from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_current_user
from apps.api.app.models.entities import User
from apps.api.app.schemas.auth import (
    AuthResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from apps.api.app.schemas.common import APIResponse
from apps.api.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[AuthResponse], status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Register a new user account with secure password hashing."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    service = AuthService(db)
    result = service.register(payload, ip_address=client_ip)
    return APIResponse(
        success=True,
        message="User account created successfully",
        data=result,
    )


@router.post("/login", response_model=APIResponse[AuthResponse], status_code=status.HTTP_200_OK)
def login(
    payload: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate user credentials and issue JWT access token."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    service = AuthService(db)
    result = service.login(payload, ip_address=client_ip)
    return APIResponse(
        success=True,
        message="Authentication successful",
        data=result,
    )


@router.post("/logout", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
def logout(
    current_user: User = Depends(get_current_user),
):
    """Stateless JWT logout acknowledgement (clears client session)."""
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data={"user_id": current_user.id},
    )


@router.get("/me", response_model=APIResponse[UserResponse], status_code=status.HTTP_200_OK)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """Retrieve profile and roles for the currently authenticated user."""
    return APIResponse(
        success=True,
        message="Profile retrieved",
        data=UserResponse.model_validate(current_user),
    )

