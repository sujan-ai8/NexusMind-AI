# Cloud Workload Ingestion Pipeline

## 1. Overview

The NexusMind AI Ingestion Pipeline accepts raw cloud infrastructure telemetry in CSV, JSON, and JSONL formats. It supports both single and multi-node traces containing metrics such as CPU utilization, memory consumption, network throughput, disk I/O, request volumes, and estimated instance costs.

---

## 2. Ingestion Stages

1. **Upload & Streaming Validation**:
   - The user submits files via `POST /api/v1/datasets/upload` as multipart form data.
   - The engine validates file extensions (`.csv`, `.json`, `.jsonl`), verifies MIME types, and computes SHA-256 integrity checksums.
2. **Safe Workspace Storage**:
   - Uploaded files are routed to `/storage/raw/{workspace_id}/{dataset_id}/{filename}` through the `LocalStorageService`.
   - Directory traversal attacks (`../`) are strictly blocked by path resolution assertions.
3. **Automated Schema Inference**:
   - The file is quickly inspected for total row counts, column names, data types, and initial null counts.
   - Initial schema records are persisted to the `dataset_schemas` table.
4. **Column Alias Matching**:
   - The `SchemaNormalizer` tests raw column headers against known telemetry alias dictionaries (e.g., matching `cpu_pct` or `cpu_usage` to `cpu_utilization`).
   - Default column mapping is registered in `dataset_column_mappings`.
5. **State Transition**:
   - The dataset record moves from `UPLOADED` to `READY` status, making it immediately available for quality audits and PySpark processing.
