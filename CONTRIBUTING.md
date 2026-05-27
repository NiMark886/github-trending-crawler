# Contributing to GitHub Trending Crawler

Thank you for your interest in contributing to GitHub Trending Crawler! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Types of Contributions

1. **Bug Reports**: Report bugs and issues
2. **Feature Requests**: Suggest new features
3. **Code Contributions**: Submit pull requests
4. **Documentation**: Improve documentation
5. **Testing**: Help with testing

### Getting Started

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/your-username/github-trending-crawler.git
cd github-trending-crawler
```

2. **Create a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. **Run the application**

```bash
python cli.py --help
```

## Code Style

### Python Style Guide

We follow PEP 8 style guide. Please ensure your code adheres to these standards.

### Key Points

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Use type hints where appropriate

### Code Formatting

We recommend using the following tools:

```bash
# Install formatters
pip install black isort flake8

# Format code
black .
isort .

# Check style
flake8 .
```

### Docstring Format

Use Google style docstrings:

```python
def fetch_trending(since: str = "weekly") -> List[Dict]:
    """
    Fetch GitHub trending repositories.

    Args:
        since: Time range (daily/weekly/monthly)

    Returns:
        List of repository dictionaries

    Raises:
        RequestException: If request fails
    """
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_crawler.py
```

### Writing Tests

- Write tests for all new features
- Aim for high test coverage (>80%)
- Use descriptive test names
- Mock external dependencies

### Test Structure

```
tests/
├── __init__.py
├── test_crawler.py
├── test_downloader.py
├── test_search.py
└── test_database.py
```

## Pull Request Process

### Before Submitting

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Update CHANGELOG.md** with your changes
4. **Ensure all tests pass**
5. **Follow code style guidelines**

### PR Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what the PR does and why
3. **Related Issues**: Link to related issues
4. **Changes Made**: List the changes
5. **Testing**: Describe how you tested

### PR Template

```markdown
## Description

A clear description of what this PR does.

## Related Issues

Fixes #(issue number)

## Changes Made

- Change 1
- Change 2

## Testing

Describe how you tested your changes.

## Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: How to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, etc.
6. **Screenshots**: If applicable

### Feature Requests

When requesting features, please include:

1. **Description**: Clear description of the feature
2. **Motivation**: Why this feature is needed
3. **Proposed Solution**: How it should work
4. **Alternatives**: Any alternatives you've considered

## Development Guidelines

### Adding New Features

1. **Create an issue** first to discuss the feature
2. **Get approval** before starting work
3. **Create a feature branch** from main
4. **Implement the feature** following code style
5. **Add tests** for the feature
6. **Update documentation**
7. **Submit a PR**

### Fixing Bugs

1. **Create an issue** describing the bug
2. **Create a bug fix branch** from main
3. **Fix the bug** with minimal changes
4. **Add regression tests**
5. **Submit a PR**

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add proxy support for downloads
fix: Fix timeout issue in crawler
docs: Update README with new features
test: Add tests for database module
refactor: Improve error handling
```

### Branch Naming

Use descriptive branch names:

```
feature/proxy-support
bugfix/timeout-issue
docs/update-readme
refactor/error-handling
```

## Questions?

If you have questions about contributing, please:

1. Check the existing documentation
2. Search for existing issues
3. Create a new issue with the question tag

Thank you for contributing! 🎉
