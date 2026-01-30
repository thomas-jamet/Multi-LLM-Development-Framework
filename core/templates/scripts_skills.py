#!/usr/bin/env python3
"""Skill Management Script Generators

Generates SkillsMP API client, search tool, discovery workflow, and list scripts.
"""


def get_skillsmp_client_script() -> str:
    """Generate SkillsMP API client (skillsmp_client.py)."""
    lines = [
        "#!/usr/bin/env python3",
        '"""SkillsMP API Client for skill discovery."""',
        "import os",
        "import requests",
        "from typing import Dict, List, Optional",
        "",
        "",
        "class SkillsMPError(Exception):",
        '    """Custom exception for SkillsMP API errors."""',
        "    ",
        "    def __init__(self, code: str, message: str):",
        "        self.code = code",
        "        self.message = message",
        '        super().__init__(f"{code}: {message}")',
        "",
        "",
        "class SkillsMP:",
        '    """Client for SkillsMP API.',
        "    ",
        "    Provides access to 110,000+ community skills via keyword and AI semantic search.",
        '    """',
        "    ",
        '    BASE_URL = "https://skillsmp.com/api/v1"',
        "    ",
        "    def __init__(self, api_key: Optional[str] = None):",
        '        """Initialize with API key from env or parameter.',
        "        ",
        "        Args:",
        "            api_key: Optional API key. If not provided, reads from SKILLSMP_API_KEY env var.",
        "            ",
        "        Raises:",
        "            ValueError: If no API key is provided or found in environment.",
        '        """',
        '        self.api_key = api_key or os.getenv("SKILLSMP_API_KEY")',
        "        if not self.api_key:",
        "            raise ValueError(",
        '                "API key required. Set SKILLSMP_API_KEY environment variable "',
        '                "or pass api_key to constructor"',
        "            )",
        "        ",
        "        self.headers = {",
        '            "Authorization": f"Bearer {self.api_key}",',
        '            "Content-Type": "application/json"',
        "        }",
        "    ",
        "    def _handle_response(self, response: requests.Response) -> Dict:",
        '        """Handle API response and parse errors.',
        "        ",
        "        Args:",
        "            response: requests Response object",
        "            ",
        "        Returns:",
        "            Parsed JSON response",
        "            ",
        "        Raises:",
        "            SkillsMPError: If API returns an error",
        '        """',
        "        try:",
        "            response.raise_for_status()",
        "            return response.json()",
        "        except requests.HTTPError:",
        "            # Try to parse error response",
        "            try:",
        "                error_data = response.json()",
        "                if not error_data.get('success', True):",
        "                    error_info = error_data.get('error', {})",
        "                    raise SkillsMPError(",
        "                        code=error_info.get('code', 'UNKNOWN_ERROR'),",
        "                        message=error_info.get('message', 'An error occurred')",
        "                    )",
        "            except (ValueError, KeyError):",
        "                # If we can't parse the error, raise original HTTP error",
        "                response.raise_for_status()",
        "    ",
        "    def search(",
        "        self,",
        "        query: str,",
        "        page: int = 1,",
        "        limit: int = 20,",
        '        sort_by: str = "stars"',
        "    ) -> Dict:",
        '        """Search skills by keyword.',
        "        ",
        "        Args:",
        "            query: Search query string",
        "            page: Page number (default: 1)",
        "            limit: Results per page (default: 20, max: 100)",
        "            sort_by: Sort order - 'stars' or 'recent'",
        "            ",
        "        Returns:",
        "            Dict containing results and pagination info",
        "            ",
        "        Raises:",
        "            requests.HTTPError: If API request fails",
        '        """',
        '        url = f"{self.BASE_URL}/skills/search"',
        "        params = {",
        '            "q": query,',
        '            "page": page,',
        '            "limit": min(limit, 100),  # Cap at 100',
        '            "sortBy": sort_by',
        "        }",
        "        ",
        "        response = requests.get(url, headers=self.headers, params=params, timeout=10)",
        "        return self._handle_response(response)",
        "    ",
        "    def ai_search(self, query: str) -> Dict:",
        '        """Search skills using AI semantic search.',
        "        ",
        "        Uses Cloudflare AI to understand natural language queries and return",
        "        semantically relevant results with relevance scores.",
        "        ",
        "        Args:",
        "            query: Natural language search query",
        "            ",
        "        Returns:",
        "            Dict containing AI-ranked results with relevance scores",
        "            ",
        "        Raises:",
        "            requests.HTTPError: If API request fails",
        '        """',
        '        url = f"{self.BASE_URL}/skills/ai-search"',
        '        params = {"q": query}',
        "        ",
        "        response = requests.get(url, headers=self.headers, params=params, timeout=10)",
        "        return self._handle_response(response)",
        "    ",
        "    def download_skill(self, skill_url: str) -> str:",
        '        """Download SKILL.md content from GitHub.',
        "        ",
        "        Args:",
        "            skill_url: Raw GitHub URL to SKILL.md file",
        "            ",
        "        Returns:",
        "            Skill content as string",
        "            ",
        "        Raises:",
        "            requests.HTTPError: If download fails",
        '        """',
        "        response = requests.get(skill_url, timeout=10)",
        "        response.raise_for_status()",
        "        return response.text",
    ]
    return "\n".join(lines)


def get_skillsmp_search_script() -> str:
    """Generate SkillsMP search/install CLI tool (skillsmp_search.py)."""
    # This is a long script, so I'll create it as a raw string template
    return '''#!/usr/bin/env python3
"""Enhanced skill discovery using SkillsMP API.

This script searches the SkillsMP marketplace (110,000+ skills) and allows
interactive installation of discovered skills.

Usage:
    # Keyword search
    python scripts/shared/skillsmp_search.py "email templates"

    # AI semantic search
    python scripts/shared/skillsmp_search.py "help me write professional emails" --ai

    # Search and install
    python scripts/shared/skillsmp_search.py "pdf tools" --install 2
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from scripts.shared.skillsmp_client import SkillsMP, SkillsMPError


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Search SkillsMP marketplace for AI skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "email templates"              # Keyword search
  %(prog)s "write resumes" --ai           # AI semantic search
  %(prog)s "pdf" --limit 5                # Limit results
  %(prog)s "data analysis" --install 3    # Install skill #3
        """
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--ai", action="store_true", help="Use AI semantic search")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10, max: 100)")
    parser.add_argument("--sort", choices=["stars", "recent"], default="stars", help="Sort order")
    parser.add_argument("--install", type=int, metavar="N", help="Install skill by number (1-N)")

    args = parser.parse_args()

    try:
        client = SkillsMP()

        # Execute search
        if args.ai:
            print(f"\\n🤖 AI Semantic Search: '{args.query}'")
            print("=" * 80)
            results = client.ai_search(args.query)
            # Handle API response structure
            data = results.get('data', {})
            skills = data.get('skills', [])
        else:
            print(f"\\n🔍 Keyword Search: '{args.query}'")
            print("=" * 80)
            results = client.search(args.query, limit=args.limit, sort_by=args.sort)
            # Handle API response structure
            data = results.get('data', {})
            pagination = data.get('pagination', {})
            total = pagination.get('total', 0)
            showing = len(data.get('skills', []))
            print(f"Found {total} skills | Showing {showing}\\n")
            skills = data.get('skills', [])

        if not skills:
            print("\\n❌ No skills found matching your query")
            print("\\n💡 Try:")
            print("  • Different keywords")
            print("  • AI semantic search (--ai flag)")
            print("  • Broader search terms")
            return

        # Display results
        for i, skill in enumerate(skills, 1):
            display_skill(i, skill, args.ai)

        # Installation
        if args.install:
            if 1 <= args.install <= len(skills):
                skill = skills[args.install - 1]
                install_skill(client, skill)
            else:
                print(f"\\n❌ Invalid skill number. Choose 1-{len(skills)}")
                sys.exit(1)
        else:
            print("\\n💡 To install a skill, run with --install N (e.g., --install 1)")

    except SkillsMPError as e:
        print(f"\\n❌ API Error: {e.message}")

        # Provide helpful guidance based on error code
        if e.code == "MISSING_API_KEY":
            print("💡 Add SKILLSMP_API_KEY to your .env file")
        elif e.code == "INVALID_API_KEY":
            print("💡 Check your API key at https://skillsmp.com/settings/api-keys")
        elif e.code == "MISSING_QUERY":
            print("💡 Provide a search query (e.g., make discover q=\\"pdf\\")")
        elif e.code == "INTERNAL_ERROR":
            print("💡 SkillsMP service issue - try again later")

        sys.exit(1)
    except ValueError as e:
        print(f"\\n❌ Configuration Error: {e}")
        print("\\n💡 Make sure SKILLSMP_API_KEY is set in .env")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"\\n❌ Network Error: {e}")
        print("\\n💡 Check your internet connection")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def display_skill(number: int, skill: dict, is_ai_search: bool = False):
    """Display a skill result in formatted output.

    Args:
        number: Skill number in results
        skill: Skill data dictionary
        is_ai_search: Whether this is from AI search (show relevance score)
    """
    name = skill.get('name', 'Unknown')
    description = skill.get('description', 'No description')
    author = skill.get('author', 'Unknown')
    stars = skill.get('stars', 0)
    url = skill.get('githubUrl', skill.get('url', ''))  # API uses githubUrl

    print(f"{number}. \\033[1;36m{name}\\033[0m")
    print(f"   📝 {description[:100]}{'...' if len(description) > 100 else ''}")
    print(f"   👤 {author}", end="")

    if stars:
        print(f" | ⭐ {stars} stars", end="")

    if is_ai_search and 'relevanceScore' in skill:
        score = skill['relevanceScore']
        print(f" | 🎯 {score:.2%} relevance", end="")

    print(f"\\n   🔗 {url}\\n")


def install_skill(client: SkillsMP, skill: dict):
    """Install a skill to .agent/skills/ directory.

    Args:
        client: SkillsMP API client
        skill: Skill data dictionary
    """
    skill_name = skill['name']
    skill_url = skill.get('skillUrl')

    if not skill_url:
        print(f"\\n❌ No SKILL.md URL found for {skill_name}")
        return

    # Download SKILL.md
    print(f"\\n📥 Downloading {skill_name}...")
    try:
        content = client.download_skill(skill_url)
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return

    # Create skill directory
    skill_dir = Path(".agent/skills") / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # Save SKILL.md
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content)

    print(f"✅ Installed to: {skill_dir}")
    print(f"\\n📝 SKILL.md: {len(content)} bytes")
    print(f"\\n💡 Next steps:")
    print(f"   1. Review: cat {skill_file}")
    print(f"   2. Commit: git add .agent/skills/{skill_name}")
    print(f"   3. List: make list-skills")


if __name__ == "__main__":
    main()
'''


def get_skill_discovery_workflow() -> str:
    """Generate the SkillsMP Skill Discovery workflow."""
    lines = [
        "---",
        "description: Search and install skills from SkillsMP marketplace (110,000+ skills)",
        "---",
        "",
        "# Skill Discovery Workflow",
        "",
        "This workflow guides you through discovering and installing skills from the SkillsMP marketplace.",
        "",
        "## Prerequisites",
        "",
        "- SKILLSMP_API_KEY configured in `.env` file",
        "- Internet connection for API access",
        "",
        "## Steps",
        "",
        "### 1. Search for Skills",
        "",
        "Search the SkillsMP marketplace by topic or keyword:",
        "",
        "```bash",
        'make discover q="topic"',
        'make discover q="pdf tools"',
        'make discover q="email templates"',
        "```",
        "",
        "The search will return:",
        "- Skill ID (for installation)",
        "- Skill name",
        "- Description",
        "- Author",
        "- Repository URL",
        "",
        "### 2. Review Search Results",
        "",
        "Examine the returned skills. Note the `id` of any skill you want to install.",
        "",
        "Example output:",
        "```",
        "ID: skill-pdf-tools",
        "Name: PDF Tools",
        "Description: Comprehensive PDF manipulation toolkit",
        "Author: anthropics",
        "Repo: https://github.com/anthropics/skills/tree/main/pdf",
        "```",
        "",
        "### 3. Install a Skill",
        "",
        "Install a skill using its ID:",
        "",
        "```bash",
        'make skill-install id="skill-pdf-tools"',
        "```",
        "",
        "This will:",
        "- Download the SKILL.md file",
        "- Create `.agent/skills/skill-name/` directory",
        "- Save the skill for immediate use",
        "",
        "### 4. Verify Installation",
        "",
        "List installed skills to confirm:",
        "",
        "```bash",
        "make list-skills",
        "```",
        "",
        "The newly installed skill should appear in the output.",
        "",
        "## API Reference",
        "",
        "**Search API:**",
        "```bash",
        'make discover q="<search_query>"',
        "```",
        "",
        "**Install API:**",
        "```bash",
        'make skill-install id="<skill-id>"',
        "```",
        "",
        "## Error Handling",
        "",
        "Common errors:",
        "",
        "- **Missing API Key:** Add `SKILLSMP_API_KEY` to `.env` file",
        "- **Invalid API Key:** Check your key at skillsmp.com/settings",
        "- **Network Error:** Check internet connection",
        "- **Skill Not Found:** Verify the skill ID from search results",
    ]
    return "\n".join(lines)


def get_list_skills_script() -> str:
    """Generate cross-platform list-skills script."""
    return '''#!/usr/bin/env python3
"""List available skills and workflows (cross-platform)."""
from pathlib import Path

def list_items(directory: str, label: str, emoji: str):
    """List markdown files in a directory."""
    path = Path(directory)
    if not path.exists():
        return

    items = sorted([f.stem for f in path.glob("*.md")])
    if items:
        print(f"\\n{emoji} {label}:")
        for item in items:
            print(f"   - {item}")

if __name__ == "__main__":
    list_items(".agent/skills", "Available Skills", "📚")
    list_items(".agent/workflows", "Available Workflows", "📋")
    list_items(".agent/patterns", "Available Patterns", "🎨")
    print()
'''
