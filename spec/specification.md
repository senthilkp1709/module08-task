# Feature Specification: Jira Weekly Status Report Automation

**Feature branch:** Not assigned  
**Created:** 2026-10-04  
**Status:** Ready for planning  
**Input:** Existing project specification in `project_spec.md`, project constitution in `spec/constitution.md`, and module validation rules in `validation-rules.md`.

## Summary

Provide a local web application for a Delivery Manager to generate, review, and retrieve client-ready weekly delivery status reports using Jira data. Each report covers one Monday-through-Friday calendar week for one configured team of 10 people in one Jira project and board. It includes delivery status, issue progress, sprint velocity, individual Jira-based workload information, and manually supplied risks and escalations.

The React/Express application replaces the existing Python CLI; backward compatibility with the CLI is not required. PostgreSQL is the authoritative report archive. Generated reports remain available as saved Markdown and are retrievable in the application.

## User Scenarios & Testing

### Scenario 1 - Generate a report for a reporting week (Priority: P1)

As a Delivery Manager, I want to select a reporting week and provide report details so that I can generate a consistent status report from Jira without manually compiling its contents.

**Why this priority:** Report generation is the primary value of the application.

**Independent test:** With valid Jira configuration and mocked Jira responses for a selected week, submit a report request and verify that a report is generated with the selected dates, requested metadata, and expected report sections.

**Acceptance scenarios:**

1. **Given** I am on the report-generation page, **When** I provide a prepared-by name and submit a valid Monday week start, **Then** the application uses the configured team name and generates a report for that Monday through Friday.
2. **Given** I do not select a week, **When** I submit a prepared-by name, **Then** the application defaults to the most recent Monday and ends the period on that Friday.
3. **Given** the selected date is not a Monday or is not a valid date, **When** I submit the form, **Then** the application rejects the request with a clear validation message and does not create a report.
4. **Given** Jira returns an authentication, authorization, network, or service error, **When** report generation is attempted, **Then** the user sees an actionable error and no complete-looking report is saved.
5. **Given** Jira data is incomplete or a requested source is unavailable, **When** report generation is attempted, **Then** the application identifies the missing data and does not silently represent the report as complete.

### Scenario 2 - Review and download a generated report (Priority: P1)

As a Delivery Manager, I want to review the report before sharing it so that I can check its contents and provide a client-ready Markdown document.

**Independent test:** Generate a report using fixture data, open its detail view, and verify the report sections, Markdown content, metadata, and download.

**Acceptance scenarios:**

1. **Given** report generation succeeds, **When** the result is shown, **Then** I can review the rendered report and its generation metadata.
2. **Given** I am viewing a report, **When** I request the Markdown version, **Then** the application returns a downloadable `.md` file with the same report content and date range.
3. **Given** a report section has no matching issues or risks, **When** I review the report, **Then** the section remains present and clearly indicates that there are no entries.

### Scenario 3 - Browse historical reports (Priority: P1)

As a Delivery Manager, I want to view and retrieve previous reports so that I can refer to past delivery updates without regenerating them.

**Independent test:** Create reports for multiple weeks, then verify that the history view lists each report and that a selected report can be opened and downloaded.

**Acceptance scenarios:**

1. **Given** reports have been generated, **When** I open report history, **Then** I see each retained report with its week, team, prepared-by, generation date, and overall status.
2. **Given** I select a historical report, **When** its detail view loads, **Then** I see the saved report and can download its Markdown without querying Jira again.
3. **Given** no reports have yet been generated, **When** I open report history, **Then** I see a clear empty state and an action to generate the first report.

### Scenario 4 - Supply risks and escalations (Priority: P1)

As a Delivery Manager, I want to enter risks and escalations for the reporting week so that client-specific context not available in Jira is represented accurately.

**Independent test:** Submit risks and escalations with a report request and verify that each supplied entry appears in the report in the same order and wording.

**Acceptance scenarios:**

1. **Given** I enter one or more risk or escalation items, **When** I generate a report, **Then** those entries appear verbatim and in order in the report.
2. **Given** I provide no risk or escalation items, **When** I generate a report, **Then** the section states `None this week.`
3. **Given** a submitted risk item contains ordinary punctuation or line breaks, **When** it is included in the report, **Then** its text is preserved and rendered safely without executing markup or script content.

### Scenario 5 - Prevent duplicate report generation (Priority: P1)

As a Delivery Manager, I want reports to be immutable so that retrying a request cannot replace or erase a report already generated for that week.

**Independent test:** Generate a report for a team and week, submit the same request again, and verify that the original remains unchanged and the user receives a conflict.

**Acceptance scenarios:**

1. **Given** a report already exists for the same team and reporting week, **When** I submit another generation request, **Then** the application does not overwrite the saved report and explains the conflict.
2. **Given** a report-generation request fails, **When** I retry after correcting the cause, **Then** the failed attempt has not replaced or corrupted a previously saved report.
3. **Given** a report already exists, **When** I submit another generation request for that team and week, **Then** the application does not offer an in-place replacement flow.

### Scenario 6 - Understand report health and source data (Priority: P1)

As a client-facing report preparer, I want status and source information to be consistent and traceable so that I can explain the reported health and data currency.

**Independent test:** Exercise each documented status threshold with fixture data and verify the status, calculation inputs, source note, and generation timestamp.

**Acceptance scenarios:**

1. **Given** blockers exist and the completion ratio is below 30%, **When** the overall status is calculated, **Then** it is `Delayed`.
2. **Given** the condition for `Delayed` is false and blockers exist or the completion ratio is below 50%, **When** the overall status is calculated, **Then** it is `At Risk`.
3. **Given** neither preceding condition applies, **When** the overall status is calculated, **Then** it is `On Track`.
4. **Given** committed story points are zero or velocity is unavailable, **When** the completion ratio is calculated under the current validation rule, **Then** the ratio is 1.0 and the report makes the unavailable/zero-point context clear.
5. **Given** a report is generated, **When** I read its footer, **Then** I can identify Jira as the source and see when the report was generated.

## Requirements

### Functional Requirements

- **FR-001:** The application MUST support one configured Jira project/board and one team of 10 people for the initial release.
- **FR-002:** The report-generation workflow MUST collect a prepared-by name and MUST use the single configured team name; it MUST NOT accept an arbitrary team name per report.
- **FR-003:** The workflow MUST accept a reporting-week start date in exact `YYYY-MM-DD` format, validate that it is a valid calendar date and a Monday, and default to the most recent Monday in `Asia/Kolkata` when omitted. Future reporting weeks MUST be rejected.
- **FR-004:** The report period MUST be the selected Monday through Friday inclusive in `Asia/Kolkata`, represented for timestamp queries as Monday 00:00 inclusive through the following Saturday 00:00 exclusive. It MUST NOT be inferred from Jira sprint boundaries.
- **FR-005:** The system MUST retrieve Jira data for the configured project using Jira REST API v3 over HTTPS and the configured Jira email and API token.
- **FR-006:** Jira configuration MUST include base URL, API token, email, and project key. Missing or blank required configuration MUST prevent report generation and identify the missing setting without revealing secret values.
- **FR-007:** Jira issue search MUST retrieve all matching pages until all results reported by Jira have been fetched. Unsuccessful Jira responses MUST be surfaced as errors.
- **FR-008:** The report MUST include, in this order:
  1. Header with team name, reporting-week date range, prepared-by name, and generation date.
  2. Executive summary and overall status (`On Track`, `At Risk`, or `Delayed`).
  3. Issues moved to Done during the reporting week, with key, summary, and assignee.
  4. Issues currently In Progress or In Review, with key, summary, assignee, and status.
  5. Blocked issues, with key, summary, assignee, and blocker reason when available.
  6. Sprint velocity, including committed and completed story points and a prior-week trend when the comparison data is available.
  7. Individual workload information for the 10 team members, including assigned issue counts and Jira worklog hours for the reporting week.
  8. Risks and escalations supplied for the report.
  9. Footer identifying data source and generation timestamp.
- **FR-009:** Completed issues MUST be distinct Jira issues in the configured project with at least one transition into a status in the Done category during the reporting period, even if later reopened. In-progress issues MUST be the current snapshot of project issues in In Progress or In Review at data-collection time. Blocked issues MUST be project issues currently identified by Jira's flagged/impediment flag. A configured blocker-reason field MUST be used when available; otherwise the reason MUST be shown as `Not provided`.
- **FR-010:** Sprint metrics MUST use the configured Jira board. Select the active sprint with the latest start date; if no active sprint exists, select the most recently completed sprint available as of report generation. The report MUST identify the selected sprint and distinguish unavailable velocity from a valid zero. Compare completed points to the prior completed sprint on the same board using the same story-point field; show absolute and percentage change when prior completed points are greater than zero, otherwise label the comparison unavailable.
- **FR-011:** The application MUST calculate completion ratio as completed points divided by committed points for the selected sprint when committed points are greater than zero. When committed points are zero or no sprint data exists despite a successful query, the current project validation rule uses a ratio of 1.0; the report MUST disclose the zero/unavailable basis so the value is not mistaken for measured completion. Jira errors or permission failures for this required source MUST fail generation rather than use this fallback.
- **FR-012:** Overall status MUST be calculated using the selected sprint's completion ratio in this order: `Delayed` when blockers exist and completion ratio is below 30%; otherwise `At Risk` when blockers exist or completion ratio is below 50%; otherwise `On Track`. A completion ratio exactly equal to 30% or 50% does not satisfy the corresponding “below” threshold.
- **FR-013:** The workload table MUST show exactly the configured 10 team members, their current count of distinct assigned non-Done issues, and Jira worklog hours authored by each member during the reporting week. A successful Jira query with no matching worklogs MUST produce zero hours; a failed or unauthorized query is a source failure. The system MUST NOT invent utilization percentages or imply timesheet-based capacity.
- **FR-014:** The report-generation workflow MUST allow manual entry of risks and escalations. Entries MUST be preserved verbatim and in order. When no usable entries are supplied, the report MUST contain `None this week.`
- **FR-015:** Every successful report MUST be retained in PostgreSQL and available as a Markdown `.md` download.
- **FR-016:** The application MUST provide a report-history view and report detail view. Historical views MUST use saved report data and MUST NOT require a new Jira request.
- **FR-017:** Reports MUST be immutable. A unique report identity is the configured team and Monday week-start date. A duplicate request MUST return a conflict and MUST NOT replace, delete, or mutate the existing report; no replacement flow is in scope.
- **FR-017a:** Saved reports MUST NOT be editable. Corrections require a separately approved future revision feature; users may provide the summary and risk entries before generation.
- **FR-018:** Report generation MUST provide clear loading, success, empty, validation, conflict, and failure states. Generation MUST fail without saving if any required Jira source fails or returns incomplete data.
- **FR-019:** The application MUST identify Jira and the generation timestamp in every report. It MUST make unavailable or incomplete source sections explicit.
- **FR-020:** User-supplied text and Jira content MUST be rendered safely; report text MUST NOT execute HTML or script content in the browser.
- **FR-021:** Credentials and secrets MUST never be exposed to frontend code, report output, or application logs. The initial application is single-user and local-only, binds to loopback, does not implement application login, and MUST not allow cross-origin requests from untrusted origins.
- **FR-022:** The frontend MUST provide accessible, keyboard-operable report-generation, history, detail, and download workflows.

### Key Entities

- **Team:** The reporting team/engagement name and its configured roster of 10 people.
- **Report:** A persisted report associated with a team and Monday-Friday reporting period; includes preparation metadata, generation timestamp, overall status, rendered report content, and source completeness information.
- **Report issue entry:** A Jira issue included in a report section with the relevant issue key, summary, assignee, status, and blocker reason where applicable.
- **Sprint metrics:** Committed and completed story points, selected sprint context, completion ratio, and optional prior-week comparison.
- **Member workload:** A team member's assigned issue count and Jira worklog hours for the reporting period.
- **Risk or escalation:** A manually entered text item associated with a report, preserved verbatim and in input order.

### Project Constraints

- The frontend technology baseline is React 18 with Vite.
- The backend technology baseline is Node.js with Express.
- PostgreSQL 15 is the persistent data store and MUST run through Docker for local development. The application services MUST also be runnable through the documented Docker Compose setup.
- The application MUST follow `spec/constitution.md` for security, testing, data integrity, maintainability, and governance.
- The application is manually operated in the initial release. Scheduled generation, email, Slack, and Confluence publishing are excluded.
- The initial release supports one Jira project/board and one 10-person team; aggregation across projects or teams is excluded.

## Success Criteria

- **SC-001:** A Delivery Manager can generate a report for a valid week with the required team and author details without manually assembling Jira sections.
- **SC-002:** 100% of generated reports contain all nine required sections in the specified order, including explicit empty-state text when a section has no entries.
- **SC-003:** For a fixture set with known Jira results, the report includes all matching completed, current in-progress/review, and blocked issues, with no issue omitted due to Jira pagination.
- **SC-004:** The selected period is always exactly Monday through Friday; invalid dates and non-Monday start dates are rejected before report creation.
- **SC-005:** The documented status thresholds produce the correct status for all boundary cases: 30%, 50%, blocker presence, and combinations thereof.
- **SC-006:** The workload section contains one row per configured team member and reports the correct Jira-derived assigned issue counts and worklog hours for the reporting week.
- **SC-007:** All manually supplied risk and escalation entries are present in saved and downloaded report content, in their original order and wording; an empty set yields `None this week.`
- **SC-008:** Successful reports are retained and can be opened and downloaded from history without querying Jira again.
- **SC-009:** Repeated generation for an existing team/week never silently changes or deletes the existing report.
- **SC-010:** Jira and configuration failures are visible to the user, do not expose secrets, and do not create a report that appears complete.
- **SC-011:** Generated report content identifies Jira as a data source and includes the actual generation timestamp.
- **SC-012:** The application can be started with PostgreSQL 15 through the documented Docker setup, and schema changes can be applied reproducibly.
- **SC-013:** Required Jira configuration, including a valid HTTPS base URL, project key, board ID, story-point field ID, and exactly 10 roster account IDs, is validated before generation; configuration errors name the missing or invalid setting without disclosing secret values.

## Resolved Decisions and Operating Defaults

- **Migration:** The web application replaces the Python CLI. CLI compatibility and automatic import of existing filesystem reports are not required. PostgreSQL is the source of truth; filesystem Markdown output is not required.
- **Users and hosting:** The initial release is a single-user local application with no login. The web server binds to loopback only; remote/multi-user deployment is out of scope.
- **Team and Jira configuration:** One fixed team label, one Jira project key, one board ID, story-point field ID, and exactly 10 roster entries are supplied through backend environment/configuration. Roster identities use Jira account IDs. The roster is not edited in the browser. Use `customfield_10016` as the story-point field when no override is configured.
- **Reporting dates:** Use `Asia/Kolkata` for report date boundaries and displayed generation time. When omitted, use the current week's Monday if today is Monday through Friday; on Saturday or Sunday use the immediately preceding Monday. Reject future week starts.
- **Issue semantics:** Completed issues are deduplicated by issue key and included if transitioned into Done at least once during the period. In-progress/review status and assigned non-Done issue count are snapshots at collection time. Worklog hours are attributed to the Jira worklog author.
- **Sprint and blocker semantics:** Use the configured board; among active sprints select the one with the latest start date, otherwise the most recently completed sprint. Compare completed points against the prior completed sprint on that board. Use Jira's flagged/impediment flag for blocked status and a configured field for the reason; display `Not provided` if no reason is populated.
- **Velocity and status:** Use the configured story-point field. Compare prior-week velocity only when comparable data exists. Preserve the existing 1.0 completion-ratio fallback when committed points are zero or velocity is unavailable, and explicitly label the basis as unmeasured in the report. The allowed status values remain `On Track`, `At Risk`, and `Delayed`.
- **Executive summary:** The preparer may enter an optional summary up to 2,000 characters. If omitted, generate a factual summary from report status and counts only. Do not infer causes or make unsupported forecasts.
- **Configuration validation:** The Jira base URL MUST use HTTPS. Required non-secret settings are validated as non-empty and correctly formatted before Jira calls. Node.js 22 LTS is the backend runtime baseline.
- **Data validation:** Story-point values MUST be finite and non-negative. Completed points MAY exceed committed points; the completion ratio is not capped. Any malformed required metric data fails generation with a source-data error.
- **Jira metric source:** Use Jira's sprint report values for committed and completed points; do not recompute scope-change adjustments independently. Store the selected sprint identifier and returned metric values with report metadata.
- **Failure policy:** All required Jira sources must succeed. Retry network errors, HTTP 429, and HTTP 5xx responses at most three attempts with exponential backoff, honoring a bounded `Retry-After` when supplied. If a required source remains unavailable or returns invalid required data, fail the run without saving a report; do not save partial reports.
- **Persistence and retention:** Store rendered Markdown as canonical report content with searchable report metadata in PostgreSQL. Do not retain raw Jira payloads. Reports are immutable, cannot be edited or deleted in-app, and are retained indefinitely in v1; duplicate team/week requests return a conflict. No filesystem Markdown archive is required.
- **Text validation and rendering:** Use the configured team label; trim and require the prepared-by field (maximum 120 characters). Accept risk entries as separate plain-text items, omit empty entries, preserve submitted text and order, and escape HTML and Markdown syntax so entries render literally in the browser preview and downloaded Markdown. Limit a request to 20 risk items of at most 2,000 characters each.
- **API/browser security:** Serve the frontend and API from the same local origin in the default setup; do not enable wildcard CORS. Reject invalid request bodies and forbidden control characters while allowing ordinary text and line breaks.
- **History and operations:** History is sorted newest week first and paginated at 20 records per page. Downloads use UTF-8 Markdown with filename `status-report-YYYY-MM-DD.md`, where the date is the Monday week start. PostgreSQL 15 runs in Docker with a persistent volume and health check; schema changes use versioned migrations. Backend logs use request correlation IDs and record generation outcome without secrets or raw Jira content. Backup/restore and production hosting are outside v1.
- **Quality defaults:** Target WCAG 2.2 AA for core flows and current evergreen Chrome, Edge, and Firefox. For the expected single-project/team size, report generation should complete within 60 seconds for at least 95% of successful runs under normal Jira availability; history listing should load within 2 seconds for at least 95% of requests.
- **Verification gates:** Provide backend unit and integration tests, frontend component tests, and end-to-end coverage for generation, report history, and Markdown download. These checks and static analysis MUST pass before a release.
