# Bootstrap Source - Module Reference

Quick reference for all modules in the bootstrap source.

---

## config.py (251 lines)

**Purpose:** Central configuration and constants
**Dependencies:** None

### Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `VERSION` | str | Script version ("1.0.0") |
| `EXIT_SUCCESS` | int | Exit code 0 |
| `EXIT_VALIDATION_ERROR` | int | Exit code 1 |
| `EXIT_CREATION_ERROR` | int | Exit code 2 |
| `TIERS` | dict | Tier metadata (Lite, Standard, Enterprise) |
| `TEMPLATES` | dict | Built-in templates (fastapi, cli, scraper, etc.) |
| `DEFAULT_DIRECTORIES` | list | Base directory structure |
| `PHONY_TARGETS` | dict | Makefile targets by tier |
| `GITIGNORE_PATTERNS` | list | .gitignore template |

### Usage Example

```python
from config import VERSION, TIERS

print(f"Bootstrap v{VERSION}")
print(f"Tier 2: {TIERS['2']['name']}")  # "Standard"
```

---

## core.py (411 lines)

**Purpose:** Base exceptions, utilities, and validators
**Dependencies:** `config.py`

### Exception Hierarchy

```
WorkspaceError (base)
├── ValidationError
├── CreationError
├── UpgradeError
├── RollbackError
└── ConfigurationError
```

### Key Functions

#### Validators

- `validate_project_name(name: str)` - Validate project name format
- `validate_tier_upgrade(current, target)` - Prevent downgrades
- `validate_python_version(version)` - Check version format
- `validate_manifest_path(path)` - **Security:** Prevent path traversal
- `validate_rollback_backup(name, path)` - Verify backup exists

#### Utilities

- `success(msg)`, `error(msg)`, `warning(msg)`, `info(msg)` - Colored output
- `header(msg)`, `dim(msg)` - Formatting
- `show_progress(step, total, message)` - Progress bar
- `load_config(path)` - Load .gemini-bootstrap.json

---

## providers/base.py (108 lines)

**Purpose:** LLM provider abstraction
**Dependencies:** `config.py`, `core.py`

### Interface

```python
class LLMProvider:
    """Base interface for LLM providers."""

    def generate(self, prompt: str) -> str:
        """Generate content from prompt."""
        raise NotImplementedError
```

### Future Implementations

- `AnthropicProvider` (Claude)
- `OpenAIProvider` (GPT)
- `GoogleProvider` (Gemini)

---

## core/makefile.py (638 lines)

**Purpose:** Generate Makefiles for all tiers
**Dependencies:** `config.py`

### Main Function

```python
def generate_makefile(tier: str, pkg_name: str) -> str:
    """Generate tier-specific Makefile content."""
    # Returns complete Makefile as string
```

### Tier-Specific Targets

| Tier | Unique Targets |
|------|---------------|
| Lite | `run`, `install` |
| Standard | + `test`, `coverage`, `snapshot` |
| Enterprise | + `eval`, `scan`, `shift-report`, `lock` |

---

## core/templates.py (637 lines)

**Purpose:** Generate file templates
**Dependencies:** `config.py`

### Template Functions

1. `get_gemini_md(tier)` - GEMINI.md constitution
2. `get_audit_script(tier)` - Workspace audit script
3. `get_session_script()` - Session tracking
4. `get_status_script(tier)` - Health dashboard
5. `get_doc_indexer()` - Documentation indexer
6. `get_list_skills_script()` - Skill lister
7. `get_workspace_schema()` - JSON schema for workspace.json
8. `get_settings_schema()` - JSON schema for settings.json
9. `get_ci_workflow(tier, pkg, py_ver)` - GitHub Actions CI
10. `get_pre_commit_config()` - Pre-commit hooks
11. `get_snapshot_script(tier)` - Snapshot/restore (Tiers 2-3)

---

## content_generators.py (387 lines)

**Purpose:** Generate dynamic content
**Dependencies:** `config.py`, `core.py`

### Key Functions

- `get_workspace_json(tier, name, parent)` - workspace.json metadata
- `get_getting_started(tier, pkg)` - Tier-specific quickstart guide
- `get_readme(tier, pkg)` - README template
- `get_roadmap(tier)` - Backlog template
- `get_cheatsheet(tier)` - Commands reference
- `get_archive_workflow()` - Deprecation workflow
- `get_test_sample(tier, pkg)` - Sample test file

---

## operations/create.py (705 lines)

**Purpose:** Workspace CRUD operations
**Dependencies:** All above modules

### Main Functions

#### create_workspace()

```python
def create_workspace(
    name: str,
    tier: str,
    base_path: Path,
    template: str | None = None,
    git: bool = False,
    force: bool = False,
    quiet: bool = False
) -> None:
    """Create new workspace with specified tier."""
```

**Process:**
1. Validate inputs
2. Create directory structure
3. Generate files (Makefile, GEMINI.md, scripts, etc.)
4. Set permissions
5. Initialize git (if requested)
6. Log telemetry (if enabled)

#### validate_workspace()

```python
def validate_workspace(workspace_path: Path) -> None:
    """Validate existing workspace structure."""
```

**Checks:**
- Required files exist (GEMINI.md, Makefile, etc.)
- JSON files valid
- Tier-specific requirements met

#### upgrade_workspace()

```python
def upgrade_workspace(
    workspace_path: Path,
    target_tier: str,
    yes: bool = False
) -> None:
    """Upgrade workspace to higher tier."""
```

**Process:**
1. Validate upgrade path (no downgrades)
2. Create backup in `.gemini/backups/`
3. Add tier-specific directories
4. Update files (Makefile, GEMINI.md, etc.)
5. Update workspace.json

#### rollback_workspace()

```python
def rollback_workspace(
    workspace_path: Path,
    backup_name: str | None = None
) -> None:
    """Restore from backup."""
```

---

## __main__.py (339 lines)

**Purpose:** CLI entry point
**Dependencies:** All modules

### Entry Point

```python
def main() -> int:
    """Main entry point with exception handling."""
    try:
        return _main_impl()
    except WorkspaceError as e:
        error(str(e))
        return EXIT_WORKSPACE_ERROR
    except KeyboardInterrupt:
        return EXIT_INTERRUPT
```

### Argument Parser

```bash
# Creation
python bootstrap.py -t 2 -n myapp

# Validation
python bootstrap.py --validate ./myapp

# Upgrade
python bootstrap.py --upgrade ./myapp -t 3

# Templates
python bootstrap.py -t 2 -n api --from-template fastapi

# Options
python bootstrap.py --help
python bootstrap.py --version
python bootstrap.py --list-templates
python bootstrap.py --run-self-tests
```

---

## build.py (209 lines)

**Purpose:** Build modular source → single file
**Dependencies:** None (standalone build script)

### Algorithm

1. Read `module_order` list
2. For each module:
   - Read source
   - Strip internal imports
   - Preserve external imports
   - Append to output
3. Write to `../bootstrap.py`
4. Make executable

### Module Order

```python
module_order = [
    "config.py",
    "core.py",
    "providers/base.py",
    "core/makefile.py",
    "core/templates.py",
    "content_generators.py",
    "operations/create.py",
    "__main__.py"
]
```

---

## Quick Reference

### Common Tasks

| Task | Module | Function |
|------|--------|----------|
| Validate project name | `core.py` | `validate_project_name()` |
| Generate Makefile | `core/makefile.py` | `generate_makefile()` |
| Create workspace | `operations/create.py` | `create_workspace()` |
| Handle errors | `core.py` | Exception hierarchy |
| Build bootstrap | `build.py` | `main()` |

### File Locations

- **Source:** This repository (`source-workspace/`)
- **Compiled:** `../bootstrap.py`
- **Build Script:** `build.py`
- **Tests:** `tests/` (to be implemented)

---

*Last Updated: 2026-01-28*
