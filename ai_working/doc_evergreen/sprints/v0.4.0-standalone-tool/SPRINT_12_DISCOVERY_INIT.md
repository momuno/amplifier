# Sprint 12: Template Discovery & Init Command

**Duration:** 1 day
**Goal:** Enable short-form template names and bootstrap projects with `init`
**Value Delivered:** Users can start new projects in <5 minutes with zero friction

---

## Why This Sprint?

Sprint 11 made the tool installable. Sprint 12 makes it delightful to use. The `.doc-evergreen/` convention provides a clear home for templates, and the `init` command removes the "blank page" problem for new users.

---

## Deliverables

### 1. Template Discovery in .doc-evergreen/ (~150 lines)

**What it does:**
- Looks for templates in `.doc-evergreen/` directory
- Enables short names: `doc-evergreen regen readme` → `.doc-evergreen/readme.json`
- Falls back to absolute paths if needed
- Clear error if template not found

**Why this sprint:**
- Convention makes common case simple
- Familiar pattern (like .github/, .vscode/)
- Clean project organization
- Natural place for documentation config

**Implementation notes:**
- Add template resolution logic to CLI
- Check `.doc-evergreen/{name}.json` first
- If not found, try as absolute/relative path
- Error message suggests creating with `init` if not found

**Files modified:**
- `cli.py` - Add `resolve_template_path()` function

**Resolution logic:**
```python
def resolve_template_path(name: str) -> Path:
    """Resolve template name to path.

    Tries:
    1. .doc-evergreen/{name}.json (if name doesn't end with .json)
    2. {name} as-is (absolute or relative path)
    3. Error with helpful message
    """
    if not name.endswith('.json'):
        # Try convention first
        convention_path = Path.cwd() / '.doc-evergreen' / f'{name}.json'
        if convention_path.exists():
            return convention_path

    # Try as path
    path = Path(name)
    if path.exists():
        return path

    # Not found - helpful error
    raise FileNotFoundError(
        f"Template not found: {name}\n"
        f"Tried:\n"
        f"  - .doc-evergreen/{name}.json\n"
        f"  - {name}\n"
        f"Run 'doc-evergreen init' to create starter template."
    )
```

### 2. Init Command (~200 lines)

**What it does:**
- `doc-evergreen init` creates `.doc-evergreen/` directory
- Generates starter template (readme.json)
- Interactive prompts for project name, description (optional)
- Provides ready-to-use template

**Why this sprint:**
- Removes "blank page" problem
- Instant onboarding
- Shows users what good templates look like
- Zero friction to get started

**Implementation notes:**
- New CLI command: `init`
- Create `.doc-evergreen/` if not exists
- Don't overwrite existing templates
- Optional interactive mode (default to sensible values)
- Generate working template with common sections

**Files modified:**
- `cli.py` - Add `init` command

**Init command structure:**
```python
@cli.command("init")
@click.option("--name", help="Project name (default: directory name)")
@click.option("--description", help="Project description")
@click.option("--force", is_flag=True, help="Overwrite existing template")
def init(name: str | None, description: str | None, force: bool):
    """Initialize doc-evergreen in current project.

    Creates .doc-evergreen/ directory with starter template.

    Examples:
      doc-evergreen init
      doc-evergreen init --name "My Project"
    """
    # Implementation
```

**Starter template structure:**
```json
{
  "document": {
    "output": "README.md",
    "sections": [
      {
        "heading": "# {Project Name}",
        "prompt": "Brief overview...",
        "sources": ["**/*.py", "**/*.md"]
      },
      {
        "heading": "## Installation",
        "prompt": "How to install...",
        "sources": ["pyproject.toml", "setup.py", "requirements.txt"]
      },
      {
        "heading": "## Usage",
        "prompt": "Basic usage examples...",
        "sources": ["examples/**", "**/*.py"]
      },
      {
        "heading": "## Development",
        "prompt": "Development setup...",
        "sources": ["Makefile", "*.md"]
      }
    ]
  }
}
```

### 3. Updated regen-doc Command (~50 lines modifications)

**What it does:**
- Accepts short names: `regen readme`
- Uses `resolve_template_path()` for discovery
- Maintains backward compatibility with absolute paths

**Why this sprint:**
- Completes the convention-based workflow
- Makes regeneration simple
- Consistent with init command

**Files modified:**
- `cli.py` - Update `regen-doc` to use template resolution

**Command enhancement:**
```python
@cli.command("regen-doc")
@click.argument("template_name")  # Was template_path
def regen_doc(template_name: str):
    """Regenerate documentation from template.

    Examples:
      doc-evergreen regen readme              # Uses .doc-evergreen/readme.json
      doc-evergreen regen api                 # Uses .doc-evergreen/api.json
      doc-evergreen regen /abs/path/doc.json  # Absolute path still works
    """
    template_path = resolve_template_path(template_name)
    # ... rest of existing logic
```

### 4. Convention Documentation (~100 lines)

**What it does:**
- Documents `.doc-evergreen/` convention
- Explains template naming
- Shows init workflow
- Provides examples

**Why this sprint:**
- Users need to understand the convention
- Help text can't explain everything
- Examples show the way

**Files created/modified:**
- Add section to USER_GUIDE.md
- Update CLI help text
- Add .gitignore recommendations

**Documentation content:**
```markdown
## The .doc-evergreen/ Convention

doc-evergreen follows a convention-based approach similar to .github/ or .vscode/:

### Structure
```
your-project/
├── .doc-evergreen/          # Template storage
│   ├── readme.json          # Main README template
│   ├── api.json             # API docs template
│   └── contributing.json    # Contributor guide template
├── README.md                # Generated documentation
└── src/                     # Your code
```

### Short Names
```bash
doc-evergreen regen readme  # Finds .doc-evergreen/readme.json
doc-evergreen regen api     # Finds .doc-evergreen/api.json
```

### Why This Convention?
- Templates travel with project
- Clear ownership (part of project, not tool)
- Version controlled with code
- Zero configuration needed
```

---

## What Gets Punted

- **Template wizard** - Simple init sufficient
- **Template library/marketplace** - Single starter template enough
- **Multiple init templates** - One good default sufficient
- **Template validation during init** - Basic validation sufficient
- **Interactive template editor** - JSON files work fine

**Why**: These are enhancements. Core init command provides enough value.

---

## Dependencies

**Requires from Sprint 11:**
- Working package installation
- Convention-based path resolution (cwd = project)
- Global CLI command
- Updated help text

**Provides for Sprint 13:**
- Complete workflow (init → customize → regen)
- Template discovery by name
- Clear conventions for documentation
- Foundation for real-world testing

---

## Acceptance Criteria

### Must Have
- ✅ `doc-evergreen init` creates `.doc-evergreen/readme.json`
- ✅ Generated template is valid and works
- ✅ `doc-evergreen regen readme` finds `.doc-evergreen/readme.json`
- ✅ Short names work: `regen api`, `regen contributing`
- ✅ Absolute paths still work for flexibility
- ✅ Clear error if template not found
- ✅ Won't overwrite existing templates (unless --force)
- ✅ Interactive prompts work (or use defaults)
- ✅ All tests pass

### Nice to Have (Defer if time constrained)
- ❌ Multiple starter templates
- ❌ Template validation wizard
- ❌ Auto-detect project type

---

## Technical Approach

### Template Resolution Strategy
**Decision**: Try convention first, fall back to path
**Rationale**: Makes common case (convention) fast, keeps flexibility

### Init Command Design
**Decision**: Interactive with sensible defaults
**Rationale**: Works for both scripted and interactive use

### Template Structure
**Decision**: 4 sections (Overview, Installation, Usage, Development)
**Rationale**: Covers 90% of projects, users can customize

### Naming Convention
**Decision**: Short names without .json extension
**Rationale**: Cleaner UX, consistent with other CLI tools

---

## Testing Requirements

### TDD Approach

Follow red-green-refactor for all features:

**For each feature:**
1. 🔴 Write failing test first
2. 🟢 Write minimal code to pass
3. 🔵 Refactor for quality
4. ✅ Commit (all tests green)

### Unit Tests (Write First)

**Test template resolution:**
```python
def test_resolve_template_convention(tmp_path):
    """Short name resolves to .doc-evergreen/{name}.json"""
    os.chdir(tmp_path)
    (tmp_path / ".doc-evergreen").mkdir()
    template = tmp_path / ".doc-evergreen" / "readme.json"
    template.write_text('{"document": {...}}')

    path = resolve_template_path("readme")
    assert path == template

def test_resolve_template_absolute(tmp_path):
    """Absolute path still works"""
    template = tmp_path / "custom" / "doc.json"
    template.parent.mkdir()
    template.write_text('{"document": {...}}')

    path = resolve_template_path(str(template))
    assert path == template

def test_resolve_template_not_found(tmp_path):
    """Clear error when template not found"""
    os.chdir(tmp_path)
    with pytest.raises(FileNotFoundError) as exc:
        resolve_template_path("nonexistent")
    assert "Run 'doc-evergreen init'" in str(exc.value)
```

**Test init command:**
```python
def test_init_creates_directory(tmp_path, cli_runner):
    """init creates .doc-evergreen/ directory"""
    os.chdir(tmp_path)
    result = cli_runner.invoke(cli, ["init"])

    assert result.exit_code == 0
    assert (tmp_path / ".doc-evergreen").exists()
    assert (tmp_path / ".doc-evergreen" / "readme.json").exists()

def test_init_no_overwrite(tmp_path, cli_runner):
    """init doesn't overwrite existing template"""
    os.chdir(tmp_path)
    (tmp_path / ".doc-evergreen").mkdir()
    template = tmp_path / ".doc-evergreen" / "readme.json"
    template.write_text("CUSTOM")

    result = cli_runner.invoke(cli, ["init"])

    assert result.exit_code != 0
    assert template.read_text() == "CUSTOM"  # Unchanged

def test_init_with_force(tmp_path, cli_runner):
    """init --force overwrites existing"""
    os.chdir(tmp_path)
    (tmp_path / ".doc-evergreen").mkdir()
    template = tmp_path / ".doc-evergreen" / "readme.json"
    template.write_text("OLD")

    result = cli_runner.invoke(cli, ["init", "--force"])

    assert result.exit_code == 0
    assert "OLD" not in template.read_text()

def test_init_template_valid(tmp_path, cli_runner):
    """Generated template is valid"""
    os.chdir(tmp_path)
    cli_runner.invoke(cli, ["init"])

    template_path = tmp_path / ".doc-evergreen" / "readme.json"
    template = parse_template(template_path)
    validation = validate_template(template)
    assert validation.valid
```

### Integration Tests (Write First)

**Test full workflow:**
```python
def test_init_to_regen_workflow(tmp_path, cli_runner):
    """Full workflow: init → customize → regen"""
    os.chdir(tmp_path)

    # 1. Init project
    result = cli_runner.invoke(cli, ["init", "--name", "TestProject"])
    assert result.exit_code == 0

    # 2. Create some source files
    (tmp_path / "main.py").write_text("# Test code")

    # 3. Regenerate using short name
    result = cli_runner.invoke(cli, ["regen", "readme"])
    assert result.exit_code == 0
    assert (tmp_path / "README.md").exists()
```

**Test discovery across projects:**
```python
def test_discovery_isolated_per_project(tmp_path, cli_runner):
    """Each project has independent .doc-evergreen/"""
    project1 = tmp_path / "proj1"
    project2 = tmp_path / "proj2"

    for project in [project1, project2]:
        project.mkdir()
        os.chdir(project)
        cli_runner.invoke(cli, ["init"])

    # Each has its own templates
    assert (project1 / ".doc-evergreen" / "readme.json").exists()
    assert (project2 / ".doc-evergreen" / "readme.json").exists()

    # Templates are independent
    os.chdir(project1)
    result = cli_runner.invoke(cli, ["regen", "readme"])
    assert result.exit_code == 0
```

### Manual Testing (After Automated Tests Pass)

- [ ] Run init in empty directory
- [ ] Customize generated template
- [ ] Regenerate with short name
- [ ] Try with absolute path
- [ ] Test error messages
- [ ] Verify .gitignore suggestions

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## What You Learn

After this sprint:
1. **What starter template works best?** → Informs future defaults
2. **Is .doc-evergreen/ convention clear?** → Validates design
3. **What errors do users hit?** → Guides error message improvements
4. **Do short names feel natural?** → Confirms UX decisions

These learnings inform Sprint 13's documentation and validation.

---

## Success Metrics

**Quantitative:**
- Init creates valid template in <5 seconds
- Template discovery works 100% of time
- Zero configuration needed
- All tests green

**Qualitative:**
- "I know where to put templates" - convention is obvious
- "Getting started was easy" - init removes friction
- Short names feel natural
- Error messages are helpful

---

## Implementation Order (TDD Daily Workflow)

### Morning (4 hours): Template Discovery

**Hour 1-2: Resolution Logic**
- 🔴 Write tests: `test_resolve_template_*`
- 🟢 Implement `resolve_template_path()`
- 🔵 Refactor: Clean up logic, improve errors
- ✅ Commit: "feat: add template discovery in .doc-evergreen/"

**Hour 3-4: Update regen-doc**
- 🔴 Write tests: `test_regen_short_names`
- 🟢 Update regen-doc to use resolution
- 🔵 Refactor: Simplify argument handling
- ✅ Commit: "feat: support short template names"

### Afternoon (4 hours): Init Command

**Hour 5-6: Init Command**
- 🔴 Write tests: `test_init_*`
- 🟢 Implement init command
- 🔵 Refactor: Extract template generation
- ✅ Commit: "feat: add init command"

**Hour 7: Integration & Testing**
- 🔴 Write test: `test_init_to_regen_workflow`
- 🟢 Fix any integration issues
- 🔵 Refactor: Improve error handling
- ✅ Commit: "test: verify full init workflow"

**Hour 8: Documentation & Polish**
- Update USER_GUIDE.md with convention
- Add examples to help text
- Run full test suite
- Manual testing
- ✅ Commit: "docs: document .doc-evergreen/ convention"

---

## Known Limitations (By Design)

1. **Single starter template** - One good default (can add more later)
2. **No template wizard** - Simple JSON editing sufficient
3. **Convention required** - Must use .doc-evergreen/ for short names
4. **No template validation during init** - Basic validation only

---

## Next Sprint Preview

After Sprint 12 ships, Sprint 13 will add:
- Comprehensive installation guide
- Migration guide from v0.3.0
- Real-world usage validation
- Troubleshooting documentation
- Final polish and testing

Sprint 12 completes the feature set; Sprint 13 makes it production-ready.
