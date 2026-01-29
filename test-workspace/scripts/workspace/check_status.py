#!/usr/bin/env python3
"""Show workspace status with health dashboard."""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Respect NO_COLOR environment variable
USE_COLOR = not os.environ.get("NO_COLOR")


def _c(code: str) -> str:
    return code if USE_COLOR else ""


# Pre-define colors to avoid backslashes in f-strings (Py3.11 compatibility)
BLUE = _c("\033[1;34m")
GREEN = _c("\033[1;32m")
YELLOW = _c("\033[1;33m")
RED = _c("\033[1;31m")
CYAN = _c("\033[1;36m")
RESET = _c("\033[0m")


def get_git_info():
    """Get git branch and status info."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        # Check for uncommitted changes
        status = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout.strip()

        has_changes = len(status.split("\n")) if status else 0
        return branch, has_changes
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None


def get_dependency_age():
    """Check age of dependency files (timezone-aware)."""
    dep_files = ["pyproject.toml", "requirements.txt"]
    for f in dep_files:
        p = Path(f)
        if p.exists():
            mtime = datetime.fromtimestamp(
                p.stat().st_mtime, tz=timezone.utc
            ).astimezone()
            days_ago = (datetime.now(timezone.utc).astimezone() - mtime).days
            return f, days_ago
    return None, None


def calculate_health_score():
    """Calculate workspace health score (0-100).

    Returns:
        Tuple of (score, issues_list)
    """
    score = 100
    issues = []

    # Check required files (25 points)
    required_files = [
        "GEMINI.md",
        "Makefile",
        ".gemini/workspace.json",
        "docs/roadmap.md",
    ]
    for f in required_files:
        if not Path(f).exists():
            score -= 6
            issues.append(f"Missing {f}")

    # Check git status (20 points)
    branch, changes = get_git_info()
    if branch is None:
        score -= 10
        issues.append("No git repository")
    elif changes and changes > 10:
        score -= 10
        issues.append(f"{changes} uncommitted changes")
    elif changes and changes > 0:
        score -= 5

    # Check session tracking (15 points)
    sessions_dir = Path("logs/sessions")
    if not sessions_dir.exists():
        score -= 15
        issues.append("No sessions directory")

    # Check documentation freshness (20 points)
    roadmap = Path("docs/roadmap.md")
    if roadmap.exists():
        mtime = datetime.fromtimestamp(
            roadmap.stat().st_mtime, tz=timezone.utc
        ).astimezone()
        days_ago = (datetime.now(timezone.utc).astimezone() - mtime).days
        if days_ago > 90:
            score -= 20
            issues.append(f"Roadmap stale ({days_ago} days)")
        elif days_ago > 30:
            score -= 10
            issues.append(f"Roadmap aging ({days_ago} days)")

    # Check dependency freshness (20 points)
    dep_file, dep_age = get_dependency_age()
    if dep_file and dep_age:
        if dep_age > 180:
            score -= 20
            issues.append(f"{dep_file} very old ({dep_age} days)")
        elif dep_age > 90:
            score -= 10
            issues.append(f"{dep_file} aging ({dep_age} days)")

    return max(0, score), issues


if __name__ == "__main__":
    print(f"{CYAN}📊 Workspace Status{RESET}\n")

    # Workspace metadata
    workspace_file = Path(".gemini/workspace.json")
    if workspace_file.exists():
        with open(workspace_file) as f:
            workspace = json.load(f)
        print(f"Name: {workspace.get('name', 'Unknown')}")
        print(
            f"Tier: {workspace.get('tier')} ({['Lite', 'Standard', 'Enterprise'][int(workspace.get('tier', '1')) - 1]})"
        )
        print(f"Created: {workspace.get('created', 'Unknown')}")
    else:
        print("⚠️  No workspace.json found")

    # Git info
    print()
    branch, changes = get_git_info()
    if branch:
        print(f"Branch: {branch}")
        if changes:
            print(f"Uncommitted changes: {changes}")
        else:
            print("Working tree clean ✓")

    # Health score
    print()
    score, issues = calculate_health_score()
    if score >= 90:
        indicator = f"{GREEN}🟢"
        rating = "Excellent"
    elif score >= 70:
        indicator = f"{YELLOW}🟡"
        rating = "Good"
    elif score >= 50:
        indicator = f"{YELLOW}🟠"
        rating = "Fair"
    else:
        indicator = f"{RED}🔴"
        rating = "Needs Attention"

    print(f"Health: {indicator} {score}/100 ({rating}){RESET}")

    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"  • {issue}")
