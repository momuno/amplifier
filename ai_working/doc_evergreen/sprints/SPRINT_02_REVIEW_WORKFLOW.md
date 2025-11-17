# Sprint 2: Review Workflow

**Duration**: 2 days (Week 1, Days 4-5)
**Goal**: Add preview generation, diff display, and accept/reject workflow
**Value Delivered**: Confidence to overwrite real documentation files safely

---

## Why This Sprint?

Sprint 1 proved we can generate docs. Now we need **confidence to use it on real files**.

**The Problem**: Direct file overwrite is scary
- What if generation is wrong?
- What if it removes important content?
- What if LLM hallucinates?

**The Solution**: Review before committing
- Generate to preview file first
- Show exactly what changed
- Require explicit user acceptance

**Value**: Transforms from "interesting experiment" to "tool I trust"

---

## What You'll Have After This Sprint

Enhanced script that:
1. Generates to `README.preview.md` (not direct overwrite)
2. Shows side-by-side diff of changes
3. Prompts: "Accept changes? (y/n/e)"
4. On 'y': Overwrites original file
5. On 'n': Keeps original, deletes preview
6. On 'e': Opens preview in editor for manual tweaking

**Run it like**: `python generate_readme.py`
**Output**: Preview → Review → Accept/Reject

---

## Deliverables

### 1. Preview Generator (~50 lines)
**File**: `preview.py`

**What it does**: Generates to temporary preview file instead of final destination

**Why this sprint**: Need safe staging area before overwriting

**Implementation notes**:
- Function: `generate_preview(template, context, target_file) -> preview_path`
- Preview naming: `{target_file}.preview.md`
- Returns path to preview file
- Cleans up old previews if they exist

**Example**:
```python
def generate_preview(template: str, context: str, target: str) -> Path:
    """Generate doc to preview file"""
    preview_path = Path(f"{target}.preview.md")
    generated = generate_doc(template, context)
    preview_path.write_text(generated)
    return preview_path
```

### 2. Diff Display (~100 lines)
**File**: `diff.py`

**What it does**: Shows colorized side-by-side comparison of original vs preview

**Why this sprint**: Users need to see what changed

**Implementation notes**:
- Use Python's `difflib` (built-in)
- Unified diff format (like git diff)
- Colorized output (red = removed, green = added)
- Line numbers for reference
- Summary statistics (lines added/removed/changed)

**Key function**:
```python
def show_diff(original_path: str, preview_path: str) -> None:
    """Display colorized diff between files"""
    original = Path(original_path).read_text().splitlines()
    preview = Path(preview_path).read_text().splitlines()

    diff = difflib.unified_diff(
        original, preview,
        fromfile=original_path,
        tofile=preview_path,
        lineterm=""
    )

    for line in diff:
        print(colorize_diff_line(line))

    print_diff_summary(original, preview)
```

### 3. Accept/Reject Prompt (~80 lines)
**File**: `reviewer.py`

**What it does**: Prompts user for action after showing diff

**Why this sprint**: Need explicit user decision before overwriting

**Implementation notes**:
- Prompt: "Accept changes? (y/n/e/?) "
- Options:
  - `y` (yes): Overwrite original with preview
  - `n` (no): Keep original, delete preview
  - `e` (edit): Open preview in $EDITOR for manual tweaks
  - `?` (help): Show option explanations
- Validates input
- Handles edge cases (file permissions, etc.)

**Example flow**:
```python
def review_changes(original: Path, preview: Path) -> ReviewAction:
    """Prompt user to accept/reject/edit changes"""
    while True:
        choice = input("\nAccept changes? (y/n/e/?) ").lower().strip()

        if choice == "y":
            return ReviewAction.ACCEPT
        elif choice == "n":
            return ReviewAction.REJECT
        elif choice == "e":
            return ReviewAction.EDIT
        elif choice == "?":
            show_help()
        else:
            print("Invalid option. Try again.")
```

### 4. File Operations (~60 lines)
**File**: `file_ops.py`

**What it does**: Safely handles file replacement and cleanup

**Why this sprint**: Need reliable file operations

**Implementation notes**:
- Atomic file replacement (write to temp, then move)
- Backup original before overwriting (optional)
- Clean up preview files
- Handle file permissions
- Error handling for I/O operations

**Key functions**:
```python
def accept_changes(original: Path, preview: Path) -> None:
    """Replace original with preview content"""
    # Atomic replacement
    shutil.copy2(preview, original)
    preview.unlink()
    print(f"✓ Updated {original}")

def reject_changes(preview: Path) -> None:
    """Keep original, delete preview"""
    preview.unlink()
    print("✗ Changes rejected, original unchanged")

def edit_preview(preview: Path) -> None:
    """Open preview in user's editor"""
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, str(preview)])
```

### 5. Updated Main Script (~100 lines)
**File**: `generate_readme.py` (modified from Sprint 1)

**What it does**: Orchestrates preview → diff → review → action workflow

**Why this sprint**: Integrate all new components

**Implementation notes**:
- Load template and context (from Sprint 1)
- Generate to preview file (not direct)
- Show diff
- Prompt for review
- Execute user's choice
- Handle errors gracefully

**New flow**:
```python
def main():
    # Sprint 1 foundation
    template = load_template("templates/readme-template.md")
    context = gather_context()

    # Sprint 2 additions
    preview_path = generate_preview(template, context, "README.md")
    print(f"\n✓ Generated preview: {preview_path}")

    show_diff("README.md", preview_path)

    action = review_changes(Path("README.md"), preview_path)

    if action == ReviewAction.ACCEPT:
        accept_changes(Path("README.md"), preview_path)
    elif action == ReviewAction.REJECT:
        reject_changes(preview_path)
    elif action == ReviewAction.EDIT:
        edit_preview(preview_path)
        # Re-prompt after editing
        action = review_changes(Path("README.md"), preview_path)
        # ... handle post-edit choice
```

### 6. Tests (~150 lines)
**File**: `test_sprint2.py`

**TDD Approach - Write tests FIRST**:

**Day 4 - Preview Generation**:
- 🔴 Write test: `test_generate_preview_creates_file()`
- 🔴 Write test: `test_preview_naming_convention()`
- 🟢 Implement: `generate_preview()` function
- 🔵 Refactor: Clean up old previews
- ✅ Commit (tests pass)

**Day 4 - Diff Display**:
- 🔴 Write test: `test_diff_detects_changes()`
- 🔴 Write test: `test_diff_no_changes()`
- 🟢 Implement: `show_diff()` function
- 🔵 Refactor: Colorization helpers
- ✅ Commit (tests pass)

**Day 5 - Review Workflow**:
- 🔴 Write test: `test_accept_overwrites_original()`
- 🔴 Write test: `test_reject_keeps_original()`
- 🟢 Implement: Review action handlers
- 🔵 Refactor: File operation helpers
- ✅ Commit (tests pass)

**Test coverage**:
- Preview file creation
- Diff generation (with mock files)
- Accept/reject actions
- File operations (with temp files)
- Error handling (missing files, permissions)

**Manual Testing Checklist**:
- [ ] Generate preview successfully
- [ ] Diff shows correct changes
- [ ] Accept overwrites original correctly
- [ ] Reject preserves original
- [ ] Edit opens in editor
- [ ] Can re-review after editing

---

## What Gets Punted (Deliberately Excluded)

### ❌ Auto-backup before overwrite
- **Why**: Users can use git for version control
- **Reconsider**: v2 if users request it

### ❌ Side-by-side visual diff
- **Why**: Terminal unified diff is sufficient
- **Reconsider**: v2 (web UI or TUI)

### ❌ Partial acceptance (accept some sections, reject others)
- **Why**: Accept/reject all or manual edit in 'e' mode
- **Reconsider**: v2 if workflow proves cumbersome

### ❌ Diff highlighting by section
- **Why**: Line-level diff is standard and clear
- **Reconsider**: v2 for template-aware diffing

### ❌ Multiple review rounds without regeneration
- **Why**: Can edit in 'e' mode and re-review
- **Reconsider**: v2 if regeneration is slow

### ❌ Diff statistics dashboard
- **Why**: Simple line count summary sufficient
- **Reconsider**: v2 for analytics

---

## Dependencies

**Requires from previous sprints**:
- Sprint 1: `template.py`, `context.py`, `generator.py`
- Sprint 1: Working generation function

**Provides for future sprints**:
- Preview workflow pattern
- User confirmation UX
- File operation utilities

---

## Acceptance Criteria

### Must Have
- ✅ Preview file generated before overwriting
- ✅ Diff clearly shows all changes
- ✅ User can accept/reject with single keypress
- ✅ Accept replaces original file correctly
- ✅ Reject preserves original file
- ✅ No data loss on any path
- ✅ Clear feedback for each action

### Nice to Have (Defer if time constrained)
- ❌ Colorized diff (can be black/white)
- ❌ Edit mode (can accept/reject only)
- ❌ Summary statistics (lines changed)

---

## Technical Approach

### TDD Red-Green-Refactor Cycle

**Every feature follows this pattern**:

1. **🔴 RED Phase** (~40% of time):
   - Write test that fails
   - Example: `assert preview_file_exists(target)`

2. **🟢 GREEN Phase** (~40% of time):
   - Write minimal code to pass test
   - Example: Simple file write, no cleanup yet

3. **🔵 REFACTOR Phase** (~20% of time):
   - Improve code quality
   - Example: Extract helpers, add cleanup logic

4. **✅ COMMIT**:
   - All tests green = commit point
   - Never commit with failing tests

### Diff Library Choice

**Use `difflib`** (Python standard library):
- No external dependencies
- Unified diff format (familiar from git)
- Sufficient for terminal display

**Why not fancier diff tools?**
- Keep it simple (Sprint 1-4 philosophy)
- External tools add dependencies
- Terminal diff is readable and standard

### User Interaction

**Prompt Design**:
```
Generated preview: README.preview.md

Showing changes:
[diff output here]

Summary: +15 lines, -8 lines, ~23 changed

Accept changes? (y/n/e/?)
  y - Accept and overwrite README.md
  n - Reject and keep original
  e - Edit preview in $EDITOR
  ? - Show this help

Your choice: _
```

**Key UX decisions**:
- Single letter commands (fast)
- Clear action descriptions
- Non-destructive by default
- Can always reject or edit

---

## Implementation Order

### Day 4: Preview + Diff (Foundation)

**Morning** (4 hours):
- 🔴 Write test: Preview file generation
- 🟢 Implement: `preview.generate_preview()`
- 🔵 Refactor: Path handling
- ✅ Commit

- 🔴 Write test: Diff generation
- 🟢 Implement: `diff.show_diff()` (basic)
- 🔵 Refactor: Line colorization helpers
- ✅ Commit

**Afternoon** (4 hours):
- Test preview generation with real README
- Test diff display with known changes
- Polish diff formatting
- Add summary statistics
- ✅ Commit (preview + diff working)

### Day 5: Review + Integration (Complete Workflow)

**Morning** (4 hours):
- 🔴 Write test: Accept action
- 🔴 Write test: Reject action
- 🟢 Implement: `reviewer.review_changes()`
- 🟢 Implement: File operations
- 🔵 Refactor: Error handling
- ✅ Commit

**Afternoon** (4 hours):
- Integrate into `generate_readme.py`
- End-to-end manual testing
- Test all paths (accept/reject/edit)
- Handle edge cases
- ✅ Final commit

**End of day**: Demo complete review workflow

---

## Testing Requirements

### TDD Workflow Per Feature

**Example: Accept Changes**

1. **🔴 RED - Write Test First**:
```python
def test_accept_changes_overwrites_original(tmp_path):
    original = tmp_path / "README.md"
    preview = tmp_path / "README.preview.md"

    original.write_text("Original content")
    preview.write_text("New content")

    accept_changes(original, preview)

    assert original.read_text() == "New content"
    assert not preview.exists()  # Cleaned up
```

2. **🟢 GREEN - Minimal Implementation**:
```python
def accept_changes(original: Path, preview: Path):
    shutil.copy2(preview, original)
    preview.unlink()
```

3. **🔵 REFACTOR - Improve Quality**:
```python
def accept_changes(original: Path, preview: Path) -> None:
    """Atomically replace original with preview content"""
    try:
        shutil.copy2(preview, original)
        preview.unlink()
        logger.info(f"Updated {original}")
    except IOError as e:
        logger.error(f"Failed to update {original}: {e}")
        raise
```

### Unit Tests (Write First)
- `test_preview_file_created()` - Preview generation
- `test_diff_empty_when_identical()` - No changes detection
- `test_diff_shows_additions()` - Added lines
- `test_diff_shows_deletions()` - Removed lines
- `test_accept_overwrites()` - File replacement
- `test_reject_preserves()` - Original unchanged
- `test_preview_cleanup()` - No leftover files

### Integration Tests (Write First When Possible)
- `test_full_accept_workflow()` - Generate → Accept → Original updated
- `test_full_reject_workflow()` - Generate → Reject → Original preserved
- `test_no_changes_workflow()` - Generate identical → No diff shown

### Manual Testing Checklist (After Automated Tests)
- [ ] Run full generation
- [ ] Preview file created correctly
- [ ] Diff is readable and accurate
- [ ] Accept overwrites correctly
- [ ] Reject preserves original
- [ ] Edit opens editor
- [ ] Can abort at any point
- [ ] No leftover preview files

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What You Learn

After this sprint ships, you discover:

1. **User Confidence**
   - Does review workflow feel safe?
   - Is diff output clear enough?
   - Do users trust accept/reject decisions?

2. **Workflow Efficiency**
   - Is review step too slow?
   - Do users always accept? (maybe skip review?)
   - Is edit mode useful or confusing?

3. **Quality Indicators**
   - What kinds of changes do users accept?
   - What triggers rejection?
   - Are there patterns in edits?

4. **UX Improvements Needed**
   - Better diff formatting?
   - More/fewer options?
   - Different prompts?

**These learnings directly inform**:
- Sprint 3: CLI design (based on workflow patterns)
- Sprint 4: Context selection (based on what changes users reject)
- v2: Potential automation (if users always accept certain changes)

---

## Known Limitations (By Design)

1. **Terminal-only diff** - No GUI
   - **Why acceptable**: Terminal is universal, works everywhere
   - **Future**: v2 could add web/TUI viewer

2. **All-or-nothing acceptance** - Can't accept specific sections
   - **Why acceptable**: Edit mode allows manual tweaks
   - **Future**: v2 could add section-level acceptance

3. **No diff history** - Only current vs preview
   - **Why acceptable**: Git provides full history
   - **Future**: v2 could integrate with git diff

4. **Single file at a time** - No batch review
   - **Why acceptable**: MVP focuses on single doc regeneration
   - **Future**: Sprint 3+ could add batch processing

---

## Success Criteria

### Code Quality
- ✅ All tests pass (>80% coverage)
- ✅ TDD cycle followed for all features
- ✅ Clean, readable code
- ✅ Proper error handling

### User Experience
- ✅ Review workflow feels safe
- ✅ Diff is clear and readable
- ✅ Accept/reject is obvious
- ✅ No confusing states
- ✅ Can always abort safely

### Reliability
- ✅ No data loss on any path
- ✅ Atomic file operations
- ✅ Preview cleanup reliable
- ✅ Handles edge cases (missing files, permissions)

### Validation
- ✅ User trusts the tool enough to use on real files
- ✅ Review process takes <2 minutes
- ✅ Clear what changed and why

---

## Next Sprint Preview

After this sprint adds review confidence, Sprint 3 makes the tool **reusable**:

**The Need**: "I want to use this for other docs, not just README"

**The Solution**:
- Proper CLI interface (`amplifier doc-update <file> --template <template>`)
- Template selection (different templates for different doc types)
- Organized template library
- Project configuration file

**Why Next**: Now that generation works (Sprint 1) and review is safe (Sprint 2), time to make it a real tool that works for any documentation file.

---

## Quick Reference

**Key Files**:
- `preview.py` - Preview generation
- `diff.py` - Diff display
- `reviewer.py` - Accept/reject workflow
- `file_ops.py` - Safe file operations

**Key Commands**:
```bash
# Run with review workflow
python generate_readme.py
# → Generates preview
# → Shows diff
# → Prompts for action

# Run tests
pytest tests/test_sprint2.py -v
```

**Review Options**:
- `y` - Accept changes
- `n` - Reject changes
- `e` - Edit preview
- `?` - Show help

---

**Remember**: This sprint is about **confidence to use**, not fancy features. Goal is to trust the tool enough to let it overwrite real files.
