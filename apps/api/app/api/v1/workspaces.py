from typing import List
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_current_user, require_workspace_role
from apps.api.app.models.entities import User
from apps.api.app.models.enums import RoleEnum
from apps.api.app.schemas.common import APIResponse
from apps.api.app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceResponse,
    WorkspaceSettingsResponse,
    WorkspaceSettingsUpdateRequest,
)
from apps.api.app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["Workspace Management"])


@router.get("", response_model=APIResponse[List[WorkspaceResponse]], status_code=status.HTTP_200_OK)
def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all workspaces that the authenticated user has access to."""
    service = WorkspaceService(db)
    workspaces = service.list_user_workspaces(current_user.id)
    return APIResponse(
        success=True,
        message="Workspaces retrieved",
        data=workspaces,
    )


@router.post("", response_model=APIResponse[WorkspaceResponse], status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new workspace and assign the creator as WORKSPACE_ADMIN."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    service = WorkspaceService(db)
    workspace = service.create_workspace(payload, user_id=current_user.id, ip_address=client_ip)
    return APIResponse(
        success=True,
        message="Workspace created successfully",
        data=workspace,
    )


@router.get("/{workspace_id}/settings", response_model=APIResponse[WorkspaceSettingsResponse])
def get_workspace_settings(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve settings for a specific workspace."""
    service = WorkspaceService(db)
    settings_data = service.get_workspace_settings(workspace_id, current_user.id)
    return APIResponse(success=True, data=settings_data)


@router.put("/{workspace_id}/settings", response_model=APIResponse[WorkspaceSettingsResponse])
def update_workspace_settings(
    workspace_id: str,
    payload: WorkspaceSettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.WORKSPACE_ADMIN)),
):
    """Update settings for a workspace (Requires WORKSPACE_ADMIN role)."""
    service = WorkspaceService(db)
    settings_data = service.update_workspace_settings(workspace_id, current_user.id, payload)
    return APIResponse(success=True, message="Settings updated", data=settings_data)

