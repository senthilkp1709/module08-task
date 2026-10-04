# Module 08 Validation Rules

Use these checks to validate the weekly Jira status report generator. Jira API behavior can be tested with mocked responses; no live credentials are needed for those tests.

1. **CLI arguments and reporting week**
   - Running without `--team` or `--prepared-by` fails argument validation.
   - An explicit `--week-start` must parse as an ISO date (`YYYY-MM-DD`).
   - When omitted, the start date is the most recent Monday; the report period ends four days later on Friday.

2. **Configuration validation**
   - Each missing or blank required setting (`JIRA_BASE_URL`, `JIRA_API_TOKEN`, `JIRA_EMAIL`, `JIRA_PROJECT_KEY`) causes a clear error that names the missing variable.
   - A valid configuration loads all four settings, removes a trailing slash from the base URL, and uses `customfield_10016` when no story-point field override is set.

3. **Jira data fetching**
   - Requests use Jira email and API token authentication and surface unsuccessful HTTP responses as errors.
   - Search results are paginated until the reported total is reached.
   - Verify the fetched categories: issues changed to Done during the report week; issues currently In Progress or In Review; Blocked issues; sprint velocity from an active sprint or, if none exists, a closed sprint; and utilization worklogs within the report dates.

4. **Report content and status**
   - The generated Markdown includes the header, executive summary, overall status, completed/in-progress/blocked issue tables, sprint velocity, individual utilization, risks and escalations, and footer in the expected order.
   - With blockers and completion below 30%, status is `Delayed`; with blockers or completion below 50%, it is `At Risk`; otherwise it is `On Track`.
   - When velocity is absent or committed points are zero, the formatter uses a completion ratio of 1.0.

5. **Risks input behavior**
   - Bullet entries are returned without their leading bullet marker; blank lines, HTML comments, and non-bullet lines are ignored.
   - A missing file or a file with no usable entries produces `None this week.` in the report.

6. **Dated output and overwrite protection**
   - Reports are written to `<out-dir>/status-report-YYYY-MM-DD.md`, where the date is the Monday week start; the output directory is created if needed.
   - If that path already exists, generation fails without `--force`; with `--force`, the report is replaced.
