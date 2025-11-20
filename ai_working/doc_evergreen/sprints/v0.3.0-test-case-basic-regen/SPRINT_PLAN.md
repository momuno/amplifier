# Doc-Evergreen Sprint Plan: v0.3.0 - Test Case + Basic Regeneration

## Version Summary
**Version**: v0.3.0
**Feature**: Template-Based Regeneration with Test Case
**Problem**: Users can't easily update documentation as code changes. Need reliable regeneration workflow with change preview.

**Target**: 10-day timeline to production-ready regeneration
**Primary Test Case**: `templates/amplifier_readme.json` - Regenerate `amplifier/README.md`
- Real-world validation with existing documentation
- 9 sections covering introduction, architecture, installation, usage, testing, storage, future, and module docs
- Uses actual project structure as test data

---

## Sprint Overview

| Sprint | Duration | Name | Value Delivered |
|--------|----------|------|-----------------|
| 8 | 4 days | Template Parser | Working regeneration with diff preview |
| 9 | 3 days | Source Context | Progress feedback and source clarity |
| 10 | 3 days | Change Detection | Real-world validation and documentation |

**Total: 10 days (2 weeks)**

---

## Value Progression

### Sprint 8: Template-Based Regeneration Core
**After this sprint, you can**:
- Regenerate docs from templates with `regen-doc` command
- Preview changes before applying (diff view)
- Use example templates immediately

**What you learn**:
- How often users need to regenerate
- What diff format is most helpful
- Where users get confused

### Sprint 9: Progressive Enhancement & Source Clarity
**After this sprint, you can**:
- See real-time progress during generation
- Understand how sources work clearly
- Iterate on regeneration smoothly

**What you learn**:
- How often users iterate
- What errors users hit most
- Whether progress is too verbose/sparse

### Sprint 10: Real-World Validation
**After this sprint, you can**:
- Use templates on production projects confidently
- Follow comprehensive guides
- Apply best practices

**What you learn**:
- What real-world patterns emerge
- Where users still get stuck
- What documentation gaps remain

---

## Integrated Issues

This sprint plan resolves:

- **ISSUE-004** (CLI help text) → Sprint 8: New clear help text for `regen-doc`
- **ISSUE-005** (no example templates) → Sprint 8: 3 examples + Sprint 10: real-world templates
- **ISSUE-006** (sources template vs CLI) → Sprint 9: Documentation + error messages
- **ISSUE-007** (no progress feedback) → Sprint 9: Progress callback system

---

## What Changes vs. What Stays

### Stays the Same (v0.2.0 → v0.3.0)
- Template JSON structure (Document → Sections with heading/prompt/sources)
- Schema classes (Template, Document, Section, ValidationResult)
- Source file gathering mechanism
- Recursive section nesting support
- Validation system for templates

### Changes (New in v0.3.0)
- **New command**: `regen-doc` replaces `doc-update`
- **New workflow**: Template-based with diff preview and approval
- **New features**: Change detection, diff generation, iterative refinement
- **Enhanced UX**: Progress feedback, better error messages, example templates
- **Resolved issues**: Issues #004, #005, #006, #007 integrated

### Deferred to Future
- Single-shot mode implementation (Issue #009) - chunked mode sufficient for MVP
- Advanced diff algorithms - start with simple unified diff
- CI/CD integration - manual workflow first

---

## Why This Sequencing?

### Value-First, Not Infrastructure-First

**NOT this (infrastructure-first)**:
```
❌ Sprint 8: Build advanced diff library
❌ Sprint 9: Create template validation framework
❌ Sprint 10: Finally regenerate a doc (value in Sprint 10!)
```

**YES this (value-first)**:
```
✅ Sprint 8: Regenerate doc with diff (value immediately!)
✅ Sprint 9: Make it visible and understandable (confidence)
✅ Sprint 10: Validate with real usage (production-ready)
```

### Learning Checkpoints

Each sprint teaches something critical for the next:

**Sprint 8 → Sprint 9**:
- Seeing regeneration reveals what users need to see (progress)
- Basic workflow shows where clarity is needed (sources, errors)

**Sprint 9 → Sprint 10**:
- Progress feedback shows if workflow feels right
- Clear errors reveal remaining documentation needs

**Sprint 10 → v0.4.0**:
- Real-world usage reveals next priorities
- Production patterns inform future features

---

## Technical Decisions

### Use Existing Schema
- No custom placeholder syntax ({{LLM:}}, {{INCLUDE:}})
- JSON structure proven and working
- No schema changes needed

### Simple Diff First
- Python `difflib.unified_diff` sufficient
- No external library dependencies
- Can enhance later without breaking changes

### Replace doc-update
- No backward compatibility needed (per user)
- Clean slate for better UX
- Clearer command naming

### Chunked Mode Only
- Single-shot mode deferred
- ChunkedGenerator reliable and tested
- Simplifies implementation and testing

---

## Deferred to v0.4.0

### Features NOT in v0.3.0
1. **Single-shot mode** (Issue #009) - Chunked mode sufficient for MVP
2. **Advanced diff algorithms** - Simple unified diff works
3. **Section-level regeneration** - Full doc regen only (simpler)
4. **Template validation beyond existing** - Current validation adequate
5. **CI/CD integration** - Manual workflow first

### Why Defer?
- **Not needed to prove value**: Basic regeneration is enough
- **Optimization without data**: Don't know what's needed until users try MVP
- **Complexity vs benefit**: Each adds time but unclear value
- **Learn first, build later**: Real usage reveals what matters

---

## Timeline at a Glance

```
Week 1:
├── Day 1-4: Sprint 8 (Template Parser)
├── Day 5-7: Sprint 9 (Source Context)

Week 2:
├── Day 8-10: Sprint 10 (Change Detection)
```

**Flexibility built in**:
- Each sprint is self-contained
- Can extend/shrink based on learnings
- Can stop after Sprint 9 and still have value

---

## Success Criteria

### Quantitative
- ✅ `regen-doc` command works reliably
- ✅ Change detection accuracy: 100%
- ✅ **PRIMARY: `templates/amplifier_readme.json` regenerates amplifier/README.md successfully**
- ✅ 2+ additional example templates work
- ✅ Test coverage >80%

### Qualitative
- ✅ User can run test case without reading docs
- ✅ Diff output is clear and understandable for real-world changes
- ✅ Users don't ask "is it working?"
- ✅ New user can succeed with guide alone
- ✅ Team confident shipping v0.3.0

### Ultimate Test
**Can we regenerate amplifier/README.md and get quality output?**
- If YES → MVP success, validates real-world usage
- If NO → Identify blockers and iterate

---

## Next Steps

1. **Review sprint plan** - Does this sequencing make sense?
2. **Read Sprint 8 details** - See SPRINT_08_TEMPLATE_PARSER.md
3. **Start building** - Day 1 begins with end-to-end value
4. **Ship fast, learn fast** - Iterate based on real usage

---

## Sprint Document Links

Detailed plans for each sprint:

1. [Sprint 8: Template Parser](./SPRINT_08_TEMPLATE_PARSER.md) - 4 days
2. [Sprint 9: Source Context](./SPRINT_09_SOURCE_CONTEXT.md) - 3 days
3. [Sprint 10: Change Detection](./SPRINT_10_CHANGE_DETECTION.md) - 3 days

---

## Remember

- Sprint 8 delivers value on Day 4
- Each sprint makes the tool MORE useful
- Infrastructure emerges from needs, not speculation
- Test with real docs, real usage, real workflows
- Pivot fast if assumptions prove wrong

**The goal**: Shipping confidence, not shipping features.
