#!/usr/bin/env python3
"""Snapshot Script Generator

Generates workspace snapshot creation and restore script.
"""
def get_create_snapshot_script() -> str:
    """Generate snapshot creation/restore script (create_snapshot.py)."""
    return (
        '''#!/usr/bin/env python3
"""Create and restore workspace snapshots using git tags and directory backups."""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_DIR = Path(".snapshots")

def get_git_available():
    """Check if git is available and repo is initialized."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def list_snapshots():
    """List all available snapshots."""
    snapshots = []
    
    # Check git tags
    if get_git_available():
        try:
            result = subprocess.run(
                ["git", "tag", "-l", "snapshot-*"],
                capture_output=True, text=True, check=True
            )
            tags = [line.strip() for line in result.stdout.split("\\\\n") if line.strip()]
            snapshots.extend([(tag, "git") for tag in tags])
        except subprocess.CalledProcessError:
            pass
    
    # Check directory backups
    if SNAPSHOT_DIR.exists():
        for backup in SNAPSHOT_DIR.iterdir():
            if backup.is_dir():
                snapshots.append((backup.name, "backup"))
    
    return snapshots

def create_snapshot(name: str):
    """Create a workspace snapshot."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snapshot_name = f"snapshot-{name}-{timestamp}" if name else f"snapshot-{timestamp}"
    
    print(f"📸 Creating snapshot: {snapshot_name}")
    
    # Create git tag if available
    if get_git_available():
        try:
            subprocess.run(
                ["git", "tag", "-a", snapshot_name, "-m", f"Snapshot: {name or 'unnamed'}"],
                check=True
            )
            print(f"✅ Git tag created: {snapshot_name}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git tag creation failed: {e}")
    
    # Create directory backup
    backup_path = SNAPSHOT_DIR / snapshot_name
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Backup critical files and directories
    critical_items = [
        ".gemini/workspace.json",
        ".gemini/settings.json", 
        "GEMINI.md",
        "Makefile",
        "pyproject.toml",
        "src/",
        ".agent/"
    ]
    
    for item in critical_items:
        src = Path(item)
        if not src.exists():
            continue
        
        dest = backup_path / item
        try:
            if src.is_dir():
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        except Exception as e:
            print(f"⚠️  Failed to backup {item}: {e}")
    
    # Save snapshot metadata
    metadata = {
        "name": name or "unnamed",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_tag": snapshot_name if get_git_available() else None
    }
    
    with open(backup_path / "snapshot.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Backup created: {backup_path}")
    print(f"\\\\n💡 Restore with: make restore name=\\"{snapshot_name}\\"")

def restore_snapshot(name: str):
    """Restore workspace from a snapshot."""
    # Find snapshot
    snapshots = list_snapshots()
    matching = [s for s in snapshots if name in s[0]]
    
    if not matching:
        print(f"❌ Snapshot '{name}' not found")
        print("\\\\nAvailable snapshots:")
        for snap_name, snap_type in snapshots:
            print(f"  • {snap_name} ({snap_type})")
        sys.exit(1)
    
    snapshot_name = matching[0][0]
    print(f"🔄 Restoring snapshot: {snapshot_name}")
    
    # Confirm
    confirm = input("⚠️  This will overwrite current files. Continue? [y/N]: ").strip().lower()
    if confirm != "y":
        print("❌ Restore cancelled")
        sys.exit(0)
    
    # Restore from directory backup
    backup_path = SNAPSHOT_DIR / snapshot_name
    if not backup_path.exists():
        print(f"❌ Backup directory not found: {backup_path}")
        sys.exit(1)
    
    # Restore files
    restored_count = 0
    for item in backup_path.rglob("*"):
        if item.is_file() and item.name != "snapshot.json":
            rel_path = item.relative_to(backup_path)
            dest = Path(rel_path)
            
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                restored_count += 1
            except Exception as e:
                print(f"⚠️  Failed to restore {rel_path}: {e}")
    
    print(f"✅ Restored {restored_count} files from {snapshot_name}")

def main():
    parser = argparse.ArgumentParser(description="Workspace Snapshot Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a snapshot")
    create_parser.add_argument("name", nargs="?", default="", help="Snapshot name")
    
    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from snapshot")
    restore_parser.add_argument("name", help="Snapshot name (or partial match)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available snapshots")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_snapshot(args.name)
    elif args.command == "restore":
        restore_snapshot(args.name)
    elif args.command == "list":
        snapshots = list_snapshots()
        if snapshots:
            print("Available snapshots:")
            for snap_name, snap_type in snapshots:
                print(f"  • {snap_name} ({snap_type})")
        else:
            print("No snapshots found")

if __name__ == "__main__":
    main()
'''
    )
