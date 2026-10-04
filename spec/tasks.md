# Implementation Tasks: Jira Weekly Status Report Automation

**Source plan:** `spec/plan.md`  
**Requirements:** `spec/specification.md`  
**Constitution:** `spec/constitution.md`

Tasks are grouped by delivery phase, not strict execution order. Follow the dependency-aware, risk-adjusted execution waves below. Start with low-risk, high-gain foundation and pure business-rule validation, then address external Jira uncertainty before committing to downstream integration. Within each wave, independent tasks may proceed in parallel. Each acceptance criterion is independently verifiable. Jira behavior MUST be tested with deterministic mocked responses; automated tests MUST NOT require live credentials.

## Recommended Execution Order

### Wave 1 — Low-risk, high-gain foundations

1. **T001** — Establish the workspace and test scripts.
2. **T003** — Validate backend configuration and secret boundaries.
3. **T013** — Implement and test timezone, reporting-week, and status rules as pure functions.

These tasks are relatively bounded and unblock validation or clarify core behavior early. T013 is listed under Phase 4 for domain ownership, but should be implemented in this early wave because it does not depend on Jira, persistence, or UI work.

### Wave 2 — Local runnable baseline and persistence

4. **T002** — Docker Compose stack.
5. **T004** — Health/readiness and same-origin local setup.
6. **T005 → T006** — Migrations, then immutable repository.

T005 schema design may be drafted alongside T002, but migration execution and integration tests require PostgreSQL.

### Wave 3 — Resolve external Jira risk, then collect data

7. **T007** — Start with a bounded Jira capability/permissions check for the exact configured project, board, sprint metrics, changelog, flag, and worklog data; record any API limitations before completing the client.
8. **T008**, then **T009**, **T010**, and **T011** — Implement pagination and source-specific collectors. T009-T011 may proceed in parallel after T007/T008 where their Jira endpoints are independent.
9. **T012** — Orchestrate all required sources after the individual collectors are verified.

Do not start report endpoint integration until required Jira sources have deterministic success/failure contracts.

### Wave 4 — Normalize and persist the report workflow

10. **T014** — Summary behavior after the domain inputs are stable.
11. **T015** — Canonical Markdown after source data and domain rules are available.
12. **T016** — Finalize the API contract against the report and persistence representations.
13. **T017**, **T018**, and **T019** — Implement generation, read/download, and observability. T018 can proceed after T006/T016 independently of Jira; T019 can start after T004 and be completed with T017.

T016 contract discovery may start in Wave 1, but final schemas must agree with T005/T006 and T015.

### Wave 5 — User experience

14. **T020**, followed by **T021**, **T022**, and **T023** as their APIs become available.
15. **T024** — Accessibility and browser validation after the primary flows are integrated; run accessibility checks incrementally while building the UI.

### Wave 6 — Release readiness

16. **T025** — Operational verification in an isolated test database/Compose project.
17. **T026** — Run quality gates continuously throughout delivery and complete the full gate here.
18. **T027** — Performance measurement using a fixed, documented test profile and representative fixtures.
19. **T028** — Finalize operator documentation and release review.

If a prerequisite or acceptance criterion fails, stop downstream dependent work, resolve that blocker, then resume. Do not delay low-cost unit/static checks until the end.

## Phase 1 — Application Foundation and Configuration

### T001 — Establish frontend and backend workspace

Create or refine the project layout for the Vite frontend, Express backend, shared API contracts, and their tests. Add package scripts for development, build, lint/static checks, and test execution.

**Status:** Implemented; build, lint, and tests pass on Node.js v24.21.0. Verification on the specified Node.js 22 LTS runtime remains pending because it is not installed in the current environment.

**Acceptance criteria**

- Frontend runs with React 18 and Vite; backend runs with Node.js 22 LTS.
- Separate documented scripts start, build, lint, and test the frontend and backend.
- Shared request/response contracts have a single authoritative definition.
- No Jira or database credential is needed in the frontend build.

### T002 — Add Docker Compose application stack

Define Docker Compose services for the frontend/backend application and PostgreSQL 15, with persistent database storage and health checks.

**Acceptance criteria**

- A fresh checkout can start the app and PostgreSQL using the documented Compose command.
- PostgreSQL reports healthy before migrations or backend database operations begin.
- Application and database ports bind to loopback only in the local configuration.
- PostgreSQL data survives application/container restarts.
- Compose configuration contains no actual credentials.

### T003 — Add configuration template and runtime validation

Implement backend-only environment configuration for Jira URL, email, API token, project key, board ID, fixed team label, 10 Jira account IDs, story-point field, and blocker-reason field.

**Acceptance criteria**

- Missing or malformed required values fail before report generation and identify the setting without printing secret values.
- Jira base URL must use HTTPS.
- Exactly 10 valid roster account IDs are required; duplicates are rejected.
- Story-point field defaults to `customfield_10016` when no override is supplied.
- `.env.example` contains placeholders only, and actual `.env` files remain ignored.
- Configuration is never bundled into frontend assets or returned by health/API responses.

### T004 — Add service readiness and safe local origin

Implement application/database readiness checks and configure same-origin local serving.

**Acceptance criteria**

- `GET /api/health` reports readiness without returning credentials or internal configuration.
- Database unavailability is reflected as not-ready rather than healthy.
- Frontend and API use one local origin; wildcard CORS is not enabled.
- Backend listener binds to loopback in the local setup.

## Phase 2 — Data Model and Immutable Report Storage

### T005 — Define and migrate report schema

Create versioned PostgreSQL migrations for report metadata, canonical Markdown, status, report period, source/sprint metadata, and stored metrics needed for history.

**Acceptance criteria**

- Migrations build the schema from a clean PostgreSQL 15 database.
- Week start/end, team, prepared-by, generation timestamp, status, canonical Markdown, selected sprint metadata, and relevant metrics can be stored and queried.
- Timestamps use an unambiguous UTC representation; report display dates are formatted in Asia/Kolkata.
- Constraints enforce required values and valid status values.
- Migration status is inspectable and failures surface explicitly.

### T006 — Implement immutable report repository

Implement create, paginated list, get-by-ID, and Markdown retrieval operations. Enforce the configured team + Monday week-start unique identity in PostgreSQL.

**Acceptance criteria**

- Repository create is atomic and returns a recognizable duplicate conflict for an existing team/week.
- Concurrent creates for the same team/week result in exactly one saved report and one conflict.
- No update or delete operation is exposed for reports.
- History sorts by week start descending and uses 20 items per page.
- Repository stores no raw Jira payload or secret.

## Phase 3 — Jira Client and Source Data

### T007 — Implement Jira HTTP client

Implement Jira REST API v3 authentication and request handling, including timeout, pagination support, safe errors, and bounded retry policy.

**Acceptance criteria**

- Requests use the configured Jira email and API token; the token is not logged or exposed to the caller.
- Insecure/non-HTTPS Jira base URLs are rejected.
- Transient network errors, HTTP 429, and HTTP 5xx receive at most three total attempts with exponential backoff and bounded `Retry-After` handling.
- Non-retryable errors and retry exhaustion are surfaced as typed source failures without leaking credentials or response secrets.
- Unit tests verify success, authentication setup, errors, retries, and timeouts using mocks.

### T008 — Implement complete Jira search pagination

Implement paginated issue search that retrieves every result reported by Jira and prevents silent truncation.

**Acceptance criteria**

- Search continues until the server-reported total has been fetched.
- Zero-result searches return an empty collection successfully.
- Malformed pages, inconsistent pagination, or a failed page fail the collection rather than returning a success-shaped partial result.
- Tests cover multiple pages, empty results, page failure, and changing/inconsistent totals.

### T009 — Collect completed, in-progress, and blocked issues

Implement issue data collection and normalization for the three issue report sections.

**Acceptance criteria**

- Completed issues are distinct by Jira key and include issues with a Done-category transition in the IST Monday-inclusive/Saturday-exclusive interval, even if subsequently reopened.
- In-progress issues represent current project issues in In Progress or In Review at collection time.
- Blocked issues represent currently flagged/impediment project issues.
- Blocker reason comes from the configured field; missing reason renders as `Not provided`.
- Assignee absence is handled consistently and does not break report generation.
- Tests verify boundary timestamps, status transitions/reopens, deduplication, flags, and empty categories.

### T010 — Collect sprint metrics and comparison

Implement configured-board sprint selection and collect current and prior completed sprint report metrics.

**Acceptance criteria**

- If active sprints exist, the sprint with the latest start date is selected.
- Otherwise the most recently completed sprint available at generation time is selected.
- The immediately prior completed sprint on the same board is used for comparison when available.
- Metrics use the configured story-point field and Jira sprint report values.
- Values must be finite and non-negative; invalid metric data fails generation.
- Zero prior completed points or unavailable comparison is labeled unavailable; absolute and percentage change are shown when defined.
- Tests cover multiple active sprints, no active sprint, no completed sprint, malformed values, and comparison availability.

### T011 — Collect team assignments and worklogs

Implement roster-based assigned issue counts and worklog-hour collection for all configured members.

**Acceptance criteria**

- Results include exactly one row per configured team member, keyed by Jira account ID.
- Assigned count is the current count of distinct project issues assigned to that member and not in Done.
- Worklog hours are attributed by author and limited to the Monday 00:00 through Saturday 00:00 Asia/Kolkata interval.
- Successful empty worklog results show zero hours; permission/API failures fail the required source.
- Tests cover all ten roster rows, zero activity, duplicate issue results, author attribution, and date boundaries.

### T012 — Orchestrate complete source collection

Implement the collection orchestration required by report generation.

**Acceptance criteria**

- All required Jira sources are collected before a report is persisted.
- Any required-source error, incomplete result, or invalid required metric aborts generation.
- No partial or complete-looking report is saved on failure.
- Collection produces a normalized typed result without persisting raw Jira payloads.
- Tests verify all-source success and failure at each required source.

## Phase 4 — Domain Rules and Markdown

### T013 — Implement reporting period and status rules

Implement pure date resolution, reporting-period validation, completion ratio, and overall status functions.

**Acceptance criteria**

- Exact `YYYY-MM-DD` valid Monday dates are accepted; malformed, non-Monday, and future dates are rejected.
- Default week uses current Monday Monday-Friday, or previous Monday when the current day is Saturday/Sunday, evaluated in Asia/Kolkata.
- Period interval is Monday 00:00 inclusive through Saturday 00:00 exclusive in Asia/Kolkata.
- Completion ratio is completed/committed points when committed points are positive; zero committed or successful no-sprint data uses 1.0 and is marked unmeasured.
- Jira failures never use the fallback.
- Status follows the exact specified threshold order, including equality behavior at 30% and 50%.
- Unit tests cover weekday defaults, DST-independent IST boundaries, invalid inputs, zero points, ratios above 100%, blockers, and threshold boundaries.

### T014 — Implement factual executive summary

Implement optional user-supplied executive summary and generated summary behavior.

**Acceptance criteria**

- User summary is optional and limited to 2,000 characters.
- If omitted, the generated summary uses only calculated status and report counts.
- Generated summary invents no causes, risks, or forecasts.
- Summary text is safely escaped in preview and Markdown output.
- Tests cover missing, blank, maximum-length, and unsafe text.

### T015 — Generate canonical Markdown report

Create deterministic Markdown formatting for all specified report sections and metadata.

**Acceptance criteria**

- All nine sections appear in the required order.
- Header includes configured team label, Monday-Friday range, prepared-by name, and generation date.
- Content includes status, issue lists, sprint metrics/trend, ten-member workload table, risks, and Jira/timestamp footer.
- Empty sections remain present with explicit empty text; no risks produce `None this week.`
- Missing/unmeasured velocity and unavailable comparison are clearly labeled.
- Risk entries are ordered and preserved as text; unsafe HTML and Markdown syntax render literally in preview and download.
- Generated document uses UTF-8 and is deterministic for equivalent normalized inputs apart from generation timestamp.
- Tests verify section order, fields, escaping, and output fixture.

## Phase 5 — API and Generation Workflow

### T016 — Define and validate API contracts

Document and implement schemas for report-generation requests and history/detail/download responses.

**Acceptance criteria**

- `POST /api/reports` accepts only week start, prepared-by, optional executive summary, and risk items; team comes from backend configuration.
- Required strings are trimmed and validated; prepared-by is at most 120 characters.
- At most 20 risk items of at most 2,000 characters each are accepted; empty items are omitted.
- Invalid request fields and forbidden control characters return actionable validation errors.
- API contract documentation matches implemented request and response shapes.

### T017 — Implement report-generation endpoint

Connect input validation, source collection, domain rules, Markdown rendering, and atomic persistence.

**Acceptance criteria**

- Successful generation persists a report only after all required sources and formatting succeed.
- Duplicate team/week requests return conflict and do not alter the original report.
- Jira, configuration, and database failures return safe actionable errors without stack traces or secrets.
- Request correlation ID appears in logs and error context without recording raw Jira content.
- API integration tests verify success, invalid input, source failure, DB failure, duplicate conflict, and concurrent duplicate submissions.

### T018 — Implement report history, detail, and download endpoints

Implement persisted report read APIs without Jira access.

**Acceptance criteria**

- `GET /api/reports` returns newest-first pages of 20 records and supports page navigation.
- `GET /api/reports/:id` returns saved report metadata and content without a Jira request.
- `GET /api/reports/:id/download` returns the canonical UTF-8 Markdown with filename `status-report-YYYY-MM-DD.md`.
- Unknown or malformed IDs return an appropriate not-found/validation response without database detail leakage.
- Tests verify pagination, stable saved content, download headers, and no Jira client calls.

### T019 — Implement health and failure observability

Complete readiness, correlation, and safe operational logging.

**Acceptance criteria**

- Health distinguishes application readiness from database readiness and exposes no secrets.
- Each request has a correlation ID propagated to logs and safe error responses.
- Logs record generation outcome and failure category but exclude credentials, raw Jira payloads, and sensitive report body content.
- Tests or targeted checks confirm secret values cannot appear in API errors or logs.

## Phase 6 — React User Experience

### T020 — Build report-generation form

Implement the form for week, prepared-by, optional executive summary, and risk entries.

**Acceptance criteria**

- Configured team label is shown read-only; user cannot submit an arbitrary team.
- Week defaults follow backend rules and client-side validation gives helpful feedback without replacing server validation.
- Users can add/remove risk entries within the defined count and length limits.
- Controls have semantic labels, keyboard operation, visible focus, and associated validation messages.
- Component tests cover valid submission, invalid week, required prepared-by, risk limits, and summary limits.

### T021 — Build progress, error, and success experience

Implement submission state, source failure states, duplicate conflict, and navigation to the generated report.

**Acceptance criteria**

- Submitting state prevents accidental duplicate clicks and communicates progress.
- Validation errors, Jira/configuration/database failures, and duplicate conflicts are distinguishable and actionable.
- Successful generation navigates to the saved report detail.
- No error message exposes secrets, raw stack traces, or unsafe server content.
- Component tests cover loading, success, source failure, validation, and conflict states.

### T022 — Build report preview and detail

Implement saved report detail and safe Markdown preview.

**Acceptance criteria**

- Detail view displays saved report, metadata, status, and generation time in IST.
- Preview displays literal escaped user/Jira content and does not execute HTML or script.
- Download action retrieves the canonical Markdown from the backend.
- Unavailable/empty sections remain visibly explained.
- Tests verify report rendering, escaping, metadata, and download action.

### T023 — Build paginated report history

Implement report archive browsing, empty state, and page navigation.

**Acceptance criteria**

- History shows reporting week, team, prepared-by, generation date, and status.
- Results are newest week first, 20 per page, with usable previous/next controls.
- Empty history presents a clear message and action to generate a report.
- Selecting a report opens detail without querying Jira.
- Tests cover empty history, page navigation, ordering, and detail navigation.

### T024 — Verify accessibility and browser support

Audit and correct the generation, history, detail, and download workflows against the accessibility target.

**Acceptance criteria**

- Core flows meet WCAG 2.2 AA checks for keyboard access, semantic structure, labels, contrast, focus visibility, and error announcements.
- Workflows are manually or automatically verified in current evergreen Chrome, Edge, and Firefox.
- Any exception is documented and does not block essential task completion.

## Phase 7 — Release Hardening and Handoff

### T025 — Verify Docker bootstrap, migrations, and persistence

Run clean-environment operational checks using documented commands.

**Acceptance criteria**

- Compose starts app and PostgreSQL 15 from a clean setup and health checks pass.
- Migrations apply to an empty database and migration status is reported.
- Saved reports persist across container restarts.
- Backend reports not-ready when the database is unavailable.
- Configuration setup uses example placeholders and does not require committed secrets.

### T026 — Run complete quality gates

Execute backend unit/integration tests, frontend component tests, end-to-end tests, static analysis, and migration checks.

**Acceptance criteria**

- All defined suites and static checks pass in the supported Node.js runtime.
- No live Jira credentials are required for automated suites.
- Boundary, empty, partial, failure, duplicate, security, and report-output cases required by the constitution are covered.
- Test results and any accepted non-blocking limitations are documented.

### T027 — Validate performance targets

Measure generation and history response performance against the specification.

**Acceptance criteria**

- Under a documented representative fixture/load and normal Jira availability, at least 95% of successful report generations complete within 60 seconds.
- At least 95% of history listing requests complete within 2 seconds for the expected data volume.
- Any missed target has a measured cause and remediation or explicitly approved exception.

### T028 — Complete operator documentation and release review

Document setup, configuration, roster format, operations, migrations, report generation, history/download, and failure behavior.

**Acceptance criteria**

- A fresh developer can follow documentation to start the app, configure placeholders, apply migrations, generate a mocked/test report, and run checks.
- Documentation states the Python CLI is replaced, old reports are not imported, and report replacement/deletion are not supported.
- Review confirms no secrets in source, frontend bundle, API responses, logs, or report output.
- SC-001 through SC-013 are each demonstrated by test or documented verification.

## Dependencies

- T001 precedes all implementation tasks. T003 and T013 depend on T001 but do not require Docker or Jira.
- T002 precedes T004 and database integration in T005-T006. T004 also depends on T003 for safe configuration behavior.
- T005 precedes T006; T006 precedes T017-T018. T017 additionally depends on T012-T016.
- T003 precedes T007 and the Jira collectors. T007 precedes T008; T008 precedes T009 and T011. T010 depends on T007 and configured board/field settings. T009-T011 precede T012.
- T012, T013, and T014 precede T015. T015 and T006 inform final T016 contract schemas. T016 precedes T017-T018.
- T004, T007, and T017 inform completion of T019.
- T016 and T017 precede T020-T021. T018 precedes T022-T023. T020 precedes T021-T024; T021-T023 precede final T024 sign-off.
- T025 depends on T002, T005-T006, and T017. T026 runs continuously and has a final completion gate after implementation. T027 depends on an integrated report flow and documented test profile. T028 is last and depends on verified app operations and quality results.
