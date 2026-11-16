from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from apps.api.app.models.entities import ProcessingJob, ProcessingLog


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, job_id: str, workspace_id: str) -> Optional[ProcessingJob]:
        return self.db.execute(
            select(ProcessingJob).where(
                ProcessingJob.id == job_id,
                ProcessingJob.workspace_id == workspace_id,
            )
        ).scalar_one_or_none()

    def list_by_workspace(
        self,
        workspace_id: str,
        dataset_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ProcessingJob]:
        stmt = select(ProcessingJob).where(ProcessingJob.workspace_id == workspace_id)
        if dataset_id:
            stmt = stmt.where(ProcessingJob.dataset_id == dataset_id)
        stmt = stmt.order_by(ProcessingJob.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_by_workspace(self, workspace_id: str, dataset_id: Optional[str] = None) -> int:
        stmt = select(func.count(ProcessingJob.id)).where(ProcessingJob.workspace_id == workspace_id)
        if dataset_id:
            stmt = stmt.where(ProcessingJob.dataset_id == dataset_id)
        return self.db.execute(stmt).scalar() or 0

    def create(self, job: ProcessingJob) -> ProcessingJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update(self, job: ProcessingJob) -> ProcessingJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def add_log(self, job_id: str, message: str, level: str = "INFO", stage: str = "PROCESSING") -> ProcessingLog:
        log_entry = ProcessingLog(
            job_id=job_id,
            level=level.upper(),
            message=message,
            stage=stage,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_logs(self, job_id: str) -> List[ProcessingLog]:
        stmt = select(ProcessingLog).where(ProcessingLog.job_id == job_id).order_by(ProcessingLog.timestamp.asc())
        return list(self.db.execute(stmt).scalars().all())
