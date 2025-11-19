# Problem B Convergence Complete

**Date**: 2025-01-18
**Session**: Divergence → Convergence for Problem B (Chunked Generation)

---

## 🎉 Convergence Summary

We've successfully moved from divergent exploration to convergent MVP definition for Problem B.

### What We Accomplished

✅ **DIVERGED**: Explored chunked generation approaches, control points, validation strategies
✅ **CAPTURED**: Organized ideas into clear feature clusters
✅ **CONVERGED**: Defined 5-feature MVP for section-by-section generation
✅ **DEFERRED**: Preserved 13 features for future iterations with clear reconsider conditions

---

## 📄 Documentation Created

### 1. MVP Definition - Problem B
**File**: `MVP_DEFINITION_PROBLEM_B.md`
**Size**: ~45KB (comprehensive specification)

**Contents**:
- The ONE problem (unpredictable single-shot generation)
- The specific user (developers needing control/guardrails)
- 5 must-have features
- Success criteria
- Technical architecture
- 3-week timeline (Sprints 5-7)
- Risk mitigation strategies

### 2. Deferred Features - Problem B
**File**: `DEFERRED_FEATURES_PROBLEM_B.md`
**Size**: ~27KB (preserved ideas)

**Contents**:
- 13 deferred features organized by priority
- Clear "reconsider when" conditions for each
- Relationship to Problem A deferrals
- Decision framework for future evaluation

---

## 🎯 The Problem B MVP (Sprints 5-7)

### Core Problem
"Full-document single-shot generation lacks user control and guardrails, making output unpredictable and difficult to steer toward user's actual needs"

### Solution: Chunked Section-by-Section Generation

**The 5 Must-Have Features:**

1. **Template with Section-Level Prompts**
   - Extend JSON template to include explicit prompt per section
   - Gives users "strong guardrail input" they need
   - Builds on Sprint 1-4 template system

2. **Sequential Section Generation**
   - Generate document section-by-section in DFS order
   - Each section = separate LLM call
   - Smaller, more predictable prompts

3. **Context Flow Between Sections**
   - Later sections receive summaries of earlier sections
   - Maintains coherence across chunks
   - Enables natural cross-references

4. **Section Review Checkpoints (Optional)**
   - Pause after each section for user review
   - Accept / Regenerate / Edit / Quit
   - Ultimate user control

5. **Source Validation & Visibility**
   - Validate sources before generation (fail early)
   - Show which sources used per section
   - Fixes ISSUE-001, addresses ISSUE-003

---

## 📊 Success Criteria

**The MVP succeeds if:**

1. ✅ Template with section-level prompts parses correctly
2. ✅ Each section generates sequentially with appropriate context
3. ✅ Later sections reference earlier sections appropriately
4. ✅ Source validation prevents empty context errors (ISSUE-001 fixed)
5. ✅ User sees which sources are used per section (ISSUE-003 addressed)
6. ✅ Interactive mode lets user review/steer at checkpoints
7. ✅ Output is more coherent and steerable than single-shot generation
8. ✅ User feels more control over output quality

---

## 🗓️ Timeline

**Total: 2-3 weeks**

### Week 1: Sprint 5 (Core Infrastructure)
- Template format extension (section prompts)
- Sequential DFS generation
- Source validation (ISSUE-001 fix)
- Basic context flow

### Week 2: Sprint 6 (Polish & Testing)
- Section review checkpoints (interactive mode)
- Enhanced source visibility (ISSUE-003 complete)
- Dogfooding (doc_evergreen's own README)
- Documentation

### Week 3: Sprint 7 (Buffer)
- Edge case handling
- Error messages
- User testing
- Performance optimization

---

## 🚫 What's Explicitly OUT of Scope (v2)

**Deferred to Phase 2:**
- Post-order validation and updates (bidirectional flow)
- Sibling consistency checks (overlap/gap detection)
- Tree backtracking (generate → validate → refine loop)

**Deferred to Phase 3:**
- Dynamic tree growth (LLM proposes sections)
- State management / resume capability
- Advanced forward reference handling

**Deferred (Issue-Specific):**
- ISSUE-002 (error pattern detection) - section review handles this

**Total**: 13 features thoughtfully deferred with clear reconsider conditions

---

## 🔗 Relationship to Problem A

### Problem A (COMPLETED - Sprints 1-4)
**"Documentation needs reliable regeneration"**
- ✅ Template-based structure
- ✅ Source resolution (glob patterns)
- ✅ Single-shot generation
- ✅ Review & accept workflow

### Problem B (THIS MVP - Sprints 5-7)
**"Single-shot needs control and predictability"**
- Section-by-section generation
- Explicit prompts per section
- Context flow between sections
- Review checkpoints for steering
- Source validation and visibility

**Builds On**: Problem B extends Problem A's foundation (template system, source resolution) with chunked generation and user control.

---

## 📝 Issue Tracker Updates Needed

### ISSUE-001: Empty Context Handling (High Priority - Bug)
**Status**: Assigned to Sprint 5
**Fix**: Source validation (Feature 5)
- Validate sources before generation
- Fail early with clear error
- Show which sections lack sources

### ISSUE-003: Source Visibility (Medium Priority - Enhancement)
**Status**: Assigned to Sprint 5
**Fix**: Source visibility (Feature 5)
- Show sources used per section
- Display file counts and paths
- Token usage transparency

### ISSUE-002: Error Message Detection (Medium Priority - Enhancement)
**Status**: Deferred
**Reason**: Section review checkpoints (Feature 4) handle this manually
**Reconsider When**: Users accept error content frequently (>5% of sections)

---

## 🎨 Philosophy Alignment

This MVP embodies the project's core principles:

**Ruthless Simplicity**:
- 5 features only (vs 18 explored = 72% deferred)
- Forward-only generation (no backtracking)
- Simple CLI (no web UI)

**Start Minimal, Grow as Needed**:
- Test section-by-section approach first
- Learn what control points matter
- Don't build features we might not need

**Present-Moment Focus**:
- Solves today's pain (unpredictable generation)
- Uses today's tools (LLM + JSON)
- No future-proofing

**Trust in Emergence**:
- Section patterns will emerge through use
- Quality standards discovered through testing
- Right features prove themselves through need

**User Control & Confidence**:
- Explicit prompts = strong input guardrails
- Review checkpoints = strong output control
- Source validation = fail early confidence
- Visibility = trust through transparency

---

## ✅ Next Steps

### 1. Review & Approve MVP Definition
**Action**: User confirms MVP scope is correct
**Output**: Green light to proceed

### 2. Break Into Executable Sprints
**Action**: Create detailed sprint plans for Sprints 5-7
**Tool**: `/plan-sprints` or manual sprint planning
**Output**: Sprint backlog with tasks

### 3. Update Issue Tracker
**Action**: Assign issues to sprints
- ISSUE-001 → Sprint 5
- ISSUE-003 → Sprint 5
- ISSUE-002 → Defer (document reason)

### 4. Begin Sprint 5 (Week 1)
**Focus**: Core infrastructure
**Goal**: Section prompts + DFS generation + source validation + context flow

---

## 📈 Metrics for Success

### Quantitative
- Section generation: <30s each
- Context overhead: <5s per section
- Source validation: <10s total
- Total time: <10min for 10-section doc

### Qualitative
- User reports more control
- Fewer full-doc regenerations needed
- Higher section quality satisfaction
- Easier to steer output

### Bug Fixes
- ✅ ISSUE-001 resolved (empty context)
- ✅ ISSUE-003 resolved (source visibility)

---

## 🎯 Test Case

**Template**: doc_evergreen's own README with 3-5 sections
**Expected Behavior**:
1. Validate all sources upfront (show counts)
2. Generate Overview with specified sources
3. Generate Features with Overview context + sources
4. Generate Getting Started with all previous context
5. Pause for review after each (if --interactive)
6. Produce coherent README with natural flow

**If sources missing**: Fail with clear error before generation

---

## 💡 Key Insights from Convergence

1. **Control is key**: Users need both input guardrails (prompts) and output control (review checkpoints)

2. **Visibility builds trust**: Showing what sources are used and what's happening reduces anxiety

3. **Fail early**: Source validation before generation prevents frustrating errors

4. **Context flow is critical**: Sections must reference each other naturally despite chunked generation

5. **Simplicity first**: Forward-only generation is sufficient for MVP; backtracking can wait

6. **13 deferrals with clear conditions**: Nothing is lost, everything preserved for future

---

## 📚 Documentation Structure

```
ai_working/doc_evergreen/
├── MVP_DEFINITION.md              # Problem A (Sprints 1-4) - COMPLETED
├── DEFERRED_FEATURES.md            # Problem A deferrals
├── MVP_DEFINITION_PROBLEM_B.md     # Problem B (Sprints 5-7) - THIS MVP
├── DEFERRED_FEATURES_PROBLEM_B.md  # Problem B deferrals
├── CONVERGENCE_COMPLETE.md         # This summary (you are here)
├── issues/
│   ├── ISSUE-001-empty-context.md
│   ├── ISSUE-002-misleading-success.md
│   └── ISSUE-003-no-source-feedback.md
└── sprints/
    ├── sprint-1-results.md         # Completed
    ├── sprint-2-results.md         # Completed
    ├── sprint-3-results.md         # Completed
    └── sprint-4-results.md         # Completed
```

**Next**: Sprint 5-7 planning and execution

---

## 🚀 Ready to Build!

**Problem B MVP is fully defined.**

✅ Core problem identified
✅ User needs understood
✅ 5 features scoped
✅ Success criteria clear
✅ Timeline established
✅ Risks mitigated
✅ Deferrals preserved
✅ Philosophy aligned

**All that remains**: Break into sprints and start building.

---

**Nothing is lost. Everything is preserved. The best features will prove themselves through use.**
