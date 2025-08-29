# DummyPy Analytics Library

## Overview

DummyPy is a Python analytics library created for educational and testing purposes. This toolkit provides example statistical modeling, data analysis, and visualization capabilities designed to showcase modern Python development practices.

**📚 EDUCATIONAL & DEMONSTRATION PURPOSE**
This software is created for learning and demonstration purposes. Feel free to use, modify, and distribute.

## Quick Start

### ☁️ Instant Development with GitHub Codespaces

Get started immediately with a fully configured cloud development environment:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/markrichardson/dummypy?quickstart=1)

**Benefits:**
- 🚀 **Zero Setup** - Ready in 2-3 minutes
- 🔧 **Pre-configured** - All tools and dependencies included
- 📊 **Marimo Notebooks** - Interactive analytics environment on port 8080
- 🛡️ **Quality Tools** - Ruff, pre-commit, and testing ready to use

### 💻 Local Development

## Core Features

- **Example Statistical Models**: Sample algorithms & statistics for data analysis
- **Data Processing**: Demonstration of data manipulation and analysis techniques
- **Visualization Tools**: Example plotting and data visualization capabilities

## Installation & Setup

#### Quick Start (Linux/macOS)

```bash
# Clone the repository
git clone git@github.com:[USERNAME]/dummypy.git
cd dummypy

# Run the automated setup
make setup
```

#### Windows Users

For detailed Windows setup instructions using WSL and VS Code, see **[INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)**.

#### Available Commands

```bash
make help          # Show all available commands
make setup         # Create development environment
make test          # Run test suite
make lint          # Run code quality checks
make format        # Format code
make clean         # Clean up environment
```

## Usage

```python
import dummypy as dp

grid = dp.Grid()
grid.diff()
```

## Development

For developers working on this project, comprehensive documentation about the CI/CD infrastructure, development workflows, and quality assurance processes is available in **[GITHUB_CICD_README.md](GITHUB_CICD_README.md)**.

This documentation covers:
- GitHub Actions workflows for automated testing and deployment
- Pre-commit hooks for code quality enforcement
- Dependency management with Renovate
- GitHub Codespaces cloud development environment
- Development workflow commands and best practices

## Architecture

- **Core Models** (`dummypy.models`): Example statistical models
- **Core Payoffs** (`dummypy.payoffs`): Demonstration payoff functions
- **Analytics** (`dummypy.analytics`): Sample performance tracking and reporting

## License

© 2025 Mark Richardson. Released under MIT License.

This software is provided for educational and demonstration purposes. Feel free to use, modify, and distribute according to the MIT License terms.

---

**Version**: 0.1.0
**Last Updated**: August 2025
**Classification**: CONFIDENTIAL
