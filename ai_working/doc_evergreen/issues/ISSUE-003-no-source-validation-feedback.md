# ISSUE-003: No User Feedback When Source Globs Match Zero Files

**Status:** Resolved
**Priority:** Medium
**Type:** Enhancement
**Created:** 2025-11-18
**Updated:** 2025-11-19
**Resolved:** 2025-11-19 (Sprint 5/6 - v0.2.0)

## Description

When a user provides source patterns via `--sources` that are syntactically valid but match zero files, the tool provides no feedback about this before proceeding to generation. The user only discovers the problem indirectly when they see error messages in the generated content.

## Reproduction Steps

1. Run: `uv run python3 doc-update.py README.md --sources "src/*.py,docs/*.md"`
2. Observe: No message about how many files were matched
3. Observe: No warning that zero files were found
4. Discover problem only when generated content contains errors

**Frequency:** Always (when patterns match zero files)

## Expected Behavior

The tool should provide feedback about source resolution:
1. Display: "Found 0 files matching patterns: src/*.py, docs/*.md"
2. Suggest: "Use --show-sources to debug pattern matching"
3. OR: Automatically show matched sources (like `--show-sources` does)
4. Allow user to proceed with informed understanding or fail early

## Actual Behavior

1. Source patterns are silently expanded (resulting in empty list)
2. Only logging warnings appear (not visible to user)
3. No stdout feedback about source resolution
4. User proceeds unaware that no sources were found
5. Problem becomes apparent only when generation fails

## Root Cause

**Location:** `doc_evergreen/cli.py:144-158` and `doc_evergreen/source_resolver.py:109-133`

**Technical Explanation:**

Source resolution happens silently:

```python
# cli.py line 149: Resolve sources
resolved = resolve_sources(cli_sources=sources, add_sources=add_sources, base_dir=base_dir, exclusions=exclusions)

# cli.py line 152: Validate sources (only logs warnings, no user feedback)
validated = validate_sources(resolved)

# source_resolver.py line 130: Warning logged but not displayed to user
logger.warning(f"Source file not found: {source}")
```

**The problem:**
- Source resolution and validation use logging only (user doesn't see logs by default)
- No stdout feedback about how many sources were found
- `--show-sources` flag exists but user must know to use it proactively
- Main workflow provides no visibility into source discovery

**Contributing Factors:**
- Separation between `--show-sources` workflow and main workflow
- Assumption that logging is sufficient for feedback
- No summary of source discovery in normal operation

## Impact Analysis

**Severity:** Medium - Doesn't cause data loss but creates confusion

**User Impact:**
- Trial and error required to debug source patterns
- Unclear whether patterns are correct or directories don't exist
- Must learn about `--show-sources` flag to get visibility
- Frustrating experience when patterns are slightly wrong

**Workaround:**
1. Always use `--show-sources` first before running actual generation
2. Manually verify directories exist before running tool
3. Check log output (if logging is configured)

## Acceptance Criteria

To consider this issue resolved:

- [ ] Tool displays source count before generation: "Using X source files"
- [ ] When count is 0, displays: "Warning: No source files found"
- [ ] Lists patterns that matched nothing: "Patterns matched nothing: src/*.py, docs/*.md"
- [ ] Suggests using `--show-sources` for detailed debugging
- [ ] Option to show source summary by default (or via flag)
- [ ] Test cases for zero-match scenarios
- [ ] Documentation explains source discovery feedback

## Related Issues

- Related to: ISSUE-001 - Both stem from lack of source validation feedback
- Related to: ISSUE-002 - Better feedback would prevent misleading success messages

## Technical Notes

**Proposed Solution:**

Add source summary display in main workflow:

```python
# After validate_sources (cli.py after line 152)
validated = validate_sources(resolved)

# NEW: Display source summary
if validated:
    click.echo(f"Using {len(validated)} source file(s)")
    if len(validated) <= 5:
        for source in validated:
            click.echo(f"  • {Path(source).name}")
    else:
        for source in validated[:5]:
            click.echo(f"  • {Path(source).name}")
        click.echo(f"  ... and {len(validated) - 5} more")
else:
    # This would be handled by ISSUE-001 fix (fail early)
    click.echo("Warning: No source files found", err=True)
```

**Alternative Approaches:**
1. Always show full source list like `--show-sources` - Too verbose
2. Add `--verbose` flag for source details - More flexible but more complex
3. Show sources only when count < threshold - Balances verbosity

**Implementation Complexity:** Low - Simple display logic

**Estimated Effort:** 1 hour (including test cases)

## Testing Notes

**Test Cases Needed:**
- [ ] Test feedback with 0 sources
- [ ] Test feedback with 1-5 sources (show all)
- [ ] Test feedback with >5 sources (show summary)
- [ ] Test that source names are displayed clearly
- [ ] Test that feedback doesn't break workflow
- [ ] Test with both CLI sources and default sources

**Regression Risk:** Low - Adding informational output doesn't change behavior

## Sprint Assignment

**Assigned to:** Sprint 5 (User Experience Improvement)
**Rationale:** Medium priority, improves debuggability, low implementation complexity, natural companion to ISSUE-001

## Resolution

**Resolved in:** Sprint 5/6 (v0.2.0 - Chunked Generation)
**Implementation:** Source visibility in validation reports and per-section logging

**How it was addressed:**

Sprint 5 implemented validation reporting that shows which sources are used:
1. **Validation report** shows resolved file paths per section before generation
2. **Per-section logging** displays which sources are being used during generation
3. **Source count display** shows how many files were found for each section
4. **Clear failure messages** when sections have no sources (combined with ISSUE-001 fix)

Sprint 6 enhanced visibility with:
1. **Interactive checkpoints** showing section-by-section progress
2. **Source display** at each checkpoint showing which files contributed
3. **Context flow visibility** showing how sections build on each other

While the original proposal suggested showing sources in the main workflow, the implemented solution provides visibility through:
- Upfront validation reports (shows all sources before generation)
- Section-by-section progress (shows sources as they're used)
- Interactive mode (optional checkpoints with full source visibility)

This addresses the core issue: users now have clear visibility into which sources are being used and can quickly identify when patterns don't match expected files.

## Comments / Updates

### 2025-11-19
Issue marked as resolved. Implemented across Sprint 5 (validation reports) and Sprint 6 (interactive visibility). The combination of upfront validation and per-section logging provides the needed source visibility.

### 2025-11-18
Issue captured from user feedback. Users need visibility into source resolution to understand why generation fails or succeeds. Proposed solution adds source count summary to main workflow.
