# ISSUE-009: Single-Shot Mode Not Implemented - Both Modes Use Chunked Generator

**Status:** Open
**Priority:** High
**Type:** Bug (Missing Feature)
**Created:** 2025-11-19
**Updated:** 2025-11-19

---

## Description

The CLI advertises two generation modes (`--mode single` and `--mode chunked`), but single-shot mode is not actually implemented. Both modes fall back to using `ChunkedGenerator`, making the `--mode` option misleading and non-functional.

## User Feedback

> "i see the 2 different modes, chunked and single. i'd like to confirm how each works."

**Investigation revealed:** The modes don't actually work differently because `single_generator.py` doesn't exist.

## Reproduction Steps

1. Run: `doc-update --mode single template.json`
2. Run: `doc-update --mode chunked template.json`
3. Observe: Both produce identical behavior (section-by-section generation)
4. Check source code: `single_generator.py` doesn't exist
5. See fallback code in `cli.py` lines 16-19

**Frequency:** Always - both modes always use chunked generator

## Expected Behavior

**Single-Shot Mode Should:**
1. Have its own implementation in `single_generator.py`
2. Generate entire document in one LLM call
3. Be faster than chunked mode
4. Use different prompt structure (all sections at once)
5. Not build inter-section context

**Chunked Mode Should:**
1. Use `ChunkedGenerator` (already works correctly)
2. Generate section-by-section
3. Build context between sections
4. Make N LLM calls for N sections

**Currently:**
Both modes → `ChunkedGenerator` → section-by-section generation

## Actual Behavior

**CLI code (lines 16-19):**
```python
try:
    from doc_evergreen.single_generator import Generator
except ImportError:
    Generator = ChunkedGenerator  # Falls back to chunked!
```

**What happens:**
1. CLI tries to import `single_generator.Generator`
2. Import fails (file doesn't exist)
3. Falls back to `ChunkedGenerator`
4. **Both modes use chunked generation**

**Result:**
- `--mode single` is misleading (doesn't do single-shot)
- `--mode chunked` works but is the only option
- No performance benefit from choosing "single"
- Users think they're getting different behavior but aren't

## Root Cause

**Location:** Missing file: `doc_evergreen/single_generator.py`

**Technical Explanation:**

The project has:
- ✅ `ChunkedGenerator` class (`chunked_generator.py`)
- ✅ CLI routing to different generators based on mode
- ❌ **No `single_generator.py` file**
- ❌ **No `Generator` class for single-shot**

**Historical context:**
- `generator.py` exists with basic single-shot logic
- But CLI imports from `single_generator` not `generator`
- Possibly renamed/refactored and import wasn't updated
- Or single-shot mode was planned but never implemented

## Impact Analysis

**Severity:** High - Core feature advertised but not working

**User Impact:**
- False expectation of performance difference
- Can't actually use single-shot generation
- Mode selection is meaningless
- Wastes time thinking about which mode to use

**Workaround:**
None - both modes do the same thing regardless of selection

## Acceptance Criteria

To consider this issue resolved:

**Option 1: Implement Single-Shot Generator**
- [ ] Create `doc_evergreen/single_generator.py`
- [ ] Implement `Generator` class that:
  - [ ] Takes entire template at once
  - [ ] Builds single combined prompt
  - [ ] Makes one LLM call
  - [ ] Returns complete document
- [ ] Ensure CLI correctly routes to it
- [ ] Add tests for single-shot mode
- [ ] Verify performance difference (should be faster)
- [ ] Update documentation (ISSUE-008)

**Option 2: Remove Single-Shot Mode**
- [ ] Remove `--mode` option from CLI
- [ ] Remove import fallback code
- [ ] Update help text to remove mode references
- [ ] Document that only chunked mode exists
- [ ] Consider adding single-shot in future version

**Recommendation:** Option 1 (implement single-shot) because:
- Feature is already advertised in help text
- CLI code expects it to exist
- Users would benefit from faster single-call option
- `generator.py` already has basic implementation to build from

## Related Issues

- Blocks: ISSUE-008 - Can't document mode differences until both modes work
- Related to: ISSUE-007 - Single-shot mode would need different progress feedback

## Technical Notes

**Proposed Solution: Implement Single-Shot Generator**

**1. Create `single_generator.py` based on existing `generator.py`:**

```python
"""Single-shot document generator - generates entire document in one LLM call."""

from pathlib import Path
from pydantic_ai import Agent
from doc_evergreen.core.template_schema import Template
from doc_evergreen.core.source_validator import validate_all_sources

class Generator:
    """Generate documentation in single LLM call."""

    def __init__(self, template: Template, base_dir: Path, model: str | None = None):
        self.template = template
        self.base_dir = base_dir
        self.model = model or "anthropic:claude-sonnet-4-5-20250929"

    async def generate(self) -> str:
        """Generate complete document in one LLM call.

        Returns:
            Complete markdown document
        """
        # 1. Validate sources
        validation = validate_all_sources(self.template, self.base_dir)
        if not validation.valid:
            raise ValueError(f"Source validation failed: {validation.errors}")

        # 2. Build combined prompt from all sections
        combined_prompt = self._build_combined_prompt()

        # 3. Gather all source content
        all_sources = self._gather_all_sources(validation)

        # 4. Create user prompt
        user_prompt = f"""Generate this complete documentation:

{combined_prompt}

## Source Materials
{all_sources}

Generate the complete markdown document."""

        # 5. Call LLM once
        agent = Agent(self.model, system_prompt="You are a technical documentation writer.")
        result = await agent.run(user_prompt)

        return result.data

    def _build_combined_prompt(self) -> str:
        """Build combined prompt from all sections."""
        # Walk sections and build outline
        parts = [f"# {self.template.document.title}\n"]
        # ... build section structure ...
        return "\n\n".join(parts)

    def _gather_all_sources(self, validation) -> str:
        """Gather content from all sources."""
        # Combine all section sources
        # ... implementation ...
```

**2. Update CLI import to match actual filename:**

```python
# cli.py - Option A: Keep current import
from doc_evergreen.single_generator import Generator

# cli.py - Option B: Rename generator.py to single_generator.py
# (move existing generator.py to single_generator.py)
```

**3. Add tests:**

```python
# tests/test_single_generator.py
async def test_single_shot_generates_complete_doc():
    template = create_test_template()
    generator = Generator(template, base_dir)
    result = await generator.generate()

    assert "# Document Title" in result
    assert all section appears in result
```

**Alternative Implementation:**
- Could refactor existing `generator.py` and rename to `single_generator.py`
- Already has single-shot logic that could be adapted
- Would need updates for new validation system

**Implementation Complexity:** Medium
- Can adapt existing `generator.py` code
- Need to integrate with new validation system
- Need to test thoroughly

**Estimated Effort:** 6-8 hours
- 3-4 hours: Implement single-shot generator
- 2-3 hours: Testing and validation
- 1 hour: Integration and documentation

## Testing Notes

**Test Cases Needed:**
- [ ] Single-shot mode generates complete document in one call
- [ ] Chunked mode still works (unchanged)
- [ ] Single-shot is faster than chunked (performance test)
- [ ] Both modes produce equivalent content quality
- [ ] Mode routing works correctly (no fallback to chunked)
- [ ] Validation works for both modes

**Regression Risk:** Low to Medium
- New code path, shouldn't affect chunked mode
- Need to ensure CLI routing doesn't break

## Sprint Assignment

**Assigned to:** TBD (Feature Implementation)
**Rationale:**
- Important feature but requires implementation work
- v0.3.0 focused on critical UX/documentation issues
- Can be deferred if chunked mode meets needs
- Should be implemented before 1.0 release

## Comments / Updates

### 2025-11-19
Issue discovered during code investigation. User asked about mode differences and investigation revealed single-shot mode doesn't actually exist. Both modes fall back to chunked generator. This is a significant feature gap where advertised functionality doesn't work.

**Decision needed:** Implement single-shot mode OR remove the option and document chunked-only? Recommend implementing single-shot for completeness and performance benefits.
