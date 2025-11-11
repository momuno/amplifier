# Developer Guide Template

## Instructions for AI

You are generating a developer/contributor guide for a software project.

**Tone**: Technical, comprehensive, welcoming to contributors
**Audience**: Developers who want to contribute to or extend the project
**Structure**: Follow the example structure below

## Required Sections

1. **Overview**: Project architecture and organization
2. **Development Setup**: How to get started developing
3. **Code Standards**: Style, testing, documentation requirements
4. **Development Workflow**: How to contribute changes
5. **Testing**: How to run and write tests
6. **Release Process**: How releases are made (if applicable)

## Example Output

---

# Developer Guide

## Project Overview

High-level architecture and how the project is organized.

### Directory Structure

```
project/
├── src/           # Source code
├── tests/         # Test suite
├── docs/          # Documentation
└── scripts/       # Build and utility scripts
```

### Key Components

- **Component 1**: What it does
- **Component 2**: What it does
- **Component 3**: What it does

## Development Setup

### Prerequisites

- Python 3.11+
- Additional tools or dependencies

### Installation

```bash
# Clone repository
git clone <repo-url>

# Install dependencies
make install

# Run tests
make test
```

## Code Standards

### Style Guide

- Follow PEP 8 for Python code
- Line length: 120 characters
- Use type hints

### Testing Requirements

- All new features must have tests
- Maintain >80% code coverage
- Run `make test` before committing

### Documentation

- Docstrings for all public functions/classes
- Update relevant documentation files
- Include examples in docstrings

## Development Workflow

### Making Changes

1. Create a feature branch: `git checkout -b feature/description`
2. Make your changes
3. Run tests: `make test`
4. Run linting: `make check`
5. Commit changes: `git commit -m "description"`
6. Push and create pull request

### Pull Request Process

- Provide clear description of changes
- Link to relevant issues
- Ensure CI passes
- Request review from maintainers

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_module.py

# Run with coverage
pytest --cov=src tests/
```

### Writing Tests

Example test structure:

```python
def test_feature():
    # Arrange
    setup_data()

    # Act
    result = perform_action()

    # Assert
    assert result == expected
```

## Release Process

How releases are created and published (if applicable).

---

## Source Content

The following files have been provided as source material. Extract project structure, conventions, and development practices:

{{SOURCE_FILES}}

## Generation Rules

1. Extract actual project structure from source files
2. Identify coding standards from existing code
3. Find test patterns and requirements
4. Look for CI/CD configuration
5. Use real examples from the codebase
6. Include make targets or scripts that actually exist
7. Be specific about tools and versions used
