# TDD Cycle: Sprint Implementation

Implement sprint features using Test-Driven Development with agent coordination.

**What this does:**
- Loads TDD cycle workflow context
- Coordinates between tdd-specialist, zen-architect, and modular-builder agents
- Guides you through RED-GREEN-REFACTOR cycles
- Delivers sprint deliverable with tested, working code

**Usage:**
- Duration per sprint plan (2-5 days typically)
- Requires completed sprint plan
- Best done after `/plan-sprints`

**The TDD Cycle:**
1. 🔴 **RED**: tdd-specialist writes failing test
2. 🟢 **GREEN**: Implementation agent writes minimal code to pass
3. 🔵 **REFACTOR**: Improve code quality with test protection
4. Repeat for next test

**Agent Coordination:**
- **tdd-specialist**: Writes all tests first
- **modular-builder**: Implements simple features
- **zen-architect + modular-builder**: Implements complex features
- **Orchestrator (me)**: Decides which agent based on test complexity

**Process per feature:**
1. tdd-specialist writes test (behavior-focused, honest)
2. I assess complexity:
   - Simple → modular-builder implements directly
   - Complex → zen-architect designs, modular-builder implements
3. Refactor for quality
4. Commit on green
5. Next test

**Post-sprint cleanup:**
1. Review codebase for obsolete files
2. Remove functions/classes replaced by sprint work
3. Clean up unused imports and dependencies
4. Remove any leftover test mocks or fixtures
5. Ensure no irrelevant context remains
6. Final commit with cleanup changes

**Outputs:**
- Test files (written first)
- Implementation code (minimal, passes tests)
- Refactored code (clean, maintainable)
- Working sprint deliverable

**What you'll need to provide:**
- Sprint number to implement
- Sprint plan must exist
- Approval for commits (on green tests)
- Feedback during implementation

**After this:**
- Sprint deliverable complete
- All tests passing
- Code refactored and committed
- Ready for next sprint with `/tdd-cycle [next-sprint]`

**Philosophy:**
- Tests first, always (RED-GREEN-REFACTOR)
- Tests are honest gatekeepers
- Minimal code to pass (no over-engineering)
- Refactor with test protection
- Commit on green

**Test Quality:**
- Test behavior, not implementation
- AAA pattern (Arrange-Act-Assert)
- Given-When-Then style
- No mocking everything
- Fast, isolated, repeatable

**Documentation:** See `ai_context/workflows/TDD_CYCLE.md` for detailed guide.

---

**Ready? Let's implement your sprint with TDD.**

I'll now load the TDD cycle workflow and start coordinating agents.

**Which sprint are you implementing?** (e.g., "1" for Sprint 1)
