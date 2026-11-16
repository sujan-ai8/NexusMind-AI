import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from apps.api.app.models.entities import (
    Dataset,
    ProcessingJob,
    ProcessedDataset,
    AnalyticsSnapshot,
    AnomalyEvent,
)
from apps.api.app.repositories.audit_repository import AuditRepository
from apps.api.app.repositories.dataset_repository import DatasetRepository
from apps.api.app.repositories.job_repository import JobRepository
from apps.api.app.services.storage.local_storage import LocalStorageService
from apps.api.app.services.bigdata.schema_normalizer import SchemaNormalizer
from apps.api.app.services.bigdata.spark_engine import PySparkProcessingEngine
from apps.api.app.services.bigdata.analytics_engine import AnalyticsEngine


class ProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.dataset_repo = DatasetRepository(db)
        self.job_repo = JobRepository(db)
        self.audit_repo = AuditRepository(db)
        self.storage = LocalStorageService()
        self.normalizer = SchemaNormalizer()
        self.spark_engine = PySparkProcessingEngine()
        self.analytics_engine = AnalyticsEngine()

    def list_jobs(
        self,
        workspace_id: str,
        dataset_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        skip = (page - 1) * page_size
        items = self.job_repo.list_by_workspace(
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            skip=skip,
            limit=page_size,
        )
        total = self.job_repo.count_by_workspace(workspace_id=workspace_id, dataset_id=dataset_id)
        return {
            "jobs": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_job(self, workspace_id: str, job_id: str) -> ProcessingJob:
        job = self.job_repo.get_by_id(job_id=job_id, workspace_id=workspace_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Processing job {job_id} not found.",
            )
        return job

    def get_job_logs(self, workspace_id: str, job_id: str) -> List[Dict[str, Any]]:
        self.get_job(workspace_id=workspace_id, job_id=job_id)
        logs = self.job_repo.get_logs(job_id=job_id)
        return [
            {
                "id": l.id,
                "job_id": l.job_id,
                "level": l.level,
                "stage": l.stage,
                "message": l.message,
                "timestamp": l.timestamp,
            }
            for l in logs
        ]

    def create_processing_job(
        self,
        workspace_id: str,
        dataset_id: str,
        user_id: str,
        engine_preference: str = "PYSPARK",
        job_type: str = "DATASET_ETL_AND_ANALYTICS",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ProcessingJob:
        dataset = self.dataset_repo.get_by_id(dataset_id=dataset_id, workspace_id=workspace_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found.",
            )

        job = ProcessingJob(
            workspace_id=workspace_id,
            dataset_id=dataset.id,
            job_type=job_type,
            status="QUEUED",
            engine=engine_preference.upper(),
            progress=0,
            parameters_json=parameters or {"engine": engine_preference.upper()},
            started_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )
        created_job = self.job_repo.create(job)
        self.job_repo.add_log(created_job.id, f"Processing job created with engine: {job.engine}", "INFO", "INITIALIZE")

        return created_job

    def execute_processing_pipeline(
        self,
        workspace_id: str,
        job_id: str,
        user_id: str,
    ) -> ProcessingJob:
        job = self.get_job(workspace_id=workspace_id, job_id=job_id)
        dataset = self.dataset_repo.get_by_id(dataset_id=job.dataset_id, workspace_id=workspace_id)
        if not dataset:
            job.status = "FAILED"
            job.error_message = "Associated dataset not found."
            return self.job_repo.update(job)

        start_time = time.time()
        job.status = "RUNNING"
        job.progress = 10
        self.job_repo.update(job)
        self.job_repo.add_log(job.id, "Beginning dataset ingestion and verification stage...", "INFO", "INGESTION")

        try:
            # 1. Fetch column mapping
            mapping_record = self.dataset_repo.get_column_mapping(dataset.id)
            column_mapping = mapping_record.mapping_json if mapping_record else {}

            # 2. Resolve absolute file path
            raw_file_abs_path = self.storage.resolve_path(dataset.storage_uri)

            self.job_repo.add_log(job.id, f"Reading dataset from storage: {dataset.storage_uri}", "INFO", "READ")
            job.progress = 25
            self.job_repo.update(job)

            # 3. Execute PySpark / Pandas transformation engine
            self.job_repo.add_log(job.id, f"Initializing {job.engine} distributed transformation engine...", "INFO", "TRANSFORMATION")
            process_result = self.spark_engine.process_dataset(
                workspace_id=workspace_id,
                dataset_id=dataset.id,
                raw_file_path=raw_file_abs_path,
                file_format=dataset.file_format,
                column_mapping=column_mapping,
            )

            job.progress = 65
            job.records_processed = process_result["records_processed"]
            job.records_failed = process_result["records_failed"]
            self.job_repo.add_log(
                job.id,
                f"Data transformation completed. Valid records: {process_result['records_processed']}, Invalid: {process_result['records_failed']}",
                "INFO",
                "CLEANING",
            )
            self.job_repo.update(job)

            # 4. Save ProcessedDataset metadata
            processed_record = ProcessedDataset(
                dataset_id=dataset.id,
                job_id=job.id,
                workspace_id=workspace_id,
                storage_uri=process_result["processed_parquet_path"],
                feature_store_uri=process_result.get("features_parquet_path"),
                row_count=process_result["records_processed"],
                column_count=len(process_result["columns"]),
                schema_json={"columns": process_result["columns"]},
                engine_used=process_result["engine_used"],
                spark_config_json={"compression": process_result["compression"]},
                lineage_json={"raw_source": dataset.storage_uri, "transformed_at": datetime.now(timezone.utc).isoformat()},
            )
            self.dataset_repo.save_processed(processed_record)

            # 5. Execute Analytics and Statistical Anomaly Detection
            self.job_repo.add_log(job.id, "Executing cloud intelligence analytics and statistical anomaly detection...", "INFO", "ANALYTICS")
            job.progress = 80
            self.job_repo.update(job)

            # Get cost config if present
            cost_cfg = self.dataset_repo.get_cost_config(workspace_id)
            cost_rates = cost_cfg.compute_hourly_rates_json if cost_cfg else None

            analytics_result = self.analytics_engine.compute_all_analytics(
                cleaned_parquet_path=process_result["processed_parquet_path"],
                dataset_id=dataset.id,
                cost_rates=cost_rates,
            )

            # 6. Save AnalyticsSnapshot
            snapshot = AnalyticsSnapshot(
                dataset_id=dataset.id,
                workspace_id=workspace_id,
                job_id=job.id,
                snapshot_type="CLUSTER_TELEMETRY",
                data_json=analytics_result,
                metrics_json=analytics_result["overview"],
            )
            self.dataset_repo.save_analytics(snapshot)

            # 7. Save Anomaly Events
            anomaly_objects = []
            for anom in analytics_result.get("anomalies", []):
                anomaly_objects.append(
                    AnomalyEvent(
                        dataset_id=dataset.id,
                        workspace_id=workspace_id,
                        resource_id=anom["instance_id"],
                        timestamp=datetime.fromisoformat(anom["timestamp"]) if isinstance(anom["timestamp"], str) else anom["timestamp"],
                        metric_name=anom["metric_name"],
                        observed_value=anom["metric_value"],
                        expected_range_min=anom.get("details_json", {}).get("min", 0.0),
                        expected_range_max=anom.get("expected_value") or 100.0,
                        detection_method=anom["detection_method"],
                        severity=anom["severity"],
                        explanation=anom.get("details_json", {}).get("explanation", f"Anomaly detected in {anom['metric_name']}"),
                    )
                )
            if anomaly_objects:
                self.dataset_repo.save_anomalies(anomaly_objects)
                self.job_repo.add_log(job.id, f"Detected and recorded {len(anomaly_objects)} statistical anomaly events.", "INFO", "ANOMALIES")

            # 8. Complete Job
            duration_ms = int((time.time() - start_time) * 1000)
            job.status = "COMPLETED"
            job.progress = 100
            job.execution_duration_ms = duration_ms
            job.completed_at = datetime.now(timezone.utc)
            self.job_repo.update(job)
            self.job_repo.add_log(job.id, f"Job finished successfully in {duration_ms}ms.", "INFO", "COMPLETED")

            # Update dataset
            dataset.status = "PROCESSED"
            dataset.processing_engine = process_result["engine_used"]
            self.dataset_repo.update(dataset)

            self.audit_repo.log(
                action="PROCESSING_JOB_COMPLETED",
                resource_type="PROCESSING_JOB",
                workspace_id=workspace_id,
                user_id=user_id,
                resource_id=job.id,
                details_json={"records_processed": process_result["records_processed"], "duration_ms": duration_ms},
            )

            return job

        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            job.status = "FAILED"
            job.progress = 100
            job.execution_duration_ms = duration_ms
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            self.job_repo.update(job)
            self.job_repo.add_log(job.id, f"Execution failed: {str(exc)}", "ERROR", "FAILURE")

            dataset.status = "ERROR"
            self.dataset_repo.update(dataset)

            self.audit_repo.log(
                action="PROCESSING_JOB_FAILED",
                resource_type="PROCESSING_JOB",
                workspace_id=workspace_id,
                user_id=user_id,
                resource_id=job.id,
                details_json={"error": str(exc)},
            )
            return job

    def cancel_job(self, workspace_id: str, job_id: str, user_id: str) -> ProcessingJob:
        job = self.get_job(workspace_id=workspace_id, job_id=job_id)
        if job.status in ["COMPLETED", "FAILED", "CANCELLED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Job {job_id} cannot be cancelled because it is in status {job.status}.",
            )
        job.status = "CANCELLED"
        job.completed_at = datetime.now(timezone.utc)
        self.job_repo.update(job)
        self.job_repo.add_log(job.id, f"Job cancelled by user {user_id}", "WARN", "CANCEL")

        self.audit_repo.log(
            action="PROCESSING_JOB_CANCELLED",
            resource_type="PROCESSING_JOB",
            workspace_id=workspace_id,
            user_id=user_id,
            resource_id=job.id,
        )
        return job
