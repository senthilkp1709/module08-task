"""Markdown formatting logic for the weekly status report (project_spec.md section 6).

Fills in the structure from module09-task/reports/template.md using data
fetched from Jira plus manually supplied risks.
"""
from __future__ import annotations

import datetime as dt

from jira_client import ReportData

ON_TRACK = "On Track"
AT_RISK = "At Risk"
DELAYED = "Delayed"


def determine_overall_status(data: ReportData) -> str:
    """Heuristic per project_spec.md section 12 (exact formula left to implementation).

    Blocked issues or a sub-50% velocity completion rate puts the week At Risk;
    a lower completion rate (<30%) with blockers is Delayed; otherwise On Track.
    """
    completion_ratio = 1.0
    if data.velocity and data.velocity.committed_points:
        completion_ratio = data.velocity.completed_points / data.velocity.committed_points

    if data.blocked_issues and completion_ratio < 0.3:
        return DELAYED
    if data.blocked_issues or completion_ratio < 0.5:
        return AT_RISK
    return ON_TRACK


def _issue_table(rows: list[tuple[str, ...]], headers: tuple[str, ...]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join("---" for _ in headers) + "|"
    if not rows:
        empty_row = "| " + " | ".join("" for _ in headers) + " |"
        return "\n".join([header_line, sep_line, empty_row])
    body_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, sep_line, *body_lines])


def build_markdown_report(
    *,
    team_name: str,
    prepared_by: str,
    week_start: dt.date,
    week_end: dt.date,
    date_generated: dt.date,
    data: ReportData,
    risks: list[str],
    executive_summary: str,
    data_source_note: str,
) -> str:
    overall_status = determine_overall_status(data)

    completed_table = _issue_table(
        [(i.key, i.summary, i.assignee) for i in data.completed_issues],
        ("Key", "Summary", "Assignee"),
    )
    in_progress_table = _issue_table(
        [(i.key, i.summary, i.assignee, i.status) for i in data.in_progress_issues],
        ("Key", "Summary", "Assignee", "Status"),
    )
    blocked_table = _issue_table(
        [(i.key, i.summary, i.assignee, i.blocker) for i in data.blocked_issues],
        ("Key", "Summary", "Assignee", "Blocker"),
    )
    utilization_table = _issue_table(
        [(u.name, str(u.assigned_issues), str(u.worklog_hours)) for u in data.utilization],
        ("Name", "Assigned Issues", "Worklog Hours"),
    )

    committed = data.velocity.committed_points if data.velocity else ""
    completed_points = data.velocity.completed_points if data.velocity else ""

    risks_section = "\n".join(f"- {risk}" for risk in risks) if risks else "- None this week."

    return f"""# Weekly Status Report

**Team:** {team_name}
**Report Week:** {week_start.isoformat()} to {week_end.isoformat()}
**Prepared By:** {prepared_by}
**Date Generated:** {date_generated.isoformat()}

## Executive Summary
{executive_summary}

## Overall Status
{overall_status}

## Completed Issues
{completed_table}

## In-Progress Issues
{in_progress_table}

## Blocked Issues
{blocked_table}

## Sprint Velocity / Burndown
| Metric | Value |
|---|---|
| Committed Story Points | {committed} |
| Completed Story Points | {completed_points} |

## Individual Utilization
{utilization_table}

## Risks & Escalations
{risks_section}

## Footer
{data_source_note}
"""
