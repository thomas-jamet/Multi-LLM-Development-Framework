"""Output formatting for workspace operations.

Provides structured data classes and formatters for both JSON and
human-readable output formats.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any
import json


try:
    from core_utils import success, info, warning, error, dim
except ImportError:
    from ..core_utils import success, info, error, dim


@dataclass
class WorkspaceInfo:
    """Information about a workspace."""

    name: str
    path: str
    tier: str
    tier_name: str
    template: Optional[str]
    git_initialized: bool
    provider: str
    python_version: str


@dataclass
class CreationResult:
    """Result of workspace creation operation."""

    success: bool
    workspace: WorkspaceInfo
    stats: Dict[str, Any]
    next_steps: List[str]
    timestamp: str
    dry_run: bool = False
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of workspace validation operation."""

    valid: bool
    path: str
    issues: List[str]
    timestamp: str
    tier: Optional[str] = None
    tier_name: Optional[str] = None


@dataclass
class UpgradeResult:
    """Result of workspace upgrade operation."""

    success: bool
    path: str
    from_tier: str
    to_tier: str
    changes: List[str]
    timestamp: str
    backup_created: bool = False
    error_message: Optional[str] = None


@dataclass
class RollbackResult:
    """Result of workspace rollback operation."""

    success: bool
    path: str
    snapshot_id: str
    restored_tier: Optional[str]
    timestamp: str
    error_message: Optional[str] = None


class OutputFormatter:
    """Format operation results as JSON or human-readable text."""

    def __init__(self, json_mode: bool = False):
        """Initialize formatter.

        Args:
            json_mode: If True, output JSON; otherwise output human-readable text
        """
        self.json_mode = json_mode

    def format_creation(self, result: CreationResult) -> str:
        """Format workspace creation result.

        Args:
            result: Creation result data

        Returns:
            Formatted output string
        """
        if self.json_mode:
            return json.dumps(asdict(result), indent=2)
        else:
            return self._format_creation_human(result)

    def _format_creation_human(self, result: CreationResult) -> str:
        """Format creation result as human-readable text.

        Args:
            result: Creation result data

        Returns:
            Human-readable formatted string
        """
        lines = []

        if result.dry_run:
            lines.append(info(" [DRY RUN MODE - No files created]"))
            lines.append("")

        if result.success:
            workspace = result.workspace
            lines.append(success(f"Created '{workspace.name}' ({workspace.tier_name})"))
            lines.append("")
            lines.append(dim(f"  📁 Location: {workspace.path}"))
            lines.append(dim(f"  🔧 Provider: {workspace.provider}"))
            lines.append(dim(f"  🐍 Python: {workspace.python_version}"))

            if workspace.git_initialized:
                lines.append(dim("  📦 Git: initialized"))

            if workspace.template:
                lines.append(dim(f"  📋 Template: {workspace.template}"))

            stats = result.stats
            if "files_created" in stats:
                lines.append(dim(f"  📝 Files: {stats['files_created']} created"))
            if "dirs_created" in stats:
                lines.append(dim(f"  📂 Directories: {stats['dirs_created']} created"))
            if "duration_seconds" in stats:
                lines.append(dim(f"  ⏱️  Duration: {stats['duration_seconds']:.2f}s"))

            lines.append("")
            lines.append("Next steps:")
            for step in result.next_steps:
                lines.append(f"  👉 {step}")
        else:
            lines.append(error(f"Failed to create workspace: {result.error_message}"))

        return "\n".join(lines)

    def format_validation(self, result: ValidationResult) -> str:
        """Format workspace validation result.

        Args:
            result: Validation result data

        Returns:
            Formatted output string
        """
        if self.json_mode:
            return json.dumps(asdict(result), indent=2)
        else:
            return self._format_validation_human(result)

    def _format_validation_human(self, result: ValidationResult) -> str:
        """Format validation result as human-readable text.

        Args:
            result: Validation result data

        Returns:
            Human-readable formatted string
        """
        lines = []

        if result.valid:
            lines.append(success(f"Workspace '{result.path}' is valid"))
            if result.tier and result.tier_name:
                lines.append(dim(f"  Tier: {result.tier_name}"))
        else:
            lines.append(error(f"Workspace '{result.path}' has issues:"))
            for issue in result.issues:
                lines.append(f"  ❌ {issue}")

        return "\n".join(lines)

    def format_upgrade(self, result: UpgradeResult) -> str:
        """Format workspace upgrade result.

        Args:
            result: Upgrade result data

        Returns:
            Formatted output string
        """
        if self.json_mode:
            return json.dumps(asdict(result), indent=2)
        else:
            return self._format_upgrade_human(result)

    def _format_upgrade_human(self, result: UpgradeResult) -> str:
        """Format upgrade result as human-readable text.

        Args:
            result: Upgrade result data

        Returns:
            Human-readable formatted string
        """
        lines = []

        if result.success:
            lines.append(
                success(
                    f"Upgraded workspace from Tier {result.from_tier} → {result.to_tier}"
                )
            )
            lines.append(dim(f"  📁 Path: {result.path}"))

            if result.backup_created:
                lines.append(dim("  💾 Backup: created"))

            if result.changes:
                lines.append("")
                lines.append("Changes:")
                for change in result.changes:
                    lines.append(f"  • {change}")
        else:
            lines.append(error(f"Upgrade failed: {result.error_message}"))

        return "\n".join(lines)

    def format_rollback(self, result: RollbackResult) -> str:
        """Format workspace rollback result.

        Args:
            result: Rollback result data

        Returns:
            Formatted output string
        """
        if self.json_mode:
            return json.dumps(asdict(result), indent=2)
        else:
            return self._format_rollback_human(result)

    def _format_rollback_human(self, result: RollbackResult) -> str:
        """Format rollback result as human-readable text.

        Args:
            result: Rollback result data

        Returns:
            Human-readable formatted string
        """
        lines = []

        if result.success:
            lines.append(
                success(f"Rolled back workspace to snapshot {result.snapshot_id}")
            )
            lines.append(dim(f"  📁 Path: {result.path}"))
            if result.restored_tier:
                lines.append(dim(f"  📊 Tier: {result.restored_tier}"))
        else:
            lines.append(error(f"Rollback failed: {result.error_message}"))

        return "\n".join(lines)
