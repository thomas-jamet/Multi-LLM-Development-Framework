#!/usr/bin/env python3
"""List available skills and workflows (cross-platform)."""

from pathlib import Path


def list_items(directory: str, label: str, emoji: str):
    """List markdown files in a directory."""
    path = Path(directory)
    if not path.exists():
        return

    items = sorted([f.stem for f in path.glob("*.md")])
    if items:
        print(f"\n{emoji} {label}:")
        for item in items:
            print(f"   - {item}")


if __name__ == "__main__":
    list_items(".agent/skills", "Available Skills", "📚")
    list_items(".agent/workflows", "Available Workflows", "📋")
    list_items(".agent/patterns", "Available Patterns", "🎨")
    print()
