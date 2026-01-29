#!/usr/bin/env python3
"""
Template Generation Package

Exports all template generator functions for workspace creation.
Organized into logical modules:
- gemini_md: GEMINI.md constitution
- github_workflow: CI/CD workflows
- scripts_core: audit, session, docs, status
- scripts_snapshot: snapshot/restore functionality
- scripts_skills: skill management tools
- schemas: JSON schemas for validation
- configs: pre-commit and other configs
"""

from .gemini_md import get_gemini_md
from .github_workflow import get_github_workflow
from .scripts_core import (
    get_run_audit_script,
    get_manage_session_script,
    get_index_docs_script,
    get_check_status_script,
)
from .scripts_snapshot import get_create_snapshot_script
from .scripts_skills import (
    get_manage_skills_script,
    get_explore_skills_script,
    get_skill_discovery_workflow,
    get_list_skills_script,
)
from .schemas import (
    get_workspace_schema,
    get_settings_schema,
    get_bootstrap_config_schema,
)
from .configs import get_precommit_config

__all__ = [
    # GEMINI.md
    "get_gemini_md",
    # GitHub
    "get_github_workflow",
    # Core scripts
    "get_run_audit_script",
    "get_manage_session_script",
    "get_index_docs_script",
    "get_check_status_script",
    # Snapshot
    "get_create_snapshot_script",
    # Skills
    "get_manage_skills_script",
    "get_explore_skills_script",
    "get_skill_discovery_workflow",
    "get_list_skills_script",
    # Schemas
    "get_workspace_schema",
    "get_settings_schema",
    "get_bootstrap_config_schema",
    # Configs
    "get_precommit_config",
]
