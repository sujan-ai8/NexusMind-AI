# Software Project Management: 04. Non-Functional Requirements (NFR)

## 1. Performance & Scalability
- **NFR-PERF-01 (API Response Latency):** 95th percentile (p95) API response time for telemetry summary endpoints must not exceed 250 milliseconds under local test loads.
- **NFR-PERF-02 (Frontend Bundle Size):** Production Vite bundle must be optimized through code-splitting and tree-shaking, maintaining initial index load under 500 KB gzip.
- **NFR-PERF-03 (Database Indexing):** All foreign keys (`workspace_id`, `user_id`, `project_id`) and unique identifiers (`email`, `slug`) must maintain B-Tree indexes.
- **NFR-PERF-04 (Connection Pooling):** Backend database engine must employ connection pre-pinging and connection pooling to avoid resource exhaustion.

---

## 2. Security & Compliance
- **NFR-SEC-01 (Zero Secret Leakage):** No API keys, database passwords, or JWT secrets may be embedded directly in frontend code or committed to git.
- **NFR-SEC-02 (Password Storage):** Plaintext passwords must never be logged or stored. Bcrypt with standard cost factor (12 rounds) is required.
- **NFR-SEC-03 (Cross-Origin Resource Sharing):** CORS policies must strictly restrict API access to approved domains. Wildcard origin with credentials enabled is prohibited.
- **NFR-SEC-04 (SQL Injection Prevention):** All queries must execute via parameterized ORM statements in SQLAlchemy 2.0. Raw un-sanitized string concatenation is banned.
- **NFR-SEC-05 (Tenant Data Isolation):** Every read/write query for dataset, model, and project assets must enforce a `workspace_id` predicate verified against user membership.

---

## 3. Reliability, Availability & Maintainability
- **NFR-REL-01 (Graceful Degradation):** In the event of temporary database disconnects, healthcheck probes shall report degraded status rather than throwing unhandled exceptions.
- **NFR-REL-02 (Containerization):** Application components must package into standardized Docker containers with verified healthchecks.
- **NFR-REL-03 (Modular Architecture):** Codebase must maintain clean decoupling across UI components, API routers, business services, and database repositories.

---

## 4. Usability & Accessibility
- **NFR-USE-01 (Responsive Design):** The user interface must adapt responsively across desktop (1920x1080), laptop (1366x768), tablet (768x1024), and mobile viewport widths (375px+).
- **NFR-USE-02 (Theme Consistency):** Light and Dark modes must conform to WCAG 2.1 AA color contrast standards for all primary text and chart visualizations.
- **NFR-USE-03 (Feedback & States):** All asynchronous user actions (loading, submitting, error) must display appropriate visual indicators (spinners, skeletons, toast alerts).

