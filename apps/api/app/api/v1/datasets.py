import os
from typing import Any, Dict, List, Optional
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_active_workspace, get_current_user, require_workspace_role
from apps.api.app.models.entities import User, Workspace
from apps.api.app.models.enums import RoleEnum
from apps.api.app.schemas.common import APIResponse, PaginatedResponse
from apps.api.app.schemas.dataset import DatasetCreateRequest, DatasetResponse
from apps.api.app.schemas.bigdata import (
    ColumnMappingUpdateRequest,
    ColumnMappingResponse,
    DatasetPreviewResponse,
    DatasetSchemaResponse,
    DataQualityReportResponse,
    ProcessDatasetRequest,
    ProcessingJobResponse,
)
from apps.api.app.services.dataset_service import DatasetService
from apps.api.app.services.bigdata.processing_service import ProcessingService

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])


@router.get("", response_model=APIResponse[PaginatedResponse[DatasetResponse]], status_code=status.HTTP_200_OK)
def list_datasets(
    search: Optional[str] = Query(None, description="Search by dataset name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List datasets in the active workspace with search and pagination."""
    service = DatasetService(db)
    items, total = service.list_datasets(
        workspace_id=workspace.id,
        search=search,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        message="Datasets retrieved",
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.post("", response_model=APIResponse[DatasetResponse], status_code=status.HTTP_201_CREATED)
def create_dataset(
    payload: DatasetCreateRequest,
    request: Request,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.ANALYST)),
):
    """Register dataset metadata in the active workspace (Requires ANALYST or higher role)."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    service = DatasetService(db)
    dataset = service.create_dataset(
        workspace_id=workspace.id,
        payload=payload,
        user_id=current_user.id,
        ip_address=client_ip,
    )
    return APIResponse(
        success=True,
        message="Dataset registered successfully",
        data=dataset,
    )


@router.post("/upload", response_model=APIResponse[DatasetResponse], status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    request: Request = None,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.ANALYST)),
):
    """Upload a raw cloud workload dataset file (CSV, JSON, JSONL)."""
    content = await file.read()
    client_ip = request.client.host if request and request.client else "127.0.0.1"

    service = DatasetService(db)
    dataset = service.upload_dataset_file(
        workspace_id=workspace.id,
        user_id=current_user.id,
        filename=file.filename or "workload_data.csv",
        content=content,
        dataset_name=name,
        description=description,
        ip_address=client_ip,
    )

    return APIResponse(
        success=True,
        message="Dataset uploaded and analyzed successfully",
        data=DatasetResponse.model_validate(dataset),
    )


@router.get("/{dataset_id}", response_model=APIResponse[DatasetResponse], status_code=status.HTTP_200_OK)
def get_dataset(
    dataset_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve metadata for a specific dataset."""
    service = DatasetService(db)
    dataset = service.get_dataset(workspace_id=workspace.id, dataset_id=dataset_id)
    return APIResponse(
        success=True,
        message="Dataset retrieved",
        data=DatasetResponse.model_validate(dataset),
    )


@router.delete("/{dataset_id}", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
def delete_dataset(
    dataset_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.WORKSPACE_ADMIN)),
):
    """Delete a dataset and all associated storage artifacts (Requires ADMIN)."""
    service = DatasetService(db)
    service.delete_dataset(workspace_id=workspace.id, dataset_id=dataset_id, user_id=current_user.id)
    return APIResponse(
        success=True,
        message="Dataset deleted successfully",
        data={"dataset_id": dataset_id, "deleted": True},
    )


@router.get("/{dataset_id}/preview", response_model=APIResponse[DatasetPreviewResponse], status_code=status.HTTP_200_OK)
def get_dataset_preview(
    dataset_id: str,
    limit: int = Query(100, ge=1, le=500),
    page: int = Query(1, ge=1),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Preview first 100 records and column statistics."""
    service = DatasetService(db)
    preview = service.get_dataset_preview(
        workspace_id=workspace.id,
        dataset_id=dataset_id,
        limit=limit,
        page=page,
    )
    return APIResponse(
        success=True,
        message="Dataset preview retrieved",
        data=DatasetPreviewResponse(**preview),
    )


@router.get("/{dataset_id}/schema", response_model=APIResponse[DatasetSchemaResponse], status_code=status.HTTP_200_OK)
def get_dataset_schema(
    dataset_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve inferred schema and column types for a dataset."""
    service = DatasetService(db)
    schema = service.get_schema(workspace_id=workspace.id, dataset_id=dataset_id)
    return APIResponse(
        success=True,
        message="Dataset schema retrieved",
        data=DatasetSchemaResponse(**schema),
    )


@router.get("/{dataset_id}/column-mapping", response_model=APIResponse[ColumnMappingResponse], status_code=status.HTTP_200_OK)
def get_dataset_column_mapping(
    dataset_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get active column mapping to standard cloud workload schema."""
    service = DatasetService(db)
    mapping = service.get_column_mapping(workspace_id=workspace.id, dataset_id=dataset_id)
    return APIResponse(
        success=True,
        message="Column mapping retrieved",
        data=ColumnMappingResponse(**mapping),
    )


@router.post("/{dataset_id}/column-mapping", response_model=APIResponse[ColumnMappingResponse], status_code=status.HTTP_200_OK)
def update_dataset_column_mapping(
    dataset_id: str,
    payload: ColumnMappingUpdateRequest,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.ANALYST)),
):
    """Configure column mapping for standard cloud workload fields."""
    service = DatasetService(db)
    mapping = service.update_column_mapping(
        workspace_id=workspace.id,
        dataset_id=dataset_id,
        mapping=payload.mapping,
        user_id=current_user.id,
    )
    return APIResponse(
        success=True,
        message="Column mapping updated successfully",
        data=ColumnMappingResponse(**mapping),
    )


@router.post("/{dataset_id}/validate", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
def validate_dataset_schema(
    dataset_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Validate dataset schema and mapping against required cloud workload fields."""
    service = DatasetService(db)
    mapping = service.get_column_mapping(workspace_id=workspace.id, dataset_id=dataset_id)
    return APIResponse(
        success=True,
        message="Schema validation complete",
        data={
            "dataset_id": dataset_id,
            "is_valid": mapping["is_valid"],
            "missing_required_fields": mapping["missing_required_fields"],
            "configured_fields": list(mapping["mapping"].keys()),
        },
    )


@router.post("/{dataset_id}/quality/audit", response_model=APIResponse[DataQualityReportResponse], status_code=status.HTTP_200_OK)
def run_quality_audit(
    dataset_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.ANALYST)),
):
    """Execute comprehensive data quality audit."""
    service = DatasetService(db)
    report = service.run_quality_audit(
        workspace_id=workspace.id,
        dataset_id=dataset_id,
        user_id=current_user.id,
    )
    return APIResponse(
        success=True,
        message="Data quality audit completed",
        data=DataQualityReportResponse(**report),
    )


@router.get("/{dataset_id}/quality", response_model=APIResponse[Optional[DataQualityReportResponse]], status_code=status.HTTP_200_OK)
def get_dataset_quality_report(
    dataset_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get latest data quality audit report."""
    service = DatasetService(db)
    report = service.get_latest_quality_report(workspace_id=workspace.id, dataset_id=dataset_id)
    if not report:
        return APIResponse(
            success=True,
            message="No data quality report found. Please run an audit first.",
            data=None,
        )
    return APIResponse(
        success=True,
        message="Data quality report retrieved",
        data=DataQualityReportResponse(**report),
    )


@router.post("/{dataset_id}/process", response_model=APIResponse[ProcessingJobResponse], status_code=status.HTTP_202_ACCEPTED)
def process_dataset(
    dataset_id: str,
    payload: ProcessDatasetRequest,
    background_tasks: BackgroundTasks,
    sync: bool = Query(False, description="Run synchronously if True (recommended for tests or quick jobs)"),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.ANALYST)),
):
    """Trigger distributed PySpark or Pandas transformation & analytics pipeline."""
    processing_service = ProcessingService(db)
    job = processing_service.create_processing_job(
        workspace_id=workspace.id,
        dataset_id=dataset_id,
        user_id=current_user.id,
        engine_preference=payload.engine,
        parameters=payload.parameters,
    )

    if sync:
        job = processing_service.execute_processing_pipeline(
            workspace_id=workspace.id,
            job_id=job.id,
            user_id=current_user.id,
        )
    else:
        # Pass job execution to background tasks
        background_tasks.add_task(
            processing_service.execute_processing_pipeline,
            workspace.id,
            job.id,
            current_user.id,
        )

    return APIResponse(
        success=True,
        message=f"Processing job initiated with engine {payload.engine}",
        data=ProcessingJobResponse.model_validate(job),
    )


@router.get("/{dataset_id}/download")
def download_dataset(
    dataset_id: str,
    output_type: str = Query("raw", pattern="^(raw|processed)$"),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download permitted raw or processed dataset file."""
    service = DatasetService(db)
    dataset = service.get_dataset(workspace_id=workspace.id, dataset_id=dataset_id)

    if output_type == "raw":
        if not dataset.storage_uri:
            raise HTTPException(status_code=404, detail="Dataset file not found.")
        abs_path = service.storage.resolve_path(dataset.storage_uri)
        filename = dataset.original_filename or f"{dataset.name}.csv"
        return FileResponse(path=abs_path, filename=filename, media_type="application/octet-stream")
    else:
        processed = service.dataset_repo.get_latest_processed(dataset_id=dataset.id)
        if not processed:
            raise HTTPException(status_code=404, detail="Processed dataset file not found. Run processing first.")
        abs_path = service.storage.resolve_path(processed.storage_uri)
        filename = f"{dataset.name}_cleaned.parquet"
        return FileResponse(path=abs_path, filename=filename, media_type="application/octet-stream")
