#!/usr/bin/env python3
"""
Template Generation Module

Generates all file templates: GEMINI.md, scripts, schemas, configs.
"""

from typing import Dict
import json


# Version constant (imported from config in final build)
VERSION = "2026.26"

def get_gemini_md(tier: str, project_name: str) -> str:
    """Generate GEMINI.md constitution."""
    base = """# Gemini Native Workspace ({edition} Edition)
**Philosophy:** "{philosophy}"
**Role:** {role}
**Version:** {version}

## 1. The Cognitive Laws
1.  **Skill Check:** Before asking "How?", check `.agent/skills/`.
2.  **Workflow Adherence:** Follow `.agent/workflows/` for complex tasks.
3.  **Pattern Matching:** Code must mimic `.agent/patterns/`.
4.  **Evolution:** Use the "Gardener Protocol" to modify rules.

## 2. The Laws of Physics
1.  **Hygiene:** Write temp files to `scratchpad/`.
2.  **Safety:** **NEVER** print secrets to stdout.
3.  **Continuity:** Update `docs/roadmap.md` every session.
4.  **Interface:** Use `Makefile` targets. Do not run raw shell commands.
5.  **Sessions:** Start with `make session-start`, end with `make session-end`.
"""
    if tier == "1":
        return (
            base.format(
                edition="Lite",
                philosophy="Reliable Automation",
                role="Automation Specialist",
                version=VERSION,
            )
            + "\n## 3. Architecture\n* **Input:** `data/inputs/`\n* **Logic:** `src/main.py`\n* **Output:** `logs/run.log`"
        )
    elif tier == "2":
        return (
            base.format(
                edition="Standard",
                philosophy="The Modular Monolith",
                role="Lead Software Engineer",
                version=VERSION,
            )
            + f"\n## 3. Architecture\n* **Modules:** `src/{project_name}/`\n* **Tests:** `tests/unit/`\n* **Context:** Shared Global Context."
        )
    else:
        return (
            base.format(
                edition="Enterprise",
                philosophy="Headless Organization",
                role="CTO / Architect",
                version=VERSION,
            )
            + f"\n## 3. Architecture\n* **Domains:** `src/{project_name}/domains/` (Strict Isolation)\n* **Contracts:** `outputs/contracts/`\n* **Evals:** `tests/evals/`\n\n## 4. Multi-Agent Protocol\n* Sub-Agents do NOT inherit Root Context.\n* Use `make shift-report` for handoffs.\n* Run `make snapshot` before major changes."
        )

def get_github_workflow(tier: str, python_version: str = DEFAULT_PYTHON_VERSION) -> str:
    """Generate GitHub Actions CI workflow with caching and optional matrix testing.

    Args:
        tier: Workspace tier (1, 2, or 3)
        python_version: Primary Python version for CI (also used in matrix)

    Returns:
        YAML content for .github/workflows/ci.yml
    """
    base = f"""name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'
      - name: Audit workspace
        run: python scripts/audit.py
"""
    if tier == "1":
        return (
            base
            + f"""
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'
          cache: 'pip'
      - run: pip install -q -r requirements.txt
      - run: python src/main.py
"""
        )
    elif tier == "2":
        return (
            base
            + f"""
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['{python_version}']
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: 'pip'
      - name: Install dependencies
        run: pip install -q -e ".[dev]"
      - name: Run tests
        run: pytest tests/ -q
      - name: Run tests with coverage (optional)
        run: |
          pip install -q pytest-cov 2>/dev/null || true
          pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=0 2>/dev/null || true
        continue-on-error: true
"""
        )
    else:
        return (
            base
            + f"""
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['{python_version}']
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: 'pip'
      - name: Install uv
        run: pip install -q uv
      - name: Install dependencies
        run: uv sync --quiet
      - name: Run unit tests
        run: uv run pytest tests/unit/ -q

  eval:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'
          cache: 'pip'
      - name: Install uv
        run: pip install -q uv
      - name: Install dependencies
        run: uv sync --quiet
      - name: Run agent evaluations
        run: uv run pytest tests/evals/ -q
"""
        )

def get_audit_script() -> str:
    """Generate workspace audit script."""
    return (
        '''#!/usr/bin/env python3
"""Workspace structure auditor - validates against Gemini Standard."""
import os
import sys
from pathlib import Path

def main():
    print("🔍 Auditing workspace structure...")
    errors = 0
    
    # Check core files
    required = ["GEMINI.md", "Makefile", ".gemini/workspace.json"]
    for f in required:
        if not Path(f).exists():
            print(f"❌ Missing core file: {f}")
            errors += 1
            
    # Check directories
    required_dirs = ["logs", "docs"]
    for d in required_dirs:
        if not Path(d).exists():
            print(f"❌ Missing directory: {d}/")
            errors += 1
            
    if errors == 0:
        print("✅ Audit passed.")
        sys.exit(0)
    else:
        print(f"❌ Audit failed with {errors} errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    )

def get_session_script() -> str:
    """Generate session management script."""
    return (
        '''#!/usr/bin/env python3
"""Session management for Gemini workspaces."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

def load_sessions():
    log_path = Path("logs/sessions/history.json")
    if log_path.exists():
        try:
            with open(log_path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return []

def save_session(entry):
    log_dir = Path("logs/sessions")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    history = load_sessions()
    history.append(entry)
    
    with open(log_dir / "history.json", "w") as f:
        json.dump(history, f, indent=2)
        
    # Also append to human readable log
    with open(log_dir / "session.log", "a") as f:
        f.write(f"[{entry['timestamp']}] {entry['action'].upper()}: {entry['message']}\\n")

def get_git_status():
    try:
        # Get brief stats
        res = subprocess.run(
            ["git", "diff", "--shortstat"], 
            capture_output=True, text=True
        )
        if res.stdout.strip():
            return f"Auto-generated: {res.stdout.strip()}"
            
        # If no diff, maybe staged changes?
        res = subprocess.run(
            ["git", "diff", "--cached", "--shortstat"],
            capture_output=True, text=True
        )
        if res.stdout.strip():
            return f"Auto-generated (staged): {res.stdout.strip()}"
            
        return "Session ended (no changes detected)"
    except FileNotFoundError:
        return "Session ended (git not available)"

def start_session(msg):
    message = msg if msg else "Session started"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "start",
        "message": message
    }
    save_session(entry)
    print(f"🚀 Session started: {message}")

def end_session(msg):
    message = msg if msg else get_git_status()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "end",
        "message": message
    }
    save_session(entry)
    print(f"🎬 Session ended: {message}")

def main():
    parser = argparse.ArgumentParser(description="Session Manager")
    parser.add_argument("command", choices=["start", "end", "force-end-all"])
    parser.add_argument("msg", nargs="?", default="", help="Session message")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_session(args.msg)
    elif args.command == "end":
        end_session(args.msg)
    elif args.command == "force-end-all":
        print("Force ending all sessions...")

if __name__ == "__main__":
    main()
'''
    )


def get_doc_indexer_script() -> str:
    """Generate document indexer script."""
    return (
        r"""#!/usr/bin/env python3
import os
from pathlib import Path

def generate_index():
    docs_path = Path("docs")
    if not docs_path.exists():
        print("❌ docs/ directory not found.")
        return

    readme_content = [
        "# Workspace Index",
        "This file is automatically generated by `make index`. Do not edit manually.",
        "",
        "## 📁 Directories",
        ""
    ]
    
    # Define directory descriptions
    descriptions = {
        "standards": "Workspace rules and bootstrap protocols.",
        "projects": "Project-specific deep-dives and documentation.",
        "knowledge": "General research, notes, and shared learning.",
        "decisions": "Architecture Decision Records (ADRs).",
        "archive": "Historical context and deprecated documents.",
        "templates": "Standard document templates."
    }

    folders = sorted([d for d in docs_path.iterdir() if d.is_dir()])
    
    for folder in folders:
        desc = descriptions.get(folder.name, "")
        header = f"### [{folder.name}](docs/{folder.name}/)"
        if desc:
            header += f" - {desc}"
        readme_content.append(header)
        
        # List files in folder (top level only)
        files = sorted([f for f in folder.iterdir() if f.is_file() and not f.name.startswith(".")])
        if files:
            for file in files:
                readme_content.append(f"* [{file.name}](docs/{folder.name}/{file.name})")
        else:
            readme_content.append("* (No documents yet)")
        readme_content.append("")

    readme_content.append("## 📝 Latest Changes")
    readme_content.append("Check [docs/roadmap.md](docs/roadmap.md) for the latest project logs.")

    with open("README.md", "w") as f:
        f.write("\n".join(readme_content))
    
    print("✅ README.md updated with latest index.")

if __name__ == "__main__":
    generate_index()
"""
    )

def get_status_script() -> str:
    """Generate workspace status script with health dashboard."""
    return (
        '''#!/usr/bin/env python3
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
BLUE = _c('\\033[1;34m')
GREEN = _c('\\033[1;32m')
YELLOW = _c('\\033[1;33m')
RED = _c('\\033[1;31m')
CYAN = _c('\\033[1;36m')
RESET = _c('\\033[0m')

def get_git_info():
    """Get git branch and status info."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        # Check for uncommitted changes
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        has_changes = len(status.split("\\n")) if status else 0
        return branch, has_changes
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None

def get_dependency_age():
    """Check age of dependency files (timezone-aware)."""
    dep_files = ["pyproject.toml", "requirements.txt"]
    for f in dep_files:
        p = Path(f)
        if p.exists():
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).astimezone()
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
    required_files = ["GEMINI.md", "Makefile", ".gemini/workspace.json", "docs/roadmap.md"]
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
        mtime = datetime.fromtimestamp(roadmap.stat().st_mtime, tz=timezone.utc).astimezone()
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
    print(f"{CYAN}📊 Workspace Status{RESET}\\n")
    
    # Workspace metadata
    workspace_file = Path(".gemini/workspace.json")
    if workspace_file.exists():
        with open(workspace_file) as f:
            workspace = json.load(f)
        print(f"Name: {workspace.get('name', 'Unknown')}")
        print(f"Tier: {workspace.get('tier')} ({['Lite', 'Standard', 'Enterprise'][int(workspace.get('tier', '1'))-1]})")
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
        print("\\nIssues:")
        for issue in issues:
            print(f"  • {issue}")
'''
    )

def get_skill_manager_script() -> str:
    """Generate skill manager script for adding/removing skills."""
    lines = [
        '#!/usr/bin/env python3',
        '"""Skill Manager - Install and remove Agent Skills."""',
        'import argparse',
        'import os',
        'import shutil',
        'import sys',
        'import urllib.request',
        'from pathlib import Path',
        '',
        '# Github raw content URL pattern',
        'GITHUB_RAW_BASE = "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"',
        '',
        'def fetch_skill(source: str):',
        '    """Fetch a skill from a URL or GitHub shorthand."""',
        '    print(f"📥 Fetching skill from: {source}")',
        '    ',
        '    # Parse source',
        '    if source.startswith("http"):',
        '        url = source',
        '        filename = source.split("/")[-1]',
        '    elif len(source.split("/")) >= 3:',
        '        # shorthand: owner/repo/path/to/skill.md',
        '        parts = source.split("/")',
        '        owner = parts[0]',
        '        repo = parts[1]',
        '        path = "/".join(parts[2:])',
        '        branch = "main" # Default to main',
        '        ',
        '        # Determine filename',
        '        filename = parts[-1]',
        '        ',
        '        url = GITHUB_RAW_BASE.format(',
        '            owner=owner,',
        '            repo=repo,',
        '            branch=branch,',
        '            path=path',
        '        )',
        '    else:',
        '        print("❌ Invalid source format. Use \'owner/repo/path/to/skill.md\' or full URL.")',
        '        sys.exit(1)',
        '        ',
        '    if not filename.endswith(".md"):',
        '        filename += ".md"',
        '',
        '    # Define target path',
        '    target_dir = Path(".agent/skills")',
        '    # If workflow, go to workflows',
        '    title_lower = filename.lower()',
        '    if "workflow" in title_lower or "guide" in title_lower:',
        '         target_dir = Path(".agent/workflows")',
        '    ',
        '    target_dir.mkdir(parents=True, exist_ok=True)',
        '    target_file = target_dir / filename',
        '    ',
        '    try:',
        '        with urllib.request.urlopen(url) as response:',
        '            content = response.read().decode(\'utf-8\')',
        '            ',
        '        with open(target_file, "w") as f:',
        '            f.write(content)',
        '            ',
        '        print(f"✅ Installed: {target_file}")',
        '        ',
        '    except Exception as e:',
        '        print(f"❌ Failed to fetch skill: {e}")',
        '        sys.exit(1)',
        '',
        'def remove_skill(name: str):',
        '    """Remove a local skill."""',
        '    # check skills and workflows',
        '    paths = [',
        '        Path(".agent/skills") / name,',
        '        Path(".agent/skills") / (name + ".md"),',
        '        Path(".agent/workflows") / name,',
        '        Path(".agent/workflows") / (name + ".md")',
        '    ]',
        '    ',
        '    found = False',
        '    for p in paths:',
        '        if p.exists():',
        '            p.unlink()',
        '            print(f"🗑️  Removed: {p}")',
        '            found = True',
        '            ',
        '    if not found:',
        '        print(f"⚠️  Skill \'{name}\' not found.")',
        '',
        'def main():',
        '    parser = argparse.ArgumentParser(description="Skill Manager")',
        '    subparsers = parser.add_subparsers(dest="command", required=True)',
        '    ',
        '    fetch_parser = subparsers.add_parser("fetch", help="Install a skill")',
        '    fetch_parser.add_argument("source", help="GitHub shorthand (owner/repo/path) or URL")',
        '    ',
        '    remove_parser = subparsers.add_parser("remove", help="Remove a skill")',
        '    remove_parser.add_argument("name", help="Name of the skill to remove")',
        '    ',
        '    args = parser.parse_args()',
        '    ',
        '    if args.command == "fetch":',
        '        fetch_skill(args.source)',
        '    elif args.command == "remove":',
        '        remove_skill(args.name)',
        '',
        'if __name__ == "__main__":',
        '    main()'
    ]
    return "\n".join(lines)

def get_skill_explorer_script() -> str:
    """Generate skill explorer script for discovering skills from GitHub."""
    lines = [
        '#!/usr/bin/env python3',
        '"""Skill Explorer - Discover capabilities from community repositories."""',
        'import argparse',
        'import json',
        'import os',
        'import sys',
        'import urllib.request',
        'import urllib.error',
        'from pathlib import Path',
        '',
        '# Curated sources for discovery',
        'CURATED_SOURCES = [',
        '    "anthropics/skills",',
        '    "google-gemini/gemini-cli",',
        '    "huggingface/skills",',
        '    "langchain-ai/langchain",',
        '    "microsoft/semantic-kernel",',
        '    "heilcheng/awesome-agent-skills"',
        ']',
        '',
        'def search_github(query: str, limit: int = 10):',
        '    """Search GitHub repositories for cues."""',
        '    print(f"🔍 Searching GitHub for \'{query}\'...")',
        '    ',
        '    # Check curated sources first if query matches',
        '    results = []',
        '    query_lower = query.lower()',
        '    ',
        '    for source in CURATED_SOURCES:',
        '        if query_lower in source.lower() or query_lower == "all":',
        '            results.append({',
        '                "name": source,',
        '                "description": "Curated Source",',
        '                "url": f"https://github.com/{source}",',
        '                "stars": "⭐ Verified"',
        '            })',
        '            ',
        '    if results:',
        '        print(f"\\nFound {len(results)} curated source(s):")',
        '        for r in results:',
        '            print(f"   • {r[\'name\']} - {r[\'url\']}")',
        '            ',
        '    # TODO: Real GitHub API search implementation would go here.',
        '    # For now, we guide the user to the curated lists as they are high signal.',
        '    print("\\n💡 Tip: Use \'make skill-add source=owner/repo/path/to/skill.md\' to install.")',
        '    print("   For now, please browse the curated repositories above for skills.")',
        '',
        'def main():',
        '    parser = argparse.ArgumentParser(description="Skill Explorer")',
        '    parser.add_argument("command", choices=["search"], help="Command to run")',
        '    parser.add_argument("query", help="Search term (use \'all\' for curated list)")',
        '    ',
        '    args = parser.parse_args()',
        '    ',
        '    if args.command == "search":',
        '        search_github(args.query)',
        '',
        'if __name__ == "__main__":',
        '    main()',
    ]
    return "\n".join(lines)

def get_skill_discovery_workflow() -> str:
    """Generate the Skill Discovery workflow."""
    lines = [
        '# Workflow: Skill Discovery Protocol',
        '',
        '**Goal**: Identify, Evaluate, and Install new capabilities from external sources.',
        '',
        '## 1. Search',
        'Run the explorer to find relevant repositories:',
        '```bash',
        'make discover q="topic"  # e.g., "python", "docker", "web"',
        '```',
        '',
        '## 2. Evaluate',
        'Before installing, evaluate the source:',
        '- Check the repository URL.',
        '- Look for `.md` files in `skills/` or `tools/` directories.',
        '- Read the raw code/prompt to ensure it matches our safety standards.',
        '',
        '## 3. Adapt',
        'Most external skills need adaptation to the Gemini Native Standard:',
        '1.  **Context**: Does it assume specific file paths?',
        '2.  **Format**: Convert to standard Markdown skill format.',
        '3.  **Refine**: Remove specific mentions of other agents (e.g., "You are Claude").',
        '',
        '## 4. Install',
        'Use the manager to fetch the raw file, then edit:',
        '```bash',
        'make skill-add source="owner/repo/path/to/skill.md"',
        '# Then edit the file in .agent/skills/',
        '```',
    ]
    return "\n".join(lines)


def get_list_skills_script() -> str:
    """Generate cross-platform list-skills script."""
    return (
        '''#!/usr/bin/env python3
"""List available skills and workflows (cross-platform)."""
from pathlib import Path

def list_items(directory: str, label: str, emoji: str):
    """List markdown files in a directory."""
    path = Path(directory)
    if not path.exists():
        return
    
    items = sorted([f.stem for f in path.glob("*.md")])
    if items:
        print(f"\\n{emoji} {label}:")
        for item in items:
            print(f"   - {item}")

if __name__ == "__main__":
    list_items(".agent/skills", "Available Skills", "📚")
    list_items(".agent/workflows", "Available Workflows", "📋")
    list_items(".agent/patterns", "Available Patterns", "🎨")
    print()
'''
    )

def get_workspace_schema() -> str:
    """Generate JSON schema for workspace.json validation and IDE autocomplete."""
    return json.dumps(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Gemini Workspace Configuration",
            "description": "Metadata for Gemini Native Workspace Standard",
            "type": "object",
            "required": ["version", "tier", "name", "created", "standard"],
            "properties": {
                "version": {
                    "type": "string",
                    "description": "Standard version used to create workspace",
                    "pattern": "^\\d{4}\\.\\d+$",
                },
                "tier": {
                    "type": "string",
                    "enum": ["1", "2", "3"],
                    "description": "Workspace tier: 1=Lite, 2=Standard, 3=Enterprise",
                },
                "name": {
                    "type": "string",
                    "description": "Project name",
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_-]*$",
                },
                "created": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 timestamp of workspace creation",
                },
                "standard": {
                    "type": "string",
                    "const": "Gemini Native Workspace Standard",
                },
                "parent_workspace": {
                    "type": "string",
                    "description": "Path to parent workspace (for monorepos)",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "archived"],
                    "default": "active",
                },
                "upgraded": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp of last tier upgrade",
                },
                "previous_tier": {
                    "type": "string",
                    "enum": ["1", "2"],
                    "description": "Tier before last upgrade",
                },
                "scripts_updated": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp of last script update",
                },
            },
        },
        indent=2,
    )

def get_settings_schema() -> str:
    """Generate JSON schema for settings.json validation and IDE autocomplete."""
    return json.dumps(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Gemini Workspace Settings",
            "description": "Permissions and behavior settings for Gemini workspace",
            "type": "object",
            "properties": {
                "permissions": {
                    "type": "object",
                    "properties": {
                        "filesystem": {
                            "type": "object",
                            "properties": {
                                "read": {"type": "array", "items": {"type": "string"}},
                                "edit": {"type": "array", "items": {"type": "string"}},
                                "ignore": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                        "terminal": {
                            "type": "object",
                            "properties": {
                                "execution_policy": {
                                    "type": "string",
                                    "enum": ["safe-only", "hybrid", "unrestricted"],
                                },
                                "allowed_commands": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    },
                },
                "behavior": {
                    "type": "object",
                    "properties": {
                        "auto_context_refresh": {"type": "boolean", "default": True}
                    },
                },
                "parent_workspace": {"type": "string"},
            },
        },
        indent=2,
    )

def get_bootstrap_config_schema() -> str:
    """Generate JSON schema for .gemini-bootstrap.json validation and documentation."""
    return json.dumps(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Gemini Bootstrap Configuration",
            "description": "Team defaults for the Gemini workspace bootstrap script",
            "type": "object",
            "properties": {
                "default_tier": {
                    "type": "string",
                    "enum": ["1", "2", "3"],
                    "description": "Default tier for new workspaces (1=Lite, 2=Standard, 3=Enterprise)",
                },
                "shared_agent_path": {
                    "type": "string",
                    "description": "Path to shared .agent/ directory for team-wide skills/workflows",
                },
                "templates_path": {
                    "type": "string",
                    "description": "Path to custom templates directory",
                },
                "default_git": {
                    "type": "boolean",
                    "default": False,
                    "description": "Initialize git repository by default",
                },
                "python_version": {
                    "type": "string",
                    "pattern": "^3\\.\\d+$",
                    "default": "3.11",
                    "description": "Python version for CI workflows",
                },
            },
        },
        indent=2,
    )

def get_precommit_config() -> str:
    """Generate .pre-commit-config.yaml template."""
    return """# Pre-commit hooks configuration
# Install: pip install pre-commit && pre-commit install
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  # Uncomment for conventional commits
  # - repo: https://github.com/compilerla/conventional-pre-commit
  #   rev: v3.2.0
  #   hooks:
  #     - id: conventional-pre-commit
  #       stages: [commit-msg]
"""