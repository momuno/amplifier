# Doc-Evergreen Sprint Plan: v0.4.0 - Standalone Tool

## Version Summary
**Version**: v0.4.0
**Feature**: Convention-Based Standalone Tool
**Problem**: doc_evergreen only works within its own repository. Can't be installed or used with other projects.

**Target**: 2-3 day timeline to shippable standalone tool
**Breaking Change**: Yes - changes to how templates reference sources (now relative to cwd, not template)

---

## Sprint Overview

| Sprint | Duration | Name | Value Delivered |
|--------|----------|------|-----------------|
| 11 | 1 day | Package & Convention | Installable tool that works from any project |
| 12 | 1 day | Template Discovery & Init | Bootstrap projects with `init` command |
| 13 | 1 day | Documentation & Validation | Complete guide and real-world testing |

**Total: 3 days**

---

## Value Progression

### Sprint 11: Installable Tool with Convention-Based Usage
**After this sprint, you can**:
- Install doc-evergreen globally: `pipx install .`
- Run `doc-evergreen` from ANY project directory
- Sources in templates are relative to project root (cwd)
- Zero configuration needed

**What you learn**:
- Does convention-based approach feel natural?
- Are there edge cases with path resolution?
- Is installation smooth?

### Sprint 12: Template Discovery & Project Bootstrap
**After this sprint, you can**:
- Run `doc-evergreen init` to bootstrap projects
- Use short names: `doc-evergreen regen readme`
- Templates live in `.doc-evergreen/` directory
- Clear workflow for new projects

**What you learn**:
- What starter templates do users need?
- Is `.doc-evergreen/` convention clear?
- What errors do users hit during init?

### Sprint 13: Production-Ready with Documentation
**After this sprint, you can**:
- Follow comprehensive installation guide
- Understand migration from v0.3.0
- Use tool confidently on real projects
- Troubleshoot common issues

**What you learn**:
- What documentation gaps remain?
- Are there hidden edge cases?
- Is tool ready for wider use?

---

## Integrated Issues

This sprint plan addresses:

- **ISSUE-011** (project_root support) → Sprint 11: Convention-based approach replaces explicit field
- **ISSUE-010** (Makefile OUTPUT param) → RESOLVED: Already fixed in v0.3.0
- **ISSUE-008** (mode clarity) → DEFERRED: Not critical for v0.4.0
- **ISSUE-009** (single-shot mode) → DEFERRED: Chunked mode sufficient

---

## What Changes vs. What Stays

### Stays the Same (v0.3.0 → v0.4.0)
- Template JSON structure (Document → Sections)
- Schema classes (Template, Document, Section)
- ChunkedGenerator implementation
- Change detection and diff system
- `regen-doc` command functionality
- Validation system

### Changes (New in v0.4.0)
- **New packaging**: pyproject.toml + entry point
- **New convention**: cwd = project root
- **New command**: `init` to bootstrap projects
- **New discovery**: Templates in `.doc-evergreen/` directory
- **Breaking change**: Source paths now relative to cwd, not template
- **Enhanced UX**: Global installation, zero config

### Deferred to Future
- PyPI publishing - git install sufficient for now
- Watch mode - manual regeneration sufficient
- CI/CD integration helpers
- Template marketplace
- Multi-project aggregation
- IDE integration

---

## Why This Sequencing?

### Value-First, Not Infrastructure-First

**NOT this (infrastructure-first)**:
```
❌ Sprint 11: Build elaborate config system
❌ Sprint 12: Create template marketplace
❌ Sprint 13: Finally make it installable (value in Sprint 13!)
```

**YES this (value-first)**:
```
✅ Sprint 11: Installable + works anywhere (value immediately!)
✅ Sprint 12: Bootstrap makes it easy to start (adoption)
✅ Sprint 13: Document and validate (production-ready)
```

### Learning Checkpoints

Each sprint teaches something critical for the next:

**Sprint 11 → Sprint 12**:
- Installing reveals what users need to get started (init command)
- Convention-based usage shows where templates should live

**Sprint 12 → Sprint 13**:
- Init command reveals what docs need emphasis
- Template discovery shows what errors need better messages

**Sprint 13 → v0.5.0**:
- Real-world usage reveals next priorities
- Documentation gaps guide future improvements

---

## Technical Decisions

### Convention Over Configuration
- cwd IS the project root (no --project flag needed)
- Templates in `.doc-evergreen/` (familiar pattern like .github/)
- Sources relative to cwd, not template location
- **Why**: Simpler mental model, zero config

### Package Structure
- Use pyproject.toml (modern Python standard)
- Entry point: `doc-evergreen` command
- Install with pip/pipx (no custom installers)
- **Why**: Standard, well-understood, works everywhere

### Breaking Change Handling
- v0.4.0 is a breaking change (source path resolution)
- Provide clear migration guide
- Old templates need one-time update
- **Why**: Better long-term design worth the migration cost

### Template Discovery
- Look for `.doc-evergreen/{name}.json`
- Fall back to absolute paths if needed
- Clear error if template not found
- **Why**: Convention makes common case simple, still flexible

---

## Deferred to v0.5.0+

### Features NOT in v0.4.0
1. **PyPI publishing** - Git install works fine for now
2. **Watch mode** - Manual regen sufficient
3. **Template versioning** - Not needed yet
4. **Project config files** - Convention removes need
5. **Advanced template discovery** - Simple discovery sufficient
6. **CI/CD integration helpers** - Manual workflow first
7. **Multi-project aggregation** - Single project focus
8. **Template marketplace** - Too early
9. **IDE integration** - Command-line first

### Why Defer?
- **Not needed to prove value**: Basic standalone tool is enough
- **Optimization without data**: Don't know what's needed until users try it
- **Complexity vs benefit**: Each adds time but unclear value
- **Learn first, build later**: Real usage reveals what matters

---

## Timeline at a Glance

```
Day 1: Sprint 11 (Package & Convention)
├── Morning: pyproject.toml + entry point
├── Afternoon: Convention-based path resolution
└── Evening: Installation testing

Day 2: Sprint 12 (Template Discovery & Init)
├── Morning: .doc-evergreen/ discovery
├── Afternoon: init command
└── Evening: Integration testing

Day 3: Sprint 13 (Documentation & Validation)
├── Morning: Updated documentation
├── Afternoon: Real-world testing
└── Evening: Final polish + ship
```

**Flexibility built in**:
- Each sprint is self-contained
- Can extend Day 3 if needed for testing
- Can stop after Sprint 12 and still have core value

---

## Success Criteria

### Quantitative
- ✅ `pipx install .` works from doc_evergreen directory
- ✅ `doc-evergreen --help` available globally
- ✅ `doc-evergreen init` creates working template
- ✅ `doc-evergreen regen readme` works from any project
- ✅ Test coverage >80%
- ✅ Works with 3+ different project structures

### Qualitative
- ✅ User can install in <2 minutes
- ✅ First doc generation in <5 minutes
- ✅ Zero PYTHONPATH configuration needed
- ✅ Convention feels natural and obvious
- ✅ Migration from v0.3.0 clear and simple
- ✅ Team confident shipping v0.4.0

### Ultimate Test
**Can a user install tool once and use it on any project?**
- If YES → Standalone tool success
- If NO → Identify blockers and iterate

---

## Breaking Changes & Migration

### What Breaks in v0.4.0
1. **Source path resolution**: Sources now relative to cwd, not template location
2. **Installation method**: Now requires pip/pipx install
3. **Template location**: Recommended to move to `.doc-evergreen/`

### Migration Path from v0.3.0
1. Install tool: `pip install -e .` from doc_evergreen directory
2. Move templates to `.doc-evergreen/` in your project
3. Update source paths in templates (if needed)
4. Test with `doc-evergreen regen <template>`

**Migration Guide** will be included in Sprint 13 documentation.

---

## Risk Assessment

### Low Risk
- Standard Python packaging (well understood)
- Convention pattern familiar (like .github/, .vscode/)
- Path resolution straightforward
- Clear rollback path

### Medium Risk
- Path resolution change might break edge cases
- Installation adds complexity
- Users need to migrate existing templates
- Different project structures might have issues

### Mitigation
- Test with 3-4 different project types
- Clear error messages for path issues
- Comprehensive migration guide
- Document known limitations
- Conservative estimates with buffer

---

## Next Steps

1. **Review sprint plan** - Does this sequencing make sense?
2. **Read Sprint 11 details** - See SPRINT_11_PACKAGE_CONVENTION.md
3. **Start building** - Day 1 begins with installable tool
4. **Ship fast, learn fast** - Iterate based on real usage

---

## Sprint Document Links

Detailed plans for each sprint:

1. [Sprint 11: Package & Convention](./SPRINT_11_PACKAGE_CONVENTION.md) - 1 day
2. [Sprint 12: Template Discovery & Init](./SPRINT_12_DISCOVERY_INIT.md) - 1 day
3. [Sprint 13: Documentation & Validation](./SPRINT_13_DOCS_VALIDATION.md) - 1 day

---

## Remember

- Sprint 11 delivers installable tool on Day 1
- Each sprint makes the tool MORE useful
- Convention over configuration = simplicity
- Test with real projects, real workflows
- Breaking changes worth it for better design
- Document migration clearly

**The goal**: Standalone tool that "just works" anywhere.
