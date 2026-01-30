#!/usr/bin/env python3
"""
Configuration File Template Generators

Generates pre-commit and other config file templates.
"""


def get_precommit_config() -> str:
    """Generate .pre-commit-config.yaml template."""
    return """# Pre-commit hooks configuration
# Install: pip install pre-commit && pre-commit install
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  # Uncomment for conventional commits
  # - repo: https://github.com/compilerla/conventional-pre-commit
  #   rev: v3.2.0
  #   hooks:
  #     - id: conventional-pre-commit
  #       stages: [commit-msg]
"""
