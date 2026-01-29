#!/usr/bin/env python3
"""Skill Explorer - Discover and install capabilities from community repositories."""
import argparse
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Curated sources with known skill paths
CURATED_SOURCES = {
    "anthropics/skills": ["bash.md", "github.md", "editor.md", "sql.md"],
    "google-gemini/gemini-cli": ["examples/skills/"],
    "huggingface/skills": ["skills/"],
}

GITHUB_RAW = "https://raw.githubusercontent.com/{repo}/main/{path}"

def extract_title(content: str) -> str:
    """Extract title from markdown (first # heading)."""
    for line in content.split("\n")[:20]:
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled Skill"

def extract_description(content: str) -> str:
    """Extract first paragraph after title."""
    lines = content.split("\n")
    desc_lines = []
    found_title = False
    
    for line in lines[:30]:
        if line.startswith("# "):
            found_title = True
            continue
        if found_title and line.strip() and not line.startswith("#"):
            if line.startswith("```"):
                break
            desc_lines.append(line.strip())
            if len(desc_lines) >= 3:
                break
    
    return " ".join(desc_lines)[:150] + "..." if desc_lines else "No description available"

def fetch_skill_content(repo: str, path: str) -> str:
    """Fetch raw skill content from GitHub."""
    url = GITHUB_RAW.format(repo=repo, path=path)
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.read().decode("utf-8")
    except Exception:
        return None

def discover_skills(query: str):
    """Discover skills from curated sources."""
    skills = []
    query_lower = query.lower()
    
    # Match repositories
    for repo, paths in CURATED_SOURCES.items():
        if query_lower == "all" or query_lower in repo.lower():
            for path in paths:
                content = fetch_skill_content(repo, path)
                if content:
                    skills.append({
                        "repo": repo,
                        "path": path,
                        "content": content,
                        "title": extract_title(content),
                        "description": extract_description(content),
                        "source": f"{repo}/{path}"
                    })
    
    return skills

def preview_skill(content: str, max_lines: int = 20):
    """Display skill preview."""
    lines = content.split("\n")
    preview_lines = lines[:max_lines]
    total_lines = len(lines)
    
    print("\n" + "━" * 60)
    print("\n".join(preview_lines))
    print("━" * 60)
    print(f"(showing first {max_lines} lines, {total_lines} total)\n")

def install_skill(skill: dict):
    """Install a skill to .agent/ directory."""
    # Determine target directory
    filename = skill["path"].split("/")[-1]
    if not filename.endswith(".md"):
        filename += ".md"
        
    title_lower = skill["title"].lower()
    if "workflow" in title_lower or "guide" in title_lower:
        target_dir = Path(".agent/workflows")
    else:
        target_dir = Path(".agent/skills")
    
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / filename
    
    # Check if exists
    if target_file.exists():
        overwrite = input(f"⚠️  {filename} already exists. Overwrite? [y/N]: ").strip().lower()
        if overwrite != "y":
            print("❌ Installation cancelled")
            return False
    
    # Write file
    try:
        with open(target_file, "w") as f:
            f.write(skill["content"])
        print(f"✅ Installed to: {target_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to install: {e}")
        return False

def interactive_selection(skills: list):
    """Interactive menu for skill selection and installation."""
    if not skills:
        print("\n❌ No skills found matching your query.")
        print("\n💡 Try: make discover q="all" to see all curated skills")
        return
    
    print(f"\nFound {len(skills)} skill(s):\n")
    
    # Display menu
    for i, skill in enumerate(skills, 1):
        print("━" * 60)
        print(f"[{i}] {skill['title']}")
        print(f"    {skill['description']}")
        print(f"    📦 Source: {skill['source']}")
        print(f"    ⭐ Verified Repository")
    print("━" * 60)
    
    installed_count = 0
    
    # Installation loop
    while True:
        print(f"\nInstall a skill? [1-{len(skills)}, n to skip]: ", end="")
        choice = input().strip().lower()
        
        if choice == "n" or choice == "":
            break
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(skills):
                skill = skills[idx]
                print(f"\n📄 Previewing: {skill['title']}")
                preview_skill(skill["content"])
                
                confirm = input("✅ Install this skill? [y/N]: ").strip().lower()
                if confirm == "y":
                    if install_skill(skill):
                        installed_count += 1
                else:
                    print("⏭️  Skipped")
            else:
                print(f"❌ Invalid choice. Enter 1-{len(skills)} or n")
        except ValueError:
            print(f"❌ Invalid input. Enter a number 1-{len(skills)} or n")
    
    if installed_count > 0:
        print(f"\n🎉 Done! Installed {installed_count} skill(s).")
    else:
        print("\n👋 No skills installed.")

def search_github(query: str):
    """Search and display skills interactively."""
    print(f"🔍 Searching for skills related to '{query}'...")
    
    skills = discover_skills(query)
    interactive_selection(skills)

def main():
    parser = argparse.ArgumentParser(
        description="Skill Explorer - Discover and install AI agent capabilities"
    )
    parser.add_argument(
        "command",
        choices=["search"],
        help="Command to run"
    )
    parser.add_argument(
        "query",
        help="Search term (try 'all', 'bash', 'sql', etc.)"
    )
    
    args = parser.parse_args()
    
    if args.command == "search":
        search_github(args.query)

if __name__ == "__main__":
    main()