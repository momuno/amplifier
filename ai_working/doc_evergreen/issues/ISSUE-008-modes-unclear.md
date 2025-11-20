# ISSUE-008: Unclear What "Chunked" vs "Single-Shot" Modes Do

**Status:** Open
**Priority:** Medium
**Type:** Enhancement (Documentation)
**Created:** 2025-11-19
**Updated:** 2025-11-19

---

## Description

The CLI offers two generation modes (`--mode single` and `--mode chunked`) but doesn't clearly explain what each mode does, when to use them, or how they differ. Users must guess or experiment to understand the functionality.

## User Feedback

> "i see the 2 different modes, chunked and single. i'd like to confirm how each works. its not clear what is going on when i run each of them."

## Reproduction Steps

1. Run: `doc-update --help`
2. See: `--mode [single|chunked]  Generation mode: single-shot or section-by-section`
3. Question: What's the actual difference?
4. Run with each mode and observe... no visible difference (see ISSUE-009)
5. Still unclear about the purpose and benefits of each

**Frequency:** Always - affects all users trying to choose a mode

## Expected Behavior

**Clear documentation explaining:**

### Chunked Mode (`--mode chunked`)
- **How it works**: Generates one section at a time sequentially
- **Process**:
  - Section 1 → call LLM → get result
  - Section 2 → call LLM (with Section 1 context) → get result
  - Section 3 → call LLM (with Sections 1-2 context) → get result
- **Benefits**:
  - Later sections can reference earlier content
  - Better context continuity
  - Can see progress section-by-section
- **Drawbacks**:
  - Slower (N LLM calls for N sections)
  - Higher API costs
- **When to use**:
  - Multi-section documents where later sections reference earlier ones
  - When sections need to build on each other
  - When you want granular progress feedback

### Single-Shot Mode (`--mode single`)
- **How it works**: Generates entire document in one LLM call
- **Process**:
  - Give all prompts/sources at once → call LLM once → get complete document
- **Benefits**:
  - Faster (one LLM call total)
  - Lower API costs
  - More coherent overall structure
- **Drawbacks**:
  - No section-by-section context building
  - All-or-nothing generation
- **When to use**:
  - Simple documents
  - Independent sections
  - When speed/cost matters more than context continuity

### Help Text Should Explain This

```bash
--mode [single|chunked]
    Generation mode:
    - 'single': Generate entire document in one LLM call (faster, lower cost)
    - 'chunked': Generate section-by-section with context (better continuity)
    Default: single
```

## Actual Behavior

**Current help text:**
```
--mode [single|chunked]  Generation mode: single-shot or section-by-section
```

**Problems:**
- "single-shot" vs "section-by-section" doesn't explain the difference
- No guidance on when to use each
- No explanation of trade-offs
- No documentation beyond help text
- Users must experiment to understand

## Root Cause

**Location:**
- CLI help text: `doc_evergreen/cli.py` line 26-28
- Missing documentation: No MODES.md or README section

**Technical Explanation:**

The help text is too brief:
```python
@click.option(
    "--mode",
    type=click.Choice(["single", "chunked"]),
    default="single",
    help="Generation mode: single-shot or section-by-section",
)
```

And there's no documentation file explaining:
- How each mode works internally
- Trade-offs between modes
- When to use which mode
- Performance/cost implications

## Impact Analysis

**Severity:** Medium - Doesn't prevent usage but causes confusion

**User Impact:**
- Users default to "single" without understanding alternatives
- May use wrong mode for their use case
- Unclear why they'd choose one over the other
- Experimentation required to learn differences

**Workaround:**
1. Try both modes and compare results
2. Read source code to understand implementation
3. Guess based on mode names

## Acceptance Criteria

To consider this issue resolved:

- [ ] **Improved help text:**
  ```python
  help="Generation mode: 'single' (one LLM call, faster) or 'chunked' (section-by-section with context, better continuity). Default: single"
  ```
- [ ] **Create MODES.md documentation** explaining:
  - [ ] How each mode works (with diagrams if helpful)
  - [ ] Benefits and drawbacks comparison table
  - [ ] When to use each mode
  - [ ] Performance/cost comparison
  - [ ] Example use cases for each
- [ ] **Update README** with modes section
- [ ] **Update CLI docstring** with mode examples:
  ```python
  # For independent sections, use single-shot (faster)
  doc-update template.json

  # For sections that reference each other, use chunked
  doc-update --mode chunked template.json
  ```

## Related Issues

- Blocked by: ISSUE-009 - Single-shot mode doesn't exist yet!
- Related to: ISSUE-005 - Example templates should show when to use each mode
- Related to: ISSUE-007 - Progress feedback would clarify mode differences

## Technical Notes

**Proposed Solution:**

**1. Update CLI help text:**

```python
@click.option(
    "--mode",
    type=click.Choice(["single", "chunked"]),
    default="single",
    help=(
        "Generation mode:\n"
        "  'single'  - Generate entire document in one LLM call (faster, lower cost)\n"
        "  'chunked' - Generate section-by-section with context (better continuity)\n"
        "Default: single"
    ),
)
```

**2. Create MODES.md:**

```markdown
# Generation Modes

## Chunked Mode

**How it works:**
Generates one section at a time, passing previous sections as context.

**Flow:**
```
Section 1 → LLM → Result 1
Section 2 + Context(Result 1) → LLM → Result 2
Section 3 + Context(Results 1-2) → LLM → Result 3
```

**Use when:**
- Later sections reference earlier content
- Building narrative across sections
- Want section-by-section progress

**Trade-offs:**
- ✓ Better context continuity
- ✓ Sections can reference each other
- ✗ Slower (N API calls)
- ✗ Higher cost

## Single-Shot Mode

**How it works:**
Generates entire document in one LLM call.

**Flow:**
```
All sections + all sources → LLM → Complete document
```

**Use when:**
- Sections are independent
- Want faster generation
- Cost/speed matters

**Trade-offs:**
- ✓ Faster (1 API call)
- ✓ Lower cost
- ✓ More coherent overall
- ✗ No inter-section context
```

**3. Add mode comparison to README**

**Implementation Complexity:** Low - Documentation only

**Estimated Effort:** 2-3 hours

## Testing Notes

**Test Cases Needed:**
- [ ] Help text displays correctly formatted
- [ ] Documentation is clear and accurate
- [ ] Examples in docs work as described

**Regression Risk:** None - Documentation only

## Sprint Assignment

**Assigned to:** TBD (Documentation - After ISSUE-009 is fixed)
**Rationale:** Important for user understanding, but blocked by single-shot implementation

## Comments / Updates

### 2025-11-19
Issue captured from user feedback. User wanted to understand the difference between modes but documentation was insufficient. This is a moderate priority documentation gap that affects mode selection decisions.

**Note:** Currently both modes use chunked generator (see ISSUE-009), so this documentation should be written but will only be fully relevant once single-shot mode is implemented.
