from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from apps.api.app.models.entities import (
    Dataset,
    DatasetSchema,
    DatasetColumnMapping,
    DataQualityReport,
    ProcessedDataset,
    AnalyticsSnapshot,
    AnomalyEvent,
    CostConfiguration,
)


class DatasetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, dataset_id: str, workspace_id: str) -> Optional[Dataset]:
        return self.db.execute(
            select(Dataset).where(
                Dataset.id == dataset_id,
                Dataset.workspace_id == workspace_id,
            )
        ).scalar_one_or_none()

    def list_by_workspace(
        self,
        workspace_id: str,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dataset]:
        stmt = select(Dataset).where(Dataset.workspace_id == workspace_id)
        if search:
            stmt = stmt.where(Dataset.name.ilike(f"%{search}%"))
        stmt = stmt.order_by(Dataset.created_at.desc()).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_by_workspace(self, workspace_id: str) -> int:
        stmt = select(func.count(Dataset.id)).where(Dataset.workspace_id == workspace_id)
        return self.db.execute(stmt).scalar() or 0

    def create(self, dataset: Dataset) -> Dataset:
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def update(self, dataset: Dataset) -> Dataset:
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def delete(self, dataset: Dataset) -> None:
        self.db.delete(dataset)
        self.db.commit()

    # Schema info
    def get_schema(self, dataset_id: str) -> Optional[DatasetSchema]:
        return self.db.execute(
            select(DatasetSchema).where(DatasetSchema.dataset_id == dataset_id)
        ).scalar_one_or_none()

    def save_schema(self, schema: DatasetSchema) -> DatasetSchema:
        existing = self.get_schema(schema.dataset_id)
        if existing:
            existing.columns_json = schema.columns_json
            existing.detected_fields_json = schema.detected_fields_json
            self.db.commit()
            self.db.refresh(existing)
            return existing
        self.db.add(schema)
        self.db.commit()
        self.db.refresh(schema)
        return schema

    # Column mapping
    def get_column_mapping(self, dataset_id: str) -> Optional[DatasetColumnMapping]:
        return self.db.execute(
            select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
        ).scalar_one_or_none()

    def save_column_mapping(self, mapping: DatasetColumnMapping) -> DatasetColumnMapping:
        existing = self.get_column_mapping(mapping.dataset_id)
        if existing:
            existing.mapping_json = mapping.mapping_json
            existing.is_validated = mapping.is_validated
            self.db.commit()
            self.db.refresh(existing)
            return existing
        self.db.add(mapping)
        self.db.commit()
        self.db.refresh(mapping)
        return mapping

    # Quality Report
    def get_latest_quality_report(self, dataset_id: str) -> Optional[DataQualityReport]:
        stmt = (
            select(DataQualityReport)
            .where(DataQualityReport.dataset_id == dataset_id)
            .order_by(DataQualityReport.created_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_quality_report(self, report: DataQualityReport) -> DataQualityReport:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    # Processed Dataset
    def get_latest_processed(self, dataset_id: str) -> Optional[ProcessedDataset]:
        stmt = (
            select(ProcessedDataset)
            .where(ProcessedDataset.dataset_id == dataset_id)
            .order_by(ProcessedDataset.created_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_processed(self, processed: ProcessedDataset) -> ProcessedDataset:
        self.db.add(processed)
        self.db.commit()
        self.db.refresh(processed)
        return processed

    # Analytics Snapshot
    def get_latest_analytics(self, dataset_id: str) -> Optional[AnalyticsSnapshot]:
        stmt = (
            select(AnalyticsSnapshot)
            .where(AnalyticsSnapshot.dataset_id == dataset_id)
            .order_by(AnalyticsSnapshot.created_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_analytics(self, snapshot: AnalyticsSnapshot) -> AnalyticsSnapshot:
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    # Anomalies
    def list_anomalies(self, dataset_id: str, limit: int = 100) -> List[AnomalyEvent]:
        stmt = (
            select(AnomalyEvent)
            .where(AnomalyEvent.dataset_id == dataset_id)
            .order_by(AnomalyEvent.timestamp.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def save_anomalies(self, anomalies: List[AnomalyEvent]) -> None:
        for a in anomalies:
            self.db.add(a)
        self.db.commit()

    # Cost Configuration
    def get_cost_config(self, workspace_id: str) -> Optional[CostConfiguration]:
        stmt = select(CostConfiguration).where(CostConfiguration.workspace_id == workspace_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def save_cost_config(self, config: CostConfiguration) -> CostConfiguration:
        existing = self.get_cost_config(config.workspace_id)
        if existing:
            existing.compute_hourly_rates_json = config.compute_hourly_rates_json
            existing.currency = config.currency
            existing.storage_gb_month_rate = config.storage_gb_month_rate
            existing.network_egress_gb_rate = config.network_egress_gb_rate
            self.db.commit()
            self.db.refresh(existing)
            return existing
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
