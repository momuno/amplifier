# Workflow: Feature Scope to Sprints (Sprint-Planner)

**Purpose**: Break down feature scope into executable value-first sprints following lean/agile principles.

**Agent**: `sprint-planner`
**Command**: `/plan-sprints [feature-scope-path]`
**Duration**: 20-30 minutes
**Output**: Sprint plan documents with detailed breakdown

---

## When to Use This Workflow

✅ **Use when:**
- Have a converged feature scope definition
- Ready to plan implementation
- Need to break down features into deliverables
- Want realistic timeline with milestones
- Following the ideation → feature scope → sprints → code flow

❌ **Don't use when:**
- Don't have clear feature scope yet (use `/converge` first)
- Feature scope is tiny (1-2 days work, just implement directly)
- Requirements are still changing rapidly

---

## What the Sprint-Planner Does

### Core Principles

**1. Value-First Sequencing**
- Most valuable learning delivered first
- Each sprint delivers working functionality
- Can stop after any sprint with usable software

**2. Vertical Slicing**
- End-to-end features, not horizontal layers
- "Walking skeleton" over "complete foundations"
- Working software over comprehensive features

**3. Realistic Estimation**
- Based on complexity and unknowns
- Accounts for learning and iteration
- Includes test-writing time (TDD)

**4. Clear Deliverables**
- Each sprint has concrete outcomes
- Acceptance criteria defined upfront
- Learning goals explicit

---

## Input: Feature Scope Definition

The sprint-planner needs your `FEATURE_SCOPE.md` which should contain:

**Required**:
- The ONE problem statement
- 3-5 must-have features
- Success criteria
- Timeline (e.g., "2 weeks")
- First test target (if applicable)

**Optional but helpful**:
- Architecture overview
- Technical specifications
- Risks and mitigation strategies

**Example**: `ai_working/doc_evergreen/convergence/YYYY-MM-DD-feature-name/FEATURE_SCOPE.md`

---

## The Sprint Planning Process

### Step 1: Analyze Feature Scope

**Agent reviews**:
- Feature complexity
- Dependencies between features
- Technical risks
- Learning opportunities
- Test coverage needs

**Example from doc-evergreen**:
```
3 features analyzed:
- Template-based regeneration (moderate complexity)
- Context gathering (straightforward)
- Review & accept workflow (moderate complexity)

Total estimated: ~2,000 LOC including tests
Timeline: 2 weeks (10 working days)
```

### Step 2: Identify Value-First Sequencing

**Agent determines**:
- Which feature delivers learning fastest?
- What's the "walking skeleton" (end-to-end proof)?
- What can be built incrementally?
- What validates core assumptions early?

**Example from doc-evergreen**:
```
Sprint 1: Proof of concept (hardcoded)
  → Tests if LLM can generate acceptable docs
  → Working end-to-end on Day 3

Sprint 2: Review workflow
  → Makes it safe to use
  → Builds on Sprint 1

Sprint 3: CLI + templates
  → Makes it reusable
  → Generalizes Sprint 1+2

Sprint 4: Context control
  → Completes feature scope
  → Final polish
```

### Step 3: Break Down Into Sprints

**Each sprint includes**:
- Duration (2-5 days typically)
- Clear deliverable (what works at the end)
- Features included
- What gets deliberately punted
- Learning goals
- Acceptance criteria
- Estimated LOC

**Example Sprint Structure**:
```markdown
# Sprint 1: Proof of Concept (3 days)

## Deliverable
Working README generation using hardcoded sources and templates

## Includes
- Hardcoded template for README
- Hardcoded source file list
- LLM-based generation
- Output to file

## Deliberately Punted
- CLI (use Python script directly)
- Multiple templates
- User-specified sources
- Review workflow

## Learning Goal
Does LLM generation produce acceptable output?

## Acceptance Criteria
- [ ] Can generate README from template
- [ ] Output is 80%+ acceptable
- [ ] Takes <5 minutes to run

## Estimated LOC
~500 lines (including tests)
```

### Step 4: Define TDD Implementation Order

**For each sprint, agent specifies**:
- Test categories (unit, integration, e2e)
- Test-writing sequence
- Implementation dependencies
- Commit strategy

**Example**:
```
Sprint 1 TDD Order:
1. Test: Template loading
2. Implement: Template loader
3. Test: Source reading
4. Implement: Source reader
5. Test: LLM generation
6. Implement: Generator
7. Test: End-to-end
8. Refactor all
```

### Step 5: Estimate Realistic Timeline

**Agent considers**:
- Complexity of each sprint
- Test-writing time (40% of effort)
- Refactoring time (20% of effort)
- Integration overhead
- Unknown unknowns buffer

**Rule of thumb**:
- Simple sprint: 2-3 days
- Moderate sprint: 3-4 days
- Complex sprint: 4-5 days
- Total feature scope: Usually 1-4 weeks

---

## 🚨 MANDATORY OUTPUT STRUCTURE

**CRITICAL**: All sprint outputs MUST be created in a versioned directory structure. This is NOT optional.

### Required Directory Structure

```
ai_working/[project-name]/sprints/vX.Y.Z-feature-name/
├── SPRINT_PLAN.md              # Overview
├── SPRINT_01_NAME.md           # Sprint 1 details
├── SPRINT_02_NAME.md           # Sprint 2 details
├── SPRINT_03_NAME.md           # Sprint 3 details
└── SPRINT_04_NAME.md           # Sprint 4 details (if needed)
```

**Real Example (doc_evergreen v0.1.0)**:
```
ai_working/doc_evergreen/sprints/v0.1.0-template-system/
├── SPRINT_PLAN.md
├── SPRINT_01_PROOF_OF_CONCEPT.md
├── SPRINT_02_REVIEW_WORKFLOW.md
├── SPRINT_03_CLI_TEMPLATES.md
└── SPRINT_04_CONTEXT_CONTROL.md
```

**Real Example (doc_evergreen v0.2.0)**:
```
ai_working/doc_evergreen/sprints/v0.2.0-chunked-generation/
├── SPRINT_PLAN.md
├── SPRINT_01_CHUNKED_PROCESSING.md
├── SPRINT_02_INTEGRATION.md
└── SPRINT_03_VALIDATION.md
```

**Version Naming Convention**:
- Format: `vX.Y.Z-feature-name`
- Major (v2.0.0): Breaking changes
- Minor (v0.2.0): New features, backward compatible
- Patch (v0.2.1): Bug fixes only

### Structure Validation

**Before declaring sprint planning complete, verify**:

✅ Directory exists: `ai_working/[project]/sprints/vX.Y.Z-feature-name/`
✅ `SPRINT_PLAN.md` is INSIDE the versioned directory
✅ All `SPRINT_##_NAME.md` files are INSIDE the versioned directory
✅ NO sprint files exist directly in `ai_working/[project]/sprints/`
✅ Version number follows SemVer format (vX.Y.Z)

**If files are in wrong location**: DELETE and recreate in correct versioned directory.

---

## Outputs Created

### 1. `SPRINT_PLAN.md` (Overview)

**Location**: `ai_working/[project]/sprints/vX.Y.Z-feature-name/SPRINT_PLAN.md`

**Contains**:
- Overview of all sprints with version number
- Total timeline
- Sprint breakdown summary
- Philosophy alignment
- What's deferred to next version

**Purpose**: High-level roadmap.

### 2. `SPRINT_0X_[NAME].md` (Detailed Plans)

**Location**: `ai_working/[project]/sprints/vX.Y.Z-feature-name/SPRINT_##_NAME.md`

**One file per sprint, contains**:
- Sprint number and name
- Duration estimate
- Deliverable description
- Features included
- What's deliberately punted
- Learning goal
- Acceptance criteria
- TDD implementation order
- Estimated LOC
- Day-by-day breakdown (for longer sprints)

**Purpose**: Implementation blueprint for `/tdd-cycle`.

---

## Example: doc-evergreen Sprint Breakdown

### Input
feature scope with 3 features, 2-week timeline

### Output
4 sprints created:

**Sprint 1: Proof of Concept (3 days)**
- Hardcoded everything
- Tests core assumption: Can LLM generate good docs?
- Delivers working generation by Day 3
- ~500 LOC

**Sprint 2: Review Workflow (2 days)**
- Preview files and diff display
- Accept/reject/edit workflow
- Makes it safe to use on real files
- ~400 LOC

**Sprint 3: CLI + Templates (3 days)**
- Proper CLI interface
- Multiple template types
- Configuration support
- ~650 LOC

**Sprint 4: Context Control (2 days)**
- User-specified sources
- Glob patterns
- Completes feature scope
- ~500 LOC

**Total**: 10 days, ~2,050 LOC (including tests)

---

## Sprint Planning Principles

### 1. Value-First Ordering

**Good**:
```
Sprint 1: Working end-to-end (hardcoded)
Sprint 2: Review workflow (makes it safe)
Sprint 3: Flexibility (CLI + templates)
```

**Bad**:
```
Sprint 1: Database setup
Sprint 2: API layer
Sprint 3: CLI framework
Sprint 4: Try to connect everything
```

**Why**: Deliver working software early, validate assumptions fast.

### 2. Vertical Slicing

**Good**:
```
Sprint 1: Simple doc generation working end-to-end
(even if hardcoded)
```

**Bad**:
```
Sprint 1: Complete database layer
Sprint 2: Complete API layer
Sprint 3: Complete UI layer
```

**Why**: Horizontal layers don't deliver value until connected.

### 3. Deliberate Punting

**Each sprint explicitly states what's NOT included**:
```
Deliberately Punted:
- CLI interface (use Python script)
- Multiple templates (single hardcoded template)
- User-specified sources (hardcoded list)
```

**Why**: Prevents scope creep, keeps sprint focused.

### 4. Learning-Driven

**Each sprint has explicit learning goal**:
```
Learning Goal:
Does LLM generation produce acceptable output?
```

**Why**: Sprints exist to validate assumptions and learn.

---

## TDD Integration

Each sprint plan includes TDD implementation order:

### Test Categories

**Unit Tests (60%)**:
- Individual functions/classes
- Fast, isolated
- Example: Test template parsing

**Integration Tests (30%)**:
- Components working together
- Example: Template + context → generation

**E2E Tests (10%)**:
- Full user workflows
- Example: Command → generated doc

### Implementation Order

**For each feature in sprint**:
1. Write unit tests (RED)
2. Implement to pass (GREEN)
3. Refactor (BLUE)
4. Write integration tests
5. Implement integrations
6. Write E2E test
7. Final refactor

### Commit Strategy

**Commit points**:
- After each green test
- After each refactor
- At sprint completion

**Why**: Always have working code in history.

---

## Common Sprint Patterns

### Pattern 1: The Proof of Concept Sprint

**Characteristics**:
- Hardcoded everything
- End-to-end working
- Validates core assumption
- Usually Sprint 1

**Example**: doc-evergreen Sprint 1

### Pattern 2: The Safety Sprint

**Characteristics**:
- Makes risky things safe
- Adds review/approval workflows
- Builds confidence
- Usually early (Sprint 2-3)

**Example**: doc-evergreen Sprint 2 (review workflow)

### Pattern 3: The Flexibility Sprint

**Characteristics**:
- Generalizes hardcoded things
- Adds configuration
- Makes it reusable
- Usually mid-sprint

**Example**: doc-evergreen Sprint 3 (CLI + templates)

### Pattern 4: The Completion Sprint

**Characteristics**:
- Fills remaining gaps
- Polish and refinement
- Completes feature scope scope
- Usually final sprint

**Example**: doc-evergreen Sprint 4 (context control)

---

## Adjusting Sprint Plans

### When Sprint is Too Big

**Signs**:
- >5 days estimate
- >1,000 LOC
- Too many features
- Unclear what "done" means

**Solution**: Split into 2 sprints
- Find natural breakpoint
- Each sprint delivers value
- Maintain dependencies

### When Sprint is Too Small

**Signs**:
- <1 day estimate
- <200 LOC
- Trivial implementation
- Not worth separate sprint

**Solution**: Combine with adjacent sprint
- Maintain value-first order
- Keep total sprint reasonable (<5 days)

### When Dependencies Are Wrong

**Signs**:
- Sprint 2 needs Sprint 3 features
- Can't deliver value without skipping ahead
- Order doesn't make sense

**Solution**: Reorder sprints
- Respect dependencies
- Maintain value-first when possible
- Document why order changed

---

## Success Criteria

Sprint planning succeeded when:

✅ Each sprint delivers working software
✅ First sprint validates core assumption
✅ Total timeline matches feature scope timeline
✅ Clear what's in/out of each sprint
✅ TDD order is obvious
✅ Acceptance criteria are testable
✅ Can stop after any sprint with usable software
✅ Learning goals are explicit

---

## Tips for Effective Sprint Planning

### Do:
✅ Start with simplest working version (Sprint 1)
✅ Deliver learning early
✅ Make each sprint independently valuable
✅ Explicitly punt things to later sprints
✅ Include test time in estimates (40% of effort)
✅ Have clear acceptance criteria

### Don't:
❌ Build infrastructure before features
❌ Make Sprint 1 just setup/scaffolding
❌ Ignore dependencies between sprints
❌ Forget to define learning goals
❌ Underestimate test writing time
❌ Try to fit everything in Sprint 1

---

## After Sprint Planning: Next Steps

1. **Review the sprint plans**:
   - Read SPRINT_PLAN.md for overview
   - Read each detailed sprint plan

2. **Adjust if needed**:
   - Sprint too big? Split it
   - Dependencies wrong? Reorder
   - Unclear deliverable? Clarify

3. **Start Sprint 1**:
   - Use `/tdd-cycle 1` to begin implementation
   - Follow the TDD order specified
   - Deliver the sprint deliverable

4. **After each sprint**:
   - Review what was learned
   - Adjust remaining sprints if needed
   - Start next sprint

---

## Integration with Other Workflows

**Before this workflow**:
- Used `/converge` to create feature scope definition
- Have clear feature scope scope (3-5 features)

**After this workflow**:
- Have detailed sprint plans
- Ready for implementation
- Use `/tdd-cycle` for each sprint

**Complete chain**:
```
Idea → [/converge] → feature scope → [/plan-sprints] → Sprints → [/tdd-cycle] → Code
```

---

## Command Usage

### Basic Invocation
```
/plan-sprints [mvp-definition-path]
```

**Example**:
```
/plan-sprints ai_working/doc_evergreen/feature scope_DEFINITION.md
```

**What happens**:
1. Loads sprint-planner agent
2. Agent reads feature scope definition
3. Analyzes features and complexity
4. Creates sprint breakdown
5. Generates SPRINT_PLAN.md + individual sprint docs
6. Places in `ai_working/[project]/sprints/`

### Tips for Using the Command
- Ensure feature scope definition is complete
- Review sprint plans after creation
- Adjust if needed before starting implementation
- Use sprint plans as implementation blueprint

---

## Philosophy Alignment

This workflow embodies:

**Ruthless Simplicity**:
- Start with hardcoded proof
- Generalize only when needed
- Deliver minimal viable per sprint

**Value-First Delivery**:
- Learning delivered early
- Working software each sprint
- Can stop after any sprint

**Vertical Slicing**:
- End-to-end features
- Not horizontal layers
- Walking skeleton approach

**TDD Integration**:
- Tests written first
- Estimates include test time
- Implementation order specified

**Trust in Emergence**:
- Don't design everything upfront
- Each sprint informs the next
- Adjust based on learning

---

**Ready to plan your feature scope sprints? Run `/plan-sprints [mvp-path]`**
