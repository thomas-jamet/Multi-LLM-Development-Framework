#!/usr/bin/env python3
"""
Bootstrap Source Configuration Module

Central configuration and constants for workspace bootstrap.
Defines tier specifications, default structures, and branding.
"""

from typing import List

# Version Information
VERSION = "2026.26"
DEFAULT_PYTHON_VERSION = "3.11"

# Exit Codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_CREATION_ERROR = 2
EXIT_UPGRADE_ERROR = 3
EXIT_ROLLBACK_ERROR = 4
EXIT_CONFIG_ERROR = 5
EXIT_WORKSPACE_ERROR = 6
EXIT_INTERRUPT = 130
EXIT_UNEXPECTED_ERROR = 255
SCRIPT_NAME = "Multi-LLM Development Framework"

# Supported LLM Providers
SUPPORTED_PROVIDERS = ["gemini", "claude", "codex"]
DEFAULT_PROVIDER = "gemini"

# Tier Definitions
TIER_NAMES = {"1": "Lite", "2": "Standard", "3": "Enterprise"}

TIER_DESCRIPTIONS = {
    "1": "Lightweight workspace with basic features",
    "2": "Full-featured workspace with testing and quality gates",
    "3": "Enterprise workspace with advanced features and evaluations",
}

# Directory Structure Templates
BASE_DIRECTORIES = [
    "src",
    "tests",
    "docs",
    "logs",
    "scratchpad",
    ".agent/skills",
    ".agent/workflows",
]

TIER_SPECIFIC_DIRECTORIES = {
    "1": [],  # Lite has no additional directories
    "2": ["docs/architecture", "docs/api"],
    "3": ["docs/architecture", "docs/api", "docs/evaluations", "benchmarks"],
}

# Script Organization Patterns
# Maps tier -> category -> list of script names (without .py extension)
SCRIPT_CATEGORIES = {
    "1": {  # Lite: flat structure in scripts/
        "": [
            "run_audit",
            "manage_session",
            "check_status",
            "index_docs",
            "list_skills",
            "manage_skills",
            "explore_skills",
        ]
    },
    "2": {  # Standard: functional categories
        "workspace": ["run_audit", "manage_session", "check_status", "create_snapshot"],
        "skills": ["list_skills", "manage_skills", "explore_skills"],
        "docs": ["index_docs"],
    },
    "3": {  # Enterprise: domain-based (shared is default)
        "shared": ["run_audit", "manage_session", "check_status", "create_snapshot"]
    },
}

# Standard script verbs for verb_noun.py naming convention
SCRIPT_VERBS = [
    "run",  # Execute processes (audit, tests)
    "check",  # Inspections (status, health)
    "manage",  # CRUD operations (session, config, skills)
    "generate",  # Create artifacts (reports, docs)
    "sync",  # Data synchronization
    "index",  # Build search indices
    "list",  # Display collections
    "create",  # Create new items (snapshots)
    "explore",  # Discovery/exploration (skills)
]

# File Permissions (Standard tier paths as reference)
EXECUTABLE_FILES = [
    "scripts/workspace/run_audit.py",
    "scripts/workspace/manage_session.py",
    "scripts/workspace/check_status.py",
    "scripts/workspace/create_snapshot.py",
    "scripts/docs/index_docs.py",
    "scripts/skills/list_skills.py",
    "scripts/skills/manage_skills.py",
    "scripts/skills/explore_skills.py",
]

# Snapshot configuration
SNAPSHOTS_DIR = ".snapshots"

# Color Codes for Terminal Output
COLORS = {
    "BLUE": "\\033[1;34m",
    "GREEN": "\\033[1;32m",
    "YELLOW": "\\033[1;33m",
    "RED": "\\033[1;31m",
    "NC": "\\033[0m",  # No Color
}

# Branding
BRANDING = {
    "emoji": {
        "system": "⚙️",
        "tools": "🔧",
        "branding": "🎨",
        "session": "⏱️",
        "health": "🏥",
        "hygiene": "🧹",
        "security": "🛡️",
        "app": "🚀",
        "test": "🧪",
        "docs": "📚",
        "env": "📦",
        "archive": "🛡️",
    }
}

# Makefile .PHONY targets by tier
PHONY_TARGETS = {
    "1": [
        "run",
        "test",
        "install",
        "context",
        "clean",
        "audit",
        "session-start",
        "session-end",
        "init",
        "list-skills",
        "help",
        "doctor",
        "status",
        "health",
        "lint",
        "format",
        "ci-local",
        "deps-check",
        "security-scan",
        "session-force-end-all",
        "onboard",
        "sync",
        "search",
        "list-todos",
        "index",
        "backup",
        "skill-add",
        "skill-remove",
    ],
    "2": [
        "run",
        "test",
        "test-watch",
        "coverage",
        "typecheck",
        "install",
        "context",
        "clean",
        "audit",
        "session-start",
        "session-end",
        "init",
        "list-skills",
        "help",
        "snapshot",
        "restore",
        "doctor",
        "status",
        "health",
        "format",
        "update",
        "docs",
        "lint",
        "ci-local",
        "deps-check",
        "security-scan",
        "session-force-end-all",
        "onboard",
        "backup",
        "sync",
        "search",
        "list-todos",
        "index",
        "skill-add",
        "skill-remove",
    ],
    "3": [
        "scan",
        "test",
        "test-watch",
        "coverage",
        "typecheck",
        "audit",
        "eval",
        "context",
        "context-frontend",
        "context-backend",
        "install",
        "clean",
        "session-start",
        "session-end",
        "init",
        "list-skills",
        "shift-report",
        "snapshot",
        "restore",
        "doctor",
        "status",
        "health",
        "help",
        "lint",
        "format",
        "update",
        "lock",
        "docs",
        "ci-local",
        "deps-check",
        "security-scan",
        "session-force-end-all",
        "onboard",
        "backup",
        "sync",
        "search",
        "list-todos",
        "index",
        "skill-add",
        "skill-remove",
    ],
}

# Default requirements by tier
DEFAULT_REQUIREMENTS = {
    "1": [
        "# Lite Workspace Dependencies",
        "# Add your project dependencies here",
        "",
        "# Code Quality",
        "ruff>=0.1.0",
    ],
    "2": [
        "# Standard Workspace Dependencies",
        "# Add your project dependencies here",
        "",
        "# Testing",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "",
        "# Code Quality",
        "ruff>=0.1.0",
        "mypy>=1.0.0",
    ],
    "3": [
        "# Enterprise Workspace Dependencies",
        "# Add your project dependencies here",
        "",
        "# High-performance package manager (recommended)",
        "uv>=0.1.0",
        "",
        "# Testing & Quality",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-benchmark>=4.0.0",
        "",
        "# Code Quality",
        "ruff>=0.1.0",
        "mypy>=1.0.0",
    ],
}

# Git ignore patterns
GITIGNORE_PATTERNS = [
    "# Python",
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    "*.so",
    ".Python",
    "build/",
    "develop-eggs/",
    "dist/",
    "downloads/",
    "eggs/",
    ".eggs/",
    "lib/",
    "lib64/",
    "parts/",
    "sdist/",
    "var/",
    "wheels/",
    "*.egg-info/",
    ".installed.cfg",
    "*.egg",
    "",
    "# Virtual Environment",
    "venv/",
    "ENV/",
    "env/",
    ".venv/",
    "",
    "# IDE",
    ".vscode/",
    ".idea/",
    "*.swp",
    "*.swo",
    "*~",
    "",
    "# Project Specific",
    "logs/*.log",
    "scratchpad/*",
    ".env",
    ".env.local",
    "",
    "# Testing",
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    "",
    "# LLM Provider Cache (provider-specific)",
    ".gemini/cache/",
    ".claude/cache/",
    ".codex/cache/",
    "",
    "# OS",
    ".DS_Store",
    "Thumbs.db",
]


def get_all_directories(tier: str) -> List[str]:
    """Get complete directory list for a tier."""
    return BASE_DIRECTORIES + TIER_SPECIFIC_DIRECTORIES.get(tier, [])


def get_tier_name(tier: str) -> str:
    """Get human-readable tier name."""
    return TIER_NAMES.get(tier, "Unknown")


def get_phony_targets(tier: str) -> List[str]:
    """Get .PHONY targets for a tier."""
    return PHONY_TARGETS.get(tier, PHONY_TARGETS["1"])


def get_gitignore_for_tier(tier: str) -> List[str]:
    """Get complete .gitignore patterns for a tier including data directories.

    Args:
        tier: Workspace tier ("1" for Lite, "2" for Standard, "3" for Enterprise)

    Returns:
        Complete list of gitignore patterns
    """
    patterns = GITIGNORE_PATTERNS.copy()

    # Add tier-specific data patterns
    if tier in ["1", "2"]:  # Lite/Standard: flat data structure
        patterns.extend(
            [
                "",
                "# Data (Lite/Standard tier pattern)",
                "data/inputs/*",
                "!data/inputs/.gitkeep",
                "data/outputs/*",
            ]
        )
    else:  # Enterprise: domain-based data structure
        patterns.extend(
            [
                "",
                "# Data (Enterprise tier pattern)",
                "data/*/inputs/*",
                "data/*/outputs/*",
                "!data/*/.gitkeep",
            ]
        )

    return patterns


# Tier Metadata
TIERS = {
    "1": {
        "name": "Lite",
        "desc": "Lightweight workspace with basic features",
        "order": 1,
    },
    "2": {
        "name": "Standard",
        "desc": "Full-featured workspace with testing",
        "order": 2,
    },
    "3": {
        "name": "Enterprise",
        "desc": "Enterprise workspace with advanced features",
        "order": 3,
    },
}

# Templates (placeholder - can be extended)
TEMPLATES = {}
