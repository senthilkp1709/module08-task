"""Risks & escalations input handling (project_spec.md section 11).

Risks aren't tracked in Jira, so the Delivery Manager maintains a small editable
Markdown file (default: risks-this-week.md) that this module reads and embeds
verbatim into the generated report.
"""
from __future__ import annotations

from pathlib import Path

DEFAULT_RISKS_FILE = "risks-this-week.md"


def load_risks(path: str | Path = DEFAULT_RISKS_FILE) -> list[str]:
    """Read bullet-point risk entries from an editable input file.

    Lines that are blank, HTML comments, or don't start with a bullet marker
    are ignored. Returns the risk lines with the leading "- " stripped.
    """
    risks_path = Path(path)
    if not risks_path.exists():
        return ["None this week."]

    lines: list[str] = []
    in_comment = False
    for raw_line in risks_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("<!--"):
            in_comment = True
        if in_comment:
            if line.endswith("-->"):
                in_comment = False
            continue
        if line.startswith("- "):
            lines.append(line[2:].strip())
        elif line.startswith("-") and len(line) > 1:
            lines.append(line[1:].strip())

    return lines or ["None this week."]
