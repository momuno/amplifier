# Sprint 5: Chunked Core Infrastructure

**Duration**: 5 days (Week 1)
**Goal**: Implement section-by-section generation with context flow and source validation
**Value Delivered**: Working chunked generation that produces coherent documents with early failure on missing sources

---

## Why This Sprint?

This is the **most critical sprint for v0.2.0** because it validates the core hypothesis:

**Question**: Does section-by-section generation with explicit prompts improve control and predictability over single-shot?

**If YES** → Continue to Sprint 6 (add user controls)
**If NO** → Reconsider approach, possibly abandon chunked generation

**No point building interactive checkpoints or advanced visibility if chunked generation doesn't work.**

---

## What You'll Have After This Sprint

A working chunked generator that:
1. Parses templates with section-level prompts
2. Validates all sources BEFORE generation starts (fail early)
3. Generates sections sequentially in DFS order
4. Passes context summaries from earlier to later sections
5. Shows which sources are used for each section
6. Produces coherent complete documents

**Run it like**: `doc-update --mode chunked template.json`
**Output**: Complete document with natural section flow

---

## Deliverables

### 1. Extended Template Schema (~50 lines)
**File**: `doc_evergreen/core/template.py` (extend existing)

**What it does**: Add support for section-level `prompt` field

**Why this sprint**: Foundation for explicit prompts per section

**Implementation notes**:
- Add `prompt: str` field to section schema (required for chunked mode)
- Validate prompt exists when using chunked generation
- Backward compatible (single-shot mode doesn't require prompts)
- Support nested sections with prompts

**Schema Extension**:
```python
class Section:
    heading: str
    prompt: Optional[str] = None  # Required for chunked mode
    sources: list[str] = []
    sections: list[Section] = []
```

**Example Template** (from feature scope):
```json
{
  "document": {
    "title": "doc_evergreen README",
    "output": "README.md",
    "sections": [
      {
        "heading": "Overview",
        "prompt": "High-level overview (2-3 paragraphs). Emphasize living documentation.",
        "sources": ["doc_evergreen/doc-update.py", "README.md"]
      },
      {
        "heading": "Features",
        "prompt": "List key features. Reference Overview concepts.",
        "sources": ["doc_evergreen/**/*.py"]
      }
    ]
  }
}
```

### 2. Source Validator (~150 lines)
**File**: `doc_evergreen/core/source_validator.py` (NEW)

**What it does**: Validates all sources upfront before generation starts

**Why this sprint**: Fixes ISSUE-001 (prevents empty context errors)

**Implementation notes**:
- Traverse template tree, resolve sources for each section
- Check if any section has zero sources → fail with clear error
- Display resolved file paths per section (validation report)
- Cache resolved sources (don't re-glob for each section)
- Show file counts and sizes

**Key Functions**:
```python
def validate_all_sources(template: Template) -> ValidationResult:
    """Validate sources for all sections before generation.

    Returns:
        ValidationResult with success/failure and section details

    Raises:
        ValidationError if any section has no sources
    """

def display_validation_report(result: ValidationResult) -> None:
    """Display validation results to user with file counts."""
```

**Example Output**:
```
📋 Validating template sources...

Section: Overview
  Sources: ["doc_evergreen/doc-update.py", "README.md"]
  ✅ Found: doc_evergreen/doc-update.py (4.2 KB)
  ✅ Found: README.md (3.1 KB)

Section: Features
  Sources: ["doc_evergreen/**/*.py"]
  ✅ Found 8 files (12.4 KB total)

Section: Installation
  Sources: ["setup.py"]
  ❌ ERROR: No files found matching "setup.py"

❌ Validation failed: Section 'Installation' has no sources
Fix: Check glob pattern or add missing files
```

### 3. Context Manager (~200 lines)
**File**: `doc_evergreen/core/context_manager.py` (NEW)

**What it does**: Manages context flow between sections (summaries of earlier sections)

**Why this sprint**: Enables coherence across chunked generation

**Implementation notes**:
- Track generated sections and their content
- Generate concise summaries (3-5 sentences) for context
- Limit context size to prevent token overflow
- Optionally limit to N most recent sections

**Key Functions**:
```python
class ContextManager:
    def __init__(self, max_context_sections: int = 10):
        self.sections: list[GeneratedSection] = []
        self.max_context_sections = max_context_sections

    def add_section(self, heading: str, content: str) -> None:
        """Add a generated section and create summary."""

    def get_context_for_section(self, section_index: int) -> str:
        """Get context summary for a section (all previous sections)."""

    async def summarize_section(self, heading: str, content: str) -> str:
        """Generate concise summary of section (LLM call)."""
```

**Summary Format**:
```
Previous Sections Context:

## Overview
Summary: doc_evergreen maintains living documentation through template-based regeneration.
Focuses on reliability and explicitness over automation.

## Features
Summary: Key features include template system, source resolution, review workflow, and
chunked generation with section-level prompts.
```

### 4. Chunked Generator (~300 lines)
**File**: `doc_evergreen/core/chunked_generator.py` (NEW)

**What it does**: Generates document section-by-section in DFS order

**Why this sprint**: Core value of chunked generation

**Implementation notes**:
- DFS traversal of section tree
- Separate LLM call per section
- Pass sources + context to each generation
- Show progress (which section, which sources)
- Assemble complete document at end

**Key Functions**:
```python
class ChunkedGenerator:
    def __init__(self, template: Template, source_resolver: SourceResolver):
        self.template = template
        self.source_resolver = source_resolver
        self.context_manager = ContextManager()

    async def generate(self) -> str:
        """Generate complete document section-by-section.

        Returns:
            Complete markdown document
        """

    async def generate_section(
        self,
        section: Section,
        context: str,
        level: int
    ) -> str:
        """Generate single section with sources + context."""

    def traverse_dfs(self, sections: list[Section]) -> Iterator[Section]:
        """DFS traversal yielding sections in generation order."""
```

**Generation Flow**:
```python
async def generate(self) -> str:
    # 1. Validate sources (fail early)
    validation = validate_all_sources(self.template)
    if not validation.success:
        raise ValidationError(validation.errors)

    # 2. Generate sections in DFS order
    output = []
    for section in traverse_dfs(self.template.sections):
        # Get sources for this section
        sources = resolve_sources(section)

        # Get context from previous sections
        context = self.context_manager.get_context_for_section()

        # Generate section
        content = await self.generate_section(section, sources, context)

        # Add to output and context
        output.append(content)
        self.context_manager.add_section(section.heading, content)

    # 3. Assemble complete document
    return "\n\n".join(output)
```

**Progress Output**:
```
Generating section: Overview
  Using sources: doc_evergreen/doc-update.py, README.md (7.3 KB)
  Context: None (first section)
  [calling LLM...]
  ✅ Generated 342 words in 6.2s

Generating section: Features
  Using sources: 8 Python files (12.4 KB)
  Context: Summary of Overview (2 sentences)
  [calling LLM...]
  ✅ Generated 521 words in 9.1s
```

### 5. CLI Integration (~100 lines)
**File**: `doc_evergreen/doc-update.py` (extend existing)

**What it does**: Add `--mode` flag to choose single-shot vs chunked

**Why this sprint**: Need to run chunked generation from CLI

**Implementation notes**:
- Add `--mode` flag: `single` (default) or `chunked`
- Route to appropriate generator based on mode
- Validate template has prompts if using chunked mode
- Maintain backward compatibility

**CLI Changes**:
```python
@click.command()
@click.argument('template_path')
@click.option('--mode', type=click.Choice(['single', 'chunked']),
              default='single', help='Generation mode')
@click.option('--output', help='Override output path')
def update(template_path: str, mode: str, output: Optional[str]):
    """Generate/update documentation from template."""
    template = load_template(template_path)

    if mode == 'chunked':
        # Validate template has section prompts
        validate_section_prompts(template)
        generator = ChunkedGenerator(template, source_resolver)
    else:
        generator = Generator(template, source_resolver)

    result = await generator.generate()
    # ... review workflow
```

**Usage**:
```bash
# Single-shot mode (existing, default)
doc-update template.json

# Chunked mode (new)
doc-update --mode chunked template.json
```

### 6. Tests (~400 lines)
**Files**:
- `tests/test_source_validator.py`
- `tests/test_context_manager.py`
- `tests/test_chunked_generator.py`
- `tests/test_chunked_integration.py`

**TDD Approach - Write tests FIRST**:

**Day 1 - Template Schema**:
- 🔴 Write test: `test_section_with_prompt_parses()`
- 🟢 Implement: Section schema with `prompt` field
- 🔵 Refactor: Validation logic
- ✅ Commit (tests pass)

**Day 2 - Source Validation**:
- 🔴 Write test: `test_validate_finds_missing_sources()`
- 🔴 Write test: `test_validate_passes_with_all_sources()`
- 🟢 Implement: `SourceValidator.validate_all_sources()`
- 🔵 Refactor: Error reporting
- ✅ Commit (tests pass)

**Day 3 - Context Manager**:
- 🔴 Write test: `test_context_manager_adds_sections()`
- 🔴 Write test: `test_context_manager_limits_size()`
- 🟢 Implement: `ContextManager` class
- 🔵 Refactor: Summary generation
- ✅ Commit (tests pass)

**Day 4 - Chunked Generator**:
- 🔴 Write test: `test_dfs_traversal_order()`
- 🔴 Write test: `test_generate_section_with_context()`
- 🟢 Implement: `ChunkedGenerator` core
- 🔵 Refactor: Progress reporting
- ✅ Commit (tests pass)

**Day 5 - Integration**:
- 🔴 Write test: `test_end_to_end_chunked_generation()`
- 🟢 Implement: CLI integration
- 🔵 Refactor: Error handling
- ✅ Manual test: Full document generation
- ✅ Commit (tests pass)

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What Gets Punted (Deliberately Excluded)

### ❌ Interactive Review Checkpoints
- **Why**: Core generation must work first
- **Reconsider**: Sprint 6 (after chunked generation proven)

### ❌ Regenerate with Feedback
- **Why**: Basic generation first, steering later
- **Reconsider**: Sprint 6 (part of interactive mode)

### ❌ Advanced Source Visibility
- **Why**: Basic "show sources used" is enough for MVP
- **Reconsider**: Sprint 6 (enhanced display with token counts)

### ❌ Resume from Checkpoint
- **Why**: Full generation fast enough (<10min)
- **Reconsider**: v0.3.0 if generation becomes slow

### ❌ Post-order Validation
- **Why**: Forward-only is simpler, tests core assumption
- **Reconsider**: v0.3.0 if inconsistencies are common

### ❌ Dynamic Section Discovery
- **Why**: Static templates test core value first
- **Reconsider**: v0.4.0 if users add sections manually often

---

## Dependencies

**Requires from previous sprints**:
- Template parser (`template.py` from Sprint 1)
- Source resolver (`source_resolver.py` from Sprint 4)
- Review workflow (`review.py` from Sprint 2)
- CLI framework (`doc-update.py` from Sprint 3)

**Provides for future sprints**:
- `ChunkedGenerator` for Sprint 6 to extend
- `ContextManager` for Sprint 6 to use
- `SourceValidator` for Sprint 6 to enhance
- Template with prompts format for Sprint 6

---

## Acceptance Criteria

### Must Have
- ✅ Template parser accepts section-level `prompt` field
- ✅ Source validation fails early if any section has no sources
- ✅ Sections generated in correct DFS order
- ✅ Context flows from earlier to later sections
- ✅ Complete document is coherent end-to-end
- ✅ Sources displayed during generation (basic visibility)
- ✅ CLI flag switches between single-shot and chunked
- ✅ All tests pass (>80% coverage)

### Nice to Have (Defer if time constrained)
- ❌ Token count display (save for Sprint 6)
- ❌ Progress percentage (basic "Section N of M" is enough)
- ❌ Colored output (plain text fine for MVP)

---

## Technical Approach

### TDD Red-Green-Refactor Cycle

**Every feature follows this pattern**:

1. **🔴 RED Phase** (~40% of time):
   - Write test that fails
   - Clarifies exactly what needs to be built
   - Example: `assert validate_sources(template) raises ValidationError when missing`

2. **🟢 GREEN Phase** (~40% of time):
   - Write minimal code to pass test
   - Don't optimize yet
   - Example: Simple source check, basic error message

3. **🔵 REFACTOR Phase** (~20% of time):
   - Improve code quality
   - Tests still pass (protecting changes)
   - Example: Extract helpers, improve error messages, add progress display

4. **✅ COMMIT**:
   - All tests green = commit point
   - Never commit with failing tests

### DFS Traversal Strategy

**Why DFS (depth-first):**
- Natural reading order for nested sections
- Complete subtrees before moving to siblings
- Simpler than breadth-first for context management

**Example Tree**:
```
Introduction
Features
  ├── Core Features
  └── Advanced Features
Installation
  ├── Prerequisites
  └── Steps
```

**DFS Order**:
1. Introduction
2. Features
3. Core Features
4. Advanced Features
5. Installation
6. Prerequisites
7. Steps

**Implementation**:
```python
def traverse_dfs(sections: list[Section], level: int = 0):
    for section in sections:
        yield (section, level)
        if section.sections:
            yield from traverse_dfs(section.sections, level + 1)
```

### Context Summarization

**Approach**: Use LLM to summarize each section for context

**Prompt**:
```
Summarize this section in 2-3 sentences for use as context in later sections.
Focus on key points and concepts introduced.

Section Heading: {heading}
Section Content: {content}

Concise Summary:
```

**Advantages**:
- Self-referential (same LLM used for generation)
- Captures semantic meaning, not just text truncation
- Adaptable to section length and complexity

**Fallback**: If summary fails, use first 500 characters

### Source Resolution Caching

**Problem**: Resolving glob patterns is expensive (filesystem I/O)

**Solution**: Cache resolved sources in validation phase
```python
class SourceCache:
    def __init__(self):
        self._cache: dict[str, list[Path]] = {}

    def resolve(self, pattern: str) -> list[Path]:
        if pattern not in self._cache:
            self._cache[pattern] = glob_files(pattern)
        return self._cache[pattern]
```

**Benefits**:
- Resolve each glob pattern once
- Validation phase populates cache
- Generation phase uses cache (no re-globbing)

---

## Implementation Order

### Day 1: Template Schema + Validation Infrastructure

**Morning** (4 hours):
- 🔴 Write test: Section schema with prompts
- 🟢 Implement: Extend `Section` class with `prompt` field
- 🔵 Refactor: Validation logic
- ✅ Commit

- 🔴 Write test: Validate section prompts exist (chunked mode)
- 🟢 Implement: Prompt validation
- 🔵 Refactor: Error messages
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: Source validator finds missing sources
- 🟢 Implement: Basic source validation logic
- 🔵 Refactor: Validation report display
- ✅ Commit

- Create example template with section prompts
- Test validation with real files
- ✅ Commit (validation working)

### Day 2: Source Validator + Context Manager Foundation

**Morning** (4 hours):
- 🔴 Write test: Validator caches resolved sources
- 🟢 Implement: Source caching in validator
- 🔵 Refactor: Cache interface
- ✅ Commit

- 🔴 Write test: Display validation report
- 🟢 Implement: Formatted output with file counts
- Test with doc_evergreen's own files
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: ContextManager adds sections
- 🟢 Implement: Basic context tracking
- 🔵 Refactor: Data structures
- ✅ Commit

- 🔴 Write test: Context size limiting
- 🟢 Implement: Max sections limit
- ✅ Commit (context manager basic functionality)

### Day 3: Context Summarization + DFS Traversal

**Morning** (4 hours):
- 🔴 Write test: Generate section summary
- 🟢 Implement: LLM-based summarization
- 🔵 Refactor: Prompt for summaries
- ✅ Commit

- 🔴 Write test: Context formatting for prompts
- 🟢 Implement: Format context from summaries
- Test summary quality with real sections
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: DFS traversal order
- 🟢 Implement: Recursive DFS iterator
- 🔵 Refactor: Clean traversal logic
- ✅ Commit

- Test DFS with nested section trees
- Verify order matches expectations
- ✅ Commit (DFS working)

### Day 4: Chunked Generator Core

**Morning** (4 hours):
- 🔴 Write test: Generate single section with sources
- 🟢 Implement: Basic section generation
- 🔵 Refactor: LLM prompt structure
- ✅ Commit

- 🔴 Write test: Generate section with context
- 🟢 Implement: Context passing to LLM
- Test section generation quality
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: Complete document assembly
- 🟢 Implement: Full generate() flow
- 🔵 Refactor: Progress reporting
- ✅ Commit

- Wire together: validation → generation → assembly
- Test with multi-section template
- ✅ Commit (chunked generator working)

### Day 5: CLI Integration + End-to-End Testing

**Morning** (4 hours):
- 🔴 Write test: CLI --mode flag
- 🟢 Implement: Mode selection in CLI
- 🔵 Refactor: Generator factory
- ✅ Commit

- 🔴 Write test: End-to-end chunked generation
- 🟢 Wire CLI → ChunkedGenerator → Review
- Test full workflow
- ✅ Commit

**Afternoon** (4 hours):
- Manual quality evaluation with doc_evergreen README
- Compare chunked vs single-shot output
- Document findings (coherence, quality, issues)
- 🔵 Refactor: Any obvious improvements
- ✅ Final commit

**End of day**: Demo chunked generation, discuss Sprint 6

---

## Testing Requirements

### TDD Workflow Per Feature

**Example: Source Validator**

1. **🔴 RED - Write Test First**:
```python
def test_validate_fails_on_missing_sources():
    template = Template(sections=[
        Section(heading="Test", prompt="Test prompt", sources=["nonexistent.py"])
    ])
    validator = SourceValidator()

    with pytest.raises(ValidationError) as exc:
        validator.validate_all_sources(template)

    assert "no sources" in str(exc.value).lower()
    assert "Test" in str(exc.value)
```

2. **🟢 GREEN - Minimal Implementation**:
```python
def validate_all_sources(self, template: Template) -> None:
    for section in traverse_sections(template):
        sources = self.resolve_sources(section.sources)
        if not sources:
            raise ValidationError(f"Section '{section.heading}' has no sources")
```

3. **🔵 REFACTOR - Improve Quality**:
```python
def validate_all_sources(self, template: Template) -> ValidationResult:
    result = ValidationResult()
    for section in traverse_sections(template):
        resolved = self.resolve_and_cache(section.sources)
        if not resolved:
            result.add_error(
                section=section.heading,
                message=f"No files found matching: {section.sources}",
                suggestion="Check glob pattern or add missing files"
            )
    return result
```

### Unit Tests (Write First)
- `test_section_schema_with_prompt()` - Template parsing
- `test_validate_all_sources_success()` - Validation passes
- `test_validate_all_sources_failure()` - Validation fails appropriately
- `test_context_manager_adds_section()` - Context tracking
- `test_context_manager_summarizes()` - Summary generation
- `test_dfs_traversal_order()` - DFS iteration
- `test_generate_section_with_context()` - Single section generation
- `test_chunked_generate_complete()` - Full document generation

### Integration Tests (Write First When Possible)
- `test_end_to_end_chunked_generation()` - Full workflow
- `test_cli_mode_selection()` - CLI routing
- `test_validation_before_generation()` - Fail early behavior

### Manual Testing Checklist (After Automated Tests)
- [ ] Run `doc-update --mode chunked template.json`
- [ ] Validation phase shows all sections and sources
- [ ] Generation shows progress for each section
- [ ] Complete document is created
- [ ] Sections reference each other appropriately
- [ ] Quality evaluation: Is output coherent?
- [ ] Compare to single-shot: Is chunked better?

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What You Learn

After this sprint ships, you discover:

1. **Chunked Generation Quality**
   - Is section-by-section output more coherent?
   - Do explicit prompts provide sufficient guardrails?
   - How does it compare to single-shot?

2. **Context Flow Effectiveness**
   - Do later sections reference earlier sections appropriately?
   - Is context size manageable (no token overflow)?
   - Are summaries adequate or do we need more detail?

3. **Source Validation Value**
   - Does fail-early prevent common errors?
   - Is validation report clear and helpful?
   - Are error messages actionable?

4. **Performance Characteristics**
   - How long does each section take?
   - Is <30s per section achievable?
   - Is total time acceptable (<10min for 10 sections)?

5. **User Experience Needs**
   - Where do users want visibility?
   - Where do users want control?
   - What's missing for confidence?

**These learnings directly inform**:
- Sprint 6: Where to add interactive checkpoints
- Sprint 6: What visibility to enhance
- Sprint 7: What edge cases to handle

---

## Known Limitations (By Design)

1. **No interactive checkpoints** - Auto mode only
   - **Why acceptable**: Need to validate core generation first
   - **Fix in**: Sprint 6 (after core proven)

2. **Basic source visibility** - Simple file list
   - **Why acceptable**: Sufficient to validate approach
   - **Fix in**: Sprint 6 (add token counts, sizes)

3. **No regeneration with feedback** - Generate once only
   - **Why acceptable**: Testing core quality first
   - **Fix in**: Sprint 6 (interactive mode)

4. **Forward-only generation** - No backtracking or updates
   - **Why acceptable**: Simpler state management, faster
   - **Fix in**: v0.3.0 if needed (after learning from usage)

5. **No resume capability** - Must generate full doc
   - **Why acceptable**: Generation fast enough (<10min)
   - **Fix in**: v0.3.0 if generation becomes slow

---

## Success Criteria

### Code Quality
- ✅ All tests pass (>80% coverage)
- ✅ TDD cycle followed for all features
- ✅ Clean, readable code (~1,200 lines total)
- ✅ Proper error handling (fail fast with clear messages)

### Generated Output Quality
- ✅ Complete document assembled correctly
- ✅ Sections generated in correct DFS order
- ✅ Later sections reference earlier sections appropriately
- ✅ Document reads coherently end-to-end
- ✅ Quality comparable to or better than single-shot

### Validation & Visibility
- ✅ Tool fails early if sources missing
- ✅ Validation report clear and actionable
- ✅ Sources displayed during generation
- ✅ Progress visible for each section

### Performance
- ✅ Validation completes in <10s
- ✅ Section generation in <30s each
- ✅ Total time <10min for 10-section doc

### Learning Validation
- ✅ Can articulate what works well
- ✅ Can identify areas for Sprint 6 improvement
- ✅ Confident chunked approach is valuable

---

## Next Sprint Preview

After this sprint proves chunked generation works, Sprint 6 adds **user control**:

**The Need**: "I want to review sections as they're generated and steer output"

**The Solution**:
- Interactive mode (`--interactive` flag)
- Review checkpoints after each section
- Accept / Regenerate with feedback / Edit / Quit
- Enhanced source visibility (token counts, sizes)

**Why Next**: Now that we know chunked generation produces coherent output (Sprint 5), we need fine-grained control over that output.

---

## Quick Reference

**Key Files**:
- `doc_evergreen/core/source_validator.py` - Validates sources
- `doc_evergreen/core/context_manager.py` - Manages context flow
- `doc_evergreen/core/chunked_generator.py` - Section-by-section generation
- `doc_evergreen/doc-update.py` - CLI with --mode flag

**Key Commands**:
```bash
# Run chunked generation
doc-update --mode chunked template.json

# Run tests (TDD)
pytest tests/test_chunked_generator.py -v

# Compare modes
doc-update --mode single template.json  # Old way
doc-update --mode chunked template.json  # New way
```

**Key Questions**:
- Is chunked output more coherent than single-shot?
- Do explicit prompts provide sufficient control?
- Where do users need more visibility or control?

---

**Remember**: This sprint is about **validation, not perfection**. Goal is to prove chunked generation improves control and predictability over single-shot.
