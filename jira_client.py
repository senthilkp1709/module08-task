"""Jira REST API data fetching for the weekly status report generator.

Covers project_spec.md section 4 (Data Sources): completed/in-progress/blocked
issues, sprint velocity, and per-person utilization — all read-only queries.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import requests

from config import JiraConfig

API_V3 = "/rest/api/3"
AGILE_V1 = "/rest/agile/1.0"
DONE_STATUSES = ("Done",)
IN_PROGRESS_STATUSES = ("In Progress", "In Review")
BLOCKED_STATUSES = ("Blocked",)


@dataclass
class Issue:
    key: str
    summary: str
    assignee: str
    status: str = ""
    blocker: str = ""


@dataclass
class SprintVelocity:
    sprint_name: str
    committed_points: float
    completed_points: float


@dataclass
class Utilization:
    name: str
    assigned_issues: int
    worklog_hours: float


@dataclass
class ReportData:
    completed_issues: list[Issue] = field(default_factory=list)
    in_progress_issues: list[Issue] = field(default_factory=list)
    blocked_issues: list[Issue] = field(default_factory=list)
    velocity: SprintVelocity | None = None
    utilization: list[Utilization] = field(default_factory=list)


class JiraClient:
    """Thin wrapper around the Jira Cloud REST API (core + Agile)."""

    def __init__(self, config: JiraConfig, session: requests.Session | None = None):
        self._config = config
        self._session = session or requests.Session()
        self._session.auth = (config.email, config.api_token)
        self._session.headers.update({"Accept": "application/json"})

    def _get(self, base: str, path: str, **params) -> dict:
        response = self._session.get(f"{self._config.base_url}{base}{path}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def _search(self, jql: str, fields: list[str]) -> list[dict]:
        issues: list[dict] = []
        start_at = 0
        page_size = 100
        while True:
            data = self._get(
                API_V3,
                "/search",
                jql=jql,
                fields=",".join(fields),
                startAt=start_at,
                maxResults=page_size,
            )
            issues.extend(data.get("issues", []))
            start_at += page_size
            if start_at >= data.get("total", 0):
                break
        return issues

    @staticmethod
    def _assignee_name(issue: dict) -> str:
        assignee = issue["fields"].get("assignee")
        return assignee["displayName"] if assignee else "Unassigned"

    def get_completed_issues(self, week_start: dt.date, week_end: dt.date) -> list[Issue]:
        statuses = ", ".join(f'"{s}"' for s in DONE_STATUSES)
        jql = (
            f'project = "{self._config.project_key}" AND status changed to ({statuses}) '
            f'during ("{week_start.isoformat()}", "{week_end.isoformat()}") '
            "ORDER BY updated DESC"
        )
        issues = self._search(jql, fields=["summary", "assignee"])
        return [
            Issue(key=i["key"], summary=i["fields"]["summary"], assignee=self._assignee_name(i))
            for i in issues
        ]

    def get_in_progress_issues(self) -> list[Issue]:
        statuses = ", ".join(f'"{s}"' for s in IN_PROGRESS_STATUSES)
        jql = f'project = "{self._config.project_key}" AND status in ({statuses}) ORDER BY status'
        issues = self._search(jql, fields=["summary", "assignee", "status"])
        return [
            Issue(
                key=i["key"],
                summary=i["fields"]["summary"],
                assignee=self._assignee_name(i),
                status=i["fields"]["status"]["name"],
            )
            for i in issues
        ]

    def get_blocked_issues(self) -> list[Issue]:
        statuses = ", ".join(f'"{s}"' for s in BLOCKED_STATUSES)
        jql = f'project = "{self._config.project_key}" AND status in ({statuses})'
        issues = self._search(jql, fields=["summary", "assignee", "comment"])
        result = []
        for i in issues:
            comments = i["fields"].get("comment", {}).get("comments", [])
            blocker = comments[-1]["body"] if comments else "No blocker details provided."
            if isinstance(blocker, dict):  # Atlassian Document Format body
                blocker = "See issue comments for details."
            result.append(
                Issue(
                    key=i["key"],
                    summary=i["fields"]["summary"],
                    assignee=self._assignee_name(i),
                    blocker=blocker,
                )
            )
        return result

    def _find_board_id(self) -> int | None:
        data = self._get(AGILE_V1, "/board", projectKeyOrId=self._config.project_key)
        boards = data.get("values", [])
        return boards[0]["id"] if boards else None

    def get_sprint_velocity(self) -> SprintVelocity | None:
        board_id = self._find_board_id()
        if board_id is None:
            return None

        sprint_data = self._get(AGILE_V1, f"/board/{board_id}/sprint", state="active")
        sprints = sprint_data.get("values", [])
        if not sprints:
            sprint_data = self._get(AGILE_V1, f"/board/{board_id}/sprint", state="closed")
            sprints = sprint_data.get("values", [])
        if not sprints:
            return None

        sprint = sprints[0]
        field_id = self._config.story_points_field
        issues_data = self._get(
            AGILE_V1, f"/sprint/{sprint['id']}/issue", fields=f"status,{field_id}"
        )

        committed = 0.0
        completed = 0.0
        for issue in issues_data.get("issues", []):
            points = issue["fields"].get(field_id) or 0
            committed += points
            if issue["fields"]["status"]["statusCategory"]["key"] == "done":
                completed += points

        return SprintVelocity(sprint_name=sprint["name"], committed_points=committed, completed_points=completed)

    def get_utilization(self, week_start: dt.date, week_end: dt.date) -> list[Utilization]:
        jql = f'project = "{self._config.project_key}" AND assignee is not EMPTY'
        issues = self._search(jql, fields=["assignee"])

        assigned_counts: dict[str, int] = {}
        worklog_seconds: dict[str, float] = {}
        for issue in issues:
            name = self._assignee_name(issue)
            assigned_counts[name] = assigned_counts.get(name, 0) + 1

            worklog_data = self._get(API_V3, f"/issue/{issue['key']}/worklog")
            for entry in worklog_data.get("worklogs", []):
                started = dt.datetime.fromisoformat(entry["started"]).date()
                if week_start <= started <= week_end:
                    author = entry["author"]["displayName"]
                    worklog_seconds[author] = worklog_seconds.get(author, 0) + entry["timeSpentSeconds"]

        names = sorted(set(assigned_counts) | set(worklog_seconds))
        return [
            Utilization(
                name=name,
                assigned_issues=assigned_counts.get(name, 0),
                worklog_hours=round(worklog_seconds.get(name, 0) / 3600, 1),
            )
            for name in names
        ]

    def fetch_report_data(self, week_start: dt.date, week_end: dt.date) -> ReportData:
        return ReportData(
            completed_issues=self.get_completed_issues(week_start, week_end),
            in_progress_issues=self.get_in_progress_issues(),
            blocked_issues=self.get_blocked_issues(),
            velocity=self.get_sprint_velocity(),
            utilization=self.get_utilization(week_start, week_end),
        )
