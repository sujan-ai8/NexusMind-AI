# NexusMind AI — Big Data Analytics & Data Engineering Architecture

## 1. Executive Summary

Phase 2 establishes the enterprise Big Data Analytics and distributed data engineering platform of **NexusMind AI**. The engine ingests large-scale cloud infrastructure workload telemetry traces, executes distributed data validation, cleaning, and transformations using Apache Spark (PySpark 4.3) and vectorized Pandas, computes multi-dimensional workload metrics, detects statistical anomalies without ML bias, and generates standardized Parquet feature stores for Phase 3 Advanced Machine Learning.

---

## 2. Distributed End-to-End Pipeline Architecture

```
                  RAW CLOUD TELEMETRY
          (CSV, JSON, JSONL, Multi-Node AWS Logs)
                           │
                           ▼
          ┌──────────────────────────────────┐
          │     Data Ingestion Subsystem     │
          │  • Multipart file streaming      │
          │  • MIME & extension validation   │
          │  • SHA-256 hash & size checking  │
          │  • Workspace-isolated storage    │
          └────────────────┬─────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │     Schema & Metadata Engine     │
          │  • Inferred column statistics    │
          │  • Auto-detected column mappings │
          │  • UTC timezone normalization    │
          └────────────────┬─────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │       Data Quality Engine        │
          │  • Deduplication                 │
          │  • Timestamp validity checking   │
          │  • Bound clipping [0%, 100%]     │
          │  • Negative value flooring       │
          │  • Median/Mode imputation        │
          │  • Rejected record segregation   │
          │  • 0-100 Quality Score formula   │
          └────────────────┬─────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │   PySpark 4.3 Processing Engine   │
          │  • Master: local[*]              │
          │  • Distributed transformation    │
          │  • Parquet output (Snappy)       │
          │  • Phase 3 ML Feature Store      │
          └────────────────┬─────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │     Cloud Intelligence Engine    │
          │  • CPU, Memory, Network, Storage │
          │  • Diurnal workload profiling    │
          │  • Efficiency (Idle/Downsizing)  │
          │  • Cost estimation (with warning)│
          │  • Z-score & IQR Anomaly Engine  │
          └────────────────┬─────────────────┘
                           │
                           ▼
          ┌──────────────────────────────────┐
          │     REST API & UI Dashboard      │
          │  • FastAPI asynchronous endpoints │
          │  • Recharts visual components    │
          │  • CSV/JSON/Parquet export engine │
          └──────────────────────────────────┘
```

---

## 3. Technology Matrix

| Layer | Component | Specification |
|---|---|---|
| **Distributed Processing** | PySpark / Apache Spark | Version 4.3.0, Java 21 LTS runtime |
| **Data Engine Fallback** | Vectorized Pandas & PyArrow | Pandas 2.2.2, PyArrow 24.0.0 |
| **Relational Storage** | PostgreSQL 16 / SQLite 3 | SQLAlchemy 2.0 ORM, Alembic Migrations |
| **Object / File Storage** | Local Storage Adapter | Partitioned by `/storage/{category}/{workspace_id}/{dataset_id}` |
| **Analytical Output** | Apache Parquet | Snappy compression, columnar binary layout |
| **API Layer** | FastAPI | Pydantic v2 validation, background workers |
| **Frontend Dashboard** | React 18, TypeScript, Tailwind | Recharts, shadcn/ui components |

---

## 4. Multi-Tenant Data Isolation

All data ingestion, storage directories, database queries, and processing jobs are partitioned strictly by `workspace_id`. Workspace isolation is enforced via database foreign keys (`ON DELETE CASCADE`) and repository queries with mandatory `where(Dataset.workspace_id == workspace_id)` filters.
