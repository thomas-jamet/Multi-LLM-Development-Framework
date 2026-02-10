"""Workspace upgrade operations.

Handles upgrading workspaces to higher tiers.
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

try:
    from config import TIERS
    from core_utils import (
        success,
        warning,
        info,
        header,
        _c,
        Colors,
        ValidationError,
        ConfigurationError,
        UpgradeError,
    )
    from core.templates import get_gemini_md, get_github_workflow
    from core.makefile import get_makefile
    from operations.utils import (
        get_shift_report_script,
        get_vscode_settings,
        get_settings,
    )
except ImportError:
    # During build, imports are flat
    from ..config import TIERS
    from ..core_utils import (
        success,
        warning,
        info,
        header,
        _c,
        Colors,
        ValidationError,
        ConfigurationError,
        UpgradeError,
    )
    from ..core.templates import get_gemini_md, get_github_workflow
    from ..core.makefile import get_makefile
    from .utils import get_shift_report_script, get_vscode_settings, get_settings


def upgrade_workspace(
    path: str, target_tier: str | None = None, yes: bool = False
) -> None:
    """Upgrade a workspace to a higher tier.

    Args:
        path: Path to workspace to upgrade
        target_tier: Target tier to upgrade to (optional, defaults to next tier)
        yes: If True, skip confirmation prompts (for CI/CD automation)

    Raises:
        UpgradeError: If upgrade fails or target tier is lower than current (downgrade)
        ValidationError: If workspace doesn't exist or is invalid
        ConfigurationError: If workspace.json is malformed
    """
    base = Path(path).resolve()

    if not base.exists():
        raise ValidationError(f"Path does not exist: {path}")

    ws_file = base / ".gemini/workspace.json"
    if not ws_file.exists():
        raise ValidationError("Not a Gemini workspace")

    try:
        with open(ws_file) as f:
            ws = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid workspace.json (malformed JSON): {e}") from e
    except PermissionError as e:
        raise ConfigurationError(
            "Cannot read workspace.json (permission denied)"
        ) from e

    current_tier = ws.get("tier", "1")
    current_order = TIERS[current_tier]["order"]

    header(f"Current: {TIERS[current_tier]['name']}")

    # Determine target tier
    if target_tier:
        # Validate it's an upgrade, not a downgrade
        target_order = TIERS[target_tier]["order"]
        if target_order < current_order:
            raise UpgradeError(
                f"Cannot downgrade from tier {current_tier} to tier {target_tier}. "
                f"Use rollback instead if you need to restore a previous state."
            )
        if target_order == current_order:
            info(f"Already at tier {current_tier} - no upgrade needed")
            return
        final_target = target_tier
    else:
        # Default to next tier
        if current_order >= 3:
            info("Already at Enterprise tier - no upgrade available")
            return
        final_target = str(current_order + 1)
    pkg_name = (
        ws.get("name", base.name)
        .replace("-", "_")
        .replace(" ", "_")
        .replace(".", "_")
        .lower()
    )

    # Build detailed change preview
    print(
        f"\n{_c(Colors.BOLD)}Upgrading to: {TIERS[final_target]['name']}{_c(Colors.RESET)}\n"
    )

    if final_target == "2":
        print(f"{_c(Colors.GREEN)}✅ Will Add:{_c(Colors.RESET)}")
        print(f"   📂 src/{pkg_name}/ - Modular package structure")
        print("   📂 tests/unit/ - Unit test directory")
        print("   📂 tests/integration/ - Integration test directory")
        print("   📂 .snapshots/ - Snapshot/restore support")
        print("   📄 pyproject.toml - Python package metadata")
        print("   📄 .agent/skills/debug.md - Debug protocol")
        print("   📄 .agent/workflows/feature.md - Feature workflow")
        print(f"\n{_c(Colors.YELLOW)}⚠️  Will Modify:{_c(Colors.RESET)}")
        print("   📄 GEMINI.md - Role: 'Lead Software Engineer'")
        print("   📄 Makefile - Add: test, snapshot, typecheck targets")
        print("   📄 .gemini/settings.json - Update permissions")
        print(f"\n{_c(Colors.RED)}🗑️  Will Remove:{_c(Colors.RESET)}")
        print("   📄 requirements.txt - replaced by pyproject.toml")
    elif final_target == "3":
        print(f"{_c(Colors.GREEN)}✅ Will Add:{_c(Colors.RESET)}")
        print(f"   📂 src/{pkg_name}/domains/frontend/ - Frontend domain")
        print(f"   📂 src/{pkg_name}/domains/backend/ - Backend domain")
        print("   📂 outputs/contracts/ - Inter-domain schemas")
        print("   📂 tests/evals/ - Agent capability tests")
        print("   📂 docs/decisions/ - Architecture Decision Records")
        print("   📂 inputs/ - Read-only data directory")
        print("   📄 scripts/shift_report.py - Handoff reports")
        print(f"\n{_c(Colors.YELLOW)}⚠️  Will Modify:{_c(Colors.RESET)}")
        print("   📄 GEMINI.md - Role: 'CTO / Architect'")
        print("   📄 Makefile - Add: scan, eval, shift-report, lock targets")
        print("   📄 .gemini/settings.json - Update permissions")

    print(f"\n{_c(Colors.BLUE)}📦 Backup:{_c(Colors.RESET)}")
    print("   Modified files are saved to .gemini/backups/pre_upgrade_<TIMESTAMP>/")

    # Confirmation unless --yes is passed
    if not yes:
        response = (
            input(f"\n{_c(Colors.BOLD)}Proceed with upgrade? [y/N]{_c(Colors.RESET)} ")
            .strip()
            .lower()
        )
        if response != "y":
            print("Upgrade cancelled.")
            return

    # Add missing structure
    # When upgrading multiple tiers (e.g., 1->3), apply all intermediate structures
    if int(final_target) >= 2 and int(current_tier) < 2:
        # Apply Standard tier structure (needed for tier 2 and above)
        (base / f"src/{pkg_name}").mkdir(parents=True, exist_ok=True)
        (base / "tests/unit").mkdir(parents=True, exist_ok=True)
        (base / "tests/integration").mkdir(parents=True, exist_ok=True)

        if not (base / f"src/{pkg_name}/__init__.py").exists():
            (base / f"src/{pkg_name}/__init__.py").write_text("")

        if not (base / "pyproject.toml").exists():
            (base / "pyproject.toml").write_text(
                f'[project]\nname = "{pkg_name}"\nversion = "0.1.0"'
            )

        if not (base / ".agent/skills/debug.md").exists():
            (base / ".agent/skills/debug.md").write_text(
                "# Debug Skill\n\nDebug protocol skill."
            )

        if not (base / ".agent/workflows/feature.md").exists():
            (base / ".agent/workflows/feature.md").write_text(
                "# Feature Workflow\n\nFeature implementation workflow."
            )

        # Clean up Lite tier artifacts
        if (base / "requirements.txt").exists():
            (base / "requirements.txt").unlink()
            warning("removed obsolete requirements.txt")

    if int(final_target) >= 3 and int(current_tier) < 3:
        # Apply Enterprise tier structure (needed for tier 3)
        (base / f"src/{pkg_name}/domains/frontend").mkdir(parents=True, exist_ok=True)
        (base / f"src/{pkg_name}/domains/backend").mkdir(parents=True, exist_ok=True)
        (base / "outputs/contracts").mkdir(parents=True, exist_ok=True)
        (base / "tests/evals").mkdir(parents=True, exist_ok=True)
        (base / "docs/decisions").mkdir(parents=True, exist_ok=True)
        (base / "inputs").mkdir(
            parents=True, exist_ok=True
        )  # Enterprise-specific input directory

        if not (base / f"src/{pkg_name}/domains/frontend/GEMINI.md").exists():
            (base / f"src/{pkg_name}/domains/frontend/GEMINI.md").write_text(
                "# Domain: Frontend\nContext: UI Only."
            )

        if not (base / f"src/{pkg_name}/domains/backend/GEMINI.md").exists():
            (base / f"src/{pkg_name}/domains/backend/GEMINI.md").write_text(
                "# Domain: Backend\nContext: API Only."
            )

        if not (base / "scripts/shift_report.py").exists():
            (base / "scripts/shift_report.py").write_text(get_shift_report_script())

    # Update workspace.json
    ws["tier"] = final_target
    ws["upgraded"] = datetime.now(timezone.utc).astimezone().isoformat()
    ws["previous_tier"] = current_tier

    with open(ws_file, "w") as f:
        json.dump(ws, f, indent=2)

    # Backup existing config files before overwriting
    backup_files = [
        "GEMINI.md",
        "Makefile",
        ".gemini/settings.json",
        ".vscode/settings.json",
        ".github/workflows/ci.yml",
    ]
    backup_dir = (
        base
        / ".gemini/backups"
        / f"pre_upgrade_{datetime.now(timezone.utc).astimezone().strftime('%Y%m%d_%H%M%S')}"
    )
    backup_dir.mkdir(parents=True, exist_ok=True)

    for fname in backup_files:
        fpath = base / fname
        if fpath.exists():
            # Handle nested files by flattening or keeping structure relative to backup_dir?
            # Simple flatten for these specific files is usually okay, but let's be safe
            dest = backup_dir / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fpath, dest)
            info(f"Backed up {fname} to {dest}")

    # Update GEMINI.md
    (base / "GEMINI.md").write_text(get_gemini_md(final_target, pkg_name))

    # Update Makefile
    (base / "Makefile").write_text(get_makefile(final_target, pkg_name))

    # Update CI/CD
    (base / ".github/workflows/ci.yml").write_text(get_github_workflow(final_target))

    # Update VS Code settings
    (base / ".vscode/settings.json").write_text(get_vscode_settings())

    # Update settings.json for new tier permissions
    (base / ".gemini/settings.json").write_text(get_settings(final_target))

    success(f"Upgraded to {TIERS[final_target]['name']}")
