#!/usr/bin/env python3
"""
GitHub Workflow Template Generator

Generates tier-specific GitHub Actions CI workflows.
"""

from config import DEFAULT_PYTHON_VERSION


def get_github_workflow(tier: str, python_version: str = DEFAULT_PYTHON_VERSION) -> str:
    """Generate GitHub Actions CI workflow with caching and optional matrix testing.

    Args:
        tier: Workspace tier (1, 2, or 3)
        python_version: Primary Python version for CI (also used in matrix)

    Returns:
        YAML content for .github/workflows/ci.yml
    """
    base = f"""name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'
      - name: Audit workspace
        run: python scripts/audit.py
"""
    if tier == "1":
        return (
            base
            + f"""
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'
          cache: 'pip'
      - run: pip install -q -r requirements.txt
      - run: python src/main.py
"""
        )
    elif tier == "2":
        return (
            base
            + f"""
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['{python_version}']
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: 'pip'
      - name: Install dependencies
        run: pip install -q -e ".[dev]"
      - name: Run tests
        run: pytest tests/ -q
      - name: Run tests with coverage (optional)
        run: |
          pip install -q pytest-cov 2>/dev/null || true
          pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=0 2>/dev/null || true
        continue-on-error: true
"""
        )
    else:
        return (
            base
            + f"""
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['{python_version}']
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{{{ matrix.python-version }}}}
          cache: 'pip'
      - name: Install uv
        run: pip install -q uv
      - name: Install dependencies
        run: uv sync --quiet
      - name: Run unit tests
        run: uv run pytest tests/unit/ -q

  eval:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{python_version}'
          cache: 'pip'
      - name: Install uv
        run: pip install -q uv
      - name: Install dependencies
        run: uv sync --quiet
      - name: Run agent evaluations
        run: uv run pytest tests/evals/ -q
"""
        )
