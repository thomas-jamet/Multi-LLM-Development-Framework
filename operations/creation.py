"""Workspace creation operations.

Handles creation of new workspaces with tier-specific configurations.
"""

import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from config import (
        TIERS,
        TEMPLATES,
        DEFAULT_PYTHON_VERSION,
        DEFAULT_PROVIDER,
    )
    from core_utils import (
        validate_project_name,
        success,
        error,
        warning,
        info,
        header,
        dim,
        CreationError,
    )
    from operations.utils import (
        _build_workspace_directories,
        _build_workspace_files,
        _write_file_safe,
        show_dry_run_summary,
        log_bootstrap_event,
    )
    from operations.enterprise import get_enterprise_domain
except ImportError:
    # During build, imports are flat
    from ..config import (
        TIERS,
        TEMPLATES,
        DEFAULT_PYTHON_VERSION,
        DEFAULT_PROVIDER,
    )
    from ..core_utils import (
        validate_project_name,
        success,
        error,
        warning,
        info,
        header,
        dim,
        CreationError,
    )
    from .utils import (
        _build_workspace_directories,
        _build_workspace_files,
        _write_file_safe,
        show_dry_run_summary,
        log_bootstrap_event,
    )
    from .enterprise import get_enterprise_domain


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
    provider: str = DEFAULT_PROVIDER,
) -> None:
    """Create a new workspace with specified configuration.

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
        provider: LLM provider name ('gemini', 'claude', 'codex')

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
            "Use --force to overwrite, or manually add workspace files to the existing project"
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
            test_path = target_dir / f".{provider}_preflight_{name}"
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

    # Get domain for enterprise tier
    domain = "core"  # default
    if tier == "3":
        domain = get_enterprise_domain(name, template_files)

    # Use helper functions to build structure
    dirs = _build_workspace_directories(tier, pkg_name, provider, domain)
    files = _build_workspace_files(
        tier,
        name,
        pkg_name,
        parent,
        python_version,
        template_files,
        template_deps,
        provider,
        domain,
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
