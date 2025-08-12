.PHONY: help setup activate deactivate clean test lint format python info pre-commit install-hooks

# Default target
help:
	@echo "DummyPy Development Environment"
	@echo "=================================="
	@echo ""
	@echo "Setup commands:"
	@echo "  setup         - Run the setup script to create environment"
	@echo "  install-hooks - Install pre-commit hooks"
	@echo "  clean         - Remove the virtual environment"
	@echo ""
	@echo "Development commands:"
	@echo "  activate      - Show activation command"
	@echo "  python        - Run Python in the virtual environment"
	@echo "  test          - Run tests with pytest"
	@echo "  lint          - Run linting with ruff"
	@echo "  format        - Format code with ruff"
	@echo "  pre-commit    - Run pre-commit on all files"
	@echo ""
	@echo "Info commands:"
	@echo "  info          - Show environment information"
	@echo "  help          - Show this help message"

# Environment paths
VENV_PATH := $(HOME)/venvs/dummypy
PYTHON := $(VENV_PATH)/bin/python
UV := uv

# Setup environment
setup:
	@echo "Running setup script..."
	@./setup-local-linux.sh

# Clean environment
clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV_PATH)
	@echo "Environment cleaned."

# Show activation command
activate:
	@echo "To activate the virtual environment, run:"
	@echo "  source $(VENV_PATH)/bin/activate"
	@echo ""
	@echo "To deactivate:"
	@echo "  deactivate"

# Run Python in virtual environment
python:
	@if [ ! -f "$(PYTHON)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@$(PYTHON)

# Run tests
test:
	@echo "Running tests..."
	@echo "Syncing dependencies..."
	@$(UV) sync --extra dev
	@$(UV) run pytest tests/ -v

# Format code
format:
	@echo "Formatting code with ruff..."
	@$(UV) sync --extra dev
	@$(UV) run ruff format .

# Run linting with ruff
lint:
	@echo "Running linting with ruff..."
	@$(UV) sync --extra dev
	@$(UV) run ruff check .

# Install pre-commit hooks
install-hooks:
	@if [ ! -f "$(PYTHON)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Installing pre-commit hooks..."
	@VIRTUAL_ENV="$(VENV_PATH)" $(UV) tool install pre-commit
	@VIRTUAL_ENV="$(VENV_PATH)" $(UV) tool run pre-commit install

# Run pre-commit on all files
pre-commit:
	@echo "Running pre-commit on all files..."
	@$(UV) sync --extra dev
	@$(UV) tool run pre-commit run --all-files

# Show environment info
info:
	@echo "DummyPy Development Environment Info"
	@echo "======================================"
	@echo ""
	@if [ -f "$(PYTHON)" ]; then \
		echo "✅ Virtual environment: $(VENV_PATH)"; \
		echo "✅ Python version: $$($(PYTHON) --version)"; \
		echo "✅ Python path: $(PYTHON)"; \
		echo "✅ Package manager: uv"; \
		echo ""; \
		echo "Installed packages:"; \
		VIRTUAL_ENV="$(VENV_PATH)" $(UV) pip list | head -10; \
		echo "... (use 'VIRTUAL_ENV=$(VENV_PATH) uv pip list' for full list)"; \
	else \
		echo "❌ Virtual environment not found at $(VENV_PATH)"; \
		echo "   Run 'make setup' to create it."; \
	fi

# Install additional packages
install:
	@if [ ! -f "$(PYTHON)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Usage: make install PACKAGE=package_name"; \
		exit 1; \
	fi
	@echo "Installing $(PACKAGE)..."
	@VIRTUAL_ENV="$(VENV_PATH)" $(UV) pip install $(PACKAGE)

# Reinstall project in editable mode
reinstall:
	@if [ ! -f "$(PYTHON)" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Reinstalling dummypy package in editable mode..."
	@VIRTUAL_ENV="$(VENV_PATH)" $(UV) pip install -e .
