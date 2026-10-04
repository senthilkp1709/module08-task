# Module 08 Walkthrough: Weekly Jira Status Report Generator

## Walkthrough

This module implements a command-line workflow that gathers Jira data and writes a dated Markdown status report. `main.py` parses the team, author, report week, executive summary, risks-file, environment-file, output-directory, and overwrite options. It selects the most recent Monday when no week is supplied, sets Friday as the week end, then calls the configuration loader, Jira client, risks loader, and report formatter in sequence.

`config.py` loads Jira credentials from the selected `.env` file and fails with a clear message if a required setting is absent. `jira_client.py` authenticates with the Jira email and API token and gathers completed, in-progress, and blocked issues, sprint velocity, and per-person assigned-issue/worklog totals. `risks_input.py` reads bullet entries from the editable risks file and uses a default message when the file is missing or contains no entries. `report_formatter.py` builds the report tables and sections and applies the overall-status heuristic: blockers or completion below 50% mean At Risk, while blockers plus completion below 30% mean Delayed.

The output path is `<out-dir>/status-report-YYYY-MM-DD.md`, using the Monday date. Existing reports are protected by default; `--force` allows replacement. The README lists the command and all options. For example: `python main.py --team "Staff Aug Delivery Team" --prepared-by "Senthil Kumar"`.

## Summary

- The CLI coordinates configuration, Jira data collection, manual risks, formatting, and archive output.
- Jira credentials are required; risks are supplied separately through an editable file.
- Reports cover a Monday-Friday week, are dated by the Monday start date, and are not overwritten unless `--force` is used.

## Quiz

1. Which module loads and validates Jira environment settings?
2. What dates define the default report period?
3. What happens if the dated output report already exists and `--force` is not supplied?

### Answers

1. `config.py`.
2. Monday through Friday, with Monday selected as the most recent Monday by default.
3. The run stops with an error rather than overwriting the report.
