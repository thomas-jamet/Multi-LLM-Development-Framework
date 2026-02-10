# Quick Start Guide

Get started with the Multi-LLM Development Framework in 5 minutes.

---

## Prerequisites

- Python 3.11+
- Git
- Basic command line familiarity

---

## Installation

### 1. Download the Bootstrap Script

```bash
# Clone the repository
git clone https://github.com/thomas-jamet/gemini-workspace-framework.git
cd gemini-workspace-framework

# The bootstrap script is ready to use
./bootstrap.py --version
```

### 2. Test It Works

```bash
# List available templates
./bootstrap.py --list-templates

# Show help
./bootstrap.py --help
```

---

## Create Your First Workspace

### Standard Tier (Recommended for Most Projects)

```bash
# Create a new workspace
./bootstrap.py create my-project \
  --tier 2 \
  --provider gemini

# Navigate to your workspace
cd ../my-project
```

### What You Get

Your workspace now has:
- `.agent/skills/` - Reusable capabilities
- `.agent/workflows/` - Orchestrated sequences
- `scripts/` - Automation tools
- `docs/` - Documentation
- `Makefile` - Standardized interface
- `GEMINI.md` - AI context file

---

## Essential Commands

All workspaces use the same Makefile interface:

```bash
# See all available commands
make help

# Start a work session
make session-start

# Check workspace status
make status

# Run workspace audit
make audit

# End session (commits work)
make session-end
```

---

## Your First Workflow

Workflows are defined in `.agent/workflows/`.

**Create a workflow** (`.agent/workflows/hello.md`):

```markdown
---
description: Simple hello world workflow
---

# Hello Workflow

1. Echo a message
2. Create a file
3. Show completion

## Steps

// turbo
echo "Hello from workflow!"

// turbo
echo "Workflow content" > output.txt

// turbo
cat output.txt
```

**Run it** via chat:
```
/hello
```

Or directly:
```bash
make hello
```

---

## Adding a Skill

Skills are reusable capabilities in `.agent/skills/`.

**Create a skill** (`.agent/skills/example/SKILL.md`):

```markdown
---
name: Example Skill
description: Demonstrates skill structure
---

# Example Skill

## Purpose
Show how to create a reusable capability.

## Usage
When the user asks to "demonstrate the example skill", follow these steps.

## Steps
1. Check if file exists
2. Create file if missing
3. Display content
```

Skills provide AI agents with specialized knowledge for specific tasks.

---

## Workspace Tiers

### Lite (Tier 1)
**For:** Simple scripts, utilities
**Has:** Basic structure, minimal overhead

### Standard (Tier 2) ⭐ Recommended
**For:** Most projects
**Has:** Full framework, skills, workflows, documentation

### Enterprise (Tier 3)
**For:** Complex multi-domain systems
**Has:** Domain separation, advanced patterns

---

## Next Steps

### Customize Your Workspace

1. **Edit `GEMINI.md`** - Add workspace-specific context for AI
2. **Create workflows** - Automate common tasks
3. **Add skills** - Build reusable capabilities
4. **Document** - Keep `docs/roadmap.md` updated

### Learn More

- [Workspace Standard](WORKSPACE_STANDARD.md) - Complete specification
- [Framework README](../README.md) - Why this approach and core principles
- [Development Guide](docs/development.md) - Contributing patterns
- [Contributing](CONTRIBUTING.md) - How to contribute

### Example Workspaces

See real-world examples:
- **Docker Management** - Infrastructure automation (Standard)
- **Education Pipeline** - Content processing (Standard)
- **Career Automation** - Multi-domain system (Enterprise)

---

## Common Workflows

### Session Management

```bash
# Start working
make session-start

# Do your work...

# End session (auto-commits)
make session-end
```

### Documentation

```bash
# Generate documentation index
make index

# Update roadmap
vim docs/roadmap.md
```

### Development

```bash
# Run linting
make lint

# Format code
make format

# Run tests (if configured)
make test
```

---

## Troubleshooting

### "Command not found: make"

**Solution**: Install `make`
```bash
# Ubuntu/Debian
sudo apt install build-essential

# macOS (with Homebrew)
brew install make
```

### "Python version too old"

**Solution**: Install Python 3.11+
```bash
# Check version
python3 --version

# Install via package manager or pyenv
```

### "Workspace already exists"

**Solution**: Choose different name or remove existing
```bash
rm -rf ../my-project
./bootstrap.py create my-project --tier 2
```

---

## Best Practices

1. **Start with Standard Tier** - Don't over-engineer
2. **Use session management** - Keeps git clean
3. **Document as you go** - Update `docs/roadmap.md`
4. **Create workflows early** - Automate repetitive tasks
5. **Keep GEMINI.md current** - Helps AI understand context

---

## Getting Help

- **Documentation**: Check `docs/` directory
- **Examples**: See `WORKSPACE_STANDARD.md` patterns
- **Issues**: GitHub issues for bugs/features
- **Philosophy**: See the [README](../README.md) to understand why this approach

---

## What Makes This Different

**Traditional approach:**
- Ad-hoc file organization
- No AI context
- Inconsistent patterns
- Hard to maintain

**Multi-LLM approach:**
- Predictable structure
- AI-optimized documentation
- Reusable patterns
- Sustainable long-term

See the [README](../README.md) for the deeper rationale behind this framework.

---

**Ready to build sustainable AI-assisted projects!** 🚀
