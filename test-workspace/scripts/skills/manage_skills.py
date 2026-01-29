#!/usr/bin/env python3
"""Skill Manager - Install and remove Agent Skills."""
import argparse
import os
import shutil
import sys
import urllib.request
from pathlib import Path

# Github raw content URL pattern
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"

def fetch_skill(source: str):
    """Fetch a skill from a URL or GitHub shorthand."""
    print(f"📥 Fetching skill from: {source}")
    
    # Parse source
    if source.startswith("http"):
        url = source
        filename = source.split("/")[-1]
    elif len(source.split("/")) >= 3:
        # shorthand: owner/repo/path/to/skill.md
        parts = source.split("/")
        owner = parts[0]
        repo = parts[1]
        path = "/".join(parts[2:])
        branch = "main" # Default to main
        
        # Determine filename
        filename = parts[-1]
        
        url = GITHUB_RAW_BASE.format(
            owner=owner,
            repo=repo,
            branch=branch,
            path=path
        )
    else:
        print("❌ Invalid source format. Use 'owner/repo/path/to/skill.md' or full URL.")
        sys.exit(1)
        
    if not filename.endswith(".md"):
        filename += ".md"

    # Define target path
    target_dir = Path(".agent/skills")
    # If workflow, go to workflows
    title_lower = filename.lower()
    if "workflow" in title_lower or "guide" in title_lower:
         target_dir = Path(".agent/workflows")
    
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / filename
    
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
            
        with open(target_file, "w") as f:
            f.write(content)
            
        print(f"✅ Installed: {target_file}")
        
    except Exception as e:
        print(f"❌ Failed to fetch skill: {e}")
        sys.exit(1)

def remove_skill(name: str):
    """Remove a local skill."""
    # check skills and workflows
    paths = [
        Path(".agent/skills") / name,
        Path(".agent/skills") / (name + ".md"),
        Path(".agent/workflows") / name,
        Path(".agent/workflows") / (name + ".md")
    ]
    
    found = False
    for p in paths:
        if p.exists():
            p.unlink()
            print(f"🗑️  Removed: {p}")
            found = True
            
    if not found:
        print(f"⚠️  Skill '{name}' not found.")

def main():
    parser = argparse.ArgumentParser(description="Skill Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    fetch_parser = subparsers.add_parser("fetch", help="Install a skill")
    fetch_parser.add_argument("source", help="GitHub shorthand (owner/repo/path) or URL")
    
    remove_parser = subparsers.add_parser("remove", help="Remove a skill")
    remove_parser.add_argument("name", help="Name of the skill to remove")
    
    args = parser.parse_args()
    
    if args.command == "fetch":
        fetch_skill(args.source)
    elif args.command == "remove":
        remove_skill(args.name)

if __name__ == "__main__":
    main()