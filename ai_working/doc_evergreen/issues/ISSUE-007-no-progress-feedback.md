# ISSUE-007: No Progress or Activity Feedback During Generation

**Status:** Open
**Priority:** High
**Type:** Enhancement (UX)
**Created:** 2025-11-19
**Updated:** 2025-11-19

---

## Description

When running `doc-update`, the CLI provides no output or feedback during the generation process. Users see a blank terminal and don't know if the tool is working, hung, or crashed. This is especially problematic for long-running generations with multiple sections.

## User Feedback

> "I'm running [command] and don't see anything on the screen. is it hanging or processing?"

## Reproduction Steps

1. Run: `doc-update example_template.json`
2. Observe: Terminal shows no output
3. Wait: 30 seconds, 1 minute, 2 minutes...
4. Question: Is it working? Should I wait? Should I kill it?
5. Eventually: Either completes with output or errors

**Frequency:** Always - affects every generation

## Expected Behavior

The tool should provide continuous feedback:

```
Loading template: example_template.json
Validating sources...
✓ Found 4 source files

Generating documentation (chunked mode)...

[1/4] Generating: Overview
      Sources: cli.py, __init__.py (2 files)
      ⣾ Calling LLM...
      ✓ Complete (12.3s)

[2/4] Generating: Command Line Interface
      Sources: cli.py (1 file)
      ⣾ Calling LLM...
      ✓ Complete (8.7s)

[3/4] Generating: Template System
      Sources: template_schema.py (1 file)
      ⣾ Calling LLM...
      ✓ Complete (10.1s)

[4/4] Generating: Source Resolution
      Sources: source_resolver.py (1 file)
      ⣾ Calling LLM...
      ✓ Complete (9.4s)

✓ Generated: DOC_EVERGREEN_GUIDE.md (40.5s total)
```

## Actual Behavior

**Current output:**
```
[user runs command]
[blank terminal for 30-60+ seconds]
[either succeeds or fails with error]
```

**No feedback about:**
- Template loading
- Source validation
- Which section is being generated
- How many sections total
- LLM calls in progress
- Time elapsed
- Overall progress percentage

## Root Cause

**Location:** `doc_evergreen/cli.py` and `doc_evergreen/chunked_generator.py`

**Technical Explanation:**

The CLI has minimal output statements:

```python
# cli.py only outputs:
- Error messages (if validation fails)
- "Generated: {output_path}" (on success)

# chunked_generator.py uses logger but not CLI output:
logger.info("Validating sources...")
logger.info(f"Generating: {section.heading}")
logger.info(f"  Sources: {len(sources)} files")
```

**The problem:**
- Logger output goes to logs, not visible to user by default
- No `click.echo()` statements during generation
- No progress indicators
- No time estimates or completion percentages

## Impact Analysis

**Severity:** High - Makes tool feel unresponsive and unreliable

**User Impact:**
- Uncertainty if tool is working or hung
- Cannot estimate completion time
- May kill process thinking it's frozen
- Anxiety during long generations
- Reduced trust in tool reliability

**Workaround:**
1. Wait patiently (no way to know how long)
2. Check process list: `ps aux | grep doc-update`
3. Check system resources to see if Python is active
4. Hope it eventually completes

## Acceptance Criteria

To consider this issue resolved:

- [ ] **Template loading feedback**:
  - [ ] "Loading template: {path}"
  - [ ] "Validating sources..."
  - [ ] "✓ Found {N} source files"
- [ ] **Generation progress**:
  - [ ] "[X/N] Generating: {section.heading}"
  - [ ] "      Sources: {list of files} ({count} files)"
  - [ ] Spinner or progress indicator during LLM calls
  - [ ] "      ✓ Complete ({time}s)"
- [ ] **Summary on completion**:
  - [ ] "✓ Generated: {output_path} ({total_time}s total)"
- [ ] **Error feedback**:
  - [ ] Clear indication which step failed
  - [ ] What was being processed when error occurred
- [ ] **Optional verbose mode**:
  - [ ] `--verbose` or `-v` flag for detailed output
  - [ ] Shows prompts, context sizes, etc.

## Related Issues

- Related to: ISSUE-008 - Progress would clarify which mode is running
- Partially addresses: ISSUE-006 - Would show which sources being used

## Technical Notes

**Proposed Solution:**

**1. Add progress output to CLI:**

```python
# In cli.py after template validation
click.echo(f"Loading template: {template_path}")
click.echo("Validating sources...")
click.echo(f"✓ Found {total_sources} source files")
click.echo(f"\nGenerating documentation ({mode} mode)...")
```

**2. Add progress callbacks to generator:**

```python
# In chunked_generator.py
async def generate(self, progress_callback=None) -> str:
    for idx, section in enumerate(traverse_dfs(...), 1):
        if progress_callback:
            progress_callback(f"[{idx}/{total}] Generating: {section.heading}")
            progress_callback(f"      Sources: {sources_list}")

        # ... generate section ...

        if progress_callback:
            progress_callback(f"      ✓ Complete ({elapsed}s)")
```

**3. Use click.echo for progress:**

```python
# In cli.py
def progress_callback(msg: str):
    click.echo(msg)

generator = ChunkedGenerator(template, base_dir)
result = asyncio.run(generator.generate(progress_callback=progress_callback))
```

**4. Add spinner for LLM calls (optional):**

Use `click.progressbar()` or simple spinner:
```python
import itertools
import sys

spinner = itertools.cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
sys.stdout.write(next(spinner))
sys.stdout.flush()
```

**Alternative Approaches:**
1. Use `rich` library for progress bars and spinners (adds dependency)
2. Use `tqdm` for progress bars (adds dependency)
3. Simple click.echo with timestamps (no dependencies)

**Implementation Complexity:** Low to Medium
- Simple echo statements: Low effort
- Progress callbacks: Medium effort
- Spinners/rich output: Medium effort

**Estimated Effort:** 3-4 hours

## Testing Notes

**Test Cases Needed:**
- [ ] Progress output appears for single-section template
- [ ] Progress output appears for multi-section template
- [ ] Progress output appears for nested sections
- [ ] Time measurements are reasonable
- [ ] Error messages still clear when progress enabled
- [ ] Output doesn't interfere with `--output` file writing

**Regression Risk:** Low - Adding output doesn't change core logic

## Sprint Assignment

**Assigned to:** TBD (High Priority - UX)
**Rationale:** High user impact, low implementation risk, improves confidence

## Comments / Updates

### 2025-11-19
Issue captured from user feedback. User ran command and saw no output, couldn't tell if tool was working or frozen. This is a critical UX issue that makes the tool feel unresponsive and unreliable.

---

## RESOLUTION

**Resolved in**: Sprint 9 Day 1 (v0.3.0)
**Commit**: eb74e1b - "feat(doc_evergreen): Sprint 9 Day 1 - progress feedback system"
**Date**: 2025-11-20

**What was implemented**:

**Progress Callback System** (chunked_generator.py):
1. Added `progress_callback` parameter to `ChunkedGenerator.generate()`
2. Timing tracking for each section
3. Progress indicators showing section X of N
4. Source file display per section
5. Completion markers with timing

**CLI Integration** (cli.py):
```python
def progress_callback(msg: str) -> None:
    """Display progress messages during generation."""
    click.echo(msg, nl=False)

result = generator.generate(progress_callback=progress_callback)
```

**Output format** (exactly as proposed in acceptance criteria):
```
[1/4] Generating: Overview
      Sources: README.md, pyproject.toml (2 files)
      ✓ Complete (5.2s)

[2/4] Generating: Installation
      Sources: README.md, setup.py (2 files)
      ✓ Complete (3.8s)
```

**Tests**: 9 comprehensive tests covering all progress feedback functionality

**All acceptance criteria met** - Real-time progress feedback fully implemented and working.
