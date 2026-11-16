from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from apps.api.app.models.enums import DatasetStatusEnum


class DatasetCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = Field(None, max_length=500)
    file_format: str = Field(default="CSV")
    file_size_bytes: int = Field(default=1024)
    storage_uri: Optional[str] = Field(default="s3://nexusmind-sample-storage/datasets/initial.csv")
    row_count: int = Field(default=0)


class DatasetResponse(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    original_filename: Optional[str] = None
    file_format: str
    file_size_bytes: int
    storage_uri: str
    row_count: int
    column_count: Optional[int] = 0
    status: str
    quality_status: Optional[str] = "PENDING"
    quality_score: Optional[float] = None
    processing_engine: Optional[str] = "PYSPARK"
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
