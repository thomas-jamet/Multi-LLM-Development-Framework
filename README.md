# Bootstrap Source - Modular Architecture

This directory contains the modular source code for the Gemini Native Workspace Bootstrap Script.

## 📁 Structure

```
bootstrap_src/
├── build.py                    # Build script (compiles modules → bootstrap.py)
├── config.py                   # Constants, tier definitions, exit codes
├── core.py                     # Exceptions, utilities, validators
├── content_generators.py       # Content generation functions
├── __main__.py                 # CLI parsing and main() entry point
├── core/                       # Core functionality
│   ├── makefile.py            # Makefile generation
│   └── templates.py           # Template generation (11 functions)
├── operations/                 # Workspace operations
│   └── create.py              # Create, validate, upgrade, rollback
└── providers/                  # LLM provider abstraction
    └── base.py                # Provider interface

8 modules • 3,683 lines → compiles to 4,187-line bootstrap.py
```

## 🔨 Building

Compile the modular source into a single distributable file:

```bash
python build.py
```

This creates `bootstrap.py` in the parent directory with:
- All external imports preserved
- Internal imports stripped
- Modules concatenated in dependency order
- Build metadata header

## 📝 Module Guidelines

- **Target size**: < 500 lines per module (flexible for complex modules)
- **Naming**: Clear, descriptive names following Python conventions
- **Dependencies**: Core modules first, operations last
- **Imports**: Use absolute imports; avoid `from bootstrap_src.*`

## 🧪 Development Workflow

1. **Edit modules** in `bootstrap_src/`
2. **Run build script**: `python build.py`
3. **Test output**: `python ../bootstrap.py --version`
4. **Verify functionality**: Test workspace creation, validation, etc.

## 📊 Module Responsibilities

| Module | Lines | Purpose |
|--------|-------|---------|
| `core.py` | 411 | Base exceptions, logging, validation, utilities |
| `config.py` | 250 | Constants (VERSION, TIERS, EXIT codes, paths) |
| `providers/base.py` | 108 | LLM provider interface (LLM-agnostic design) |
| `core/makefile.py` | 638 | Makefile generation for all tiers |
| `core/templates.py` | 638 | File templates (GEMINI.md, scripts, schemas) |
| `content_generators.py` | 388 | workspace.json, README, getting started |
| `operations/create.py` | 706 | Workspace CRUD operations |
| `__main__.py` | 339 | argparse CLI, main() entry point |

## 🎯 Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Dependency Order**: Core → Config → Providers → Operations → CLI
3. **LLM-Agnostic**: Provider abstraction allows multi-LLM support
4. **Build-Time Compilation**: Users get single file, developers get modules
5. **Backward Compatible**: Compiled output is a drop-in replacement
6. **Tier-Aware Architecture**: Script organization scales from flat (Lite) to categorized (Standard) to domain-based (Enterprise)

## 🔧 Modifying the Build Process

The `build.py` script:
1. Reads modules in `module_order` (line 97)
2. Strips internal imports (`from bootstrap_src.*`, `from .`)
3. Preserves external imports (`import os`, `from pathlib import Path`)
4. Concatenates code with module separator comments
5. Adds build metadata header

To add a new module:
1. Create the module file
2. Add to `module_order` in `build.py` (in dependency order)
3. Rebuild and test

## 📖 Further Reading

- Parent directory walkthrough: `../brain/.../walkthrough.md`
- Task breakdown: `../brain/.../task.md`
- Original monolith: `../docs/knowledge/technical/20260127 - Technical - Gemini - Unified Workspace Bootstrap Script.py`

---

**Built with**: Automated extraction + manual refinement
**Maintainability**: 36% reduction in source lines vs original monolith
**Architecture**: Modular source → Single-file distribution
