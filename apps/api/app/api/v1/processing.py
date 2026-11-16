from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_active_workspace, get_current_user, require_workspace_role
from apps.api.app.models.entities import User, Workspace
from apps.api.app.models.enums import RoleEnum
from apps.api.app.schemas.common import APIResponse, PaginatedResponse
from apps.api.app.schemas.bigdata import ProcessingJobResponse, ProcessingLogResponse
from apps.api.app.services.bigdata.processing_service import ProcessingService

router = APIRouter(prefix="/processing", tags=["Distributed Processing Engine"])


@router.get("/jobs", response_model=APIResponse[PaginatedResponse[ProcessingJobResponse]], status_code=status.HTTP_200_OK)
def list_processing_jobs(
    dataset_id: Optional[str] = Query(None, description="Filter by dataset ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List distributed processing jobs in the active workspace."""
    service = ProcessingService(db)
    result = service.list_jobs(
        workspace_id=workspace.id,
        dataset_id=dataset_id,
        page=page,
        page_size=page_size,
    )
    items = [ProcessingJobResponse.model_validate(j) for j in result["jobs"]]
    total = result["total"]
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return APIResponse(
        success=True,
        message="Processing jobs retrieved",
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get("/jobs/{job_id}", response_model=APIResponse[ProcessingJobResponse], status_code=status.HTTP_200_OK)
def get_processing_job(
    job_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve details, status, and metrics for a specific processing job."""
    service = ProcessingService(db)
    job = service.get_job(workspace_id=workspace.id, job_id=job_id)
    return APIResponse(
        success=True,
        message="Job details retrieved",
        data=ProcessingJobResponse.model_validate(job),
    )


@router.post("/jobs/{job_id}/cancel", response_model=APIResponse[ProcessingJobResponse], status_code=status.HTTP_200_OK)
def cancel_processing_job(
    job_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    _role=Depends(require_workspace_role(RoleEnum.ANALYST)),
):
    """Cancel a running or pending processing job."""
    service = ProcessingService(db)
    job = service.cancel_job(workspace_id=workspace.id, job_id=job_id, user_id=current_user.id)
    return APIResponse(
        success=True,
        message="Job cancelled",
        data=ProcessingJobResponse.model_validate(job),
    )


@router.get("/jobs/{job_id}/logs", response_model=APIResponse[List[ProcessingLogResponse]], status_code=status.HTTP_200_OK)
def get_processing_job_logs(
    job_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch chronological execution logs for a processing job."""
    service = ProcessingService(db)
    logs = service.get_job_logs(workspace_id=workspace.id, job_id=job_id)
    return APIResponse(
        success=True,
        message="Job logs retrieved",
        data=[ProcessingLogResponse(**l) for l in logs],
    )
