from apps.api.app.core.security import get_password_hash
from apps.api.app.models.entities import User, WorkspaceMember
from apps.api.app.models.enums import RoleEnum


def test_rbac_dataset_creation_viewer_forbidden(client, db_session, test_workspace):
    # Create viewer user
    viewer_user = User(
        email="viewer@enterprise.io",
        hashed_password=get_password_hash("Viewer12345!"),
        full_name="Dashboard Viewer",
        is_active=True,
        is_platform_admin=False,
    )
    db_session.add(viewer_user)
    db_session.flush()

    member = WorkspaceMember(
        workspace_id=test_workspace.id,
        user_id=viewer_user.id,
        role=RoleEnum.VIEWER.value,
    )
    db_session.add(member)
    db_session.commit()

    # Login as viewer
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": viewer_user.email, "password": "Viewer12345!"},
    ).json()
    token = login_res["data"]["token"]["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": test_workspace.id,
    }

    # Viewer attempts to create dataset -> Should be 403 Forbidden
    dataset_payload = {
        "name": "unauthorized_dataset.csv",
        "description": "Viewer attempt",
        "file_format": "CSV",
    }
    response = client.post("/api/v1/datasets", json=dataset_payload, headers=headers)
    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


def test_rbac_dataset_creation_analyst_allowed(client, db_session, test_workspace):
    # Create analyst user
    analyst_user = User(
        email="analyst@enterprise.io",
        hashed_password=get_password_hash("Analyst12345!"),
        full_name="Data Analyst",
        is_active=True,
        is_platform_admin=False,
    )
    db_session.add(analyst_user)
    db_session.flush()

    member = WorkspaceMember(
        workspace_id=test_workspace.id,
        user_id=analyst_user.id,
        role=RoleEnum.ANALYST.value,
    )
    db_session.add(member)
    db_session.commit()

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": analyst_user.email, "password": "Analyst12345!"},
    ).json()
    token = login_res["data"]["token"]["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-Id": test_workspace.id,
    }

    # Analyst creates dataset -> Should be 201 Created
    dataset_payload = {
        "name": "workload_analyst_sample.csv",
        "description": "Created by analyst",
        "file_format": "CSV",
        "row_count": 5000,
    }
    response = client.post("/api/v1/datasets", json=dataset_payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["name"] == "workload_analyst_sample.csv"

