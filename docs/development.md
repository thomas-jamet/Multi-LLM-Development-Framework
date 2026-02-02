# Development Guide

Comprehensive guide for developing and maintaining the Bootstrap Script source code.

---

## Table of Contents

- [Adding Modules](#adding-modules)
- [Debugging Build Issues](#debugging-build-issues)
- [Testing Procedures](#testing-procedures)
- [Release Process](#release-process)

---

## Adding Modules

### When to Add a Module

Add a new module when:
- Existing modules exceed 700 lines (refactor needed)
- New functional domain is introduced (e.g., new provider type)
- Separation of concerns would improve maintainability

### Step-by-Step Process

1. **Create the file** in the appropriate directory
2. **Write the code** following module guidelines (<500 lines target)
3. **Update `build.py`** - Add to `module_order` list in dependency order
4. **Test build:** `make build`
5. **Verify output:** `python3 ../bootstrap.py --version`
6. **Update docs:** Add to `docs/tools_reference.md`

### Common Pitfalls

**Import Errors After Build:**
- Problem: Module imports aren't working in compiled output
- Cause: Internal imports (`from bootstrap_src.*`) not stripped, or external imports missing
- Solution: Ensure external imports are at module top level; check `build.py` import stripping logic

**Duplicate Definitions:**
- Problem: Build fails with "X already defined"
- Solution: Remove duplicate constants/classes; use those from `config.py`

**Module Too Large:**
- Problem: Module exceeds 1000 lines
- Solution: Split into sub-modules within a directory, update `build.py` accordingly

---

## Debugging Build Issues

### Quick Diagnosis

```bash
python3 build.py 2>&1 | tee build.log
echo $?  # 0 = success
```

### Common Failures

#### 1. Missing Module Error

```
❌ Missing module: path/to/module.py
```

**Fix:** Module listed in `build.py` doesn't exist - check path or remove from `module_order`

#### 2. Import Stripping Errors

```python
# In compiled bootstrap.py
ImportError: No module named 'bootstrap_src'
```

**Fix:** Build script failed to strip internal imports - verify stripping logic in `build.py`

#### 3. NameError at Runtime

```python
NameError: name 'ValidationError' is not defined
```

**Fix:** Module using `ValidationError` comes before `core.py` - reorder in `module_order`

#### 4. Module Order Dependencies

**Symptom:** Build succeeds but runtime crashes with import/name errors

**Fix:** Ensure dependency order:
1. `config.py` (no dependencies)
2. `core.py` (depends on config)
3. Domain modules (providers/, core/, operations/)
4. `__main__.py` (depends on everything)

### Debugging Workflow

1. **Isolate:** `make clean && make build`
2. **Check syntax:** `python3 -m py_compile module.py` for each module
3. **Verify build script:** `python3 -m py_compile build.py`
4. **Inspect output:** Check `../bootstrap.py` for obvious issues
5. **Bisect:** Comment out recently added modules to find culprit

---

## Testing Procedures

### Quick Verification (3 steps)

```bash
make build
python3 ../bootstrap.py --version
python3 ../bootstrap.py --run-self-tests
```

### Comprehensive Testing

#### Test 1-4: Basic Functions

```bash
# Version check
python3 ../bootstrap.py --version
# Expected: Multi-LLM Development Framework v1.0.1

# Self-tests
python3 ../bootstrap.py --run-self-tests
# Expected: ✅ All tests pass

# Help display
python3 ../bootstrap.py --help
# Expected: Usage information

# List templates
python3 ../bootstrap.py --list-templates
# Expected: List of available templates
```

#### Test 5-7: Workspace Creation

```bash
cd /tmp

# Tier 1 (Lite)
python3 ../bootstrap.py -t 1 -n test-lite -y
cd test-lite && make audit && cd ..
rm -rf test-lite

# Tier 2 (Standard)
python3 ../bootstrap.py -t 2 -n test-std -y
cd test-std && make audit && make test && cd ..
rm -rf test-std

# Tier 3 (Enterprise)
python3 ../bootstrap.py -t 3 -n test-ent -y
cd test-ent && make audit && cd ..
rm -rf test-ent
```

#### Test 8: Template Application

```bash
python3 ../bootstrap.py -t 2 -n test-fastapi --from-template fastapi -y
cd test-fastapi
grep -q "from fastapi import FastAPI" src/test_fastapi/main.py && echo "✅ Template applied"
cd .. && rm -rf test-fastapi
```

#### Test 9: Workspace Validation

```bash
python3 ../bootstrap.py -t 2 -n test-validate -y
python3 ../bootstrap.py --validate test-validate
# Expected: Validation passes
rm -rf test-validate
```

#### Test 10: Workspace Upgrade

```bash
python3 ../bootstrap.py -t 1 -n test-upgrade -y
python3 ../bootstrap.py --upgrade test-upgrade -t 2 -y
cd test-upgrade
grep '"tier": "2"' .gemini/workspace.json && echo "✅ Upgraded"
cd .. && rm -rf test-upgrade
```

### Automated Test Script

Create `/tmp/test-bootstrap.sh`:

```bash
#!/bin/bash
set -e

echo "🧪 Running Bootstrap Test Suite..."

# Basic tests
python3 ../bootstrap.py --version
python3 ../bootstrap.py --run-self-tests

# Workspace creation
for tier in 1 2 3; do
    python3 ../bootstrap.py -t $tier -n test-t$tier -y
    cd test-t$tier && make audit && cd ..
    rm -rf test-t$tier
done

echo "✅ All tests passed!"
```

---

## Release Process

### Pre-Release Checklist

- [ ] All planned features implemented
- [ ] Critical bugs resolved
- [ ] Code passes `make lint`
- [ ] Documentation updated

### Release Steps

#### 1. Version Bump

```bash
vim config.py
# Update: VERSION = "2026.XX"

vim README.md
# Update version references

vim docs/roadmap.md
# Move completed items, update version history
```

#### 2. Quality Checks

```bash
make lint    # Must pass
make clean
make build   # Must succeed
```

#### 3. Functional Testing

Run comprehensive test suite (see Testing Procedures above).

#### 4. Build Verification

```bash
# Check file size
ls -lh ../bootstrap.py
# Expected: ~180-220KB

# Verify content
python3 ../bootstrap.py --version
# Expected: Shows new version

python3 ../bootstrap.py --run-self-tests
# Expected: All pass
```

#### 5. Commit and Tag

```bash
git add -A
git commit -m "Release v2026.XX

- Feature: [description]
- Fix: [description]
- Update: [description]
"

git tag -a v2026.XX -m "Release v2026.XX

Major changes:
- [Feature]
- [Fix]
"

git push origin main --tags
```

#### 6. Distribution

```bash
# Create versioned copy
cp ../bootstrap.py ../bootstrap-v2026.XX.py

# Distribute to deployment location
cp ../bootstrap.py /path/to/distribution/
```

### Post-Release

- Monitor for issues
- Update changelog
- Gather feedback

### Hotfix Process

For critical bugs:

```bash
# Increment version (e.g., 1.0.1 → 1.0.2)
vim config.py

# Fix bug in affected module
vim [module].py

# Fast-track release
make build
python3 ../bootstrap.py --run-self-tests
git commit -m "Hotfix v2026.XX: [description]"
git tag v2026.XX
git push origin main --tags
```

---

## Build System Internals

### How build.py Works

1. **Read modules** in `module_order` (dependency-sorted)
2. **Strip internal imports** (`from bootstrap_src.*`, `from .`)
3. **Preserve external imports** (`import json`, `from pathlib import Path`)
4. **Concatenate** with module separator comments
5. **Write output** to `../bootstrap.py`
6. **Make executable** (`chmod +x`)

### Import Stripping Logic

```python
def should_strip_import(line: str) -> bool:
    # Strip internal package imports
    if "from bootstrap_src." in line:
        return True

    # Strip relative imports
    if line.startswith("from ."):
        return True

    # Preserve everything else
    return False
```

### Module Order Rules

- `config.py` **first** - defines constants
- `core.py` **second** - base exceptions, validators
- Domain modules - in dependency order
- `__main__.py` **last** - CLI entry point

---

## Code Quality Standards

### Metrics Targets

- **Module size:** <500 lines (target), <700 acceptable
- **Test coverage:** 80%+ (when tests implemented)
- **Linting:** Zero errors
- **Type hints:** All public functions

### Current Status

- Modules: 8
- Total lines: 3,683 (modular source)
- Compiled lines: 3,515 (bootstrap.py)
- Test coverage: 0% (to be implemented)
- Modules <500 lines: 5/8 (62.5%)

---

## Tier-Specific Script Organization

### Overview

The bootstrap generates different script directory structures based on the workspace tier:

**Tier 1 (Lite):** Flat structure
```
scripts/
├── check_status.py
├── index_docs.py
├── list_skills.py
├── manage_session.py
├── manage_skills.py
└── run_audit.py
```

**Tier 2 (Standard):** Categorized structure
```
scripts/
├── workspace/
│   ├── check_status.py
│   ├── create_snapshot.py
│   ├── manage_session.py
│   └── run_audit.py
├── skills/
│   ├── explore_skills.py
│   ├── list_skills.py
│   └── manage_skills.py
└── docs/
    └── index_docs.py
```

**Tier 3 (Enterprise):** Domain-based structure
```
scripts/
└── shared/           # Default domain
    ├── check_status.py
    ├── create_snapshot.py
    ├── explore_skills.py
    ├── index_docs.py
    ├── list_skills.py
    ├── manage_session.py
    ├── manage_skills.py
    └── run_audit.py
```

### Implementation

The `_script_path(tier, script_name)` helper function in `core/makefile.py` abstracts tier-specific path resolution:

```python
def _script_path(tier: str, script_name: str) -> str:
    """Get tier-specific path for a script."""
    if tier == "1":
        return f"scripts/{script_name}.py"
    elif tier == "2":
        # Look up category from SCRIPT_CATEGORIES
        for cat, scripts in SCRIPT_CATEGORIES["2"].items():
            if script_name in scripts:
                return f"scripts/{cat}/{script_name}.py"
        return f"scripts/{script_name}.py"
    else:  # tier == "3"
        # Look up domain from SCRIPT_CATEGORIES
        for cat, scripts in SCRIPT_CATEGORIES["3"].items():
            if script_name in scripts:
                return f"scripts/{cat}/{script_name}.py"
        return f"scripts/shared/{script_name}.py"
```

### Makefile Generation

Both tier-specific targets and common targets use `_script_path()` to ensure correct paths:

```python
# Tier-specific targets
def _get_makefile_tier_targets(tier: str, project_name: str) -> str:
    # Uses explicit paths with tier-specific logic

# Common targets (shared across all tiers)
def _get_makefile_common_targets(tier: str = "1") -> str:
    # Build script path variables
    sp_audit = _script_path(tier, "run_audit")
    sp_session = _script_path(tier, "manage_session")

    # Use string concatenation to avoid f-string backslash issues
    return """
audit: ## Validate workspace structure
\t@python3 """ + sp_audit + """
"""
```

### Adding New Scripts

When adding a new script to the bootstrap:

1. **Update `SCRIPT_CATEGORIES` in `config.py`**:
   ```python
   SCRIPT_CATEGORIES = {
       "2": {
           "workspace": ["run_audit", "manage_session", "new_script"],
           # ...
       }
   }
   ```

2. **Create the template in `core/templates.py`**:
   ```python
   def get_new_script() -> str:
       return """#!/usr/bin/env python3
   # Script content
   """
   ```

3. **Update script generation in `operations/create.py`**:
   ```python
   script_generators = [
       ("new_script", get_new_script),
       # ...
   ]
   ```

4. **Add Makefile target using `_script_path()`**:
   ```python
   sp_new_script = _script_path(tier, "new_script")
   # Then use: """ + sp_new_script + """
   ```

---

**Last Updated:** 2026-01-29
