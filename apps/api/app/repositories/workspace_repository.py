import re
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from apps.api.app.models.entities import Workspace, WorkspaceMember, WorkspaceSettings
from apps.api.app.models.enums import RoleEnum


class WorkspaceRepository:
    def __init__(self, db: Session):
        self.db = db

    def generate_slug(self, name: str) -> str:
        base_slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
        if not base_slug:
            base_slug = "workspace"
        slug = base_slug
        counter = 1
        while self.get_by_slug(slug) is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        return self.db.execute(
            select(Workspace).where(Workspace.id == workspace_id)
        ).scalar_one_or_none()

    def get_by_slug(self, slug: str) -> Optional[Workspace]:
        return self.db.execute(
            select(Workspace).where(Workspace.slug == slug)
        ).scalar_one_or_none()

    def list_by_user(self, user_id: str) -> List[Workspace]:
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(self, workspace: Workspace, owner_id: str) -> Workspace:
        self.db.add(workspace)
        self.db.flush()

        # Add owner as WORKSPACE_ADMIN
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role=RoleEnum.WORKSPACE_ADMIN.value,
        )
        self.db.add(member)

        # Initialize default settings
        settings = WorkspaceSettings(
            workspace_id=workspace.id,
            telemetry_enabled=True,
            aws_region=workspace.cloud_provider.lower() if workspace.cloud_provider == "AWS" else "us-east-1",
            cost_threshold=1000.0,
            max_concurrent_jobs=5,
        )
        self.db.add(settings)

        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def get_member(self, workspace_id: str, user_id: str) -> Optional[WorkspaceMember]:
        return self.db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        ).scalar_one_or_none()

    def list_members(self, workspace_id: str) -> List[WorkspaceMember]:
        return list(
            self.db.execute(
                select(WorkspaceMember).where(WorkspaceMember.workspace_id == workspace_id)
            ).scalars().all()
        )

    def get_settings(self, workspace_id: str) -> Optional[WorkspaceSettings]:
        return self.db.execute(
            select(WorkspaceSettings).where(WorkspaceSettings.workspace_id == workspace_id)
        ).scalar_one_or_none()

