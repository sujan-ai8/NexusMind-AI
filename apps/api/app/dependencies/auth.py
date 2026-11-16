from typing import Callable, List, Optional
from fastapi import Depends, Header, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from apps.api.app.core.errors import AuthenticationError, NotFoundError, PermissionDeniedError
from apps.api.app.core.security import decode_access_token
from apps.api.app.db.session import get_db
from apps.api.app.models.entities import User, Workspace, WorkspaceMember
from apps.api.app.models.enums import RoleEnum
from apps.api.app.repositories.user_repository import UserRepository
from apps.api.app.repositories.workspace_repository import WorkspaceRepository

security_bearer = HTTPBearer(auto_error=False)

# Hierarchy of permissions: PLATFORM_ADMIN > WORKSPACE_ADMIN > ANALYST > VIEWER
ROLE_HIERARCHY = {
    RoleEnum.PLATFORM_ADMIN.value: 4,
    RoleEnum.WORKSPACE_ADMIN.value: 3,
    RoleEnum.ANALYST.value: 2,
    RoleEnum.VIEWER.value: 1,
}


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authentication token is missing")

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise AuthenticationError("Invalid or expired authentication token")

    user_id = payload["sub"]
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise AuthenticationError("User associated with token no longer exists")

    if not user.is_active:
        raise AuthenticationError("User account has been deactivated")

    return user


def require_platform_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_platform_admin:
        raise PermissionDeniedError("Platform administrator privileges required")
    return current_user


def get_active_workspace(
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-Id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Workspace:
    workspace_repo = WorkspaceRepository(db)

    # If header provided, verify membership
    if x_workspace_id:
        workspace = workspace_repo.get_by_id(x_workspace_id)
        if not workspace:
            raise NotFoundError("Specified workspace does not exist")
        member = workspace_repo.get_member(x_workspace_id, current_user.id)
        if not member and not current_user.is_platform_admin:
            raise PermissionDeniedError("You do not have access to this workspace")
        return workspace

    # Otherwise fallback to user's first accessible workspace
    workspaces = workspace_repo.list_by_user(current_user.id)
    if not workspaces:
        raise NotFoundError("No workspaces found for user. Please complete onboarding first.")
    return workspaces[0]


def require_workspace_role(min_role: RoleEnum) -> Callable:
    """Dependency factory checking that the current user has at least min_role in the active workspace."""
    def role_checker(
        workspace: Workspace = Depends(get_active_workspace),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> WorkspaceMember:
        if current_user.is_platform_admin:
            # Platform admin has superuser rights
            return WorkspaceMember(
                workspace_id=workspace.id,
                user_id=current_user.id,
                role=RoleEnum.PLATFORM_ADMIN.value,
            )

        workspace_repo = WorkspaceRepository(db)
        member = workspace_repo.get_member(workspace.id, current_user.id)
        if not member:
            raise PermissionDeniedError("You are not a member of this workspace")

        user_level = ROLE_HIERARCHY.get(member.role, 0)
        required_level = ROLE_HIERARCHY.get(min_role.value, 0)

        if user_level < required_level:
            raise PermissionDeniedError(
                f"Action requires at least '{min_role.value}' role (current role: '{member.role}')"
            )

        return member

    return role_checker

