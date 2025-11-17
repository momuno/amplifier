# Sprint 3: CLI + Templates

**Duration**: 3 days (Week 2, Days 1-3)
**Goal**: Build proper CLI interface with template selection
**Value Delivered**: Reusable tool for any documentation file

---

## Why This Sprint?

Sprints 1-2 proved the concept works and is safe. Now make it **reusable beyond just README**.

**The Problem**: Currently hardcoded for one file
- Only works for README.md
- Single template baked in
- No configuration
- Not a "tool" yet, just a script

**The Solution**: Proper CLI tool
- Works for any doc file
- Multiple templates for different doc types
- Project configuration
- Feels like a real developer tool

**Value**: Transforms from "README regenerator" to "documentation maintenance tool"

---

## What You'll Have After This Sprint

A proper CLI tool:
```bash
# Regenerate README
amplifier doc-update README.md --template readme

# Regenerate API docs
amplifier doc-update docs/API.md --template api-reference

# Use custom template
amplifier doc-update CONTRIBUTING.md --template custom/contributing

# List available templates
amplifier doc-update --list-templates
```

**Integration**: Added as subcommand to existing `amplifier` CLI

---

## Deliverables

### 1. CLI Interface (~200 lines)
**File**: `scenarios/doc_evergreen/cli.py`

**What it does**: Proper command-line interface with arguments and options

**Why this sprint**: Need professional tool UX

**Implementation notes**:
- Use Click (already in amplifier project)
- Integrate as `amplifier doc-update` subcommand
- Arguments: `target_file` (positional)
- Options:
  - `--template <name>` (template to use)
  - `--sources <files>` (defer to Sprint 4, use defaults)
  - `--list-templates` (show available templates)
  - `--no-review` (skip review workflow, for automation)
- Help text with examples
- Proper error messages

**Example implementation**:
```python
import click
from pathlib import Path

@click.command("doc-update")
@click.argument("target_file", type=click.Path())
@click.option("--template", "-t", help="Template to use")
@click.option("--list-templates", is_flag=True, help="List available templates")
@click.option("--no-review", is_flag=True, help="Skip review workflow")
def doc_update(target_file, template, list_templates, no_review):
    """Regenerate documentation file using template and source context"""

    if list_templates:
        show_available_templates()
        return

    # Detect template from target file if not specified
    if not template:
        template = detect_template(target_file)

    # Load template
    template_content = load_template(template)

    # Gather context (hardcoded for now, Sprint 4 adds control)
    context = gather_context()

    # Generate preview
    preview = generate_preview(template_content, context, target_file)

    # Review workflow (unless --no-review)
    if not no_review:
        show_diff(target_file, preview)
        action = review_changes(target_file, preview)
        handle_action(action, target_file, preview)
    else:
        accept_changes(target_file, preview)
```

### 2. Template Library (~300 lines total)
**Directory**: `scenarios/doc_evergreen/templates/`

**What it does**: Collection of templates for different doc types

**Why this sprint**: Support multiple documentation types

**Templates to create**:

**2a. README Template** (`readme.md`):
- Project overview
- Installation
- Usage
- Configuration
- Contributing
- License

**2b. API Reference Template** (`api-reference.md`):
- Endpoint listing
- Request/response formats
- Authentication
- Error codes
- Examples

**2c. Contributing Guide Template** (`contributing.md`):
- How to contribute
- Development setup
- Code standards
- PR process
- Testing requirements

**Template format** (markdown with guidance):
```markdown
# {{project_name}}

{{project_tagline}}

## Overview

[Provide a high-level overview of what this project does and why it exists.
Include the core problem it solves and primary use cases.]

## Installation

[Include installation instructions for different platforms/methods.
Show prerequisites and common gotchas.]

...
```

**Template metadata** (optional YAML frontmatter):
```yaml
---
name: README Template
description: Standard README structure for open-source projects
suggested_sources:
  - README.md
  - pyproject.toml
  - src/main.py
---
```

### 3. Template Manager (~150 lines)
**File**: `template_manager.py`

**What it does**: Discovers, loads, and validates templates

**Why this sprint**: Need organized template handling

**Implementation notes**:
- Discover templates in `templates/` directory
- Load template by name or path
- Parse template metadata (if present)
- Validate template structure
- Suggest default template based on target filename

**Key functions**:
```python
def list_templates() -> list[TemplateInfo]:
    """List all available templates"""
    template_dir = Path(__file__).parent / "templates"
    return [
        parse_template_metadata(t)
        for t in template_dir.glob("*.md")
    ]

def load_template(name_or_path: str) -> str:
    """Load template content by name or path"""
    if Path(name_or_path).exists():
        return Path(name_or_path).read_text()

    template_path = find_template_by_name(name_or_path)
    return template_path.read_text()

def detect_template(target_file: str) -> str:
    """Suggest template based on target filename"""
    filename = Path(target_file).name.lower()

    mappings = {
        "readme.md": "readme",
        "contributing.md": "contributing",
        "api.md": "api-reference",
    }

    return mappings.get(filename, "readme")  # Default to readme
```

### 4. Configuration File (~50 lines)
**File**: `.doc-evergreen.yaml` (in project root)

**What it does**: Project-specific configuration for doc regeneration

**Why this sprint**: Reduce repeated CLI arguments

**Configuration format**:
```yaml
# Doc-Evergreen Configuration

# Default template directory
template_dir: ./doc-templates

# File-specific settings
files:
  README.md:
    template: readme
    sources:
      - README.md
      - pyproject.toml
      - amplifier/cli.py

  docs/API.md:
    template: api-reference
    sources:
      - amplifier/api/
      - docs/api-spec.yaml

# Default sources (if not specified per-file)
default_sources:
  - README.md
  - pyproject.toml

# LLM settings
llm:
  provider: claude
  model: claude-3-5-sonnet-20241022
```

**Config loader**:
```python
def load_config() -> Config:
    """Load .doc-evergreen.yaml from project root"""
    config_path = find_project_root() / ".doc-evergreen.yaml"

    if not config_path.exists():
        return default_config()

    return parse_yaml_config(config_path)
```

### 5. Updated Context Gatherer (~100 lines)
**File**: `context.py` (enhanced from Sprint 1)

**What it does**: Use config-based sources instead of hardcoded

**Why this sprint**: Template-specific context needs

**Implementation notes**:
- Read sources from config file
- Fall back to defaults if not configured
- Support glob patterns (`src/**/*.py`)
- Filter by relevance to target doc

**Enhanced function**:
```python
def gather_context(target_file: str, config: Config) -> str:
    """Gather source files based on config"""

    # Get sources for this specific file
    file_config = config.files.get(target_file)
    if file_config and file_config.sources:
        sources = file_config.sources
    else:
        sources = config.default_sources

    # Expand glob patterns
    expanded = expand_source_patterns(sources)

    # Read and concatenate
    context_parts = []
    for source in expanded:
        if Path(source).exists():
            content = read_source_file(source)
            context_parts.append(content)

    return "\n\n".join(context_parts)
```

### 6. Integration with Amplifier CLI (~50 lines)
**File**: `amplifier/cli.py` (add subcommand)

**What it does**: Registers `doc-update` as amplifier subcommand

**Why this sprint**: Consistent with project CLI structure

**Implementation notes**:
- Import doc_evergreen CLI function
- Register as subcommand group
- Maintain consistent UX with other amplifier commands

**Integration**:
```python
# In amplifier/cli.py
from scenarios.doc_evergreen.cli import doc_update

@click.group()
def cli():
    """Amplifier CLI"""
    pass

# Add doc-update subcommand
cli.add_command(doc_update)
```

### 7. Tests (~200 lines)
**File**: `test_sprint3.py`

**TDD Approach - Write tests FIRST**:

**Day 1 - Template Management**:
- 🔴 Write test: `test_list_templates()`
- 🔴 Write test: `test_load_template_by_name()`
- 🔴 Write test: `test_detect_template_from_filename()`
- 🟢 Implement: Template manager
- 🔵 Refactor: Template discovery logic
- ✅ Commit

**Day 2 - CLI Interface**:
- 🔴 Write test: `test_cli_with_template_option()`
- 🔴 Write test: `test_cli_list_templates()`
- 🔴 Write test: `test_cli_no_review_flag()`
- 🟢 Implement: CLI commands
- 🔵 Refactor: Argument parsing
- ✅ Commit

**Day 3 - Configuration**:
- 🔴 Write test: `test_load_config_file()`
- 🔴 Write test: `test_config_file_sources()`
- 🟢 Implement: Config loading
- 🟢 Integrate: CLI + templates + config
- 🔵 Refactor: End-to-end flow
- ✅ Commit

**Test coverage**:
- Template discovery and loading
- CLI argument parsing (use Click's testing utilities)
- Configuration file loading
- Template detection from filename
- Integration with review workflow (from Sprint 2)

**Manual Testing Checklist**:
- [ ] `amplifier doc-update README.md` works
- [ ] `amplifier doc-update --list-templates` shows templates
- [ ] `amplifier doc-update --template readme README.md` uses specific template
- [ ] Config file is loaded and respected
- [ ] Multiple templates work correctly
- [ ] Help text is clear

---

## What Gets Punted (Deliberately Excluded)

### ❌ Template marketplace/sharing
- **Why**: Start with local templates only
- **Reconsider**: v2 if users want to share templates

### ❌ Template validation/linting
- **Why**: Simple templates are hard to break
- **Reconsider**: v2 if template errors are common

### ❌ Template variables/substitution
- **Why**: LLM handles content generation, not templating engine
- **Reconsider**: v2 if needed for advanced use cases

### ❌ Interactive template creation
- **Why**: Manual template authoring is fine for MVP
- **Reconsider**: v2 (template builder wizard)

### ❌ Template versioning
- **Why**: Git provides versioning
- **Reconsider**: v2 if template compatibility issues arise

### ❌ GUI/web interface
- **Why**: CLI-first for developer workflows
- **Reconsider**: v2 for non-technical users

---

## Dependencies

**Requires from previous sprints**:
- Sprint 1: `generator.py` (generation logic)
- Sprint 2: `preview.py`, `diff.py`, `reviewer.py` (review workflow)

**Provides for future sprints**:
- CLI framework
- Template system
- Configuration pattern
- Multi-file support foundation

---

## Acceptance Criteria

### Must Have
- ✅ CLI command runs from terminal: `amplifier doc-update <file>`
- ✅ Multiple templates available and selectable
- ✅ Template auto-detection from filename works
- ✅ `--list-templates` shows available templates
- ✅ Configuration file is loaded and used
- ✅ Works for at least 3 different doc types (README, API, Contributing)
- ✅ Integrates with existing amplifier CLI
- ✅ Help text is clear and useful

### Nice to Have (Defer if time constrained)
- ❌ Template metadata validation
- ❌ Custom template directory support
- ❌ Template preview before using

---

## Technical Approach

### TDD Red-Green-Refactor Cycle

**Every feature follows this pattern**:

1. **🔴 RED Phase** (~40% of time):
   - Write test that fails
   - Example: `assert "readme" in list_templates()`

2. **🟢 GREEN Phase** (~40% of time):
   - Write minimal code to pass test
   - Example: Basic template discovery

3. **🔵 REFACTOR Phase** (~20% of time):
   - Improve code quality
   - Example: Extract path handling, add error cases

4. **✅ COMMIT**:
   - All tests green = commit point

### CLI Framework: Click

**Why Click**:
- Already used in amplifier project
- Excellent testing utilities
- Clean syntax
- Good help text generation

**Testing pattern**:
```python
from click.testing import CliRunner

def test_doc_update_command():
    runner = CliRunner()
    result = runner.invoke(doc_update, ["README.md", "--template", "readme"])

    assert result.exit_code == 0
    assert "Generated preview" in result.output
```

### Template Format

**Keep it simple**:
- Plain markdown files
- Optional YAML frontmatter for metadata
- Human-readable and editable
- No complex templating syntax (LLM generates content)

**Template structure**:
```markdown
---
name: README Template
description: Standard README for open-source projects
---

# {{project_name}}

[Section guidance for LLM here...]

## Installation

[Installation instructions guidance...]
```

### Configuration File: YAML

**Why YAML**:
- Human-friendly
- Supports comments
- Standard for configuration
- Easy to parse (PyYAML)

**Optional by design**:
- Tool works without config (sensible defaults)
- Config provides convenience, not requirement

---

## Implementation Order

### Day 1: Template System (Foundation)

**Morning** (4 hours):
- 🔴 Write test: Template discovery
- 🔴 Write test: Template loading
- 🟢 Implement: `template_manager.py`
- 🔵 Refactor: Path handling
- ✅ Commit

- Create 3 template files:
  - `templates/readme.md`
  - `templates/api-reference.md`
  - `templates/contributing.md`

**Afternoon** (4 hours):
- 🔴 Write test: Template detection
- 🟢 Implement: Auto-detection logic
- Test with real template files
- ✅ Commit (template system working)

### Day 2: CLI Interface (User Interaction)

**Morning** (4 hours):
- 🔴 Write test: CLI command parsing
- 🔴 Write test: Template selection
- 🟢 Implement: `cli.py` with Click
- 🔵 Refactor: Argument validation
- ✅ Commit

**Afternoon** (4 hours):
- Integrate CLI with Sprint 1-2 components
- Wire template manager into CLI
- Test end-to-end with different templates
- ✅ Commit (CLI working)

### Day 3: Configuration + Integration (Polish)

**Morning** (4 hours):
- 🔴 Write test: Config file loading
- 🔴 Write test: Per-file settings
- 🟢 Implement: Config loader
- 🟢 Enhance: Context gatherer to use config
- 🔵 Refactor: Config validation
- ✅ Commit

**Afternoon** (4 hours):
- Create example `.doc-evergreen.yaml`
- Integrate into amplifier CLI
- End-to-end testing with all features
- Polish error messages
- Update documentation
- ✅ Final commit

**End of day**: Demo complete CLI tool with multiple templates

---

## Testing Requirements

### TDD Workflow Per Feature

**Example: Template Detection**

1. **🔴 RED - Write Test First**:
```python
def test_detect_template_from_readme():
    assert detect_template("README.md") == "readme"

def test_detect_template_from_contributing():
    assert detect_template("CONTRIBUTING.md") == "contributing"

def test_detect_template_default():
    assert detect_template("RANDOM.md") == "readme"  # Default
```

2. **🟢 GREEN - Minimal Implementation**:
```python
def detect_template(filename: str) -> str:
    name = Path(filename).name.lower()
    if "readme" in name:
        return "readme"
    if "contributing" in name:
        return "contributing"
    return "readme"
```

3. **🔵 REFACTOR - Improve Quality**:
```python
FILENAME_TO_TEMPLATE = {
    "readme.md": "readme",
    "contributing.md": "contributing",
    "api.md": "api-reference",
}

def detect_template(filename: str) -> str:
    """Detect appropriate template from target filename"""
    name = Path(filename).name.lower()
    return FILENAME_TO_TEMPLATE.get(name, "readme")
```

### Unit Tests (Write First)
- `test_list_templates()` - Template discovery
- `test_load_template_by_name()` - Loading by name
- `test_load_template_by_path()` - Loading by path
- `test_detect_template()` - Auto-detection
- `test_load_config()` - Config file parsing
- `test_cli_arguments()` - Click CLI parsing

### Integration Tests (Write First When Possible)
- `test_cli_with_template()` - Full CLI flow
- `test_config_overrides_defaults()` - Config priority
- `test_multiple_templates_work()` - Template switching

### Manual Testing Checklist (After Automated Tests)
- [ ] Install as amplifier subcommand
- [ ] Run `amplifier doc-update --help`
- [ ] Generate README with auto-detected template
- [ ] Generate API docs with explicit template
- [ ] Create `.doc-evergreen.yaml` and verify it's used
- [ ] List templates works
- [ ] Error messages are helpful

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What You Learn

After this sprint ships, you discover:

1. **Template Effectiveness**
   - Which templates work well?
   - What structure guides LLM best?
   - What sections are always good vs need editing?

2. **CLI UX**
   - Are defaults sensible?
   - Is template selection intuitive?
   - What options do users actually use?

3. **Configuration Needs**
   - Is config file necessary or just nice-to-have?
   - What settings do users want to configure?
   - How much flexibility is needed?

4. **Multi-Doc Workflow**
   - Do users regenerate multiple docs in sequence?
   - Are templates reused or customized per project?
   - What friction points exist?

**These learnings directly inform**:
- Sprint 4: Context selection (based on per-template needs)
- v2: Template improvements (based on usage patterns)
- v2: Batch operations (if multi-doc workflow is common)

---

## Known Limitations (By Design)

1. **Manual template creation** - No template builder
   - **Why acceptable**: Templates are simple markdown files
   - **Future**: v2 could add interactive template wizard

2. **Local templates only** - No sharing/marketplace
   - **Why acceptable**: MVP focuses on personal use
   - **Future**: v2 could add template repository

3. **Simple config format** - No advanced features
   - **Why acceptable**: Covers common cases
   - **Future**: v2 could add conditional logic, variables

4. **No template validation** - Relies on reasonable templates
   - **Why acceptable**: Simple format is hard to break
   - **Future**: v2 could add linting

---

## Success Criteria

### Code Quality
- ✅ All tests pass (>80% coverage)
- ✅ TDD cycle followed for all features
- ✅ Clean CLI interface
- ✅ Proper error handling

### User Experience
- ✅ CLI feels professional
- ✅ Template selection is intuitive
- ✅ Help text is clear
- ✅ Defaults are sensible
- ✅ Integrates naturally with amplifier

### Functionality
- ✅ Works for multiple doc types
- ✅ Template auto-detection works
- ✅ Config file reduces repetition
- ✅ Can regenerate any doc in project

### Validation
- ✅ Successfully regenerate 3+ different doc types
- ✅ User prefers this to running script manually
- ✅ Configuration reduces CLI verbosity

---

## Next Sprint Preview

After this sprint makes the tool reusable, Sprint 4 adds **context control**:

**The Need**: "I want to control which source files are included for context"

**The Solution**:
- CLI option: `--sources "src/main.py,docs/arch.md"`
- Smart context selection (relevant files only)
- Per-template source recommendations
- Context size optimization

**Why Next**: Now that CLI exists (Sprint 3) and templates vary (Sprint 3), users need control over what context goes into generation for different doc types.

---

## Quick Reference

**Key Files**:
- `cli.py` - CLI interface
- `template_manager.py` - Template handling
- `templates/*.md` - Template files
- `.doc-evergreen.yaml` - Configuration

**Key Commands**:
```bash
# Basic usage
amplifier doc-update README.md

# Explicit template
amplifier doc-update docs/API.md --template api-reference

# List templates
amplifier doc-update --list-templates

# Skip review (for automation)
amplifier doc-update README.md --no-review

# Help
amplifier doc-update --help
```

**Template Files**:
- `templates/readme.md` - README structure
- `templates/api-reference.md` - API docs
- `templates/contributing.md` - Contributing guide

---

**Remember**: This sprint is about **reusability across doc types**, not perfecting individual templates. Goal is to make it work for any documentation file, not just README.
