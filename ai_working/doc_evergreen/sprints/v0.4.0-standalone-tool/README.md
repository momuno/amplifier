# Sprint Plan v0.4.0: Standalone Tool

**Created:** 2025-11-20
**Status:** Ready for Implementation
**Duration:** 3 days (conservative estimate)

---

## Quick Overview

Transform doc_evergreen from repository-bound tool into a true standalone CLI application that works with ANY project.

**Key Theme:** Convention over Configuration

---

## Files in This Directory

1. **SPRINT_PLAN.md** - Overall plan and value progression
2. **SPRINT_11_PACKAGE_CONVENTION.md** - Day 1: Installable package + convention-based usage
3. **SPRINT_12_DISCOVERY_INIT.md** - Day 2: Template discovery + init command
4. **SPRINT_13_DOCS_VALIDATION.md** - Day 3: Documentation + real-world validation

---

## The Big Picture

### Current State (v0.3.0)
- Works only within doc_evergreen repository
- Requires PYTHONPATH setup
- Templates reference sources relative to template location
- Not reusable across projects

### Target State (v0.4.0)
- Installable globally: `pipx install .`
- Works from ANY project directory
- Convention-based: Templates in `.doc-evergreen/`
- Sources relative to project root (cwd)
- Zero configuration

---

## Value Delivered Per Sprint

### Sprint 11 (Day 1)
**Installable Tool**
- Install once: `pipx install git+https://...`
- Use anywhere: `cd any-project && doc-evergreen regen-doc template.json`
- Sources resolved relative to project root

### Sprint 12 (Day 2)
**Bootstrap & Discovery**
- Bootstrap: `doc-evergreen init` creates starter template
- Short names: `doc-evergreen regen readme` (finds `.doc-evergreen/readme.json`)
- Convention: Templates live in `.doc-evergreen/` directory

### Sprint 13 (Day 3)
**Production Ready**
- Installation guide
- Migration guide from v0.3.0
- Real-world validation (3+ projects)
- Example templates

---

## Breaking Changes

v0.4.0 includes breaking changes (worth it for better design):

1. **Source Path Resolution**
   - OLD: Relative to template location
   - NEW: Relative to cwd (project root)

2. **Installation Required**
   - OLD: Run from repository
   - NEW: Install globally with pip/pipx

3. **Convention Introduced**
   - OLD: Templates anywhere
   - NEW: Recommended in `.doc-evergreen/`

Migration guide included in Sprint 13.

---

## Success Criteria

After v0.4.0 ships, users should be able to:

1. Install tool: `pipx install git+https://github.com/user/doc-evergreen.git`
2. Bootstrap project: `cd my-app && doc-evergreen init`
3. Generate docs: `doc-evergreen regen readme`
4. Just works: No config, no setup, no confusion

**If all 4 work smoothly → v0.4.0 is successful**

---

## Key Decisions

### 1. Convention Over Configuration
**Choice:** cwd = project root, templates in `.doc-evergreen/`
**Why:** Simpler mental model, zero config, familiar pattern

### 2. Breaking Change Accepted
**Choice:** Change source path resolution
**Why:** Better long-term design worth migration cost

### 3. Git Install Only (v0.4.0)
**Choice:** No PyPI publishing yet
**Why:** Works fine, reduces distribution overhead

### 4. TDD Throughout
**Choice:** Test-first for all features
**Why:** Ensures quality, enables refactoring, documents behavior

---

## Timeline

```
Day 1: Sprint 11 - Package & Convention
├── Morning: pyproject.toml + entry point + tests
├── Afternoon: Convention-based path resolution + tests
└── Evening: Installation testing

Day 2: Sprint 12 - Discovery & Init
├── Morning: Template discovery logic + tests
├── Afternoon: Init command + tests
└── Evening: Integration testing

Day 3: Sprint 13 - Docs & Validation
├── Morning: Installation + migration guides
├── Afternoon: Real-world validation (3+ projects)
└── Evening: Examples + final polish
```

**Conservative:** 3 days
**Optimistic:** 2 days (if no surprises)

---

## Deferred to v0.5.0+

Features NOT in v0.4.0 (15 deferred):
- PyPI publishing
- Watch mode
- Template marketplace
- CI/CD integration helpers
- Multi-project aggregation
- IDE integration
- Advanced template discovery
- Template versioning
- Dry-run mode
- Backup/rollback
- Performance optimization
- Project config files
- Git integration
- Single-shot mode
- Mode clarity docs

**All preserved** in `ai_working/doc_evergreen/convergence/2025-11-20-standalone-tool/DEFERRED_FEATURES.md`

---

## Next Steps

1. Review SPRINT_PLAN.md for overall strategy
2. Review SPRINT_11_PACKAGE_CONVENTION.md for Day 1 details
3. Begin implementation with TDD approach
4. Ship with confidence!

---

## Related Documents

**Convergence:**
- `../../convergence/2025-11-20-standalone-tool/FEATURE_SCOPE.md` - Feature details
- `../../convergence/2025-11-20-standalone-tool/CONVERGENCE_COMPLETE.md` - Decisions
- `../../convergence/2025-11-20-standalone-tool/DEFERRED_FEATURES.md` - What's not included

**Issues:**
- `../../issues/ISSUE-011-project-root-support.md` - Replaced by convention approach
- `../../issues/ISSUES_TRACKER.md` - All open issues

**Previous Sprints:**
- `../v0.3.0-test-case-basic-regen/` - Previous sprint reference

---

## Notes for Implementers

### TDD Discipline
- Write test FIRST (red)
- Write minimal code to pass (green)
- Refactor for quality (refactor)
- Commit with green tests
- Never skip tests

### Path Resolution
- All sources relative to `Path.cwd()`
- Template location doesn't matter
- Clear errors when sources not found

### Convention Benefits
- Zero configuration
- Obvious where templates live
- Familiar pattern (.github/, .vscode/)
- Templates travel with project

### Breaking Change Communication
- Be honest and clear
- Provide migration path
- Explain the "why"
- Make migration simple

---

**Let's ship a standalone tool that "just works"!**
