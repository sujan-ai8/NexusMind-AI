from typing import List
from sqlalchemy.orm import Session
from apps.api.app.core.errors import NotFoundError, PermissionDeniedError
from apps.api.app.models.entities import Workspace, WorkspaceSettings
from apps.api.app.models.enums import RoleEnum
from apps.api.app.repositories.audit_repository import AuditRepository
from apps.api.app.repositories.workspace_repository import WorkspaceRepository
from apps.api.app.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceSettingsResponse,
    WorkspaceSettingsUpdateRequest,
)


class WorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.workspace_repo = WorkspaceRepository(db)
        self.audit_repo = AuditRepository(db)

    def list_user_workspaces(self, user_id: str) -> List[WorkspaceResponse]:
        workspaces = self.workspace_repo.list_by_user(user_id)
        results = []
        for ws in workspaces:
            member = self.workspace_repo.get_member(ws.id, user_id)
            res = WorkspaceResponse.model_validate(ws)
            if member:
                res.role = member.role
            results.append(res)
        return results

    def create_workspace(
        self, payload: WorkspaceCreateRequest, user_id: str, ip_address: str = "127.0.0.1"
    ) -> WorkspaceResponse:
        slug = self.workspace_repo.generate_slug(payload.name)
        workspace = Workspace(
            name=payload.name.strip(),
            slug=slug,
            description=payload.description.strip() if payload.description else None,
            type=payload.type.value,
            cloud_provider=payload.cloud_provider.value,
            owner_id=user_id,
        )
        created = self.workspace_repo.create(workspace, owner_id=user_id)

        self.audit_repo.log(
            action="WORKSPACE_CREATED",
            resource_type="WORKSPACE",
            workspace_id=created.id,
            user_id=user_id,
            resource_id=created.id,
            details_json={"name": created.name, "cloud_provider": created.cloud_provider},
            ip_address=ip_address,
        )

        res = WorkspaceResponse.model_validate(created)
        res.role = RoleEnum.WORKSPACE_ADMIN.value
        return res

    def get_workspace_or_raise(self, workspace_id: str, user_id: str) -> Workspace:
        workspace = self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace not found")

        member = self.workspace_repo.get_member(workspace_id, user_id)
        if not member:
            raise PermissionDeniedError("Access to this workspace is denied")

        return workspace

    def get_workspace_settings(self, workspace_id: str, user_id: str) -> WorkspaceSettingsResponse:
        self.get_workspace_or_raise(workspace_id, user_id)
        settings = self.workspace_repo.get_settings(workspace_id)
        if not settings:
            raise NotFoundError("Workspace settings not found")
        return WorkspaceSettingsResponse.model_validate(settings)

    def update_workspace_settings(
        self, workspace_id: str, user_id: str, payload: WorkspaceSettingsUpdateRequest
    ) -> WorkspaceSettingsResponse:
        self.get_workspace_or_raise(workspace_id, user_id)
        settings = self.workspace_repo.get_settings(workspace_id)
        if not settings:
            raise NotFoundError("Workspace settings not found")

        if payload.telemetry_enabled is not None:
            settings.telemetry_enabled = payload.telemetry_enabled
        if payload.aws_region is not None:
            settings.aws_region = payload.aws_region
        if payload.alert_email is not None:
            settings.alert_email = payload.alert_email
        if payload.cost_threshold is not None:
            settings.cost_threshold = payload.cost_threshold
        if payload.max_concurrent_jobs is not None:
            settings.max_concurrent_jobs = payload.max_concurrent_jobs

        self.db.commit()
        self.db.refresh(settings)
        return WorkspaceSettingsResponse.model_validate(settings)

