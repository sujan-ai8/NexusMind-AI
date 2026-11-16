from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_current_user
from apps.api.app.models.entities import User
from apps.api.app.repositories.user_repository import UserRepository
from apps.api.app.schemas.auth import UserResponse
from apps.api.app.schemas.common import APIResponse
from apps.api.app.schemas.settings import SystemSettingsResponse, UserProfileUpdateRequest
from apps.api.app.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=APIResponse[SystemSettingsResponse], status_code=status.HTTP_200_OK)
def get_system_settings(
    current_user: User = Depends(get_current_user),
):
    """Retrieve system configuration and enabled capabilities."""
    settings_data = SettingsService.get_system_settings()
    return APIResponse(
        success=True,
        message="System settings retrieved",
        data=settings_data,
    )


@router.put("/profile", response_model=APIResponse[UserResponse], status_code=status.HTTP_200_OK)
def update_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile information for the authenticated user."""
    user_repo = UserRepository(db)
    if payload.full_name is not None and len(payload.full_name.strip()) > 1:
        current_user.full_name = payload.full_name.strip()
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url.strip()

    updated_user = user_repo.update(current_user)
    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=UserResponse.model_validate(updated_user),
    )

