# AI-Assisted Development Workflows

**Purpose**: This directory documents the complete workflows for AI-assisted product development, from ideation to implementation.

---

## The Complete Development Flow

```
💡 Idea/Feature Request
    ↓
📊 [/converge] Convergence-Architect
    ↓ (produces)
📄 MVP Definition + Deferred Features
    ↓
🗓️ [/plan-sprints] Sprint-Planner
    ↓ (produces)
📋 Sprint Plans (value-first, incremental)
    ↓
🔴🟢🔵 [/tdd-cycle] TDD Implementation
    ↓ (produces)
✅ Working Software + Learnings
    ↓
🔄 Revisit Deferred Features → Next MVP
```

---

## The Three Core Workflows

### 1. Ideation to MVP: Convergence-Architect
**Document**: [IDEATION_TO_MVP.md](./IDEATION_TO_MVP.md)
**Command**: `/converge [project-name]`

**Purpose**: Transform divergent exploration into a focused MVP with everything else thoughtfully deferred.

**Phases**:
- 🌟 DIVERGE: Explore all possibilities freely
- 📋 CAPTURE: Organize ideas into structures
- 🎯 CONVERGE: Identify the MVP (3-5 features)
- 💾 DEFER: Preserve ideas for future iterations

**Outputs**:
- `ai_working/[project]/MVP_DEFINITION.md`
- `ai_working/[project]/DEFERRED_FEATURES.md`

**When to use**: Starting new projects, defining features, scope reduction

---

### 2. MVP to Sprints: Sprint-Planner
**Document**: [MVP_TO_SPRINTS.md](./MVP_TO_SPRINTS.md)
**Command**: `/plan-sprints [mvp-definition-path]`

**Purpose**: Break down MVP into executable value-first sprints following lean/agile principles.

**Key Principles**:
- Vertical slices (end-to-end functionality)
- Value-first ordering (deliver learning early)
- Realistic timelines (based on complexity)
- Clear deliverables per sprint

**Outputs**:
- `ai_working/[project]/sprints/SPRINT_PLAN.md` (overview)
- `ai_working/[project]/sprints/SPRINT_0X_[NAME].md` (detailed plans)

**When to use**: After MVP convergence, before implementation starts

---

### 3. Sprint Implementation: TDD Cycle
**Document**: [TDD_CYCLE.md](./TDD_CYCLE.md)
**Command**: `/tdd-cycle [sprint-number]`

**Purpose**: Implement sprint features using Test-Driven Development with coordinated agent workflow.

**The TDD Cycle**:
- 🔴 RED: Write failing test (tdd-specialist)
- 🟢 GREEN: Minimal code to pass (modular-builder or zen-architect + modular-builder)
- 🔵 REFACTOR: Improve with test protection (modular-builder)

**Agent Coordination**:
- Simple tests → modular-builder directly
- Complex tests → zen-architect (design) → modular-builder (implement)
- Orchestrator decides based on test scope

**Outputs**:
- Test files (written first)
- Implementation code (minimal, passes tests)
- Refactored code (improved quality, tests still pass)

**When to use**: Implementing each sprint from the sprint plan

---

## Workflow Selection Guide

### "I have a new project idea"
→ Start with `/converge` to go from idea to MVP

### "I have an MVP definition ready"
→ Use `/plan-sprints` to break it into sprints

### "I have sprint plans ready"
→ Use `/tdd-cycle` to implement each sprint

### "I'm not sure what I need"
→ Use `/workflow` to see this overview and decide

---

## Philosophy Alignment

All workflows embody the project's core principles:

**Ruthless Simplicity**:
- Start minimal, grow as needed
- Avoid future-proofing
- Question every abstraction

**Value-First Delivery**:
- Vertical slices over horizontal layers
- Working software over comprehensive documentation
- Learning-driven over plan-driven

**Test-Driven Development**:
- Tests define requirements
- Red-green-refactor cycle
- Tests are honest gatekeepers

**Trust in Emergence**:
- Don't design everything upfront
- Let patterns emerge through use
- Complexity justifies itself through need

---

## Real-World Example: doc-evergreen

**Starting Point**: "I want a tool to keep documentation up-to-date"

**Step 1 - Convergence** (`/converge doc-evergreen`):
- Explored 6 use cases, 23 features
- Converged to 3-feature MVP
- Deferred 20 features to v2+
- Output: MVP_DEFINITION.md + DEFERRED_FEATURES.md

**Step 2 - Sprint Planning** (`/plan-sprints`):
- Broke MVP into 4 sprints (2 weeks)
- Sprint 1: Proof of concept (3 days)
- Sprint 2: Review workflow (2 days)
- Sprint 3: CLI + templates (3 days)
- Sprint 4: Context control (2 days)
- Output: 5 sprint plan documents

**Step 3 - TDD Implementation** (`/tdd-cycle 1`):
- Sprint 1 implementation with TDD
- Tests written first for each feature
- Minimal code to pass tests
- Refactor for quality
- Output: Working proof of concept

**Result**: From idea to working MVP in 2 weeks, with all ideas preserved for future iterations.

---

## Tips for Success

### During Convergence
- ✅ Explore freely without self-censoring
- ✅ Document everything (nothing is lost)
- ✅ Be ruthless about MVP scope
- ✅ Trust that deferred ≠ deleted

### During Sprint Planning
- ✅ Prioritize learning over features
- ✅ Vertical slices that work end-to-end
- ✅ Realistic estimates (don't over-commit)
- ✅ Clear acceptance criteria per sprint

### During TDD Implementation
- ✅ Write the test first (always!)
- ✅ Test behavior, not implementation
- ✅ Minimal code to pass (resist over-engineering)
- ✅ Refactor with test protection
- ✅ Commit on green tests

---

## Meta-Workflow: The Learning Loop

After completing a sprint or MVP:

1. **Review**: What worked? What didn't?
2. **Learn**: What assumptions were validated/invalidated?
3. **Decide**: Which deferred features matter most now?
4. **Iterate**: Run convergence on next feature set

This creates a continuous improvement cycle where each iteration is informed by real usage and learning.

---

## Getting Started

**New to these workflows?**
1. Read through this README
2. Review the example (doc-evergreen above)
3. Try `/converge` on a small idea
4. Follow the flow through to implementation

**Experienced user?**
- Jump directly to the workflow you need
- Reference the detailed docs for specifics
- Use the slash commands for quick execution

---

## Contributing to These Workflows

These workflows evolve based on usage:
- Found a better pattern? Document it
- Hit a pain point? Note it for improvement
- Discovered a shortcut? Share it

The goal is continuous improvement of the development process itself.

---

**Ready to build something? Start with `/converge [your-idea]`**
