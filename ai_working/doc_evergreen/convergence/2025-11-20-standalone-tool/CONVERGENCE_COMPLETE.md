# Convergence Complete: Standalone Tool

**Date**: 2025-11-20
**Version**: v0.4.0
**Duration**: Focused scope definition (45 minutes)

---

## Summary

Successfully converged from exploration to focused feature scope for doc_evergreen v0.4.0.

**Theme**: Convention-Based Standalone Tool

---

## Process

### DIVERGE Phase
- Explored full possibility space of "standalone tool"
- Considered 10+ different approaches
- Evaluated installation methods, config strategies, template management

### CAPTURE Phase
- Organized ideas into structured features
- Identified core vs. nice-to-have
- Grouped related capabilities

### CONVERGE Phase
- Selected 5 essential features for v0.4.0
- Ruthless focus on enabling standalone usage
- Clear value proposition for each feature

### DEFER Phase
- Deferred 15 features to future versions
- Each with clear reconsider conditions
- Preserved all ideas in DEFERRED_FEATURES.md

---

## Feature Scope (v0.4.0)

**5 Features** enabling standalone tool usage:

1. **Proper Python Package** (2-3 hours)
   - pyproject.toml with entry point
   - pip/pipx installable
   - Global CLI command

2. **Convention-Based Discovery** (1-2 hours)
   - Run from project root
   - cwd-based path resolution
   - No configuration needed

3. **Template Directory Convention** (3-4 hours)
   - `.doc-evergreen/` directory pattern
   - Short-form template names
   - Familiar pattern (like .github/)

4. **Init Command** (4-5 hours)
   - Bootstrap projects quickly
   - Starter templates
   - Interactive setup

5. **Updated Documentation** (2-3 hours)
   - Installation guide
   - Convention explanations
   - Migration from v0.3.0

**Total Effort**: 12-17 hours (1.5-2 days)
**Conservative Estimate**: 3 days with testing

---

## Key Decisions

### Decision 1: Convention Over Configuration
**Choice**: Convention-based (.doc-evergreen/) over explicit project_root field
**Rationale**: Simpler mental model, zero config, familiar pattern
**Trade-off**: Less flexible, but flexibility not needed for MVP

### Decision 2: Templates in Project
**Choice**: Templates live in target project, not tool repo
**Rationale**: Templates travel with project, clear ownership
**Trade-off**: Template duplication across projects (acceptable)

### Decision 3: cwd = project root
**Choice**: Current directory is implicitly the project being documented
**Rationale**: Natural, no --project flag needed, obvious behavior
**Trade-off**: Can't document project from different location (rare need)

### Decision 4: Git-based install only
**Choice**: No PyPI publishing in v0.4.0
**Rationale**: pip install from git works fine, avoid distribution overhead
**Trade-off**: Slightly harder discovery (but tool is early stage)

---

## Deferred Count

**15 features deferred** to v0.5.0+:
- PyPI publishing
- Advanced template discovery
- Project config files
- Template marketplace
- Watch mode
- CI/CD helpers
- Multi-project aggregation
- IDE integration
- Git integration
- Single-shot mode
- Mode clarity docs
- Template versioning
- Dry-run mode
- Backup/rollback
- Performance optimization

**All preserved** in DEFERRED_FEATURES.md with reconsider conditions.

---

## Files Created

1. **FEATURE_SCOPE.md**
   - 5 features with acceptance criteria
   - Effort estimates
   - Clear value propositions

2. **DEFERRED_FEATURES.md**
   - 15 deferred features
   - Reconsider conditions for each
   - Effort estimates preserved

3. **CONVERGENCE_COMPLETE.md** (this file)
   - Process summary
   - Key decisions documented
   - Next steps clear

**Location**: `ai_working/doc_evergreen/convergence/2025-11-20-standalone-tool/`

---

## Next Steps

### Immediate
1. Review and approve feature scope
2. Use `/convergent-dev:2-plan-sprints doc_evergreen` to create sprint plan
3. Assign version number (v0.4.0 confirmed)
4. Begin Sprint 11 implementation

### Before Implementation
- [ ] Review FEATURE_SCOPE.md
- [ ] Confirm 5 features are right scope
- [ ] Approve estimated timeline
- [ ] Ready to begin sprints

---

## Validation

**Scope Check**:
- ✅ Focused (5 features, all related to standalone usage)
- ✅ Achievable (12-17 hours, 2-3 days)
- ✅ Valuable (enables core use case)
- ✅ Testable (clear acceptance criteria)
- ✅ Shippable (complete, coherent MVP)

**Ruthless Check**:
- ✅ Every feature essential for standalone usage
- ✅ Nothing extra included
- ✅ Clear what's deferred and why
- ✅ Scope won't creep

---

## Success Criteria for v0.4.0

After v0.4.0 ships, users should be able to:

1. **Install tool**: `pipx install git+https://github.com/user/doc-evergreen.git`
2. **Bootstrap project**: `cd my-app && doc-evergreen init`
3. **Generate docs**: `doc-evergreen regen readme`
4. **Just works**: No config, no setup, no confusion

**If all 4 work smoothly → v0.4.0 is successful**

---

## Convergence Quality

**Questions that forced clarity**:
- What's the simplest possible design?
- What can we defer without losing core value?
- What matches user mental models?
- What's the 80/20 of standalone tool?

**Answers led to**:
- Convention over configuration
- Simplicity over flexibility
- Essential 5 features only
- 15 features deferred thoughtfully

---

**Convergence Status**: ✅ **COMPLETE**

**Ready for**: Sprint planning (`/convergent-dev:2-plan-sprints`)
