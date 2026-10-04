# Implementation Plan: Jira Weekly Status Report Automation

**Status:** Ready for implementation  
**Specification:** `spec/specification.md`  
**Constitution:** `spec/constitution.md`

## Objective

Deliver the local web application described in the specification: a React 18 + Vite frontend, Node.js 22 LTS + Express backend, and PostgreSQL 15 database. A single Delivery Manager can generate, review, and download immutable weekly Jira status reports, then browse their saved history.

The implementation replaces the Python CLI as the supported workflow. PostgreSQL is authoritative; no import of previous filesystem reports or CLI compatibility is required.

## Architecture and Delivery Boundaries

- **Frontend:** React 18 + Vite, served with the backend from the same local origin. It handles report inputs, status/loading/error messages, preview, history, details, and Markdown download. It never receives Jira credentials or connects directly to PostgreSQL.
- **Backend:** Node.js 22 LTS + Express. It owns configuration validation, Jira API access, report business rules, Markdown generation, and persistence.
- **Database:** PostgreSQL 15 in Docker Compose with a persistent local volume, health check, and versioned schema migrations.
- **Jira integration:** Jira REST API v3 over HTTPS, using backend-only environment configuration. Use a configured project key, board ID, Jira email/API token, custom story-point field (default `customfield_10016`), configured blocker-reason field, and exactly 10 roster entries mapped by Jira account ID.
- **Persistence:** Store canonical UTF-8 Markdown and searchable report metadata/metrics. Do not persist raw Jira payloads. Enforce uniqueness for configured team + Monday week-start and make saved reports immutable.
- **Operation:** Local single-user only, loopback-bound, no application login, no wildcard CORS, and no production deployment in v1.

## Risk-Adjusted Execution Strategy

Phase headings describe capability areas; they are not a strict serial schedule. Execute the tasks in `spec/tasks.md` by dependency-aware waves:

1. Start with low-risk, high-gain foundations: workspace/test scripts (T001), configuration and secret-boundary validation (T003), and pure timezone/report-period/status rules (T013).
2. Establish the local runtime and persistence baseline (T002, T004, T005, T006).
3. Resolve the highest external uncertainty early with a bounded Jira endpoint/permission feasibility check as the first part of T007. Then implement pagination and source collectors (T008-T011) before orchestration (T012).
4. Complete report formatting, API contract, and backend workflows (T014-T019), then deliver the UI (T020-T024).
5. Run operational, quality, performance, and documentation gates (T025-T028).

Continue static checks and unit tests throughout delivery. Do not begin work whose prerequisite acceptance criteria are failing; independent tasks inside a wave may run in parallel. Final dependency edges are listed in `spec/tasks.md`.

## Phases and Milestones

### Phase 1 — Application foundation and configuration

**Work**

- Establish clear frontend, backend, and shared contract/test organization within the existing `module08-task` starter structure.
- Set Node.js 22 LTS and React 18 + Vite baselines; add only necessary scripts, dependencies, lint/static checks, and test runners.
- Create Docker Compose services for the application and PostgreSQL 15, including database health check, persistent volume, loopback-only ports, and documented startup/shutdown.
- Add versioned migration infrastructure and a database connectivity/health check.
- Define and validate backend environment configuration for Jira URL/email/token/project/board, team label, exactly 10 Jira account IDs, story-point field, and blocker-reason field. Default story-point field to `customfield_10016`; require HTTPS for Jira.
- Provide a safe `.env.example` with placeholders only; keep real credentials out of source control, frontend bundles, and logs.
- Supersede the CLI workflow in project usage documentation without importing its historical reports.

**Milestone M1 — Reproducible app shell**

- Frontend and backend start through the documented Docker Compose workflow.
- PostgreSQL 15 becomes healthy, the initial migration applies reproducibly, and health checks report service readiness.
- Missing/invalid configuration produces a clear server-side error before report generation; no secret value is returned or logged.
- Local ports bind to loopback and the frontend/API use the same origin.

### Phase 2 — Data model and immutable report storage

**Work**

- Create migrations for report metadata and saved Markdown. Include report ID, configured team label, week start/end, prepared-by, optional executive summary, generated-at timestamp, overall status, source/sprint metadata, metrics, and canonical Markdown.
- Add a database uniqueness constraint for configured team + Monday week-start. Do not add update/delete operations for saved reports.
- Define typed repository operations for create, paginated list, get by ID, and retrieve canonical Markdown.
- Ensure report creation is atomic: do not write until all required Jira data is successfully collected and formatted; handle simultaneous duplicate requests through the database constraint and return a conflict.
- Persist timestamps in UTC and format report dates/timestamps in `Asia/Kolkata`.

**Milestone M2 — Persistence contract**

- Migrations create the schema from an empty database and can be reapplied safely according to the migration tool's standard.
- Integration tests verify persistence, history ordering/pagination, immutability, and duplicate conflict behavior, including concurrent attempts.
- No raw Jira response payloads or secrets are stored.

### Phase 3 — Jira client and source-data collection

**Work**

- Implement a backend Jira client with authentication, HTTPS validation, request timeouts, safe error mapping, and bounded retries for network errors, HTTP 429, and HTTP 5xx. Honor a bounded `Retry-After` when present; cap attempts at three.
- Implement complete pagination for Jira issue searches until all reported results are fetched.
- Collect, with explicit time bounds and configuration:
  - Distinct project issues transitioned into a Done-category status during Monday 00:00 through Saturday 00:00 IST.
  - Current project issues in In Progress or In Review at collection time.
  - Currently flagged/impediment issues and configured blocker reason when populated.
  - Configured-board sprint data: active sprint with latest start date, otherwise most recently completed sprint; current and prior completed sprint report metrics.
  - Current distinct assigned non-Done project issue counts for each configured roster member.
  - Worklogs authored by each roster member within the report interval.
- Validate source completeness and metric values. Treat a successful query with no worklogs as zero hours; treat permission/API errors or malformed required data as generation failure.
- Keep Jira responses in memory only for report generation; do not persist raw payloads.

**Milestone M3 — Verified Jira data**

- Mocked client tests cover authentication setup, pagination, report-period boundaries, transitions/reopens, status snapshots, flags, sprint selection, worklog attribution, empty results, rate limiting, retry exhaustion, and permission/network errors.
- Known fixtures produce exact issue sets, roster counts, worklog hours, sprint selection, and metrics.
- Failed required sources cannot produce a saved report.

### Phase 4 — Report domain rules and Markdown generation

**Work**

- Implement pure, testable domain functions for IST week resolution/validation, issue grouping/deduplication, workload aggregation, sprint metric interpretation, status determination, and summary construction.
- Apply the specified status order: `Delayed` for blockers and ratio below 30%; otherwise `At Risk` for blockers or ratio below 50%; otherwise `On Track`. Equality at 30%/50% is not “below.”
- Use completed/committed sprint points. Apply the 1.0 ratio fallback only for zero committed points or no sprint data after a successful query; label the ratio unmeasured in report content. Do not use fallback for Jira failures.
- Generate a deterministic, ordered Markdown report with all nine required sections, clear empty/unavailable text, data-source note, and generation timestamp.
- Include the prior completed sprint comparison on the same board when comparable; otherwise state that comparison is unavailable.
- Escape user- and Jira-supplied text for literal rendering in the browser preview and Markdown download. Keep risks in input order; use `None this week.` when none are provided.
- Build the executive summary from user text when provided, otherwise from factual status and counts only.

**Milestone M4 — Correct and safe report output**

- Unit tests cover every report section, ordering, empty state, output escaping, date and status boundaries, and the zero/unavailable velocity case.
- Fixture-generated Markdown matches the required shape and preserves provided risk wording without interpreting it as HTML or Markdown.
- The HTML preview and downloaded Markdown represent the same saved report content.

### Phase 5 — Express API and end-to-end generation workflow

**Work**

- Define and document validated API contracts. Initial endpoints:
  - `POST /api/reports` — accept week start, prepared-by, optional executive summary, and risk items; use configured team.
  - `GET /api/reports` — newest-first history, 20 reports per page.
  - `GET /api/reports/:id` — saved report metadata and content for review.
  - `GET /api/reports/:id/download` — UTF-8 Markdown as `status-report-YYYY-MM-DD.md`.
  - `GET /api/health` — application/database readiness without exposing configuration secrets.
- Validate exact ISO date format, Monday-only and non-future week starts, required fields and limits, request body shape, and forbidden control characters.
- Return consistent, actionable validation, conflict, Jira-source, and internal error responses; do not return stack traces or secret values.
- Protect local browser/API boundary with same-origin serving and restrictive CORS configuration; bind service interfaces to loopback.
- Attach request correlation IDs and log generation outcomes without credentials or raw Jira content.

**Milestone M5 — Backend workflow complete**

- API integration tests cover valid generation, invalid inputs, configuration errors, source failures, retries, duplicate conflicts, database failures, history/detail/download, and saved-report retrieval without Jira calls.
- A failed generation creates no report. A duplicate request cannot modify the saved report.

### Phase 6 — Accessible React user experience

**Work**

- Build a report-generation screen with selected/default week, prepared-by, optional summary, and repeatable risk-entry controls. Display the configured team label as read-only context.
- Provide clear inline validation, submitting/progress state, success navigation, Jira/configuration/database failure messages, and duplicate-report conflict messaging.
- Build report preview/detail, newest-first paginated history, empty-history state, and Markdown download.
- Use semantic HTML, keyboard-operable controls, visible focus, accessible labels and errors, and safe literal rendering of untrusted report content.
- Verify primary workflows against WCAG 2.2 AA and current evergreen Chrome, Edge, and Firefox.

**Milestone M6 — User workflows complete**

- Component tests cover form validation, loading/success/error/empty/conflict states, history pagination, report detail, and download affordance.
- End-to-end tests verify generate → review → history → download and verify duplicate protection.
- Core UI workflows meet the accessibility target.

### Phase 7 — Release hardening and handoff

**Work**

- Run all backend unit/integration tests, frontend component tests, end-to-end tests, static analysis, and migration checks.
- Verify Docker Compose startup from a clean state, persistent data across container restarts, health checks, and safe shutdown.
- Measure report generation and history performance against SC targets: report generation within 60 seconds and history listing within 2 seconds for at least 95% of successful requests in the expected environment.
- Document configuration, roster setup, Docker operation, migrations, report generation, history/download behavior, errors, and the no-CLI/no-import scope.
- Review logs, browser bundles, and API responses to confirm no secrets or raw Jira payloads leak.

**Milestone M7 — Release candidate accepted**

- All verification gates pass and all success criteria SC-001 through SC-013 are demonstrated.
- No critical or high-severity defects remain in generation correctness, report immutability, credential handling, or source-failure behavior.
- A fresh developer can configure placeholders, run the app and PostgreSQL, apply migrations, and run the test suite using the documented steps.

## Cross-Phase Acceptance Gates

- Follow `spec/constitution.md`; resolve any conflict in the specification before implementation.
- Never save a report if a required source fails or returns invalid required data.
- Never overwrite, mutate, or delete an existing report.
- Keep all Jira credentials and database credentials backend-only.
- Verify every required report section, report-order rule, status boundary, empty state, and explicit unavailable-data case.
- Keep tests deterministic with mocked Jira responses; live Jira credentials are not required for automated validation.
- Use versioned migrations and ensure persistence constraints, not only application checks, enforce report uniqueness.

## Dependencies and Risks

| Dependency or risk | Impact | Mitigation |
|---|---|---|
| Jira account lacks issue history, worklog, sprint, or flag permissions | Required collection fails; no report can be created | Validate access early in Phase 3 and report the specific missing source without exposing credentials |
| Jira custom fields or board configuration differ from expected | Incorrect blocker, story-point, or sprint data | Require explicit config validation and test against representative mocked fixtures before live integration |
| Jira pagination, rate limits, or response volume exceeds the target | Slow or incomplete generation | Paginate completely, use bounded retry/timeouts, record safe correlation IDs, and measure performance with realistic fixtures |
| Exact 10-person roster is invalid or Jira account IDs are stale | Workload rows are missing or misattributed | Fail configuration validation before generation and provide a documented roster format |
| Docker or migration drift across environments | Setup failures or data inconsistency | Test clean database bootstrap and migration application in the release gate |
| IST reporting dates differ from Jira timestamp interpretation | Issues/worklogs can fall into the wrong week | Centralize timezone conversion and test inclusive/exclusive boundaries around midnight |

## Exclusions

- Scheduled generation, CI-triggered reports, webhooks, email, Slack, and Confluence delivery.
- Multi-project, multi-board, or multi-team aggregation.
- Remote/multi-user hosting, login, role management, and in-app roster administration.
- In-app editing, deletion, or replacement of saved reports.
- Import of legacy filesystem reports and continued Python CLI support.
- Utilization percentages, timesheet integration, raw Jira payload retention, and production backup/restore.
