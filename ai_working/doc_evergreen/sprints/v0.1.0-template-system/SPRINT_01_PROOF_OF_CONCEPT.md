# Sprint 1: Proof of Concept

**Duration**: 3 days (Week 1, Days 1-3)
**Goal**: Generate amplifier's README end-to-end with hardcoded template and sources
**Value Delivered**: Working documentation regeneration that proves the concept

---

## Why This Sprint?

This is the **most critical sprint** because it validates the entire MVP hypothesis:

**Question**: Can we generate acceptable documentation from templates + source context?

**If YES** → Continue building features
**If NO** → Pivot approach immediately

**No point building CLI, review workflows, or context selection if generation doesn't work.**

---

## What You'll Have After This Sprint

A simple Python script that:
1. Loads a hardcoded template (README structure)
2. Gathers hardcoded source files (key amplifier files)
3. Sends template + context to LLM
4. Writes generated README to disk
5. You can read it and evaluate quality

**Run it like**: `python generate_readme.py`
**Output**: `README.generated.md`

---

## Deliverables

### 1. Template File (~50 lines)
**File**: `templates/readme-template.md`

**What it does**: Defines README structure with section markers

**Why this sprint**: Need something to generate from

**Implementation notes**:
- Markdown format with clear sections
- Section markers like `## Installation`, `## Usage`, `## Architecture`
- Placeholder text showing expected content type
- Based on amplifier's current README structure

**Example structure**:
```markdown
# {{project_name}}

{{project_tagline}}

## Overview
{{high_level_description}}

## Installation
{{installation_instructions}}

## Usage
{{usage_examples}}
...
```

### 2. Context Gatherer (~100 lines)
**File**: `context.py`

**What it does**: Reads hardcoded list of source files and returns content

**Why this sprint**: LLM needs codebase context

**Implementation notes**:
- Simple function: `gather_context() -> str`
- Hardcoded file paths for MVP test:
  - `README.md` (current README for reference)
  - `amplifier/cli.py` (main CLI code)
  - `pyproject.toml` (dependencies, metadata)
  - `AGENTS.md` (project guidelines)
- Reads files, concatenates with separators
- Returns single string with all context

**Hardcoded sources** (no CLI, no user input):
```python
SOURCES = [
    "README.md",
    "amplifier/cli.py",
    "pyproject.toml",
    "AGENTS.md"
]
```

### 3. LLM Generator (~150 lines)
**File**: `generator.py`

**What it does**: Sends template + context to Claude, returns generated doc

**Why this sprint**: Core value is LLM generation

**Implementation notes**:
- Use PydanticAI (already in project)
- Prompt structure:
  ```
  You are a technical writer generating documentation.

  Template (desired structure):
  {template_content}

  Source Context (codebase information):
  {gathered_context}

  Generate a complete README following the template structure,
  using information from the source context.
  ```
- Simple error handling (log and exit if LLM fails)
- Return raw markdown string

### 4. Main Script (~50 lines)
**File**: `generate_readme.py`

**What it does**: Orchestrates the flow, writes output file

**Why this sprint**: Need runnable end-to-end flow

**Implementation notes**:
- Loads template from file
- Calls `context.gather_context()`
- Calls `generator.generate_doc(template, context)`
- Writes to `README.generated.md`
- Prints "Done! Check README.generated.md"

**Simple flow**:
```python
def main():
    template = load_template("templates/readme-template.md")
    context = gather_context()
    generated = generate_doc(template, context)
    write_file("README.generated.md", generated)
    print("✓ Generated README.generated.md")
```

### 5. Tests (~100 lines)
**File**: `test_sprint1.py`

**TDD Approach - Write tests FIRST**:

**Day 1 - Template Loading**:
- 🔴 Write test: `test_load_template_exists()`
- 🟢 Implement: `load_template()` function
- 🔵 Refactor: Clean up error handling
- ✅ Commit (tests pass)

**Day 2 - Context Gathering**:
- 🔴 Write test: `test_gather_context_reads_files()`
- 🔴 Write test: `test_gather_context_format()`
- 🟢 Implement: `gather_context()` function
- 🔵 Refactor: Extract file reading helper
- ✅ Commit (tests pass)

**Day 2-3 - LLM Generation** (manual testing primary):
- 🔴 Write test: `test_generate_doc_returns_markdown()`
- 🟢 Implement: `generate_doc()` function
- 🔵 Refactor: Extract prompt building
- ✅ Manual test: Run full generation
- ✅ Commit (tests pass)

**Test coverage**:
- Template loading (with mock file)
- Context gathering (with test files)
- Generator returns non-empty string
- End-to-end integration test

**Manual Testing** (Primary validation):
- [ ] Run `python generate_readme.py`
- [ ] Read `README.generated.md`
- [ ] Compare to current README.md
- [ ] Evaluate quality (80%+ acceptable?)

---

## What Gets Punted (Deliberately Excluded)

### ❌ CLI Interface
- **Why**: Can run script directly (`python generate_readme.py`)
- **Reconsider**: Sprint 3 (after proving generation works)

### ❌ User-specified sources
- **Why**: Hardcoded list is faster for first test
- **Reconsider**: Sprint 4 (after CLI exists)

### ❌ Preview/diff workflow
- **Why**: Can manually compare files for first test
- **Reconsider**: Sprint 2 (after seeing generated quality)

### ❌ Template variables/customization
- **Why**: Static template is simpler
- **Reconsider**: Sprint 3 (when adding template selection)

### ❌ Multiple templates
- **Why**: Only need one for README test
- **Reconsider**: Sprint 3 (when making reusable)

### ❌ Error recovery/retry
- **Why**: Fail fast to learn issues
- **Reconsider**: Sprint 3 (after core flow proven)

### ❌ Logging/progress indicators
- **Why**: Simple print statements sufficient
- **Reconsider**: Sprint 3 (polish phase)

---

## Dependencies

**Requires from previous sprints**: None (first sprint!)

**Provides for future sprints**:
- Template format definition
- Context gathering approach
- LLM prompt structure
- Generated doc quality baseline

---

## Acceptance Criteria

### Must Have
- ✅ Script runs without errors
- ✅ Generates complete README file
- ✅ Output is valid markdown
- ✅ Content reflects amplifier project accurately
- ✅ Takes <5 minutes to run
- ✅ 80%+ of content is acceptable quality

### Nice to Have (Defer if time constrained)
- ❌ Perfect formatting match
- ❌ All sections 100% complete
- ❌ Zero manual editing needed

---

## Technical Approach

### TDD Red-Green-Refactor Cycle

**Every feature follows this pattern**:

1. **🔴 RED Phase** (~40% of time):
   - Write test that fails
   - Clarifies exactly what needs to be built
   - Example: `assert load_template("readme.md") contains expected sections`

2. **🟢 GREEN Phase** (~40% of time):
   - Write minimal code to pass test
   - Don't optimize yet
   - Example: Simple file read, no error handling yet

3. **🔵 REFACTOR Phase** (~20% of time):
   - Improve code quality
   - Tests still pass (protecting changes)
   - Example: Extract helpers, improve names, add error handling

4. **✅ COMMIT**:
   - All tests green = commit point
   - Never commit with failing tests

### LLM Integration

**Provider**: Claude (via PydanticAI)

**Prompt Engineering**:
```python
system_prompt = """
You are a technical documentation expert.
Generate clear, accurate documentation following the provided template structure.
Use information from the source code context provided.
Maintain professional tone appropriate for developer audience.
"""

user_prompt = f"""
Template Structure:
{template_content}

Source Context:
{gathered_context}

Generate a complete documentation file following the template structure.
"""
```

**Key decisions**:
- Use PydanticAI's `Agent` for structured generation
- Simple retry (3 attempts) for transient failures
- No streaming (return complete doc)
- No caching (optimize in Sprint 3 if needed)

### File Structure

```
doc-evergreen/
├── generate_readme.py       # Main script (~50 lines)
├── template.py              # Template loading (~50 lines)
├── context.py               # Context gathering (~100 lines)
├── generator.py             # LLM generation (~150 lines)
├── templates/
│   └── readme-template.md   # README structure (~50 lines)
└── tests/
    └── test_sprint1.py      # Unit tests (~100 lines)
```

**Total estimated**: ~500 lines of code + tests

---

## Implementation Order

### Day 1: Template + Context (Foundation)

**Morning** (4 hours):
- 🔴 Write test: Load template file
- 🟢 Implement: `template.load_template()`
- 🔵 Refactor: Error handling
- ✅ Commit

- 🔴 Write test: Gather context from files
- 🟢 Implement: `context.gather_context()` (hardcoded paths)
- 🔵 Refactor: File reading helper
- ✅ Commit

**Afternoon** (4 hours):
- Create `templates/readme-template.md`
- Test template loading with real file
- Test context gathering with amplifier files
- ✅ Commit (foundation complete)

### Day 2: LLM Generation (Core Value)

**Morning** (4 hours):
- 🔴 Write test: Generator returns markdown
- 🟢 Implement: `generator.generate_doc()` (basic)
- 🔵 Refactor: Prompt extraction
- ✅ Commit

- Setup PydanticAI integration
- Initial prompt engineering
- First generation test (may be poor quality)

**Afternoon** (4 hours):
- Iterate on prompt structure
- Test with real amplifier context
- Refine template if needed
- ✅ Commit (generation working)

### Day 3: Integration + Testing (Validation)

**Morning** (4 hours):
- 🔴 Write test: End-to-end integration
- 🟢 Implement: `generate_readme.py` main script
- Wire all components together
- ✅ Run full generation

**Afternoon** (4 hours):
- Manual quality evaluation
- Compare generated vs current README
- Document findings (what works, what needs improvement)
- 🔵 Refactor: Any obvious improvements
- ✅ Final commit

**End of day**: Demo generated README, discuss next sprint

---

## Testing Requirements

### TDD Workflow Per Feature

**Example: Context Gathering**

1. **🔴 RED - Write Test First**:
```python
def test_gather_context_includes_all_sources():
    context = gather_context()
    assert "amplifier/cli.py" in context
    assert "pyproject.toml" in context
    assert len(context) > 100  # Not empty
```

2. **🟢 GREEN - Minimal Implementation**:
```python
def gather_context():
    sources = ["README.md", "amplifier/cli.py", "pyproject.toml"]
    content = ""
    for path in sources:
        content += f"\n--- {path} ---\n"
        content += Path(path).read_text()
    return content
```

3. **🔵 REFACTOR - Improve Quality**:
```python
def gather_context():
    sources = get_default_sources()
    return "\n".join(read_source_file(s) for s in sources)

def read_source_file(path: str) -> str:
    return f"\n--- {path} ---\n{Path(path).read_text()}"
```

### Unit Tests (Write First)
- `test_load_template_success()` - Template loading works
- `test_load_template_missing()` - Error handling
- `test_gather_context_format()` - Context has expected structure
- `test_generator_returns_markdown()` - Generation produces string

### Integration Tests (Write First When Possible)
- `test_end_to_end_generation()` - Full script runs successfully
- `test_output_file_created()` - README.generated.md exists
- `test_output_is_valid_markdown()` - Can parse as markdown

### Manual Testing Checklist (After Automated Tests)
- [ ] Run `python generate_readme.py`
- [ ] File `README.generated.md` created
- [ ] Content is readable markdown
- [ ] Sections match template structure
- [ ] Information is accurate to amplifier project
- [ ] No obvious errors or hallucinations
- [ ] Quality evaluation: Is 80%+ acceptable?

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What You Learn

After this sprint ships, you discover:

1. **Generation Quality**
   - Is LLM output "good enough"?
   - What needs refinement (prompts, template, context)?
   - How much manual editing is needed?

2. **Context Needs**
   - Which source files are most valuable?
   - Is there too much/too little context?
   - What information is missing?

3. **Template Effectiveness**
   - Does template guide LLM well?
   - What sections work/don't work?
   - How much structure is needed?

4. **Time/Cost**
   - How long does generation take?
   - LLM token costs
   - Is <5 minutes achievable?

**These learnings directly inform**:
- Sprint 2: What needs review
- Sprint 3: Template improvements
- Sprint 4: Context selection needs

---

## Known Limitations (By Design)

1. **Hardcoded sources** - Only works for amplifier README
   - **Why acceptable**: First test only needs to work once
   - **Fix in**: Sprint 4 (context control)

2. **No review workflow** - Direct file write
   - **Why acceptable**: Manual comparison works for validation
   - **Fix in**: Sprint 2 (preview + diff)

3. **No CLI** - Direct script execution
   - **Why acceptable**: `python generate_readme.py` is fine for testing
   - **Fix in**: Sprint 3 (proper CLI)

4. **Single template** - No customization
   - **Why acceptable**: Only generating one doc type
   - **Fix in**: Sprint 3 (template selection)

5. **No error recovery** - Fails fast
   - **Why acceptable**: Want to see failures during testing
   - **Fix in**: Sprint 3 (after patterns emerge)

---

## Success Criteria

### Code Quality
- ✅ All tests pass (>80% coverage)
- ✅ TDD cycle followed for all features
- ✅ Clean, readable code (~500 lines total)
- ✅ Proper error handling (fail fast with clear messages)

### Generated Output Quality
- ✅ Valid markdown syntax
- ✅ All template sections present
- ✅ Accurate information about amplifier
- ✅ 80%+ content is acceptable without editing
- ✅ Professional tone and clarity

### Performance
- ✅ Runs in <5 minutes
- ✅ LLM responds successfully
- ✅ Files load without errors

### Learning Validation
- ✅ Can articulate what works well
- ✅ Can identify specific improvements needed
- ✅ Confident to proceed to Sprint 2

---

## Next Sprint Preview

After this sprint proves generation works, Sprint 2 adds the critical **review workflow**:

**The Need**: "I want to see what changed before overwriting my README"

**The Solution**:
- Generate to `.preview.md` file
- Show diff vs current file
- Prompt: Accept / Reject / Edit
- Only overwrite on explicit acceptance

**Why Next**: Now that we know generation quality (Sprint 1), we need confidence to replace real files safely.

---

## Quick Reference

**Key Files**:
- `generate_readme.py` - Run this
- `README.generated.md` - Check this

**Key Commands**:
```bash
# Run generation
python generate_readme.py

# Run tests (TDD)
pytest tests/test_sprint1.py -v

# Compare output
diff README.md README.generated.md
```

**Key Questions**:
- Does generated README accurately describe amplifier?
- Is quality acceptable (80%+ good)?
- What needs improvement?

---

**Remember**: This sprint is about **validation, not perfection**. Goal is to prove the concept works well enough to continue building.
