import io
import os
import pytest
from apps.api.app.models.entities import Workspace, WorkspaceMember
from apps.api.app.models.enums import RoleEnum


def get_auth_headers(client, user, workspace_id):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "Password123!"},
    ).json()
    token = login_res["data"]["token"]["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": workspace_id,
    }


def create_sample_csv_content():
    return (
        "timestamp,instance_id,instance_type,service_name,application_name,cloud_provider,cloud_region,cpu_utilization,memory_utilization,network_in,network_out,storage_utilization,storage_read,storage_write,request_count,workload_volume,status\n"
        "2026-10-01 00:00:00,i-01,c6i.xlarge,api-gateway,web,AWS,us-east-1,45.2,60.5,12.5,25.0,40.0,10.0,5.0,1200,1200,RUNNING\n"
        "2026-10-01 01:00:00,i-01,c6i.xlarge,api-gateway,web,AWS,us-east-1,52.8,62.1,18.0,30.5,40.5,12.0,6.0,1450,1450,RUNNING\n"
        "2026-10-01 02:00:00,i-01,c6i.xlarge,api-gateway,web,AWS,us-east-1,88.4,75.0,45.0,70.0,41.0,25.0,15.0,3200,3200,RUNNING\n"
        "2026-10-01 03:00:00,i-02,t3.medium,standby,worker,AWS,us-east-1,2.5,10.0,0.5,0.8,20.0,1.0,0.5,10,10,RUNNING\n"
        "2026-10-01 04:00:00,i-02,t3.medium,standby,worker,AWS,us-east-1,3.1,10.2,0.6,0.9,20.0,1.0,0.5,12,12,RUNNING\n"
        "2026-10-01 05:00:00,i-03,r6i.xlarge,analytics,worker,AWS,us-east-1,35.0,85.5,15.0,20.0,55.0,15.0,8.0,600,600,RUNNING\n"
    ).encode("utf-8")


def test_dataset_upload_csv(client, test_user, test_workspace):
    headers = get_auth_headers(client, test_user, test_workspace.id)
    csv_bytes = create_sample_csv_content()

    files = {"file": ("cloud_telemetry.csv", io.BytesIO(csv_bytes), "text/csv")}
    data = {"name": "Test Cluster Telemetry", "description": "Benchmark telemetry"}

    res = client.post("/api/v1/datasets/upload", headers=headers, files=files, data=data)
    assert res.status_code == 201
    dataset = res.json()["data"]
    assert dataset["name"] == "Test Cluster Telemetry"
    assert dataset["file_format"] == "CSV"
    assert dataset["row_count"] == 6
    assert dataset["column_count"] == 17
    assert dataset["workspace_id"] == test_workspace.id
    assert dataset["status"] == "READY"


def test_dataset_preview_and_schema(client, test_user, test_workspace):
    headers = get_auth_headers(client, test_user, test_workspace.id)
    csv_bytes = create_sample_csv_content()
    files = {"file": ("cloud_telemetry.csv", io.BytesIO(csv_bytes), "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    dataset_id = upload_res.json()["data"]["id"]

    # Preview
    preview_res = client.get(f"/api/v1/datasets/{dataset_id}/preview", headers=headers)
    assert preview_res.status_code == 200
    preview = preview_res.json()["data"]
    assert preview["total_rows"] == 6
    assert len(preview["columns"]) == 17
    assert len(preview["rows"]) == 6
    assert preview["rows"][0]["instance_id"] == "i-01"

    # Schema
    schema_res = client.get(f"/api/v1/datasets/{dataset_id}/schema", headers=headers)
    assert schema_res.status_code == 200
    schema = schema_res.json()["data"]
    assert schema["column_count"] == 17
    col_names = [c["column_name"] for c in schema["columns"]]
    assert "cpu_utilization" in col_names
    assert "memory_utilization" in col_names


def test_column_mapping_and_validation(client, test_user, test_workspace):
    headers = get_auth_headers(client, test_user, test_workspace.id)
    csv_bytes = create_sample_csv_content()
    files = {"file": ("cloud_telemetry.csv", io.BytesIO(csv_bytes), "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    dataset_id = upload_res.json()["data"]["id"]

    # Retrieve auto-detected mapping
    map_res = client.get(f"/api/v1/datasets/{dataset_id}/column-mapping", headers=headers)
    assert map_res.status_code == 200
    mapping = map_res.json()["data"]
    assert mapping["is_valid"] is True
    assert mapping["mapping"]["cpu_utilization"] == "cpu_utilization"

    # Update mapping
    update_payload = {"mapping": mapping["mapping"]}
    update_payload["mapping"]["workload_volume"] = "request_count"
    up_res = client.post(
        f"/api/v1/datasets/{dataset_id}/column-mapping",
        headers=headers,
        json=update_payload,
    )
    assert up_res.status_code == 200
    assert up_res.json()["data"]["mapping"]["workload_volume"] == "request_count"

    # Validate
    val_res = client.post(f"/api/v1/datasets/{dataset_id}/validate", headers=headers)
    assert val_res.status_code == 200
    assert val_res.json()["data"]["is_valid"] is True


def test_data_quality_audit(client, test_user, test_workspace):
    headers = get_auth_headers(client, test_user, test_workspace.id)
    csv_bytes = create_sample_csv_content()
    files = {"file": ("cloud_telemetry.csv", io.BytesIO(csv_bytes), "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    dataset_id = upload_res.json()["data"]["id"]

    # Run audit
    audit_res = client.post(f"/api/v1/datasets/{dataset_id}/quality/audit", headers=headers)
    assert audit_res.status_code == 200
    report = audit_res.json()["data"]
    assert report["dataset_id"] == dataset_id
    assert report["quality_score"] >= 80.0
    assert report["total_records"] == 6
    assert report["valid_records"] == 6
    assert report["invalid_records"] == 0

    # Fetch latest report
    get_res = client.get(f"/api/v1/datasets/{dataset_id}/quality", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["quality_score"] == report["quality_score"]


def test_pyspark_processing_and_analytics_pipeline(client, test_user, test_workspace):
    headers = get_auth_headers(client, test_user, test_workspace.id)
    csv_bytes = create_sample_csv_content()
    files = {"file": ("cloud_telemetry.csv", io.BytesIO(csv_bytes), "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    dataset_id = upload_res.json()["data"]["id"]

    # Trigger processing pipeline synchronously
    proc_payload = {"engine": "PYSPARK", "parameters": {"generate_features": True}}
    proc_res = client.post(
        f"/api/v1/datasets/{dataset_id}/process?sync=true",
        headers=headers,
        json=proc_payload,
    )
    assert proc_res.status_code in [200, 202]
    job = proc_res.json()["data"]
    assert job["status"] == "COMPLETED"
    assert job["records_processed"] == 6
    assert job["progress"] in [1.0, 100, 100.0]

    # Verify execution logs
    logs_res = client.get(f"/api/v1/processing/jobs/{job['id']}/logs", headers=headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()["data"]
    assert len(logs) >= 3

    # Test Analytics Overview
    overview_res = client.get(f"/api/v1/analytics/overview?dataset_id={dataset_id}", headers=headers)
    assert overview_res.status_code == 200
    ov = overview_res.json()["data"]
    assert ov["total_records"] == 6
    assert ov["average_cpu"] > 0
    assert ov["disclaimer"] == "Estimated cost based on configured pricing assumptions."

    # Test CPU Analytics
    cpu_res = client.get(f"/api/v1/analytics/cpu?dataset_id={dataset_id}", headers=headers)
    assert cpu_res.status_code == 200
    cpu_data = cpu_res.json()["data"]
    assert cpu_data["average_cpu"] > 0
    assert len(cpu_data["usage_by_instance"]) > 0

    # Test Memory Analytics
    mem_res = client.get(f"/api/v1/analytics/memory?dataset_id={dataset_id}", headers=headers)
    assert mem_res.status_code == 200
    assert mem_res.json()["data"]["average_memory"] > 0

    # Test Network Analytics
    net_res = client.get(f"/api/v1/analytics/network?dataset_id={dataset_id}", headers=headers)
    assert net_res.status_code == 200
    assert net_res.json()["data"]["total_network_in_gb"] >= 0

    # Test Storage Analytics
    storage_res = client.get(f"/api/v1/analytics/storage?dataset_id={dataset_id}", headers=headers)
    assert storage_res.status_code == 200
    assert storage_res.json()["data"]["average_storage_utilization"] > 0

    # Test Workload Analytics
    workload_res = client.get(f"/api/v1/analytics/workload?dataset_id={dataset_id}", headers=headers)
    assert workload_res.status_code == 200
    assert workload_res.json()["data"]["total_requests"] > 0

    # Test Resource Efficiency (Check idle & underutilized identification)
    eff_res = client.get(f"/api/v1/analytics/resources?dataset_id={dataset_id}", headers=headers)
    assert eff_res.status_code == 200
    eff_data = eff_res.json()["data"]
    assert eff_data["idle_count"] >= 1  # i-02 is idle (cpu ~2.8%)
    assert len(eff_data["candidates"]) > 0

    # Test Cost Analytics with explicit disclaimer
    cost_res = client.get(f"/api/v1/analytics/cost?dataset_id={dataset_id}", headers=headers)
    assert cost_res.status_code == 200
    cost_data = cost_res.json()["data"]
    assert cost_data["monthly_estimated_cost"] > 0
    assert "Estimated cost based on configured pricing assumptions." in cost_data["disclaimer"]

    # Test Anomalies
    anom_res = client.get(f"/api/v1/analytics/anomalies?dataset_id={dataset_id}", headers=headers)
    assert anom_res.status_code == 200


def test_export_analytics_and_download(client, test_user, test_workspace):
    headers = get_auth_headers(client, test_user, test_workspace.id)
    csv_bytes = create_sample_csv_content()
    files = {"file": ("cloud_telemetry.csv", io.BytesIO(csv_bytes), "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", headers=headers, files=files)
    dataset_id = upload_res.json()["data"]["id"]

    # Process first
    client.post(f"/api/v1/datasets/{dataset_id}/process?sync=true", headers=headers, json={"engine": "PANDAS"})

    # Create CSV export
    exp_payload = {"dataset_id": dataset_id, "export_format": "CSV", "report_type": "PROCESSED_DATA"}
    exp_res = client.post("/api/v1/exports/analytics", headers=headers, json=exp_payload)
    assert exp_res.status_code == 201
    export_info = exp_res.json()["data"]
    export_id = export_info["export_id"]

    # Check export status
    st_res = client.get(f"/api/v1/exports/{export_id}", headers=headers)
    assert st_res.status_code == 200
    assert st_res.json()["data"]["status"] == "COMPLETED"

    # Download export
    dl_res = client.get(f"/api/v1/exports/{export_id}/download", headers=headers)
    assert dl_res.status_code == 200
    assert len(dl_res.content) > 0


def test_cross_workspace_isolation(client, test_user, test_workspace, db_session):
    headers_ws1 = get_auth_headers(client, test_user, test_workspace.id)

    # Create second workspace for user
    ws2 = Workspace(
        name="Isolated Workspace Beta",
        slug="isolated-ws-beta",
        type="ENTERPRISE",
        cloud_provider="AWS",
        owner_id=test_user.id,
    )
    db_session.add(ws2)
    db_session.flush()

    member2 = WorkspaceMember(workspace_id=ws2.id, user_id=test_user.id, role=RoleEnum.WORKSPACE_ADMIN.value)
    db_session.add(member2)
    db_session.commit()

    headers_ws2 = get_auth_headers(client, test_user, ws2.id)

    # Upload dataset in Workspace 1
    csv_bytes = create_sample_csv_content()
    files = {"file": ("ws1_data.csv", io.BytesIO(csv_bytes), "text/csv")}
    up_res = client.post("/api/v1/datasets/upload", headers=headers_ws1, files=files)
    dataset_id = up_res.json()["data"]["id"]

    # Attempt to access dataset from Workspace 2 -> MUST be 404
    get_res = client.get(f"/api/v1/datasets/{dataset_id}", headers=headers_ws2)
    assert get_res.status_code == 404

    # Attempt to preview dataset from Workspace 2 -> MUST be 404
    prev_res = client.get(f"/api/v1/datasets/{dataset_id}/preview", headers=headers_ws2)
    assert prev_res.status_code == 404

    # Attempt to delete dataset from Workspace 2 -> MUST be 404
    del_res = client.delete(f"/api/v1/datasets/{dataset_id}", headers=headers_ws2)
    assert del_res.status_code == 404
