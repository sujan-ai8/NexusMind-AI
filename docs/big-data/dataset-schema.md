# Standardized Cloud Workload Telemetry Schema

## 1. Field Specification

NexusMind AI standardizes all ingested telemetry to a unified 17-field cloud infrastructure schema:

| Field Name | Type | Mandatory | Allowed Range | Unit | Description |
|---|---|---|---|---|---|
| `timestamp` | Datetime (UTC) | **Yes** | ISO-8601 | UTC | Metric measurement timestamp |
| `instance_id` | String | No | Alphanumeric | - | Virtual machine, node, or container ID |
| `instance_type` | String | No | e.g., c6i.xlarge | - | Hardware instance tier or machine family |
| `service_name` | String | No | Text | - | Logical microservice or workload name |
| `application_name` | String | No | Text | - | High-level application system |
| `cloud_provider` | String | No | AWS, GCP, Azure | - | Origin cloud infrastructure provider |
| `cloud_region` | String | No | e.g., us-east-1 | - | Physical data center availability zone |
| `cpu_utilization` | Float | No | [0.0, 100.0] | % | CPU percentage consumption |
| `memory_utilization` | Float | No | [0.0, 100.0] | % | Memory percentage consumption |
| `network_in` | Float | No | >= 0.0 | MB/s | Network ingress rate |
| `network_out` | Float | No | >= 0.0 | MB/s | Network egress rate |
| `storage_utilization` | Float | No | [0.0, 100.0] | % | Disk volume utilization |
| `storage_read` | Float | No | >= 0.0 | MB/s | Disk read throughput |
| `storage_write` | Float | No | >= 0.0 | MB/s | Disk write throughput |
| `request_count` | Integer | No | >= 0 | req/interval | Total incoming HTTP/RPC requests |
| `workload_volume` | Integer | No | >= 0 | req/interval | Processed workload volume metric |
| `instance_cost` | Float | No | >= 0.0 | USD/hr | Actual or estimated instance hourly cost |
| `status` | String | No | RUNNING, etc. | - | Instance operational health state |

---

## 2. Alias Resolution Engine

The `SchemaNormalizer` automatically resolves heterogeneous vendor naming schemes:
- `cpu_utilization` ← `["cpu", "cpu_pct", "cpu_percent", "cpu_usage", "avg_cpu"]`
- `memory_utilization` ← `["mem", "mem_pct", "memory_usage", "avg_mem"]`
- `network_in` ← `["net_in", "bytes_in", "network_rx", "rx_bytes"]`
- `request_count` ← `["requests", "req_count", "calls", "transactions"]`
