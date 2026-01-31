# Multi-LLM Development Framework

A modular, LLM-agnostic framework for building AI-assisted workspaces with consistent structure, reusable skills, and orchestrated workflows.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**[📚 Quick Start](docs/quickstart.md)** | [Documentation](docs/) | [Contributing](CONTRIBUTING.md)

**Author**: [Thomas Jamet](https://www.linkedin.com/in/jamet/)

---

## 🤔 Why This Exists

AI coding assistants excel at generation but provide **no organizational structure**. This leads to:

- **"Vibe coding"** — ad-hoc file creation, no patterns, invisible technical debt
- **Context inefficiency** — AI agents waste cycles asking "where is this file?"
- **Demo vs. reality gap** — "build X in 10 minutes" content ignores 6-month maintenance

**This framework solves the unsolved problem: long-term maintainability of AI-assisted projects.**

### The Difference

| Without Structure | With Framework |
|-------------------|----------------|
| Every project starts from scratch | Predictable patterns across all projects |
| AI searches, asks clarifying questions | AI knows the structure, acts immediately |
| Works for 1 project, fails at 5 | Scales from prototype to portfolio |

> **Structure scales. Chaos doesn't.**

---

## ✨ Features

- **LLM-Agnostic**: Supports Gemini, Claude, and Codex providers
- **Tiered Architecture**: Lite → Standard → Enterprise (matched to project complexity)
- **Skills + Workflows**: Atomic capabilities + orchestrated sequences
- **Built-in Validation**: Health monitoring and structure verification
- **Upgrade System**: Tier upgrades with backup/rollback support

## 🚀 Quick Start

```bash
# Default (Gemini)
python bootstrap.py -t 2 -n myproject

# Claude provider
python bootstrap.py -t 2 -n myproject --provider claude

# Codex provider
python bootstrap.py -t 2 -n myproject --provider codex
```

## 🔌 Supported Providers

| Provider | Config File | Config Dir | Default |
|----------|-------------|------------|---------|
| Gemini | `GEMINI.md` | `.gemini/` | ✓ |
| Claude | `CLAUDE.md` | `.claude/` | |
| Codex | `CODEX.md` | `.codex/` | |

---

## 🎯 Core Principles

1. **Structure Scales, Chaos Doesn't** — Ad-hoc works for 1 project, fails at 3, collapses at 5

2. **Consistency is Cognitive Efficiency** — Same patterns = lower mental overhead

3. **Documentation for Agents, Not Just Humans** — Config files provide AI context, reducing iteration cycles

4. **Maintenance Matters More Than Generation** — Code is written once, modified dozens of times

5. **Tiered Complexity** — Match project structure to actual needs (Lite/Standard/Enterprise)

---

## 📁 Project Structure

```
├── build.py                    # Compiles modules → bootstrap.py
├── config.py                   # Constants, tier definitions
├── core.py                     # Exceptions, utilities, validators
├── __main__.py                 # CLI entry point
├── core/                       # Core functionality
│   ├── makefile.py            # Makefile generation
│   └── templates/             # Template generation
├── operations/                 # Workspace operations
│   └── create.py              # Create, validate, upgrade
└── providers/                  # LLM provider abstraction
    ├── base.py                # Provider interface
    ├── gemini.py              # Gemini implementation
    ├── claude.py              # Claude implementation
    └── codex.py               # Codex implementation
```

## 🔨 Building

```bash
python build.py
```

Creates `bootstrap.py` (~5,300 lines) with all modules concatenated.

---

## 💬 Questions & Contact

- **Discussions**: [GitHub Discussions](https://github.com/thomas-jamet/gemini-workspace-framework/discussions)
- **Issues**: [GitHub Issues](https://github.com/thomas-jamet/gemini-workspace-framework/issues)
- **Author**: [LinkedIn](https://www.linkedin.com/in/jamet/)

**License**: MIT
