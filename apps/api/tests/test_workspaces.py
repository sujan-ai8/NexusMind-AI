def test_workspace_creation_and_listing(client, test_user):
    # Login to get token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "Password123!"},
    ).json()
    token = login_res["data"]["token"]["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # Create workspace
    create_payload = {
        "name": "Cloud Optimization Alpha",
        "description": "Initial workspace created during onboarding",
        "type": "ENTERPRISE",
        "cloud_provider": "AWS",
    }
    create_res = client.post(
        "/api/v1/workspaces",
        json=create_payload,
        headers=auth_header,
    )
    assert create_res.status_code == 201
    created_ws = create_res.json()["data"]
    assert created_ws["name"] == "Cloud Optimization Alpha"
    assert created_ws["role"] == "WORKSPACE_ADMIN"

    # List workspaces
    list_res = client.get("/api/v1/workspaces", headers=auth_header)
    assert list_res.status_code == 200
    items = list_res.json()["data"]
    assert len(items) >= 1
    assert any(ws["id"] == created_ws["id"] for ws in items)


def test_dashboard_summary_with_workspace(client, test_user, test_workspace):
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "Password123!"},
    ).json()
    token = login_res["data"]["token"]["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": test_workspace.id,
    }

    response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["workspace_id"] == test_workspace.id
    assert data["is_demo_metrics"] is True
    assert "DEMO DATA" in data["disclaimer"]
    assert len(data["kpis"]) == 5

