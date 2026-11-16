# Statistical Anomaly Detection Framework

## 1. Non-ML Detection Strategy

In Phase 2, anomaly detection is performed using **pure statistical and mathematical methodologies** to establish an unbiased baseline before introducing machine learning models in Phase 3.

---

## 2. Statistical Algorithms

### A. Z-Score (3-Sigma Threshold)
Identifies anomalies in approximately normally distributed baseline metrics (e.g., standard CPU and Memory usage):

$$Z = \frac{|x - \mu|}{\sigma}$$

- **Threshold**: $Z \ge 2.5$
- **Severity Mapping**:
  - $|Z| \ge 3.5$: **CRITICAL** (e.g., catastrophic flash spikes or node lockups)
  - $3.0 \le |Z| < 3.5$: **HIGH**
  - $2.5 \le |Z| < 3.0$: **MEDIUM**

### B. Interquartile Range (IQR Fence)
Used for non-Gaussian, bursty, or skewed metrics (e.g., incoming request rates or network ingress spikes):

$$\text{IQR} = Q_3 - Q_1$$
$$\text{Upper Fence} = Q_3 + 2.0 \times \text{IQR}$$

Values exceeding the upper fence are flagged as structural outliers.

---

## 3. Anomaly Persistence & Schema

Detected anomalies are stored in the `anomaly_events` table with:
- `timestamp`: Point in time of detection.
- `resource_id`: Targeted VM node or container ID.
- `metric_name`: Observed metric (`cpu_utilization`, `memory_utilization`, `workload_volume`).
- `observed_value`: Measured numeric value.
- `expected_range_min` & `expected_range_max`: Statistical fence boundary.
- `detection_method`: `Z_SCORE` or `IQR`.
- `severity`: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
- `explanation`: Contextual human-readable diagnostic message.
