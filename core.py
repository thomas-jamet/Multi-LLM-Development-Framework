#!/usr/bin/env python3
"""
Core Bootstrap Module

Defines exceptions, utilities, validators, and helper functions.
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict
from functools import lru_cache


# Version constant
VERSION = "2026.26"
DEFAULT_PYTHON_VERSION = "3.11"
VALID_PYTHON_VERSION_PATTERN = re.compile(r"^3\.\d+$")

# Global flag for color output
USE_COLOR: bool = os.environ.get("NO_COLOR") is None


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def _c(code: str) -> str:
    """Return color code if colors are enabled, empty string otherwise."""
    return code if USE_COLOR else ""


def show_progress(step: int, total: int, message: str) -> None:
    """Display progress indicator for long-running operations."""
    bar_length = 30
    filled = int(bar_length * step / total)
    bar = "█" * filled + "░" * (bar_length - filled)
    percent = int(100 * step / total)
    print(
        f"\r{_c(Colors.CYAN)}[{bar}] {percent}% {_c(Colors.RESET)} {message}",
        end="",
        flush=True,
    )
    if step == total:
        print()  # New line when complete


def success(msg: str) -> None:
    print(f"{_c(Colors.GREEN)}✅ {msg}{_c(Colors.RESET)}")


def error(msg: str) -> None:
    print(f"{_c(Colors.RED)}❌ {msg}{_c(Colors.RESET)}")


def warning(msg: str) -> None:
    print(f"{_c(Colors.YELLOW)}⚠️  {msg}{_c(Colors.RESET)}")


def info(msg: str) -> None:
    print(f"{_c(Colors.BLUE)}ℹ️  {msg}{_c(Colors.RESET)}")


def header(msg: str) -> None:
    print(f"\n{_c(Colors.BOLD)}{msg}{_c(Colors.RESET)}")


def dim(msg: str) -> None:
    print(f"{_c(Colors.DIM)}{msg}{_c(Colors.RESET)}")


# --- STRUCTURED LOGGING & TELEMETRY ---

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



def validate_project_name(name: str) -> None:
    """Validate project name.

    Args:
        name: Project name to validate

    Raises:
        ValidationError: If project name is invalid
    """
    if not name:
        raise ValidationError("Project name cannot be empty")
    if len(name) > 50:
        raise ValidationError("Project name must be 50 characters or less")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name):
        raise ValidationError(
            "Project name must start with a letter and contain only letters, numbers, underscores, and hyphens"
        )
    # Path traversal protection
    if ".." in name or "/" in name or "\\" in name:
        raise ValidationError(
            "Project name cannot contain path separators or parent directory references"
        )
    reserved = {"test", "tests", "src", "lib", "bin", "build", "dist"}
    if name.lower() in reserved:
        raise ValidationError(f"'{name}' is a reserved name, please choose another")


def validate_python_version(version: str) -> None:
    """Validate Python version string format.

    Args:
        version: Expected format like '3.10', '3.11', '3.12'

    Raises:
        ValidationError: If Python version format is invalid
    """
    if not version:
        raise ValidationError("Python version cannot be empty")
    if not VALID_PYTHON_VERSION_PATTERN.match(version):
        raise ValidationError(
            f"Invalid Python version '{version}'. Expected format: 3.10, 3.11, 3.12, etc."
        )


def validate_tier_upgrade(current_tier: str, target_tier: str) -> None:
    """Validate tier upgrade path prevents downgrades.

    Args:
        current_tier: Current workspace tier (1, 2, or 3)
        target_tier: Target tier for upgrade

    Raises:
        ValidationError: If upgrade path is invalid
    """
    try:
        current = int(current_tier)
        target = int(target_tier)

        if target < current:
            raise ValidationError(
                f"Cannot downgrade from Tier {current_tier} ({TIERS[current_tier]['name']}) to Tier {target_tier} ({TIERS[target_tier]['name']})"
            )

        if target == current:
            raise ValidationError(
                f"Workspace is already at Tier {current_tier} ({TIERS[current_tier]['name']})"
            )

        # Validate tier exists
        if target_tier not in TIERS:
            raise ValidationError(
                f"Invalid target tier '{target_tier}'. Must be 1, 2, or 3"
            )

    except (ValueError, KeyError):
        raise ValidationError(
            f"Invalid tier values: current='{current_tier}', target='{target_tier}'"
        )


def validate_template_name(name: str) -> None:
    """Validate template name exists in TEMPLATES.

    Args:
        name: Template name to validate

    Raises:
        ValidationError: If template name is unknown
    """
    if not name:
        raise ValidationError("Template name cannot be empty")

    if name not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES.keys()))
        raise ValidationError(
            f"Unknown template '{name}'. Available templates: {available}"
        )


def validate_manifest_path(path: str) -> None:
    """Prevent path traversal in context manifests.

    Args:
        path: File path from manifest

    Raises:
        ValidationError: If path contains security vulnerabilities

    Security:
        Prevents loading files outside workspace via path traversal.
    """
    if not path:
        raise ValidationError("Manifest path cannot be empty")

    # Reject absolute paths
    if path.startswith("/") or (
        len(path) > 1 and path[1] == ":"
    ):  # Unix or Windows absolute
        raise ValidationError(f"Manifest paths must be relative, not absolute: {path}")

    # Reject UNC paths (Windows network paths)
    if path.startswith("\\\\"):
        raise ValidationError(f"UNC paths not allowed in manifest: {path}")

    # Reject parent directory references
    if ".." in path.split("/"):
        raise ValidationError(f"Path traversal detected in manifest: {path}")

    # Check for null bytes (security)
    if "\0" in path:
        raise ValidationError(f"Null byte detected in manifest path: {path}")


def validate_rollback_backup(backup_name: str, workspace_path: Path) -> None:
    """Validate backup exists before attempting rollback.

    Args:
        backup_name: Name of backup/snapshot to restore
        workspace_path: Path to workspace

    Raises:
        ValidationError: If backup doesn't exist or is invalid
    """
    if not backup_name:
        raise ValidationError("Backup name cannot be empty")

    backup_dir = workspace_path / SNAPSHOTS_DIR / backup_name

    if not backup_dir.exists():
        # List available backups
        snapshots_path = workspace_path / SNAPSHOTS_DIR
        if snapshots_path.exists():
            available = [d.name for d in snapshots_path.iterdir() if d.is_dir()]
            if available:
                available_str = ", ".join(sorted(available))
                raise ValidationError(
                    f"Backup '{backup_name}' not found. Available: {available_str}"
                )
        raise ValidationError(f"Backup '{backup_name}' not found. No backups exist.")

    if not backup_dir.is_dir():
        raise ValidationError(
            f"Backup path exists but is not a directory: {backup_dir}"
        )

def load_config(config_path: Path | None = None) -> dict:
    """Load config from .gemini-bootstrap.json if it exists.

    Args:
        config_path: Optional explicit path; defaults to cwd/.gemini-bootstrap.json

    Returns:
        Configuration dictionary or empty dict if not found/invalid

    Security:
        Path traversal validation prevents loading config from outside cwd.
    """
    path = config_path or Path.cwd() / ".gemini-bootstrap.json"

    # Security: Validate path doesn't traverse outside expected locations
    try:
        resolved_path = path.resolve()
        cwd_resolved = Path.cwd().resolve()
        # Allow paths within cwd or explicit absolute paths that exist
        if config_path is None and not str(resolved_path).startswith(str(cwd_resolved)):
            warning("Config path traversal detected, ignoring")
            return {}
    except (OSError, ValueError):
        warning("Invalid config path, ignoring")
        return {}

    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            warning("Invalid .gemini-bootstrap.json (malformed JSON), ignoring")
        except PermissionError:
            warning("Cannot read .gemini-bootstrap.json (permission denied), ignoring")
        except Exception as e:
            warning(f"Unexpected error reading .gemini-bootstrap.json: {e}")
    return {}

def _get_file_cache_key(path: Path) -> str:
    """Generate cache key based on file modification time for cache invalidation.

    Args:
        path: File or directory path to generate cache key for

    Returns:
        Cache key string combining path and mtime, or path:missing if not exists

    Used by @lru_cache decorated functions to automatically invalidate cache
    when the underlying file changes.
    """
    if not path.exists():
        return f"{path}:missing"

    try:
        if path.is_file():
            mtime = path.stat().st_mtime
            return f"{path}:{mtime}"
        else:
            # For directories, hash all file mtimes for comprehensive invalidation
            mtimes = []
            for file in path.rglob("*"):
                if file.is_file():
                    try:
                        mtimes.append(
                            f"{file.relative_to(path)}:{file.stat().st_mtime}"
                        )
                    except (OSError, ValueError):
                        # Skip files we can't stat
                        continue
            if mtimes:
                return (
                    f"{path}:"
                    + hashlib.sha256("".join(sorted(mtimes)).encode()).hexdigest()
                )
            else:
                return f"{path}:empty"
    except (OSError, PermissionError):
        # If we can't access the file, use a timestamp-based key
        return f"{path}:error:{datetime.now(timezone.utc).timestamp()}"



# --- CUSTOM EXCEPTION HIERARCHY ---


class WorkspaceError(Exception):
    """Base exception for all workspace-related errors.

    All workspace operations should raise subclasses of this exception instead
       of using sys.exit(), allowing for proper exception handling and testing.
    """

    pass


class ValidationError(WorkspaceError):
    """Raised when validation fails (project name, tier, template, paths, etc.).

    Examples:
        - Invalid project name format
        - Invalid tier upgrade path (downgrade attempt)
        - Invalid Python version string
        - Path traversal detected in manifest
    """

    pass


class CreationError(WorkspaceError):
    """Raised when workspace creation fails.

    Examples:
        - Directory already exists
        - Insufficient permissions
        - Disk space issues
        - Template application errors
    """

    pass


class UpgradeError(WorkspaceError):
    """Raised when workspace upgrade fails.

    Examples:
        - Invalid upgrade path (downgrade attempt)
        - Missing workspace.json
        - Backup creation fails
        - File conflicts during upgrade
    """

    pass


class RollbackError(WorkspaceError):
    """Raised when rollback/restore operation fails.

    Examples:
        - Backup/snapshot not found
        - Restore operation fails
        - Invalid backup structure
    """

    pass


class ConfigurationError(WorkspaceError):
    """Raised when configuration is invalid or missing.

    Examples:
        - Malformed workspace.json
        - Missing required fields
        - Invalid settings  - Schema validation failures
    """

    pass
