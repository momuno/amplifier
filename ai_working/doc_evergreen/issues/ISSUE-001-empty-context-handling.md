# ISSUE-001: Tool Proceeds with Empty Context Instead of Failing Early

**Status:** Resolved
**Priority:** High
**Type:** Bug
**Created:** 2025-11-18
**Updated:** 2025-11-19
**Resolved:** 2025-11-19 (Sprint 5 - v0.2.0)

## Description

When a user provides source patterns that match zero files (e.g., `--sources "src/*.py,docs/*.md"` when those directories don't exist), the tool proceeds to generate documentation with empty context instead of failing early with a clear error message. This results in the LLM receiving no context and producing an error message as the documentation content.

## Reproduction Steps

1. Navigate to the doc_evergreen directory (or any directory without `src/` or `docs/` subdirectories)
2. Run: `uv run python3 doc-update.py README.md --sources "src/*.py,docs/*.md"`
3. Accept the file creation when prompted
4. Observe the generated README.md contains an error message instead of actual documentation

**Frequency:** Always (when source patterns match zero files)

## Expected Behavior

The tool should detect when source resolution results in zero files and:
1. Display a clear error message: "Error: No source files found matching patterns: src/*.py, docs/*.md"
2. Suggest checking the patterns or using `--show-sources` to preview what would be included
3. Exit with non-zero status code before attempting to generate documentation
4. NOT proceed to call the LLM with empty context

## Actual Behavior

1. Source patterns are parsed and expanded (resulting in empty list)
2. Empty list passes through `validate_sources()` with only warnings in logs
3. Empty context string is passed to `gather_context()`
4. LLM receives template with empty context
5. LLM generates error message about missing context
6. Error message is written to preview file
7. User sees "✅ Accepted: README.md updated" (misleading success)
8. README.md contains LLM's error message instead of documentation

## Root Cause

**Location:** `doc_evergreen/cli.py:149-158`

**Technical Explanation:**

The CLI performs source resolution in these steps:

```python
# Line 149: Resolve sources using source resolver
resolved = resolve_sources(cli_sources=sources, add_sources=add_sources, base_dir=base_dir, exclusions=exclusions)

# Line 152: Validate sources
validated = validate_sources(resolved)

# Line 155: Convert to Path objects for gather_context
source_paths = [Path(s) for s in validated]

# Line 158: Gather context
context = gather_context(sources=source_paths)
```

**The problem:**
1. `resolve_sources()` with glob patterns that match nothing returns `[]`
2. `validate_sources([])` returns `[]` (logs warnings but doesn't fail)
3. `gather_context([])` returns `""` (empty string)
4. No check exists between these steps to fail early when source list is empty

**Contributing Factors:**
- `validate_sources()` only logs warnings for missing files, doesn't enforce minimum
- No validation that context string is non-empty before calling LLM
- Success message displays even when generated content contains errors

## Impact Analysis

**Severity:** High - Creates confusing user experience and writes incorrect content to files

**User Impact:**
- Users waste time accepting changes that are actually errors
- Documentation files get overwritten with error messages
- Misleading success messages reduce trust in the tool
- No clear guidance on what went wrong or how to fix it

**Workaround:**
1. Always use `--show-sources` first to verify patterns match files
2. Check that source directories exist before running the tool
3. Use default sources (no `--sources` flag) which have broader patterns

## Acceptance Criteria

To consider this issue resolved:

- [ ] Tool detects when source resolution results in zero files
- [ ] Clear error message displayed: "Error: No source files found matching patterns: [list]"
- [ ] Error message suggests using `--show-sources` to debug patterns
- [ ] Tool exits with non-zero status code (does not proceed to generation)
- [ ] Test case added for empty source list scenario
- [ ] Test case added for non-existent glob patterns
- [ ] Documentation updated to explain source resolution behavior

## Related Issues

- Related to: ISSUE-002 - Confusing success message compounds this problem
- Related to: ISSUE-003 - Better source validation feedback would prevent this

## Technical Notes

**Proposed Solution:**

Add validation after source resolution in `cli.py`:

```python
# After line 152 (validate_sources)
validated = validate_sources(resolved)

# NEW: Check for empty source list
if not validated:
    click.echo("Error: No source files found matching the specified patterns.", err=True)
    if sources:
        click.echo(f"Patterns used: {sources}", err=True)
    click.echo("\nTry:", err=True)
    click.echo("  1. Check that source paths/patterns are correct", err=True)
    click.echo("  2. Use --show-sources to preview what would be included", err=True)
    click.echo("  3. Omit --sources to use default patterns", err=True)
    raise SystemExit(1)

# Continue with existing flow
source_paths = [Path(s) for s in validated]
```

**Alternative Approaches:**
1. Add `min_sources` parameter to `validate_sources()` - More flexible but adds complexity
2. Check context length before LLM call - Too late, better to fail earlier
3. Return validation result from `gather_context()` - Mixing concerns

**Implementation Complexity:** Low - Single validation check with clear error message

**Estimated Effort:** 1 hour (including test cases)

## Testing Notes

**Test Cases Needed:**
- [ ] Test with non-existent directory patterns (`src/*.py` when no src/ exists)
- [ ] Test with patterns that match zero files (`*.xyz` when no .xyz files exist)
- [ ] Test that error message includes the actual patterns used
- [ ] Test that exit code is non-zero
- [ ] Test that no preview file is created when sources are empty
- [ ] Test that default sources (no --sources flag) still work

**Regression Risk:** Low - Adding validation doesn't change existing behavior for valid inputs

## Sprint Assignment

**Assigned to:** Sprint 5 (High Priority Bug Fix)
**Rationale:** High impact on user experience, low implementation complexity, blocks effective tool usage

## Resolution

**Resolved in:** Sprint 5 (v0.2.0 - Chunked Generation)
**Implementation:** Source validation system with fail-early behavior

**How it was fixed:**

Sprint 5 implemented a comprehensive source validation system (`source_validator.py`) that:
1. **Validates all sources upfront** before generation starts (fail early)
2. **Checks for empty source lists** per section and fails with clear error
3. **Displays validation report** showing which sources were resolved for each section
4. **Prevents LLM calls with empty context** by validating before generation begins

The new `validate_all_sources()` function:
- Traverses the template tree and resolves sources for each section
- Reports error if any section has zero sources
- Shows file counts and resolved paths in validation report
- Exits cleanly before attempting generation

This completely eliminates the issue of proceeding with empty context. Users now get immediate, actionable feedback when source patterns don't match any files.

## Comments / Updates

### 2025-11-19
Issue marked as resolved. Implemented in Sprint 5 as part of the source validation system. The upfront validation approach prevents the tool from ever calling the LLM with empty context.

### 2025-11-18
Issue captured from user feedback. Root cause identified in source resolution flow. Proposed solution is a simple validation check with clear error messaging.
