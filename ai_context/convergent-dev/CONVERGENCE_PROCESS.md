# Workflow: Ideation to Feature Scope (Convergence-Architect)

**Purpose**: Transform divergent exploration into a focused feature scope definition with all ideas thoughtfully preserved.

**Agent**: `convergence-architect`
**Command**: `/converge [project-name]`
**Duration**: 30-60 minutes
**Output**: FEATURE_SCOPE.md + DEFERRED_FEATURES.md + Updated MASTER_BACKLOG.md

---

## When to Use This Workflow

✅ **Use when:**

- Starting a new project or feature
- Have lots of ideas but unclear scope
- Need to narrow possibilities to shippable feature scope
- Feeling overwhelmed by options
- Want to ensure nothing gets lost while converging
- Pure exploration/ideation (capturing ideas even if nothing becomes "next")
- Finding next feature from existing backlog

❌ **Don't use when:**

- Requirements are already crystal clear
- Feature scope is obvious and small
- Just need to implement a well-defined task

---

## Backlog Integration

**The convergence-architect agent reviews your existing `MASTER_BACKLOG.md` to:**

1. **Surface relevant items** - "You mentioned X, which relates to item Y in the backlog"
2. **Suggest promising candidates** - "Item Z from the backlog might be a good next feature"
3. **Connect related ideas** - "This new idea builds on backlog item W"
4. **Remind you of past ideation** - You won't remember everything - the backlog will

**Two common scenarios:**

**Scenario 1: Pure Exploration/Ideation**

- Dump ideas freely, capture everything
- Most/all ideas might get deferred to backlog - that's perfectly fine!
- Goal is to preserve thinking, not force a feature scope

**Scenario 2: Finding Next Feature**

- Agent surfaces promising items from backlog
- New ideas explored alongside backlog review
- Convergence identifies the best "next vertical slice"
- Remaining ideas return to backlog

---

## The Four Phases

### 🌟 Phase 1: DIVERGE (10-20 minutes)

**Goal**: Explore ALL possibilities without constraint.

**What Happens**:

- Agent asks expansive questions
- You share use cases, features, ideas freely
- No evaluation or judgment yet
- Capture everything that comes to mind

**Good Prompts to Share**:

- User experiences you envision
- Problems you're trying to solve
- Features you've imagined
- Edge cases and special scenarios
- "What if..." possibilities

**Example from doc-evergreen**:

```
User shared 6 use cases:
1. Change detection and doc updates
2. Dependable doc generation process
3. Version control for docs and generation inputs
4. Creating docs from scratch
5. Template/prompt creation and evolution
6. Intelligent doc discovery

Plus recursive template ideas, quality thresholds, specialty features, etc.
```

**Agent Behavior**:

- Asks "what else?" repeatedly
- Encourages ambitious thinking
- Helps organize thoughts as they flow
- Suggests perspectives you haven't considered

**Your Role**:

- Think freely without self-censoring
- Share half-formed ideas (they're valuable!)
- Don't worry about feasibility yet
- Explore "unlimited resources" scenarios

**Transition Signal**:
Agent asks: "Are you feeling like you've explored the full space, or is there more?"

---

### 📋 Phase 2: CAPTURE (10-15 minutes)

**Goal**: Organize divergent ideas into clear structures.

**What Happens**:

- Agent groups related ideas into clusters
- Identifies dependencies between features
- Notes assumptions to validate
- Highlights patterns and relationships

**Example from doc-evergreen**:

```
Organized into:
- 6 main use cases
- 3 core specialty features (source gathering, analysis, doc update)
- Template lifecycle concept
- Recursive structure insights
```

**Agent Behavior**:

- Groups related ideas
- Maps dependencies ("A needs B")
- Flags assumptions ("Users will want X")
- Preserves everything (nothing deleted)

**Your Role**:

- Confirm groupings make sense
- Clarify relationships
- Add missing connections

**Important for Exploration Mode**:
This CAPTURE phase is critical even when doing pure exploration. It ensures backlog items are:

- Relevant to the project
- Well-defined and structured
- Not just raw brain dumps

Without CAPTURE, the backlog becomes disorganized notes. With CAPTURE, it becomes a curated collection of potential features.

**Transition Signal**:
Agent announces: "Let's transition to PHASE 3: CONVERGE. In this phase, I'll help you decide what to build FIRST..." (or "Let's pause here and capture everything to the backlog" in exploration mode)

---

### 🎯 Phase 3: CONVERGE (15-20 minutes)

**Goal**: Identify the feature scope - what to build FIRST.

**Artifact Created**:

- ✅ `FEATURE_SCOPE.md` - Created at END of this phase

**What Happens**:

- Agent asks forcing questions
- Helps identify THE core problem
- Challenges complexity
- Guides to minimal viable scope

**The Forcing Questions**:

**Value Questions:**

- "What's the ONE problem you're solving?"
- "Who has this problem RIGHT NOW?"
- "How do they solve it today?"
- "Why is the current solution insufficient?"

**Learning Questions:**

- "What's your biggest assumption?"
- "What's the fastest way to test that assumption?"

**Simplicity Questions:**

- "Can we cut this in half?"
- "What if you only had 1 week?"
- "What's the embarrassingly simple version?"

**Example from doc-evergreen**:

```
Converged to:
- ONE problem: Docs drift, manual updates tedious
- 3 must-have features:
  1. Template-based regeneration
  2. Context gathering
  3. Review & accept workflow
- Everything else deferred
```

**Agent Creates**: `FEATURE_SCOPE.md` during this phase

**Your Role**:

- Answer forcing questions honestly
- Resist feature creep
- Trust that deferred ≠ deleted
- Focus on learning, not perfection

**Key Decision**: What teaches us the most with least effort?

**Phase 3 Completion Checklist**:

```
[ ] Core problem identified (one sentence)
[ ] Feature scope defined (3-5 features)
[ ] FEATURE_SCOPE.md created with test case documented
```

**Transition Signal**:
Agent announces: "Let's transition to PHASE 4: DEFER. We'll preserve all ideas not in feature scope..."

---

### 💾 Phase 4: DEFER (10-15 minutes)

**Goal**: Preserve all non-scope ideas with clear rationale.

**Artifacts Created**:

- ✅ `DEFERRED_FEATURES.md` - All non-scope features
- ✅ `MASTER_BACKLOG.md` - Updated with deferred items
- ✅ `CONVERGENCE_COMPLETE.md` - Session summary

**CRITICAL: All 3 files above are MANDATORY. Agent must create all 3 before declaring completion.**

**What Happens**:

- Agent captures everything NOT in feature scope
- Documents WHY each thing is deferred
- Sets "reconsider when..." conditions
- Organizes by priority (v2, future, parking lot)
- **Creates all 3 required files**
- **Validates all 4 total files exist before announcing completion**

**Example from doc-evergreen**:

```
23 deferred features organized:
- Version 2 (6 features): Change detection, template lifecycle, etc.
- Future (8 features): Meta-templates, cross-file tracking, etc.
- Optimizations (4 features): Background processing, caching, etc.
- Parking Lot (5+ ideas): Template marketplace, hooks, etc.

Each with:
- What it is
- Why valuable
- Why deferred
- Reconsider when [specific condition]
```

**Agent Creates**: `DEFERRED_FEATURES.md` during this phase

**Your Role**:

- Confirm categorization makes sense
- Add any "reconsider when" conditions
- Feel confident nothing is lost

**Completion Signal**:
Agent announces: "🎉 Convergence Complete!" with summary of all phases and artifacts created.

---

## Outputs Created (ALL MANDATORY)

**CRITICAL**: All 4 outputs below are MANDATORY for convergence completion. The convergence-architect agent MUST create all 4 files before declaring completion.

### 1. `ai_working/[project]/convergence/YYYY-MM-DD-feature-name/FEATURE_SCOPE.md` ✅ REQUIRED

**Contains**:

- The ONE problem statement
- The specific user (not hypothetical)
- Current solution and why it fails
- Feature scope solution (3-5 features with rationale)
- Success criteria
- Timeline
- Architecture overview
- Risks and mitigation

**Purpose**: Blueprint for implementation.

**Note**: Version number (vX.Y.Z) is NOT assigned here - the sprint-planner determines that.

**Created in**: Phase 3 (CONVERGE)

### 2. `ai_working/[project]/convergence/YYYY-MM-DD-feature-name/DEFERRED_FEATURES.md` ✅ REQUIRED

**Contains**:

- All explored features not in feature scope
- Organized by priority
- Each with "reconsider when" conditions
- Preserves the full divergent exploration

**Purpose**: Nothing lost, clear path for v2+.

**Created in**: Phase 4 (DEFER)

### 3. `ai_working/[project]/convergence/YYYY-MM-DD-feature-name/CONVERGENCE_COMPLETE.md` ✅ REQUIRED

**Contains**:

- Summary of all 4 phases
- Statistics (N use cases explored, M features, X converged, Y deferred)
- Complete list of all files created
- Next steps guidance

**Purpose**: Session completion record and handoff to next workflow step.

**Created in**: Phase 4 (DEFER - Completion)

### 4. `ai_working/[project]/convergence/MASTER_BACKLOG.md` (updated or created) ✅ REQUIRED

**Contains**:

- Consolidated deferred features from ALL convergence sessions
- Single source of truth for backlog
- Reviewed at start of each convergence session

**Purpose**: Ensure no ideas are forgotten across multiple convergence cycles.

**Updated in**: Phase 4 (DEFER)

---

### Validation Before Completion

The convergence-architect agent validates these 4 files exist before declaring "Convergence Complete":

```
[ ] FEATURE_SCOPE.md created
[ ] DEFERRED_FEATURES.md created
[ ] CONVERGENCE_COMPLETE.md created
[ ] MASTER_BACKLOG.md updated/created
```

**If ANY file is missing, the workflow is NOT complete.**

---

## Tips for Effective Convergence

### During Divergence

✅ **Do:**

- Share half-formed ideas
- Think big without constraint
- Explore "what if" scenarios
- Mention edge cases and special situations

❌ **Don't:**

- Self-censor or filter
- Worry about feasibility
- Try to converge too early
- Rush through exploration

### During Convergence

✅ **Do:**

- Answer forcing questions honestly
- Challenge your own scope creep
- Focus on learning value
- Trust the deferral process

❌ **Don't:**

- Try to fit everything in feature scope
- Fear losing good ideas (they're preserved!)
- Ignore the "embarrassingly simple" question
- Forget to identify the ONE problem

### General

✅ **Do:**

- Let phases unfold naturally
- Trust the agent's guidance
- Think of initial feature scope as first learning iteration
- Remember: defer ≠ delete

❌ **Don't:**

- Skip phases
- Make initial scope "version 1.0" (start with v0.1.0!)
- Treat deferred features as rejected
- Rush to implementation without clear feature scope

---

## Common Challenges and Solutions

### Challenge: "Everything feels essential!"

**Solution**: Use the forcing questions. If you only had 1 week, what would you build? That's probably your feature scope.

### Challenge: "I'm afraid to defer good features"

**Solution**: Deferred features have clear "reconsider when" conditions. You WILL come back to them after learning from initial release.

### Challenge: "The feature scope feels too simple"

**Solution**: That's the point! Simple scope = fast learning = informed next iteration. Complex scope = slow delivery = assumptions untested.

### Challenge: "I keep adding 'just one more feature'"

**Solution**: For each feature, ask: "Do we NEED this for learning, or are we GUESSING users want it?" Guess = defer.

---

## Success Criteria

You've successfully converged when:

✅ You can state THE ONE problem in one sentence
✅ Feature scope has 3-5 features max (not 10+)
✅ Each feature has clear "why essential" rationale
✅ You feel good about what's deferred (not lost)
✅ You have clear success criteria
✅ You know what you'll learn from initial release
✅ Timeline feels achievable (usually 1-4 weeks)
✅ **OR** all ideas captured to backlog with intent to return and define scope (pure exploration is valid, but FEATURE_SCOPE.md must eventually be completed before sprint planning)

---

## Real Example: doc-evergreen Session

**Input**: "I have ideas for a doc-evergreen tool"

**Divergence** (20 min):

- 6 use cases shared
- 20+ features explored
- Template lifecycle discussions
- Recursive architecture ideas

**Capture** (10 min):

- Organized into clusters
- Identified 3 specialty features
- Noted dependencies
- Mapped relationships

**Convergence** (15 min):

- ONE problem: Docs drift, updates tedious
- 3 must-have features: Template regen, context gathering, review
- 20 features deferred
- 2-week timeline

**Defer** (10 min):

- 23 features organized by priority
- Each with "reconsider when" conditions
- Clear path for v2+

**Total time**: ~55 minutes
**Output**: Clear feature scope + preserved exploration

---

## After Convergence: Next Steps

1. **Review the artifacts**:

   - Read FEATURE_SCOPE.md thoroughly
   - Check DEFERRED_FEATURES.md for clarity
   - Review MASTER_BACKLOG.md to see consolidated ideas

2. **Adjust if needed**:

   - Scope still too big? Re-converge
   - Something missing? Add to deferred list
   - Pure exploration session? No adjustment needed - ideas are captured!

3. **Move to sprint planning**:

   - Use `/plan-sprints` to break feature scope into sprints with version number
   - Sprint planner will also consider any tracked issues from ISSUES_TRACKER.md
   - This is the natural next step

4. **Share with stakeholders**:
   - Feature scope definition is stakeholder-ready
   - Shows what's in scope and what's intentionally deferred

---

## Integration with Other Workflows

**Before this workflow**:

- You have an idea or feature request
- Possibly some rough notes or explorations

**After this workflow**:

- Clear feature scope definition (or all ideas captured if pure exploration)
- All ideas preserved in MASTER_BACKLOG.md
- Ready for sprint planning

**Next workflow**:

- Use `/plan-sprints` with your FEATURE_SCOPE.md
- Sprint planner breaks feature scope into executable sprints with version number
- Sprint planner also considers existing issues from ISSUES_TRACKER.md

**Complete chain**:

```
Idea → [/converge] → Feature Scope → [/plan-sprints] → Sprints → [/tdd-cycle] → Code → [/capture-issues] → (cycle repeats)
```

---

## Command Usage

### Basic Invocation

```
/converge [project-name]
```

**Example**:

```
/converge doc-evergreen
```

**What happens**:

1. Loads convergence-architect agent
2. Agent reviews existing MASTER_BACKLOG.md (if present)
3. Agent greets and explains process
4. Begins DIVERGE phase (surfaces relevant backlog items)
5. Progresses through all 4 phases
6. Creates FEATURE_SCOPE.md and DEFERRED_FEATURES.md
7. Updates MASTER_BACKLOG.md with new deferred features

### Tips for Using the Command

- Have your ideas ready (but rough is fine!)
- Set aside 45-60 minutes uninterrupted
- Be ready to answer forcing questions
- Trust the process through all 4 phases

---

## Philosophy Alignment

This workflow embodies:

**Ruthless Simplicity**:

- Start with minimum viable scope
- Defer everything not essential
- 3-5 features max for initial release

**Trust in Emergence**:

- Don't design everything upfront
- Learn from initial release before building v2
- Let complexity justify itself

**Value-First Thinking**:

- Focus on learning value
- Deliver fastest path to validation
- Iterate based on real usage

**Respect for Divergence**:

- Divergent thinking is a strength
- All ideas have value
- Deferring preserves, not deletes

---

**Ready to converge your next idea? Run `/converge [project-name]`**
