# doc-evergreen Implementation Plan

**Purpose**: Comprehensive plan for building the doc-evergreen tool for automatic documentation generation and maintenance.

**Version**: 1.0
**Date**: 2025-01-07
**Status**: Design Complete, Implementation Pending

---

## Executive Summary

The doc-evergreen tool enables automatic documentation generation from source code and configuration files. It combines LLM intelligence for discovery and generation with deterministic script execution for automation.

**Key Features**:
- Generate new documentation from source files
- Update existing documentation while preserving history
- Automatic template creation and versioning
- Fully automatable (git hooks, CI/CD)
- AI assistant integration for interactive setup

---

## Architecture Overview

### Design Philosophy

**The tool is deterministic:**
- Requires all parameters via CLI
- Reports missing parameters clearly
- Never prompts user directly
- Fully automatable for git hooks/CI/CD

**The assistant (Claude) provides intelligence:**
- Reads tool README for requirements
- Engages user to gather missing info
- Calls tool with complete parameters

### Component Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLI Interface                     │
│  (Click-based, parameter validation, help text)     │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │ create │  │  regen  │  │  update  │
   └────┬───┘  └────┬────┘  └────┬─────┘
        │           │            │
        └───────────┼────────────┘
                    ▼
        ┌───────────────────────┐
        │    Core Components    │
        ├───────────────────────┤
        │ • File Discovery      │
        │ • Template Manager    │
        │ • LLM Generator       │
        │ • History Manager     │
        │ • Version Control     │
        └───────────────────────┘
```

---

## Directory Structure

### Tool Installation Location

```
scenarios/doc_evergreen/
├── IMPLEMENTATION_PLAN.md    # This document
├── README.md                 # User guide + assistant reference
├── pyproject.toml            # Dependencies
├── cli.py                    # Main CLI entry point
├── commands/
│   ├── __init__.py
│   ├── create.py             # create command
│   ├── update.py             # update command
│   └── regenerate.py         # regenerate command
├── core/
│   ├── __init__.py
│   ├── discovery.py          # File discovery and glob handling
│   ├── template.py           # Template management and versioning
│   ├── generator.py          # LLM generation via direct API
│   ├── history.py            # history.yaml management
│   └── versioning.py         # Document versioning and backup
├── templates/                # Built-in starter templates
│   ├── readme.md
│   ├── api-reference.md
│   ├── user-guide.md
│   └── developer-guide.md
└── tests/
    ├── test_discovery.py
    ├── test_template.py
    ├── test_history.py
    └── test_integration.py
```

### Per-Repository State (.doc-evergreen/)

```
.doc-evergreen/
├── history.yaml              # Configuration and version history
├── templates/
│   ├── readme-amplifier.v1.md       # Generated templates
│   ├── readme-amplifier.v2.md       # (versioned)
│   ├── user-guide-cli.v1.md
│   └── api-reference-python.v1.md
└── versions/
    ├── README.md.2025-01-07T10-30-00.bak
    ├── README.md.2025-01-07T14-15-30.bak
    └── docs/
        ├── USER_GUIDE.md.2025-01-07T11-00-00.bak
        └── API_REFERENCE.md.2025-01-07T14-15-00.bak
```

**Note**: All files in `.doc-evergreen/` are committed to git for team collaboration.

---

## Data Structures

### history.yaml Format

```yaml
docs:
  README.md:
    created: 2025-01-07T10:30:00Z
    last_generated: 2025-01-07T14:15:30Z
    path: README.md
    template_used:
      name: readme-amplifier
      path: .doc-evergreen/templates/readme-amplifier.v2.md
    previous_versions:
      - timestamp: 2025-01-07T10:30:00Z
        backup_path: .doc-evergreen/versions/README.md.2025-01-07T10-30-00.bak
        template_used:
          name: readme-amplifier
          path: .doc-evergreen/templates/readme-amplifier.v1.md
      - timestamp: 2025-01-07T14:00:30Z
        backup_path: .doc-evergreen/versions/README.md.2025-01-07T14-00-30.bak
        template_used:
          name: readme-amplifier
          path: .doc-evergreen/templates/readme-amplifier.v2.md
    sources:
      - "src/**/*.py"
      - "pyproject.toml"
      - "CLAUDE.md"
    about: "Main project README"

  docs/USER_GUIDE.md:
    created: 2025-01-07T11:00:00Z
    last_generated: 2025-01-07T11:00:00Z
    path: docs/USER_GUIDE.md
    template_used:
      name: user-guide-cli-focused
      path: .doc-evergreen/templates/user-guide-cli-focused.v1.md
    previous_versions: []
    sources:
      - "src/cli/*.py"
      - "examples/*.py"
      - "README.md"
    about: "User guide for CLI usage"
```

### Template Metadata

Each template file includes YAML frontmatter:

```markdown
---
name: readme-amplifier
version: 2
created: 2025-01-07T10:30:00Z
derived_from: scenarios/doc_evergreen/templates/readme.md
customizations:
  - Added project-specific sections
  - Adjusted tone for technical audience
  - Included amplifier-specific examples
---

# README Generation Template

[... template content ...]
```

---

## Commands Specification

### `create` Command

**Purpose**: Create new documentation from scratch.

**Signature**:
```bash
doc-evergreen create \
    --about <topic> \
    --output <path> \
    [--sources <globs>] \
    [--template <name>] \
    [--dry-run]
```

**Parameters**:
- `--about` (required): Description of what the doc should cover
- `--output` (required): Full path including filename (e.g., `docs/API_REFERENCE.md`)
- `--sources` (optional): Glob patterns for files to include (default: auto-discover)
- `--template` (optional): Specific template to use (default: auto-select)
- `--dry-run` (optional): Show what would be generated without writing files

**Behavior**:
1. Validate all required parameters present
2. If `--sources` not provided, auto-discover files based on `--about`
3. If `--template` not provided, auto-select based on `--about`
4. Generate template if doesn't exist, or customize existing
5. Call LLM to generate document
6. Save document to `--output` path
7. Update history.yaml
8. Report success and location of generated file

**Exit Codes**:
- `0`: Success
- `1`: Missing required parameters
- `2`: File discovery failed
- `3`: Template creation failed
- `4`: LLM generation failed
- `5`: File write failed

**Example**:
```bash
# Full specification
$ doc-evergreen create \
    --about "API reference for knowledge synthesis" \
    --output "docs/API_REFERENCE.md" \
    --sources "src/knowledge_synthesis/**/*.py"

# Auto-discovery
$ doc-evergreen create \
    --about "Contributing guide" \
    --output "docs/CONTRIBUTING.md"

# Dry run
$ doc-evergreen create \
    --about "User guide" \
    --output "docs/USER_GUIDE.md" \
    --dry-run
```

---

### `regenerate` Command

**Purpose**: Regenerate documentation from saved configuration.

**Signature**:
```bash
doc-evergreen regenerate <doc-path>
doc-evergreen regenerate --all
```

**Parameters**:
- `<doc-path>` (required if not --all): Path to document to regenerate
- `--all` (flag): Regenerate all configured documents
- `--dry-run` (optional): Show what would be regenerated

**Behavior**:
1. Load configuration from history.yaml
2. If `<doc-path>` not in history, fail with helpful message
3. Use saved template and sources
4. Backup existing document
5. Generate fresh document
6. Update history.yaml with new version entry
7. Report success

**Exit Codes**:
- `0`: Success
- `1`: Document not found in history
- `2`: Configuration corrupted
- `3`: LLM generation failed
- `4`: File write failed

**Example**:
```bash
# Regenerate single doc
$ doc-evergreen regenerate README.md

# Regenerate all
$ doc-evergreen regenerate --all

# Dry run
$ doc-evergreen regenerate README.md --dry-run
```

---

### `update` Command (Future)

**Purpose**: Update existing document (alias for create with analysis).

**Deferred for post-MVP**: Can be implemented as create command with additional analysis step.

---

## Core Components

### 1. File Discovery (`core/discovery.py`)

**Responsibilities**:
- Parse glob patterns
- Find matching files
- Validate UTF-8 encoding
- Respect .gitignore patterns
- Auto-discover files based on topic

**Key Functions**:

```python
def find_files(patterns: list[str], base_path: Path) -> list[Path]:
    """Find files matching glob patterns."""

def validate_utf8(file_path: Path) -> bool:
    """Check if file is valid UTF-8."""

def auto_discover_files(topic: str, repo_path: Path) -> list[Path]:
    """Auto-discover relevant files based on topic."""
```

**Auto-Discovery Logic**:
1. Analyze topic to determine doc type
2. Scan repo structure (use gitignore patterns)
3. Score files by relevance using heuristics:
   - Filename matches (e.g., "API" in topic → find api.py files)
   - Directory structure (e.g., "CLI" → look in src/cli/)
   - File types (e.g., "Python API" → .py files)
4. Return top N most relevant files

**Testing**:
- Unit tests with mock file system
- Test glob pattern expansion
- Test UTF-8 validation
- Test auto-discovery with sample topics

---

### 2. Template Management (`core/template.py`)

**Responsibilities**:
- Load built-in starter templates
- Create customized templates via LLM
- Version templates automatically
- Load templates from history

**Key Functions**:

```python
def load_builtin_template(template_name: str) -> str:
    """Load template from scenarios/doc_evergreen/templates/."""

def create_custom_template(
    builtin_template: str,
    about: str,
    existing_doc: str | None = None
) -> tuple[str, str]:
    """
    Create customized template via LLM.
    Returns (template_content, template_name).
    """

def save_template(
    template_content: str,
    template_name: str,
    repo_path: Path
) -> Path:
    """
    Save template with automatic versioning.
    Returns path to saved template.
    """

def load_template_from_history(
    template_path: str,
    repo_path: Path
) -> str:
    """Load previously saved template."""
```

**Template Versioning**:
- Check if template with same name exists
- If exists, increment version number
- Save as `{name}.v{N}.md`
- Update history.yaml with new version path

**Testing**:
- Test loading built-in templates
- Test template customization
- Test versioning logic
- Test template metadata parsing

---

### 3. LLM Generator (`core/generator.py`)

**Responsibilities**:
- Direct Anthropic API calls
- Read API key from `.claude/api_key.txt`
- Generate documents from template + sources
- Handle errors and retries

**Key Functions**:

```python
def load_api_key() -> str:
    """Load Anthropic API key from .claude/api_key.txt."""

def generate_document(
    template: str,
    sources: dict[str, str],  # path -> content
    about: str
) -> str:
    """
    Generate document via direct Anthropic API call.
    Returns generated markdown content.
    """

def customize_template(
    builtin_template: str,
    about: str,
    existing_doc: str | None = None
) -> str:
    """
    Customize template via LLM.
    Returns customized template content.
    """
```

**API Integration**:
```python
import anthropic

client = anthropic.Anthropic(api_key=load_api_key())

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    temperature=0.3,
    messages=[{
        "role": "user",
        "content": prompt
    }]
)
```

**Prompt Structure**:
```
You are generating documentation for a software project.

Template:
{template_content}

Source Files:
{source_files_content}

Topic: {about}

Instructions:
1. Follow the template structure
2. Extract relevant information from source files
3. Generate clear, accurate documentation
4. Use markdown formatting

Generate the documentation:
```

**Testing**:
- Mock API calls for testing
- Test prompt generation
- Test error handling
- Test with actual API (integration tests)

---

### 4. History Manager (`core/history.py`)

**Responsibilities**:
- Read/write history.yaml
- Validate structure
- Query doc configurations
- Update version history

**Key Functions**:

```python
def load_history(repo_path: Path) -> dict:
    """Load history.yaml, create if doesn't exist."""

def save_history(history: dict, repo_path: Path) -> None:
    """Save history.yaml with validation."""

def get_doc_config(doc_path: str, repo_path: Path) -> dict | None:
    """Get configuration for specific document."""

def add_doc_entry(
    doc_path: str,
    config: dict,
    repo_path: Path
) -> None:
    """Add or update document configuration."""

def add_version_entry(
    doc_path: str,
    backup_path: str,
    template_path: str,
    repo_path: Path
) -> None:
    """Add version entry to document history."""
```

**Validation**:
- Ensure required fields present
- Validate paths exist
- Check timestamp formats
- Verify template references

**Testing**:
- Test YAML read/write
- Test validation logic
- Test configuration queries
- Test concurrent access (if needed)

---

### 5. Version Control (`core/versioning.py`)

**Responsibilities**:
- Backup documents before regeneration
- Create timestamped backups
- Manage backup storage

**Key Functions**:

```python
def backup_document(
    doc_path: Path,
    repo_path: Path
) -> Path:
    """
    Backup document to .doc-evergreen/versions/.
    Returns backup path.
    """

def restore_version(
    backup_path: Path,
    doc_path: Path
) -> None:
    """Restore document from backup (future feature)."""

def list_versions(doc_path: str, repo_path: Path) -> list[dict]:
    """List all versions of a document."""
```

**Backup Path Format**:
```
.doc-evergreen/versions/{doc_path}.{timestamp}.bak

Examples:
.doc-evergreen/versions/README.md.2025-01-07T10-30-00.bak
.doc-evergreen/versions/docs/USER_GUIDE.md.2025-01-07T11-00-00.bak
```

**Testing**:
- Test backup creation
- Test path generation
- Test directory creation
- Test version listing

---

## LLM Integration Details

### API Configuration

**API Key Location**: `.claude/api_key.txt`
**Model**: `claude-sonnet-4-20250514`
**Max Tokens**: 4000
**Temperature**: 0.3 (deterministic)

### Key Prompts

#### 1. Template Customization Prompt

```python
prompt = f"""You are customizing a documentation template for a software project.

Built-in Template:
{builtin_template}

Project Context:
- Topic: {about}
{"- Existing Document Structure: " + existing_doc if existing_doc else ""}

Task:
Create a customized version of this template that:
1. Maintains the overall structure
2. Adjusts tone/style for the specific project
3. Adds project-specific sections if needed
4. Includes appropriate examples

Return only the customized template in markdown format with YAML frontmatter:
---
name: {template_name}
version: 1
derived_from: {builtin_name}
customizations:
  - [list key changes]
---

[template content]
"""
```

#### 2. Document Generation Prompt

```python
prompt = f"""You are generating documentation for a software project.

Template:
{template}

Source Files:
{format_sources(sources)}

Topic: {about}

Instructions:
1. Follow the template structure exactly
2. Extract relevant information from source files
3. Generate clear, accurate, technical documentation
4. Use proper markdown formatting
5. Include code examples where appropriate
6. Ensure all links are valid

Generate the complete documentation:
"""
```

#### 3. Auto-Discovery Prompt

```python
prompt = f"""You are helping identify relevant files for documentation.

Repository Structure:
{repo_structure}

Documentation Topic: {about}

Task:
Identify the most relevant files for this documentation topic.
Consider:
- File names and paths
- File types
- Directory organization
- Common patterns

Return a JSON list of file paths in order of relevance:
["path/to/file1.py", "path/to/file2.md", ...]
"""
```

---

## Implementation Chunks (Testable Increments)

### Chunk 1: CLI Skeleton and Parameter Validation

**Goal**: Basic CLI structure with proper parameter handling.

**Scope**:
- Set up Click CLI framework
- Implement `create` command with all parameters
- Validate required parameters
- Show helpful error messages
- Implement `--help` text

**Files**:
- `cli.py`
- `commands/create.py`

**Testing**:
```bash
# Should show error for missing params
$ doc-evergreen create --about "test"
# Error: Missing required parameter: --output

# Should show help
$ doc-evergreen create --help

# Should validate (but not execute yet)
$ doc-evergreen create --about "test" --output "test.md"
# Success: Parameters validated (not implemented yet)
```

**Acceptance Criteria**:
- [ ] CLI responds to commands
- [ ] Required parameters enforced
- [ ] Help text displays correctly
- [ ] Error messages are clear

---

### Chunk 2: History.yaml Management

**Goal**: Read/write and query history.yaml.

**Scope**:
- Load/save YAML files
- Create history structure if doesn't exist
- Query document configuration
- Add new document entries
- Update version history

**Files**:
- `core/history.py`
- `tests/test_history.py`

**Testing**:
```python
# Unit tests
def test_create_history():
    # Should create .doc-evergreen/history.yaml

def test_add_doc_entry():
    # Should add new document configuration

def test_get_doc_config():
    # Should retrieve existing configuration

def test_add_version_entry():
    # Should add version to document history
```

**Acceptance Criteria**:
- [ ] Creates history.yaml if doesn't exist
- [ ] Reads existing history correctly
- [ ] Adds new entries
- [ ] Updates existing entries
- [ ] Validates YAML structure

---

### Chunk 3: File Discovery and Gathering

**Goal**: Find and read source files.

**Scope**:
- Glob pattern expansion
- UTF-8 validation
- File content reading
- Auto-discovery (basic heuristics)

**Files**:
- `core/discovery.py`
- `tests/test_discovery.py`

**Testing**:
```python
# Unit tests
def test_glob_expansion():
    # Should expand patterns like "src/**/*.py"

def test_utf8_validation():
    # Should validate file encoding

def test_read_files():
    # Should read file contents

def test_auto_discovery():
    # Should find relevant files based on topic
```

**Manual Testing**:
```bash
# Create test command to exercise discovery
$ doc-evergreen test-discovery --sources "src/**/*.py"
# Outputs: Found 45 files (234 KB)
```

**Acceptance Criteria**:
- [ ] Glob patterns expand correctly
- [ ] UTF-8 validation works
- [ ] Files are read successfully
- [ ] Auto-discovery finds relevant files

---

### Chunk 4: Template Management and Versioning

**Goal**: Load, customize, and version templates.

**Scope**:
- Load built-in templates
- Parse template metadata
- Save templates with versioning
- Load templates from history

**Files**:
- `core/template.py`
- `templates/readme.md` (built-in example)
- `tests/test_template.py`

**Testing**:
```python
# Unit tests
def test_load_builtin():
    # Should load from scenarios/doc_evergreen/templates/

def test_save_template():
    # Should save to .doc-evergreen/templates/

def test_versioning():
    # Should increment version on save
    # readme.v1.md → readme.v2.md

def test_parse_metadata():
    # Should extract YAML frontmatter
```

**Acceptance Criteria**:
- [ ] Built-in templates load correctly
- [ ] Templates save with proper versioning
- [ ] Metadata is preserved
- [ ] Version numbers increment correctly

---

### Chunk 5: LLM Integration with Direct API Calls

**Goal**: Connect to Anthropic API for generation.

**Scope**:
- Load API key from `.claude/api_key.txt`
- Direct API calls to Anthropic
- Template customization via LLM
- Document generation via LLM
- Error handling and retries

**Files**:
- `core/generator.py`
- `tests/test_generator.py` (with mocks)

**Testing**:
```python
# Unit tests (mocked API)
def test_load_api_key():
    # Should read from .claude/api_key.txt

def test_customize_template(mock_api):
    # Should call API with correct prompt

def test_generate_document(mock_api):
    # Should generate doc from template + sources

# Integration test (real API, manual)
def test_real_api_call():
    # Actual API call for validation
```

**Manual Testing**:
```bash
# Test with real API
$ doc-evergreen test-llm \
    --template "templates/readme.md" \
    --sources "README.md"
# Outputs: Generated test document
```

**Acceptance Criteria**:
- [ ] API key loads correctly
- [ ] API calls succeed
- [ ] Prompts are well-formed
- [ ] Responses are parsed correctly
- [ ] Errors are handled gracefully

---

### Chunk 6: Document Generation and Versioning

**Goal**: Complete end-to-end generation flow.

**Scope**:
- Backup existing documents
- Generate new documents
- Write to output path
- Update history.yaml
- Implement dry-run mode

**Files**:
- `core/versioning.py`
- `commands/create.py` (complete implementation)
- `tests/test_integration.py`

**Testing**:
```bash
# End-to-end test
$ doc-evergreen create \
    --about "Test documentation" \
    --output "test_docs/TEST.md" \
    --sources "README.md" \
    --dry-run

# Outputs:
# Would generate: test_docs/TEST.md
# Using template: readme (customized)
# From sources: README.md (12 KB)
# [Preview of first 500 chars]

# Actual generation
$ doc-evergreen create \
    --about "Test documentation" \
    --output "test_docs/TEST.md" \
    --sources "README.md"

# Outputs:
# ✓ test_docs/TEST.md created
# ✓ Configuration saved to .doc-evergreen/history.yaml
```

**Acceptance Criteria**:
- [ ] Documents backup before regeneration
- [ ] New documents are generated
- [ ] Files written to correct location
- [ ] History.yaml updated correctly
- [ ] Dry-run shows preview without writing

---

### Chunk 7: Regenerate Command

**Goal**: Implement regeneration from history.

**Scope**:
- Load configuration from history
- Regenerate single document
- Regenerate all documents
- Update version history

**Files**:
- `commands/regenerate.py`
- `tests/test_regenerate.py`

**Testing**:
```bash
# Regenerate single doc
$ doc-evergreen regenerate test_docs/TEST.md

# Outputs:
# Loading configuration from history...
# Backing up current version...
# Regenerating test_docs/TEST.md...
# ✓ test_docs/TEST.md updated

# Regenerate all
$ doc-evergreen regenerate --all

# Outputs:
# Regenerating 3 documents...
#   [1/3] README.md ✓
#   [2/3] docs/USER_GUIDE.md ✓
#   [3/3] test_docs/TEST.md ✓
```

**Acceptance Criteria**:
- [ ] Loads config from history correctly
- [ ] Regenerates documents successfully
- [ ] Version history updated
- [ ] Works with --all flag

---

## Testing Strategy

### Unit Tests

**Coverage**: Individual functions in isolation
**Tools**: pytest, mocks
**Files**: `tests/test_*.py`

**Key Areas**:
- History YAML read/write
- Template versioning logic
- File discovery and glob expansion
- API prompt generation

### Integration Tests

**Coverage**: Component interactions
**Tools**: pytest with temp directories
**Setup**: Create test repo structure

**Key Scenarios**:
- Create doc with auto-discovery
- Regenerate from history
- Template versioning flow
- Complete end-to-end generation

### Manual Testing

**Coverage**: Real-world usage
**Setup**: Use this repo as test subject

**Test Cases**:
1. Generate README.md
2. Generate docs/USER_GUIDE.md
3. Regenerate after code changes
4. Test with git hooks
5. Test dry-run mode

### Acceptance Testing

**Coverage**: User-facing scenarios
**Setup**: Clean repo, follow README

**Scenarios**:
1. First-time setup
2. Assistant-guided creation
3. Automated regeneration
4. Template customization
5. Version recovery

---

## Edge Cases and Error Handling

### File System Errors

- **Missing directories**: Create parent directories automatically
- **Permission errors**: Clear error message, exit cleanly
- **Disk full**: Fail gracefully, don't corrupt history
- **Symbolic links**: Follow or warn, configurable

### LLM API Errors

- **Rate limiting**: Retry with exponential backoff
- **Timeout**: Configurable timeout, clear error
- **Invalid response**: Validate, retry once, then fail
- **API key invalid**: Clear error message, check key location

### Configuration Errors

- **Corrupted history.yaml**: Validate, backup, attempt repair
- **Missing template**: Fall back to built-in, warn user
- **Invalid glob patterns**: Validate, show example
- **No files found**: Clear error, suggest alternatives

### User Input Errors

- **Invalid paths**: Validate, show absolute path being used
- **Missing required params**: Show which are missing
- **Contradictory flags**: Clear error, show correct usage

### Concurrency Issues

- **Multiple regenerations**: File locking or warn
- **Git merge conflicts**: Document manual resolution steps
- **History.yaml conflicts**: Provide merge strategy

---

## Dependencies

### Python Requirements

```toml
[project]
name = "doc-evergreen"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "click>=8.1.0",        # CLI framework
    "pyyaml>=6.0",         # YAML parsing
    "anthropic>=0.18.0",   # Direct API access
    "pathspec>=0.11.0",    # Gitignore handling
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.1.0",
]
```

### External Dependencies

- **Anthropic API**: Requires API key in `.claude/api_key.txt`
- **Git**: For version control (optional, enhances features)

---

## Deployment and Usage

### Installation (Development)

```bash
cd scenarios/doc_evergreen
make install
```

### Make Targets

```makefile
.PHONY: install test check run

install:
    uv sync

test:
    uv run pytest tests/ -v

check:
    uv run ruff check .
    uv run pyright .

run:
    uv run python -m doc_evergreen.cli
```

### Git Hook Setup (User-facing)

```bash
# .git/hooks/pre-commit
#!/bin/bash
doc-evergreen regenerate --all --non-interactive
if [ $? -ne 0 ]; then
  echo "Documentation update failed"
  exit 1
fi
```

### CI/CD Integration

```yaml
# .github/workflows/docs.yml
name: Update Documentation
on:
  push:
    branches: [main]
    paths: ['src/**', 'examples/**']

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Regenerate docs
        run: doc-evergreen regenerate --all
      - name: Commit if changed
        run: |
          git add docs/ README.md
          git commit -m "chore: update docs" || echo "No changes"
          git push
```

---

## Future Enhancements (Post-MVP)

### Phase 2 Features

- [ ] `update` command (analyze existing doc structure)
- [ ] `list` command (show all configured docs)
- [ ] `show` command (display doc configuration)
- [ ] `forget` command (remove doc from history)
- [ ] `diff` command (compare versions)
- [ ] `restore` command (revert to previous version)

### Advanced Features

- [ ] Multi-language support (currently Python-focused)
- [ ] Custom template inheritance
- [ ] Template marketplace/sharing
- [ ] Integration with documentation sites (MkDocs, Sphinx)
- [ ] Incremental updates (only regenerate changed sections)
- [ ] Collaborative editing (merge user edits with generated content)

### Performance Optimizations

- [ ] Cache LLM responses
- [ ] Parallel document generation
- [ ] Smart file chunking for large repos
- [ ] Incremental source file scanning

---

## Success Metrics

### MVP Success Criteria

- [ ] Can create new documentation from CLI
- [ ] Can regenerate documentation automatically
- [ ] Templates are customized per-project
- [ ] Version history is preserved
- [ ] Works in git hooks without interaction
- [ ] Dry-run mode works correctly

### Quality Metrics

- [ ] Unit test coverage >80%
- [ ] Integration tests pass
- [ ] Manual testing scenarios complete
- [ ] Documentation is comprehensive
- [ ] Error messages are helpful

### User Experience Metrics

- [ ] Time to first doc generation: <5 minutes
- [ ] Time to setup automation: <10 minutes
- [ ] Assistant can use tool without human intervention (for regeneration)
- [ ] Error recovery is straightforward

---

## Timeline and Milestones

### Week 1: Foundation
- [ ] Chunk 1: CLI skeleton
- [ ] Chunk 2: History management
- [ ] Chunk 3: File discovery

### Week 2: Core Features
- [ ] Chunk 4: Template management
- [ ] Chunk 5: LLM integration
- [ ] Chunk 6: Document generation

### Week 3: Completion
- [ ] Chunk 7: Regenerate command
- [ ] Testing and bug fixes
- [ ] Documentation
- [ ] User acceptance testing

---

## References and Resources

### Related Documents
- `scenarios/doc_evergreen/README.md` - User guide and assistant reference
- `CLAUDE.md` - Project guidelines
- `AGENTS.md` - Agent usage patterns

### External References
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Click Documentation](https://click.palletsprojects.com/)
- [YAML Specification](https://yaml.org/spec/1.2.2/)

### Design Decisions
- Direct API calls (not SDK) to avoid Claude Code interference
- YAML for configuration (human-readable, git-friendly)
- Automatic template versioning (simplifies management)
- Deterministic tool + intelligent assistant (separation of concerns)

---

## Appendix

### Example: Complete Generation Flow

```bash
# 1. User creates new doc
$ doc-evergreen create \
    --about "API reference for knowledge synthesis system" \
    --output "docs/API_REFERENCE.md" \
    --sources "src/knowledge_synthesis/**/*.py"

# Tool executes:
# 1. Validates parameters ✓
# 2. Discovers/reads source files ✓
# 3. Loads built-in template: api-reference.md ✓
# 4. Customizes template via LLM ✓
# 5. Saves template: .doc-evergreen/templates/api-reference-ks.v1.md ✓
# 6. Generates document via LLM ✓
# 7. Writes to: docs/API_REFERENCE.md ✓
# 8. Updates history.yaml ✓

# Output:
✓ docs/API_REFERENCE.md created (8.2 KB)
✓ Template saved: api-reference-ks.v1.md
✓ Configuration saved to .doc-evergreen/history.yaml

To regenerate after changes:
  doc-evergreen regenerate docs/API_REFERENCE.md

# 2. User modifies code, regenerates
$ doc-evergreen regenerate docs/API_REFERENCE.md

# Tool executes:
# 1. Loads config from history.yaml ✓
# 2. Loads template: api-reference-ks.v1.md ✓
# 3. Reads source files ✓
# 4. Backs up current doc ✓
# 5. Generates fresh document ✓
# 6. Writes to: docs/API_REFERENCE.md ✓
# 7. Updates history with version entry ✓

# Output:
✓ Backed up: .doc-evergreen/versions/docs/API_REFERENCE.md.2025-01-07T15-30-00.bak
✓ docs/API_REFERENCE.md regenerated (8.4 KB)

To compare versions:
  diff docs/API_REFERENCE.md .doc-evergreen/versions/docs/API_REFERENCE.md.2025-01-07T15-30-00.bak

# 3. Git hook regenerates all docs
$ doc-evergreen regenerate --all

# Tool executes:
# 1. Loads all configs from history.yaml ✓
# 2. Regenerates each doc ✓
# 3. Updates version history ✓

# Output:
Regenerating 3 documents...
  [1/3] README.md ✓
  [2/3] docs/USER_GUIDE.md ✓
  [3/3] docs/API_REFERENCE.md ✓

All documentation updated successfully.
```

---

**Document Version**: 1.0
**Last Updated**: 2025-01-07
**Status**: Ready for Implementation
**Next Step**: Begin Chunk 1 - CLI Skeleton
