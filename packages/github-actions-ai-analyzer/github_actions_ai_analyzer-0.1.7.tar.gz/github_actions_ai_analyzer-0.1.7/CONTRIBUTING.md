# Contributing to GitHub Actions AI Analyzer

Thank you for your interest in contributing to GitHub Actions AI Analyzer! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Development Setup

1. Fork the repository
2. Clone your fork:

   ```bash
   git clone https://github.com/your-username/Github-Actions-AI-Analyzer.git
   cd Github-Actions-AI-Analyzer
   ```

3. Install the package in development mode:

   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Guidelines

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run the formatters before committing:

```bash
black src/ tests/
isort src/ tests/
```

### Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src/github_actions_ai_analyzer
```

### Type Checking

Run type checking:

```bash
mypy src/
```

## Adding New Features

### Error Patterns

To add new error patterns:

1. Add the pattern to the appropriate category in `src/github_actions_ai_analyzer/core/pattern_matcher.py`
2. Create tests in `tests/unit/test_pattern_matcher.py`
3. Update documentation if needed

### Language Support

To add support for a new language:

1. Create a new directory in `src/github_actions_ai_analyzer/languages/`
2. Implement language-specific patterns and context parsers
3. Add tests for the new language support
4. Update the main analyzer to include the new language

### CLI Commands

To add new CLI commands:

1. Add the command to `src/github_actions_ai_analyzer/cli/main.py`
2. Create tests in `tests/integration/test_cli.py`
3. Update the CLI documentation

## Submitting Changes

### Pull Request Process

1. Create a feature branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:

   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

3. Push your branch and create a pull request

4. Ensure all tests pass and code quality checks are satisfied

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build or tool changes

### Pull Request Guidelines

- Provide a clear description of the changes
- Include tests for new functionality
- Update documentation if needed
- Ensure all CI checks pass

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
