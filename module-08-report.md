# Module 08 Completion Report

## Tracked Files
```
project_spec.md
```

## Spec Commit History
```
2d309d5 (HEAD -> master, origin/master) Add project spec for weekly status report generator
```

## project_spec.md Contents
```markdown
# Project Specification: Weekly Status Report Generator

## 1. Overview

A command-line tool that generates a weekly status report for a Staff Augmentation engagement, pulling live data from Jira. The report is intended for the client/end customer and summarizes team delivery progress for a single team of 10 people on one Jira board.

**Owner:** Delivery Manager
**Primary audience:** Client / end customer
**Team size:** 10 people, single Jira project/board

## 2. Goals

- Eliminate manual compilation of weekly status reports from Jira.
- Produce a consistent, client-ready Markdown report every week.
- Keep a historical, dated archive of all past reports.

## 3. Non-Goals

- No automated scheduling in v1 (manual trigger only).
- No Confluence publishing, email, or Slack delivery in v1 (Markdown file output only).
- No support for multi-board/multi-project aggregation in v1.

## 4. Data Sources

| Data | Source | Notes |
|---|---|---|
| Completed / in-progress / blocked issues | Jira REST API | Query by project key + status category |
| Sprint velocity / burndown | Jira REST API (sprint report / issue history) | Committed vs. completed story points |
| Individual utilization/allocation (10 people) | Jira REST API (worklogs / assignee issue load) | Derived from Jira worklogs, not a separate timesheet system |
| Risks & escalations | Manually entered by Delivery Manager | No Jira field/label for this yet; collected via a manual input step (e.g. prompt or editable input file) each run |

## 5. Report Period

- "Weekly" = fixed calendar week, **Monday through Friday** (not aligned to Jira sprint boundaries).
- Each run generates a report covering the most recently completed (or current, in-progress) calendar week.

## 6. Report Contents

The generated Markdown report includes, in order:

1. **Header** — team name, report week (date range), prepared-by, generation date.
2. **Executive summary** — short narrative, overall status (On Track / At Risk / Delayed).
3. **Completed issues** — table of issues moved to Done during the week (key, summary, assignee).
4. **In-progress issues** — table of issues currently In Progress / In Review (key, summary, assignee, status).
5. **Blocked issues** — table of issues flagged/blocked (key, summary, assignee, blocker reason).
6. **Sprint velocity / burndown** — committed vs. completed story points, trend vs. prior weeks.
7. **Individual utilization/allocation** — per-person table (10 rows) showing assigned issues/worklog hours for the week, derived from Jira.
8. **Risks & escalations** — manually supplied list, included verbatim in the report.
9. **Footer** — data source/timestamp note.

## 7. Trigger Model

- Manual only: Delivery Manager runs a CLI command when ready to generate the report.
- No background scheduler, no CI job, no webhook in v1.

## 8. Technology Stack

- **Language:** Python 3
- **Jira access:** Jira REST API (v3) via HTTPS, using an existing Jira API token (already available — no token provisioning needed).
- **Output:** Markdown (`.md`) file only.

## 9. Configuration

Connection details are supplied via a `.env` file (already gitignored in this repo), not CLI arguments:

```
JIRA_BASE_URL=
JIRA_API_TOKEN=
JIRA_EMAIL=
JIRA_PROJECT_KEY=
```

The script loads these at startup and fails fast with a clear error if any are missing.

## 10. Output & Archiving

- Each run writes a new, dated report file — previous reports are never overwritten.
- Suggested naming convention: `reports/status-report-YYYY-MM-DD.md` (date = week start, Monday).
- The `reports/` directory accumulates a full historical archive over time.

## 11. Manual Input for Risks/Escalations

Since risks & escalations aren't tracked in Jira, the tool needs a lightweight way to capture them each run. Options to decide during design:
- Interactive CLI prompt asking the Delivery Manager to type risk entries at generation time, or
- An editable local file (e.g. `risks-this-week.md` or `.txt`) that the Delivery Manager updates before running the generator, which the tool reads and embeds into the report.

(To be finalized in implementation — default assumption: editable local input file, since it's reusable and doesn't block the script mid-run.)

## 12. Open Questions / Assumptions for Implementation

- Utilization will be approximated from Jira worklogs and/or assigned issue counts per person — exact formula to be defined when building the utilization section.
- No historical trend storage beyond the archived Markdown files themselves (i.e., velocity trend is computed by re-reading past Jira data, not past reports).
- Single Jira project key covers the whole 10-person team; no per-person team/board mapping needed.

## 13. Out of Scope for v1 (Future Enhancements)

- Scheduled/automated generation.
- Email, Slack, or Confluence delivery.
- Multi-project/multi-board aggregation.
- Native risk/escalation tracking integration (e.g. a Jira label or issue type).
```
