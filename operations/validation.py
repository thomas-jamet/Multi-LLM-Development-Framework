"""Workspace validation operations.

Validates existing workspaces against the Multi-LLM Development Framework standard.
"""

import json
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

try:
    from core_utils import (
        success,
        error,
        info,
        header,
        ValidationError,
        ConfigurationError,
        _get_file_cache_key,
    )
except ImportError:
    # During build, imports are flat
    from ..core_utils import (
        success,
        error,
        info,
        header,
        ValidationError,
        _get_file_cache_key,
    )


@lru_cache(maxsize=128)
def _validate_workspace_impl(base_path: str, cache_key: str) -> tuple[dict, list]:
    """Internal implementation for workspace validation (cached).

    Args:
        base_path: Path to workspace
        cache_key: Cache invalidation key (based on workspace.json mtime)

    Returns:
        Tuple of (workspace_dict, issues_list)
    """
    base = Path(base_path)
    issues = []

    ws_file = base / ".gemini/workspace.json"
    if not ws_file.exists():
        return {}, ["Missing .gemini/workspace.json"]

    try:
        with open(ws_file) as f:
            ws = json.load(f)
    except json.JSONDecodeError as e:
        return {}, [f"Invalid workspace.json: {e}"]
    except PermissionError:
        return {}, ["Cannot read workspace.json (permission denied)"]

    # Basic validation checks
    if "tier" not in ws:
        issues.append("Missing 'tier' in workspace.json")
    if "version" not in ws:
        issues.append("Missing 'version' in workspace.json")

    return ws, issues


@lru_cache(maxsize=128)
def validate_workspace(path: str) -> None:
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
