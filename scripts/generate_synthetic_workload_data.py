import math
import os
import random
from datetime import datetime, timedelta, timezone
import pandas as pd


def generate_synthetic_telemetry(
    output_path: str = "data/sample_cloud_workload_telemetry.csv",
    days: int = 14,
    interval_minutes: int = 15,
) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    random.seed(42)

    instances = [
        {"id": "i-0a1b2c3d4e01", "type": "c6i.xlarge", "svc": "api-gateway", "app": "nexus-web", "reg": "us-east-1", "pattern": "web"},
        {"id": "i-0a1b2c3d4e02", "type": "c6i.xlarge", "svc": "api-gateway", "app": "nexus-web", "reg": "us-east-1", "pattern": "web"},
        {"id": "i-0b2c3d4e5f01", "type": "t3.medium", "svc": "auth-service", "app": "nexus-auth", "reg": "us-east-1", "pattern": "steady"},
        {"id": "i-0b2c3d4e5f02", "type": "t3.medium", "svc": "auth-service", "app": "nexus-auth", "reg": "us-east-1", "pattern": "steady"},
        {"id": "i-0c3d4e5f6a01", "type": "m6i.xlarge", "svc": "payment-processor", "app": "nexus-billing", "reg": "us-east-1", "pattern": "bursty"},
        {"id": "i-0d4e5f6a7b01", "type": "m6i.2xlarge", "svc": "product-catalog", "app": "nexus-store", "reg": "us-east-1", "pattern": "memory_heavy"},
        {"id": "i-0e5f6a7b8c01", "type": "c6i.2xlarge", "svc": "data-ingestion", "app": "nexus-pipeline", "reg": "us-east-1", "pattern": "batch"},
        {"id": "i-0f6a7b8c9d01", "type": "t3.medium", "svc": "standby-worker", "app": "nexus-standby", "reg": "us-east-1", "pattern": "idle"},
        {"id": "i-0f6a7b8c9d02", "type": "t3.large", "svc": "standby-backup", "app": "nexus-standby", "reg": "us-east-1", "pattern": "underutilized"},
        {"id": "i-0a9b8c7d6e01", "type": "r6i.xlarge", "svc": "analytics-worker", "app": "nexus-analytics", "reg": "us-east-1", "pattern": "memory_leak"},
    ]

    base_time = datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    total_steps = int((days * 24 * 60) / interval_minutes)

    rows = []

    for step in range(total_steps):
        current_time = base_time + timedelta(minutes=step * interval_minutes)
        hour = current_time.hour
        weekday = current_time.weekday()
        is_weekend = weekday >= 5

        # Diurnal pattern (peak at 14:00 UTC, trough at 04:00 UTC)
        diurnal_factor = (math.sin((hour - 8) / 24 * 2 * math.pi) + 1.0) / 2.0  # 0 to 1
        weekend_mult = 0.6 if is_weekend else 1.0

        for inst in instances:
            p = inst["pattern"]

            if p == "web":
                base_cpu = 30.0 + (diurnal_factor * 40.0 * weekend_mult) + random.uniform(-4, 4)
                base_mem = 45.0 + (diurnal_factor * 20.0) + random.uniform(-2, 2)
                req_count = int((1200 + diurnal_factor * 3500 * weekend_mult) + random.randint(-100, 100))
                net_in = round(15.0 + diurnal_factor * 45.0 + random.uniform(-2, 2), 2)
                net_out = round(35.0 + diurnal_factor * 85.0 + random.uniform(-3, 3), 2)

            elif p == "steady":
                base_cpu = 22.0 + random.uniform(-3, 3)
                base_mem = 38.0 + random.uniform(-1, 1)
                req_count = int(350 + random.randint(-30, 30))
                net_in = round(4.0 + random.uniform(-0.5, 0.5), 2)
                net_out = round(6.0 + random.uniform(-0.5, 0.5), 2)

            elif p == "bursty":
                # Regular traffic with occasional flash sale spike
                is_flash_sale = (step % 180 == 45)  # Spike every ~45 hours
                spike_add = 55.0 if is_flash_sale else 0.0
                base_cpu = 25.0 + (diurnal_factor * 20.0) + spike_add + random.uniform(-3, 3)
                base_mem = 40.0 + (spike_add * 0.4) + random.uniform(-2, 2)
                req_count = int((500 + (spike_add * 70)) + random.randint(-40, 40))
                net_in = round(8.0 + (spike_add * 0.8) + random.uniform(-1, 1), 2)
                net_out = round(14.0 + (spike_add * 1.5) + random.uniform(-1, 1), 2)

            elif p == "memory_heavy":
                base_cpu = 35.0 + (diurnal_factor * 15.0) + random.uniform(-3, 3)
                base_mem = 72.0 + (diurnal_factor * 12.0) + random.uniform(-1.5, 1.5)
                req_count = int(850 + random.randint(-50, 50))
                net_in = round(18.0 + random.uniform(-2, 2), 2)
                net_out = round(22.0 + random.uniform(-2, 2), 2)

            elif p == "batch":
                # Batch job kicks off daily at 02:00 to 05:00 UTC
                is_batch_window = 2 <= hour <= 5
                batch_cpu = 88.0 if is_batch_window else 12.0
                base_cpu = batch_cpu + random.uniform(-4, 4)
                base_mem = 65.0 if is_batch_window else 20.0
                req_count = int(100 if not is_batch_window else 4200)
                net_in = round(55.0 if is_batch_window else 2.0, 2)
                net_out = round(70.0 if is_batch_window else 3.0, 2)

            elif p == "idle":
                base_cpu = random.uniform(1.2, 3.8)
                base_mem = random.uniform(8.5, 12.0)
                req_count = random.randint(0, 5)
                net_in = round(random.uniform(0.1, 0.4), 2)
                net_out = round(random.uniform(0.1, 0.4), 2)

            elif p == "underutilized":
                base_cpu = random.uniform(8.0, 16.0)
                base_mem = random.uniform(15.0, 22.0)
                req_count = random.randint(20, 60)
                net_in = round(random.uniform(0.5, 1.8), 2)
                net_out = round(random.uniform(0.8, 2.5), 2)

            elif p == "memory_leak":
                # Memory slowly grows from 30% to 96% over 10 days, then restarts
                leak_cycle_step = step % (10 * 24 * 4)
                leak_pct = (leak_cycle_step / (10 * 24 * 4)) * 65.0
                base_cpu = 30.0 + (diurnal_factor * 15.0) + random.uniform(-2, 2)
                base_mem = 28.0 + leak_pct + random.uniform(-1, 1)
                req_count = int(400 + random.randint(-30, 30))
                net_in = round(8.0 + random.uniform(-1, 1), 2)
                net_out = round(12.0 + random.uniform(-1, 1), 2)

            # Bounds clamping
            cpu = max(0.5, min(99.8, round(base_cpu, 2)))
            mem = max(5.0, min(99.5, round(base_mem, 2)))
            storage_util = round(45.0 + (step / total_steps) * 8.0, 2)
            storage_read = round(12.5 + random.uniform(0, 15), 2)
            storage_write = round(8.0 + random.uniform(0, 10), 2)

            rows.append({
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "instance_id": inst["id"],
                "instance_type": inst["type"],
                "service_name": inst["svc"],
                "application_name": inst["app"],
                "cloud_provider": "AWS",
                "cloud_region": inst["reg"],
                "cpu_utilization": cpu,
                "memory_utilization": mem,
                "network_in": net_in,
                "network_out": net_out,
                "storage_utilization": storage_util,
                "storage_read": storage_read,
                "storage_write": storage_write,
                "request_count": req_count,
                "workload_volume": req_count,
                "status": "RUNNING",
            })

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"Synthetic cloud workload dataset created: {output_path} ({len(df)} rows, {len(df.columns)} columns)")
    return output_path


if __name__ == "__main__":
    generate_synthetic_telemetry()
