"""Configuration loading for the weekly status report generator.

Connection details are supplied via a .env file per project_spec.md section 9.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

REQUIRED_VARS = ("JIRA_BASE_URL", "JIRA_API_TOKEN", "JIRA_EMAIL", "JIRA_PROJECT_KEY")


@dataclass(frozen=True)
class JiraConfig:
    base_url: str
    api_token: str
    email: str
    project_key: str
    # Story point field id varies per Jira instance; defaults to the common one.
    story_points_field: str = "customfield_10016"


def load_config(env_file: str | None = ".env") -> JiraConfig:
    """Load and validate Jira connection settings, failing fast if any are missing."""
    load_dotenv(env_file)

    values = {name: os.environ.get(name, "").strip() for name in REQUIRED_VARS}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill in the values."
        )

    return JiraConfig(
        base_url=values["JIRA_BASE_URL"].rstrip("/"),
        api_token=values["JIRA_API_TOKEN"],
        email=values["JIRA_EMAIL"],
        project_key=values["JIRA_PROJECT_KEY"],
        story_points_field=os.environ.get("JIRA_STORY_POINTS_FIELD", "customfield_10016").strip(),
    )
