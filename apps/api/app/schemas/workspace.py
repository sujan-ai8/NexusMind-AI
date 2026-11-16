from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from apps.api.app.models.enums import CloudProviderEnum, RoleEnum, WorkspaceTypeEnum


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Production Cloud Ops"})
    description: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "Primary cloud monitoring workspace"})
    type: WorkspaceTypeEnum = Field(default=WorkspaceTypeEnum.ENTERPRISE)
    cloud_provider: CloudProviderEnum = Field(default=CloudProviderEnum.AWS)


class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[WorkspaceTypeEnum] = None
    cloud_provider: Optional[CloudProviderEnum] = None


class WorkspaceMemberResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    role: RoleEnum
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceSettingsResponse(BaseModel):
    id: str
    workspace_id: str
    telemetry_enabled: bool
    aws_region: str
    alert_email: Optional[str] = None
    cost_threshold: float
    max_concurrent_jobs: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceSettingsUpdateRequest(BaseModel):
    telemetry_enabled: Optional[bool] = None
    aws_region: Optional[str] = None
    alert_email: Optional[str] = None
    cost_threshold: Optional[float] = None
    max_concurrent_jobs: Optional[int] = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    type: str
    cloud_provider: str
    owner_id: str
    role: Optional[str] = None  # Current user's role in this workspace
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

