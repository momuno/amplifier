---
name: Contributing Guide Template
description: Guidelines for project contributors
suggested_sources:
  - CONTRIBUTING.md
  - README.md
  - pyproject.toml
  - .github/**/*.md
---

# Contributing to {{project_name}}

Thank you for your interest in contributing to {{project_name}}! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

[Explain expected behavior and community standards. Link to CODE_OF_CONDUCT.md if it exists.]

We are committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and professional in all interactions.

## Getting Started

[Guide new contributors through initial setup]

### Prerequisites

[List required tools, software versions, and knowledge]

- Python 3.11+
- Git
- [Other requirements]

### Fork and Clone

[Instructions for forking and cloning the repository]

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/project-name.git
cd project-name
```

## Development Setup

[Detailed instructions for setting up development environment]

### 1. Install Dependencies

[Show installation commands]

```bash
# Example using uv
make install

# Or manually
uv sync
```

### 2. Configure Environment

[Explain any environment setup, config files, or secrets]

```bash
# Copy example config
cp .env.example .env

# Edit with your settings
nano .env
```

### 3. Verify Setup

[Commands to verify everything works]

```bash
# Run tests
make test

# Run linters
make check
```

## How to Contribute

[Explain different ways to contribute]

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix issues and improve stability
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Increase test coverage
- **Performance**: Optimize code efficiency
- **Refactoring**: Improve code quality

### Finding Work

[How to find issues to work on]

- Check the [issue tracker](link) for open issues
- Look for issues labeled `good first issue` or `help wanted`
- Propose new features by opening an issue first

## Code Standards

[Explain coding standards and conventions]

### Style Guide

[Language-specific style requirements]

- Follow PEP 8 for Python code
- Use type hints consistently
- Write clear, descriptive variable names
- Keep functions focused and small

### Code Quality Tools

[Tools used for maintaining code quality]

```bash
# Format code
make format

# Run linters
make lint

# Type checking
make typecheck

# Run all checks
make check
```

### Documentation

[Documentation requirements]

- Add docstrings to all public functions/classes
- Update README.md if adding new features
- Include code examples where helpful
- Keep documentation up to date with code changes

## Testing

[Testing requirements and guidelines]

### Writing Tests

[How to write tests for this project]

```python
# Example test structure
def test_feature_name():
    """Test description"""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

### Running Tests

[Commands to run tests]

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_specific.py

# Run with coverage
make test-coverage
```

### Test Requirements

- Add tests for new features
- Ensure existing tests still pass
- Aim for high code coverage (>80%)
- Test edge cases and error conditions

## Pull Request Process

[Step-by-step PR submission process]

### 1. Create a Branch

[Branch naming conventions]

```bash
# Create feature branch
git checkout -b feature/description

# Or bug fix branch
git checkout -b fix/issue-number
```

### 2. Make Changes

[Development workflow]

- Make focused, logical commits
- Write clear commit messages
- Keep changes small and reviewable
- Test your changes thoroughly

### 3. Commit Guidelines

[Commit message format]

```
type(scope): brief description

Longer explanation if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions or changes
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

### 4. Push and Create PR

[PR creation process]

```bash
# Push your branch
git push origin your-branch-name

# Create PR on GitHub
# Fill out the PR template
# Link related issues
```

### 5. PR Review

[What to expect during review]

- Maintainers will review your code
- Address feedback promptly
- Be open to suggestions
- Iterate until approved
- Squash commits if requested

### PR Checklist

Before submitting, verify:

- [ ] Code follows project style guide
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] PR description explains the changes
- [ ] Linked related issues

## Reporting Issues

[How to report bugs or request features]

### Bug Reports

[Template for bug reports]

When reporting a bug, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Exact steps to trigger the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, relevant details
- **Logs/Screenshots**: Any helpful diagnostic information

### Feature Requests

[Template for feature requests]

When requesting a feature:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered?
- **Additional Context**: Any other relevant information

## Getting Help

[How to get assistance]

- **Documentation**: Check [docs](link) first
- **Discussions**: Use [GitHub Discussions](link) for questions
- **Chat**: Join our [community chat](link)
- **Issues**: Open an issue for bugs or features

## Recognition

[How contributors are recognized]

All contributors will be recognized in:
- Project README
- Release notes
- Contributors list

Thank you for contributing to {{project_name}}!
