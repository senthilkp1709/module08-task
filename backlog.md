# Implementation Backlog: Weekly Status Report Generator

Derived from [project_spec.md](./project_spec.md).

## Phase 1: Setup
- [ ] Initialize Python 3 project structure (virtualenv, `requirements.txt`) — *(manual)* — [#2](https://github.com/senthilkp1709/module08-task/issues/2)
- [ ] Add `.gitignore` covering `.env`, `__pycache__/`, build artifacts, venvs — *(manual)* — [#3](https://github.com/senthilkp1709/module08-task/issues/3)
- [ ] Create `.env.example` documenting `JIRA_BASE_URL`, `JIRA_API_TOKEN`, `JIRA_EMAIL`, `JIRA_PROJECT_KEY` — *(manual)* — [#4](https://github.com/senthilkp1709/module08-task/issues/4)
- [ ] Implement config loader that reads `.env` and fails fast with a clear error if any required variable is missing — *(manual)* — [#5](https://github.com/senthilkp1709/module08-task/issues/5)
- [ ] Create `reports/` output directory for the historical archive — *(manual)* — [#6](https://github.com/senthilkp1709/module08-task/issues/6)
- [ ] Decide and scaffold the risks/escalations manual input mechanism (editable input file, per spec section 11) — *(manual)* — [#1](https://github.com/senthilkp1709/module08-task/issues/1) (duplicate: [#7](https://github.com/senthilkp1709/module08-task/issues/7))

## Phase 2: Core Features
- [ ] Implement Jira REST API v3 authenticated session (email + API token) — *(MCP: jira-python, used by all fetch tools)*
- [ ] Fetch **completed issues**: query by project key + status changed to Done during the report week; return key, summary, assignee — *(MCP: fetch_completed_issues)*
- [ ] Fetch **in-progress issues**: query by project key + status in (In Progress, In Review); return key, summary, assignee, status — *(MCP: fetch_in_progress_issues)*
- [ ] Fetch **blocked issues**: query flagged/blocked issues; return key, summary, assignee, blocker reason — *(MCP: fetch_blocked_issues)*
- [ ] Fetch **sprint velocity/burndown**: committed vs. completed story points via Jira Agile API (board + sprint lookup) — *(MCP: fetch_sprint_velocity)*
- [ ] Fetch **individual utilization**: per-person assigned issue counts and worklog hours for the 10-person team — *(MCP: fetch_individual_utilization)*
- [ ] Implement reading of manually supplied risks/escalations and embedding them verbatim — *(MCP: load_risks)*
- [ ] Implement overall status determination logic (On Track / At Risk / Delayed) — *(MCP: determine_overall_status)*
- [ ] Build report header (team name, report week date range, prepared-by, generation date) — *(MCP: build_status_report)*
- [ ] Build executive summary section (short narrative input) — *(MCP: build_status_report)*
- [ ] Build footer with data source/timestamp note — *(MCP: build_status_report)*
- [ ] Assemble the full Markdown report in the section order defined in spec section 6 — *(MCP: build_status_report)*

## Phase 3: Integration
- [ ] Wire a CLI command that runs config loading → Jira data fetching → formatting → file write end-to-end — *(manual)*
- [ ] Implement Monday–Friday calendar week calculation (not aligned to sprint boundaries) — *(MCP: build_status_report, reuses main._most_recent_monday)*
- [ ] Implement dated output file naming (`reports/status-report-YYYY-MM-DD.md`, date = week start Monday) — *(MCP: build_status_report)*
- [ ] Ensure each run writes a new file and never overwrites a previously archived report — *(MCP: build_status_report, `force` flag)*
- [ ] Wire the risks/escalations input file into the CLI run — *(MCP: build_status_report)*
- [ ] Perform an end-to-end manual run against a real Jira project and confirm the output report is complete and correctly formatted — *(manual, exercises MCP: build_status_report)*

## Phase 4: Testing
- [ ] Unit test the config loader (valid `.env` loads correctly; missing variables raise a clear error) — *(custom skill — not yet created)*
- [ ] Unit test completed/in-progress/blocked issue fetching using mocked Jira API responses — *(custom skill — not yet created)*
- [ ] Unit test sprint velocity fetching (board lookup, active vs. closed sprint fallback) using mocked responses — *(custom skill — not yet created)*
- [ ] Unit test individual utilization calculation (assigned counts + worklog hour aggregation) using mocked responses — *(custom skill — not yet created)*
- [ ] Unit test pagination handling for Jira search queries — *(custom skill — not yet created)*
- [ ] Unit test the risks/escalations input loader (various file formats, missing file default) — *(custom skill — not yet created)*
- [ ] Unit test the overall status determination logic, including edge cases (no blockers, zero committed points, etc.) — *(custom skill — not yet created)*
- [ ] Unit test the Markdown report assembly against the expected template structure — *(custom skill — not yet created)*
- [ ] Unit test CLI behavior (argument parsing, default week calculation, existing-file protection, `--force` override) — *(custom skill — not yet created)*

## Phase 5: Documentation
- [ ] Write README with project overview and prerequisites — *(custom skill: write-documentation.agent.md)*
- [ ] Document setup steps: installing dependencies, creating `.env` from `.env.example`, preparing the risks input file — *(custom skill: write-documentation.agent.md)*
- [ ] Document CLI usage with example commands — *(custom skill: write-documentation.agent.md)*
- [ ] Document the output location, file naming convention, and archiving behavior — *(custom skill: write-documentation.agent.md)*
