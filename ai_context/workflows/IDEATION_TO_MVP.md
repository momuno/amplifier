# Workflow: Ideation to MVP (Convergence-Architect)

**Purpose**: Transform divergent exploration into a focused MVP definition with all ideas thoughtfully preserved.

**Agent**: `convergence-architect`
**Command**: `/converge [project-name]`
**Duration**: 30-60 minutes
**Output**: MVP_DEFINITION.md + DEFERRED_FEATURES.md

---

## When to Use This Workflow

✅ **Use when:**
- Starting a new project or feature
- Have lots of ideas but unclear scope
- Need to narrow possibilities to shippable MVP
- Feeling overwhelmed by options
- Want to ensure nothing gets lost while converging

❌ **Don't use when:**
- Requirements are already crystal clear
- MVP scope is obvious and small
- Just need to implement a well-defined task

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

**Transition Signal**:
Agent announces: "Let's transition to PHASE 3: CONVERGE. In this phase, I'll help you decide what to build FIRST..."

---

### 🎯 Phase 3: CONVERGE (15-20 minutes)

**Goal**: Identify the MVP - what to build FIRST.

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

**Agent Creates**: `MVP_DEFINITION.md` during this phase

**Your Role**:
- Answer forcing questions honestly
- Resist feature creep
- Trust that deferred ≠ deleted
- Focus on learning, not perfection

**Key Decision**: What teaches us the most with least effort?

**Transition Signal**:
Agent announces: "Let's transition to PHASE 4: DEFER. We'll preserve all ideas not in MVP..."

---

### 💾 Phase 4: DEFER (10-15 minutes)

**Goal**: Preserve all non-MVP ideas with clear rationale.

**What Happens**:
- Agent captures everything NOT in MVP
- Documents WHY each thing is deferred
- Sets "reconsider when..." conditions
- Organizes by priority (v2, future, parking lot)

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

## Outputs Created

### 1. `ai_working/[project]/MVP_DEFINITION.md`

**Contains**:
- The ONE problem statement
- The specific user (not hypothetical)
- Current solution and why it fails
- MVP solution (3-5 features with rationale)
- Success criteria
- Timeline
- Architecture overview
- Risks and mitigation

**Purpose**: Blueprint for implementation.

### 2. `ai_working/[project]/DEFERRED_FEATURES.md`

**Contains**:
- All explored features not in MVP
- Organized by priority
- Each with "reconsider when" conditions
- Preserves the full divergent exploration

**Purpose**: Nothing lost, clear path for v2+.

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
- Try to fit everything in MVP
- Fear losing good ideas (they're preserved!)
- Ignore the "embarrassingly simple" question
- Forget to identify the ONE problem

### General
✅ **Do:**
- Let phases unfold naturally
- Trust the agent's guidance
- Think of MVP as first learning iteration
- Remember: defer ≠ delete

❌ **Don't:**
- Skip phases
- Make MVP "version 1.0" (it's v0.1!)
- Treat deferred features as rejected
- Rush to implementation without clear MVP

---

## Common Challenges and Solutions

### Challenge: "Everything feels essential!"
**Solution**: Use the forcing questions. If you only had 1 week, what would you build? That's probably your MVP.

### Challenge: "I'm afraid to defer good features"
**Solution**: Deferred features have clear "reconsider when" conditions. You WILL come back to them after learning from MVP.

### Challenge: "The MVP feels too simple"
**Solution**: That's the point! Simple MVP = fast learning = informed next iteration. Complex MVP = slow delivery = assumptions untested.

### Challenge: "I keep adding 'just one more feature'"
**Solution**: For each feature, ask: "Do we NEED this for learning, or are we GUESSING users want it?" Guess = defer.

---

## Success Criteria

You've successfully converged when:

✅ You can state THE ONE problem in one sentence
✅ MVP has 3-5 features max (not 10+)
✅ Each feature has clear "why essential" rationale
✅ You feel good about what's deferred (not lost)
✅ You have clear success criteria
✅ You know what you'll learn from MVP
✅ Timeline feels achievable (usually 1-4 weeks)

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
**Output**: Clear MVP + preserved exploration

---

## After Convergence: Next Steps

1. **Review the artifacts**:
   - Read MVP_DEFINITION.md thoroughly
   - Check DEFERRED_FEATURES.md for clarity

2. **Adjust if needed**:
   - Scope still too big? Re-converge
   - Something missing? Add to deferred list

3. **Move to sprint planning**:
   - Use `/plan-sprints` to break MVP into sprints
   - This is the natural next step

4. **Share with stakeholders**:
   - MVP definition is stakeholder-ready
   - Shows what's in scope and what's intentionally deferred

---

## Integration with Other Workflows

**Before this workflow**:
- You have an idea or feature request
- Possibly some rough notes or explorations

**After this workflow**:
- Clear MVP definition
- All ideas preserved
- Ready for sprint planning

**Next workflow**:
- Use `/plan-sprints` with your MVP_DEFINITION.md
- Breaks MVP into executable sprints

**Complete chain**:
```
Idea → [/converge] → MVP → [/plan-sprints] → Sprints → [/tdd-cycle] → Code
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
2. Agent greets and explains process
3. Begins DIVERGE phase
4. Progresses through all 4 phases
5. Creates MVP_DEFINITION.md and DEFERRED_FEATURES.md

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
- 3-5 features max for MVP

**Trust in Emergence**:
- Don't design everything upfront
- Learn from MVP before building v2
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
