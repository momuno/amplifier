# Feature Scope: Standalone Tool

**Version**: v0.4.0
**Date**: 2025-11-20
**Theme**: Convention-Based Standalone Tool

---

## Vision

Transform doc_evergreen into a true standalone CLI tool that can document ANY project on the local filesystem using a simple convention-based approach.

**User Mental Model**: "I'm in my project directory, I run doc-evergreen, it documents my project"

---

## Problem Statement

**Current State (v0.3.0)**:
- doc_evergreen only works within its own repository
- Complex PYTHONPATH setup required
- Can only document files in the same repo
- Not reusable across projects
- Installation unclear

**Target State (v0.4.0)**:
- doc_evergreen is a standalone installable tool
- Works with ANY project on filesystem
- Simple installation: `pip install -e .`
- Convention-based: Templates in `.doc-evergreen/` directory
- Just works: Run from project root, tool documents that project

---

## In-Scope Features (v0.4.0)

### Feature 1: Proper Python Package

**What**: Create installable package with CLI entry point

**Deliverables**:
- Add `pyproject.toml` to doc_evergreen
- Define `[project.scripts]` entry point: `doc-evergreen = "doc_evergreen.cli:cli"`
- Configure dependencies properly
- Add build system configuration

**Acceptance Criteria**:
- [ ] `pip install -e .` works from doc_evergreen directory
- [ ] `doc-evergreen --help` command available globally
- [ ] `pipx install .` creates isolated global command
- [ ] All dependencies installed automatically
- [ ] Entry point calls correct CLI function

**Value**: Users can install tool once, use everywhere

**Effort**: 2-3 hours

---

### Feature 2: Convention-Based Project Discovery

**What**: Tool assumes cwd is the project being documented

**Deliverables**:
- Change source resolution from template-relative to cwd-relative
- Update ChunkedGenerator to use cwd as base_dir
- Remove complex PYTHONPATH requirements
- Update all path resolution logic

**Acceptance Criteria**:
- [ ] Running from project root documents that project
- [ ] Sources in template are relative to project root (cwd)
- [ ] Output paths relative to project root
- [ ] No --project flag needed (cwd IS the project)
- [ ] Works with any directory structure

**Value**: Zero configuration - just works

**Effort**: 1-2 hours (partially done - cli.py already uses Path.cwd())

---

### Feature 3: Template Directory Convention

**What**: Projects store templates in `.doc-evergreen/` directory

**Deliverables**:
- Template discovery in `.doc-evergreen/` directory
- Short-form command: `doc-evergreen regen readme` finds `.doc-evergreen/readme.json`
- Clear error if `.doc-evergreen/` doesn't exist
- Documentation explaining convention

**Acceptance Criteria**:
- [ ] `doc-evergreen regen readme` finds `.doc-evergreen/readme.json`
- [ ] `doc-evergreen regen api` finds `.doc-evergreen/api.json`
- [ ] Clear error if template not found in `.doc-evergreen/`
- [ ] Can still use absolute paths if needed
- [ ] `.gitignore` recommendation for generated files

**Value**: Clean project organization, familiar pattern

**Effort**: 3-4 hours

---

### Feature 4: Init Command

**What**: Bootstrap new projects with starter templates

**Deliverables**:
- `doc-evergreen init` command
- Creates `.doc-evergreen/` directory
- Generates starter template (readme.json)
- Interactive prompts for customization (or use defaults)
- Example templates users can copy

**Acceptance Criteria**:
- [ ] `doc-evergreen init` creates `.doc-evergreen/readme.json`
- [ ] Template is valid and ready to use
- [ ] Prompts for project name, description (optional)
- [ ] Provides starter sections (Overview, Installation, Usage)
- [ ] Works in any directory
- [ ] Doesn't overwrite existing `.doc-evergreen/`

**Value**: Instant onboarding, zero friction

**Effort**: 4-5 hours

---

### Feature 5: Updated Documentation

**What**: Reflect new standalone usage model

**Deliverables**:
- Update USER_GUIDE.md with installation instructions
- Update TEMPLATES.md with cwd-relative paths
- Update BEST_PRACTICES.md with convention examples
- Add README.md for doc_evergreen itself
- Migration guide from v0.3.0

**Acceptance Criteria**:
- [ ] Installation section shows pip install -e .
- [ ] Examples use convention-based approach
- [ ] Clear explanation of `.doc-evergreen/` pattern
- [ ] Migration guide for v0.3.0 users
- [ ] All examples tested and working

**Value**: Users understand and can use the tool

**Effort**: 2-3 hours

---

## Success Metrics

**Quantitative**:
- Install time: <2 minutes (clone + pip install)
- First doc generation: <5 minutes (init + regen)
- Zero PYTHONPATH configuration
- Works with 100% of local projects

**Qualitative**:
- "Just works" - no setup complexity
- Familiar pattern (like .github/, .vscode/)
- Natural workflow (run from project)
- Clear what to do when errors occur

---

## Out of Scope (Deferred)

Everything except the 5 features above:
- PyPI publishing
- CI/CD integration helpers
- Watch mode / auto-regeneration
- Multi-project aggregation
- Template marketplace
- IDE integration
- Git integration
- Advanced config management
- Performance optimization
- Single-shot mode (ISSUE-009)
- Mode clarity (ISSUE-008)

---

## Dependencies

**Requires**:
- v0.3.0 complete ✅ (done)
- ISSUE-011 design (captured)

**Provides**:
- True standalone tool
- Foundation for future features
- Clean user experience

---

## Risk Assessment

**Low Risk**:
- All changes are additive
- v0.3.0 functionality preserved
- Clear rollback path

**Medium Risk**:
- Installation step adds complexity
- Path resolution change might break edge cases
- Need comprehensive testing across different project structures

**Mitigation**:
- Test with 3-4 different project types
- Clear error messages for unsupported scenarios
- Document known limitations

---

## Estimated Timeline

**Total**: 12-17 hours (1.5-2 days)

- Feature 1 (Package): 2-3 hours
- Feature 2 (Convention): 1-2 hours (mostly done)
- Feature 3 (Discovery): 3-4 hours
- Feature 4 (Init): 4-5 hours
- Feature 5 (Docs): 2-3 hours

**Conservative**: 3 days with testing and polish

---

## Next Step

After feature scope approval:
- Use `/convergent-dev:2-plan-sprints` to break into executable sprints
- Sprint plan will specify day-by-day implementation
- Follow TDD methodology throughout
