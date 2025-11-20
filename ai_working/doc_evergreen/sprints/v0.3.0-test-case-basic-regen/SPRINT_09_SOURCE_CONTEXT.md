# Sprint 9: Progressive Enhancement & Source Clarity

**Duration:** 3 days
**Goal:** Add progress feedback and clarify source gathering
**Value Delivered:** Users see what's happening during generation and understand how sources work

---

## Why This Sprint?

Sprint 8 provides core regeneration, but users need visibility into what's happening during generation (Issue #007) and clarity about how sources work (Issue #006). These UX improvements make the tool feel more reliable and understandable.

---

## Deliverables

### 1. Progress Feedback System (~120 lines + ~60 lines tests)

**What it does:**
- Shows real-time progress during generation
- Displays section being generated
- Shows source files being used
- Includes timing information
- Resolves **ISSUE-007** (no progress feedback)

**Why this sprint:**
- Makes tool feel responsive (not hanging)
- Teaches users what's happening
- Easy integration with existing ChunkedGenerator

**Implementation notes:**
```python
# Add progress callback to ChunkedGenerator
class ChunkedGenerator:
    async def generate(
        self,
        progress_callback: Callable[[str], None] | None = None
    ) -> str:
        """Generate with optional progress feedback."""
        for idx, section in enumerate(sections, 1):
            if progress_callback:
                progress_callback(
                    f"[{idx}/{total}] Generating: {section.heading}\n"
                    f"      Sources: {', '.join(sources)} ({len(sources)} files)\n"
                )

            # ... generate section ...

            if progress_callback:
                progress_callback(f"      ✓ Complete ({elapsed:.1f}s)\n")

# Use in regen-doc command:
def progress_callback(msg: str):
    click.echo(msg, nl=False)

result = await generator.generate(progress_callback=progress_callback)
```

**Output example:**
```
Loading template: examples/simple.json
Validating sources...
✓ Found 4 source files

Generating documentation (chunked mode)...

[1/2] Generating: Overview
      Sources: README.md, src/main.py (2 files)
      ✓ Complete (8.3s)

[2/2] Generating: Installation
      Sources: setup.py, requirements.txt (2 files)
      ✓ Complete (5.7s)

✓ Generated new content (14.0s total)
```

### 2. Source Gathering Documentation (~100 lines markdown)

**What it does:**
- Expands TEMPLATES.md with source gathering section
- Explains per-section sources clearly
- Shows glob pattern examples
- Documents source resolution behavior
- Resolves **ISSUE-006** (sources template vs CLI)

**Why this sprint:**
- Major source of user confusion
- Low effort, high impact
- Natural extension of Sprint 8 docs

**Content structure:**
```markdown
# Source Specification

## How Sources Work

Sources are specified per-section in your template:

```json
{
  "heading": "API Documentation",
  "sources": ["src/api/*.py", "src/models.py"]
}
```

## Glob Patterns

Supported patterns:
- `src/*.py` - All .py files in src/
- `src/**/*.py` - All .py files in src/ and subdirectories
- `README.md` - Specific file

## Resolution

Sources are resolved relative to template location.

## Common Patterns

(Examples of typical source specifications)
```

### 3. Enhanced Error Messages (~80 lines)

**What it does:**
- Improves error messages for common failures
- Adds specific guidance on how to fix
- Points to relevant documentation
- Partially addresses Issue #006

**Why this sprint:**
- Users getting stuck on errors
- Small changes, big UX impact
- Builds on Sprint 8 foundation

**Examples:**
```python
# Before:
raise ValueError("Section 'Overview' has no sources")

# After:
raise ValueError(
    f"Section '{section.heading}' has no sources.\n"
    f"Fix: Add 'sources' field to section in template:\n"
    f'  "sources": ["path/to/file.py", "docs/*.md"]\n'
    f"See: TEMPLATES.md#source-specification"
)
```

### 4. Iterative Refinement Workflow (~150 lines + ~100 lines tests)

**What it does:**
- After applying changes, offers to regenerate
- Allows iterative improvement without restarting
- Tracks iteration count
- Natural workflow for refinement

**Why this sprint:**
- Users often want to tweak and regenerate
- Reduces friction in workflow
- Teaches by showing multiple examples

**Implementation notes:**
```python
# After applying changes:
click.echo(f"\n✓ Changes applied to {output_path}")

while True:
    if not click.confirm("Regenerate with updated sources?"):
        break

    # Generate again
    new_content = await generator.generate(progress_callback)
    has_changes, diff = detect_changes(output_path, new_content)

    if not has_changes:
        click.echo("No changes detected.")
        break

    show_diff(diff)
    if click.confirm("Apply these changes?"):
        output_path.write_text(new_content)
        iteration += 1
    else:
        break

click.echo(f"\nCompleted {iteration} iteration(s)")
```

---

## What Gets Punted

- **Fancy spinner animations** - Simple progress text sufficient
- **Progress percentage** - Section N/M sufficient
- **Time estimates** - Actual timing better than predictions
- **Verbose mode flag** - One level of detail sufficient for now

---

## Dependencies

**Requires from Sprint 8:**
- Working regen-doc command
- ChunkedGenerator
- Change detection
- Template documentation base

**Provides for Sprint 10:**
- Complete user experience
- Comprehensive documentation
- Resolved user confusion points

---

## Acceptance Criteria

### Must Have
- ✅ Progress feedback shows during generation
- ✅ Section name and sources displayed
- ✅ Timing information included
- ✅ Source documentation clear and comprehensive
- ✅ Error messages actionable and helpful
- ✅ Iterative workflow works smoothly

### Nice to Have (Defer if time constrained)
- ❌ Colored progress output
- ❌ Estimated time remaining
- ❌ Resource usage stats

---

## Testing Requirements

**TDD Approach:** Follow red-green-refactor cycle for all features

**Unit Tests (Write First):**
- Progress callback receives correct messages
- Timing measurements accurate
- Iteration tracking works
- Error messages format correctly

**Integration Tests (Write First):**
- Progress appears during real generation
- Iterative workflow completes correctly
- Error messages show in actual failure scenarios

**Manual Testing (After Automated Tests Pass):**
- [ ] Generate large doc and watch progress
- [ ] Trigger errors and verify helpful messages
- [ ] Test iterative refinement workflow
- [ ] Verify documentation clarity

**Test Coverage Target:** >80%

---

## What You Learn

After this sprint:
1. **How often users iterate** → Shows if workflow is right
2. **What errors users hit most** → Guides future improvements
3. **Whether progress is too verbose/sparse** → Can tune in future

---

## Success Metrics

**Quantitative:**
- Progress messages for every section
- All errors have helpful messages
- Iterative refinement works in <5 seconds

**Qualitative:**
- Users don't ask "is it working?"
- Users understand errors without asking
- Iteration feels natural

---

## Implementation Order (TDD Daily Workflow)

**Day 1: Progress Feedback**
- 🔴 Write failing tests for progress callbacks
- 🟢 Implement progress callback mechanism
- 🟢 Integrate with ChunkedGenerator
- 🟢 Add timing measurements
- ✅ Test and commit

**Day 2: Source Documentation + Error Messages**
- Expand TEMPLATES.md with source section
- Update error messages throughout
- Add examples and troubleshooting
- Test all error paths
- ✅ Commit

**Day 3: Iterative Refinement**
- 🔴 Write failing tests for iteration workflow
- 🟢 Implement refinement loop
- 🟢 Test edge cases (no changes, multiple iterations)
- Integration testing
- ✅ Sprint review

---

## Known Limitations (By Design)

1. **No progress bar** - Text-based progress sufficient
2. **No time estimates** - Show actual timing instead
3. **No cancellation** - User can Ctrl+C (standard)

---

## Next Sprint Preview

After Sprint 9, users will want:
- Practical application examples (Sprint 10)
- Real-world templates (Sprint 10)
- Comprehensive guide (Sprint 10)
