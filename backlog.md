# Implementation Backlog: Weekly Status Report Generator

Derived from [project_spec.md](./project_spec.md).

## Phase 1: Setup
- [ ] Initialize Python 3 project structure (virtualenv, `requirements.txt`) — *(manual; Approach 2)* — [#2](https://github.com/senthilkp1709/module08-task/issues/2)
- [ ] Add `.gitignore` covering `.env`, `__pycache__/`, build artifacts, venvs — *(manual; Approach 2)* — [#3](https://github.com/senthilkp1709/module08-task/issues/3)
- [ ] Create `.env.example` documenting `JIRA_BASE_URL`, `JIRA_API_TOKEN`, `JIRA_EMAIL`, `JIRA_PROJECT_KEY` — *(manual; Approach 2)* — [#4](https://github.com/senthilkp1709/module08-task/issues/4)
- [ ] Implement config loader that reads `.env` and fails fast with a clear error if any required variable is missing — *(manual; Approach 3)* — [#5](https://github.com/senthilkp1709/module08-task/issues/5)
- [ ] Create `reports/` output directory for the historical archive — *(manual; Approach 2)* — [#6](https://github.com/senthilkp1709/module08-task/issues/6)
- [ ] Decide and scaffold the risks/escalations manual input mechanism (editable input file, per spec section 11) — *(manual; Approach 2)* — [#1](https://github.com/senthilkp1709/module08-task/issues/1) (duplicate: [#7](https://github.com/senthilkp1709/module08-task/issues/7))

## Phase 2: Core Features
- [ ] Implement Jira REST API v3 authenticated session (email + API token) — *(MCP: jira-python, used by all fetch tools; Approach 3)*
- [ ] Fetch **completed issues**: query by project key + status changed to Done during the report week; return key, summary, assignee — *(MCP: fetch_completed_issues; Approach 3)*
- [ ] Fetch **in-progress issues**: query by project key + status in (In Progress, In Review); return key, summary, assignee, status — *(MCP: fetch_in_progress_issues; Approach 3)*
- [ ] Fetch **blocked issues**: query flagged/blocked issues; return key, summary, assignee, blocker reason — *(MCP: fetch_blocked_issues; Approach 3)*
- [ ] Fetch **sprint velocity/burndown**: committed vs. completed story points via Jira Agile API (board + sprint lookup) — *(MCP: fetch_sprint_velocity; Approach 3)*
- [ ] Fetch **individual utilization**: per-person assigned issue counts and worklog hours for the 10-person team — *(MCP: fetch_individual_utilization; Approach 3)*
- [ ] Implement reading of manually supplied risks/escalations and embedding them verbatim — *(MCP: load_risks; Approach 1)*
- [ ] Implement overall status determination logic (On Track / At Risk / Delayed) — *(MCP: determine_overall_status; Approach 3)*
- [ ] Build report header (team name, report week date range, prepared-by, generation date) — *(MCP: build_status_report; Approach 3)*
- [ ] Build executive summary section (short narrative input) — *(MCP: build_status_report; Approach 3)*
- [ ] Build footer with data source/timestamp note — *(MCP: build_status_report; Approach 3)*
- [ ] Assemble the full Markdown report in the section order defined in spec section 6 — *(MCP: build_status_report; Approach 3)*

## Phase 3: Integration
- [ ] Wire a CLI command that runs config loading → Jira data fetching → formatting → file write end-to-end — *(manual; Approach 3)*
- [ ] Implement Monday–Friday calendar week calculation (not aligned to sprint boundaries) — *(MCP: build_status_report, reuses main._most_recent_monday; Approach 3)*
- [ ] Implement dated output file naming (`reports/status-report-YYYY-MM-DD.md`, date = week start Monday) — *(MCP: build_status_report; Approach 3)*
- [ ] Ensure each run writes a new file and never overwrites a previously archived report — *(MCP: build_status_report, `force` flag; Approach 3)*
- [ ] Wire the risks/escalations input file into the CLI run — *(MCP: build_status_report; Approach 3)*
- [ ] Perform an end-to-end manual run against a real Jira project and confirm the output report is complete and correctly formatted — *(manual, exercises MCP: build_status_report)*

## Phase 4: Testing
- [ ] Unit test the config loader (valid `.env` loads correctly; missing variables raise a clear error) — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test completed/in-progress/blocked issue fetching using mocked Jira API responses — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test sprint velocity fetching (board lookup, active vs. closed sprint fallback) using mocked responses — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test individual utilization calculation (assigned counts + worklog hour aggregation) using mocked responses — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test pagination handling for Jira search queries — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test the risks/escalations input loader (various file formats, missing file default) — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test the overall status determination logic, including edge cases (no blockers, zero committed points, etc.) — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test the Markdown report assembly against the expected template structure — *(custom skill — not yet created; Approach 3)*
- [ ] Unit test CLI behavior (argument parsing, default week calculation, existing-file protection, `--force` override) — *(custom skill — not yet created; Approach 3)*

## Phase 5: Documentation
- [ ] Write README with project overview and prerequisites — *(custom skill: write-documentation.agent.md; Approach 2)*
- [ ] Document setup steps: installing dependencies, creating `.env` from `.env.example`, preparing the risks input file — *(custom skill: write-documentation.agent.md; Approach 2)*
- [ ] Document CLI usage with example commands — *(custom skill: write-documentation.agent.md; Approach 2)*
- [ ] Document the output location, file naming convention, and archiving behavior — *(custom skill: write-documentation.agent.md; Approach 2)*

## Notes: Candidates for GitHub Coding Agent Delegation (Module 19)

Tasks below are well-defined, self-contained coding/scaffolding work with no need for human judgment or live external credentials — good candidates to delegate:

- Phase 1: Initialize Python 3 project structure; Add `.gitignore`; Create `.env.example`; Implement config loader; Create `reports/` output directory
- Phase 2: All items (Jira session, fetch completed/in-progress/blocked issues, sprint velocity, individual utilization, risks loading, overall status logic, report header/executive summary/footer, full report assembly)
- Phase 3: Wire CLI command; Monday–Friday calendar week calculation; dated output file naming; new-file-never-overwrite logic; wiring risks file into CLI
- Phase 4: All unit test items (use mocked Jira responses, no live system needed)
- Phase 5: All documentation items

**Not suitable for delegation (needs human judgment or live access):**
- Phase 1: "Decide and scaffold the risks/escalations manual input mechanism" — requires a design decision between CLI prompt vs. input file (see spec section 11)
- Phase 3: "Perform an end-to-end manual run against a real Jira project..." — requires live Jira credentials and manual verification of output

