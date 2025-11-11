# README Template

## Instructions for AI

You are generating a top-level README.md for a software project.

**Tone**: Professional, welcoming, concise
**Audience**: Developers discovering the project for the first time
**Structure**: Follow the example structure below

## Required Sections

1. **Project Title & Description**: One-sentence description, then 2-3 sentence overview
2. **Key Features**: Bullet list of 3-5 main capabilities
3. **Quick Start**: Installation and basic usage
4. **Documentation Links**: Point to detailed guides
5. **Contributing**: Brief note on how to contribute

## Example Output

---

# Project Name

Brief one-sentence description.

Longer description providing context about what this project does, why it exists, and who should use it. Keep to 2-3 sentences maximum.

## Features

- Feature 1: Brief description
- Feature 2: Brief description
- Feature 3: Brief description

## Quick Start

```bash
# Installation
pip install project-name

# Basic usage
python -m project
```

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Detailed usage instructions
- [Developer Guide](docs/DEV_GUIDE.md) - Contributing and development setup

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Source Content

The following files have been provided as source material. Use them to populate the sections above with accurate, current information:

{{SOURCE_FILES}}

## Generation Rules

1. Extract project name from pyproject.toml or package structure
2. Infer features from code structure and docstrings
3. Extract installation commands from pyproject.toml or setup files
4. Keep code examples minimal but functional
5. Link to existing detailed docs rather than duplicating content
6. If information is unclear, use placeholder like [TODO: clarify X]
