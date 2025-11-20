# Convergence: Ideation to Feature Scope

Transform divergent exploration into a focused feature scope definition.

**What this does:**
- Launches the `convergence-architect` agent
- **Reviews existing `MASTER_BACKLOG.md`** to surface relevant/promising items
- Guides you through 4 phases: DIVERGE → CAPTURE → CONVERGE → DEFER
- Creates `FEATURE_SCOPE.md` and `DEFERRED_FEATURES.md` in dated convergence directory
- Updates `MASTER_BACKLOG.md` with all deferred features
- Preserves all ideas while identifying what to build first
- **Supports pure exploration mode** - It's fine if everything gets deferred!

**Usage:**
- Takes 45-60 minutes
- Best with dedicated focus time
- Have your ideas ready (rough is fine!)

**Backlog Integration:**

The convergence-architect agent reviews your existing `MASTER_BACKLOG.md` to:

1. **Surface relevant items**: "You mentioned X, which relates to item Y in the backlog"
2. **Suggest promising candidates**: "Item Z from the backlog might be a good next feature"
3. **Connect related ideas**: "This new idea builds on backlog item W"
4. **Remind you of past ideation**: You won't remember everything - the backlog will

**Two common scenarios:**

**Scenario 1: Pure Exploration/Ideation**
- "I have a bunch of ideas to explore and capture"
- Diverge freely, capture everything to backlog
- Most/all ideas might get deferred - that's fine!
- A pause may be needed to later "unearth" backlog items to define feature scope
- **Note**: FEATURE_SCOPE.md must eventually be defined before moving to sprint planning

**Scenario 2: Finding Next Feature**
- "What should I work on next?"
- Agent surfaces promising items from backlog
- New ideas are explored alongside backlog review
- Convergence identifies the best "next vertical slice"
- Remaining ideas return to backlog

**Process:**
1. **DIVERGE** (10-20 min): Explore all possibilities freely
2. **CAPTURE** (10-15 min): Organize ideas into structures
3. **CONVERGE** (15-20 min): Identify the feature scope (3-5 features max)
4. **DEFER** (10-15 min): Preserve all non-scope ideas with reconsider conditions

**Outputs:**
- `ai_working/[project-name]/convergence/YYYY-MM-DD-feature-name/FEATURE_SCOPE.md`
- `ai_working/[project-name]/convergence/YYYY-MM-DD-feature-name/DEFERRED_FEATURES.md`
- `ai_working/[project-name]/convergence/YYYY-MM-DD-feature-name/CONVERGENCE_COMPLETE.md`
- `ai_working/[project-name]/convergence/MASTER_BACKLOG.md` (updated)

**What you'll need to provide:**
- Project/feature name
- Your ideas and use cases (can be rough)
- Answers to forcing questions during convergence

**After this:**
- Use `/convergent-dev:2-plan-sprints` to break scope into executable sprints with version number
- Or review/adjust feature scope first

**Philosophy:**
- Diverge freely without constraint
- Converge ruthlessly to shippable scope
- Defer thoughtfully (nothing is lost!)
- 3-5 features max for initial scope

**Documentation:** See `ai_context/convergent-dev/CONVERGENCE_PROCESS.md` for detailed guide.

---

**Ready? Let's converge your idea to a shippable MVP.**

I'll now launch the convergence-architect agent to guide you through the process.

**First question:** What project or feature are you exploring?
