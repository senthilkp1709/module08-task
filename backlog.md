# Implementation Backlog: Weekly Status Report Generator

Derived from [project_spec.md](./project_spec.md).

## Phase 1: Setup
- [ ] Initialize Python 3 project structure (virtualenv, `requirements.txt`)
- [ ] Add `.gitignore` covering `.env`, `__pycache__/`, build artifacts, venvs
- [ ] Create `.env.example` documenting `JIRA_BASE_URL`, `JIRA_API_TOKEN`, `JIRA_EMAIL`, `JIRA_PROJECT_KEY`
- [ ] Implement config loader that reads `.env` and fails fast with a clear error if any required variable is missing
- [ ] Create `reports/` output directory for the historical archive
- [ ] Decide and scaffold the risks/escalations manual input mechanism (editable input file, per spec section 11)

## Phase 2: Core Features
- [ ] Implement Jira REST API v3 authenticated session (email + API token)
- [ ] Fetch **completed issues**: query by project key + status changed to Done during the report week; return key, summary, assignee
- [ ] Fetch **in-progress issues**: query by project key + status in (In Progress, In Review); return key, summary, assignee, status
- [ ] Fetch **blocked issues**: query flagged/blocked issues; return key, summary, assignee, blocker reason
- [ ] Fetch **sprint velocity/burndown**: committed vs. completed story points via Jira Agile API (board + sprint lookup)
- [ ] Fetch **individual utilization**: per-person assigned issue counts and worklog hours for the 10-person team
- [ ] Implement reading of manually supplied risks/escalations and embedding them verbatim
- [ ] Implement overall status determination logic (On Track / At Risk / Delayed)
- [ ] Build report header (team name, report week date range, prepared-by, generation date)
- [ ] Build executive summary section (short narrative input)
- [ ] Build footer with data source/timestamp note
- [ ] Assemble the full Markdown report in the section order defined in spec section 6

## Phase 3: Integration
- [ ] Wire a CLI command that runs config loading → Jira data fetching → formatting → file write end-to-end
- [ ] Implement Monday–Friday calendar week calculation (not aligned to sprint boundaries)
- [ ] Implement dated output file naming (`reports/status-report-YYYY-MM-DD.md`, date = week start Monday)
- [ ] Ensure each run writes a new file and never overwrites a previously archived report
- [ ] Wire the risks/escalations input file into the CLI run
- [ ] Perform an end-to-end manual run against a real Jira project and confirm the output report is complete and correctly formatted

## Phase 4: Testing
- [ ] Unit test the config loader (valid `.env` loads correctly; missing variables raise a clear error)
- [ ] Unit test completed/in-progress/blocked issue fetching using mocked Jira API responses
- [ ] Unit test sprint velocity fetching (board lookup, active vs. closed sprint fallback) using mocked responses
- [ ] Unit test individual utilization calculation (assigned counts + worklog hour aggregation) using mocked responses
- [ ] Unit test pagination handling for Jira search queries
- [ ] Unit test the risks/escalations input loader (various file formats, missing file default)
- [ ] Unit test the overall status determination logic, including edge cases (no blockers, zero committed points, etc.)
- [ ] Unit test the Markdown report assembly against the expected template structure
- [ ] Unit test CLI behavior (argument parsing, default week calculation, existing-file protection, `--force` override)

## Phase 5: Documentation
- [ ] Write README with project overview and prerequisites
- [ ] Document setup steps: installing dependencies, creating `.env` from `.env.example`, preparing the risks input file
- [ ] Document CLI usage with example commands
- [ ] Document the output location, file naming convention, and archiving behavior
