# Contributing to WinRM MCP Server

Thank you for considering contributing to WinRM MCP Server! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Setting up the development environment

1. Clone the repository:

   ```bash
   git clone https://github.com/antonvano-microsoft/winrm-mcp-server.git
   cd winrm-mcp-server
   ```

2. Install dependencies with development tools:

   ```bash
   uv sync --dev
   ```

3. Activate the virtual environment:

   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On Unix/macOS
   source .venv/bin/activate
   ```

## Development Workflow

### Code Formatting

We use [Black](https://black.readthedocs.io/) and [isort](https://pycqa.github.io/isort/) for code formatting:

```bash
# Format code
uv run black .
uv run isort .

# Check formatting
uv run black --check .
uv run isort --check-only .
```

### Type Checking

We use [mypy](https://mypy.readthedocs.io/) for static type checking:

```bash
# Run type checks
uv run mypy .
```

### Running Tests

```bash
# Run all tests
uv run pytest -v
```

### Building the Package

```bash
# Build distribution packages
uv build
```

### Publishing (Maintainers Only)

```bash
# Publish to PyPI
uv publish
```

## Code Standards

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Maintain backwards compatibility when possible
- Add tests for new functionality

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting a PR
- Aim for good test coverage
- Test against multiple Python versions when possible

## Submitting Changes

1. Fork the repository
2. Create a feature branch from `master`
3. Make your changes
4. Run tests and formatting checks
5. Commit your changes with a clear commit message
6. Push to your fork
7. Create a Pull Request

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Release Process

1. Update version in `pyproject.toml` and `src/winrm_mcp_server/__init__.py`
2. Update `CHANGELOG.md` with new version and changes
3. Create a new release on GitHub
4. The package will be automatically published to PyPI

## Security

Please report security vulnerabilities privately by email rather than opening public issues. See our [Security Policy](SECURITY.md) for more details.

## Questions?

Feel free to open an issue for questions about contributing or to discuss potential changes before implementing them.
