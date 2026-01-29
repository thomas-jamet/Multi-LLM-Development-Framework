# ==============================================================================
# ⚙️  SYSTEM CONFIGURATION
# ==============================================================================
.DEFAULT_GOAL := help
SHELL         := /bin/bash
.SHELLFLAGS   := -eu -o pipefail -c
MAKEFLAGS     += --warn-undefined-variables
MAKEFLAGS     += --no-builtin-rules

.PHONY: build test lint format clean help audit status install check-ruff \
        onboard

# ==============================================================================
# 🔧 TOOLS & INTERPRETERS
# ==============================================================================
PYTHON := python3
RUFF   := ruff

# ==============================================================================
# 🎨 BRANDING & COLORS
# ==============================================================================
BLUE   := \033[1;34m
GREEN  := \033[1;32m
YELLOW := \033[1;33m
RED    := \033[1;31m
NC     := \033[0m  # No Color

# ==============================================================================
# 🔨 BUILD & COMPILATION
# ==============================================================================

build: ## Compile modular source → bootstrap.py
	@echo "$(BLUE)🔨 Building bootstrap.py...$(NC)"
	@$(PYTHON) build.py
	@echo "$(GREEN)✅ Build complete: ../bootstrap.py$(NC)"

clean: ## Remove build artifacts and caches
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -f ../bootstrap.py 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

# ==============================================================================
# 🧪 QUALITY & TESTING
# ==============================================================================

check-ruff: ## Check if ruff is installed
	@command -v $(RUFF) >/dev/null 2>&1 || { \
		echo "$(RED)❌ ruff not found. Install with: pip install ruff$(NC)"; \
		exit 1; \
	}

lint: check-ruff ## Run code quality checks (ruff + mypy)
	@echo "$(BLUE)🔍 Running linter...$(NC)"
	@$(RUFF) check .
	@$(RUFF) format --check .
	@echo "$(GREEN)✅ Linting passed$(NC)"
	@if command -v mypy > /dev/null 2>&1; then \
		echo "$(BLUE)🔍 Running type checker...$(NC)"; \
		mypy .; \
		echo "$(GREEN)✅ Type checking passed$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  mypy not installed. Install with: pip install mypy$(NC)"; \
	fi

format: check-ruff ## Auto-format code (ruff)
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	@$(RUFF) format .
	@echo "$(GREEN)✅ Code formatted$(NC)"

test: ## Run test suite
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v; \
	else \
		echo "$(YELLOW)⚠️  pytest not installed. Install with: pip install pytest$(NC)"; \
		echo "$(BLUE)ℹ️  Running manual verification instead:$(NC)"; \
		$(PYTHON) ../bootstrap.py --version && \
		$(PYTHON) ../bootstrap.py --run-self-tests; \
	fi

# ==============================================================================
# 🏥 WORKSPACE HEALTH
# ==============================================================================

audit: ## Validate workspace structure
	@echo "$(BLUE)🔍 Auditing workspace structure...$(NC)"
	@echo ""
	@echo "$(YELLOW)Core Files (Standard Dev Repo):$(NC)"
	@test -f README.md && echo "  $(GREEN)✅$(NC) README.md" || echo "  $(RED)❌$(NC) README.md"
	@test -f CONTRIBUTING.md && echo "  $(GREEN)✅$(NC) CONTRIBUTING.md" || echo "  $(RED)❌$(NC) CONTRIBUTING.md"
	@test -f Makefile && echo "  $(GREEN)✅$(NC) Makefile" || echo "  $(RED)❌$(NC) Makefile"
	@test -f .gitignore && echo "  $(GREEN)✅$(NC) .gitignore" || echo "  $(RED)❌$(NC) .gitignore"
	@echo ""
	@echo "$(YELLOW)Source Modules:$(NC)"
	@test -f config.py && echo "  $(GREEN)✅$(NC) config.py" || echo "  $(RED)❌$(NC) config.py"
	@test -f core.py && echo "  $(GREEN)✅$(NC) core.py" || echo "  $(RED)❌$(NC) core.py"
	@test -f build.py && echo "  $(GREEN)✅$(NC) build.py" || echo "  $(RED)❌$(NC) build.py"
	@test -d core && echo "  $(GREEN)✅$(NC) core/" || echo "  $(RED)❌$(NC) core/"
	@test -d operations && echo "  $(GREEN)✅$(NC) operations/" || echo "  $(RED)❌$(NC) operations/"
	@test -d providers && echo "  $(GREEN)✅$(NC) providers/" || echo "  $(RED)❌$(NC) providers/"
	@echo ""
	@echo "$(YELLOW)Documentation:$(NC)"
	@test -d docs && echo "  $(GREEN)✅$(NC) docs/" || echo "  $(RED)❌$(NC) docs/"
	@test -f docs/architecture.md && echo "  $(GREEN)✅$(NC) docs/architecture.md" || echo "  $(RED)❌$(NC) docs/architecture.md"
	@test -f docs/development.md && echo "  $(GREEN)✅$(NC) docs/development.md" || echo "  $(RED)❌$(NC) docs/development.md"
	@test -f docs/tools_reference.md && echo "  $(GREEN)✅$(NC) docs/tools_reference.md" || echo "  $(RED)❌$(NC) docs/tools_reference.md"
	@echo ""
	@echo "$(GREEN)✅ Audit complete$(NC)"

status: ## Show workspace health dashboard
	@echo ""
	@echo "$(BLUE)📊 Bootstrap Source Workspace$(NC)"
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"
	@echo "  $(YELLOW)Workspace:$(NC) source-workspace"
	@echo "  $(YELLOW)Purpose:$(NC)   Bootstrap Script Development"
	@echo "  $(YELLOW)Version:$(NC)   2026.26"
	@echo ""
	@echo "  $(YELLOW)Modules:$(NC)   8 Python files (3,683 LOC)"
	@echo "  $(YELLOW)Build:$(NC)     Modular Source → Single File"
	@echo ""
	@if [ -f ../bootstrap.py ]; then \
		echo "  $(YELLOW)Status:$(NC)    $(GREEN)✅ bootstrap.py compiled$(NC)"; \
	else \
		echo "  $(YELLOW)Status:$(NC)    $(RED)❌ bootstrap.py missing (run 'make build')$(NC)"; \
	fi
	@echo "$(BLUE)════════════════════════════════════════════════════════════$(NC)"
	@echo ""

onboard: status ## First-run experience for new contributors
	@echo "$(GREEN)🎓 Welcome to Bootstrap Source Workspace!$(NC)"
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  1. Build the bootstrap: $(BLUE)make build$(NC)"
	@echo "  2. Test it:             $(BLUE)python ../bootstrap.py --version$(NC)"
	@echo "  3. Read the docs:       $(BLUE)cat docs/development.md$(NC)"
	@echo ""
	@echo "$(YELLOW)Essential Commands:$(NC)"
	@echo "  $(GREEN)make build$(NC)   - Compile modular source"
	@echo "  $(GREEN)make lint$(NC)    - Check code quality"
	@echo "  $(GREEN)make test$(NC)    - Run tests"
	@echo "  $(GREEN)make help$(NC)    - Show all commands"
	@echo ""

# ==============================================================================
# 📦 DEPENDENCIES
# ==============================================================================

install: ## Install development dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@if [ -f pyproject.toml ]; then \
		pip install -e .; \
	else \
		echo "$(YELLOW)⚠️  No pyproject.toml found$(NC)"; \
		echo "$(BLUE)ℹ️  Install ruff manually: pip install ruff$(NC)"; \
	fi

# ==============================================================================
# 📚 HELP
# ==============================================================================

help: ## Show categorized help manual
	@echo ""
	@echo "$(BLUE)🛠️  Bootstrap Source Workspace - Command Manual$(NC)"
	@echo ""
	@awk 'BEGIN { \
		FS = ":.*##"; \
		section = ""; \
	} \
	/^# ===+ .*===+$$/ { \
		match($$0, /# ===+ (.+) ===+/, arr); \
		if (arr[1] != "") { \
			gsub(/^[[:space:]]+|[[:space:]]+$$/, "", arr[1]); \
			section = arr[1]; \
			printf "\n$(YELLOW)%s$(NC)\n", section; \
		} \
		next; \
	} \
	/^[a-zA-Z_-]+:.*?## / { \
		split($$0, a, ":"); \
		cmd = a[1]; \
		split($$0, b, "## "); \
		msg = b[2]; \
		printf "  $(GREEN)%-18s$(NC) %s\n", cmd, msg; \
	}' $(MAKEFILE_LIST)
	@echo ""
