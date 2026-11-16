# NexusMind AI - API Specification (v1)

Base URL: `/api/v1`

## Authentication Endpoints

### 1. Register User
- **Route:** `POST /api/v1/auth/register`
- **Payload:**
```json
{
  "email": "user@enterprise.com",
  "password": "SecurePassword123!",
  "full_name": "Sarah Connor"
}
```
- **Response:** HTTP 201 Created with JWT access token and user profile.

### 2. Login User
- **Route:** `POST /api/v1/auth/login`
- **Payload:**
```json
{
  "email": "user@enterprise.com",
  "password": "SecurePassword123!"
}
```
- **Response:** HTTP 200 OK with JWT token.

### 3. Logout User
- **Route:** `POST /api/v1/auth/logout`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** HTTP 200 OK.

### 4. Current User Profile
- **Route:** `GET /api/v1/auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** HTTP 200 OK with profile object.

---

## Workspace Management Endpoints

### 5. List User Workspaces
- **Route:** `GET /api/v1/workspaces`
- **Headers:** `Authorization: Bearer <token>`
- **Response:** HTTP 200 OK with list of accessible workspaces and assigned roles.

### 6. Create Workspace (Onboarding Step)
- **Route:** `POST /api/v1/workspaces`
- **Headers:** `Authorization: Bearer <token>`
- **Payload:**
```json
{
  "name": "Cloud Production Ops",
  "description": "Primary infrastructure monitoring",
  "type": "ENTERPRISE",
  "cloud_provider": "AWS"
}
```
- **Response:** HTTP 201 Created. Creator receives `WORKSPACE_ADMIN` role.

---

## Dashboard & Telemetry Endpoints

### 7. Dashboard Summary
- **Route:** `GET /api/v1/dashboard/summary`
- **Headers:** `Authorization: Bearer <token>`, `X-Workspace-Id: <id>` (optional)
- **Response:** HTTP 200 OK with KPI metrics, time-series arrays, and demo disclaimer.

### 8. Dashboard Recent Activity
- **Route:** `GET /api/v1/dashboard/activity`
- **Headers:** `Authorization: Bearer <token>`, `X-Workspace-Id: <id>`
- **Response:** HTTP 200 OK with recent audit events.

---

## Dataset Management Endpoints

### 9. List Datasets
- **Route:** `GET /api/v1/datasets?search=&page=1&page_size=10`
- **Headers:** `Authorization: Bearer <token>`, `X-Workspace-Id: <id>`
- **Response:** HTTP 200 OK with paginated dataset metadata.

### 10. Register Dataset
- **Route:** `POST /api/v1/datasets`
- **Headers:** `Authorization: Bearer <token>`, `X-Workspace-Id: <id>`
- **Permissions:** `ANALYST` or `WORKSPACE_ADMIN`
- **Payload:**
```json
{
  "name": "workload_trace_nov_2026.csv",
  "description": "Cluster utilization logs",
  "file_format": "CSV",
  "file_size_bytes": 5242880,
  "row_count": 43200
}
```
- **Response:** HTTP 201 Created.

---

## Health & System Endpoints

### 11. Health Check
- **Route:** `GET /api/v1/health`
- **Response:** HTTP 200 OK with status and database connectivity flag.

### 12. Readiness Probe
- **Route:** `GET /api/v1/ready`
- **Response:** HTTP 200 OK.

