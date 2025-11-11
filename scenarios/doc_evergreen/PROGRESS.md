# doc-evergreen Implementation Progress

**Last Updated**: 2025-01-08
**Status**: ✅ ALL CHUNKS COMPLETE
**Total Tests Passing**: 108/108

---

## Overview

Building the doc-evergreen tool for automatic documentation generation and maintenance. The tool uses LLM intelligence for discovery combined with deterministic execution for automation.

**Key Design Decision**: Uses direct Anthropic API calls (not Claude Code SDK) to avoid interference when run from git hooks.

---

## Completed Chunks

### ✅ Chunk 1: CLI Skeleton and Parameter Validation

**Files Created:**
- `doc_evergreen/cli.py` - Main CLI with Click framework
- `doc_evergreen/commands/create.py` - Create command implementation
- `doc_evergreen/commands/regenerate.py` - Regenerate command implementation

**Status**: Complete and tested
**Tests**: Manual CLI testing (all passing)

**Features:**
- Click-based CLI with proper help text
- `create` command with `--about`, `--output`, `--sources`, `--template`, `--dry-run`
- `regenerate` command with `<doc-path>` or `--all` flag
- Comprehensive parameter validation
- Clear error messages

**How to Test:**
```bash
uv run python -m doc_evergreen.cli --help
uv run python -m doc_evergreen.cli create --help
uv run python -m doc_evergreen.cli create --about "test" --output "test.md" --dry-run
```

---

### ✅ Chunk 2: History.yaml Management

**Files Created:**
- `doc_evergreen/core/history.py` - History management functions
- `tests/test_history.py` - 17 tests

**Status**: Complete with 17/17 tests passing

**Features:**
- Load/save history.yaml with validation
- Query document configuration
- Add/update document entries
- Track version history
- List all configured documents
- Remove document entries

**Key Functions:**
- `load_history()` - Load or create history.yaml
- `save_history()` - Save with structure validation
- `get_doc_config()` - Get config for specific doc
- `add_doc_entry()` - Add/update doc configuration
- `add_version_entry()` - Add version to history
- `list_all_docs()` - List all configured docs
- `remove_doc_entry()` - Remove from history

**History File Structure:**
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
    sources:
      - "src/**/*.py"
      - "pyproject.toml"
    about: "Main project README"
```

---

### ✅ Chunk 3: File Discovery and Gathering

**Files Created:**
- `doc_evergreen/core/discovery.py` - File discovery functions
- `tests/test_discovery.py` - 27 tests

**Status**: Complete with 27/27 tests passing

**Features:**
- Glob pattern expansion (recursive patterns supported)
- .gitignore integration via pathspec
- UTF-8 validation
- File content reading
- Auto-discovery based on topic keywords
- File size estimation
- Respects .gitignore patterns

**Key Functions:**
- `find_files()` - Expand glob patterns
- `load_gitignore()` - Parse .gitignore into PathSpec
- `should_ignore()` - Check if file matches gitignore
- `validate_utf8()` - Validate file encoding
- `read_file()` - Read UTF-8 file contents
- `gather_files()` - Find, filter, and read files
- `auto_discover_files()` - Smart pattern generation
- `estimate_file_size()` - Calculate total size
- `format_file_size()` - Human-readable formatting

**Auto-Discovery Keywords:**
- "api" → `src/**/*.py`, `api/**/*.py`
- "cli" → `src/cli/**/*.py`, `src/commands/**/*.py`
- "readme" → `README.md`, `src/**/*.py`, `pyproject.toml`
- "contributing" → `CONTRIBUTING.md`, `.github/**/*.md`
- "user guide" → `README.md`, `docs/**/*.md`, `examples/**/*`

---

### ✅ Chunk 4: Template Management and Versioning

**Files Created:**
- `doc_evergreen/core/template.py` - Template management functions
- `doc_evergreen/templates/readme.md` - Built-in README template
- `doc_evergreen/templates/api-reference.md` - Built-in API reference template
- `doc_evergreen/templates/user-guide.md` - Built-in user guide template
- `doc_evergreen/templates/developer-guide.md` - Built-in developer guide template
- `tests/test_template.py` - 27 tests

**Status**: Complete with 27/27 tests passing

**Features:**
- Load built-in templates from package
- Automatic versioning (v1, v2, v3...)
- YAML frontmatter for metadata
- Template inheritance tracking
- Smart template selection based on keywords
- Template saving to `.doc-evergreen/templates/`

**Key Functions:**
- `list_builtin_templates()` - List available templates
- `load_builtin_template()` - Load by name
- `parse_template_metadata()` - Extract YAML frontmatter
- `create_template_metadata()` - Generate metadata
- `format_template_with_metadata()` - Add frontmatter
- `find_latest_version()` - Find highest version
- `save_template()` - Save with auto-versioning
- `get_template_path()` - Get path to version
- `select_builtin_template()` - Smart selection

**Template Versioning:**
- First save: `template-name.v1.md`
- Second save: `template-name.v2.md`
- Automatic version increment
- Metadata tracks version and derivation

**Template Selection:**
- "readme" → `readme.md`
- "api", "reference" → `api-reference.md`
- "contributing", "developer" → `developer-guide.md`
- "user guide", "tutorial" → `user-guide.md`

---

### ✅ Chunk 5: LLM Integration with Direct API Calls

**Files Created:**
- `doc_evergreen/core/generator.py` - LLM integration with direct Anthropic API
- `tests/test_generator.py` - 16 tests

**Status**: Complete with 16/16 tests passing

**Features:**
- Direct Anthropic API integration (not Claude Code SDK)
- API key loading from `.claude/api_key.txt` (searches parent directories)
- Retry logic with exponential backoff for rate limits and API errors
- Template customization via LLM
- Document generation from templates and source files
- Source file formatting with truncation for large projects

**Key Functions:**
- `load_api_key()` - Searches up directory tree for API key file
- `call_llm()` - Direct API calls with retry logic (max 3 retries, exponential backoff)
- `customize_template()` - Customizes built-in templates for specific projects
- `format_sources()` - Formats source files for prompt inclusion (50KB limit)
- `generate_document()` - Main generation function combining template + sources

**LLM Configuration:**
- Model: `claude-sonnet-4-20250514`
- Max tokens: 4000
- Temperature: 0.3 (deterministic)
- Retry strategy: Exponential backoff starting at 1s

**Error Handling:**
- `RateLimitError` - Retries with exponential backoff
- `APIError` - Retries with exponential backoff
- File not found - Clear error messages
- Empty API key - Validation with helpful message
- Empty responses - Wrapped in RuntimeError

---

### ✅ Chunk 6: Document Generation and Versioning

**Files Created:**
- `doc_evergreen/core/versioning.py` - Document backup and versioning
- `doc_evergreen/commands/create.py` - Complete implementation (updated from stub)
- `tests/test_versioning.py` - 11 tests

**Status**: Complete with 11/11 tests passing

**Features:**
- Complete end-to-end document generation flow
- Document backup before regeneration
- Template selection and customization
- File discovery (auto or manual)
- LLM generation with progress feedback
- History tracking with version entries
- Dry-run mode support

**Key Functions (versioning.py):**
- `get_versions_dir()` - Get path to .doc-evergreen/versions/
- `ensure_versions_dir()` - Create versions directory if needed
- `create_backup_path()` - Generate timestamped backup filename
- `backup_document()` - Copy document to versions directory

**Create Command Flow:**
1. **File Discovery** - Auto-discover or use provided patterns, validate UTF-8
2. **Template Selection** - Auto-select or use specified, customize via LLM
3. **Document Generation** - Generate docs from template + sources via LLM
4. **Backup** - Save existing document to .doc-evergreen/versions/ (if exists)
5. **Save** - Write generated document to output path
6. **History** - Update history.yaml with entry or version info

**User Feedback:**
- Progress messages for each step
- File count and size estimates
- Template selection info
- Generation time notice (30-60s)
- Success summary with paths

---

### ✅ Chunk 7: Regenerate Command

**Files Created/Updated:**
- `doc_evergreen/commands/regenerate.py` - Complete implementation (updated from stub)
- `tests/test_regenerate.py` - 10 tests

**Status**: Complete with 10/10 tests passing

**Features:**
- Load configuration from history.yaml
- Regenerate single document by path
- Regenerate all documents with --all flag
- Template loading (customized or built-in fallback)
- Re-customization of templates using existing doc
- Document backup before regeneration
- History updates with version tracking
- Dry-run mode support
- Comprehensive error handling

**Key Functions:**
- `regenerate_single_document()` - 6-step regeneration process
- `execute_regenerate()` - Command handler for single or all docs

**Regenerate Command Flow:**
1. **Load History** - Read history.yaml and validate
2. **Gather Source Files** - Find files matching patterns
3. **Load Template** - Customized or built-in, with fallback
4. **Generate Document** - LLM generation from template + sources
5. **Backup** - Save existing document to .doc-evergreen/versions/
6. **Save & Update** - Write new document and update history

**Usage:**
```bash
# Regenerate single document
uv run python -m doc_evergreen.cli regenerate README.md

# Regenerate all documents
uv run python -m doc_evergreen.cli regenerate --all

# Dry run to preview
uv run python -m doc_evergreen.cli regenerate --all --dry-run
```

---

## Implementation Complete

All 7 chunks have been implemented and tested. The doc-evergreen tool is fully functional with 108 passing tests.

---

## Next: Documentation and Polish (Optional)

**Priority**: MEDIUM - Tool is functional

**Requirements:**

1. **Load API Key**
   - Read from `.claude/api_key.txt`
   - Handle missing key gracefully
   - Clear error message if key invalid

2. **Direct Anthropic API Calls**
   - Use `anthropic` Python library directly
   - Model: `claude-sonnet-4-20250514`
   - Max tokens: 4000
   - Temperature: 0.3 (deterministic)
   - **DO NOT** use Claude Code SDK (conflicts with git hooks)

3. **Template Customization Prompt**
   ```python
   def customize_template(
       builtin_template: str,
       about: str,
       existing_doc: str | None = None
   ) -> str:
       """
       Use LLM to customize built-in template for project.

       Args:
           builtin_template: Built-in template content
           about: Description of documentation purpose
           existing_doc: Optional existing doc to analyze for style

       Returns:
           Customized template content
       """
   ```

4. **Document Generation Prompt**
   ```python
   def generate_document(
       template: str,
       sources: dict[str, str],  # path -> content
       about: str
   ) -> str:
       """
       Generate documentation from template and sources.

       Args:
           template: Template content (with instructions)
           sources: Dictionary of source file paths to contents
           about: Description of documentation purpose

       Returns:
           Generated documentation content
       """
   ```

5. **Error Handling**
   - Retry with exponential backoff on rate limits
   - Timeout handling (configurable)
   - Invalid response validation
   - API key errors with helpful messages

6. **Testing Strategy**
   - Mock API calls for unit tests
   - Test prompt generation
   - Test error handling
   - Manual integration test with real API (document in test file)

**Prompt Templates Needed:**

**Template Customization:**
```
You are customizing a documentation template for a software project.

Built-in Template:
{builtin_template}

Project Context:
- Topic: {about}
{existing_doc_context}

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
```

**Document Generation:**
```
You are generating documentation for a software project.

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
```

---

## Remaining Chunks After Chunk 5

### Chunk 6: Document Generation and Versioning

**Files to Update:**
- `doc_evergreen/commands/create.py` - Complete implementation
- `doc_evergreen/core/versioning.py` - New file for backup logic
- `tests/test_integration.py` - End-to-end tests

**Requirements:**
- Backup existing documents before regeneration
- Generate new documents using LLM
- Write to output path
- Update history.yaml
- Full dry-run mode implementation

### Chunk 7: Regenerate Command

**Files to Update:**
- `doc_evergreen/commands/regenerate.py` - Complete implementation

**Requirements:**
- Load configuration from history
- Regenerate single document
- Regenerate all documents
- Update version history

---

## Testing Status

### Test Summary
- **Chunk 1**: Manual CLI testing ✓
- **Chunk 2**: 17/17 automated tests passing ✓
- **Chunk 3**: 27/27 automated tests passing ✓
- **Chunk 4**: 27/27 automated tests passing ✓
- **Chunk 5**: 16/16 automated tests passing ✓
- **Chunk 6**: 11/11 automated tests passing ✓
- **Chunk 7**: 10/10 automated tests passing ✓
- **Total**: 108 automated tests passing ✅

### Run All Tests
```bash
cd scenarios/doc_evergreen
uv run pytest tests/ -v
```

### Run Specific Test Files
```bash
uv run pytest tests/test_history.py -v
uv run pytest tests/test_discovery.py -v
uv run pytest tests/test_template.py -v
```

---

## Directory Structure

```
scenarios/doc_evergreen/
├── IMPLEMENTATION_PLAN.md        # Detailed implementation plan
├── PROGRESS.md                   # This file - current progress
├── README.md                     # (To be created) User documentation
├── pyproject.toml                # Package configuration
│
├── doc_evergreen/
│   ├── __init__.py
│   ├── cli.py                    # ✅ Main CLI entry point
│   │
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── create.py             # ✅ Create command (partial)
│   │   └── regenerate.py         # ✅ Regenerate command (stub)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── history.py            # ✅ History management
│   │   ├── discovery.py          # ✅ File discovery
│   │   ├── template.py           # ✅ Template management
│   │   ├── generator.py          # ⏳ Next: LLM integration
│   │   └── versioning.py         # ⏳ Later: Document versioning
│   │
│   └── templates/                # ✅ Built-in templates
│       ├── readme.md
│       ├── api-reference.md
│       ├── user-guide.md
│       └── developer-guide.md
│
└── tests/
    ├── __init__.py
    ├── test_history.py           # ✅ 17 tests
    ├── test_discovery.py         # ✅ 27 tests
    ├── test_template.py          # ✅ 27 tests
    ├── test_generator.py         # ⏳ Next: LLM tests
    └── test_integration.py       # ⏳ Later: E2E tests
```

---

## Key Design Decisions

### 1. Direct API Calls (Not Claude Code SDK)
**Rationale**: Tool must work from git hooks without interfering with Claude Code instance
**Implementation**: Use `anthropic` library directly

### 2. Deterministic Tool + Intelligent Assistant
**Rationale**: Separation of concerns - tool is dumb, assistant is smart
**Implementation**: Tool reports missing parameters, assistant gathers them

### 3. Always Overwrite with Versioning
**Rationale**: User wants regeneration, old version is backed up
**Implementation**: Save to `.doc-evergreen/versions/` before overwriting

### 4. Template Versioning
**Rationale**: Track template evolution, allow reversion
**Implementation**: Automatic increment (v1, v2, v3...)

### 5. History File Committed to Git
**Rationale**: Team shares configuration, reproducible builds
**Implementation**: `.doc-evergreen/` is committed, not gitignored

---

## Next Steps (Immediate)

### Step 1: Implement generator.py
1. Create `doc_evergreen/core/generator.py`
2. Implement `load_api_key()`
3. Implement `customize_template()`
4. Implement `generate_document()`
5. Add error handling and retries

### Step 2: Create Tests
1. Create `tests/test_generator.py`
2. Mock API calls for unit tests
3. Test prompt generation
4. Test error handling
5. Document manual integration test

### Step 3: Wire into create.py
1. Update `commands/create.py` to use generator
2. Integrate all core modules
3. Test end-to-end with dry-run

### Step 4: Manual Testing
1. Create API key in `.claude/api_key.txt`
2. Test create command with real API
3. Verify generated documentation quality
4. Test with various file sizes

---

## API Key Setup (For Testing)

Create `.claude/api_key.txt` in repo root:
```bash
echo "your-api-key-here" > .claude/api_key.txt
```

Or set environment variable:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

---

## Common Commands

### Development
```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_history.py -v

# Run CLI
uv run python -m doc_evergreen.cli --help

# Test create command (dry-run)
uv run python -m doc_evergreen.cli create \
    --about "Test API documentation" \
    --output "docs/TEST.md" \
    --sources "src/**/*.py" \
    --dry-run
```

### Checking
```bash
# Run linter
uv run ruff check .

# Run type checker
uv run pyright .
```

---

## Known Issues / TODOs

1. **Generator not implemented** - Chunk 5 next
2. **create.py is stub** - Needs full implementation in Chunk 6
3. **regenerate.py is stub** - Needs implementation in Chunk 7
4. **No E2E tests yet** - Will add in Chunk 6
5. **No README.md** - Will write after tool is working

---

## References

- **IMPLEMENTATION_PLAN.md** - Full detailed plan with all 7 chunks
- **CLAUDE.md** - Project guidelines and philosophy
- **AGENTS.md** - General project standards
- **Anthropic API Docs** - https://docs.anthropic.com/

---

## For Post-Compaction Resume

**Start Here:**
1. Read this PROGRESS.md file completely
2. Review `IMPLEMENTATION_PLAN.md` Chunk 5 section
3. Check `doc_evergreen/core/` to see what exists
4. Run `uv run pytest tests/ -v` to verify tests still pass
5. Begin implementing `generator.py` per Chunk 5 spec

**Current State**: 4/7 chunks complete, 71 tests passing, ready for LLM integration

**Next Task**: Implement Chunk 5 - LLM integration with direct Anthropic API calls
