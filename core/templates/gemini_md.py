#!/usr/bin/env python3
"""
GEMINI.md Constitution Template Generator

Generates tier-specific GEMINI.md constitution files.
"""

# Version constant (imported from config in final build)
VERSION = "1.0.1"


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
