# Sprint Planning: MVP to Executable Sprints

Break down your MVP into value-first, executable sprints.

**What this does:**
- Launches the `sprint-planner` agent
- Analyzes your MVP definition
- Creates 2-5 sprints (typically) with detailed breakdown
- Defines TDD implementation order for each sprint

**Usage:**
- Takes 20-30 minutes
- Requires completed MVP definition
- Best done right after `/converge`

**Process:**
1. Agent reads your `MVP_DEFINITION.md`
2. Analyzes feature complexity and dependencies
3. Determines value-first sequencing
4. Breaks down into sprints (2-5 days each)
5. Defines TDD implementation order
6. Creates detailed sprint documents

**Outputs:**
- `ai_working/[project-name]/sprints/SPRINT_PLAN.md` (overview)
- `ai_working/[project-name]/sprints/SPRINT_0X_[NAME].md` (detailed plans)

**Each sprint includes:**
- Duration estimate
- Clear deliverable
- Features included
- What's deliberately punted
- Learning goal
- Acceptance criteria
- TDD implementation order
- Estimated LOC

**What you'll need to provide:**
- Path to your MVP_DEFINITION.md
- Confirmation of sprint breakdown
- Adjustments if needed

**After this:**
- Use `/tdd-cycle 1` to start implementing Sprint 1
- Review sprint plans and adjust if needed
- Have clear implementation roadmap

**Philosophy:**
- Value-first sequencing (learning early)
- Vertical slices (end-to-end features)
- Realistic timelines (include test time)
- Clear deliverables per sprint

**Documentation:** See `ai_context/workflows/MVP_TO_SPRINTS.md` for detailed guide.

---

**Ready? Let's turn your MVP into executable sprints.**

I'll now launch the sprint-planner agent to create your sprint breakdown.

**What's the path to your MVP_DEFINITION.md?**
(Example: `ai_working/doc_evergreen/MVP_DEFINITION.md`)
