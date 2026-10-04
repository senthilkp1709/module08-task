# Specification Review: Gaps, Contradictions, and Clarifications

> **Review update:** The original draft had the gaps listed below. Decisions from the user and approved conservative defaults have since been incorporated into `spec/specification.md` under “Resolved Decisions and Operating Defaults,” including the CLI migration, local single-user operation, immutable reports, roster/configuration, time zone, Jira mappings, failure behavior, retention, validation, and quality targets. The updated specification has been re-reviewed and is ready for implementation planning; the findings below are retained as review history, not as outstanding questions.

**Reviewed:** 2026-10-04  
**Scope:** `spec/constitution.md` and `spec/specification.md`, checked against the existing `project_spec.md` and `validation-rules.md`.

## Summary

The original draft had material gaps, including the transition from the Python CLI, report identity and replacement, velocity fallback, and Jira mappings. User decisions and approved defaults have been added to the updated specification. The current specification has no blocking clarification gaps and is ready for implementation planning.

## Original Draft Findings (Resolved in the Updated Specification)

### Product scope and migration

1. **Existing CLI versus new web application — high impact.** The existing project specification defines a Python CLI that writes dated Markdown files. The new specification says it replaces that interaction with a React/Express web application and stores reports in PostgreSQL. Confirm whether the CLI is being retired, retained alongside the web app, or used as a transitional interface. Define whether existing Markdown reports must be imported into the database and remain accessible in history.
2. **Single team versus team name per request.** The specification constrains the release to one configured team of 10, but asks the user to submit a team name for each report. Clarify whether this is a fixed configured team label or free-form input, and whether it participates in report identity.
3. **Meaning of “one Jira project/board.”** A Jira project can be associated with multiple boards. Specify whether the project key alone is authoritative or a board ID is also configured, and how the report behaves if these disagree.
4. **Users and operating environment.** The intended audience is a Delivery Manager, but no user roles, user count, deployment environment, or expected concurrent usage are defined. State whether the initial release is a single-user local tool or a multi-user application, and distinguish local Docker requirements from production deployment requirements.

### Reporting period and date behavior

5. **Default week selection.** “Most recent Monday” can mean the current Monday even if the week is incomplete, while the earlier project specification allows the most recently completed or current in-progress week. Specify the exact rule for each day of the week and whether future reporting weeks are allowed.
6. **Time zone and boundaries.** A Monday-to-Friday date range does not define the Jira timestamp boundaries. Choose the reporting time zone and define whether the interval is local Monday 00:00 inclusive through Saturday 00:00 exclusive. Apply the same rule to issue history, worklogs, sprint selection, and generation timestamps.
7. **Week validation.** The specification requires both an ISO date and Monday start, but does not specify whether invalid calendar dates, whitespace, or alternate ISO representations are rejected or normalized. Define the accepted input format and validation response.

### Jira data and business rules

8. **Team roster and Jira identity mapping — high impact.** The application needs to know which 10 people belong in the workload table and how each maps to Jira accounts. Define where roster entries are configured, the stable Jira identifier to use, how inactive/unmatched members appear, and who may edit the roster.
9. **Assigned issue count definition.** “Assigned issue counts” could include all currently assigned issues or only issues active during the report week. Define statuses, date criteria, deduplication, and whether the count is a weekly snapshot or period total.
10. **Worklog attribution and completeness.** Define whether hours are attributed by worklog author or issue assignee; how deleted, edited, or restricted worklogs are handled; whether billable status matters; and whether no worklogs means zero or unavailable data.
11. **Blocked issue identification and reason — high impact.** “Flagged/blocked representation” is not a concrete Jira mapping. Identify the field, flag, status, label, or combination that defines a blocker, and the source and precedence for blocker reason. Define whether closed/done issues can still count as blockers.
12. **Completed issue history.** Define the exact Jira status category/status mapping for “Done,” how multiple transitions into and out of Done during the week are treated, and how issues moved to Done and reopened before report generation are represented.
13. **Sprint selection and data period — high impact.** The report week is independent of sprint boundaries, while velocity is selected from an active sprint or a closed sprint. Define which sprint is selected when there are multiple active/closed sprints, what “most recently relevant” means, and how this sprint-level metric should be labeled alongside the calendar-week issue data.
14. **Velocity semantics.** Define committed points, completed points, sprint start/end snapshot rules, handling of scope changes, story-point field configuration, and whether completed points can exceed committed points. Specify the prior-week comparison when the prior calendar week maps to a different sprint or no comparable sprint.
15. **Status calculation for missing/zero points — contradiction with the goal of accurate health.** The validation rule and FR-011 assign a completion ratio of 1.0 when committed points are zero or velocity is unavailable. This can produce `On Track` despite having no measured velocity, and does not distinguish missing data from 100% completion. Confirm whether to preserve this legacy fallback or introduce an explicit `Unknown`/incomplete status or other rule. Also define handling of negative or greater-than-100% ratios.
16. **Status thresholds and completion numerator.** The thresholds use a completion ratio but do not unambiguously say whether it is sprint-level completed/committed points or reporting-week completion. Specify the exact source and whether equality at 30% and 50% falls into the higher status (the wording “below” implies it does not).
17. **Executive summary.** The summary is required but no authoring method, length, template, or relationship to calculated status is defined. State whether it is manually entered, automatically generated from metrics, or both, and define any validation and status-consistency rules.
18. **Missing and partial Jira sources.** The specification says not to save a successful-looking partial report, but also requires unavailable sections to be explicit. Decide whether partial reports may be saved as visibly incomplete, whether any one source failure aborts the entire report, and which sections/data sources are mandatory. Define retry and timeout expectations.
19. **Jira API operational behavior.** Pagination is required, but rate limits, timeouts, retries/backoff, maximum result sizes, API version/endpoint details, and behavior when Jira's reported total changes during pagination are unspecified.
20. **Configuration management.** The old specification names `.env` settings, including an optional story-point field override in validation rules; the new spec mentions Jira configuration but does not define its source, validation, update mechanism, or whether the story-point override is retained. Clarify how the Jira base URL is constrained to HTTPS and how configuration errors are surfaced to an operator.

### Reports, persistence, and replacement

21. **Report identity and duplicate scope — high impact.** FR-017 says same team and week cannot be silently overwritten, but does not define uniqueness by project, team ID/name, week start, or another key. Specify the database uniqueness rule and behavior for simultaneous requests.
22. **Replacement behavior conflicts with preservation.** Scenario 5 offers explicit replacement, while FR-017 requires preserving prior contents and SC-009 says reports are never silently changed or deleted. Decide whether reports are immutable revisions, whether replacement is supported, how users select it, and how old versions are listed/downloaded. The existing CLI's `--force` behavior overwrites a report, so clarify whether that legacy behavior is intentionally changing.
23. **Persistence shape and canonical content.** Reports are described as both rendered Markdown and structured entities, but the canonical source is not defined. Decide whether PostgreSQL stores the Markdown only, normalized report data only, or both; if both, define how consistency is maintained and which is authoritative for historical viewing/downloading.
24. **Retention, deletion, and recovery.** “Historical archive” implies retention but no retention period, deletion policy, backup/restore procedure, or export/migration strategy is specified. Define whether reports and Jira-derived personal data are retained indefinitely.
25. **Report edits and approval.** The workflow promises review before sharing but does not say whether users can edit the generated executive summary, risks, or rendered report after generation, nor whether edits create a new revision or require regeneration.
26. **Markdown safety versus verbatim text.** Risks must be preserved verbatim and rendered safely, but Markdown permits links and embedded HTML. Define whether raw HTML is escaped/sanitized, whether user text is rendered as literal text or Markdown, and whether the downloadable Markdown follows the same policy.
27. **Download contract.** Define filename convention, content type/encoding, line endings if material, and whether downloads use the saved canonical bytes. Clarify whether history is paginated/sortable/filterable; “see each retained report” may not scale.

### Security and interface requirements

28. **Authentication and authorization — high impact.** The constitution requires authorization “as appropriate,” and the specification lists this as an open question. Decide whether authentication is required, the mechanism, permitted roles, and access rules for listing, viewing, generating, replacing, and downloading reports.
29. **Browser/API security.** Define CORS policy, session/token storage, CSRF protections if cookie authentication is used, rate limits for report generation, and safeguards against unauthorized access to report IDs. These depend on the unresolved deployment and authentication model.
30. **Input constraints.** Define required-field trimming, maximum lengths, allowed characters, risk-item count/size limits, and behavior for control characters or empty entries. “Actionable validation” is not yet a testable contract.
31. **Accessibility and supported browsers.** Keyboard operation and semantic markup are required, but no accessibility conformance target or supported browser/device matrix is given. Name the expected standard (for example WCAG 2.2 AA) and target browsers if required.
32. **Report preview rendering.** The spec requires rendered Markdown but does not state how tables, links, long content, or untrusted Jira/user content are sanitized, or what the UI should do if preview rendering fails.

### Quality attributes and operations

33. **Performance and scale targets.** No response-time, report-generation duration, history size, or Jira-result volume target is defined. Add measurable targets for the expected team/project scale.
34. **Docker and operational contract.** PostgreSQL 15 via Docker is specified, but application containerization, compose services, health checks, ports, persistent volumes, startup dependencies, migrations, and development-versus-production modes are not defined.
35. **Observability and audit trail.** The spec requires actionable errors and traceability but does not define logging, correlation IDs, audit events, or what generation metadata/source completeness details must be recorded. Any logs must avoid tokens and sensitive Jira content.
36. **Test and delivery gates.** The constitution requires automated tests and static checks, but the specification does not identify the required test layers, CI gates, supported Node.js version, or migration verification. Set the minimum acceptance gates for release.

## Contradictions and Alignment Notes

1. **Stack and interaction change:** `project_spec.md` specifies Python 3, Jira REST API v3, CLI invocation, and filesystem-only Markdown output. The new specification selects React 18/Vite, Node.js/Express, and PostgreSQL-backed web history. This is an intentional product change only if confirmed; update or supersede the legacy specification and define migration/compatibility expectations.
2. **Output/archive behavior:** The legacy spec writes one file per week and fails on an existing file unless `--force`; the new spec persists reports in PostgreSQL and rejects duplicates, but also describes replacement with preservation. Define the new authoritative rule and whether filesystem output remains at all.
3. **Completion ratio fallback:** The validation rules require ratio `1.0` when velocity is missing or committed points are zero, while the constitution requires missing data to be explicit and not misleading. Disclosure is added in FR-011, but status calculation may still imply measured health. Resolve the desired status behavior.
4. **Incomplete data handling:** Scenarios and FR-018 disallow presenting partial collection as successful, while FR-019 requires unavailable sections to be explicit. Clarify whether the result is an unsaved failure, a saved incomplete report, or a separate draft state.
5. **Replacement and historical integrity:** Scenario 5 allows replacement, but the report is described as a dated historical archive and FR-017 requires preserving prior contents. An in-place replacement without immutable revision history would violate that intent.
6. **“10 people” and team roster:** The fixed team-size constraint is paired with a configurable roster, but no rule says whether fewer/more than 10 roster entries are rejected or shown. Define the invariant and exception behavior.

## Resolution Assessment

The updated specification now defines the CLI transition, local single-user boundary, fixed team/roster configuration, Jira project/board and field mappings, reporting timezone and date interval, sprint selection and metric source, missing/zero-velocity behavior, all-or-nothing generation, immutable report identity, storage/retention, rendering/input limits, quality targets, and verification gates. These decisions provide sufficient scope for implementation planning. The numbered findings above are retained only to document the original review and should not be treated as unresolved requirements.
