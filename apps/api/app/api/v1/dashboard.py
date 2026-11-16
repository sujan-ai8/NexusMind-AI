from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_active_workspace, get_current_user
from apps.api.app.models.entities import User, Workspace
from apps.api.app.schemas.common import APIResponse
from apps.api.app.schemas.dashboard import ActivityItemResponse, DashboardSummaryResponse
from apps.api.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=APIResponse[DashboardSummaryResponse], status_code=status.HTTP_200_OK)
def get_dashboard_summary(
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve telemetry summaries and high-level KPIs for the active workspace.
    Telemetry values are explicitly tagged as simulated DEMO DATA during Phase 1.
    """
    service = DashboardService(db)
    summary = service.get_summary(workspace)
    return APIResponse(
        success=True,
        message="Dashboard summary retrieved",
        data=summary,
    )


@router.get("/activity", response_model=APIResponse[List[ActivityItemResponse]], status_code=status.HTTP_200_OK)
def get_dashboard_activity(
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve recent operational activity and audit logs for the active workspace."""
    service = DashboardService(db)
    activities = service.get_recent_activity(workspace.id)
    return APIResponse(
        success=True,
        message="Recent activity retrieved",
        data=activities,
    )

