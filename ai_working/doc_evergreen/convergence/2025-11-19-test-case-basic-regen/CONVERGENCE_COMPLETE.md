# Convergence Complete: Test Case - Basic Regeneration

**Date**: 2025-11-19
**Duration**: ~2 hours
**Project**: doc_evergreen
**Convergence Type**: Feature scope definition

---

## 🎉 Convergence Summary

We've successfully moved from divergent exploration to convergent feature scope for the test case - basic regeneration feature.

---

## ✅ What Was Captured

### The ONE Problem
**Documentation drifts from reality as code evolves.**

Manual synchronization is time-consuming, error-prone, and demotivating. Developers must hunt down affected docs, understand changes, and rewrite sections—work that feels like duplication and competes with actual development.

### The Specific User
**Solo developers or small teams maintaining 3-5+ active projects** where code evolves frequently and documentation must stay accurate, but time is scarce.

### Feature Scope (5 Must-Have Features)

1. **Template-Based Generation**: `.md.template` files lock structure with `{{LLM: prompt}}` placeholders
2. **Source Context Gathering**: Automatically read source files into LLM context via `{{INCLUDE: path}}`
3. **Manual Regeneration Command**: `amplifier regen-doc <path>` to regenerate on demand
4. **Structure Preservation**: Non-LLM sections (static markdown) stay untouched
5. **Change Detection**: Show diff, let user decide if changes are meaningful enough to keep

### Success Criteria

- [ ] Can generate `amplifier/README.md` from template + sources
- [ ] Can regenerate manually when sources change
- [ ] Structure stays consistent across regenerations
- [ ] See diff, decide if update is meaningful
- [ ] Friction points become visible through use

### Timeline
**Ship by**: 2025-11-26 (1 week)

**Aggressive but achievable** - Focused scope, test case is real but bounded, manual trigger only.

---

## 🔄 What Was Deferred

**Total Deferred**: 21 features across 4 categories

### Phase 2: Automation & Triggers (4 features)
- Automatic change detection
- Git hook integration
- Watch mode
- Scheduled regeneration

**Reconsider when**: Manual flow used 10+ times successfully

### Phase 3: Multi-Document Operations (3 features)
- Batch regeneration
- Multi-document orchestration
- Workspace-wide regeneration

**Reconsider when**: Single-doc regeneration mature, users maintain 5+ docs

### Phase 4: Advanced Features (7 features)
- Partial/selective updates
- Human edit preservation
- Configuration files
- Review/approval workflows
- Smart structure discovery
- LLM-generated templates
- Interactive template wizard

**Reconsider when**: Core functionality mature, advanced needs emerge

### Optimizations (5 features)
- Prompt versioning system
- Relevancy scoring (1-10 scale)
- Caching/efficiency optimizations
- Incremental context updates
- Progressive/streaming output

**Reconsider when**: Performance/UX becomes bottleneck

### Parking Lot (3 features)
- Template marketplace
- Plugin/extension system
- Interactive template creation wizard

**Reconsider when**: Specific use cases emerge through usage

---

## 📊 Convergence Metrics

**Exploration Phase**:
- Ideas discussed: 26+ features/capabilities
- Use cases explored: 6+ scenarios
- Time spent: ~1 hour

**Convergence Phase**:
- Features in scope: 5 (must-have only)
- Features deferred: 21 (with clear conditions)
- Convergence ratio: 19% (5/26 selected immediately)

**Key Insight**: 81% of ideas thoughtfully deferred, not rejected. Each has clear "reconsider when" conditions.

---

## 🎯 What This Convergence Achieved

### 1. Clarity on Core Problem
- From: "Documentation is hard to maintain"
- To: "Documentation drifts from reality as code evolves"
- **Specificity matters**: Clear problem statement guides solution design

### 2. Focused Feature Scope
- From: 26+ possible features
- To: 5 must-have features for test case
- **Ruthless simplicity**: Only features essential for core value

### 3. Preserved Exploration Value
- All deferred features captured with rationale
- Clear "reconsider when" conditions for each
- Nothing lost, everything organized

### 4. Test Case Validation
- Real target: `amplifier/README.md`
- Real sources: `amplifier/core.py`, `amplifier/cli.py`, etc.
- Representative complexity (not toy example)

### 5. Learning-Focused Timeline
- 1 week sprint validates approach
- Friction points become visible
- Real usage informs Phase 2

---

## 📄 Documentation Created

### Convergence Session Files

**Feature Scope**:
```
ai_working/doc_evergreen/convergence/2025-11-19-test-case-basic-regen/FEATURE_SCOPE.md
```
- The ONE problem
- Specific user
- 5 must-have features
- Success criteria
- Test case definition

**Deferred Features**:
```
ai_working/doc_evergreen/convergence/2025-11-19-test-case-basic-regen/DEFERRED_FEATURES.md
```
- 21 deferred features organized by category
- Each with "Reconsider when" conditions
- Clear rationale for deferment

**Convergence Complete** (this file):
```
ai_working/doc_evergreen/convergence/2025-11-19-test-case-basic-regen/CONVERGENCE_COMPLETE.md
```
- Summary of convergence process
- What was captured vs. deferred
- Next steps

### Master Backlog

**Updated**:
```
ai_working/doc_evergreen/convergence/MASTER_BACKLOG.md
```
- Added Test Case convergence features to backlog
- Updated statistics (now 57 total backlog items)
- Added new prioritization section

---

## 🚀 Next Steps

### Immediate: Sprint Planning

**Run**: `/plan-sprints` to create executable sprint plan

**Sprint-planner will**:
1. Determine version number based on scope (likely v0.3.0 - new feature)
2. Break 5 features into specific tasks
3. Estimate effort for each task
4. Create sprint plan with deliverables
5. Define acceptance criteria per task

### After Sprint Planning: Implementation

1. Create `amplifier/README.md.template` based on current structure
2. Implement template parser (handle `{{LLM:}}` and `{{INCLUDE:}}`)
3. Implement source context gathering (read files from includes)
4. Implement regeneration command (`amplifier regen-doc`)
5. Implement change detection and diff display
6. Test with real `amplifier/README.md`

### After Implementation: Learning

**Questions to answer through usage**:
- Which deferred features' "reconsider when" conditions are met?
- What friction points emerged?
- What workflow patterns emerged?
- What should come next based on evidence?

---

## 🧠 Key Learnings from This Convergence

### 1. Test Case Strategy Works
Starting with single real document (not theoretical) provides concrete target and validation.

### 2. Manual Trigger Proves Value First
Automation can wait. Manual command validates core flow before adding complexity.

### 3. Structure Preservation is Non-Negotiable
Without locked templates, regeneration creates drift. Templates are the foundation.

### 4. Change Detection Enables Trust
Users need to see what changed and why. Blind overwrites break trust.

### 5. Clear Deferment Prevents Scope Creep
Every idea captured with rationale prevents "but what about...?" during implementation.

---

## 🎓 Philosophy Alignment

This convergence embodies the project's core principles:

**Ruthless Simplicity**:
- 5 features in scope (essential only)
- 21 features deferred (thoughtfully, not rejected)
- Test case over theoretical completeness

**Trust in Emergence**:
- Manual flow teaches what automation should do
- Real usage reveals what matters next
- Features prove necessity through evidence

**Present-Moment Focus**:
- Solve current problem (make regeneration viable)
- Let needs drive next iteration
- Don't build for hypothetical futures

**Learning Stance**:
- Test case is learning vehicle
- Friction points are valuable data
- Every sprint informs the next

---

## 📈 Success Metrics

**This convergence succeeds when**:

✅ Feature scope clearly defined (5 must-haves)
✅ All deferred ideas preserved with conditions
✅ Test case identified (`amplifier/README.md`)
✅ Timeline set (1 week sprint)
✅ Next steps clear (sprint planning)

**All achieved.** ✅

**Implementation succeeds when** (from Success Criteria):
- [ ] Can regenerate `amplifier/README.md` from template
- [ ] Structure stays consistent
- [ ] Change detection works
- [ ] Friction points identified for Phase 2

---

## 🔗 Related Documents

**This Convergence**:
- `FEATURE_SCOPE.md` - What we're building
- `DEFERRED_FEATURES.md` - What we're deferring
- `CONVERGENCE_COMPLETE.md` - This summary

**Project Context**:
- `MASTER_BACKLOG.md` - Consolidated backlog across all convergences
- `issues/ISSUES_TRACKER.md` - Issues discovered during sprints
- `sprints/` - Sprint plans (to be created)

**Previous Convergences**:
- `2025-11-18-problem-a-template-system/` - Template system (v0.1.0)
- `2025-11-18-chunked-generation/` - Chunked generation (v0.2.0)

---

## 💬 Closing Thoughts

This convergence demonstrates the power of **diverge → capture → converge → defer** workflow:

1. **Diverged freely** - Explored 26+ features and capabilities
2. **Captured systematically** - Organized into clear categories
3. **Converged ruthlessly** - Selected only 5 must-haves
4. **Deferred thoughtfully** - Preserved 21 features with conditions

**The result**: Clear feature scope, preserved exploration value, nothing lost.

**The proof**: Ready for sprint planning with confidence.

---

**Convergence Complete**. Time to build. 🚀

---

**Date Completed**: 2025-11-19
**Next Review**: After feature scope implementation (2025-11-26)
**Review Trigger**: When test case ships and is used for 10+ regenerations
