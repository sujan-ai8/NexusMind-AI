from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from apps.api.app.models.entities import Dataset
from apps.api.app.repositories.audit_repository import AuditRepository
from apps.api.app.repositories.dataset_repository import DatasetRepository
from apps.api.app.schemas.dataset import DatasetCreateRequest, DatasetResponse


class DatasetService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.audit_repo = AuditRepository(db)

    def list_datasets(
        self,
        workspace_id: str,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[DatasetResponse], int]:
        skip = (page - 1) * page_size
        items = self.dataset_repo.list_by_workspace(
            workspace_id=workspace_id,
            search=search,
            skip=skip,
            limit=page_size,
        )
        total = self.dataset_repo.count_by_workspace(workspace_id=workspace_id)
        responses = [DatasetResponse.model_validate(i) for i in items]
        return responses, total

    def create_dataset(
        self,
        workspace_id: str,
        payload: DatasetCreateRequest,
        user_id: str,
        ip_address: str = "127.0.0.1",
    ) -> DatasetResponse:
        dataset = Dataset(
            workspace_id=workspace_id,
            name=payload.name.strip(),
            description=payload.description.strip() if payload.description else None,
            file_format=payload.file_format.upper(),
            file_size_bytes=payload.file_size_bytes,
            storage_uri=payload.storage_uri or f"s3://nexusmind-datasets/{workspace_id}/{payload.name.lower().replace(' ', '_')}.csv",
            row_count=payload.row_count,
            status="READY",
            uploaded_by=user_id,
        )
        created = self.dataset_repo.create(dataset)

        self.audit_repo.log(
            action="DATASET_REGISTERED",
            resource_type="DATASET",
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=created.id,
            details_json={"name": created.name, "format": created.file_format},
            ip_address=ip_address,
        )

        return DatasetResponse.model_validate(created)

