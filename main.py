"""CLI entry point: generates a dated weekly status report Markdown file.

Usage:
    python main.py --team "Staff Aug Delivery Team" --prepared-by "Senthil Kumar"

Writes reports/status-report-YYYY-MM-DD.md (date = week start, Monday) and
never overwrites an existing report for that week (use --force to override).
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

from config import load_config
from jira_client import JiraClient
from report_formatter import build_markdown_report
from risks_input import DEFAULT_RISKS_FILE, load_risks

REPORTS_DIR = "reports"


def _most_recent_monday(today: dt.date) -> dt.date:
    return today - dt.timedelta(days=today.weekday())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the weekly Jira status report.")
    parser.add_argument("--team", required=True, help="Team/engagement name.")
    parser.add_argument("--prepared-by", required=True, help="Report author.")
    parser.add_argument(
        "--week-start",
        type=dt.date.fromisoformat,
        default=None,
        help="Monday of the report week (YYYY-MM-DD). Defaults to the most recent Monday.",
    )
    parser.add_argument(
        "--executive-summary",
        default="",
        help="One or two sentence overall health summary.",
    )
    parser.add_argument("--risks-file", default=DEFAULT_RISKS_FILE, help="Path to the risks input file.")
    parser.add_argument("--env-file", default=".env", help="Path to the .env file with Jira credentials.")
    parser.add_argument("--out-dir", default=REPORTS_DIR, help="Directory to write the dated report into.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing report for the week.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    week_start = args.week_start or _most_recent_monday(dt.date.today())
    week_end = week_start + dt.timedelta(days=4)
    today = dt.date.today()

    config = load_config(args.env_file)
    client = JiraClient(config)
    data = client.fetch_report_data(week_start, week_end)
    risks = load_risks(args.risks_file)

    report = build_markdown_report(
        team_name=args.team,
        prepared_by=args.prepared_by,
        week_start=week_start,
        week_end=week_end,
        date_generated=today,
        data=data,
        risks=risks,
        executive_summary=args.executive_summary or "No summary provided.",
        data_source_note=f"Source: Jira project {config.project_key}, generated {today.isoformat()}.",
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"status-report-{week_start.isoformat()}.md"
    if out_path.exists() and not args.force:
        raise SystemExit(f"{out_path} already exists. Use --force to overwrite.")

    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
