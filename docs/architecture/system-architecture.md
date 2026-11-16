# NexusMind AI - System Architecture (Phase 1 Baseline)

## Architecture Overview

NexusMind AI is architected as a modular, cloud-native, multi-tier enterprise SaaS platform designed to scale from single-developer local containerized environments up to multi-region AWS cloud deployments.

```mermaid
graph TD
    subgraph ClientLayer ["Client Layer (Browser)"]
        UI["React 18 SPA (Vite + TypeScript)"]
        Router["React Router v6"]
        Query["TanStack Query (Cache)"]
        UIComponents["Tailwind CSS + Lucide Icons + Recharts"]
    end

    subgraph GatewayLayer ["API & Gateway Layer"]
        ReverseProxy["Nginx Reverse Proxy / Load Balancer"]
        FastAPI["FastAPI Application Server (:8000)"]
        Middleware["RequestContext & CORS Middleware"]
        AuthGuards["JWT Auth & RBAC Dependencies"]
    end

    subgraph ServiceLayer ["Core Service & Domain Layer"]
        AuthSvc["AuthService (JWT & Bcrypt)"]
        WorkspaceSvc["WorkspaceService (Onboarding & Membership)"]
        DashboardSvc["DashboardService (Telemetry & Metrics)"]
        DatasetSvc["DatasetService (Metadata & Storage URI)"]
        SettingsSvc["SettingsService"]
    end

    subgraph DataAccessLayer ["Data Access & Repository Layer"]
        UserRepo["UserRepository"]
        WorkspaceRepo["WorkspaceRepository"]
        DatasetRepo["DatasetRepository"]
        AuditRepo["AuditRepository"]
        SQLAlchemy["SQLAlchemy 2.0 ORM"]
    end

    subgraph PersistenceLayer ["Persistence & Async Infrastructure"]
        PostgreSQL[("PostgreSQL 16 (Primary DB)")]
        Redis[("Redis 7 (Queue & Cache)")]
        Worker["Background Celery Worker (Phase 2-6)"]
        S3Storage[("Amazon S3 (Dataset & Model Store)")]
    end

    UI --> ReverseProxy
    ReverseProxy --> FastAPI
    FastAPI --> Middleware
    Middleware --> AuthGuards
    AuthGuards --> AuthSvc
    AuthGuards --> WorkspaceSvc
    AuthGuards --> DashboardSvc
    AuthGuards --> DatasetSvc
    AuthGuards --> SettingsSvc

    AuthSvc --> UserRepo
    WorkspaceSvc --> WorkspaceRepo
    DashboardSvc --> AuditRepo
    DatasetSvc --> DatasetRepo

    UserRepo --> SQLAlchemy
    WorkspaceRepo --> SQLAlchemy
    DatasetRepo --> SQLAlchemy
    AuditRepo --> SQLAlchemy

    SQLAlchemy --> PostgreSQL
    FastAPI -.-> Redis
    Worker -.-> Redis
    Worker -.-> PostgreSQL
    DatasetSvc -.-> S3Storage
```

---

## Key Architectural Principles

1. **Strict Multi-Tenancy & Workspace Isolation**: Every domain model links to a `workspace_id`. Cross-workspace queries are strictly prohibited through repository encapsulation and dependency verification.
2. **Layered Decoupling**: API routers only handle protocol concerns (HTTP request parsing, status codes, OpenAPI serialization). All business rules live in dedicated services; all persistence interactions live in repositories.
3. **Transparent Demo Separation**: Telemetry data during Phase 1 is clearly labeled with `is_demo_data: true` and UI badges, ensuring that mock previews never masquerade as live cloud infrastructure.
4. **Cloud-Ready Hybrid Storage**: Metadata resides in PostgreSQL while large telemetry binary/CSV payloads are pointed to S3 storage URIs without bloat in the relational database.

