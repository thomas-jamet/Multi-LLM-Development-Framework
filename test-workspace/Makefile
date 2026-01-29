# Gemini Standard Workspace
SHELL := /bin/bash
.PHONY: run test test-watch coverage typecheck install context clean audit session-start session-end init list-skills help snapshot restore doctor status health format update docs lint ci-local deps-check security-scan session-force-end-all onboard backup sync search list-todos index skill-add skill-remove

# ==============================================================================
# 🎨 BRANDING & COLORS
# ==============================================================================
BLUE   := \033[1;34m
GREEN  := \033[1;32m
YELLOW := \033[1;33m
RED    := \033[1;31m
NC     := \033[0m # No Color

# ==============================================================================
# 🚀 APPLICATION ENTRY POINT
# ==============================================================================

# PURPOSE: Execute the main logic of your workspace.
# WHEN: Use this to run your actual software.
run: ## Execute the primary application (src/{project_name}/main.py)
	@echo "$(BLUE)🚀 Launching application...$(NC)"
	@python3 -m src.test_workspace.main

# ==============================================================================
# 🧪 TESTING & QUALITY
# ==============================================================================

# PURPOSE: Validate that your code is bug-free.
# WHEN: Run before finishing every work session.
test: ## Run the full pytest suite in tests/
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@PYTHONPATH=. pytest tests/

# PURPOSE: Continuous test feedback during coding.
test-watch: ## Run tests and re-run on file changes (requires pytest-watch)
	@pytest-watch tests/ || echo \"$(YELLOW)💡 Install pytest-watch: pip install pytest-watch$(NC)\"

# PURPOSE: Check test coverage of your codebase.
coverage: ## Generate a test coverage report (html + terminal)
	@pytest tests/ --cov=src --cov-report=term-missing --cov-report=html || echo \"$(YELLOW)💡 Install pytest-cov: pip install pytest-cov$(NC)\"

# PURPOSE: Lint your code for style and errors.
lint: ## Check for code style and logical errors using ruff
	@echo "$(BLUE)🧹 Linting codebase...$(NC)"
	@ruff check . --fix

# PURPOSE: Automatically format your code.
format: ## Automatically format code (imports, spacing) with ruff
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	@ruff format .

# PURPOSE: Run static type checks to prevent bugs.
typecheck: ## Run static type analysis (mypy or pyright) to catch bugs
	@echo "$(BLUE)🔍 Type checking...$(NC)"
	@command -v mypy >/dev/null 2>&1 && mypy src/ || (command -v pyright >/dev/null 2>&1 && pyright src/ || echo \"$(YELLOW)💡 Install type checker: pip install mypy or pip install pyright$(NC)\")

# ==============================================================================
# 📚 DOCUMENTATION & LLM CONTEXT
# ==============================================================================

# PURPOSE: Export your project's "identity" for a new AI assistant.
# WHEN: Run this at the start of every NEW LLM conversation.
context: ## Export core Rules/Roadmap (GEMINI.md, etc.) for a new LLM conversation
	@echo "$(BLUE)📋 Exporting AI context...$(NC)"
	@for file in $$(cat .gemini/manifests/core); do \
		if [ -f "$$file" ]; then \
			echo "$(GREEN)--- FILE: $$file ---$(NC)"; \
			cat "$$file"; \
			echo ""; \
		fi; \
	done

# PURPOSE: Build viewable documentation site.
docs: ## Build static documentation (HTML) if configured with mkdocs
	@echo "$(BLUE)📚 Generating documentation...$(NC)"
	@command -v mkdocs >/dev/null 2>&1 && mkdocs build || echo \"$(YELLOW)⚠️  mkdocs not found. Install with: pip install mkdocs$(NC)\"

# PURPOSE: Refresh the master index of all documents.
index: ## Regenerate the master Table of Contents in README.md
	@echo "$(BLUE)🗂️  Indexing documentation...$(NC)"
	@python3 scripts/docs/index_docs.py

# ==============================================================================
# 📦 ENVIRONMENT MANAGEMENT
# ==============================================================================

# PURPOSE: Install project and dependencies.
install: ## Install the project in editable mode with dependencies
	@echo "$(BLUE)📦 Installing project dependencies...$(NC)"
	@pip3 install -e .

# PURPOSE: Update software libraries to latest versions.
update: ## Update all dependencies to their latest compatible versions
	@echo "$(BLUE)🔄 Updating dependencies...$(NC)"
	@pip3 install --upgrade -e ".[dev]"

# PURPOSE: Diagnose environment health.
doctor: ## Run environmental diagnostics (Python version, dependencies)
	@echo "$(BLUE)🔍 Checking environment...$(NC)"
	@python3 --version
	@echo "$(BLUE)📦 Checking dependencies...$(NC)"
	@command -v ruff >/dev/null 2>&1 && echo "$(GREEN)✅ ruff available$(NC)" || echo "$(YELLOW)⚠️  ruff not found (run: pip install ruff)$(NC)"
	@echo "$(BLUE)📁 Checking structure...$(NC)"
	@python3 scripts/workspace/run_audit.py

# ==============================================================================
# ⏱️ SESSION MANAGEMENT
# ==============================================================================

# PURPOSE: Tell the system you are starting work.
# WHEN: Run this EVERY TIME you begin a new task.
session-start: ## Begin a tracked work session (optional msg="...")
	@python3 scripts/workspace/manage_session.py start -- "${msg}"

# PURPOSE: finalize your work, runs quality checks, and sync to GitHub (Standard tier).
# WHEN: Run this EVERY TIME you finish a task or want to go home.
session-end: ## Close session: runs lint/tests, commits & pushes (optional msg="...")
	@echo "$(BLUE)📤 Finalizing workspace...$(NC)"
	@echo "$(BLUE)🧹 Linting...$(NC)"
	@$(MAKE) lint || ( echo "$(RED)❌ Linting failed$(NC)" && exit 1 )
	@echo "$(BLUE)🧪 Testing...$(NC)"
	@$(MAKE) test || ( echo "$(RED)❌ Tests failed$(NC)" && exit 1 )
	@python3 scripts/docs/index_docs.py
	@python3 scripts/workspace/run_audit.py
	@$(MAKE) clean
	@if [ -d .git ]; then \
		git add .; \
		if [ -n "$$(git status --porcelain)" ]; then \
			git commit -m "session end: ${msg}"; \
		else \
			echo "$(GREEN)✨ Workspace clean$(NC)"; \
		fi; \
		git push 2>/dev/null || echo "$(YELLOW)⚠️  Push failed$(NC)"; \
	else \
			echo "$(YELLOW)⚠️  Not a git repository$(NC)"; \
	fi
	@python3 scripts/workspace/manage_session.py end -- "${msg}"
	@echo "$(GREEN)✅ Quality checks passed!$(NC)"

# ==============================================================================
# 🛡️ ARCHIVE & BACKUP
# ==============================================================================

# PURPOSE: Create a workspace "Save Point".
# WHEN: Use before major or risky changes.
snapshot: ## Create an immutable local backup of your workspace state
	@if [ -z "$(name)" ]; then echo "$(RED)❌ Error: name=\"...\" is required for snapshot$(NC)" && exit 1; fi
	@python3 scripts/workspace/create_snapshot.py create "${name}"

# PURPOSE: Revert to a previous "Save Point".
restore: ## Revert workspace to a previous snapshot (use name="...")
	@if [ -z "$(name)" ]; then echo "$(RED)❌ Error: name=\"...\" is required for restore$(NC)" && exit 1; fi
	@python3 scripts/workspace/create_snapshot.py restore "${name}" $(if $(yes),--yes,)

# PURPOSE: Standard backup.
backup: snapshot ## Alias for snapshot

# ==============================================================================
# ⚙️ SYSTEM CONFIGURATION
# ==============================================================================
.DEFAULT_GOAL := help
SHELL         := /bin/bash
.SHELLFLAGS   := -eu -o pipefail -c
MAKEFLAGS     += --warn-undefined-variables
MAKEFLAGS     += --no-builtin-rules

# ==============================================================================
# 🔧 TOOLS & INTERPRETERS
# ==============================================================================
PYTHON := python3
RUFF   := ruff
PYTEST := pytest

# ==============================================================================
# 🏥 WORKSPACE HEALTH & LIFECYCLE
# ==============================================================================

# PURPOSE: Emergency stop for stale tasks.
# WHEN: Use this if you forgot to run 'session-end' and things are hung.
session-force-end-all: ## Emergency: force-close any stale or hung sessions
	@python3 scripts/session.py force-end-all

# PURPOSE: The "Start My Day" command.
# WHEN: Run this as your very first action in a new work day.
init: ## Quickstart: starts a session and exports LLM context manifest
	@python3 scripts/session.py start -- "${{msg}}"
	@echo "\n$(BLUE)📋 Exporting Context for LLM...$(NC)"
	@make context

# PURPOSE: The "New User" onboarding flow.
# WHEN: Run this once when you first start using this workspace.
onboard: ## First-run experience: runs status, audit, and diagnostic check
	@echo "\n🚀 Welcome to your Gemini Workspace!"
	@echo "─────────────────────────────────────"
	@python3 scripts/status.py
	@echo "📋 Running health check..."
	@make doctor
	@echo "\n📚 Quick Start:"
	@echo "   1. Run 'make context' and paste output into your LLM"
	@echo "   2. Say: 'I am ready to work on this project'"
	@echo "   3. Run 'make list-skills' to see available capabilities"
	@echo "   4. Check docs/GETTING_STARTED.md for full guide"
	@echo ""

# PURPOSE: Checks that your folders follow the required AI standard.
# WHEN: I run this automatically for you, but you can run it to check health.
audit: ## Validate that workspace structure complies with the standard
	@python3 scripts/audit.py

# PURPOSE: See what special "AI Capabilities" I have in this folder.
# WHEN: Use this to discover new workflows or skills I can perform.
list-skills: ## List the cognitive 'Skills' and 'Workflows' available to agents
	@echo "$(BLUE)🧠 Querying AI capabilities...$(NC)"
	@python3 scripts/list_skills.py

# PURPOSE: Install a new AI capability from a trusted source.
# WHEN: Use this when you need a specialized skill for a specific task.
skill-add: ## Fetch and install a skill (use source="owner/repo/path")
	@if [ -z "$(source)" ]; then echo "$(RED)❌ Error: source=\"...\" is required$(NC)" && exit 1; fi
	@$(PYTHON) scripts/skill_manager.py fetch "$(source)"

# PURPOSE: Remove an AI capability you no longer need.
skill-remove: ## Uninstall a local skill (use name="...")
	@if [ -z "$(name)" ]; then echo "$(RED)❌ Error: name=\"...\" is required$(NC)" && exit 1; fi
	@$(PYTHON) scripts/skill_manager.py remove "$(name)"

# PURPOSE: View your current "Health Score" and workspace status.
# WHEN: Use this to see how much progress you've made today.
status: ## Show a high-level health dashboard and git/session status
	@python3 scripts/status.py

# PURPOSE: Standard health check (alias for doctor).
health: doctor ## Alias for doctor

# PURPOSE: Show the command manual.
# WHEN: Use this whenever you are unsure what to do next.
help: ## Show categorized help manual
	@echo "\n$(BLUE)🛠️  Gemini Workspace Command Manual$(NC)"
	@awk '/^# ===+/ { \
		category = $$0; \
		gsub(/^# =+/, "", category); \
		gsub(/=+/, "", category); \
		if (length(category) > 0) printf "\n$(YELLOW) %s$(NC)\n", category; \
	} \
	/^[a-zA-Z_-]+:.*?## / { \
		split($$0, a, ":"); \
		cmd = a[1]; \
		split($$0, b, "## "); \
		msg = b[2]; \
		printf "  $(GREEN)%-18s$(NC) %s\n", cmd, msg; \
	}' $(MAKEFILE_LIST)
	@echo "\n$(BLUE)Usage Examples:$(NC)"
	@echo "  make session-start [msg='Writing research notes']"
	@echo "  make session-end [msg='Completed Phase 1']"
	@echo "  make snapshot name='pre-refactor'"

# PURPOSE: Sync your local environment with remote changes.
sync: ## Pull latest changes and update dependencies
	@echo "$(BLUE)🔄 Syncing workspace with remote...$(NC)"
	@git pull --rebase 2>/dev/null || echo "$(YELLOW)⚠️  No remote or pull failed$(NC)"
	@$(PYTHON) -m pip install -e .
	@echo "$(GREEN)✅ Sync complete$(NC)"

# PURPOSE: Fast-search the codebase for a query.
search: ## Search codebase for q="term"
	@if [ -z "$(q)" ]; then echo "$(RED)❌ Error: q=\"...\" is required$(NC)" && exit 1; fi
	@grep -rnE "$(q)" src/ tests/ docs/ || echo "$(YELLOW)No matches found for '$(q)'$(NC)"

# PURPOSE: Discover new skills from external repositories.
discover: ## Discover external skills (q="topic")
	@python3 scripts/skill_explorer.py search "$(q)"

# PURPOSE: List all TODOs and FIXMEs in the codebase.
list-todos: ## List all 'TODO' and 'FIXME' tags in the code
	@echo "$(BLUE)📝 Current Codebase Tasks:$(NC)"
	@grep -rnE "TODO|FIXME" src/ | awk -F: '{printf "  $(YELLOW)%-25s$(NC) %s\n", $$1":"$$2, $$3}' || echo "$(GREEN)✨ No pending TODOs!$(NC)"

# ==============================================================================
# 🧹 HYGIENE & QUALITY
# ==============================================================================

# PURPOSE: Delete temporary files that clog up your workspace.
# WHEN: Run this if your folders feel "heavy" or if you want to clear caches.
clean: ## Clear out temporary files, caches, and scratchpad drafts
	@echo "$(BLUE)🧹 Cleaning workspace caches...$(NC)"
	@rm -rf scratchpad/* logs/*.log __pycache__ .pytest_cache

# PURPOSE: Run CI tests locally (mirrors GitHub Actions).
# WHEN: Run this before pushing to ensuring your code passes all checks.
ci-local: ## Run CI tests locally (mirrors GitHub Actions)
	@echo "$(BLUE)🔄 Running local CI checks...$(NC)"
	@echo "📋 Step 1: Audit"
	@python3 scripts/audit.py
	@echo "📋 Step 2: Lint"
	@ruff check . || true
	@echo "📋 Step 3: Test"
	@pytest tests/ -q || echo "$(YELLOW)⚠️  No tests found or pytest not installed$(NC)"
	@echo "$(GREEN)✅ Local CI complete$(NC)"

# ==============================================================================
# 🛡️ SECURITY & DEPENDENCIES
# ==============================================================================

# PURPOSE: Check for outdated or vulnerable dependencies.
# WHEN: Run this periodically to keep your environment secure.
deps-check: ## Check for outdated/vulnerable dependencies
	@echo "$(BLUE)🔍 Checking dependencies...$(NC)"
	@pip3 list --outdated 2>/dev/null | head -20 || echo "$(YELLOW)⚠️  pip not available$(NC)"
	@echo ""
	@command -v pip-audit >/dev/null 2>&1 && pip-audit || echo "$(YELLOW)💡 Install pip-audit for vulnerability scanning: pip install pip-audit$(NC)"

# PURPOSE: Scan for secrets and vulnerabilities in the codebase.
# WHEN: Run this before publishing or after adding new dependencies.
security-scan: ## Scan for secrets and vulnerabilities
	@echo "$(BLUE)🔐 Running security scan...$(NC)"
	@command -v gitleaks >/dev/null 2>&1 && gitleaks detect --source . --no-git || echo "$(YELLOW)💡 Install gitleaks for secret scanning: brew install gitleaks$(NC)"
	@command -v pip-audit >/dev/null 2>&1 && pip-audit || true
	@echo "$(GREEN)✅ Security scan complete$(NC)"

# PURPOSE: Create a local "Save Point" of the entire workspace.
backup: snapshot ## Alias for snapshot
