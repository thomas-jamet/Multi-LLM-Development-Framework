#!/usr/bin/env python3
"""
Workspace Operations Module

Handles workspace creation, validation, and upgrades.
"""

from pathlib import Path
from typing import Dict, List
import os
import json
from datetime import datetime, timezone
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def create_workspace(
    tier: str,
    name: str,
    dry_run: bool = False,
    init_git: bool = False,
    shared_agent: str | None = None,
    parent: str | None = None,
    template_files: dict | None = None,
    template_deps: list | None = None,
    force: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    python_version: str = DEFAULT_PYTHON_VERSION,
) -> None:
    """Create a new Gemini workspace with specified configuration.

    Creates a complete workspace directory structure based on the selected tier,
    with all necessary configuration files, scripts, and cognitive layer components.

    Args:
        tier: Workspace tier ('1'=Lite, '2'=Standard, '3'=Enterprise)
        name: Project name (used for directory and package naming)
        dry_run: If True, preview what would be created without writing files
        init_git: If True, initialize a git repository in the workspace
        shared_agent: Path to shared .agent/ directory (creates symlink)
        parent: Path to parent workspace (for monorepo child projects)
        template_files: Dict of {path: content} for template-specific files
        template_deps: List of additional dependencies from template
        force: If True, overwrite existing directory
        quiet: If True, minimal output
        verbose: If True, detailed output
        python_version: Python version for CI workflows (e.g., '3.11')

    Raises:
        CreationError: On workspace creation failure
        ValidationError: On invalid project name

    Note:
        On partial failure during creation, attempts cleanup of created directory.
    """
    # Validate FIRST before any destructive operations
    validate_project_name(name)

    # Check for existing git repo in target location
    target_path = Path.cwd() / name
    if (target_path / ".git").exists() and not force:
        warning(f"Directory '{name}' contains an existing git repository")
        info(
            "Use --force to overwrite, or manually add Gemini workspace files to the existing project"
        )

    pkg_name = name.replace("-", "_").replace(" ", "_").replace(".", "_").lower()
    base = Path(parent) / name if parent else Path.cwd() / name

    # Ensure parent directory exists if specified
    if parent:
        parent_path = Path(parent)
        if not parent_path.exists():
            try:
                parent_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise CreationError(
                    f"Cannot create parent directory {parent}: {e}"
                ) from e

    # Pre-flight writability check
    if not dry_run:
        target_dir = Path(parent) if parent else Path.cwd()
        try:
            test_path = target_dir / f".gemini_preflight_{name}"
            test_path.mkdir()
            test_path.rmdir()
        except PermissionError as e:
            raise CreationError(f"Cannot write to directory: {target_dir}") from e
        except OSError as e:
            raise CreationError(f"Filesystem error during pre-flight check: {e}") from e

    if base.exists() and not dry_run:
        if force:
            if not quiet:
                warning(f"Removing existing directory '{name}'")
            shutil.rmtree(base)
        else:
            raise CreationError(
                f"Directory '{name}' already exists. Use --force to overwrite."
            )

    # Use helper functions to build structure
    dirs = _build_workspace_directories(tier, pkg_name)
    files = _build_workspace_files(
        tier, name, pkg_name, parent, python_version, template_files, template_deps
    )

    # --- DRY RUN ---
    if dry_run:
        # NEW: Use enhanced dry-run summary
        template_name = None
        if template_files:
            # Try to determine template name from files
            for tmpl_name, tmpl_config in TEMPLATES.items():
                if tmpl_config.get("files") == template_files:
                    template_name = tmpl_name
                    break

        show_dry_run_summary(tier, name, template_name, Path.cwd())

        # Still show detailed file/dir list for reference
        header("Detailed Structure Preview")
        print(f"\n📁 {name}/")
        for d in sorted(dirs):
            print(f"   📂 {d}/")
        print()
        for f in sorted(list(files.keys())[:20]):  # Show first 20 files
            print(f"   📄 {f}")
        if len(files) > 20:
            print(f"   ... and {len(files) - 20} more files")

        return

    # --- CREATE WITH ROLLBACK ---
    try:
        total_steps = len(dirs) + len(files)
        current = 0

        # Create directories sequentially (fast and avoids race conditions)
        for d in dirs:
            (base / d).mkdir(parents=True, exist_ok=True)
            current += 1
            if not quiet and current % 10 == 0:
                print(f"Progress: {current}/{total_steps} (Creating directories...)")
            if verbose:
                dim(f"  Created directory: {d}")

        # Write files in parallel for improved performance
        errors = []
        max_workers = min(32, len(files) if files else 1)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file writes to thread pool
            future_to_path = {
                executor.submit(_write_file_safe, base, path_str, content): path_str
                for path_str, content in files.items()
            }

            # Collect results as they complete
            for future in as_completed(future_to_path):
                path_str, err = future.result()
                current += 1

                if err:
                    errors.append((path_str, err))
                else:
                    if not quiet and current % 10 == 0:
                        print(f"Progress: {current}/{total_steps} (Writing files...)")
                    if verbose:
                        dim(f"  Created file: {path_str}")

        # Check for any errors during parallel writes
        if errors:
            error_summary = "; ".join([f"{p}: {e}" for p, e in errors[:3]])
            if len(errors) > 3:
                error_summary += f" (+{len(errors) - 3} more)"
            raise CreationError(
                f"Failed to write {len(errors)} file(s): {error_summary}"
            )

        (base / ".env").touch()
        if verbose:
            dim("  Created file: .env")

    except CreationError:
        # Re-raise CreationError from parallel writes
        if base.exists():
            warning("Rolling back partial workspace creation...")
            try:
                shutil.rmtree(base)
            except Exception as cleanup_err:
                warning(f"Failed to clean up partial workspace: {cleanup_err}")
        raise
    except (OSError, IOError, UnicodeEncodeError) as e:
        if base.exists():
            warning("Rolling back partial workspace creation...")
            try:
                shutil.rmtree(base)
            except Exception as cleanup_err:
                warning(f"Failed to clean up partial workspace: {cleanup_err}")
        raise CreationError(f"Failed to create workspace: {e}") from e

    # Shared agent symlink (with copy fallback for Windows)
    if shared_agent:
        shared_path = Path(shared_agent).resolve()
        if shared_path.exists():
            local_agent = base / ".agent"
            try:
                if local_agent.exists():
                    shutil.rmtree(local_agent)
                local_agent.symlink_to(shared_path)
                success(f"Linked .agent/ to {shared_agent}")
            except OSError as e:
                # Symlink failed (common on Windows without admin) - fall back to copy
                warning(f"Symlink failed ({e}), copying instead...")
                try:
                    shutil.copytree(shared_path, local_agent)
                    success(f"Copied .agent/ from {shared_agent} (symlink unavailable)")
                    info(
                        "Note: Changes to shared agent won't sync. Consider re-running with admin privileges."
                    )
                except Exception as copy_err:
                    error(f"Failed to copy shared agent: {copy_err}")
        else:
            warning(f"Shared agent path not found: {shared_agent}")

    # Git init
    if init_git:
        try:
            subprocess.run(
                ["git", "init", str(base)], check=True, capture_output=True, timeout=10
            )
            success("Initialized git repository")
        except (subprocess.CalledProcessError, FileNotFoundError):
            warning("Failed to initialize git repository")

    success(f"Created '{name}' ({TIERS[tier]['name']})")

    # NEW: Log successful creation (opt-in telemetry)
    template_name = None
    if template_files:
        for tmpl_name, tmpl_config in TEMPLATES.items():
            if tmpl_config.get("files") == template_files:
                template_name = tmpl_name
                break

    log_bootstrap_event(
        "workspace_created",
        tier=tier,
        template=template_name if template_name else "none",
        has_git=init_git,
        has_parent=bool(parent),
        files_count=len(files),
        dirs_count=len(dirs),
    )

    print(f"\n   👉 cd {name}")
    print("   👉 cat docs/GETTING_STARTED.md")


# --- VALIDATE EXISTING WORKSPACE ---


@lru_cache(maxsize=128)

def validate_workspace(path: str):
    """Validate an existing workspace against the standard.

    Args:
        path: Path to workspace to validate

    Raises:
        ValidationError: If workspace fails validation checks
        ConfigurationError: If workspace.json is malformed

    Note:
        This function uses caching to avoid redundant validation checks.
        Cache is automatically invalidated when workspace.json is modified.
    """
    base = Path(path).resolve()

    header(f"Validating: {base.name}")

    # Generate cache key based on workspace.json modification time
    ws_file = base / ".gemini/workspace.json"
    cache_key = _get_file_cache_key(ws_file) if ws_file.exists() else "missing"

    # Use cached validation
    ws, issues = _validate_workspace_impl(str(base), cache_key)

    info(f"Workspace version: {ws.get('version', 'unknown')}")
    info(f"Tier: {ws.get('tier', 'unknown')}")

    # Run audit script if exists (not cached due to external execution)
    audit_script = base / "scripts/audit.py"
    if audit_script.exists():
        result = subprocess.run(
            [sys.executable, str(audit_script)], cwd=base, timeout=30
        )
        if result.returncode != 0:
            raise ValidationError(
                f"Audit script failed with exit code {result.returncode}"
            )
    elif issues:
        # Report cached validation issues
        error("Validation failed:")
        for i in issues:
            print(f"   - {i}")
        raise ValidationError(f"Validation failed: {len(issues)} issues found")
    else:
        success("Validation passed")


# --- UPGRADE WORKSPACE ---

def upgrade_workspace(path: str, target_tier: str | None = None, yes: bool = False):
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
        print(f"   📂 tests/unit/ - Unit test directory")
        print(f"   📂 tests/integration/ - Integration test directory")
        print(f"   📂 .snapshots/ - Snapshot/restore support")
        print(f"   📄 pyproject.toml - Python package metadata")
        print(f"   📄 .agent/skills/debug.md - Debug protocol")
        print(f"   📄 .agent/workflows/feature.md - Feature workflow")
        print(f"\n{_c(Colors.YELLOW)}⚠️  Will Modify:{_c(Colors.RESET)}")
        print(f"   📄 GEMINI.md - Role: 'Lead Software Engineer'")
        print(f"   📄 Makefile - Add: test, snapshot, typecheck targets")
        print(f"   📄 .gemini/settings.json - Update permissions")
        print(f"\n{_c(Colors.RED)}🗑️  Will Remove:{_c(Colors.RESET)}")
        print(f"   📄 requirements.txt - replaced by pyproject.toml")
    elif final_target == "3":
        print(f"{_c(Colors.GREEN)}✅ Will Add:{_c(Colors.RESET)}")
        print(f"   📂 src/{pkg_name}/domains/frontend/ - Frontend domain")
        print(f"   📂 src/{pkg_name}/domains/backend/ - Backend domain")
        print(f"   📂 outputs/contracts/ - Inter-domain schemas")
        print(f"   📂 tests/evals/ - Agent capability tests")
        print(f"   📂 docs/decisions/ - Architecture Decision Records")
        print(f"   📂 inputs/ - Read-only data directory")
        print(f"   📄 scripts/shift_report.py - Handoff reports")
        print(f"\n{_c(Colors.YELLOW)}⚠️  Will Modify:{_c(Colors.RESET)}")
        print(f"   📄 GEMINI.md - Role: 'CTO / Architect'")
        print(f"   📄 Makefile - Add: scan, eval, shift-report, lock targets")
        print(f"   📄 .gemini/settings.json - Update permissions")

    print(f"\n{_c(Colors.BLUE)}📦 Backup:{_c(Colors.RESET)}")
    print(f"   Modified files are saved to .gemini/backups/pre_upgrade_<TIMESTAMP>/")

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
            (base / ".agent/skills/debug.md").write_text(SKILL_DEBUG)

        if not (base / ".agent/workflows/feature.md").exists():
            (base / ".agent/workflows/feature.md").write_text(WORKFLOW_FEATURE)

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
            backup_name = fpath.name
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
    warning("Review GEMINI.md and Makefile for tier-specific changes")


# --- UPDATE SCRIPTS ---

def rollback_workspace(path: str, backup_name: str | None = None, yes: bool = False):
    """Rollback workspace to a previous state from backup or snapshot.

    Args:
        path: Path to workspace
        backup_name: Specific backup/snapshot name (e.g., 'pre_upgrade_20260126_143022' or 'my_snapshot')
                    If None, uses most recent backup
        yes: If True, skip confirmation prompt

    Raises:
        RollbackError: If rollback operation fails
        ValidationError: If workspace or backup doesn't exist
    """
    base = Path(path).resolve()

    if not base.exists():
        raise ValidationError(f"Path does not exist: {path}")

    # Check for snapshots first (tar.gz format)
    snapshots_dir = base / SNAPSHOTS_DIR
    snapshot_file = None
    if backup_name and snapshots_dir.exists():
        snapshot_file = snapshots_dir / f"{backup_name}.tar.gz"
        if snapshot_file.exists():
            # Restore from tar.gz snapshot
            header(f"Restoring from snapshot: {backup_name}")

            if not yes:
                response = (
                    input(
                        f"\n{_c(Colors.BOLD)}Proceed with restore? [y/N]{_c(Colors.RESET)} "
                    )
                    .strip()
                    .lower()
                )
                if response != "y":
                    print("Restore cancelled.")
                    return

            try:
                import tarfile
                import tempfile

                # Extract to temp directory first
                with tempfile.TemporaryDirectory() as temp_dir:
                    with tarfile.open(snapshot_file, "r:gz") as tar:
                        # Python 3.12+ security: use filter to prevent path traversal
                        if sys.version_info >= (3, 12):
                            tar.extractall(temp_dir, filter="data")
                        else:
                            tar.extractall(temp_dir)

                    # Copy files from temp to workspace
                    temp_path = Path(temp_dir)
                    restored_count = 0
                    removed_count = 0

                    # Track files that are in the snapshot
                    snapshot_files = set()
                    for item in temp_path.rglob("*"):
                        if item.is_file():
                            rel_path = str(item.relative_to(temp_path))
                            snapshot_files.add(rel_path)
                            target = base / rel_path
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, target)
                            restored_count += 1

                    # Remove files not in snapshot (added after snapshot was taken)
                    # Skip protected directories
                    protected_prefixes = (".snapshots", ".gemini/backups", ".git")
                    for item in base.rglob("*"):
                        if item.is_file():
                            rel = str(item.relative_to(base))
                            if any(rel.startswith(p) for p in protected_prefixes):
                                continue
                            if rel not in snapshot_files:
                                item.unlink()
                                removed_count += 1

                    success(
                        f"Restored {restored_count} file(s), removed {removed_count} file(s) from snapshot {backup_name}"
                    )
                    return

            except (tarfile.TarError, OSError, PermissionError) as e:
                raise RollbackError(f"Failed to restore from snapshot: {e}") from e

    # Fall back to directory-based backups (.gemini/backups)
    backups_dir = base / ".gemini/backups"
    if not backups_dir.exists():
        # Check if we have any snapshots at all
        if snapshots_dir.exists():
            available_snapshots = list(snapshots_dir.glob("*.tar.gz"))
            if available_snapshots:
                snapshot_names = ", ".join([s.stem for s in available_snapshots[:5]])
                raise RollbackError(
                    f"No upgrade backups found, but snapshots exist: {snapshot_names}. "
                    f"Use --backup <name> to specify which snapshot to restore."
                )

        raise RollbackError(
            "No backups directory found (.gemini/backups/). Backups are created automatically during upgrades."
        )

    # Find available backups
    available_backups = sorted(
        [b for b in backups_dir.iterdir() if b.is_dir()], reverse=True
    )

    if not available_backups:
        raise RollbackError("No backups found in .gemini/backups/")

    # Select backup
    if backup_name:
        backup_dir = backups_dir / backup_name
        if not backup_dir.exists():
            available_names = ", ".join([b.name for b in available_backups[:5]])
            raise RollbackError(
                f"Backup not found: {backup_name}. Available backups: {available_names}"
            )
    else:
        # Use most recent
        backup_dir = available_backups[0]
        info(f"Using most recent backup: {backup_dir.name}")

    header(f"Rolling back from: {backup_dir.name}")

    # List files in backup
    backup_files = list(backup_dir.rglob("*"))
    backup_files = [f for f in backup_files if f.is_file()]

    if not backup_files:
        raise RollbackError("Backup directory is empty")

    print(
        f"\n{_c(Colors.YELLOW)}⚠️  Will restore {len(backup_files)} file(s):{_c(Colors.RESET)}"
    )
    for f in backup_files[:10]:  # Show first 10
        rel_path = f.relative_to(backup_dir)
        print(f"   📄 {rel_path}")
    if len(backup_files) > 10:
        print(f"   ... and {len(backup_files) - 10} more files")

    # Confirmation
    if not yes:
        response = (
            input(f"\n{_c(Colors.BOLD)}Proceed with rollback? [y/N]{_c(Colors.RESET)} ")
            .strip()
            .lower()
        )
        if response != "y":
            print("Rollback cancelled.")
            return

    # Perform rollback
    restored_count = 0
    for backup_file in backup_files:
        rel_path = backup_file.relative_to(backup_dir)
        target = base / rel_path

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_file, target)
            restored_count += 1
        except (PermissionError, IOError) as e:
            warning(f"Failed to restore {rel_path}: {e}")

    success(f"Rolled back {restored_count} file(s) from {backup_dir.name}")
    warning("Rollback complete - verify workspace with 'make audit' and 'make doctor'")


# --- EXPORT WORKSPACE AS TEMPLATE ---
# --- INTERNAL HELPER FUNCTIONS ---

def _build_workspace_directories(tier: str, pkg_name: str) -> List[str]:
    """Build list of directories to create."""
    dirs = get_all_directories(tier)
    if tier != "1":
        dirs.append(f"src/{pkg_name}")
    return sorted(list(set(dirs)))

def _build_workspace_files(
    tier: str,
    name: str,
    pkg_name: str,
    parent: str | None,
    python_version: str,
    template_files: dict | None,
    template_deps: list | None
) -> Dict[str, str]:
    """Build dictionary of {path: content} for all workspace files."""
    files = {}
    
    # Core
    files["GEMINI.md"] = get_gemini_md(tier, pkg_name)
    files["Makefile"] = get_makefile(tier, pkg_name)
    files["README.md"] = f"# {name}\n\nGenerated Gemini Workspace ({TIERS[tier]['name']})\n"
    files[".gitignore"] = "\n".join(GITIGNORE_PATTERNS)
    
    # Configuration
    files[".gemini/workspace.json"] = json.dumps({
        "version": VERSION,
        "tier": tier,
        "name": name,
        "created": datetime.now(timezone.utc).astimezone().isoformat(),
        "standard": "Gemini Native Workspace Standard",
        "parent_workspace": parent
    }, indent=2)
    
    # Scripts
    files["scripts/audit.py"] = get_audit_script()
    files["scripts/session.py"] = get_session_script()
    files["scripts/doc_indexer.py"] = get_doc_indexer_script()
    files["scripts/status.py"] = get_status_script()
    files["scripts/list_skills.py"] = get_list_skills_script()
    
    # Documentation
    files["docs/roadmap.md"] = f"# Roadmap: {name}\n\n- [ ] Initial Setup"
    
    # CI/CD
    files[".github/workflows/ci.yml"] = get_github_workflow(tier, python_version)
    
    # Python files for Tier 2+
    if tier != "1":
        files["pyproject.toml"] = f'[project]\nname = "{pkg_name}"\nversion = "0.1.0"\nrequires-python = ">={python_version}"\ndependencies = []'
        files[f"src/{pkg_name}/__init__.py"] = ""
        files[f"src/{pkg_name}/main.py"] = """def main():
    print("Hello World")

if __name__ == "__main__":
    main()
"""
        
        # Tests
        if tier == "2":
            files[f"tests/unit/test_{pkg_name}.py"] = get_standard_unit_test_example(pkg_name)
            files[f"tests/integration/test_integration.py"] = get_standard_integration_test_example(pkg_name)
        elif tier == "3":
            files[f"tests/unit/test_{pkg_name}.py"] = get_standard_unit_test_example(pkg_name)
            files[f"tests/integration/test_integration.py"] = get_standard_integration_test_example(pkg_name)
            files[f"tests/evals/test_evals.py"] = get_enterprise_eval_test_example(pkg_name)
    else:
        files["src/main.py"] = 'print("Hello World")'
        files["requirements.txt"] = "\n".join(DEFAULT_REQUIREMENTS["1"])
        
    return files

def _write_file_safe(base: Path, path_str: str, content: str):
    """Write file safely with error handling (for thread pool)."""
    target = base / path_str
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if path_str in EXECUTABLE_FILES:
            target.chmod(0o755)
        return path_str, None
    except Exception as e:
        return path_str, str(e)

def show_dry_run_summary(tier, name, template_name, cwd):
    header(f"Dry Run: Creating {name}")
    print(f"Tier: {tier} ({TIERS[tier]['name']})")
    print(f"Path: {cwd}/{name}")

def log_bootstrap_event(*args, **kwargs):
    pass # Telemetry placeholder

def get_shift_report_script():
    return "# Shift Report\n"

def get_vscode_settings():
    return "{}"

def get_settings(tier):
    return "{}"

