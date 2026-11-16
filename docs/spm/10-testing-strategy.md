# Software Project Management: 10. Testing Strategy Document

## 1. Testing Pyramid Levels

```text
       /\
      /  \    End-to-End & Acceptance Tests (Onboarding flow, Login, Dashboard)
     /----\
    /      \   Integration Tests (FastAPI TestClient + In-Memory SQLite DB + Auth)
   /--------\
  /          \  Unit Tests (Password Hashing, Token Generation, Schema Validation)
 /------------\
```

---

## 2. Test Execution Matrix (Phase 1)

| Suite Name | Scope | Framework | Execution Target | Criteria |
|---|---|---|---|---|
| **Health Tests** | API health & readiness probes | Pytest, TestClient | `tests/test_health.py` | HTTP 200, DB connected = True |
| **Auth Tests** | Registration, Login, Token, Current User | Pytest, TestClient | `tests/test_auth.py` | Validates hash, issues JWT, rejects duplicates |
| **Workspace Tests** | Creation, Listing, Summary | Pytest, TestClient | `tests/test_workspaces.py` | Verifies slug generation, workspace member role |
| **RBAC Tests** | Role enforcement & permission checks | Pytest, TestClient | `tests/test_rbac.py` | Viewer rejected (403), Analyst allowed (201) |
| **Frontend Tests** | Compilation, bundling, type-checking | Vite, TypeScript | `npm run build` | 0 errors, assets bundled to `dist/` |

---

## 3. Test Data Management
- In-memory SQLite instances are spun up per test session with static connection pooling to ensure fast, isolated, non-destructive test execution.
- Password hashing rounds during unit tests use fast bcrypt parameters to maintain rapid feedback loops (< 5 seconds total test runtime).

