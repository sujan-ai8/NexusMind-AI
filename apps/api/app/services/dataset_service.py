import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from apps.api.app.models.entities import (
    Dataset,
    DatasetSchema,
    DatasetColumnMapping,
    DataQualityReport,
)
from apps.api.app.repositories.audit_repository import AuditRepository
from apps.api.app.repositories.dataset_repository import DatasetRepository
from apps.api.app.schemas.dataset import DatasetCreateRequest, DatasetResponse
from apps.api.app.services.storage.local_storage import LocalStorageService
from apps.api.app.services.bigdata.schema_normalizer import SchemaNormalizer
from apps.api.app.services.bigdata.data_quality import DataQualityEngine


class DatasetService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.audit_repo = AuditRepository(db)
        self.storage = LocalStorageService()
        self.normalizer = SchemaNormalizer()
        self.quality_engine = DataQualityEngine()

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

    def get_dataset(self, workspace_id: str, dataset_id: str) -> Dataset:
        dataset = self.dataset_repo.get_by_id(dataset_id=dataset_id, workspace_id=workspace_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found in workspace.",
            )
        return dataset

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
            original_filename=f"{payload.name.lower().replace(' ', '_')}.{payload.file_format.lower()}",
            file_format=payload.file_format.upper(),
            file_size_bytes=payload.file_size_bytes,
            storage_uri=payload.storage_uri or f"s3://nexusmind-datasets/{workspace_id}/{payload.name.lower().replace(' ', '_')}.csv",
            row_count=payload.row_count,
            column_count=0,
            status="READY",
            quality_status="PENDING",
            processing_engine="PYSPARK",
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

    def upload_dataset_file(
        self,
        workspace_id: str,
        user_id: str,
        filename: str,
        content: bytes,
        dataset_name: Optional[str] = None,
        description: Optional[str] = None,
        ip_address: str = "127.0.0.1",
    ) -> Dataset:
        # Validate format
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in ["csv", "json", "jsonl"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '.{ext}'. Supported formats are CSV, JSON, and JSONL.",
            )

        name = dataset_name.strip() if dataset_name else os.path.splitext(filename)[0]
        file_format = ext.upper()
        file_size = len(content)

        # Create preliminary dataset record to get UUID
        dataset = Dataset(
            workspace_id=workspace_id,
            name=name,
            description=description,
            original_filename=filename,
            file_format=file_format,
            file_size_bytes=file_size,
            storage_uri="",
            row_count=0,
            column_count=0,
            status="UPLOADED",
            quality_status="PENDING",
            processing_engine="PYSPARK",
            uploaded_by=user_id,
        )
        created = self.dataset_repo.create(dataset)

        # Save physical file
        storage_rel_path = self.storage.save_raw_upload(
            workspace_id=workspace_id,
            dataset_id=created.id,
            filename=filename,
            file_bytes=content,
        )
        created.storage_uri = storage_rel_path

        # Inspect preview, row count, column names
        preview_data = self.storage.get_dataset_preview(
            relative_path=storage_rel_path,
            file_format=file_format,
            limit=100,
        )
        created.row_count = preview_data["total_rows"]
        created.column_count = len(preview_data["columns"])
        created.status = "READY"
        self.dataset_repo.update(created)

        # Detect initial column mapping
        column_names = [c["column_name"] for c in preview_data["columns"]]
        detected_mapping = self.normalizer.detect_column_mapping(column_names)
        mapping_validation = self.normalizer.validate_mapping(detected_mapping)

        # Save Schema Info
        schema_record = DatasetSchema(
            dataset_id=created.id,
            columns_json={"columns": preview_data["columns"]},
            detected_fields_json=detected_mapping,
        )
        self.dataset_repo.save_schema(schema_record)

        # Save mapping
        mapping_record = DatasetColumnMapping(
            dataset_id=created.id,
            mapping_json=detected_mapping,
            is_validated=mapping_validation["is_valid"],
        )
        self.dataset_repo.save_column_mapping(mapping_record)

        # Log audit
        self.audit_repo.log(
            action="DATASET_UPLOADED",
            resource_type="DATASET",
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=created.id,
            details_json={
                "name": created.name,
                "filename": filename,
                "file_size": file_size,
                "rows": created.row_count,
                "columns": created.column_count,
            },
            ip_address=ip_address,
        )

        return created

    def get_dataset_preview(
        self,
        workspace_id: str,
        dataset_id: str,
        limit: int = 100,
        page: int = 1,
    ) -> Dict[str, Any]:
        dataset = self.get_dataset(workspace_id=workspace_id, dataset_id=dataset_id)
        preview_data = self.storage.get_dataset_preview(
            relative_path=dataset.storage_uri,
            file_format=dataset.file_format,
            limit=limit,
        )
        return {
            "dataset_id": dataset.id,
            "total_rows": preview_data["total_rows"],
            "columns": preview_data["columns"],
            "rows": preview_data["rows"],
            "summary": {
                "file_name": dataset.original_filename or dataset.name,
                "file_size_bytes": dataset.file_size_bytes,
                "format": dataset.file_format,
                "total_columns": dataset.column_count,
            },
        }

    def get_schema(self, workspace_id: str, dataset_id: str) -> Dict[str, Any]:
        dataset = self.get_dataset(workspace_id=workspace_id, dataset_id=dataset_id)
        schema = self.dataset_repo.get_schema(dataset_id=dataset.id)
        if not schema:
            preview_data = self.storage.get_dataset_preview(
                relative_path=dataset.storage_uri,
                file_format=dataset.file_format,
                limit=10,
            )
            col_names = [c["column_name"] for c in preview_data["columns"]]
            detected_mapping = self.normalizer.detect_column_mapping(col_names)
            schema = DatasetSchema(
                dataset_id=dataset.id,
                columns_json={"columns": preview_data["columns"]},
                detected_fields_json=detected_mapping,
            )
            schema = self.dataset_repo.save_schema(schema)

        cols = schema.columns_json.get("columns", []) if isinstance(schema.columns_json, dict) else schema.columns_json
        return {
            "dataset_id": dataset.id,
            "columns": cols,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "detected_fields": schema.detected_fields_json,
            "inferred_at": schema.created_at,
        }

    def get_column_mapping(self, workspace_id: str, dataset_id: str) -> Dict[str, Any]:
        dataset = self.get_dataset(workspace_id=workspace_id, dataset_id=dataset_id)
        mapping_record = self.dataset_repo.get_column_mapping(dataset_id=dataset.id)
        if not mapping_record:
            schema_data = self.get_schema(workspace_id=workspace_id, dataset_id=dataset.id)
            column_names = [c["column_name"] for c in schema_data["columns"]]
            detected_mapping = self.normalizer.detect_column_mapping(column_names)
            validation = self.normalizer.validate_mapping(detected_mapping)
            mapping_record = DatasetColumnMapping(
                dataset_id=dataset.id,
                mapping_json=detected_mapping,
                is_validated=validation["is_valid"],
            )
            mapping_record = self.dataset_repo.save_column_mapping(mapping_record)
        else:
            validation = self.normalizer.validate_mapping(mapping_record.mapping_json)

        return {
            "dataset_id": dataset.id,
            "mapping": mapping_record.mapping_json,
            "is_valid": mapping_record.is_validated,
            "missing_required_fields": validation["missing_required"],
            "updated_at": mapping_record.updated_at,
        }

    def update_column_mapping(
        self,
        workspace_id: str,
        dataset_id: str,
        mapping: Dict[str, str],
        user_id: str,
    ) -> Dict[str, Any]:
        dataset = self.get_dataset(workspace_id=workspace_id, dataset_id=dataset_id)
        validation = self.normalizer.validate_mapping(mapping)

        mapping_record = DatasetColumnMapping(
            dataset_id=dataset.id,
            mapping_json=mapping,
            is_validated=validation["is_valid"],
        )
        saved = self.dataset_repo.save_column_mapping(mapping_record)

        self.audit_repo.log(
            action="DATASET_MAPPING_UPDATED",
            resource_type="DATASET",
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=dataset.id,
            details_json={"is_valid": saved.is_validated, "mapping": mapping},
        )

        return {
            "dataset_id": dataset.id,
            "mapping": saved.mapping_json,
            "is_valid": saved.is_validated,
            "missing_required_fields": validation["missing_required"],
            "updated_at": saved.updated_at,
        }

    def run_quality_audit(
        self,
        workspace_id: str,
        dataset_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        dataset = self.get_dataset(workspace_id=workspace_id, dataset_id=dataset_id)
        mapping_res = self.get_column_mapping(workspace_id=workspace_id, dataset_id=dataset.id)
        mapping = mapping_res["mapping"]

        # Read dataset into dataframe
        df = self.storage.read_raw_dataframe(dataset.storage_uri, dataset.file_format)

        # Audit using DataQualityEngine
        audit_result = self.quality_engine.audit_dataset(df, mapping)

        # Save DataQualityReport
        report = DataQualityReport(
            dataset_id=dataset.id,
            workspace_id=workspace_id,
            total_records=audit_result["total_records"],
            valid_records=audit_result["valid_records"],
            invalid_records=audit_result["invalid_records"],
            duplicate_records=audit_result["duplicate_records_count"],
            missing_values_count=audit_result["missing_values_count"],
            corrected_records=audit_result["metrics"].get("corrected_records", 0),
            rejected_records=audit_result["metrics"].get("rejected_records", 0),
            quality_score=audit_result["quality_score"],
            status="PASSED" if audit_result["quality_score"] >= 80.0 else ("WARNING" if audit_result["quality_score"] >= 60.0 else "FAILED"),
            issues_json={"issues": audit_result["issues"]},
            cleaning_actions_json={"actions": audit_result["metrics"].get("cleaning_actions", [])},
        )
        saved_report = self.dataset_repo.save_quality_report(report)

        # Update dataset status
        dataset.quality_status = "PASSED" if audit_result["quality_score"] >= 70.0 else "WARNING"
        dataset.quality_score = audit_result["quality_score"]
        self.dataset_repo.update(dataset)

        self.audit_repo.log(
            action="DATA_QUALITY_AUDIT",
            resource_type="DATASET",
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=dataset.id,
            details_json={
                "quality_score": audit_result["quality_score"],
                "quality_status": dataset.quality_status,
            },
        )

        return {
            "id": saved_report.id,
            "dataset_id": dataset.id,
            "workspace_id": workspace_id,
            "quality_score": saved_report.quality_score,
            "quality_status": dataset.quality_status,
            "total_records": saved_report.total_records,
            "valid_records": saved_report.valid_records,
            "invalid_records": saved_report.invalid_records,
            "missing_values_count": saved_report.missing_values_count,
            "duplicate_records_count": saved_report.duplicate_records,
            "out_of_bound_records_count": 0,
            "metrics": audit_result["metrics"],
            "issues": audit_result["issues"],
            "created_at": saved_report.created_at,
        }

    def get_latest_quality_report(self, workspace_id: str, dataset_id: str) -> Optional[Dict[str, Any]]:
        dataset = self.get_dataset(workspace_id=workspace_id, dataset_id=dataset_id)
        report = self.dataset_repo.get_latest_quality_report(dataset_id=dataset.id)
        if not report:
            return None
        issues = report.issues_json.get("issues", []) if isinstance(report.issues_json, dict) else report.issues_json
        return {
            "id": report.id,
            "dataset_id": dataset.id,
            "workspace_id": workspace_id,
            "quality_score": report.quality_score,
            "quality_status": dataset.quality_status,
            "total_records": report.total_records,
            "valid_records": report.valid_records,
            "invalid_records": report.invalid_records,
            "missing_values_count": report.missing_values_count,
            "duplicate_records_count": report.duplicate_records,
            "out_of_bound_records_count": 0,
            "metrics": report.cleaning_actions_json,
            "issues": issues,
            "created_at": report.created_at,
        }

    def delete_dataset(self, workspace_id: str, dataset_id: str, user_id: str) -> None:
        dataset = self.get_dataset(workspace_id=workspace_id, dataset_id=dataset_id)
        # Delete local files if exist
        if dataset.storage_uri:
            self.storage.delete_file(dataset.storage_uri)

        name = dataset.name
        self.dataset_repo.delete(dataset)

        self.audit_repo.log(
            action="DATASET_DELETED",
            resource_type="DATASET",
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=dataset_id,
            details_json={"name": name},
        )
