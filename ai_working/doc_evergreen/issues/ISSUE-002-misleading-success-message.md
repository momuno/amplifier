# ISSUE-002: Misleading Success Message When Generated Content Contains Errors

**Status:** Open (Deferred)
**Priority:** Medium
**Type:** Enhancement
**Created:** 2025-11-18
**Updated:** 2025-11-19
**Deferred:** v0.2.0 - Handled by section review workflow

## Description

The tool displays "✅ Accepted: README.md updated" even when the generated content contains LLM error messages instead of actual documentation. This creates a false sense of success and reduces user trust in the tool.

## Reproduction Steps

1. Run the tool with conditions that cause LLM to generate error content (e.g., empty context)
2. Accept the changes when prompted
3. Observe the success message: "✅ Accepted: README.md updated"
4. Open the file and find it contains an error message, not documentation

**Frequency:** Always (when generation produces error content)

## Expected Behavior

The tool should:
1. Detect when generated content contains error patterns (like "I don't see any context provided")
2. Display a warning: "⚠️  Warning: Generated content may contain errors - please review"
3. OR: Show a preview of the first few lines so user can see what's being written
4. Still allow user to accept if they choose, but with informed consent

## Actual Behavior

1. LLM generates error message as content
2. Content is written to preview file
3. User accepts changes
4. Success message displays: "✅ Accepted: README.md updated"
5. No indication that the content is actually an error message
6. User must manually open file to discover the problem

## Root Cause

**Location:** `doc_evergreen/cli.py:171-180`

**Technical Explanation:**

The CLI's review workflow is purely mechanical - it doesn't inspect the generated content:

```python
# Line 171: Review or auto-accept
if no_review:
    accept_changes(target_path, preview_path)
    click.echo(f"✅ Accepted: {target_file} updated")
else:
    if click.confirm("Accept changes?"):
        accept_changes(target_path, preview_path)
        click.echo(f"✅ Accepted: {target_file} updated")
    else:
        reject_changes(preview_path)
        click.echo(f"❌ Rejected: {target_file} unchanged")
```

**The problem:**
- No validation of generated content quality
- Success message assumes generation was successful
- No preview of what's about to be written to the file
- User must trust the tool blindly or manually check preview files

**Contributing Factors:**
- Empty context handling (ISSUE-001) allows bad content to be generated
- No heuristic checks for common LLM error patterns
- No option to show preview content before accepting

## Impact Analysis

**Severity:** Medium - Doesn't break functionality but severely impacts user experience

**User Impact:**
- False confidence in generated documentation
- Wasted time discovering and fixing incorrect content
- Reduced trust in the tool's reliability
- May lead to committing error messages to version control

**Workaround:**
1. Always manually inspect preview files before accepting
2. Use `--show-sources` first to ensure sources are valid
3. Check generated file immediately after acceptance

## Acceptance Criteria

To consider this issue resolved:

- [ ] Success message only displays when content is likely valid
- [ ] Warning message displays when error patterns are detected in content
- [ ] Option to show preview snippet (first 10 lines) before accepting
- [ ] Clear distinction between "file updated" and "generation successful"
- [ ] Test cases for common LLM error patterns
- [ ] Documentation explains what the success message actually means

## Related Issues

- Blocked by: ISSUE-001 - Fixing empty context handling reduces this issue's frequency
- Related to: ISSUE-003 - Better source validation prevents bad content generation

## Technical Notes

**Proposed Solution:**

Add content validation before showing success message:

```python
# After generate_preview (before review)
content = preview_path.read_text()

# Check for common error patterns
error_patterns = [
    "I don't see any context",
    "Could you please provide",
    "I need information about",
    "CONTEXT section is empty",
]

has_error = any(pattern.lower() in content.lower() for pattern in error_patterns)

if has_error:
    click.echo("⚠️  Warning: Generated content appears to contain errors", err=True)
    click.echo("Preview (first 10 lines):", err=True)
    lines = content.split('\n')[:10]
    for line in lines:
        click.echo(f"  {line}", err=True)
    click.echo("", err=True)

# Continue with existing review workflow
```

**Alternative Approaches:**
1. Always show preview snippet - More verbose but more transparent
2. Add `--preview-before-accept` flag - More control but more complex
3. Use LLM to validate output quality - Too slow and expensive

**Implementation Complexity:** Low - Pattern matching and conditional display

**Estimated Effort:** 2 hours (including multiple error pattern tests)

## Testing Notes

**Test Cases Needed:**
- [ ] Test detection of "I don't see any context" pattern
- [ ] Test detection of "Could you please provide" pattern
- [ ] Test with valid content (no false positives)
- [ ] Test warning message display format
- [ ] Test that review workflow still works with warnings
- [ ] Test `--no-review` with error content (should still warn)

**Regression Risk:** Low - Adding warnings doesn't change core functionality

## Sprint Assignment

**Assigned to:** Sprint 5 (User Experience Improvement)
**Rationale:** Medium priority, enhances user trust, low implementation complexity

## Comments / Updates

### 2025-11-19
**Issue deferred in v0.2.0**. The section-by-section review workflow introduced in Sprint 6 provides an alternative solution:
- Users can review each section as it's generated (interactive mode)
- Sections with errors are caught during generation, not after
- The upfront source validation (ISSUE-001 fix) prevents empty context errors
- Combined with ISSUE-003 (source visibility), users have clear feedback during generation

**Deferral rationale**: The new chunked generation workflow with section review checkpoints addresses the core problem (catching errors during generation) more effectively than post-hoc error detection would. The original proposal (pattern matching for error content) becomes less necessary when users review sections incrementally.

**Reconsider**: If users frequently accept error content in auto mode (non-interactive), this issue should be revisited to add error pattern detection.

### 2025-11-18
Issue captured from user feedback. The success message creates false confidence when content contains errors. Proposed solution adds pattern-based detection with preview snippet.
