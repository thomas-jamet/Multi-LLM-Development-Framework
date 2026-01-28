#!/usr/bin/env python3
"""
Content Generators Module

Generates workspace.json, README, getting started guides, etc.
"""

import json
from datetime import datetime, timezone
from typing import Dict


# Version constant (imported from config in final build)
VERSION = "2026.26"


def get_workspace_json(tier: str, name: str, parent: str | None = None) -> str:
    """Generate workspace.json metadata with timezone-aware timestamp."""
    data = {
        "version": VERSION,
        "tier": tier,
        "name": name,
        "created": datetime.now(timezone.utc).astimezone().isoformat(),
        "standard": "Gemini Native Workspace Standard",
    }
    if parent:
        data["parent_workspace"] = parent
    return json.dumps(data, indent=2)

def get_getting_started(tier: str, pkg_name: str) -> str:
    """Generate tier-specific getting started guide for onboarding."""
    common = """# Getting Started

Welcome to your Gemini Native Workspace!

## First Steps

1. **Load Context:** Run `make context` and paste into your LLM
2. **Say:** "I am ready to work on this project."
3. **Check Skills:** Run `make list-skills` to see available capabilities

## Essential Commands

| Command | Description |
|---------|-------------|
| `make context` | Load workspace context for LLM |
| `make list-skills` | Show available skills and workflows |
| `make audit` | Validate workspace structure |
| `make session-start` | Begin a work session |
| `make session-end` | End session with summary |

"""
    if tier == "1":
        return (
            common
            + """## Lite Tier Commands

| Command | Description |
|---------|-------------|
| `make run` | Execute main script |
| `make install` | Install dependencies |
| `make clean` | Clear temp files and logs |

## Quick Start

```bash
make install
make run
```
"""
        )
    elif tier == "2":
        return (
            common
            + f"""## Standard Tier Commands

| Command | Description |
|---------|-------------|
| `make run` | Run the application |
| `make test` | Run pytest suite |
| `make install` | Install in dev mode |

## Quick Start

```bash
make install
make test
make run
```

## Development Workflow

1. Plan changes in `scratchpad/current_plan.md`
2. Write tests in `tests/unit/`
3. Implement in `src/{pkg_name}/`
4. Run `make test` until green
5. Update `docs/roadmap.md`
"""
        )
    else:
        return (
            common
            + f"""## Enterprise Tier Commands

| Command | Description |
|---------|-------------|
| `make scan` | Run CLI scanner |
| `make eval` | Run agent capability tests |
| `make context-frontend` | Load frontend domain context |
| `make shift-report` | Generate shift handoff report |
| `make snapshot` | Create workspace snapshot |
| `make restore` | Restore from snapshot |

## Domain Structure

- `src/{pkg_name}/domains/frontend/` - UI context
- `src/{pkg_name}/domains/backend/` - API context
- `outputs/contracts/` - Inter-domain schemas

## Multi-Agent Workflow

1. Load domain-specific context: `make context-frontend`
2. Work within domain boundaries
3. Use contracts for cross-domain communication
4. Run `make eval` before merging
"""
        )


def get_archive_workflow() -> str:
    """Generate archive/deprecation workflow."""
    return """# Workflow: Archive Workspace
**Objective:** Safely deprecate and archive a workspace.
**Trigger:** Project end-of-life or migration complete.

## Pre-Requisites
- [ ] All work committed and pushed
- [ ] No active sessions
- [ ] Stakeholders notified

## Stages

### 1. Export
1. Run `make snapshot` to capture final state
2. Export critical docs to long-term storage
3. Document final architecture in `docs/architecture.md`

### 2. Secure
1. Rotate or revoke all secrets in `.env`
2. Remove credentials from CI/CD:
   - GitHub Actions: Settings -> Secrets -> Delete all repository secrets
   - Cloud providers: Revoke service account keys (AWS/GCP/Azure)
   - Third-party APIs: Regenerate or delete API keys
3. Check and clean common credential locations:
   - `~/.aws/credentials` - AWS CLI credentials
   - `~/.config/gcloud/` - GCP credentials
   - `~/.azure/` - Azure CLI credentials
   - `~/.npmrc` - npm auth tokens
   - `~/.docker/config.json` - Docker registry auth
   - `~/.ssh/` - Deploy keys specific to this project
4. Update access permissions
5. Remove deploy keys and webhooks

### 3. Archive
1. Update `workspace.json`: set `"status": "archived"`
2. Create final git tag: `git tag -a archive-YYYY-MM-DD`
3. Move to archive location or set repo to read-only

### 4. Notify
1. Update project documentation
2. Send archive notice to stakeholders
3. Update any dependent projects

## Post-Archive
- Workspace should not be modified
- Read access only for reference
- Delete after retention period (if applicable)
"""


def get_lite_test_example() -> str:
    """Generate example test for Lite tier (optional, for learning)."""
    return """#!/usr/bin/env python3
\"\"\"Example test for reference - Lite tier doesn't require testing.
To enable testing, upgrade to Standard tier with: python bootstrap.py --upgrade ./
\"\"\"
import sys
sys.path.insert(0, 'src')

from main import main

def test_main_runs():
    \"\"\"Verify main function executes without errors.\"\"\"
    try:
        main()
        assert True
    except Exception as e:
        assert False, f"Main function raised: {e}"

if __name__ == "__main__":
    test_main_runs()
    print("✅ Basic test passed")
"""


def get_standard_unit_test_example(pkg_name: str) -> str:
    """Generate example unit test for Standard tier."""
    return f"""\"\"\"Test suite for {pkg_name}.

Run with: pytest tests/unit/
\"\"\"
import pytest
from src.{pkg_name}.main import main

def test_main_function_exists():


def test_main_runs():
    \"\"\"Verify main function executes without errors.\"\"\"
    try:
        result = main()
        assert result is not None or result is None  # Just verify it runs
    except Exception as e:
        pytest.fail(f"main() raised {{e}}")

# Add more tests as your code grows
# Example:
# def test_specific_function():
#     assert my_function(input) == expected_output
"""


def get_standard_integration_test_example(pkg_name: str) -> str:
    """Generate example integration test for Standard tier."""
    return f"""\"\"\"Integration tests for {pkg_name}.

Tests that verify multiple components work together.
Run with: pytest tests/integration/
\"\"\"
import pytest

def test_end_to_end_flow():
    \"\"\"Test complete workflow from input to output.\"\"\"
    # Example: Test file processing pipeline
    # 1. Create test input
    # 2. Run processing
    # 3. Verify output
    pass  # Replace with actual integration test

@pytest.mark.slow
def test_external_api_integration():
    \"\"\"Test integration with external services.
    
    Mark as slow to skip in fast test runs: pytest -m "not slow"
    \"\"\"
    pass  # Replace with actual API integration test
"""


def get_enterprise_eval_test_example(pkg_name: str) -> str:
    """Generate example eval test for Enterprise tier."""
    return f"""\"\"\"Agent capability evaluation tests for {pkg_name}.

Tests multi-agent coordination and domain isolation.
Run with: pytest tests/evals/
\"\"\"
import pytest
import json
from pathlib import Path

def test_contract_validation():
    \"\"\"Verify inter-domain contracts are valid JSON schemas.\"\"\"
    contracts_dir = Path("outputs/contracts")
    if contracts_dir.exists():
        for contract_file in contracts_dir.glob("*.schema.json"):
            with open(contract_file) as f:
                schema = json.load(f)
            assert "$schema" in schema or "type" in schema

def test_domain_isolation():
    \"\"\"Verify domains don't have circular imports.\"\"\"
    # Check frontend doesn't import backend directly
    frontend_files = Path(f"src/{pkg_name}/domains/frontend").glob("**/*.py")
    for file in frontend_files:
        content = file.read_text()
        assert "from ..backend" not in content, \\
            f"{{file}} imports backend directly - use contracts instead"

def test_agent_handoff():
    \"\"\"Verify shift reports contain required information.\"\"\"
    # This would test the shift_report.py output
    pass  # Implement based on shift report spec
"""


def get_adr_template() -> str:
    """Generate ADR template for Enterprise tier."""
    return """# ADR-XXXX: [Title]

**Date:** YYYY-MM-DD  
**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-YYYY]  
**Deciders:** [List decision makers]

## Context

[Describe the forces at play, including technological, political, social, and project constraints. You may want to include:
- The issue we're trying to solve
- Why this decision is important
- What alternatives were considered]

## Decision

[Clearly state the decision that was made.  
"We will..." format works well.]

## Consequences

### Positive

- [What improves]
- [What becomes easier]
- [What new capabilities we gain]

### Negative

- [What becomes harder]
- [What we give up]
- [Technical debt or trade-offs]

### Neutral

- [Things that change but aren't strictly better or worse]

## Notes

[Optional: Additional context, links to discussions, related ADRs, implementation notes]
"""


def get_gitleaks_config() -> str:
    """Generate .gitleaks.toml configuration for secret scanning."""
    return """# Gitleaks configuration for Gemini Workspace
# Scans for hardcoded secrets, API keys, and credentials

title = "Gitleaks Config"

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '(?i)(api[_-]?key|apikey)[\\s]*[=:][\\s]*['"\\"`]?[a-z0-9]{20,}['"\\"`]?'
tags = ["api", "key"]

[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'
tags = ["aws", "access-key"]

[[rules]]
id = "github-token"
description = "GitHub Token"
regex = 'ghp_[0-9a-zA-Z]{36}'
tags = ["github", "token"]

[[rules]]
id = "generic-secret"  
description = "Generic Secret"
regex = '(?i)(secret|password|passwd|pwd)[\\s]*[=:][\\s]*['"\\"`][^'"\\"`]{8,}['"\\"`]'
tags = ["secret", "password"]

[[rules]]
id = "private-key"
description = "Private Key"
regex = '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
tags = ["key", "private"]

# Allowlist for test fixtures and examples
[allowlist]
paths = [
  "tests/fixtures/*",
  "**/test_*.py",
  "**/*_test.py",
]

regexes = [
  "example|fake|mock|dummy|test",
]
"""