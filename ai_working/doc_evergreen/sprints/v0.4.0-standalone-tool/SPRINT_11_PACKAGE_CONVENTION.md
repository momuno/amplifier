# Sprint 11: Package & Convention-Based Usage

**Duration:** 1 day
**Goal:** Create installable package with convention-based project discovery
**Value Delivered:** Users can install tool once and use it on any project

---

## Why This Sprint?

This is the foundation of standalone tool usage. Without proper packaging and convention-based discovery, doc_evergreen remains trapped in its own repository. This sprint transforms it into a true CLI tool that works anywhere.

---

## Deliverables

### 1. Python Package Configuration (~50 lines)

**What it does:**
- Creates pyproject.toml with package metadata
- Defines CLI entry point: `doc-evergreen`
- Specifies dependencies
- Enables pip/pipx installation

**Why this sprint:**
- Prerequisite for all standalone usage
- Standard Python packaging approach
- Well-understood by users

**Implementation notes:**
- Use modern pyproject.toml (PEP 621)
- Entry point: `doc-evergreen = doc_evergreen.cli:cli`
- Include all runtime dependencies
- Set minimum Python version (3.11+)

**Files created:**
- `pyproject.toml` (at doc_evergreen root)

**Example structure:**
```toml
[project]
name = "doc-evergreen"
version = "0.4.0"
description = "AI-powered documentation generation from templates"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "pydantic-ai>=0.0.14",
    # ... other deps
]

[project.scripts]
doc-evergreen = "doc_evergreen.cli:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 2. Convention-Based Path Resolution (~100 lines modifications)

**What it does:**
- Changes source path resolution from template-relative to cwd-relative
- Updates ChunkedGenerator to use cwd as base_dir
- Modifies CLI to pass cwd instead of template parent
- Ensures output paths relative to cwd

**Why this sprint:**
- Core of "run from project root" behavior
- Removes PYTHONPATH requirements
- Natural mental model

**Implementation notes:**
- Update `cli.py`: `base_dir = Path.cwd()` instead of `Path(template_path).parent`
- Update `ChunkedGenerator.__init__`: Accept base_dir parameter
- Update source file resolution in template parsing
- Keep template discovery separate (Sprint 12)

**Files modified:**
- `cli.py` - base_dir calculation
- `chunked_generator.py` - base_dir usage
- `core/template_schema.py` - if needed for validation

**Key change in cli.py:**
```python
# OLD (v0.3.0)
base_dir = Path(template_path).parent

# NEW (v0.4.0)
base_dir = Path.cwd()  # Current working directory IS the project
```

### 3. CLI Entry Point Updates (~30 lines)

**What it does:**
- Updates help text to reflect standalone usage
- Clarifies that tool works from any directory
- Updates examples to show convention

**Why this sprint:**
- Users need to understand new usage model
- Help text is primary documentation
- Sets expectations correctly

**Files modified:**
- `cli.py` - docstrings and help text

**Example help text:**
```python
@click.group()
def cli():
    """doc-evergreen - AI-powered documentation generation.

    Works with ANY project. Run from your project root directory.
    Templates reference sources relative to project root.

    Quick Start:
      cd /path/to/your-project
      doc-evergreen init
      doc-evergreen regen readme

    Installation:
      pipx install /path/to/doc-evergreen
    """
```

### 4. Installation Testing (~automated + manual)

**What it does:**
- Verifies pip install works
- Verifies pipx install works
- Tests global command availability
- Validates dependencies installed

**Why this sprint:**
- Packaging errors are common
- Must work before proceeding to Sprint 12
- Different environments need testing

**Testing checklist:**
- [ ] `pip install -e .` from doc_evergreen directory works
- [ ] `doc-evergreen --help` shows help
- [ ] `doc-evergreen regen-doc` command exists
- [ ] Can run from different directories
- [ ] `pipx install .` works (isolated environment)
- [ ] Uninstall and reinstall works

---

## What Gets Punted

- **PyPI publishing** - Git install sufficient for now
- **Advanced path handling** - Basic cwd-relative sufficient
- **Config file support** - Convention removes need
- **Backward compatibility** - v0.4.0 is breaking change

**Why**: These don't block standalone usage. Can add later based on user needs.

---

## Dependencies

**Requires from v0.3.0:**
- Working `regen-doc` command
- ChunkedGenerator implementation
- Template parsing and validation
- Change detection system

**Provides for Sprint 12:**
- Installable package
- Global CLI command
- Convention-based path resolution
- Foundation for template discovery

---

## Acceptance Criteria

### Must Have
- ✅ `pip install -e .` works from doc_evergreen directory
- ✅ `doc-evergreen --help` available globally after install
- ✅ `doc-evergreen regen-doc` works with absolute template paths
- ✅ Sources in templates resolved relative to cwd
- ✅ Output paths work relative to cwd
- ✅ All existing tests still pass
- ✅ Help text reflects new usage model

### Nice to Have (Defer if time constrained)
- ❌ Fancy progress during install
- ❌ Version check command
- ❌ Shell completion

---

## Technical Approach

### Build System Choice
**Decision**: Use hatchling (modern, simple)
**Alternatives considered**:
- setuptools - older, more complex
- poetry - additional tool required
- flit - similar to hatchling

**Rationale**: hatchling is modern, PEP 517 compliant, minimal configuration

### Path Resolution Strategy
**Decision**: All paths relative to `Path.cwd()`
**Alternatives considered**:
- Explicit --project flag
- Config file with project root
- Template-relative (v0.3.0 approach)

**Rationale**: cwd is natural, zero config, obvious behavior

### Breaking Change Communication
**Decision**: Clear in release notes, migration guide
**Approach**:
- Version bump to 0.4.0 (minor version indicates breaking change)
- Migration section in docs
- Error messages guide users

---

## Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all changes:

**For each feature:**
1. 🔴 Write test (it fails)
2. 🟢 Write code (test passes)
3. 🔵 Refactor (tests still pass)
4. ✅ Commit (green tests)

### Unit Tests (Write First)

**Test pyproject.toml validity:**
```python
def test_pyproject_valid():
    """pyproject.toml is valid and has required fields"""
    import tomllib
    config = tomllib.load(open("pyproject.toml", "rb"))
    assert config["project"]["name"] == "doc-evergreen"
    assert "doc-evergreen" in config["project"]["scripts"]
```

**Test cwd-based path resolution:**
```python
def test_source_paths_relative_to_cwd(tmp_path):
    """Sources resolved relative to cwd, not template"""
    # Arrange: Create project structure
    project = tmp_path / "my-project"
    project.mkdir()
    (project / "src").mkdir()
    (project / "src" / "code.py").write_text("# code")

    template = tmp_path / "templates" / "doc.json"
    template.parent.mkdir()
    template.write_text(json.dumps({
        "document": {
            "output": "README.md",
            "sections": [{
                "heading": "Test",
                "prompt": "Document this",
                "sources": ["src/code.py"]  # Relative to project, not template
            }]
        }
    }))

    # Act: Generate from project directory
    os.chdir(project)
    result = cli_runner.invoke(cli, ["regen-doc", str(template)])

    # Assert: Source file found relative to cwd
    assert result.exit_code == 0
```

**Test CLI entry point:**
```python
def test_cli_command_available():
    """doc-evergreen command available after install"""
    result = subprocess.run(
        ["doc-evergreen", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "doc-evergreen" in result.stdout
```

### Integration Tests (Write First)

**Test full installation workflow:**
```python
def test_pip_install_editable(tmp_venv):
    """pip install -e . creates working command"""
    # Install in clean venv
    subprocess.run(["pip", "install", "-e", "."], check=True)

    # Verify command available
    result = subprocess.run(
        ["doc-evergreen", "--version"],
        capture_output=True
    )
    assert result.returncode == 0
```

**Test cross-directory usage:**
```python
def test_works_from_any_directory(tmp_path):
    """Can run doc-evergreen from any directory"""
    project1 = tmp_path / "project1"
    project2 = tmp_path / "project2"

    # Both projects can use tool independently
    for project in [project1, project2]:
        setup_test_project(project)
        os.chdir(project)
        result = cli_runner.invoke(cli, ["regen-doc", "template.json"])
        assert result.exit_code == 0
```

### Manual Testing (After Automated Tests Pass)

- [ ] Install in clean Python environment
- [ ] Run from 3 different project directories
- [ ] Verify help text is clear
- [ ] Test uninstall and reinstall
- [ ] Check Windows compatibility (if applicable)

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## What You Learn

After this sprint:
1. **Is installation smooth?** → Informs documentation needs
2. **Does convention feel natural?** → Validates design decision
3. **What path edge cases exist?** → Guides error handling
4. **Any platform-specific issues?** → Identifies testing needs

These learnings directly inform Sprint 12's init command and Sprint 13's documentation.

---

## Success Metrics

**Quantitative:**
- Installation time <2 minutes
- Zero PYTHONPATH configuration
- Works in 100% of tested project structures
- All tests green

**Qualitative:**
- "It just works" - no surprising behavior
- Installation matches Python community standards
- Convention feels obvious, not clever
- Users don't ask "where do I run this?"

---

## Implementation Order (TDD Daily Workflow)

### Morning (4 hours): Package Setup

**Hour 1-2: pyproject.toml**
- 🔴 Write test: `test_pyproject_valid`
- 🟢 Create pyproject.toml with minimal config
- 🔵 Refactor: Add all dependencies, clean up
- ✅ Commit: "feat: add pyproject.toml with CLI entry point"

**Hour 3-4: Installation Testing**
- 🔴 Write test: `test_cli_command_available`
- 🟢 Verify `pip install -e .` creates command
- 🔵 Refactor: Fix any packaging issues
- ✅ Manual test: Install in fresh venv
- ✅ Commit: "test: verify CLI entry point works"

### Afternoon (4 hours): Convention-Based Paths

**Hour 5-6: Path Resolution**
- 🔴 Write test: `test_source_paths_relative_to_cwd`
- 🟢 Update cli.py: `base_dir = Path.cwd()`
- 🟢 Update ChunkedGenerator to use base_dir
- 🔵 Refactor: Clean up path handling
- ✅ Commit: "feat: resolve sources relative to cwd"

**Hour 7: Integration Testing**
- 🔴 Write test: `test_works_from_any_directory`
- 🟢 Fix any issues discovered
- 🔵 Refactor: Improve error messages
- ✅ Commit: "test: verify cross-directory usage"

**Hour 8: Documentation & Polish**
- Update CLI help text
- Update command docstrings
- Run full test suite
- Manual testing in different environments
- ✅ Commit: "docs: update CLI help for standalone usage"

---

## Known Limitations (By Design)

1. **Git install only** - No PyPI yet (acceptable for v0.4.0)
2. **Breaking change** - Source paths change (worth it for better design)
3. **No config file** - Convention only (simplicity over flexibility)
4. **Requires cwd = project** - Can't document remote projects (rare need)

---

## Next Sprint Preview

After Sprint 11 ships, Sprint 12 will add:
- `.doc-evergreen/` directory convention
- Template discovery by short name
- `init` command to bootstrap projects
- Clear workflow for new users

Sprint 11 creates the foundation; Sprint 12 makes it delightful to use.
