# Contributing to steer-core

Thank you for your interest in contributing to steer-core! This document provides
guidelines and instructions for contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/stanford-developers/steer-core.git
   ```
   cd steer-core
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Code Style

This project uses:
- **Black** for code formatting (line length 88)
- **isort** for import sorting (Black-compatible profile)
- **flake8** for linting

Format your code before committing:
```bash
flake8 steer_core/
```

### Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=steer_core --cov-report=term-missing
```

### Making Changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and add tests
3. Ensure all tests pass: `pytest`
4. Format your code: `black . && isort .`
5. Commit with a clear message describing the change
6. Push to your fork and open a Pull Request

## Pull Request Guidelines

- Provide a clear description of what the PR does
- Reference any related issues
- Include tests for new functionality
- Ensure CI passes before requesting review

## Reporting Bugs

Open an issue on GitHub with:
- A clear title and description
- Steps to reproduce the behavior
- Expected vs actual behavior
- Python version and OS

## Feature Requests

Open an issue on GitHub describing:
- The use case for the feature
- How it would benefit steer-core users
- Any proposed implementation approach

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the
AGPL-3.0-only license.
