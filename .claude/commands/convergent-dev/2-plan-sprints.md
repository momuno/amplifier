# Sprint Planning: Feature Scope to Executable Sprints

Break down your feature scope into value-first, executable sprints with version number.

**What this does:**
- Launches the `sprint-planner` agent
- Reads your `FEATURE_SCOPE.md` from latest convergence
- Assigns version number (vX.Y.Z) using SemVer based on scope
- Creates 2-5 sprints (typically) with detailed breakdown
- Defines TDD implementation order for each sprint

**Usage:**
- Takes 20-30 minutes
- Requires completed convergence session
- Best done right after `/convergent-dev:1-converge`

**Process:**
1. Agent reads your latest `convergence/YYYY-MM-DD-feature-name/FEATURE_SCOPE.md`
2. Determines version number (vX.Y.Z) based on scope:
   - Major (v2.0.0): Breaking changes
   - Minor (v0.2.0): New features, backward compatible
   - Patch (v0.2.1): Bug fixes only
3. Analyzes feature complexity and dependencies
4. Determines value-first sequencing
5. Breaks down into sprints (2-5 days each)
6. Defines TDD implementation order
7. Creates detailed sprint documents

**Outputs:**
- `ai_working/[project-name]/sprints/vX.Y.Z-feature-name/SPRINT_PLAN.md` (overview with version)
- `ai_working/[project-name]/sprints/vX.Y.Z-feature-name/SPRINT_N.md` (detailed plans)

**Each sprint includes:**
- Duration estimate
- Clear deliverable
- Features included
- What's deliberately deferred
- Learning goal
- Acceptance criteria
- TDD implementation order
- Estimated complexity

**What you'll need to provide:**
- Confirmation of version number
- Confirmation of sprint breakdown
- Adjustments if needed

**After this:**
- Use `/convergent-dev:3-tdd-cycle 1` to start implementing Sprint 1
- Review sprint plans and adjust if needed
- Have clear implementation roadmap

**Philosophy:**
- Value-first sequencing (learning early)
- Vertical slices (end-to-end features)
- Realistic timelines (include test time)
- Clear deliverables per sprint

**Documentation:** See `ai_context/convergent-dev/SPRINT_PLANNING.md` for detailed guide.

---

**Ready? Let's turn your feature scope into executable sprints with version number.**

I'll now launch the sprint-planner agent to analyze your convergence and create sprint breakdown.

**First, I'll locate your latest convergence session...**
