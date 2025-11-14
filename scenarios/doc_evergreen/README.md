# doc-evergreen

**Automatic documentation generation and maintenance using LLM intelligence.**

A CLI tool that generates high-quality documentation from your source code and maintains it as your project evolves.

## What It Does

doc-evergreen solves the documentation maintenance problem:

1. **Generate** - Creates comprehensive documentation from your source files using AI
2. **Maintain** - Regenerates docs when code changes, preserving quality
3. **Version** - Tracks all changes with automatic backup and history

## Quick Start

### Prerequisites

- Python 3.11+
- Anthropic API key in `.claude/api_key.txt` (repo root)

### Installation

```bash
cd scenarios/doc_evergreen
uv sync
```

### Basic Usage

**Create new documentation:**
```bash
uv run python -m doc_evergreen.cli create \
    --about "Main project README" \
    --output README.md \
    --sources "src/**/*.py" "pyproject.toml"
```

**Regenerate existing documentation:**
```bash
# Regenerate single document
uv run python -m doc_evergreen.cli regenerate README.md

# Regenerate all configured documents
uv run python -m doc_evergreen.cli regenerate --all
```

## How It Works

### The Create Command

Generates documentation through a 5-step process:

1. **File Discovery** - Finds source files matching patterns (respects .gitignore)
2. **Load Template** - Loads the built-in README template
3. **Document Generation** - Uses LLM to generate content from sources
4. **Backup** - Saves existing document to `.doc-evergreen/versions/` (if exists)
5. **Save & History** - Writes generated documentation and updates `.doc-evergreen/history.yaml`

### The Regenerate Command

Rebuilds documentation from saved configuration:

1. **Load History** - Reads configuration from history.yaml
2. **Gather Sources** - Finds files matching saved patterns
3. **Load Template** - Loads the built-in README template
4. **Generate** - Creates updated documentation
5. **Backup & Save** - Preserves old version, writes new one
6. **Update History** - Adds version entry

### Configuration Management

All settings are stored in `.doc-evergreen/history.yaml`:

```yaml
docs:
  README.md:
    created: 2025-01-07T10:30:00Z
    last_generated: 2025-01-08T14:15:30Z
    path: README.md
    template_used:
      name: readme
      path: ""
    sources:
      - "src/**/*.py"
      - "pyproject.toml"
    about: "Main project README"
    previous_versions:
      - timestamp: 2025-01-07T10:30:00Z
        backup_path: .doc-evergreen/versions/README.md.2025-01-07T10-30-00.bak
        template_used:
          name: readme
          path: ""
```

## Command Reference

### create

Generate new documentation or regenerate existing.

```bash
doc-evergreen create --about DESCRIPTION --output PATH [OPTIONS]
```

**Required:**
- `--about TEXT` - Description of documentation purpose
- `--output PATH` - Output file path (e.g., `README.md`, `docs/API.md`)

**Optional:**
- `--sources PATTERN` - Glob patterns for source files (repeatable)
  - If omitted, auto-discovers based on `--about`
  - Examples: `"src/**/*.py"`, `"*.md"`, `"api/**/*.ts"`
  - **Can be specified multiple times** to include different file types
  - Use `**` for recursive matching (e.g., `**/*.md` finds all markdown files)

**Examples:**

```bash
# Auto-discover sources
doc-evergreen create \
    --about "API documentation" \
    --output docs/API.md

# Explicit sources
doc-evergreen create \
    --about "Developer guide for authentication" \
    --output docs/DEVELOPER.md \
    --sources "src/auth/**/*.py"

# Multiple source patterns
doc-evergreen create \
    --about "Contributing guide" \
    --output CONTRIBUTING.md \
    --sources "CONTRIBUTING.md" \
    --sources ".github/**/*.md"

# Include all markdown and Python files
doc-evergreen create \
    --about "Project README covering architecture and implementation" \
    --output README.md \
    --sources "**/*.md" \
    --sources "**/*.py"
```

### Using with Make

When using the Makefile wrapper, pass multiple patterns in a single SOURCES argument separated by spaces:

```bash
# Single pattern via make
make doc-create ABOUT="API documentation" OUTPUT=docs/API.md SOURCES="src/**/*.py"

# Multiple patterns via make (space-separated in quotes)
make doc-create \
    ABOUT="Project README" \
    OUTPUT=README.md \
    SOURCES="**/*.md **/*.py"

# Mix exact files and patterns
make doc-create \
    ABOUT="Configuration guide" \
    OUTPUT=docs/CONFIG.md \
    SOURCES="pyproject.toml **/*.toml **/*.yaml"
```

**Note**: The Makefile automatically converts space-separated patterns into multiple `--sources` flags for the CLI.

### regenerate

Regenerate documentation from saved configuration.

```bash
doc-evergreen regenerate [DOC_PATH | --all]
```

**Arguments:**
- `DOC_PATH` - Specific document to regenerate (e.g., `README.md`)
- `--all` - Regenerate all configured documents

**Examples:**

```bash
# Regenerate single document
doc-evergreen regenerate README.md

# Regenerate all documents
doc-evergreen regenerate --all
```

## File Organization

```
your-project/
├── .doc-evergreen/              # Configuration and backups
│   ├── history.yaml             # Document configuration (committed)
│   └── versions/                # Document backups (committed)
│       ├── README.md.2025-01-07T10-30-00.bak
│       └── README.md.2025-01-08T14-15-30.bak
├── README.md                    # Generated documentation
└── docs/
    └── API.md                   # Generated documentation
```

**Note**: All `.doc-evergreen/` contents are committed to git for team sharing.

## API Key Setup

The tool requires an Anthropic API key.

**Option 1: File (Recommended)**
```bash
# Create in repo root
echo "your-api-key-here" > .claude/api_key.txt
```

**Option 2: Environment Variable**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

The tool searches up the directory tree from current working directory for `.claude/api_key.txt`.

## Auto-Discovery

When you don't specify `--sources`, the tool intelligently discovers relevant files based on `--about` keywords:

- "api" → `src/**/*.py`, `api/**/*.py`
- "cli" → `src/cli/**/*.py`, `src/commands/**/*.py`
- "readme" → `README.md`, `src/**/*.py`, `pyproject.toml`
- "contributing" → `CONTRIBUTING.md`, `.github/**/*.md`
- "user guide" → `README.md`, `docs/**/*.md`, `examples/**/*`

## LLM Configuration

Uses Claude Sonnet 4 with conservative settings:

- Model: `claude-sonnet-4-20250514`
- Max tokens: 4000
- Temperature: 0.3 (deterministic)
- Retry: Exponential backoff on rate limits

Generation typically takes 30-60 seconds per document.

## Error Handling

The tool handles common scenarios:

- **Missing sources** - Clear error with patterns that failed
- **Invalid UTF-8** - Skips files that can't be read as text
- **API errors** - Retries with exponential backoff (max 3 attempts)
- **Missing API key** - Helpful message with setup instructions

## Development

### Run Tests

```bash
# All tests
uv run pytest tests/ -v

# Specific test file
uv run pytest tests/test_history.py -v

# With coverage
uv run pytest tests/ --cov=doc_evergreen
```

### Code Quality

```bash
# Lint and format
uv run ruff check .
uv run ruff format .

# Type checking
uv run pyright .
```

## Architecture

### Core Modules

- **cli.py** - Click-based command-line interface
- **commands/** - Command implementations (create, regenerate)
- **core/discovery.py** - File discovery and pattern matching
- **core/generator.py** - LLM integration for generation
- **core/history.py** - Configuration management
- **core/template.py** - Template loading and versioning
- **core/versioning.py** - Document backup and versioning

### Design Principles

1. **Deterministic tool + Intelligent assistant**
   - Tool reports what it needs
   - AI assistant (Claude Code) gathers information

2. **Always overwrite with versioning**
   - Old versions automatically backed up
   - Full version history preserved

3. **History committed to git**
   - Team shares configuration
   - Reproducible documentation builds

## Known Limitations

1. **Source file size** - Large projects may hit token limits (50KB total source limit)
2. **Binary files** - Only UTF-8 text files supported
3. **API costs** - Each generation consumes API tokens (~500-2000 per document)
4. **Generation time** - 30-60 seconds per document (LLM processing)

## Troubleshooting

### "No API key found"
```bash
# Check for API key file
ls -la .claude/api_key.txt

# Or check environment
echo $ANTHROPIC_API_KEY

# Create API key file
echo "your-key" > .claude/api_key.txt
```

### "No source files found"
```bash
# Test your pattern
ls src/**/*.py  # Does this match files?

# Check .gitignore isn't excluding them
git check-ignore -v src/file.py

# Try specifying sources explicitly
doc-evergreen create --about "test" --output test.md --sources "src/**/*.py"
```

### "Rate limit exceeded"
The tool automatically retries with exponential backoff. If it persists:
- Wait 60 seconds and try again
- Check your API quota at console.anthropic.com
- Process fewer documents at once

## License

See repository root for license information.
