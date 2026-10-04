# Requirement checklist against the current implementation

## Overall assessment

The implementation is still a scaffold, not a working Jira weekly status report application.

Evidence:
- The project README explicitly states: “This workspace is the initial application scaffold; report generation and Docker orchestration are added by later implementation tasks.” ([../README.md](../README.md))
- The backend only exposes a root endpoint returning `{ service: "jira-weekly-status-report-api" }` and does not implement report generation, Jira calls, persistence, or validation. ([../backend/src/app.js](../backend/src/app.js))
- The frontend only renders a heading and static placeholder text, with no report-generation form, history view, or download flow. ([../frontend/src/App.jsx](../frontend/src/App.jsx))
- The existing tests cover only the scaffold and contract metadata, not the business logic required by the specification. ([../backend/src/app.test.js](../backend/src/app.test.js), [../frontend/src/main.test.jsx](../frontend/src/main.test.jsx))

Status legend:
- Yes = implemented and working in the current codebase
- No = not implemented
- Partial = some supporting pieces exist, but the requirement is not fully implemented or not working end-to-end

## Functional requirements

| ID | Requirement | Implemented? | Works? | Notes |
| --- | --- | --- | --- | --- |
| FR-001 | One configured Jira project/board and one team of 10 people | No | No | No Jira config, roster, or team configuration exists in the backend or frontend. |
| FR-002 | Report-generation workflow collects prepared-by and uses a configured team name only | No | No | No report form or team-bound workflow exists. |
| FR-003 | Reporting week input validation, Monday-only date, default to recent Monday, reject future weeks | Partial | No | The shared schema allows a `weekStart` string but there is no runtime validation, defaulting logic, or Monday/future-week enforcement. |
| FR-004 | Report period uses Monday through Friday in Asia/Kolkata with exact boundary semantics | No | No | No date logic, Jira period calculation, or report data assembly exists. |
| FR-005 | Jira REST API v3 over HTTPS with configured email/token | No | No | No Jira client, auth config, or HTTP integration exists. |
| FR-006 | Required Jira configuration validation and secret handling | No | No | No config file, env validation, or secret redaction logic exists. |
| FR-007 | Paginated Jira issue search retrieval until all results are fetched | No | No | No Jira search implementation or pagination loop exists. |
| FR-008 | Required nine-section report structure in the correct order | No | No | No report generation, markdown renderer, or report page exists. |
| FR-009 | Correct issue semantics for done, in-progress/review, blocked issues | No | No | No Jira issue filtering and no blocked-status logic exist. |
| FR-010 | Sprint selection, board handling, prior completed sprint comparison | No | No | No sprint metric logic or board-derived selections are present. |
| FR-011 | Completion ratio calculation and zero/unavailable fallback behavior | No | No | No sprint metrics or completion-ratio logic exists. |
| FR-012 | Overall status thresholds (`Delayed`, `At Risk`, `On Track`) | No | No | No status calculation exists. |
| FR-013 | Member workload table with exact 10 team members, assigned counts, and worklog hours | No | No | No workload aggregation or roster model exists. |
| FR-014 | Manual risks/escalations entry, ordering, and `None this week.` fallback | Partial | No | The shared API contract allows `riskItems` up to 20, but there is no input handling or rendering logic. |
| FR-015 | Persist successful reports in PostgreSQL and allow Markdown download | No | No | No database layer, migration strategy, or persistence code exists. |
| FR-016 | Report-history and report-detail views using saved data only | No | No | No view, route, or persistence-backed history exists. |
| FR-017 | Immutable report identity and duplicate conflict handling | No | No | No unique report identity, conflict detection, or storage logic exists. |
| FR-017a | Reports are not editable; corrections require a future revision flow | No | No | No editing or immutable storage mechanism exists. |
| FR-018 | Loading, success, empty, validation, conflict, and failure states | No | No | No client form states or error handling exist. |
| FR-019 | Jira source identification, generation timestamps, and explicit missing-source states | No | No | No report metadata or source notes exist. |
| FR-020 | Safe rendering of user and Jira content without HTML/script execution | No | No | No sanitization or markdown rendering is implemented. |
| FR-021 | Secret handling, loopback binding, local-only single-user security posture | Partial | No | The code does not expose credentials in frontend code, but there is no actual backend security envelope, config validation, or loopback enforcement yet. |
| FR-022 | Accessible, keyboard-operable report generation/history/detail/download workflows | No | No | No form or navigation flows are present. |

## Decision review of unchecked items

This checklist is not just describing a gap; it is identifying what still needs to happen for the project to meet the v1 specification.

### Implement now (real gaps)

These are required for the feature to work and are not optional.

| Requirement | Decision | Reason |
| --- | --- | --- |
| FR-001 | Implement now | Core product requirement for a single configured project/board and roster. |
| FR-002 | Implement now | Report generation must be team-bound and cannot accept arbitrary team names. |
| FR-003 | Implement now | Date validation and defaulting are required before any report is created. |
| FR-004 | Implement now | Exact reporting-window logic is essential for correct Jira data collection. |
| FR-005 | Implement now | Jira API integration is a core backend requirement. |
| FR-006 | Implement now | Missing config must fail safely and without exposing secrets. |
| FR-007 | Implement now | Jira pagination and error handling are required for complete results. |
| FR-008 | Implement now | The report format and section order are specified by the requirements. |
| FR-009 | Implement now | Issue semantics drive correctness of generated reports. |
| FR-010 | Implement now | Sprint selection and prior-velocity comparison are core reporting logic. |
| FR-011 | Implement now | Completion ratio and fallback behavior are required for status calculation. |
| FR-012 | Implement now | Status thresholds drive executive summary and report health. |
| FR-013 | Implement now | Team workload is part of the required report output. |
| FR-014 | Implement now | Risk entries are required inputs and must be preserved in order. |
| FR-015 | Implement now | Persistence and Markdown export are required for report retention. |
| FR-016 | Implement now | Historical views are mandatory and must use saved reports. |
| FR-017 | Implement now | Duplicate-conflict protection is part of immutable report behavior. |
| FR-017a | Implement now | Report immutability and editing restrictions are required in v1. |
| FR-018 | Implement now | State handling is required for generating and failing safely. |
| FR-019 | Implement now | Source tracing and timestamps are required in the report. |
| FR-020 | Implement now | Safe rendering is required to prevent script execution. |
| FR-021 | Implement now | Secret handling, loopback binding, and local-only security are required. |
| FR-022 | Implement now | Accessibility and keyboard workflows are required by the spec. |

### Out of scope (explicitly deferred)

None of the currently unchecked requirements are out of scope for the initial release. The specification explicitly marks the current release as a single-user, local-only app with one project/board and one team, and the unchecked items are all part of that v1 scope.

The spec does call out a few non-goals, including:
- scheduled generation,
- email/Slack/Confluence publishing,
- production hosting and backup/restore,
- cross-project or cross-team aggregation,
- CLI compatibility/import of filesystem reports.

These are intentionally excluded and should remain documented as non-goals, not as checklist items to reclassify.

### Nice-to-have / polish (non-blocking)

No current unchecked checklist items are true nice-to-have items; all remain required by the v1 specification.

The only optional items worth tracking later are:
- extra visual polish beyond the required accessibility baseline,
- additional non-essential UX refinements,
- minor front-end improvements that do not affect correctness.

These should remain separate from the must-have backlog until the required feature set is working.

## Summary

The current repository does not meet the specification. It implements only the initial scaffold and shared contract metadata, and the requirement set in the specification remains largely unimplemented.
