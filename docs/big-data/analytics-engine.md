# Cloud Workload Intelligence & Analytics Engine

## 1. Overview

The Analytics Engine computes statistical metrics, saturation curves, resource efficiency, and financial run-rates from the cleaned Parquet analytical datasets.

---

## 2. Metric Computation Specifications

### A. CPU Utilization Metrics
- **Mean & P95**: Mean, median, minimum, maximum, and 95th percentile CPU consumption across the fleet.
- **Hourly Trends**: Hourly resampled timeseries curve suitable for diurnal cycle charting.
- **Service & Instance Breakdown**: Aggregated mean utilization grouped by logical microservice and VM node.

### B. Memory Utilization Metrics
- **Mean & P95**: Average memory percentage and peak saturation points.
- **Service Consumption**: Identification of memory-intensive services (e.g., catalog, cache, or batch workers).

### C. Network & Storage I/O
- **Ingress vs. Egress**: Cumulative gigabytes transferred and megabits-per-second throughput.
- **Storage Read/Write**: Aggregate IOPS and disk volume utilization rates.

### D. Workload Pattern Profiling
- **Request Volume**: Cumulative incoming request metrics and requests-per-minute rates.
- **Diurnal Cycles**: Morning ramp-up and evening drop-off modeling.

### E. Resource Efficiency & Right-Sizing
Nodes are categorized based on utilization envelopes:
- **IDLE**: Mean CPU $< 5.0\%$ and Mean Memory $< 15.0\%$ (Candidate for decommissioning or scheduled hibernation; 90% savings).
- **UNDERUTILIZED**: Mean CPU $< 20.0\%$ (Candidate for vertical downsizing; 40% savings).
- **OPTIMAL**: Mean CPU between $20.0\%$ and $75.0\%$.
- **HIGH_SATURATION**: Mean CPU $> 75.0\%$ (Candidate for scale-out).

### F. Cloud Cost Estimation
- Rates are calculated using configurable AWS instance benchmark pricing (e.g., `c6i.xlarge` @ $0.17/hr, `m6i.2xlarge` @ $0.384/hr).
- Prominent mandatory disclaimer displayed on all responses:
  > *"Estimated cost based on configured pricing assumptions."*
