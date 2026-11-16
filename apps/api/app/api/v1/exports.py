import json
import os
import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
import pandas as pd
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.dependencies.auth import get_active_workspace, get_current_user
from apps.api.app.models.entities import Dataset, ProcessedDataset, User, Workspace
from apps.api.app.schemas.common import APIResponse
from apps.api.app.services.storage.local_storage import LocalStorageService
from apps.api.app.services.bigdata.analytics_engine import AnalyticsEngine

router = APIRouter(prefix="/exports", tags=["Data & Analytics Export"])


class ExportRequest(BaseModel):
    dataset_id: str
    export_format: str = Field(default="CSV", pattern="^(CSV|JSON|PARQUET)$")
    report_type: str = Field(default="ANALYTICS_SUMMARY", pattern="^(ANALYTICS_SUMMARY|PROCESSED_DATA|ANOMALIES)$")


# In-memory export registry for local development storage
_EXPORTS_STORE: Dict[str, Dict[str, Any]] = {}


@router.post("/analytics", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_201_CREATED)
def create_export(
    payload: ExportRequest,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate an export artifact for cloud intelligence analytics or processed datasets."""
    storage = LocalStorageService()
    export_id = str(uuid.uuid4())
    fmt = payload.export_format.upper()
    ext = "csv" if fmt == "CSV" else ("json" if fmt == "JSON" else "parquet")

    export_dir = os.path.join(storage.base_dir, "exports", workspace.id)
    os.makedirs(export_dir, exist_ok=True)
    filename = f"export_{payload.report_type.lower()}_{export_id[:8]}.{ext}"
    target_abs_path = os.path.join(export_dir, filename)

    # Fetch dataset
    from apps.api.app.api.v1.analytics import _resolve_analytics_df
    dataset, df = _resolve_analytics_df(db, workspace.id, payload.dataset_id)
    if dataset is None or df is None or len(df) == 0:
        raise HTTPException(status_code=400, detail="Cannot export: dataset has no processed data.")

    if payload.report_type == "PROCESSED_DATA":
        export_df = df
    elif payload.report_type == "ANOMALIES":
        engine = AnalyticsEngine()
        anomalies = engine.detect_statistical_anomalies(df, dataset_id=dataset.id, workspace_id=workspace.id)
        export_df = pd.DataFrame([a.model_dump() for a in anomalies])
    else:  # ANALYTICS_SUMMARY
        engine = AnalyticsEngine()
        computed = engine.compute_all_analytics(
            cleaned_parquet_path=storage.resolve_path(
                db.query(ProcessedDataset)
                .filter(ProcessedDataset.dataset_id == dataset.id)
                .first()
                .storage_uri
            )
            if db.query(ProcessedDataset).filter(ProcessedDataset.dataset_id == dataset.id).first()
            else "",
            dataset_id=dataset.id,
        ) if db.query(ProcessedDataset).filter(ProcessedDataset.dataset_id == dataset.id).first() else {"overview": {}}
        export_df = pd.DataFrame([computed.get("overview", {})])

    # Save to disk
    if fmt == "CSV":
        export_df.to_csv(target_abs_path, index=False)
    elif fmt == "JSON":
        export_df.to_json(target_abs_path, orient="records", date_format="iso", indent=2)
    elif fmt == "PARQUET":
        export_df.to_parquet(target_abs_path, index=False, engine="pyarrow")

    file_size = os.path.getsize(target_abs_path)

    export_meta = {
        "export_id": export_id,
        "workspace_id": workspace.id,
        "dataset_id": dataset.id,
        "report_type": payload.report_type,
        "export_format": fmt,
        "filename": filename,
        "file_size_bytes": file_size,
        "status": "COMPLETED",
        "local_path": target_abs_path,
        "download_url": f"/api/v1/exports/{export_id}/download",
    }
    _EXPORTS_STORE[export_id] = export_meta

    return APIResponse(
        success=True,
        message="Export artifact created successfully",
        data={
            "export_id": export_id,
            "filename": filename,
            "format": fmt,
            "file_size_bytes": file_size,
            "status": "COMPLETED",
            "download_url": f"/api/v1/exports/{export_id}/download",
        },
    )


@router.get("/{export_id}", response_model=APIResponse[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_export_status(
    export_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
):
    """Retrieve status and metadata of an export task."""
    meta = _EXPORTS_STORE.get(export_id)
    if not meta or meta.get("workspace_id") != workspace.id:
        raise HTTPException(status_code=404, detail=f"Export {export_id} not found.")

    return APIResponse(
        success=True,
        message="Export details retrieved",
        data={
            "export_id": meta["export_id"],
            "report_type": meta["report_type"],
            "format": meta["export_format"],
            "filename": meta["filename"],
            "file_size_bytes": meta["file_size_bytes"],
            "status": meta["status"],
            "download_url": meta["download_url"],
        },
    )


@router.get("/{export_id}/download")
def download_export(
    export_id: str,
    workspace: Workspace = Depends(get_active_workspace),
    current_user: User = Depends(get_current_user),
):
    """Download the generated export artifact file."""
    meta = _EXPORTS_STORE.get(export_id)
    if not meta or meta.get("workspace_id") != workspace.id:
        raise HTTPException(status_code=404, detail=f"Export {export_id} not found.")

    abs_path = meta["local_path"]
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Export file has expired or was removed.")

    return FileResponse(
        path=abs_path,
        filename=meta["filename"],
        media_type="application/octet-stream",
    )
