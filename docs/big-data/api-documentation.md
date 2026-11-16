# Big Data & Analytics REST API Specification

## 1. Authentication & Headers

All endpoints require authentication via Bearer token and active workspace header:
```http
Authorization: Bearer <access_token>
X-Workspace-Id: <workspace_uuid>
```

---

## 2. Dataset Management Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/datasets/upload` | Ingests raw telemetry file (CSV/JSON/JSONL). |
| `GET` | `/api/v1/datasets` | Paginated listing of datasets with search filter. |
| `GET` | `/api/v1/datasets/{id}` | Metadata for a specific dataset. |
| `DELETE` | `/api/v1/datasets/{id}` | Deletes dataset and all associated parquet files. |
| `GET` | `/api/v1/datasets/{id}/preview` | Returns first 100 rows, columns, and data types. |
| `GET` | `/api/v1/datasets/{id}/schema` | Retrieves detected schema and column stats. |
| `GET` | `/api/v1/datasets/{id}/column-mapping` | Retrieves active column mapping. |
| `POST` | `/api/v1/datasets/{id}/column-mapping` | Saves customized column mappings. |
| `POST` | `/api/v1/datasets/{id}/validate` | Validates mapping against standard schema. |
| `POST` | `/api/v1/datasets/{id}/quality/audit` | Executes data quality audit. |
| `GET` | `/api/v1/datasets/{id}/quality` | Retrieves latest data quality report. |
| `POST` | `/api/v1/datasets/{id}/process` | Submits PySpark/Pandas transformation job. |
| `GET` | `/api/v1/datasets/{id}/download` | Downloads raw or processed dataset file. |

---

## 3. Distributed Processing Job Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/processing/jobs` | Lists processing jobs in the workspace. |
| `GET` | `/api/v1/processing/jobs/{id}` | Status, engine, duration, and records processed. |
| `POST` | `/api/v1/processing/jobs/{id}/cancel` | Cancels a running or queued job. |
| `GET` | `/api/v1/processing/jobs/{id}/logs` | Returns stage-by-stage execution logs. |

---

## 4. Cloud Intelligence Analytics Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/analytics/overview` | Executive telemetry summary and fleet KPIs. |
| `GET` | `/api/v1/analytics/cpu` | Mean, peak, P95, and hourly CPU timeline. |
| `GET` | `/api/v1/analytics/memory` | Mean, peak, and service memory saturation. |
| `GET` | `/api/v1/analytics/network` | Ingress and egress transfer volumes and rates. |
| `GET` | `/api/v1/analytics/storage` | Disk utilization and throughput metrics. |
| `GET` | `/api/v1/analytics/workload` | Request volume distribution and cycles. |
| `GET` | `/api/v1/analytics/resources` | Idle/underutilized instances and cost savings. |
| `GET` | `/api/v1/analytics/cost` | Estimated infrastructure run-rate with disclaimer. |
| `GET` | `/api/v1/analytics/anomalies` | Detected Z-score and IQR statistical anomalies. |
| `GET` | `/api/v1/analytics/data-quality` | Data quality score and issue breakdown. |

---

## 5. Export Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/exports/analytics` | Generates CSV, JSON, or Parquet export artifact. |
| `GET` | `/api/v1/exports/{id}` | Status and file size of export task. |
| `GET` | `/api/v1/exports/{id}/download` | Streams generated export file. |
