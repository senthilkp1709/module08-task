# Project Constitution: Jira Weekly Status Report Automation

## Core Principles

### 1. Report Correctness and Traceability
Reports MUST be grounded in Jira data for the requested Monday–Friday reporting period. Calculations, status classifications, and derived utilization values MUST use documented rules, handle missing or incomplete source data explicitly, and be testable. The system MUST identify data sources and generation time and MUST NOT silently present stale, partial, or unavailable data as complete.

### 2. Secure Handling of Credentials and Data
Jira credentials, database credentials, and other secrets MUST be supplied through environment-based configuration or an approved secret store; they MUST NOT be committed, exposed to the browser, or written to logs. Backend routes MUST validate and authorize access as appropriate, validate external input, and use parameterized database queries. Only the data needed to generate and retain reports should be stored.

### 3. Clear Separation of Responsibilities
The frontend MUST use React 18 with Vite and remain a presentation and interaction layer. The Node.js/Express backend MUST own Jira integration, business rules, report generation, and persistence. PostgreSQL 15 is the system of record for persisted application data. Frontend and backend MUST communicate through explicit, documented API contracts; database access MUST remain behind the backend.

### 4. Data Integrity and Safe Persistence
PostgreSQL schema changes MUST be versioned and reproducible through migrations. Constraints and transactions MUST protect report and source-data consistency. Report generation MUST be repeatable for the same inputs, and persistence MUST avoid accidental loss or replacement of historical reports.

### 5. Verification at Each Layer
Business rules and data transformations MUST have automated tests. Backend API and persistence behavior MUST be covered by integration tests, and critical user workflows MUST be verified at the UI or end-to-end level. Tests MUST cover reporting-period boundaries, empty or partial Jira responses, failures, and duplicate report-generation attempts. Changes MUST pass the relevant tests and static checks before being considered complete.

### 6. Usable and Accessible Reporting
The interface MUST communicate loading, success, empty, and error states clearly. Report content MUST preserve the required client-facing sections and be readable, consistent, and accessible, including keyboard operability and semantic markup. Errors MUST be actionable without exposing credentials or sensitive implementation details.

### 7. Reproducible Development and Operations
The application and PostgreSQL 15 MUST be runnable in Docker using documented configuration and health checks. Setup, migrations, tests, and routine operation MUST be documented and repeatable. Environment-specific values MUST be configurable without code changes.

### 8. Maintainable, Scope-Conscious Changes
Implementation MUST favor small, cohesive modules and established project patterns. Dependencies and abstractions MUST be limited to what the project needs. Work MUST remain within the approved project scope; new capabilities or material changes to report semantics require an explicit specification update.

## Governance

This constitution governs implementation decisions and MUST be used when specifying, planning, implementing, and reviewing project changes. If a feature specification or plan conflicts with a principle, the conflict MUST be documented and resolved before implementation; any approved exception must state its rationale and scope.

Amendments MUST be made explicitly in this file and reviewed alongside any affected specifications, plans, tests, and documentation. Each amendment MUST explain the reason for the change and identify any necessary migration or compatibility work. The constitution takes precedence over conflicting project artifacts until formally amended.
