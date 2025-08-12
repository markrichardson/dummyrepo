#!/bin/bash
# Setup script for dummypy local development environment

set -e  # Exit on any error

echo "🚀 Setting up dummypy development environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Set virtual environment path
VENV_PATH="$HOME/venvs/dummypy"
echo "📁 Virtual environment will be created at: $VENV_PATH"

# Create venvs directory if it doesn't exist
mkdir -p "$HOME/venvs"

# Method 1: Using uv (fast and modern) - Default choice
setup_with_uv() {
    echo "📦 Using uv for package management..."

    # Install uv if not present
    if ! command -v uv &> /dev/null; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    else
        echo "✅ uv already installed"
    fi

    # Create virtual environment
    echo "Creating virtual environment with uv..."
    uv venv "$VENV_PATH"

    # Install dependencies (includes both main and dev dependencies)
    echo "Installing project dependencies..."
    VIRTUAL_ENV="$VENV_PATH" uv sync

    # Install development tools for Jupyter
    echo "Installing Jupyter tools..."
    VIRTUAL_ENV="$VENV_PATH" uv pip install ipykernel jupyter

    # Install the package in editable mode
    echo "Installing dummypy package in editable mode..."
    VIRTUAL_ENV="$VENV_PATH" uv pip install -e .

    echo "✅ Setup complete with uv!"
}

# Method 2: Using standard pip/venv (fallback)
setup_with_pip() {
    echo "📦 Using pip/venv for package management..."

    # Create virtual environment
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"

    # Activate virtual environment
    source "$VENV_PATH/bin/activate"

    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip

    # Install the package with all dependencies
    echo "Installing project with dependencies..."
    pip install -e ".[dev]"

    echo "✅ Setup complete with pip!"
}

# Choose method based on preference or availability
if command -v uv &> /dev/null || [ "$1" = "uv" ]; then
    setup_with_uv
else
    echo "🔄 uv not found, using pip method..."
    setup_with_pip
fi

# Register Jupyter kernel
echo "🔧 Registering Jupyter kernel..."
if [ -f "$VENV_PATH/bin/python" ]; then
    "$VENV_PATH/bin/python" -m ipykernel install --user --name dummypy --display-name "DummyPy"
    echo "✅ Jupyter kernel 'DummyPy' registered"
else
    echo "⚠️  Warning: Could not register Jupyter kernel"
fi

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
if [ -f "$VENV_PATH/bin/python" ]; then
    VIRTUAL_ENV="$VENV_PATH" uv tool install pre-commit
    VIRTUAL_ENV="$VENV_PATH" uv tool run pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  Warning: Could not install pre-commit hooks"
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment:"
echo "  source $VENV_PATH/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "Python path: $VENV_PATH/bin/python"
echo "Jupyter kernel: 'DummyPy'"
echo "Pre-commit hooks: Installed"
echo ""
echo "Development commands:"
echo "  make test        - Run tests"
echo "  make lint        - Run linting"
echo "  make format      - Format code"
echo "  make pre-commit  - Run all pre-commit checks"
echo ""
echo "Your dummypy package is installed in editable mode."
echo "Any changes to the source code will be immediately available."
