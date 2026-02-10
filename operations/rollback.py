"""Workspace rollback operations.

Handles restoring workspaces from backups or snapshots.
"""

import shutil
import sys
import tarfile
import tempfile
from pathlib import Path

try:
    from config import SNAPSHOTS_DIR
    from core_utils import (
        success,
        warning,
        info,
        header,
        _c,
        Colors,
        ValidationError,
        RollbackError,
    )
except ImportError:
    # During build, imports are flat
    from ..config import SNAPSHOTS_DIR
    from ..core_utils import (
        success,
        warning,
        info,
        header,
        _c,
        Colors,
        ValidationError,
        RollbackError,
    )


def _safe_tar_extract(tar: tarfile.TarFile, path: str) -> None:
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


def rollback_workspace(
    path: str, backup_name: str | None = None, yes: bool = False
) -> None:
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
                # Extract to temp directory first
                with tempfile.TemporaryDirectory() as temp_dir:
                    with tarfile.open(snapshot_file, "r:gz") as tar:
                        # Python 3.12+ security: use filter to prevent path traversal
                        if sys.version_info >= (3, 12):
                            tar.extractall(temp_dir, filter="data")
                        else:
                            # Python 3.11: manual validation
                            _safe_tar_extract(tar, temp_dir)

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
