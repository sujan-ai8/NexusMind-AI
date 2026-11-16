# Software Project Management: 02. Project Scope Specification

## 1. Product In-Scope Items (Phase 1 Baseline)

### 1.1 Enterprise User Experience & Design
- **Public Landing Page:** Responsive hero presentation, feature cards, 6-pillar capability breakdown, and CTA routing.
- **Unified Design System:** Deep navy and slate background palette, crisp light/dark mode support, responsive layouts, subtle borders, accessible typography.
- **Authenticated Application Shell:** Collapsible sidebar, top workspace selector, global search trigger, notifications trigger, user profile dropdown, and theme toggle.

### 1.2 Multi-Tenant Authentication & Onboarding
- User registration with email/password format validation and bcrypt hashing.
- User login issuing JSON Web Tokens (JWT) with configurable TTL.
- Stateless logout session clearing.
- 4-Step Workspace Onboarding workflow:
  - Step 1: Workspace Name & Slug allocation.
  - Step 2: Workspace Type (Enterprise, Research, Startup, Individual).
  - Step 3: Cloud Provider configuration (AWS, GCP, Azure, Hybrid).
  - Step 4: Summary confirmation & dashboard redirection.

### 1.3 Role-Based Access Control (RBAC)
- 4-Tier Role Hierarchy: `PLATFORM_ADMIN`, `WORKSPACE_ADMIN`, `ANALYST`, `VIEWER`.
- Backend dependency authorization checking workspace memberships and permissions.
- UI conditional rendering based on user role assignments.

### 1.4 Module Structure Foundations
- **Dashboard Overview:** KPI cards, Recharts time-series trends, workload distributions, cost trends, and resource comparison (clearly labeled DEMO DATA for Phase 1 preview).
- **Dataset Management:** Search, pagination, upload modal, status indicators, metadata inspect.
- **Analytics Interface:** Workload, CPU, Memory, Cloud Cost, and Anomaly analysis layouts.
- **ML Models Interface:** Model registry, training modal, metrics cards, prediction history.
- **Optimization Interface:** RL experiment overview, baseline comparison, algorithm parameters.
- **AI Copilot Interface:** Chat session layout, prompt suggestions, message feed, report prompt.
- **AWS Cloud Interface:** Cloud configuration status, integration guide, region selector.
- **Reports Interface:** Report lists, detail view, export placeholders.
- **Project Management Interface:** Sprints, tasks, milestones, and risk register boards.
- **Settings Interface:** Profile, workspace settings, security, notifications, theme preferences.

---

## 2. Product Out-of-Scope Items (Strictly Deferred to Later Phases)
The following capabilities are deliberately **not** part of Phase 1 to ensure integrity and prevent simulated illusions:
- Live streaming ingestion of real-time AWS CloudWatch telemetry (Phase 2).
- Apache Spark distributed big data transformations (Phase 3).
- Model training execution for ARIMA, Prophet, or LSTM (Phase 4).
- Proximal Policy Optimization (PPO) reinforcement learning agent loops (Phase 5).
- Live LLM streaming API calls via Anthropic / OpenAI / Bedrock (Phase 6).
- Automated cloud resource provisioning via live AWS SDK / IAM credentials (Phase 6).

---

## 3. Work Scope Boundaries & Acceptance Boundaries
- Phase 1 scope is complete when the full-stack architecture is executable, tests pass, database migrations run, authentication functions end-to-end, and all module pages render professional responsive foundations.

