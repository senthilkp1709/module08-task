# Weekly Status Report Generator (module08-task)

## Usage

Generate the current week's report:

```
python main.py --team "Staff Aug Delivery Team" --prepared-by "Senthil Kumar"
```

Flags:
- `--team` (required) — team/engagement name.
- `--prepared-by` (required) — report author.
- `--week-start` — Monday of the report week (`YYYY-MM-DD`). Defaults to the most recent Monday.
- `--executive-summary` — one or two sentence overall health summary.
- `--risks-file` — path to the risks input file. Defaults to `risks-this-week.md`.
- `--env-file` — path to the `.env` file with Jira credentials. Defaults to `.env`.
- `--out-dir` — directory to write the dated report into. Defaults to `reports`.
- `--force` — overwrite an existing report for the week instead of failing.

Output is written to `<out-dir>/status-report-YYYY-MM-DD.md` (date = week start Monday). The run fails if that file already exists unless `--force` is passed.
