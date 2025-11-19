# Doc-Evergreen Sprint Plan: v0.2.0

**Version**: 0.2.0 (Chunked Generation)
**Status**: Ready for Implementation
**Timeline**: 2-3 weeks (Sprints 5-7)
**Builds On**: v0.1.0 (Sprints 1-4 - Template-based Single-shot Generation)

---

## Version Number Rationale

**Version 0.2.0** - Minor version bump (backward compatible feature addition)

**Why 0.2.0:**
- Adds significant new features (section-by-section generation)
- Backward compatible with v0.1.0 templates (can still use single-shot mode)
- No breaking changes to existing functionality
- Extends template format (adds optional `prompt` field per section)
- New CLI flags (`--interactive`, `--auto`) but existing behavior preserved

**SemVer Breakdown:**
- **Major (0)**: Still pre-1.0, API not yet stable
- **Minor (2)**: New features - chunked generation, section prompts, context flow
- **Patch (0)**: No patches yet, fresh minor release

---

## MVP Scope Summary

"Section-by-section document generation with explicit prompts and user control"

**The Problem**: Single-shot full-document generation lacks control and predictability
**The Solution**: Generate documents section-by-section with:
- Explicit prompts per section (strong guardrails)
- Context flow between sections (coherence)
- Source validation before generation (fail early)
- Optional review checkpoints (steering)
- Clear source visibility (debugging)

**First Test**: Regenerate doc_evergreen's own README using chunked generation

---

## Sprint Overview

| Sprint | Duration | Name | Value Delivered |
|--------|----------|------|-----------------|
| 5 | 5 days | Chunked Core | Section-by-section generation working end-to-end |
| 6 | 4 days | Review & Polish | Interactive checkpoints, source visibility complete |
| 7 | 3 days | Refinement (Buffer) | Edge cases, error messages, real-world testing |

**Total: 12 days (2-3 weeks)**

---

## Value Progression

### Sprint 5: Proves Chunked Generation Works
**After this sprint, you can**:
- Generate documents section-by-section (not single-shot)
- Define explicit prompts for each section in templates
- See context flow from earlier to later sections
- Tool fails early if sources are missing (ISSUE-001 fixed)

**What you learn**:
- Does section-by-section improve output quality?
- Are explicit prompts sufficient guardrails?
- Does context flow create coherence?
- Is source validation effective?

### Sprint 6: Adds User Control
**After this sprint, you can**:
- Review each section before continuing (interactive mode)
- Regenerate sections with feedback
- See exactly which sources are used per section (ISSUE-003 addressed)
- Choose between interactive and auto modes

**What you learn**:
- Where do users want to intervene?
- What level of visibility is helpful?
- How often do sections need regeneration?
- Is interactive mode too tedious or just right?

### Sprint 7: Makes It Robust (Buffer)
**After this sprint, you can**:
- Handle edge cases gracefully (empty sections, deep nesting)
- Understand clear error messages
- Test with real projects (not just doc_evergreen)
- Trust the tool for production use

**What you learn**:
- What edge cases actually occur?
- Where do users get stuck?
- What error messages are needed?
- Is performance acceptable?

---

## Why This Sequencing?

### Value-First Learning

**NOT infrastructure-first**:
```
❌ Sprint 5: Build context manager
❌ Sprint 6: Build validator
❌ Sprint 7: Wire everything together (value in Sprint 7!)
```

**YES - working features first**:
```
✅ Sprint 5: Section generation working end-to-end (value immediately!)
✅ Sprint 6: Add control & visibility (builds on working base)
✅ Sprint 7: Polish & edge cases (refinement, not foundation)
```

### Learning Checkpoints

Each sprint teaches something critical for the next:

**Sprint 5 → Sprint 6**:
- Seeing generated sections reveals where users want control
- Context flow quality determines review granularity needed
- Source resolution experience shows visibility needs

**Sprint 6 → Sprint 7**:
- Interactive workflow reveals edge cases to handle
- User testing shows what error messages are missing
- Real usage patterns inform optimization priorities

### Risk Mitigation

**Biggest risk**: Section-by-section doesn't improve quality over single-shot
**Mitigation**: Test in Sprint 5 (Days 1-5), validate approach early

**Second risk**: Interactive checkpoints are too tedious
**Mitigation**: Test in Sprint 6 (Days 6-9), make auto mode default

**Smaller risks**: Edge cases, performance, error messages
**Addressed**: Sprint 7 (Days 10-12) after core value proven

---

## Builds On v0.1.0 Foundation

### Reusing from Sprints 1-4:
- Template parsing infrastructure (`template.py`)
- Source resolution system (`source_resolver.py`)
- Hierarchical source inheritance
- JSON template format
- Review & accept workflow (`review.py`)
- CLI framework (`doc-update.py`)

### Extending in v0.2.0:
- Template format: Add `prompt` field per section
- Generator: New `ChunkedGenerator` alongside existing `Generator`
- CLI: Add `--interactive` and `--auto` flags
- Validation: New upfront source validation phase
- Context: New context flow between sections

**Backward Compatibility**: Single-shot mode still works (templates without section prompts)

---

## Key Architecture Changes

### Before (v0.1.0 - Single-shot):
```
Template → Gather All Sources → Single LLM Call → Complete Document → Review
```

### After (v0.2.0 - Chunked):
```
Template with Section Prompts
         ↓
   Validate All Sources (fail early)
         ↓
Section 1: Generate [show sources]
         ↓
  [Optional Review Checkpoint]
         ↓
Section 2: Generate + Section 1 context [show sources]
         ↓
  [Optional Review Checkpoint]
         ↓
Section N: Generate + previous context [show sources]
         ↓
   Complete Document
         ↓
  Final Review & Accept
```

---

## Success Criteria

### Quantitative
- ✅ Section generation time: <30s per section
- ✅ Source validation time: <10s total
- ✅ Total generation time: <10min for 10-section doc
- ✅ Test coverage: >80% for new code

### Qualitative
- ✅ Users feel more control over output
- ✅ Sections are more coherent than single-shot
- ✅ Fewer full-document regenerations needed
- ✅ Clear visibility into what's happening

### Bug Fixes
- ✅ ISSUE-001 resolved (no empty context errors)
- ✅ ISSUE-003 addressed (source visibility clear)
- ⏸️ ISSUE-002 deferred (section review handles this)

---

## Deferred to Future Versions

### Not in v0.2.0 MVP

1. **Post-order validation and updates**
   - Why: Forward-only is simpler, tests core assumption first
   - Reconsider: v0.3.0 if inconsistencies are common

2. **Tree backtracking** (iterative refinement)
   - Why: Single-pass generation is faster, simpler state
   - Reconsider: v0.3.0 if one-shot quality insufficient

3. **Dynamic section discovery**
   - Why: Static templates test core value first
   - Reconsider: v0.4.0 if users manually add sections often

4. **State persistence / resume capability**
   - Why: Full generation fast enough (<10min)
   - Reconsider: v0.3.0 if generation takes >10min

5. **Advanced forward references**
   - Why: Adds complexity, unclear if needed
   - Reconsider: v0.4.0 if forward references prove common

6. **Error pattern detection** (ISSUE-002)
   - Why: Section review catches this manually
   - Reconsider: v0.3.0 if users accept error content frequently

---

## Timeline at a Glance

```
Week 1:
├── Mon-Fri: Sprint 5 (Chunked Core - 5 days)

Week 2:
├── Mon-Thu: Sprint 6 (Review & Polish - 4 days)
├── Fri-Sun: Sprint 7 (Refinement - 3 days)
```

**Flexibility**:
- Sprint 7 is optional buffer (can ship after Sprint 6)
- Each sprint is self-contained
- Can extend based on learnings

---

## Sprint Document Links

Detailed plans for each sprint:

1. [Sprint 5: Chunked Core](./SPRINT_05_CHUNKED_CORE.md) - 5 days
2. [Sprint 6: Review & Polish](./SPRINT_06_REVIEW_POLISH.md) - 4 days
3. [Sprint 7: Refinement](./SPRINT_07_REFINEMENT.md) - 3 days (buffer)

---

## Feature Summary

### 5 Must-Have Features

1. **Template with Section-Level Prompts**
   - Each section has explicit `prompt` field
   - Strong guardrails on what LLM should generate
   - Clear user expectations per section

2. **Sequential Section Generation**
   - DFS traversal (depth-first)
   - Separate LLM call per section
   - Smaller, focused prompts

3. **Context Flow Between Sections**
   - Later sections receive summaries of earlier sections
   - Maintains coherence across chunks
   - Natural cross-references

4. **Source Validation & Visibility**
   - Validate all sources before generation (fail early)
   - Show which sources used per section
   - Fixes ISSUE-001, addresses ISSUE-003

5. **Section Review Checkpoints** (Optional)
   - Interactive mode: pause after each section
   - Accept / Regenerate / Edit / Quit
   - Auto mode: no pauses (default)

---

## Philosophy Alignment

This sprint plan embodies the project's core principles:

**Ruthless Simplicity:**
- 5 features only (focused scope)
- Forward-only generation (no backtracking complexity)
- Simple CLI flags (not elaborate options)

**Value-First Sequencing:**
- Sprint 5 delivers working chunked generation
- Sprint 6 adds control (builds on working base)
- Sprint 7 is polish only (not foundation)

**Test-Driven Development:**
- TDD cycle for all features (red-green-refactor)
- Tests written before code
- >80% test coverage target

**Vertical Slices:**
- Each sprint delivers end-to-end value
- No horizontal layers (not "build all validators, then generators")
- Working features over perfect components

**Learning Through Shipping:**
- Sprint 5 validates approach
- Sprint 6 refines based on Sprint 5 learnings
- Sprint 7 handles real-world edge cases discovered

---

## Dependencies

### External Dependencies:
- PydanticAI (LLM calls)
- Claude/GPT API (text generation)
- Python 3.11+ (pathlib, asyncio)

### Internal Dependencies:
- v0.1.0 codebase (Sprints 1-4)
- Template format infrastructure
- Source resolution system
- CLI framework

### No New Dependencies:
- No additional libraries needed
- May use LLM for section summaries (self-referential)

---

## Risk Assessment

### Known Risks & Mitigations

**Risk: Context overflow** (summaries too large)
- Mitigation: Limit summaries to 3-5 sentences
- Mitigation: Monitor token usage per section

**Risk: Disjointed sections** (lack of coherence)
- Mitigation: Pass section summaries as context
- Mitigation: Test with real documents early

**Risk: Interactive mode tedious** (too many pauses)
- Mitigation: Make auto mode the default
- Mitigation: Keep review UI simple (one-key actions)

**Risk: Validation overhead** (slow source checking)
- Mitigation: Cache resolved sources
- Mitigation: Show progress during validation

---

## Metrics for Success

### Sprint 5 (Core):
- ✅ Sections generated in DFS order
- ✅ Context flows correctly between sections
- ✅ Tool fails early on missing sources
- ✅ Generated doc is coherent end-to-end

### Sprint 6 (Control):
- ✅ Interactive checkpoints work (accept/regenerate/edit/quit)
- ✅ Source visibility clear per section
- ✅ Both auto and interactive modes functional
- ✅ User can steer output effectively

### Sprint 7 (Polish):
- ✅ Edge cases handled gracefully
- ✅ Error messages are clear and actionable
- ✅ Performance acceptable (<30s per section)
- ✅ User testing validates workflow

---

## Next Actions

1. **Review sprint plan** - Does this sequencing make sense?
2. **Read Sprint 5 details** - See SPRINT_05_CHUNKED_CORE.md
3. **Begin Sprint 5** - Start with TDD (test-first)
4. **Ship incrementally** - Each sprint delivers value

---

## Remember

- Sprint 5 delivers working chunked generation
- Each sprint makes the tool MORE controllable
- Infrastructure emerges from needs, not speculation
- Test with real docs, real workflows
- Pivot fast if assumptions prove wrong

**The goal**: User control and predictability, not just features.
