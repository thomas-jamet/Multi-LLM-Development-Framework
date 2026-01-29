#!/usr/bin/env python3
"""
JSON Schema Template Generators

Generates JSON schemas for workspace validation and IDE autocomplete.
"""

import json


def get_workspace_schema() -> str:
    """Generate JSON schema for workspace.json validation and IDE autocomplete."""
    return json.dumps(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Gemini Workspace Configuration",
            "description": "Metadata for Gemini Native Workspace Standard",
            "type": "object",
            "required": ["version", "tier", "name", "created", "standard"],
            "properties": {
                "version": {
                    "type": "string",
                    "description": "Standard version used to create workspace",
                    "pattern": "^\\d{4}\\.\\d+$",
                },
                "tier": {
                    "type": "string",
                    "enum": ["1", "2", "3"],
                    "description": "Workspace tier: 1=Lite, 2=Standard, 3=Enterprise",
                },
                "name": {
                    "type": "string",
                    "description": "Project name",
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_-]*$",
                },
                "created": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 timestamp of workspace creation",
                },
                "standard": {
                    "type": "string",
                    "const": "Gemini Native Workspace Standard",
                },
                "parent_workspace": {
                    "type": "string",
                    "description": "Path to parent workspace (for monorepos)",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "archived"],
                    "default": "active",
                },
                "upgraded": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp of last tier upgrade",
                },
                "previous_tier": {
                    "type": "string",
                    "enum": ["1", "2"],
                    "description": "Tier before last upgrade",
                },
                "scripts_updated": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp of last script update",
                },
            },
        },
        indent=2,
    )

def get_settings_schema() -> str:
    """Generate JSON schema for settings.json validation and IDE autocomplete."""
    return json.dumps(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Gemini Workspace Settings",
            "description": "Permissions and behavior settings for Gemini workspace",
            "type": "object",
            "properties": {
                "permissions": {
                    "type": "object",
                    "properties": {
                        "filesystem": {
                            "type": "object",
                            "properties": {
                                "read": {"type": "array", "items": {"type": "string"}},
                                "edit": {"type": "array", "items": {"type": "string"}},
                                "ignore": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                        "terminal": {
                            "type": "object",
                            "properties": {
                                "execution_policy": {
                                    "type": "string",
                                    "enum": ["safe-only", "hybrid", "unrestricted"],
                                },
                                "allowed_commands": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    },
                },
                "behavior": {
                    "type": "object",
                    "properties": {
                        "auto_context_refresh": {"type": "boolean", "default": True}
                    },
                },
                "parent_workspace": {"type": "string"},
            },
        },
        indent=2,
    )

def get_bootstrap_config_schema() -> str:
    """Generate JSON schema for .gemini-bootstrap.json validation and documentation."""
    return json.dumps(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Gemini Bootstrap Configuration",
            "description": "Team defaults for the Gemini workspace bootstrap script",
            "type": "object",
            "properties": {
                "default_tier": {
                    "type": "string",
                    "enum": ["1", "2", "3"],
                    "description": "Default tier for new workspaces (1=Lite, 2=Standard, 3=Enterprise)",
                },
                "shared_agent_path": {
                    "type": "string",
                    "description": "Path to shared .agent/ directory for team-wide skills/workflows",
                },
                "templates_path": {
                    "type": "string",
                    "description": "Path to custom templates directory",
                },
                "default_git": {
                    "type": "boolean",
                    "default": False,
                    "description": "Initialize git repository by default",
                },
                "python_version": {
                    "type": "string",
                    "pattern": "^3\\.\\d+$",
                    "default": "3.11",
                    "description": "Python version for CI workflows",
                },
            },
        },
        indent=2,
    )
