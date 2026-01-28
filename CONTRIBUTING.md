# Contributing to Bootstrap Script

Thank you for your interest in contributing to the Gemini Native Workspace Bootstrap Script!

This document provides guidelines for developing and maintaining the modular source code that compiles into the single-file `bootstrap.py` distribution.

---

## Quick Start (5 Minutes)

### 1. Build the Script

```bash
cd /srv/data/workspaces/source-workspace
make build
```

This compiles the 8 Python modules into `../bootstrap.py`.

### 2. Test It

```bash
python3 ../bootstrap.py --version
# Expected: Gemini Bootstrap v2026.26

python3 ../bootstrap.py --run-self-tests
# Expected: ✅ All self-tests passed
```

### 3. Read the Docs

- **README.md** - Overview of the modular architecture
- **docs/architecture.md** - System design with diagrams
- **docs/development.md** - Detailed development guide

---

## Development Workflow

### Making Changes

1. **Edit modules** in the appropriate file:
   - `config.py` - Constants, tier definitions, exit codes
   - `core.py` - Exceptions, validators, utilities
   - `operations/create.py` - Workspace CRUD operations
   - Other modules as needed

2. **Rebuild**:
   ```bash
   make build
   ```

3. **Test the compiled output**:
   ```bash
   python3 ../bootstrap.py --version
   python3 ../bootstrap.py --run-self-tests
   ```

4. **Lint your code**:
   ```bash
   make lint    # Check code quality
   make format  # Auto-format
   ```

5. **Commit your changes**:
   ```bash
   git add -A
   git commit -m "Description of changes"
   ```

---

## Adding a New Module

If you need to add a new module (e.g., a new provider or operation):

### 1. Create the Module File

```bash
# Choose appropriate directory
touch providers/new_provider.py
# or
touch operations/new_operation.py
```

### 2. Follow Module Guidelines

- **Target:** <500 lines per module (flexible for complex logic)
- **Imports:** Use absolute imports from standard library
  - ✅ `from pathlib import Path`
  - ✅ `import json`
  - ❌ Avoid `from bootstrap_src.*` (these are stripped during build)
- **Type hints:** Use modern Python 3.10+ syntax
- **Docstrings:** Include clear documentation

### 3. Update build.py

Add your module to the `module_order` list in **dependency order**:

```python
# build.py (around line 97)
module_order = [
    Path("config.py"),                # Always first
    Path("core.py"),                  # Always second
    # ... existing modules ...
    Path("your_new_module.py"),       # Add here
    Path("__main__.py"),              # Always last
]
```

### 4. Rebuild and Test

```bash
make build
python3 ../bootstrap.py --version
```

---

## Testing

### Manual Testing

Create test workspaces to verify functionality:

```bash
cd /tmp  # Use system temp, not repo

# Test Tier 1 (Lite)
python3 /srv/data/workspaces/bootstrap.py -t 1 -n test-lite -y
cd test-lite && make audit && cd ..
rm -rf test-lite

# Test Tier 2 (Standard)
python3 /srv/data/workspaces/bootstrap.py -t 2 -n test-standard -y
cd test-standard && make audit && cd ..
rm -rf test-standard

# Test Tier 3 (Enterprise)
python3 /srv/data/workspaces/bootstrap.py -t 3 -n test-enterprise -y
cd test-enterprise && make audit && cd ..
rm -rf test-enterprise
```

### Automated Testing (Planned)

```bash
make test  # When pytest suite is implemented
```

See **docs/development.md** for comprehensive testing procedures.

---

## Releasing a New Version

### 1. Update Version

```bash
vim config.py
# Change: VERSION = "2026.XX"  # Increment as needed
```

Also update version references in:
- `README.md`
- `docs/roadmap.md`

### 2. Quality Checks

```bash
make lint    # Must pass
make build   # Must succeed
```

### 3. Functional Testing

```bash
# Test version
python3 ../bootstrap.py --version

# Run self-tests
python3 ../bootstrap.py --run-self-tests

# Create test workspaces (all 3 tiers)
# See "Testing" section above
```

### 4. Commit and Tag

```bash
git add -A
git commit -m "Release v2026.XX

- Feature: [description]
- Fix: [description]
"

git tag -a v2026.XX -m "Release v2026.XX"
git push origin main --tags
```

### 5. Distribute

```bash
# Copy to distribution location
cp ../bootstrap.py /path/to/distribution/bootstrap-v2026.XX.py
```

See **docs/development.md** for detailed release procedures.

---

## Common Tasks

### Debugging Build Issues

If `make build` fails:

1. **Check module paths:**
   ```bash
   # Verify all modules in build.py exist
   ls -la config.py core.py operations/create.py
   ```

2. **Look for import errors:**
   - Build script strips `from bootstrap_src.*` imports
   - Ensure external imports (`import json`, etc.) are at module top level

3. **Check module order:**
   - Dependencies must come before dependents
   - `config.py` first, `__main__.py` last

See **docs/development.md** for comprehensive debugging guide.

### Updating Documentation

When adding features:

```bash
# Update module documentation
vim docs/architecture.md
vim docs/development.md

# Update backlog
vim docs/roadmap.md
```

---

## Code Standards

### Style

- **Formatting:** Use `ruff format .`
- **Linting:** Use `ruff check .`
- **Line length:** 88 characters (ruff default)
- **Imports:** Sorted and grouped (stdlib, third-party, local)

### Module Size

- **Target:** <500 lines per module
- **Acceptable:** Up to ~700 lines for complex generators
- **Action needed:** >700 lines - consider refactoring

Current status: 5/8 modules under 500 lines ✅

### Documentation

- **Module docstrings:** Required for all modules
- **Function docstrings:** Required for public functions
- **Type hints:** Required for function signatures
- **Comments:** Explain "why", not "what"

---

## Directory Structure

```
source-workspace/
├── README.md              # Project overview
├── CONTRIBUTING.md        # This file
├── Makefile               # Build automation
├── .gitignore             # VCS hygiene
│
├── build.py               # Compilation script
├── config.py              # Constants
├── core.py                # Exceptions, utilities
├── content_generators.py  # Content generation
├── __main__.py            # CLI entry point
│
├── core/
│   ├── makefile.py        # Makefile generation
│   └── templates.py       # Template generation
│
├── operations/
│   └── create.py          # Workspace CRUD
│
├── providers/
│   └── base.py            # LLM provider interface
│
└── docs/
    ├── architecture.md    # System design
    ├── development.md     # Development guide
    ├── roadmap.md         # Backlog
    └── tools_reference.md # Module reference
```

---

## Getting Help

- **Architecture questions:** See `docs/architecture.md`
- **Development procedures:** See `docs/development.md`
- **Module reference:** See `docs/tools_reference.md`
- **Roadmap/backlog:** See `docs/roadmap.md`

---

## Tips for Success

### ✅ Do

- Run `make build` after every change
- Test the compiled `bootstrap.py`, not just the modules
- Run `make lint` before committing
- Update documentation when adding features
- Use `/tmp` for test workspaces (keeps repo clean)

### ❌ Don't

- Edit `../bootstrap.py` directly (changes will be overwritten)
- Add modules without updating `build.py`
- Create test workspaces in the repo directory
- Hard-code paths or secrets in source code
- Skip the build step when testing changes

---

## Next Steps

After reading this guide:

1. **Try building:** `make build`
2. **Test the output:** `python3 ../bootstrap.py --version`
3. **Read architecture docs:** `docs/architecture.md`
4. **Make a small change:** Add a comment, rebuild, test
5. **Check the roadmap:** `docs/roadmap.md` for contribution ideas

---

**Questions?** Check the `docs/` directory or open an issue.

*Last updated: 2026-01-28*
