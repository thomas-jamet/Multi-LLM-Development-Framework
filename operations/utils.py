"""Utility functions for workspace operations.

Shared helper functions used by creation, upgrade, and rollback operations.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

try:
    from config import (
        TIERS,
        VERSION,
        SCRIPT_CATEGORIES,
        EXECUTABLE_FILES,
        DEFAULT_REQUIREMENTS,
        get_all_directories,
        get_gitignore_for_tier,
    )
    from core_utils import header
    from core.makefile import get_makefile
    from core.templates import (
        get_github_workflow,
        get_run_audit_script,
        get_manage_session_script,
        get_index_docs_script,
        get_check_status_script,
        get_list_skills_script,
        get_create_snapshot_script,
        get_skillsmp_client_script,
        get_skillsmp_search_script,
        get_skill_discovery_workflow,
    )
    from content_generators import (
        get_standard_unit_test_example,
        get_standard_integration_test_example,
        get_enterprise_eval_test_example,
    )
except ImportError:
    # During build, imports are flat
    from ..config import (
        TIERS,
        VERSION,
        SCRIPT_CATEGORIES,
        EXECUTABLE_FILES,
        DEFAULT_REQUIREMENTS,
        get_all_directories,
        get_gitignore_for_tier,
    )
    from ..core import header
    from ..core.makefile import get_makefile
    from ..core.templates import (
        get_github_workflow,
        get_run_audit_script,
        get_manage_session_script,
        get_index_docs_script,
        get_check_status_script,
        get_list_skills_script,
        get_create_snapshot_script,
        get_skillsmp_client_script,
        get_skillsmp_search_script,
        get_skill_discovery_workflow,
    )
    from ..content_generators import (
        get_standard_unit_test_example,
        get_standard_integration_test_example,
        get_enterprise_eval_test_example,
    )


def _get_script_path(tier: str, script_name: str) -> str:
    """Get tier-specific path for a script.

    Args:
        tier: Workspace tier ("1", "2", or "3")
        script_name: Script name without extension (e.g., "run_audit")

    Returns:
        Full path relative to workspace root (e.g., "scripts/workspace/run_audit.py")
    """
    if tier == "1":  # Lite: flat structure
        return f"scripts/{script_name}.py"
    elif tier == "2":  # Standard: categorized
        # Find which category this script belongs to
        for category, scripts in SCRIPT_CATEGORIES["2"].items():
            if script_name in scripts:
                return f"scripts/{category}/{script_name}.py"
        # Fallback
        return f"scripts/{script_name}.py"
    else:  # Enterprise: domain-based
        # Default to shared for standard scripts
        for category, scripts in SCRIPT_CATEGORIES["3"].items():
            if script_name in scripts:
                return f"scripts/{category}/{script_name}.py"
        # Fallback
        return f"scripts/shared/{script_name}.py"


def _build_workspace_directories(
    tier: str, pkg_name: str, provider: str = "gemini", domain: str = "core"
) -> List[str]:
    """Build list of directories to create.

    Args:
        tier: Workspace tier ("1", "2", or "3")
        pkg_name: Package name (for src directory)
        provider: LLM provider name
        domain: Enterprise domain name (used for tier 3)

    Returns:
        Sorted list of directory paths to create
    """
    # Import provider to get config_dirname
    from providers import get_provider

    provider_obj = get_provider(provider)

    dirs = get_all_directories(tier).copy()

    # Add provider config directory
    dirs.append(provider_obj.config_dirname.lstrip("."))

    # Add script category directories based on tier
    if tier == "2":  # Standard: categorized structure
        for category in SCRIPT_CATEGORIES["2"].keys():
            if category:  # Skip empty key (flat dirs)
                dirs.append(f"scripts/{category}")
    elif tier == "3":  # Enterprise: domain-based structure
        for category in SCRIPT_CATEGORIES["3"].keys():
            if category:  # Skip empty key
                dirs.append(f"scripts/{category}")

    # Add data directories based on tier (Tiered Data Pattern)
    if tier in ["1", "2"]:  # Lite/Standard: flat data structure
        dirs.extend(["data/inputs", "data/outputs"])
    else:  # Enterprise: domain-based data structure
        dirs.extend([f"data/{domain}/inputs", f"data/{domain}/outputs", "data/shared"])

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
    template_deps: list | None,
    provider: str = "gemini",
    domain: str = "core",
) -> Dict[str, str]:
    """Build dictionary of {path: content} for all workspace files.

    Args:
        tier: Workspace tier
        name: Workspace name
        pkg_name: Package name
        parent: Parent workspace path (for monorepos)
        python_version: Python version for CI
        template_files: Optional template file overrides
        template_deps: Optional template dependencies
        provider: LLM provider
        domain: Enterprise domain name

    Returns:
        Dictionary mapping file paths to their contents
    """
    from providers import get_provider

    provider_obj = get_provider(provider)

    files = {}

    # Core - use provider-specific config filename
    files[provider_obj.config_filename] = provider_obj.get_config_template(
        tier, pkg_name
    )
    files["Makefile"] = get_makefile(tier, pkg_name, provider)
    files["README.md"] = (
        f"# {name}\n\nGenerated {provider_obj.name.title()} Workspace ({TIERS[tier]['name']})\n"
    )
    files[".gitignore"] = "\n".join(get_gitignore_for_tier(tier))

    # Provider-specific configuration directory
    config_dir = provider_obj.config_dirname
    files[f"{config_dir}/workspace.json"] = json.dumps(
        {
            "version": VERSION,
            "tier": tier,
            "name": name,
            "provider": provider,
            "created": datetime.now(timezone.utc).astimezone().isoformat(),
            "standard": "Multi-LLM Development Framework",
            "parent_workspace": parent,
        },
        indent=2,
    )

    # Scripts - use tier-specific paths
    files[_get_script_path(tier, "run_audit")] = get_run_audit_script()
    files[_get_script_path(tier, "manage_session")] = get_manage_session_script()
    files[_get_script_path(tier, "index_docs")] = get_index_docs_script()
    files[_get_script_path(tier, "check_status")] = get_check_status_script()
    files[_get_script_path(tier, "list_skills")] = get_list_skills_script()

    # Snapshot script for Standard and Enterprise tiers
    if tier in ["2", "3"]:
        files[_get_script_path(tier, "create_snapshot")] = get_create_snapshot_script()

    # SkillsMP Discovery (Standard & Enterprise only)
    if tier != "1":
        # Add SkillsMP client and search script to scripts/shared/
        files["scripts/shared/skillsmp_client.py"] = get_skillsmp_client_script()
        files["scripts/shared/skillsmp_search.py"] = get_skillsmp_search_script()
        files[".agent/workflows/shared/discover_skills.md"] = (
            get_skill_discovery_workflow()
        )

    # Documentation
    files["docs/roadmap.md"] = f"# Roadmap: {name}\n\n- [ ] Initial Setup"

    # CI/CD
    files[".github/workflows/ci.yml"] = get_github_workflow(tier, python_version)

    # Python files for Tier 2+
    if tier != "1":
        files["pyproject.toml"] = (
            f'[project]\nname = "{pkg_name}"\nversion = "0.1.0"\nrequires-python = ">={python_version}"\ndependencies = []'
        )
        files[f"src/{pkg_name}/__init__.py"] = ""
        files[f"src/{pkg_name}/main.py"] = """def main():
    print("Hello World")

if __name__ == "__main__":
    main()
"""

        # Tests
        if tier == "2":
            files[f"tests/unit/test_{pkg_name}.py"] = get_standard_unit_test_example(
                pkg_name
            )
            files["tests/integration/test_integration.py"] = (
                get_standard_integration_test_example(pkg_name)
            )
        elif tier == "3":
            files[f"tests/unit/test_{pkg_name}.py"] = get_standard_unit_test_example(
                pkg_name
            )
            files["tests/integration/test_integration.py"] = (
                get_standard_integration_test_example(pkg_name)
            )
            files["tests/evals/test_evals.py"] = get_enterprise_eval_test_example(
                pkg_name
            )
    else:
        files["src/main.py"] = 'print("Hello World")'
        files["requirements.txt"] = "\n".join(DEFAULT_REQUIREMENTS["1"])

    # Add .gitkeep files for hygiene and data directories
    files["logs/.gitkeep"] = ""
    files["scratchpad/.gitkeep"] = ""

    # Add .gitkeep for data directories based on tier
    if tier in ["1", "2"]:  # Lite/Standard: flat data structure
        files["data/inputs/.gitkeep"] = ""
    else:  # Enterprise: domain-based data structure
        files[f"data/{domain}/inputs/.gitkeep"] = ""
        files["data/shared/.gitkeep"] = ""

    return files


def _write_file_safe(base: Path, path_str: str, content: str):
    """Write file safely with error handling (for thread pool).

    Args:
        base: Base directory path
        path_str: Relative file path
        content: File content

    Returns:
        Tuple of (path_str, error_message or None)
    """
    target = base / path_str
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if path_str in EXECUTABLE_FILES:
            target.chmod(0o755)
        return path_str, None
    except Exception as e:
        return path_str, str(e)


def _safe_tar_extract(tar, path):
    """Safely extract tar archive with path traversal protection.

    Args:
        tar: TarFile object
        path: Destination path

    Raises:
        ValueError: If archive contains unsafe paths
    """
    dest_path = Path(path).resolve()

    for member in tar.getmembers():
        # Resolve member path
        member_path = (dest_path / member.name).resolve()

        # Ensure member path is within destination
        if not str(member_path).startswith(str(dest_path)):
            raise ValueError(
                f"Unsafe tar member: {member.name} (path traversal attempt)"
            )

    # Extract after validation
    tar.extractall(path)  # nosec B202 - validated above


def show_dry_run_summary(tier: str, name: str, template_name: str | None, cwd: str):
    """Show dry run summary.

    Args:
        tier: Workspace tier
        name: Workspace name
        template_name: Template name (if used)
        cwd: Current working directory
    """
    header(f"Dry Run: Creating {name}")
    print(f"Tier: {tier} ({TIERS[tier]['name']})")
    print(f"Path: {cwd}/{name}")


def log_bootstrap_event(*args, **kwargs):
    """Telemetry placeholder (not implemented)."""
    pass


def get_shift_report_script():
    """Get shift report script content (placeholder).

    Returns:
        Script content string
    """
    return "# Shift Report\n"


def get_vscode_settings():
    """Get VSCode settings content (placeholder).

    Returns:
        JSON settings string
    """
    return "{}"


def get_settings(tier: str):
    """Get workspace settings content (placeholder).

    Args:
        tier: Workspace tier

    Returns:
        JSON settings string
    """
    return "{}"
