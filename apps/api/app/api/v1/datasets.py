from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_active_workspace, get_current_user, require_workspace_role
from apps.api.app.models.entities import User, Workspace
from apps.api.app.models.enums import RoleEnum
from apps.api.app.schemas.common import APIResponse, PaginatedResponse
from apps.api.app.schemas.dataset import DatasetCreateRequest, DatasetResponse
from apps.api.app.services.dataset_service import DatasetService

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

