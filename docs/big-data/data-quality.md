# Data Quality Engine & Audit Framework

## 1. Quality Validation Philosophy

Data quality is a critical prerequisite for production analytics and machine learning. Ingested telemetry often suffers from duplicate timestamps, corrupted sensor records, out-of-bounds percentages, and missing attributes. The NexusMind AI Data Quality Engine executes automated deterministic audit rules prior to transformation.

---

## 2. Validation Checks & Rules

1. **Deduplication**:
   - Identifies exact duplicate rows across all telemetry attributes.
   - Retains the first occurrence and removes redundant records to prevent inflated throughput metrics.
2. **Timestamp Integrity**:
   - Identifies null, invalid, or unparseable timestamps.
   - Irrecoverably corrupted timestamp rows are segregated into `/storage/rejected/{workspace_id}/{dataset_id}/rejected_records.csv`.
3. **Bound Clipping [0.0%, 100.0%]**:
   - Clamps CPU and memory metrics exceeding 100% or below 0% to the valid interval.
4. **Non-Negative Flooring**:
   - Replaces negative values in network ingress/egress, storage read/write, and request volumes with 0.0.
5. **Configurable Imputation**:
   - **Numerical fields**: Imputed with the column median to avoid distortion from extreme outliers.
   - **Categorical fields**: Imputed with the column statistical mode.

---

## 3. Quality Score Formula

The overall data quality score is bounded between $0.0$ and $100.0$:

$$\text{Quality Score} = \max\left(0, 100 - \left( 30 \times \frac{N_{\text{duplicates}}}{N_{\text{total}}} + 50 \times \frac{N_{\text{rejected}}}{N_{\text{total}}} + 20 \times \frac{N_{\text{missing}}}{N_{\text{total}} \times N_{\text{cols}}} \right)\right)$$

- **PASSED**: Quality score $\ge 80.0\%$
- **WARNING**: Quality score between $60.0\%$ and $79.9\%$
- **FAILED**: Quality score $< 60.0\%$
