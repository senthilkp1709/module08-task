# Feature Specification: Jira Weekly Status Report Automation

**Feature branch:** Not assigned  
**Created:** 2026-10-04  
**Status:** Draft  
**Input:** Existing project specification in `project_spec.md`, project constitution in `spec/constitution.md`, and module validation rules in `validation-rules.md`.

## Summary

Provide a web application for a Delivery Manager to generate, review, and retrieve client-ready weekly delivery status reports using Jira data. Each report covers one Monday-through-Friday calendar week for one team of 10 people in one Jira project. It includes delivery status, issue progress, sprint velocity, individual Jira-based workload information, and manually supplied risks and escalations.

The application replaces the existing command-line interaction with a browser workflow while retaining the existing reporting rules and dated historical reports. Generated reports must remain available as Markdown and be retained in the application for later retrieval.

## User Scenarios & Testing

### Scenario 1 - Generate a report for a reporting week (Priority: P1)

As a Delivery Manager, I want to select a reporting week and provide report details so that I can generate a consistent status report from Jira without manually compiling its contents.

**Why this priority:** Report generation is the primary value of the application.

**Independent test:** With valid Jira configuration and mocked Jira responses for a selected week, submit a report request and verify that a report is generated with the selected dates, requested metadata, and expected report sections.

**Acceptance scenarios:**

1. **Given** I am on the report-generation page, **When** I provide a team name and prepared-by name and submit a valid Monday week start, **Then** the application generates a report for that Monday through Friday.
2. **Given** I do not select a week, **When** I submit valid report details, **Then** the application defaults to the most recent Monday and ends the period on that Friday.
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

### Scenario 5 - Prevent accidental duplicate or destructive generation (Priority: P1)

As a Delivery Manager, I want the system to protect existing reports so that retrying a request cannot silently replace a report already generated for that week.

**Independent test:** Generate a report for a team and week, submit the same request again, and verify that the original remains unchanged and the user receives a conflict with an explicit replacement choice.

**Acceptance scenarios:**

1. **Given** a report already exists for the same team and reporting week, **When** I submit another generation request, **Then** the application does not overwrite the saved report and explains the conflict.
2. **Given** a report-generation request fails, **When** I retry after correcting the cause, **Then** the failed attempt has not replaced or corrupted a previously saved report.
3. **Given** I explicitly confirm replacement of an existing report, **When** the replacement succeeds, **Then** the application makes the replacement explicit and does not silently discard the prior report content.

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
- **FR-002:** The report-generation workflow MUST collect a team name and prepared-by name.
- **FR-003:** The workflow MUST accept a reporting-week start date, validate that it is an ISO date and a Monday, and default to the most recent Monday when omitted.
- **FR-004:** The report period MUST be the selected Monday through Friday inclusive and MUST NOT be inferred from Jira sprint boundaries.
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
- **FR-009:** Completed issues MUST be those moved to Done during the reporting period. In-progress issues MUST reflect their current In Progress or In Review state when report data is collected. Blocked issues MUST use the configured Jira blocked/flagged representation.
- **FR-010:** Sprint velocity MUST use an active sprint when one is available, otherwise the most recently relevant closed sprint. The report MUST distinguish unavailable velocity from a valid zero.
- **FR-011:** The application MUST calculate completion ratio as completed points divided by committed points when committed points are greater than zero. When committed points are zero or velocity is unavailable, the current project validation rule uses a ratio of 1.0; the report MUST disclose the zero/unavailable basis so the value is not mistaken for measured completion.
- **FR-012:** Overall status MUST be calculated in this order: `Delayed` when blockers exist and completion ratio is below 30%; otherwise `At Risk` when blockers exist or completion ratio is below 50%; otherwise `On Track`.
- **FR-013:** Utilization/workload output MUST show the configured team members, their assigned issue counts, and Jira worklog hours for the reporting week. The system MUST NOT invent utilization percentages or imply timesheet-based capacity when no approved calculation or capacity data exists.
- **FR-014:** The report-generation workflow MUST allow manual entry of risks and escalations. Entries MUST be preserved verbatim and in order. When no usable entries are supplied, the report MUST contain `None this week.`
- **FR-015:** Every successful report MUST be retained in PostgreSQL and available as a Markdown `.md` download.
- **FR-016:** The application MUST provide a report-history view and report detail view. Historical views MUST use saved report data and MUST NOT require a new Jira request.
- **FR-017:** A report for the same team and reporting week MUST NOT be silently overwritten. Any replacement flow MUST require explicit user confirmation and preserve the replaced report or its prior contents for traceability.
- **FR-018:** Report generation MUST provide clear loading, success, empty, validation, conflict, and failure states. A failed or partial collection MUST NOT be presented as a successful complete report.
- **FR-019:** The application MUST identify Jira and the generation timestamp in every report. It MUST make unavailable or incomplete source sections explicit.
- **FR-020:** User-supplied text and Jira content MUST be rendered safely; report text MUST NOT execute HTML or script content in the browser.
- **FR-021:** Credentials and secrets MUST never be exposed to frontend code, report output, or application logs.
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
- PostgreSQL 15 is the persistent data store and MUST run through Docker for local development.
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

## Assumptions

- The Jira project and team roster are configured by an authorized project operator; the initial release does not aggregate multiple projects or teams.
- The configured Jira account has permissions to read issue history, current issue status, sprint data, worklogs, and blocker information needed for the report.
- Jira worklogs are the source for reported hours; these hours are not represented as independently verified timesheet data.
- Prior-week velocity comparison is included only when comparable source data is available. Missing comparison data is labeled unavailable rather than fabricated.
- Markdown is the canonical downloadable report format; the browser may also render the saved report for review.

## Open Questions

- What approved formula, if any, should convert Jira worklog hours or assigned issue counts into utilization/allocation percentages? Until decided, report the underlying counts and hours only.
- How will the 10-person roster and each person's Jira identity be configured and maintained?
- What Jira field, flag, or status convention definitively identifies a blocked issue, and where should its blocker reason be read from?
- Which Jira board and sprint-selection policy should be used if the configured project has multiple boards or multiple active sprints?
- What authentication and authorization mechanism is required for Delivery Manager users, and who may view or replace reports?
- Should report replacement be supported in the initial release, or should the system make generated reports immutable and require a separate revision?
- How should report dates and generation timestamps be displayed across time zones?
