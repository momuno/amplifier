# ISSUE-011: Add project_root Support for Standalone Tool Usage

**Status:** Superseded (Better Solution Implemented)
**Priority:** N/A (Superseded)
**Type:** Feature
**Created:** 2025-11-20
**Resolved:** 2025-11-20 (Sprints 11-12)
**Resolution:** Superseded by convention-based cwd approach (simpler, zero config)

## Description

doc_evergreen is designed to be a standalone tool in its own repository, used to document OTHER projects. The current design assumes the tool and the project being documented are in the same repository. This issue tracks the architectural changes needed to support external project documentation.

**User Goal:** Use doc_evergreen from one repository to document projects in different repositories.

## Current Limitations

1. **No project location specification**: Templates assume sources are relative to tool's cwd
2. **Output always in tool repo**: Generated docs saved where tool runs, not in target project
3. **Non-portable templates**: Templates can't specify which project they document
4. **Confusing workflow**: Users must cd to target project before running tool

## Proposed Architecture

### Template Schema Addition

Add `project_root` field to template schema:

```json
{
  "project_root": "../my-app",        // NEW: Path to target project
  "document": {
    "title": "My App Docs",
    "output": "README.md",             // Relative to project_root
    "sections": [{
      "heading": "Overview",
      "sources": ["src/main.py"]       // Relative to project_root
    }]
  }
}
```

### CLI Interface

Support flexible project and output overrides:

```bash
# Use template defaults
make regen-doc TEMPLATE=templates/my-app.json

# Override project location
make regen-doc TEMPLATE=templates/my-app.json PROJECT=../my-app

# Override output
make regen-doc TEMPLATE=templates/my-app.json OUTPUT=docs/API.md

# Override both
make regen-doc TEMPLATE=templates/my-app.json PROJECT=../my-app OUTPUT=README.md
```

### Resolution Logic

**Project Root Resolution:**
1. CLI `PROJECT` parameter (highest priority)
2. Template `project_root` field
3. Current working directory (fallback)

**Output Path Resolution:**
- CLI `OUTPUT` parameter overrides template `output`
- Both resolved relative to `project_root`
- Absolute paths respected as-is

**Source Path Resolution:**
- All source paths in template resolved relative to `project_root`
- Enables portable templates across machines/users

## Acceptance Criteria

To consider this issue resolved:

- [ ] Template schema includes `project_root` field
- [ ] CLI accepts `--project-root` parameter
- [ ] Makefile exposes `PROJECT` variable for easy override
- [ ] Source files resolved relative to `project_root`
- [ ] Output path resolved relative to `project_root`
- [ ] CLI `OUTPUT` parameter overrides template `output`
- [ ] Resolution logic follows priority: CLI > template > cwd
- [ ] All existing tests updated for new resolution logic
- [ ] New tests cover all resolution scenarios
- [ ] Example templates updated with `project_root`
- [ ] TEMPLATES.md documents new field
- [ ] USER_GUIDE.md includes usage examples
- [ ] Migration guide provided for v0.3.0 templates

## Impact Analysis

**Severity:** Medium - Not blocking current usage, but essential for intended use case
**User Impact:**
- **Positive**: Natural workflow for standalone tool
- **Positive**: Portable templates across projects
- **Breaking**: Requires template updates (schema change)
**Workaround:** Users can manually cd to project before running tool (current behavior)

## Related Issues

(None yet - this is the first tracked issue)

## Technical Notes

### Proposed Solution

**1. Schema Changes** (`src/doc_evergreen/models.py`):
```python
@dataclass
class Template:
    project_root: Optional[str] = None  # NEW field
    document: Document
```

**2. CLI Changes** (`src/doc_evergreen/cli.py`):
```python
@click.command()
@click.option('--template', required=True)
@click.option('--project-root', type=click.Path(exists=True))  # NEW
@click.option('--output', type=click.Path())
def regen_doc(template: str, project_root: Optional[str], output: Optional[str]):
    # Resolution logic here
```

**3. Resolution Function** (new utility):
```python
def resolve_project_root(
    cli_project: Optional[str],
    template_project: Optional[str],
    cwd: Path
) -> Path:
    """Resolve project root with priority: CLI > template > cwd."""
    if cli_project:
        return Path(cli_project).resolve()
    if template_project:
        return Path(template_project).resolve()
    return cwd

def resolve_output_path(
    cli_output: Optional[str],
    template_output: str,
    project_root: Path
) -> Path:
    """Resolve output path relative to project_root."""
    output = cli_output or template_output
    output_path = Path(output)
    if output_path.is_absolute():
        return output_path
    return (project_root / output).resolve()

def resolve_source_paths(
    sources: List[str],
    project_root: Path
) -> List[Path]:
    """Resolve all source paths relative to project_root."""
    return [
        Path(src) if Path(src).is_absolute() else project_root / src
        for src in sources
    ]
```

**4. Makefile Changes**:
```makefile
# Add PROJECT parameter
regen-doc:
	uv run doc-evergreen regen-doc \
		--template $(TEMPLATE) \
		$(if $(PROJECT),--project-root $(PROJECT)) \
		$(if $(OUTPUT),--output $(OUTPUT))
```

### Alternative Approaches

**Alternative 1: Separate config file**
- Pros: Clean separation of project config from document template
- Cons: Two files to maintain, more complex for users
- Verdict: Rejected - adds unnecessary complexity

**Alternative 2: Environment variables**
- Pros: No CLI changes needed
- Cons: Less discoverable, harder to use in Makefile
- Verdict: Rejected - CLI parameters more explicit

**Alternative 3: Template inheritance**
- Pros: Base templates for project, specific for documents
- Cons: Over-engineered for v0.4.0 scope
- Verdict: Deferred - consider for v0.5.0 if patterns emerge

### Implementation Complexity

**Complexity:** Medium
**Reasoning:**
- Schema change is straightforward (one field)
- CLI parameter addition is simple (click.option)
- Resolution logic is clear but needs thorough testing
- Template migration is mechanical but affects all examples
- Documentation updates are substantial but clear

**Estimated Effort:** 1-2 days
- Day 1: Schema, CLI, resolution logic, core tests
- Day 2: Template updates, documentation, edge case testing

## Testing Notes

### Test Cases Needed

**Resolution Logic Tests:**
- [ ] CLI project overrides template project_root
- [ ] Template project_root used when CLI not provided
- [ ] CWD used when neither CLI nor template provided
- [ ] CLI output overrides template output
- [ ] Output resolved relative to project_root
- [ ] Absolute output paths respected
- [ ] Source paths resolved relative to project_root
- [ ] Absolute source paths respected

**Integration Tests:**
- [ ] Documenting external project with template defaults
- [ ] Overriding project location via CLI
- [ ] Overriding output path via CLI
- [ ] Overriding both project and output
- [ ] Template with no project_root (backward compat)

**Edge Cases:**
- [ ] Non-existent project_root (should fail gracefully)
- [ ] Project_root with no sources (should warn)
- [ ] Relative paths with ../.. navigation
- [ ] Symlinked project directories
- [ ] Network/cloud-synced project directories

**Regression Risk:** Medium
- Schema change affects template loading
- Path resolution affects all file operations
- Need comprehensive test coverage

## Sprint Assignment

**Assigned to:** Backlog - v0.4.0
**Rationale:**
- High value for standalone tool use case
- Breaking change requires version bump
- Fits naturally after v0.3.0 stabilization
- Not blocking current development workflow
- Clear scope and well-defined requirements

**Dependencies:**
- Must complete v0.3.0 release first (Sprint 8 completion)
- Should gather user feedback on v0.3.0 before implementation
- Consider alongside other v0.4.0 architectural enhancements

## Comments / Updates

### 2025-11-20
Initial issue created based on architectural design discussion. This represents a natural evolution from single-repo tool to true standalone documentation tool. The design preserves backward compatibility (project_root optional) while enabling the intended use case.

**Key Design Decisions:**
1. **Optional field**: project_root defaults to cwd for backward compatibility
2. **CLI override**: Always allow runtime override of template defaults
3. **Relative resolution**: All paths relative to project_root for portability
4. **Absolute escape hatch**: Absolute paths work for power users

**Next Steps:**
1. ~~Validate design with convergence-architect~~ ✅ Done
2. ~~Create detailed implementation plan~~ ✅ Done
3. ~~Set up v0.4.0 sprint planning~~ ✅ Done
4. ~~Consider related architectural improvements~~ ✅ Evaluated and chose simpler approach

---

## RESOLUTION

**Resolved in:** Sprints 11-12 (v0.4.0)
**Commits:** Standalone repo (9 commits)
**Date:** 2025-11-20
**Resolution Type:** Superseded by Better Design

### What We Did Instead

During convergence session, evaluated 3 approaches and chose **Convention over Configuration**:

**Implemented Solution (BETTER than project_root):**
```bash
# Install tool once
pip install -e /path/to/doc-evergreen

# Use from ANY project
cd /my-project                  # Your project root
doc-evergreen init              # Creates .doc-evergreen/
doc-evergreen regen-doc readme  # Sources from cwd!
```

**Why This is Better:**
- ✅ Zero configuration (no project_root field needed)
- ✅ Natural mental model (run from project = document that project)
- ✅ Simpler templates (one less field to specify)
- ✅ Obvious behavior (cwd IS the project)
- ✅ Familiar pattern (.doc-evergreen/ like .github/)

**What Was Implemented:**
1. **Installable Package** (Sprint 11):
   - pyproject.toml with CLI entry point
   - src-layout structure
   - Works globally after `pip install`

2. **Convention-Based Resolution** (Sprint 11):
   - `base_dir = Path.cwd()` (not template location)
   - Sources relative to where command runs
   - Output relative to cwd

3. **Template Discovery** (Sprint 12):
   - .doc-evergreen/ convention directory
   - Short names: `regen-doc readme`
   - Templates stored with project

4. **Init Command** (Sprint 12):
   - `doc-evergreen init` bootstraps projects
   - Creates .doc-evergreen/readme.json
   - Ready-to-use starter template

**Tests:** 119 passing (36 new tests for v0.4.0 features)

**Documentation:**
- INSTALLATION.md - Complete install guide
- MIGRATION_v0.3_to_v0.4.md - Breaking changes explained
- Updated USER_GUIDE.md and BEST_PRACTICES.md

### Why Original Design Was Rejected

The `project_root` field approach had issues:
- ❌ Required configuration (field in every template)
- ❌ More complex (3-way resolution: CLI > template > cwd)
- ❌ Less obvious (which takes priority?)
- ❌ Two sources of truth (template field + CLI param)

### Comparison

**Original Proposal:**
```json
{"project_root": "../my-app", "document": {...}}
```
```bash
doc-evergreen regen-doc --project-root ../my-app template.json
```

**Implemented Solution:**
```bash
cd /my-app  # Just change directory!
doc-evergreen regen-doc readme
```

**The convention approach is dramatically simpler.**

### User Impact

**Migration:** Existing v0.3.0 users need to:
1. Install tool: `pip install -e .`
2. Update source paths (remove `../` if templates were in subdirectory)
3. Optionally adopt .doc-evergreen/ convention

See MIGRATION_v0.3_to_v0.4.md for complete guide.

**Result:** Much better UX than original proposal would have provided.
