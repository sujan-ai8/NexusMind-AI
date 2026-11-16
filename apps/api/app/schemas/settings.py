from typing import Any, Dict, Optional
from pydantic import BaseModel


class SystemSettingsResponse(BaseModel):
    app_name: str
    version: str
    environment: str
    database_type: str
    supported_cloud_providers: list[str]
    max_upload_size_mb: int
    features_enabled: Dict[str, bool]


class UserProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

