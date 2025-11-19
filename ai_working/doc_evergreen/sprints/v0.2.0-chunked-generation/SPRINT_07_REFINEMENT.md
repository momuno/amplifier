# Sprint 7: Refinement & Production Readiness (Buffer)

**Duration**: 3 days (Week 2, Days 5-7)
**Goal**: Handle edge cases, improve error messages, validate with real-world testing
**Value Delivered**: Production-ready chunked generation that handles real-world complexity gracefully

---

## Why This Sprint?

Sprint 6 delivered full v0.2.0 functionality. This sprint is **optional polish and robustness**:

**Question**: What breaks in real-world usage?

**Sprint 6 delivered working features** → **Sprint 7 makes them robust**:
- "Tool crashed on empty section" → Graceful handling
- "Deep nesting caused issues" → Support 5+ levels
- "Error message was cryptic" → Clear, actionable errors
- "Large docs felt slow" → Performance validation

**This sprint is the buffer between "works for demo" and "ready for production".**

---

## What You'll Have After This Sprint

A production-ready chunked generator that:
1. Handles edge cases gracefully (empty sections, missing prompts, etc.)
2. Supports deeply nested section hierarchies (5+ levels)
3. Provides clear, actionable error messages
4. Performs acceptably on large documents (10+ sections)
5. Has been tested with 2-3 real projects (not just doc_evergreen)
6. Ships with complete user documentation

**Test Coverage**: Real-world templates from actual projects

---

## Deliverables

### 1. Edge Case Handling (~200 lines)
**Files**: Various (extend Sprint 5-6 modules)

**What it does**: Handles corner cases without crashing

**Why this sprint**: Real-world usage reveals edge cases

**Edge Cases to Handle**:

**Empty Sections**:
```json
{
  "heading": "Placeholder",
  "prompt": "This section will be added later",
  "sources": []
}
```
- Behavior: Skip generation, insert placeholder comment
- Warning: "Section 'Placeholder' skipped (no sources)"

**Missing Prompts** (chunked mode):
```json
{
  "heading": "Features",
  "sources": ["src/*.py"]
  // No prompt field
}
```
- Behavior: Fail validation with clear error
- Error: "Section 'Features' requires 'prompt' field in chunked mode"
- Suggestion: "Add explicit prompt or use --mode single"

**Circular References** (rare but possible):
```json
{
  "heading": "A",
  "sections": [
    { "heading": "B", "sections": [{ "heading": "A" }] }
  ]
}
```
- Behavior: Detect cycle in validation
- Error: "Circular section reference detected: A → B → A"

**Very Deep Nesting** (5+ levels):
```json
{
  "heading": "Level 1",
  "sections": [{
    "heading": "Level 2",
    "sections": [{
      "heading": "Level 3",
      "sections": [...]
    }]
  }]
}
```
- Behavior: Support up to 10 levels (warning at 5+)
- Warning: "Deep nesting (6 levels) may affect readability"

**Large Source Sets** (100+ files):
```json
{
  "heading": "API Reference",
  "sources": ["src/**/*.py"]  // Matches 200 files
}
```
- Behavior: Process successfully with progress indication
- Display: "Using 200 Python files (2.4 MB, ~600k tokens)"
- Warning if exceeds LLM context: "Source size large, consider splitting"

**Implementation**:
```python
class EdgeCaseHandler:
    def validate_section(self, section: Section) -> ValidationResult:
        """Validate section for edge cases."""
        issues = []

        # Check for empty sources in chunked mode
        if not section.sources and not section.sections:
            issues.append(Warning(
                f"Section '{section.heading}' has no sources or subsections"
            ))

        # Check for missing prompt in chunked mode
        if self.mode == 'chunked' and not section.prompt:
            issues.append(Error(
                f"Section '{section.heading}' requires 'prompt' field",
                suggestion="Add prompt or use --mode single"
            ))

        # Check for deep nesting
        depth = self.calculate_depth(section)
        if depth > 5:
            issues.append(Warning(
                f"Section '{section.heading}' nested {depth} levels deep",
                suggestion="Consider flattening hierarchy"
            ))

        return ValidationResult(issues)

    def handle_empty_section(self, section: Section) -> str:
        """Generate placeholder for empty section."""
        return f"<!-- {section.heading}: No content generated (no sources) -->"
```

### 2. Enhanced Error Messages (~150 lines)
**File**: `doc_evergreen/core/error_messages.py` (NEW)

**What it does**: Provides clear, actionable error messages

**Why this sprint**: Good errors prevent user frustration

**Error Categories**:

**Validation Errors**:
```
❌ Template validation failed:

Section 'Installation' (line 23):
  ❌ No sources found matching "setup.py"

  Possible causes:
    • File doesn't exist in repository
    • Glob pattern is incorrect
    • File is in .gitignore

  Solutions:
    • Check if setup.py exists
    • Try absolute path: /path/to/setup.py
    • Use different glob: **/setup.py
    • Remove section if not needed
```

**Generation Errors**:
```
❌ Generation failed for section 'Features':

  LLM API Error: Rate limit exceeded (429)

  This usually means:
    • Too many requests in short time
    • Need to wait ~60 seconds

  What to do:
    • Wait a minute and retry
    • Use --interactive to control pacing
    • Check API key quota/limits
```

**Context Overflow Errors**:
```
⚠️  Warning: Context size approaching limit

Section 'API Reference':
  Sources: 150 files (1.8 MB, ~450k tokens)
  Context: 50k tokens (previous sections)
  Total: 500k tokens

  LLM context limit: 200k tokens

  This section may fail or be truncated.

  Suggestions:
    • Split section into smaller parts
    • Reduce source glob pattern
    • Use more specific file selection
```

**User Action Errors**:
```
❌ Editor failed to open

  Command: vim /tmp/section_edit_abc123.md
  Error: vim: command not found

  $EDITOR is set to 'vim' but not installed.

  Solutions:
    • Install vim: sudo apt install vim
    • Change $EDITOR: export EDITOR=nano
    • Use different action (accept/regenerate)
```

**Implementation**:
```python
class ErrorMessage:
    def __init__(
        self,
        title: str,
        details: str,
        causes: list[str],
        solutions: list[str]
    ):
        self.title = title
        self.details = details
        self.causes = causes
        self.solutions = solutions

    def format(self) -> str:
        """Format as user-friendly error message."""
        output = [f"❌ {self.title}", ""]

        if self.details:
            output.append(self.details)
            output.append("")

        if self.causes:
            output.append("Possible causes:")
            for cause in self.causes:
                output.append(f"  • {cause}")
            output.append("")

        if self.solutions:
            output.append("Solutions:")
            for solution in self.solutions:
                output.append(f"  • {solution}")

        return "\n".join(output)

# Predefined error templates
ERROR_TEMPLATES = {
    "missing_sources": ErrorMessage(
        title="No sources found for section '{section}'",
        details="Pattern '{pattern}' matched 0 files",
        causes=[
            "Files don't exist in repository",
            "Glob pattern is incorrect",
            "Files are in .gitignore"
        ],
        solutions=[
            "Check if files exist: ls {pattern}",
            "Try absolute paths instead of globs",
            "Verify .gitignore isn't excluding files"
        ]
    ),
    # ... more templates
}
```

### 3. Performance Optimization (~100 lines)
**Files**: Various (Sprint 5-6 modules)

**What it does**: Ensures acceptable performance on realistic workloads

**Why this sprint**: Large documents may reveal bottlenecks

**Optimization Areas**:

**Source Resolution Caching** (already in Sprint 5):
- Verify cache is working
- Measure cache hit rate
- Ensure no re-globbing during generation

**Context Size Management**:
- Limit context to N most recent sections (configurable)
- Default: 10 sections (~5k tokens typical)
- Flag: `--context-limit N`

**Parallel Summarization** (future optimization):
- Currently: Summarize sequentially after each section
- Future: Could parallelize if needed
- Defer unless <30s per section violated

**Progress Indication**:
```
Generating documentation (10 sections total)

[████████░░░░░░░░░░░░░░] 40% - Section 4 of 10
  Current: Installation
  Elapsed: 2m 15s
  Estimated remaining: 3m 20s
```

**Implementation**:
```python
class PerformanceMonitor:
    def __init__(self):
        self.section_times: list[float] = []
        self.start_time = time.time()

    def record_section_time(self, duration: float) -> None:
        """Record time for section generation."""
        self.section_times.append(duration)

    def estimate_remaining(self, sections_remaining: int) -> float:
        """Estimate time remaining based on average."""
        if not self.section_times:
            return 0
        avg_time = sum(self.section_times) / len(self.section_times)
        return avg_time * sections_remaining

    def display_progress(
        self,
        current: int,
        total: int,
        section_name: str
    ) -> None:
        """Display progress bar with estimates."""
        percent = (current / total) * 100
        elapsed = time.time() - self.start_time
        remaining = self.estimate_remaining(total - current)

        bar = self._progress_bar(percent)
        print(f"\n[{bar}] {percent:.0f}% - Section {current} of {total}")
        print(f"  Current: {section_name}")
        print(f"  Elapsed: {self._format_duration(elapsed)}")
        print(f"  Estimated remaining: {self._format_duration(remaining)}")
```

### 4. Real-World Testing (~0 lines of code, critical validation)
**What it does**: Tests with actual projects beyond doc_evergreen

**Why this sprint**: Validate assumptions with diverse templates

**Test Projects**:

1. **doc_evergreen's own README** (original test case)
   - Validates self-hosting capability
   - Tests typical CLI tool documentation

2. **A Python library project** (e.g., amplifier)
   - Tests API documentation generation
   - Complex nested structure
   - Multiple source types (code, config, docs)

3. **A simple project** (minimal template)
   - Tests edge of simplicity
   - 2-3 sections only
   - Validates basic workflow

**What to Validate**:
- Template parsing works for all
- Source resolution accurate
- Generated output quality acceptable
- Interactive mode usable
- Performance within targets
- Error messages helpful

**Document Findings**:
```markdown
# Real-World Testing Results

## Project 1: doc_evergreen README
- Template: 7 sections, 2 levels deep
- Sources: 12 Python files (15 KB)
- Generation time: 4m 32s (38s per section avg)
- Issues found:
  - ✅ None - worked perfectly
- Quality: 9/10 (minimal editing needed)

## Project 2: amplifier Documentation
- Template: 15 sections, 3 levels deep
- Sources: 45 Python files (120 KB)
- Generation time: 9m 18s (37s per section avg)
- Issues found:
  - ⚠️ One section had context overflow warning
  - Fixed by splitting sources
- Quality: 8/10 (some sections needed regeneration)

## Project 3: simple-cli README
- Template: 3 sections, 1 level
- Sources: 5 files (8 KB)
- Generation time: 1m 45s (35s per section avg)
- Issues found:
  - ✅ None - worked perfectly
- Quality: 9/10 (excellent for simple docs)

## Conclusions:
- Performance target met: <30s per section ✅
- Quality acceptable: 8-9/10 range ✅
- Edge cases handled: context overflow ✅
- User experience: smooth and predictable ✅
```

### 5. User Documentation (~300 lines markdown)
**File**: `doc_evergreen/docs/CHUNKED_GENERATION.md` (NEW)

**What it does**: Comprehensive guide for v0.2.0 chunked generation

**Why this sprint**: Users need guidance on new features

**Documentation Structure**:

```markdown
# Chunked Generation Guide

## Overview
What is chunked generation and when to use it.

## Quick Start
```bash
# Create template with section prompts
cat > template.json <<EOF
{
  "document": {
    "title": "My README",
    "sections": [
      {
        "heading": "Overview",
        "prompt": "High-level project description (2-3 paragraphs)",
        "sources": ["README.md", "pyproject.toml"]
      }
    ]
  }
}
EOF

# Generate with chunked mode
doc-update --mode chunked template.json
```

## Template Format
- Section-level prompts (explicit guidance to LLM)
- Source specification per section
- Nested sections support

## Modes
### Auto Mode (Default)
- No pauses, generates all sections
- Best for: CI/CD, batch processing

### Interactive Mode
- Pause after each section for review
- Accept / Regenerate / Edit / Quit
- Best for: First run, quality control

## Examples
### Example 1: Simple README
[Full template and walkthrough]

### Example 2: Complex Multi-Level Doc
[Full template and walkthrough]

### Example 3: API Documentation
[Full template and walkthrough]

## Tips & Best Practices
- Write explicit, focused prompts
- Specify appropriate sources per section
- Use context references ("Reference concepts from Overview")
- Start with interactive mode, switch to auto once confident

## Troubleshooting
### "No sources found"
[Solution]

### "Context overflow warning"
[Solution]

### "Generation too slow"
[Solution]

## Comparison: Single-shot vs Chunked
[Table comparing both modes with use cases]
```

### 6. Tests (~200 lines)
**Files**:
- `tests/test_edge_cases.py`
- `tests/test_error_messages.py`
- `tests/test_performance.py`

**TDD Approach - Write tests FIRST**:

**Day 1 - Edge Cases**:
- 🔴 Write test: `test_handles_empty_section()`
- 🔴 Write test: `test_handles_missing_prompt()`
- 🔴 Write test: `test_handles_deep_nesting()`
- 🟢 Implement: Edge case handlers
- 🔵 Refactor: Error recovery
- ✅ Commit (tests pass)

**Day 2 - Error Messages**:
- 🔴 Write test: `test_error_message_format()`
- 🔴 Write test: `test_helpful_suggestions()`
- 🟢 Implement: Enhanced errors
- 🔵 Refactor: Message templates
- ✅ Commit (tests pass)

**Day 3 - Performance**:
- 🔴 Write test: `test_large_document_performance()`
- 🟢 Implement: Progress monitoring
- Manual: Real-world testing
- Document: Findings and conclusions
- ✅ Final commit

**Test Coverage Target**: >80% for all new code (cumulative v0.2.0)

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What Gets Punted (Deliberately Excluded)

### ❌ Parallel Section Generation
- **Why**: Sequential is simpler, context flow is clearer
- **Reconsider**: v0.3.0 if performance becomes issue

### ❌ Advanced Caching (LLM responses)
- **Why**: Adds complexity, unclear benefit
- **Reconsider**: v0.3.0 after measuring duplicate generation frequency

### ❌ Template Validation IDE Extension
- **Why**: Out of scope, JSON schema validation sufficient
- **Reconsider**: v0.4.0 if requested by users

### ❌ Automatic Section Splitting (context overflow)
- **Why**: Manual split is simpler, user understands structure
- **Reconsider**: v0.3.0 if overflow is common

---

## Dependencies

**Requires from previous sprints**:
- All Sprint 5 components (core infrastructure)
- All Sprint 6 components (interactive control)
- Full v0.2.0 functionality working

**Provides for v0.3.0**:
- Production-ready foundation
- Known edge cases documented
- Performance baselines established
- User documentation complete

---

## Acceptance Criteria

### Must Have
- ✅ Edge cases handled gracefully (no crashes)
- ✅ Deep nesting supported (5+ levels)
- ✅ Error messages clear and actionable
- ✅ Performance acceptable (<30s per section)
- ✅ Real-world testing with 2-3 projects
- ✅ User documentation complete
- ✅ All tests pass (>80% cumulative coverage)

### Nice to Have (Defer if time constrained)
- ❌ Performance optimizations beyond baseline
- ❌ Additional example templates
- ❌ Video tutorial (defer to documentation)

---

## Technical Approach

### Edge Case Testing Strategy

**Approach**: Create synthetic "stress test" templates

**Example: Edge Case Template**:
```json
{
  "document": {
    "title": "Edge Case Test",
    "sections": [
      {
        "heading": "Empty Section",
        "prompt": "This will have no sources",
        "sources": []
      },
      {
        "heading": "Very Deep",
        "sections": [{
          "sections": [{
            "sections": [{
              "sections": [{
                "sections": [{
                  "heading": "Level 6",
                  "prompt": "Deep nesting test"
                }]
              }]
            }]
          }]
        }]
      },
      {
        "heading": "Large Source Set",
        "prompt": "All Python files",
        "sources": ["**/*.py"]
      }
    ]
  }
}
```

**Validation**: Tool should handle without crashing, provide warnings

### Performance Testing Approach

**Baseline Metrics** (from Sprint 5-6):
- Section generation: ~30s average
- Source validation: <10s
- Context summarization: ~5s per section

**Performance Test Template**:
```python
@pytest.mark.performance
async def test_large_document_performance():
    """Validate performance with realistic large document."""
    # Template: 15 sections, 3 levels deep
    # Sources: 50 files (~100 KB)
    template = load_test_template("large_doc.json")

    start = time.time()
    generator = ChunkedGenerator(template, resolver)
    result = await generator.generate()
    duration = time.time() - start

    # Performance targets
    assert duration < 600  # <10 minutes total

    # Per-section average
    avg_per_section = duration / 15
    assert avg_per_section < 40  # <40s average (allows variation)

    # Quality check
    assert len(result) > 5000  # Substantial output
    assert "##" in result  # Contains sections
```

### Error Message Design Principles

1. **Start with what's wrong** (not why)
2. **Explain possible causes** (educate)
3. **Provide actionable solutions** (empower)
4. **Use formatting for clarity** (bullets, spacing)
5. **Include context** (file, line, section name)

**Bad Error**:
```
Error: Validation failed
```

**Good Error**:
```
❌ Template validation failed:

Section 'Installation' (line 23):
  No sources found matching "setup.py"

Possible causes:
  • File doesn't exist
  • Incorrect glob pattern
  • File excluded by .gitignore

Solutions:
  • Check: ls setup.py
  • Try: **/setup.py
  • Or remove section if not needed
```

---

## Implementation Order

### Day 1: Edge Case Handling

**Morning** (4 hours):
- 🔴 Write test: Empty section handling
- 🔴 Write test: Missing prompt detection
- 🟢 Implement: Edge case validators
- 🔵 Refactor: Validation logic
- ✅ Commit

- 🔴 Write test: Deep nesting support
- 🟢 Implement: Depth tracking and warnings
- Test with deeply nested template
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: Large source set handling
- 🟢 Implement: Progress indication for large sets
- 🔵 Refactor: Source display
- ✅ Commit

- Create edge case test template
- Run full generation with edge cases
- Verify all handled gracefully
- ✅ Commit (edge cases complete)

### Day 2: Error Messages & Real-World Testing

**Morning** (4 hours):
- 🔴 Write test: Error message formatting
- 🟢 Implement: ErrorMessage class
- 🔵 Refactor: Message templates
- ✅ Commit

- 🔴 Write test: Error suggestions included
- 🟢 Implement: Context-specific suggestions
- Test various error scenarios
- ✅ Commit (error messages complete)

**Afternoon** (4 hours):
- Test with doc_evergreen README (template already exists)
- Test with second real project (amplifier or similar)
- Document findings (timing, quality, issues)
- Fix any issues discovered
- ✅ Commit

### Day 3: Performance & Documentation

**Morning** (4 hours):
- 🔴 Write test: Performance benchmarks
- 🟢 Implement: Progress monitoring
- 🔵 Refactor: Performance display
- ✅ Commit

- Run performance tests with large template
- Measure and document baseline metrics
- Verify <30s per section target
- ✅ Commit

**Afternoon** (4 hours):
- Write user documentation (CHUNKED_GENERATION.md)
- Include examples from real-world testing
- Add troubleshooting section
- Review all v0.2.0 documentation
- ✅ Final commit

**End of day**: v0.2.0 complete and ready for production use!

---

## Testing Requirements

### TDD Workflow Per Feature

**Example: Deep Nesting Support**

1. **🔴 RED - Write Test First**:
```python
def test_supports_deep_nesting():
    """Test generation with 6-level deep nesting."""
    template = create_deeply_nested_template(levels=6)
    generator = ChunkedGenerator(template, resolver)

    # Should succeed (not crash)
    result = await generator.generate()

    # Should contain all levels
    assert "######" in result  # H6 for level 6

    # Should have warned about depth
    assert "Deep nesting" in captured_warnings
```

2. **🟢 GREEN - Minimal Implementation**:
```python
def validate_nesting_depth(section: Section, current_depth: int = 0):
    if current_depth > 5:
        logger.warning(f"Deep nesting: {current_depth} levels")

    for subsection in section.sections:
        validate_nesting_depth(subsection, current_depth + 1)
```

3. **🔵 REFACTOR - Improve Quality**:
```python
class DepthValidator:
    MAX_DEPTH = 10  # Hard limit
    WARN_DEPTH = 5  # Warn threshold

    def validate_depth(
        self,
        section: Section,
        current_depth: int = 0,
        path: list[str] = []
    ) -> None:
        path.append(section.heading)

        if current_depth > self.MAX_DEPTH:
            raise ValidationError(
                f"Maximum nesting depth exceeded: {' → '.join(path)}",
                suggestion="Flatten hierarchy or split into multiple docs"
            )

        if current_depth > self.WARN_DEPTH:
            logger.warning(
                f"Deep nesting ({current_depth} levels): {' → '.join(path)}",
                suggestion="Consider flattening for readability"
            )

        for subsection in section.sections:
            self.validate_depth(subsection, current_depth + 1, path[:])
```

### Unit Tests (Write First)
- `test_handles_empty_section()` - Empty section graceful handling
- `test_missing_prompt_error()` - Clear error for missing prompt
- `test_deep_nesting_support()` - Support for 5+ levels
- `test_large_source_set()` - Handle 100+ files
- `test_error_message_format()` - Error formatting
- `test_error_suggestions()` - Actionable suggestions

### Integration Tests (Write First When Possible)
- `test_edge_case_template()` - Full generation with edge cases
- `test_real_world_template()` - Actual project template

### Performance Tests (Critical)
- `test_section_generation_time()` - <30s per section
- `test_large_document_total_time()` - <10min for 10 sections
- `test_source_validation_time()` - <10s validation

### Manual Testing Checklist (After Automated Tests)
- [ ] Run edge case template (empty, deep, large sources)
- [ ] Test with doc_evergreen README
- [ ] Test with second real project
- [ ] Verify error messages are helpful
- [ ] Check performance targets met
- [ ] Review all documentation complete
- [ ] Final quality check: Ready for production?

**Test Coverage Target**: >80% for all v0.2.0 code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What You Learn

After this sprint ships, you discover:

1. **Real-World Readiness**
   - What edge cases actually occur in practice?
   - Are error messages sufficient for self-service?
   - Do users get stuck anywhere?

2. **Performance Characteristics**
   - Is <30s per section achievable consistently?
   - What causes slowdowns (sources, LLM, context)?
   - Are optimizations needed?

3. **Documentation Effectiveness**
   - Can users onboard without help?
   - What questions still arise?
   - What examples are most useful?

4. **Production Confidence**
   - Ready to ship to users?
   - What concerns remain?
   - What should v0.3.0 prioritize?

**These learnings inform**:
- v0.3.0 roadmap (next features to add)
- Documentation improvements
- Support/FAQ content

---

## Known Limitations (By Design)

1. **No automatic section splitting** - User splits manually
   - **Why acceptable**: User understands structure better
   - **Reconsider**: v0.3.0 if context overflow common

2. **Sequential generation only** - No parallelization
   - **Why acceptable**: Context flow requires sequence
   - **Reconsider**: v0.3.0 if performance insufficient

3. **Basic performance monitoring** - No detailed profiling
   - **Why acceptable**: Meets performance targets
   - **Reconsider**: v0.3.0 if optimization needed

4. **Manual template creation** - No template generator
   - **Why acceptable**: User knows their doc structure
   - **Reconsider**: v0.4.0 if requested

---

## Success Criteria

### Production Readiness
- ✅ No known crashes or data loss scenarios
- ✅ Error messages enable self-service recovery
- ✅ Performance meets or exceeds targets
- ✅ Documentation complete and clear
- ✅ Real-world testing validates approach

### Code Quality
- ✅ All tests pass (>80% coverage cumulative)
- ✅ Edge cases handled gracefully
- ✅ Clean, maintainable code
- ✅ Good separation of concerns

### User Experience
- ✅ Smooth workflow (no surprises)
- ✅ Clear feedback at each step
- ✅ Helpful error messages
- ✅ Confidence to use in production

### v0.2.0 Complete
- ✅ All 5 features working (from feature scope)
- ✅ Bugs fixed (ISSUE-001, ISSUE-003)
- ✅ Ready to tag and release

---

## Release Checklist

Before tagging v0.2.0:

### Code
- [ ] All Sprint 5-7 tests pass
- [ ] No known bugs or crashes
- [ ] Performance targets met
- [ ] Code reviewed and clean

### Documentation
- [ ] CHUNKED_GENERATION.md complete
- [ ] CHANGELOG.md updated with v0.2.0 features
- [ ] README.md updated (if needed)
- [ ] Examples included

### Testing
- [ ] Real-world testing complete (2-3 projects)
- [ ] Edge cases validated
- [ ] Performance benchmarked
- [ ] User feedback incorporated

### Release
- [ ] Version bumped to 0.2.0
- [ ] Git tag created: v0.2.0
- [ ] Release notes written
- [ ] Migration guide (if needed)

---

## v0.3.0 Candidates

Based on Sprint 7 learnings, potential v0.3.0 features:

**High Priority** (if needed):
- Resume from partial generation
- Post-order validation and updates
- Automatic section splitting (context overflow)

**Medium Priority** (if requested):
- Batch review (every N sections)
- "Accept all remaining" option
- Side-by-side diff (regenerate)

**Low Priority** (nice to have):
- Template generator/wizard
- LLM provider choice (GPT-4, etc.)
- Parallel section generation

**Defer to User Feedback**: Real usage will reveal priorities

---

## Quick Reference

**Key Files**:
- `doc_evergreen/core/error_messages.py` - Enhanced errors
- `doc_evergreen/docs/CHUNKED_GENERATION.md` - User guide
- `tests/test_edge_cases.py` - Edge case validation
- `tests/test_performance.py` - Performance benchmarks

**Key Commands**:
```bash
# Run edge case test
doc-update --mode chunked tests/templates/edge_cases.json

# Performance test with verbose
doc-update --mode chunked --verbose tests/templates/large_doc.json

# Real-world test
doc-update --mode chunked --interactive doc_evergreen_readme.json
```

**Key Metrics**:
- Section generation: <30s target
- Total time (10 sections): <10min target
- Validation time: <10s target
- Test coverage: >80% cumulative

---

## Final Sprint Summary

**Sprint 7 completes v0.2.0** by:
1. Handling real-world edge cases
2. Providing clear error messages
3. Validating performance targets
4. Testing with actual projects
5. Completing user documentation

**After Sprint 7, v0.2.0 is production-ready.**

---

**Remember**: This sprint is about **confidence, not features**. Goal is production readiness, not new functionality.
