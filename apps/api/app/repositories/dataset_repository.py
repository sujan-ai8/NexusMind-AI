from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from apps.api.app.models.entities import Dataset


class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, dataset_id: str, workspace_id: str) -> Optional[Dataset]:
        return self.db.execute(
            select(Dataset).where(
                Dataset.id == dataset_id,
                Dataset.workspace_id == workspace_id,
            )
        ).scalar_one_or_none()

    def list_by_workspace(
        self,
        workspace_id: str,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dataset]:
        stmt = select(Dataset).where(Dataset.workspace_id == workspace_id)
        if search:
            stmt = stmt.where(Dataset.name.ilike(f"%{search}%"))
        stmt = stmt.order_by(Dataset.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_by_workspace(self, workspace_id: str) -> int:
        stmt = select(func.count(Dataset.id)).where(Dataset.workspace_id == workspace_id)
        return self.db.execute(stmt).scalar() or 0

    def create(self, dataset: Dataset) -> Dataset:
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

