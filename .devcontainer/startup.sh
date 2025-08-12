#!/bin/bash

# Set UV environment variables to avoid prompts and warnings
export UV_VENV_CLEAR=1
export UV_LINK_MODE=copy

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install all dependencies including dev
uv venv
uv sync --extra dev --frozen

# Install additional tools for Codespaces
uv pip install --no-cache-dir marimo ipykernel

# Initialize pre-commit hooks (in background to not block startup)
nohup uv run pre-commit install > /dev/null 2>&1 &

echo "🚀 DummyPy development environment ready!"
echo "📊 Marimo notebook will be available on port 8080"
echo "🔧 Pre-commit hooks installed for code quality"
