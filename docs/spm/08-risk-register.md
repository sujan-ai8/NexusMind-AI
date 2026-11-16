# Software Project Management: 08. Risk Register & Mitigation Strategy

## Risk Analysis Matrix

| Risk ID | Category | Description | Likelihood (1-5) | Impact (1-5) | Severity Score | Mitigation Strategy | Owner |
|---|---|---|---|---|---|---|---|
| **RSK-01** | Technical | High latency or out-of-memory errors when processing massive telemetry datasets. | 3 | 4 | 12 (Medium) | Implement pagination, chunked streaming, and delegate heavy computation to Celery background workers. | Backend Lead |
| **RSK-02** | Security | Cross-tenant data leakage or unauthorized access across workspaces. | 2 | 5 | 10 (High) | Strict RBAC enforcement via dependency injection in FastAPI; all database queries filtered by `workspace_id`. | Security Eng |
| **RSK-03** | Architectural | Overly complex UI state leading to rendering bottlenecks or broken routes. | 2 | 3 | 6 (Low) | Decouple global state (Auth/Workspace) using clean React contexts; use React Query for caching server state. | Frontend Lead |
| **RSK-04** | Cloud Cost | Excessive AWS cloud spend during future phase deployment and testing. | 3 | 4 | 12 (Medium) | Use Docker Compose for local development; deploy to AWS Free Tier/Serverless with automated spend limits. | DevOps Eng |
| **RSK-05** | ML / AI | RL agent instability or failure to converge in autoscaling policy training. | 3 | 4 | 12 (Medium) | Utilize proven stable baseline algorithms (PPO) with bounded action spaces and reward normalization. | ML Lead |
| **RSK-06** | Timeline | Scope creep across 6 complex academic project phases. | 3 | 4 | 12 (Medium) | Strict adherence to phased delivery; complete Phase 1 foundation fully before starting subsequent phases. | Project Lead |

