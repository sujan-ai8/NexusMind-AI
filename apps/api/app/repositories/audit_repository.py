from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from apps.api.app.models.entities import AuditLog


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        action: str,
        resource_type: str,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details_json: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            action=action,
            resource_type=resource_type,
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=resource_id,
            details_json=details_json or {},
            ip_address=ip_address,
        )
        self.db.add(log_entry)
        self.db.commit()
        return log_entry

    def list_by_workspace(self, workspace_id: str, limit: int = 10) -> List[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(AuditLog.workspace_id == workspace_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

