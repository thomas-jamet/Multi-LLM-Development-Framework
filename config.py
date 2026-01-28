#!/usr/bin/env python3
"""
Bootstrap Source Configuration Module

Central configuration and constants for workspace bootstrap.
Defines tier specifications, default structures, and branding.
"""

from typing import Dict, List, Any

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
SCRIPT_NAME = "Gemini Native Workspace Bootstrap"

# Tier Definitions
TIER_NAMES = {
    "1": "Lite",
    "2": "Standard", 
    "3": "Enterprise"
}

TIER_DESCRIPTIONS = {
    "1": "Lightweight workspace with basic features",
    "2": "Full-featured workspace with testing and quality gates",
    "3": "Enterprise workspace with advanced features and evaluations"
}

# Directory Structure Templates
BASE_DIRECTORIES = [
    "src",
    "tests",
    "docs",
    "logs",
    "scratchpad",
    ".agent/skills",
    ".agent/workflows"
]

TIER_SPECIFIC_DIRECTORIES = {
    "1": [],  # Lite has no additional directories
    "2": [
        "docs/architecture",
        "docs/api"
    ],
    "3": [
        "docs/architecture",
        "docs/api", 
        "docs/evaluations",
        "benchmarks"
    ]
}

# File Permissions
EXECUTABLE_FILES = [
    "scripts/audit.py",
    "scripts/session.py",
    "scripts/doc_indexer.py",
    "scripts/status.py",
    "scripts/list_skills.py",
    "scripts/skill_manager.py",
    "scripts/skill_explorer.py"
]

# Color Codes for Terminal Output
COLORS = {
    "BLUE": "\\033[1;34m",
    "GREEN": "\\033[1;32m",
    "YELLOW": "\\033[1;33m",
    "RED": "\\033[1;31m",
    "NC": "\\033[0m"  # No Color
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
        "archive": "🛡️"
    }
}

# Makefile .PHONY targets by tier
PHONY_TARGETS = {
    "1": [
        "run", "test", "install", "context", "clean", "audit",
        "session-start", "session-end", "init", "list-skills", "help",
        "doctor", "status", "health", "lint", "format", "ci-local",
        "deps-check", "security-scan", "session-force-end-all", "onboard",
        "sync", "search", "list-todos", "index", "backup", 
        "skill-add", "skill-remove"
    ],
    "2": [
        "run", "test", "test-watch", "coverage", "typecheck", "install",
        "context", "clean", "audit", "session-start", "session-end", "init",
        "list-skills", "help", "snapshot", "restore", "doctor", "status",
        "health", "format", "update", "docs", "lint", "ci-local",
        "deps-check", "security-scan", "session-force-end-all", "onboard",
        "backup", "sync", "search", "list-todos", "index",
        "skill-add", "skill-remove"
    ],
    "3": [
        "scan", "test", "test-watch", "coverage", "typecheck", "audit", "eval",
        "context", "context-frontend", "context-backend", "install", "clean",
        "session-start", "session-end", "init", "list-skills", "shift-report",
        "snapshot", "restore", "doctor", "status", "health", "help", "lint",
        "format", "update", "lock", "docs", "ci-local", "deps-check",
        "security-scan", "session-force-end-all", "onboard", "backup",
        "sync", "search", "list-todos", "index", "skill-add", "skill-remove"
    ]
}

# Default requirements by tier
DEFAULT_REQUIREMENTS = {
    "1": [
        "# Gemini Lite Workspace Dependencies",
        "# Add your project dependencies here",
        "",
        "# Code Quality",
        "ruff>=0.1.0"
    ],
    "2": [
        "# Gemini Standard Workspace Dependencies",
        "# Add your project dependencies here",
        "",
        "# Testing",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "",
        "# Code Quality",
        "ruff>=0.1.0",
        "mypy>=1.0.0"
    ],
    "3": [
        "# Gemini Enterprise Workspace Dependencies",
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
        "mypy>=1.0.0"
    ]
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
    "# Gemini Specific",
    ".gemini/cache/",
    "",
    "# OS",
    ".DS_Store",
    "Thumbs.db"
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


# Tier Metadata
TIERS = {
    "1": {"name": "Lite", "desc": "Lightweight workspace with basic features"},
    "2": {"name": "Standard", "desc": "Full-featured workspace with testing"},
    "3": {"name": "Enterprise", "desc": "Enterprise workspace with advanced features"}
}

# Templates (placeholder - can be extended)
TEMPLATES = {}
