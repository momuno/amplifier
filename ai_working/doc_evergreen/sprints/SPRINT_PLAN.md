# Doc-Evergreen Sprint Plan

## MVP Scope Summary
"Regenerate any documentation file with confidence using templates and explicit context"

**Target**: 2-week timeline to working MVP
**First Test**: Regenerate amplifier's top-level README.md

---

## Sprint Overview

| Sprint | Duration | Name | Value Delivered |
|--------|----------|------|-----------------|
| 1 | 3 days | Proof of Concept | Working README generation (hardcoded) |
| 2 | 2 days | Review Workflow | Safe file replacement with preview/diff |
| 3 | 3 days | CLI + Templates | Reusable tool for any doc |
| 4 | 2 days | Context Control | User-specified source files |

**Total: 10 days (2 weeks)**

---

## Value Progression

### Sprint 1: Proves the Concept
**After this sprint, you can**:
- Generate a complete README from template + sources
- See if LLM output is "good enough"
- Validate core hypothesis immediately

**What you learn**:
- Does this approach even work?
- What quality level can we achieve?
- What prompt engineering is needed?

### Sprint 2: Makes It Safe
**After this sprint, you can**:
- Preview generated docs before committing
- See exactly what changed (diff)
- Accept or reject with confidence

**What you learn**:
- What users want to review
- How much change is acceptable
- When to iterate vs accept

### Sprint 3: Makes It Reusable
**After this sprint, you can**:
- Run from command line easily
- Use custom templates for different doc types
- Generate any doc, not just README

**What you learn**:
- What template format works best
- How to organize templates
- What CLI UX feels natural

### Sprint 4: Gives Control
**After this sprint, you can**:
- Specify which sources to include
- Adjust context for each doc
- Fine-tune generation input

**What you learn**:
- How much context is needed
- What sources matter most
- How to balance detail vs noise

---

## Why This Sequencing?

### Value-First, Not Infrastructure-First

**NOT this (infrastructure-first)**:
```
❌ Sprint 1: Build CLI framework
❌ Sprint 2: Create template system
❌ Sprint 3: Implement context gathering
❌ Sprint 4: Finally generate a doc (value in Sprint 4!)
```

**YES this (value-first)**:
```
✅ Sprint 1: Generate doc end-to-end (value immediately!)
✅ Sprint 2: Make it safe (confidence to use)
✅ Sprint 3: Make it reusable (broader value)
✅ Sprint 4: Add control (polish)
```

### Learning Checkpoints

Each sprint teaches something critical for the next:

**Sprint 1 → Sprint 2**:
- Seeing generated output reveals what needs review
- Quality level determines review granularity

**Sprint 2 → Sprint 3**:
- Review workflow shows template needs
- User interaction informs CLI design

**Sprint 3 → Sprint 4**:
- Multiple doc types reveal context needs
- Template variety shows source selection patterns

### Risk Mitigation

**Biggest risk**: LLM can't generate acceptable docs
**Mitigation**: Test in Sprint 1 (Day 1-3), pivot early if needed

**Second risk**: Review workflow too cumbersome
**Mitigation**: Test in Sprint 2 (Day 4-5), simplify if needed

**Smaller risks**: CLI UX, template format, context selection
**Addressed**: Later sprints (Days 6-10) after core value proven

---

## Deferred to v2

### Features NOT in MVP
1. **Multi-file batch regeneration** - Can run tool multiple times manually
2. **Template library/marketplace** - Start with 1-2 default templates
3. **Automated context detection** - User specifies sources explicitly
4. **Incremental updates** - Full regeneration only for MVP
5. **Version control integration** - Manual git workflow initially
6. **LLM provider choice** - Single provider (Claude) for MVP

### Why Defer?
- **Not needed to prove value**: Single doc regeneration is enough
- **Optimization without data**: Don't know what's needed until users try MVP
- **Complexity vs benefit**: Each adds time but unclear value
- **Learn first, build later**: Real usage reveals what matters

---

## Timeline at a Glance

```
Week 1:
├── Mon-Wed: Sprint 1 (Proof of Concept)
├── Thu-Fri: Sprint 2 (Review Workflow)

Week 2:
├── Mon-Wed: Sprint 3 (CLI + Templates)
├── Thu-Fri: Sprint 4 (Context Control)
```

**Flexibility built in**:
- Each sprint is self-contained
- Can extend/shrink based on learnings
- Can stop after Sprint 2 and still have value

---

## Success Metrics

### Quantitative
- ✅ README regeneration takes <5 minutes
- ✅ 80%+ of output acceptable without major edits
- ✅ Tool can regenerate 5+ docs without code changes

### Qualitative
- ✅ User confident to overwrite real files
- ✅ User prefers this to manual doc updates
- ✅ User excited to try on more docs

### Ultimate Test
**Would you use this for your next doc update?**
- If YES → MVP success
- If NO → Identify blockers and iterate

---

## Next Steps

1. **Review sprint plan** - Does this sequencing make sense?
2. **Read Sprint 1 details** - See SPRINT_01_PROOF_OF_CONCEPT.md
3. **Start building** - Day 1 begins with end-to-end value
4. **Ship fast, learn fast** - Iterate based on real usage

---

## Sprint Document Links

Detailed plans for each sprint:

1. [Sprint 1: Proof of Concept](./SPRINT_01_PROOF_OF_CONCEPT.md) - 3 days
2. [Sprint 2: Review Workflow](./SPRINT_02_REVIEW_WORKFLOW.md) - 2 days
3. [Sprint 3: CLI + Templates](./SPRINT_03_CLI_TEMPLATES.md) - 3 days
4. [Sprint 4: Context Control](./SPRINT_04_CONTEXT_CONTROL.md) - 2 days

---

## Remember

- Sprint 1 delivers value on Day 3
- Each sprint makes the tool MORE useful
- Infrastructure emerges from needs, not speculation
- Test with real docs, real users, real workflows
- Pivot fast if assumptions prove wrong

**The goal**: Shipping confidence, not shipping features.
