# Workflow: TDD Cycle (Sprint Implementation)

**Purpose**: Implement sprint features using Test-Driven Development with coordinated agent workflow.

**Agents**: `tdd-specialist`, `zen-architect`, `modular-builder`
**Command**: `/tdd-cycle [sprint-number]`
**Duration**: Per sprint plan (2-5 days typically)
**Output**: Tested, working code for sprint deliverable

---

## When to Use This Workflow

✅ **Use when:**
- Have sprint plan ready
- Ready to implement features
- Want test-first development
- Following ideation → feature scope → sprints → code flow

❌ **Don't use when:**
- Don't have sprint plan yet (use `/plan-sprints` first)
- Requirements are unclear
- Just prototyping/exploring

---

## The TDD Cycle

### 🔴 RED: Write Failing Test
**Agent**: `tdd-specialist`

1. Analyzes feature requirements from sprint plan
2. Writes ONE failing test that defines desired behavior
3. Test must actually fail (proves it tests something)
4. Uses AAA (Arrange-Act-Assert) pattern
5. Tests behavior, not implementation

**Example**:
```python
def test_template_loader_reads_markdown_file():
    """
    Given: A markdown template file exists
    When: Template loader reads it
    Then: Returns parsed template structure
    """
    # ARRANGE
    template_path = "templates/readme.md"
    loader = TemplateLoader()

    # ACT
    template = loader.load(template_path)

    # ASSERT
    assert template.sections is not None
    assert len(template.sections) > 0
```

**Run test → It fails → Good!**

---

### 🟢 GREEN: Write Minimal Code to Pass
**Agent**: Depends on test complexity

#### For Simple Tests → `modular-builder` directly

**When**:
- Straightforward logic
- Single function/class
- No architecture decisions
- Obvious implementation

**Example**:
```python
# Test was: Load template file
# Minimal code to pass:

class TemplateLoader:
    def load(self, path: str) -> Template:
        with open(path) as f:
            content = f.read()
        return Template(sections=content.split('---'))
```

**Run test → It passes → Good!**

#### For Complex Tests → `zen-architect` + `modular-builder`

**When**:
- Architecture decisions needed
- Multiple components interact
- Design patterns required
- Non-obvious approach

**Process**:
1. `zen-architect` analyzes (ANALYZE mode)
2. Designs approach
3. `modular-builder` implements the design

**Example**:
```
Test: LLM generates doc from template + context

Zen-architect:
"This needs:
1. Context aggregator (reads source files)
2. Prompt builder (template + context → LLM prompt)
3. LLM caller (Claude Code SDK)
4. Response parser (markdown → document)"

Modular-builder:
[Implements those components to pass test]
```

---

### 🔵 REFACTOR: Improve Code Quality
**Agent**: `modular-builder` (or `zen-architect` if significant)

**Now that tests protect you**:
- Extract functions
- Improve names
- Remove duplication
- Better structure

**Example**:
```python
# Before refactor (works, but messy)
class TemplateLoader:
    def load(self, path: str) -> Template:
        with open(path) as f:
            content = f.read()
        parts = content.split('---')
        sections = []
        for p in parts:
            if p.strip():
                sections.append(p.strip())
        return Template(sections=sections)

# After refactor (cleaner, tests still pass)
class TemplateLoader:
    def load(self, path: str) -> Template:
        content = self._read_file(path)
        sections = self._parse_sections(content)
        return Template(sections=sections)

    def _read_file(self, path: str) -> str:
        with open(path) as f:
            return f.read()

    def _parse_sections(self, content: str) -> list[str]:
        return [s.strip() for s in content.split('---') if s.strip()]
```

**Run tests → Still pass → Good!**

**Commit after refactor.**

---

## Agent Coordination Flow

### My Role as Orchestrator

I coordinate the TDD cycle:

```
┌─────────────────────────────────────────┐
│ Sprint Plan (Input)                     │
│ - Features to implement                 │
│ - TDD order specified                   │
│ - Acceptance criteria                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ For each feature/test:                  │
│                                          │
│ 🔴 tdd-specialist                       │
│   → Write failing test                  │
│                                          │
│ [Orchestrator assesses complexity]      │
│                                          │
│ 🟢 Simple? → modular-builder            │
│    Complex? → zen-architect first       │
│   → Implement minimal code              │
│                                          │
│ 🔵 modular-builder                      │
│   → Refactor for quality                │
│                                          │
│ [Commit on green]                       │
│                                          │
│ Repeat for next test                    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ Sprint Deliverable (Output)             │
│ - All tests passing                     │
│ - Working feature                       │
│ - Clean, refactored code                │
└─────────────────────────────────────────┘
```

### Decision Criteria for Agent Selection

**I assess each test and choose**:

**Use `modular-builder` directly when**:
- ✅ Test is for single function/class
- ✅ Implementation is straightforward
- ✅ No architecture decisions needed
- ✅ Obvious what code should do
- ✅ Unit test scope

**Use `zen-architect` + `modular-builder` when**:
- ✅ Test involves multiple components
- ✅ Architecture decision needed
- ✅ Design pattern would help
- ✅ Integration test scope
- ✅ Non-obvious approach
- ✅ Trade-offs to consider

**Philosophy**: Don't over-architect simple things, but think through complex ones.

---

## Example: Sprint 1 Implementation

**Sprint 1**: Proof of Concept (3 days)

**Deliverable**: Working README generation with hardcoded sources

### Day 1: Template Loading

**Test 1** (tdd-specialist):
```python
def test_template_loader_reads_file():
    loader = TemplateLoader()
    template = loader.load("templates/readme.md")
    assert template is not None
```

**Implementation** (modular-builder - simple):
```python
class TemplateLoader:
    def load(self, path: str) -> Template:
        with open(path) as f:
            return Template(content=f.read())
```

**Refactor** (modular-builder):
```python
# Extract file reading
# Add error handling
# Improve structure
```

**Commit**: ✅ Template loading works

---

**Test 2** (tdd-specialist):
```python
def test_template_parser_extracts_sections():
    content = "# [SECTION: Overview]\n...\n---\n# [SECTION: Usage]\n..."
    parser = TemplateParser()
    sections = parser.parse(content)
    assert len(sections) == 2
```

**Implementation** (modular-builder - simple):
```python
class TemplateParser:
    def parse(self, content: str) -> list[Section]:
        parts = content.split('---')
        return [Section.from_text(p) for p in parts]
```

**Refactor**: Extract section parsing logic

**Commit**: ✅ Template parsing works

---

### Day 2: Context Gathering + LLM Integration

**Test 3** (tdd-specialist):
```python
def test_context_gatherer_reads_source_files():
    sources = ["src/main.py", "README.md"]
    gatherer = ContextGatherer()
    context = gatherer.gather(sources)
    assert len(context.files) == 2
```

**Implementation** (modular-builder - simple):
```python
class ContextGatherer:
    def gather(self, paths: list[str]) -> Context:
        files = [self._read_file(p) for p in paths]
        return Context(files=files)
```

**Commit**: ✅ Context gathering works

---

**Test 4** (tdd-specialist):
```python
def test_doc_generator_creates_markdown():
    template = Template(...)
    context = Context(...)
    generator = DocGenerator()

    doc = generator.generate(template, context)

    assert doc.content.startswith("#")
    assert len(doc.content) > 100
```

**Implementation** (zen-architect + modular-builder - complex):
- Needs LLM integration design
- Prompt construction strategy
- Response parsing approach

**Zen-architect analyzes**:
```
Approach:
1. Build prompt from template + context
2. Call Claude Code SDK
3. Parse markdown response
4. Validate output structure
```

**Modular-builder implements** the design

**Commit**: ✅ Doc generation works

---

### Day 3: End-to-End Test + Refactor

**Test 5** (tdd-specialist):
```python
def test_end_to_end_readme_generation():
    """Full integration test"""
    result = generate_readme(
        template_path="templates/readme.md",
        sources=["src/main.py", "README.md"]
    )

    assert result.success
    assert Path("README.generated.md").exists()
    # Verify content quality
```

**Implementation** (modular-builder):
- Wire all components together
- Add error handling
- Output to file

**Refactor** (modular-builder + potentially zen-architect):
- Review all code from Days 1-3
- Extract common patterns
- Improve naming
- Simplify complex parts
- Add defensive utilities

**Commit**: ✅ Sprint 1 complete - working proof of concept

---

## Test Quality Assurance

### The tdd-specialist Ensures

**Tests are HONEST gatekeepers:**
- ❌ Fail when code is broken
- ✅ Pass when code is correct
- 🎯 Test behavior, not implementation

**Common anti-patterns AVOIDED:**
1. Testing mocks instead of behavior
2. Tests that don't test anything
3. Testing implementation details
4. Interdependent tests
5. Over-mocking

**Example of good test**:
```python
def test_generates_valid_markdown():
    # Tests BEHAVIOR: output is valid markdown
    doc = generator.generate(template, context)
    assert doc.startswith("#")  # Has heading
    assert "\n\n" in doc  # Has paragraphs
    # NOT testing: how generator built the string internally
```

**Example of bad test**:
```python
def test_generator_calls_llm():
    # Tests IMPLEMENTATION: that LLM was called
    mock_llm = Mock()
    generator = Generator(mock_llm)
    generator.generate(template, context)
    mock_llm.call.assert_called_once()  # Testing the mock!
```

---

## Commit Strategy

### When to Commit

✅ **After each green test**:
```
git commit -m "feat: add template loader

Tests: test_template_loader_reads_file passes"
```

✅ **After each refactor**:
```
git commit -m "refactor: extract file reading logic

Tests: all passing, no behavior change"
```

✅ **At sprint completion**:
```
git commit -m "feat: complete Sprint 1 - proof of concept

Deliverable: Working README generation with hardcoded sources
- Template loading works
- Context gathering works
- LLM generation works
- End-to-end test passes

All acceptance criteria met."
```

### Commit Message Format

```
<type>: <description>

[optional body]

🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>
```

**Types**:
- `feat`: New feature
- `test`: Add/update tests
- `refactor`: Refactor without behavior change
- `fix`: Bug fix

---

## Progress Tracking

### During TDD Cycle

Use `TodoWrite` to track progress:

```
Sprint 1 Implementation:
├── ✅ Test: Template loading
├── ✅ Implement: Template loader
├── ✅ Refactor: Template loader
├── ✅ Test: Template parsing
├── ✅ Implement: Template parser
├── 🔄 Test: Context gathering (in progress)
├── ⏳ Implement: Context gatherer
├── ⏳ Test: LLM generation
└── ⏳ End-to-end test
```

### Sprint Completion Checklist

Before marking sprint complete:

- [ ] All tests written first (RED)
- [ ] All tests passing (GREEN)
- [ ] Code refactored for quality (BLUE)
- [ ] Acceptance criteria met
- [ ] Learning goal achieved
- [ ] Sprint deliverable working
- [ ] All commits have passing tests
- [ ] **Sprint results documented** (RESULTS.md created - see below)
- [ ] **Post-sprint cleanup completed** (see below)
- [ ] Ready for next sprint

### Sprint Results Documentation

**Purpose**: Capture sprint outcomes, learnings, and recommendations for future reference.

**Responsibility**: The orchestrator (Claude Code) creates RESULTS.md after sprint completion, not a specialized agent.

**When**: After all sprint deliverables are complete and tests are passing, but before post-sprint cleanup.

**Location**: `ai_working/[project]/sprints/[sprint-dir]/SPRINT_[NN]_RESULTS.md`

**Template Structure**:

```markdown
# Sprint [N]: [Sprint Name] - Results

**Status**: ✅ Complete
**Date**: [Completion Date]
**Version**: [e.g., v0.2.0]

## Executive Summary

[2-3 paragraph overview of what was built and why it matters]

## What We Built

### Sprint Goal
[Original sprint goal from planning]

### Deliverables
- **[Feature 1]**: [Brief description]
- **[Feature 2]**: [Brief description]
- **Tests**: [Number] tests covering [coverage description]

## TDD Cycle Implementation

### RED Phase (Tests First)
[Description of test-first approach and what tests were written]

### GREEN Phase (Make Tests Pass)
[Description of implementation to make tests pass]

### REFACTOR Phase (Quality Improvements)
[Description of refactoring and quality improvements]

## Agent Coordination

### Agents Used
- **tdd-specialist**: [What they contributed]
- **zen-architect**: [What they contributed]
- **modular-builder**: [What they contributed]
- **[other agents]**: [What they contributed]

### Coordination Patterns
[How agents worked together, what worked well, what could improve]

## Key Learnings

### Technical Insights
- [Learning 1]
- [Learning 2]
- [Learning 3]

### Process Insights
- [Learning 1]
- [Learning 2]

### What Went Well
- [Success 1]
- [Success 2]

### What Could Improve
- [Challenge 1]
- [Challenge 2]

## Success Criteria Assessment

✅ **[Criterion 1]**: [Assessment]
✅ **[Criterion 2]**: [Assessment]
⚠️ **[Criterion 3]**: [Assessment if partially met]
❌ **[Criterion 4]**: [Assessment if not met]

## Recommendations for Next Sprint

### Priority Changes
[Any adjustments to roadmap based on learnings]

### Technical Debt
[Any technical debt identified that should be addressed]

### Architecture Decisions
[Any architectural insights that inform future work]

## Files Created

**Production Code**:
- `path/to/file1.py` - [Purpose]
- `path/to/file2.py` - [Purpose]

**Tests**:
- `tests/test_file1.py` - [What it tests]
- `tests/test_file2.py` - [What it tests]

**Documentation**:
- `docs/file.md` - [Purpose]

## Statistics

- **Total Tests**: [N] ([N] unit, [N] integration)
- **Test Coverage**: [X]%
- **Lines of Code**: [Production] production, [Test] test
- **Files Created**: [N] production, [N] test
- **Sprint Duration**: [N] days/hours
- **Agent Invocations**: [tdd-specialist: N, zen-architect: N, modular-builder: N]

## Conclusion

[1-2 paragraph wrap-up of sprint success and readiness for next sprint]
```

**Key Principles**:

1. **Document outcomes, not just activities** - Focus on what was achieved and learned
2. **Capture agent coordination patterns** - Help improve future agent workflows
3. **Honest assessment** - Note what didn't work as well as what did
4. **Actionable recommendations** - Concrete suggestions for next sprint
5. **Comprehensive statistics** - Quantify the work for progress tracking

**Example Reference**: See `ai_working/doc_evergreen/sprints/v0.1.0-template-system/SPRINT_01_RESULTS.md` for a complete example.

**Orchestrator Workflow**:

```
After sprint completion:
1. Review sprint plan and acceptance criteria
2. Gather test results and coverage statistics
3. Review agent coordination logs/outputs
4. Identify key learnings and insights
5. Assess success criteria honestly
6. Create RESULTS.md using template above
7. Commit with message: "docs: add Sprint [N] results"
8. Proceed to post-sprint cleanup
```

### Post-Sprint Cleanup Phase

**Purpose**: Remove obsolete code and ensure only relevant context remains.

After sprint deliverable is complete and working:

1. **Identify obsolete files**:
   - Files from earlier sprints that have been replaced
   - Old template/prototype files no longer used
   - Temporary test fixtures that served their purpose

2. **Remove replaced functions/classes**:
   - Functions that new sprint code supersedes
   - Classes that have been refactored into better versions
   - Utilities that are now redundant

3. **Clean up imports**:
   - Remove unused imports
   - Update dependencies if packages no longer needed
   - Consolidate duplicate imports

4. **Remove test artifacts**:
   - Leftover mock objects from experiments
   - Unused test fixtures
   - Commented-out test code

5. **Verify nothing breaks**:
   - Run full test suite after cleanup
   - Ensure all tests still pass
   - Check that no files are accidentally importing removed code

6. **Document cleanup in commit**:
   ```
   chore: post-sprint cleanup for Sprint [N]

   Removed obsolete files:
   - old_file_1.py (replaced by new implementation)
   - old_file_2.py (functionality now in main module)

   Cleaned up:
   - Unused imports across modules
   - Leftover test mocks
   - Temporary fixtures

   All [N] tests still passing after cleanup.
   ```

**Example cleanup scenarios**:

**Scenario 1: Sprint replaces proof-of-concept**
```
Sprint 1 created: basic_generator.py (POC)
Sprint 3 created: template_manager.py (production)

Cleanup: Remove basic_generator.py, update tests
```

**Scenario 2: Consolidated utilities**
```
Sprint 1 created: file_reader.py
Sprint 2 created: file_writer.py
Sprint 3 created: file_ops.py (combines both)

Cleanup: Remove file_reader.py and file_writer.py
```

**Scenario 3: Test evolution**
```
Sprint 1: Used mock LLM calls
Sprint 2: Created proper test fixtures
Sprint 3: Improved mocking with @patch decorators

Cleanup: Remove old mock utilities, update all tests to new pattern
```

**Using the `post-task-cleanup` agent**:

The orchestrator can delegate cleanup to the `post-task-cleanup` agent:

```
After sprint deliverable complete:
1. Invoke post-task-cleanup agent
2. Agent reviews git status to see all changes
3. Identifies files that may be obsolete
4. Proposes cleanup actions
5. Removes unnecessary files/code
6. Verifies tests still pass
7. Creates cleanup commit
```

The agent specializes in:
- Detecting temporary artifacts
- Identifying replaced functionality
- Ensuring no accidental breakage
- Following project simplicity principles

---

## Common Patterns

### Pattern 1: The Simple Test Loop

**For straightforward features**:

```
1. tdd-specialist writes test
2. modular-builder implements directly
3. modular-builder refactors
4. Commit
5. Repeat
```

**Example**: File reading, parsing, simple transformations

---

### Pattern 2: The Complex Test Loop

**For features needing design**:

```
1. tdd-specialist writes test
2. zen-architect analyzes and designs
3. modular-builder implements design
4. modular-builder/zen-architect refactors
5. Commit
6. Repeat
```

**Example**: LLM integration, multi-component features

---

### Pattern 3: The Spike Then Test

**When approach is unclear**:

```
1. Quick spike (no tests) to explore
2. Throw away spike code
3. tdd-specialist writes test based on learning
4. Implement properly with TDD
```

**Use sparingly**: Only when genuinely unclear.

---

## Tips for Effective TDD

### Do:
✅ Write test FIRST, always
✅ Watch test fail before implementing
✅ Write minimal code to pass
✅ Refactor with test protection
✅ Commit on green tests
✅ Test behavior, not implementation
✅ Keep tests fast and isolated

### Don't:
❌ Write implementation before test
❌ Skip watching test fail
❌ Over-engineer the implementation
❌ Refactor before tests pass
❌ Test implementation details
❌ Make tests depend on each other
❌ Mock everything

---

## Troubleshooting

### "Test passes immediately"
**Problem**: Test doesn't actually test anything
**Solution**: tdd-specialist reviews test, makes it more specific

### "Can't make test pass"
**Problem**: Test is too complex or requirement unclear
**Solution**: Break into smaller tests, or spike first

### "Tests are brittle"
**Problem**: Testing implementation instead of behavior
**Solution**: tdd-specialist refactors tests to test behavior

### "Too slow"
**Problem**: Tests depend on external systems
**Solution**: Use in-memory fakes, not mocks

---

## Integration with Other Workflows

**Before this workflow**:
- Used `/converge` for feature scope
- Used `/plan-sprints` for sprint breakdown
- Have detailed sprint plan

**During this workflow**:
- Implement sprint features with TDD
- Coordinate between agents
- Deliver sprint deliverable

**After this workflow**:
- Sprint deliverable complete
- **Post-sprint cleanup performed** (remove obsolete files/code)
- Review what was learned
- Adjust remaining sprints if needed
- Start next sprint with `/tdd-cycle [next-sprint]`

**Complete chain**:
```
Idea → [/converge] → Feature Scope → [/plan-sprints] → Sprints → [/tdd-cycle] → Code → [/capture-issues] → (cycle repeats)
```

---

## Command Usage

### Basic Invocation
```
/tdd-cycle [sprint-number]
```

**Example**:
```
/tdd-cycle 1
```

**What happens**:
1. Loads TDD_CYCLE.md context
2. Reads sprint plan for Sprint 1
3. Launches tdd-specialist for first test
4. Coordinates agents through RED-GREEN-REFACTOR
5. Tracks progress with TodoWrite
6. Delivers sprint deliverable

### Advanced Usage
```
/tdd-cycle 1 --feature "template loading"
```

Focus on specific feature within sprint.

---

## Philosophy Alignment

This workflow embodies:

**Test-Driven Development**:
- Tests define requirements
- RED-GREEN-REFACTOR cycle
- Tests are honest gatekeepers

**Ruthless Simplicity**:
- Minimal code to pass tests
- No premature optimization
- Simple before complex

**Agent Specialization**:
- Right tool for right job
- tdd-specialist for tests
- modular-builder for simple code
- zen-architect for complex design

**Continuous Integration**:
- Commit on green
- Always working code
- Incremental delivery

---

**Ready to implement your sprint? Run `/tdd-cycle [sprint-number]`**
