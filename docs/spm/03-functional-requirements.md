# Software Project Management: 03. Functional Requirements Document (FRD)

## 1. System Actor Definitions
- **Guest / Visitor:** Unauthenticated user accessing public marketing, feature documentation, and auth pages.
- **Platform Administrator:** Superuser overseeing global platform settings, user lifecycle, and all workspaces.
- **Workspace Administrator:** Manager of an individual workspace, managing members, settings, and datasets.
- **Analyst:** Technical user who uploads datasets, initiates analyses, configures experiments, and drafts reports.
- **Viewer:** Read-only stakeholder who inspects dashboards and exported reports.

---

## 2. Detailed Functional Requirements Matrix

### Category 1: Identity & Access Management (IAM)
- **FR-IAM-01:** System shall permit new users to register providing full name, valid email, and secure password (min 8 chars).
- **FR-IAM-02:** System shall verify uniqueness of email address during registration and reject duplicates with HTTP 409.
- **FR-IAM-03:** Passwords must be hashed using industry-standard bcrypt before persisting to PostgreSQL.
- **FR-IAM-04:** Successful login shall generate an asymmetric or HMAC-SHA256 JWT access token with a 24-hour expiration window.
- **FR-IAM-05:** Protected API routes shall reject requests with missing, invalid, or expired tokens with HTTP 401.
- **FR-IAM-06:** System shall provide `/api/v1/auth/me` returning current user profile, email, and admin status.

### Category 2: Workspace Management & Onboarding
- **FR-WS-01:** System shall guide first-time users through a 4-step onboarding wizard.
- **FR-WS-02:** System shall auto-generate a URL-friendly unique slug from the workspace name.
- **FR-WS-03:** Workspace creator shall automatically be assigned the `WORKSPACE_ADMIN` role in `workspace_members`.
- **FR-WS-04:** Users shall be able to switch between multiple assigned workspaces via a top navigation dropdown.
- **FR-WS-05:** Requests referencing an inaccessible workspace ID shall be rejected with HTTP 403.

### Category 3: Observability Dashboard & Telemetry Visualization
- **FR-DASH-01:** System shall display 5 core KPI cards: CPU Utilization, Memory Utilization, Workload Volume, Cloud Cost, and Resource Efficiency.
- **FR-DASH-02:** All telemetry metrics displayed during Phase 1 must be explicitly badged and captioned with `DEMO DATA`.
- **FR-DASH-03:** System shall render responsive interactive time-series line/area charts using Recharts with hover tooltips.
- **FR-DASH-04:** System shall display a breakdown of workload costs by cloud service category.
- **FR-DASH-05:** System shall render recent audit logs and workspace activities retrieved from PostgreSQL.

### Category 4: Module User Interfaces
- **FR-MOD-01 (Datasets):** Interface shall support searching, pagination, format filtering, and new dataset registration.
- **FR-MOD-02 (Analytics):** Interface shall provide tabs for Workload, CPU, Memory, Cloud Cost, and Anomaly analysis.
- **FR-MOD-03 (ML Models):** Interface shall present model registry table, metric comparisons, and new training modal.
- **FR-MOD-04 (Optimization):** Interface shall present RL experiment list, convergence metrics, and baseline comparisons.
- **FR-MOD-05 (AI Copilot):** Interface shall provide conversational layout with suggested quick prompts.
- **FR-MOD-06 (AWS Cloud):** Interface shall present connection setup forms without falsely claiming active cloud links.
- **FR-MOD-07 (Reports):** Interface shall show historical reports and export actions.
- **FR-MOD-08 (SPM):** Interface shall provide project overview, active sprints, Kanban tasks, and risk tracking.
- **FR-MOD-09 (Settings):** Interface shall allow updating user profile, dark/light theme, and workspace thresholds.

