# Makefile for Python quality automation
#
# This Makefile uses 'uv' for fast, modern Python project management.
# It features a self-documenting help target. Add '##' comments to targets
# to have them appear in 'make help'.

# --- Configuration ---
# Default goal when 'make' is run without arguments.
.DEFAULT_GOAL := help

# Overridable variables. Use 'make lint SOURCE=./my_app' to override.
SOURCE ?= src
TEST_DIR ?= tests
FULL_SOURCES = $(SOURCE) $(TEST_DIR)

# Variable for passing extra command-line arguments to run targets.
# e.g., make test ARGS="-k my_specific_test"
ARGS ?=


# === Help ===
# The 'help' target uses awk to parse comments and generate a help message.
# It's a common pattern for creating self-documenting Makefiles.
help: ## ✨ Displays this help message
	@echo "Usage: make [target] [ARGS=...]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


# === Project Setup & Dependencies ===
install: ## 📦 Install project dependencies for development
	@echo "⌛ Installing development dependencies..."
	uv pip install --editable .[dev]
	@echo "✅ Dependencies installed."


# === Quality & Formatting ===
format: ## 🎨 Formats code using Ruff
	@echo "⌛ Formatting project code..."
	uv run ruff format $(FULL_SOURCES)
	uv run ruff check $(FULL_SOURCES) --fix --show-fixes
	@echo "✅ Code formatted."

lint: ## 🔍 Lints code using Ruff
	@echo "⌛ Linting project code..."
	uv run ruff check $(FULL_SOURCES) $(ARGS)
	@echo "✅ Linting complete."

mypy: ## 🧐 Checks static types with mypy
	@echo "⌛ Running mypy type checker..."
	uv run mypy $(SOURCE)/ --install-types
	@echo "✅ Type checking complete."


# === Testing & Code Metrics ===
test: ## 🧪 Runs tests with pytest
	@echo "⌛ Running tests..."
	uv run pytest $(ARGS)
	@echo "✅ Tests finished."

cc: ## 🔬 Reports cyclomatic complexity with radon
	uv run radon cc $(SOURCE)/ --show-complexity --average --total-average

mi: ## 🔧 Reports maintainability index with radon
	uv run radon mi --show --sort $(SOURCE)/


# === Build & Distribution ===
build: ## 🏗️ Builds the wheel and sdist packages
	@echo "📦 Building wheel and sdist into dist/..."
	@rm -rf dist/ # Clean previous builds first
	@uv build
	@echo "✅ Build successful."

publish-test: ## 🚀 Publishes artifacts to TestPyPI for validation
	@echo "🚀 Publishing artifacts to TestPyPI..."
	@if [ -z "$${UV_PUBLISH_TOKEN}" ]; then \
		echo "\033[31m❌ Error: UV_PUBLISH_TOKEN environment variable is not set.\033[0m"; \
		echo "   Please set it before running this command."; \
		exit 1; \
	fi
	@uv publish --index testpypi
	@echo "✅ Published to TestPyPI."


# === Cleanup ===
clean: ## 🧹 Removes build artifacts and cache files
	@echo "🧹 Cleaning up the project..."
	# Use a single rm command for efficiency and clarity
	@rm -rf \
		build/ \
		dist/ \
		*.egg-info/ \
		.eggs/ \
		.pytest_cache/ \
		.coverage \
		.mypy_cache/ \
		.ruff_cache/
	# Use find for cleaning nested cache files and directories
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -name '.DS_Store' -type f -delete
	@echo "✅ Cleanup complete."

# A more aggressive clean, often called 'distclean'. Kept commented as a reference.
# distclean: clean ## 🧹 Removes all git-ignored files (use with caution!)
#	@echo "🧹 Removing all git-ignored files and directories..."
#	@git clean -fdX


# === Project Execution ===
# This is a pattern rule that dynamically handles any 'run-*' target.
# For example, 'make run-loancalc' will execute 'uv run loancalc'.
run-%: ## ▶️  Runs an application (e.g., make run-loancalc)
	@uv run $* $(ARGS)


# === Aggregation Targets ===
quality: lint mypy cc mi ## 🏅 Runs all static analysis checks
check: quality test build ## ✅ Runs all checks (quality, tests, build)


# --- Phony Targets ---
# Declares targets that are not files. This prevents conflicts with files of the
# same name and can improve performance.
.PHONY: help install format lint mypy test cc mi quality check build publish-test clean distclean
.PHONY: run-%
