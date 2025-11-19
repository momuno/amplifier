# Sprint 6: Interactive Review & Enhanced Visibility

**Duration**: 4 days (Week 2, Days 1-4)
**Goal**: Add user control through interactive section review and enhance source visibility
**Value Delivered**: Users can steer output at each section with clear visibility into what's happening

---

## Why This Sprint?

Sprint 5 proved chunked generation works. Now we add the **critical control layer**:

**Question**: Where do users need control to effectively steer output?

**Sprint 5 Learning** → **Sprint 6 Feature**:
- "I want to catch bad sections early" → Interactive checkpoints
- "I need to know what sources affected this" → Enhanced source visibility
- "This section needs tweaking" → Regenerate with feedback
- "Let me fix this manually" → Edit in $EDITOR

**This sprint transforms chunked generation from automated to steerable.**

---

## What You'll Have After This Sprint

A fully controllable chunked generator that:
1. Pauses after each section for review (interactive mode)
2. Shows exactly which sources were used and how much
3. Lets users regenerate sections with feedback
4. Allows manual editing mid-generation
5. Supports quit-and-resume (save partial progress)
6. Provides auto mode for batch operations (no pauses)

**Run it like**:
```bash
# Interactive mode (default for manual runs)
doc-update --mode chunked --interactive template.json

# Auto mode (for CI/batch)
doc-update --mode chunked --auto template.json
```

**User Experience**:
```
Generating section: Overview
  Using sources: doc-update.py (4.2 KB), README.md (3.1 KB)
  Tokens: 2,450 (sources) + 150 (prompt) = 2,600 total
  [calling LLM...]
  ✅ Generated 342 words in 6.2s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Overview

doc_evergreen maintains living documentation...
[full section content]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options:
  [a] Accept and continue
  [r] Regenerate with feedback
  [e] Edit in $EDITOR
  [q] Quit (save progress)

Choice: _
```

---

## Deliverables

### 1. Review Checkpoint System (~200 lines)
**File**: `doc_evergreen/core/review_checkpoint.py` (NEW)

**What it does**: Pauses after each section for user review and action

**Why this sprint**: Core value - user control over output

**Implementation notes**:
- Display section content with clear boundaries
- Four actions: Accept / Regenerate / Edit / Quit
- Simple CLI interface (single-key input)
- Return user's decision to generator

**Key Functions**:
```python
class CheckpointAction(Enum):
    ACCEPT = "accept"
    REGENERATE = "regenerate"
    EDIT = "edit"
    QUIT = "quit"

class ReviewCheckpoint:
    def review_section(
        self,
        section: Section,
        content: str,
        sources_info: SourcesInfo
    ) -> tuple[CheckpointAction, Optional[str]]:
        """Present section for review, return user action.

        Returns:
            (action, feedback) where feedback is for REGENERATE action
        """

    def display_section(self, section: Section, content: str) -> None:
        """Display section with clear boundaries."""

    def get_user_choice(self) -> tuple[CheckpointAction, Optional[str]]:
        """Prompt user for action, return choice and optional feedback."""

    def edit_in_editor(self, content: str) -> str:
        """Open content in $EDITOR, return edited version."""
```

**Display Format**:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## {Section Heading}

{Full section content}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options:
  [a] Accept and continue to next section
  [r] Regenerate with feedback (you'll provide guidance)
  [e] Edit manually in $EDITOR
  [q] Quit and save progress so far

Choice (a/r/e/q): _
```

**Regenerate Flow**:
```
Choice: r

Provide feedback for regeneration (what to change):
> Make it more concise, focus on key features only

Regenerating section with your feedback...
  [calling LLM with modified prompt...]
  ✅ Generated 256 words in 5.8s

[Shows new content, prompts again]
```

**Edit Flow**:
```
Choice: e

Opening in $EDITOR...
[User edits in vim/nano/etc]
✅ Changes saved

[Shows edited content, prompts again]
```

### 2. Enhanced Source Visibility (~150 lines)
**File**: `doc_evergreen/core/source_display.py` (NEW)

**What it does**: Displays detailed source information during generation

**Why this sprint**: Addresses ISSUE-003 completely (users need to know what sources affected what)

**Implementation notes**:
- Show file paths, sizes, and counts
- Display token estimates (sources + prompt + context)
- Optionally show first few lines of each file (verbose mode)
- Clear formatting for readability

**Key Functions**:
```python
@dataclass
class SourcesInfo:
    files: list[Path]
    total_size: int
    token_estimate: TokenBreakdown

@dataclass
class TokenBreakdown:
    sources: int
    prompt: int
    context: int
    total: int

class SourceDisplay:
    def display_sources_for_section(
        self,
        section: Section,
        sources_info: SourcesInfo
    ) -> None:
        """Display source information before generating section."""

    def format_file_list(self, files: list[Path], max_display: int = 5) -> str:
        """Format file list (show first N, then 'and X more')."""

    def estimate_tokens(self, sources: str, prompt: str, context: str) -> TokenBreakdown:
        """Estimate token usage (rough: 4 chars per token)."""
```

**Display Format (Normal)**:
```
Generating section: Features
  Using sources: 8 Python files from src/ (12.4 KB total)
    - src/core/generator.py (2.1 KB)
    - src/core/template.py (1.8 KB)
    - src/core/source_resolver.py (3.2 KB)
    - ... and 5 more files
  Context: Summary of Overview (2 sentences, ~50 tokens)
  Tokens: 8,900 (sources) + 150 (prompt) + 50 (context) = 9,100 total
  [calling LLM...]
```

**Display Format (Verbose - `--verbose` flag)**:
```
Generating section: Features
  Using sources: 8 Python files from src/ (12.4 KB total)

  File: src/core/generator.py (2.1 KB, ~1,800 tokens)
  Preview:
    class Generator:
        """Base generator for documentation."""
        def generate(self, template: Template) -> str:
            ...

  File: src/core/template.py (1.8 KB, ~1,500 tokens)
  Preview:
    @dataclass
    class Template:
        """Template structure."""
        ...

  [... more files ...]

  Context: Summary of Overview (2 sentences)
  "doc_evergreen maintains living documentation through template-based
  regeneration. Focuses on reliability and explicitness."

  Token Breakdown:
    Sources: 8,900 tokens
    Prompt: 150 tokens
    Context: 50 tokens
    Total: 9,100 tokens (~$0.09 estimated)

  [calling LLM...]
```

### 3. Interactive Mode Integration (~150 lines)
**File**: `doc_evergreen/core/chunked_generator.py` (extend from Sprint 5)

**What it does**: Integrates review checkpoints into generation flow

**Why this sprint**: Wire checkpoint system into chunked generator

**Implementation notes**:
- Add `interactive: bool` parameter to `ChunkedGenerator`
- Call checkpoint after each section generation
- Handle user actions (accept, regenerate, edit, quit)
- Save partial progress on quit

**Extended `generate()` Flow**:
```python
async def generate(self, interactive: bool = False) -> str:
    # 1. Validate sources (from Sprint 5)
    validation = validate_all_sources(self.template)

    # 2. Generate sections with optional checkpoints
    output = []
    checkpoint = ReviewCheckpoint() if interactive else None

    for section in traverse_dfs(self.template.sections):
        # Generate section
        sources_info = self.get_sources_info(section)
        context = self.context_manager.get_context()

        content = await self.generate_section(
            section, sources_info, context
        )

        # Interactive checkpoint
        if checkpoint:
            action, feedback = checkpoint.review_section(
                section, content, sources_info
            )

            if action == CheckpointAction.REGENERATE:
                # Regenerate with user feedback
                content = await self.regenerate_section(
                    section, sources_info, context, feedback
                )
                # Re-prompt checkpoint with new content

            elif action == CheckpointAction.EDIT:
                # Let user edit manually
                content = checkpoint.edit_in_editor(content)

            elif action == CheckpointAction.QUIT:
                # Save partial progress and exit
                self.save_partial(output)
                raise UserQuit("Progress saved")

        # Add to output and context
        output.append(content)
        self.context_manager.add_section(section.heading, content)

    # 3. Assemble complete document
    return "\n\n".join(output)
```

**Regenerate with Feedback**:
```python
async def regenerate_section(
    self,
    section: Section,
    sources_info: SourcesInfo,
    context: str,
    feedback: str
) -> str:
    """Regenerate section with user feedback.

    Modifies the prompt to incorporate user guidance.
    """
    # Original prompt from template
    original_prompt = section.prompt

    # Enhanced prompt with feedback
    enhanced_prompt = f"""
{original_prompt}

USER FEEDBACK FOR THIS ITERATION:
{feedback}

Please regenerate the section incorporating this feedback.
"""

    # Generate with modified prompt
    return await self.generate_section_with_prompt(
        section, sources_info, context, enhanced_prompt
    )
```

### 4. CLI Flags (~50 lines)
**File**: `doc_evergreen/doc-update.py` (extend from Sprint 5)

**What it does**: Add `--interactive` and `--auto` flags

**Why this sprint**: User needs to choose mode

**Implementation notes**:
- `--interactive`: Enable checkpoints (pause after each section)
- `--auto`: Skip checkpoints (batch mode, CI)
- Default: `--auto` (less disruptive for existing workflows)
- `--verbose`: Enhanced source display

**CLI Changes**:
```python
@click.command()
@click.argument('template_path')
@click.option('--mode', type=click.Choice(['single', 'chunked']),
              default='single', help='Generation mode')
@click.option('--interactive', is_flag=True,
              help='Pause for review after each section')
@click.option('--auto', is_flag=True, default=True,
              help='Generate all sections without pausing (default)')
@click.option('--verbose', is_flag=True,
              help='Show detailed source information')
@click.option('--output', help='Override output path')
def update(
    template_path: str,
    mode: str,
    interactive: bool,
    auto: bool,
    verbose: bool,
    output: Optional[str]
):
    """Generate/update documentation from template."""
    # Validate flags
    if interactive and auto:
        raise click.UsageError("Cannot use both --interactive and --auto")

    # Set defaults
    is_interactive = interactive or not auto

    template = load_template(template_path)

    if mode == 'chunked':
        generator = ChunkedGenerator(
            template,
            source_resolver,
            interactive=is_interactive,
            verbose=verbose
        )
    else:
        generator = Generator(template, source_resolver)

    result = await generator.generate()
    # ... review workflow
```

**Usage Examples**:
```bash
# Auto mode (default, no pauses)
doc-update --mode chunked template.json

# Interactive mode (pause for review)
doc-update --mode chunked --interactive template.json

# Verbose mode (detailed source display)
doc-update --mode chunked --verbose template.json

# Interactive + verbose
doc-update --mode chunked --interactive --verbose template.json
```

### 5. Partial Progress Saving (~100 lines)
**File**: `doc_evergreen/core/partial_save.py` (NEW)

**What it does**: Saves partial progress when user quits mid-generation

**Why this sprint**: Don't lose work if user quits

**Implementation notes**:
- Save completed sections to `.partial.md` file
- Include metadata (which sections completed, timestamp)
- Clear message to user about where progress was saved
- Optional: Resume from partial (defer to v0.3.0 if time constrained)

**Key Functions**:
```python
class PartialProgressSaver:
    def save(
        self,
        sections: list[GeneratedSection],
        output_path: Path
    ) -> Path:
        """Save partial progress to .partial.md file.

        Returns:
            Path to saved file
        """

    def format_partial(
        self,
        sections: list[GeneratedSection]
    ) -> str:
        """Format partial document with metadata."""
```

**Partial File Format**:
```markdown
<!-- PARTIAL GENERATION -->
<!-- Generated: 2025-01-18 14:32:15 -->
<!-- Sections completed: 3 of 7 -->
<!-- Next section: Installation -->

# My Project README

## Overview
[complete content]

## Features
[complete content]

## Getting Started
[complete content]

<!-- Generation stopped here -->
```

**User Message on Quit**:
```
⏸️  Generation paused by user

Progress saved to: README.partial.md
  Completed sections: 3 of 7
  Next section: Installation

To resume (future feature):
  doc-update --mode chunked --resume README.partial.md template.json

To continue manually:
  1. Review README.partial.md
  2. Re-run full generation when ready
```

### 6. Tests (~300 lines)
**Files**:
- `tests/test_review_checkpoint.py`
- `tests/test_source_display.py`
- `tests/test_interactive_generation.py`

**TDD Approach - Write tests FIRST**:

**Day 1 - Review Checkpoint**:
- 🔴 Write test: `test_checkpoint_displays_section()`
- 🔴 Write test: `test_checkpoint_accepts_actions()`
- 🟢 Implement: `ReviewCheckpoint` class
- 🔵 Refactor: Display formatting
- ✅ Commit (tests pass)

**Day 2 - Source Visibility**:
- 🔴 Write test: `test_source_display_formats_list()`
- 🔴 Write test: `test_token_estimation()`
- 🟢 Implement: `SourceDisplay` class
- 🔵 Refactor: Token calculation
- ✅ Commit (tests pass)

**Day 3 - Interactive Integration**:
- 🔴 Write test: `test_regenerate_with_feedback()`
- 🔴 Write test: `test_edit_in_editor()`
- 🟢 Implement: Regenerate and edit flows
- 🔵 Refactor: Action handling
- ✅ Commit (tests pass)

**Day 4 - Full Workflow**:
- 🔴 Write test: `test_interactive_generation_end_to_end()`
- 🟢 Implement: CLI integration
- 🔵 Refactor: Error handling
- ✅ Manual test: Full interactive session
- ✅ Commit (tests pass)

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What Gets Punted (Deliberately Excluded)

### ❌ Resume from Partial
- **Why**: Save feature is valuable, resume adds complexity
- **Reconsider**: v0.3.0 if users quit frequently

### ❌ Batch Review (every N sections)
- **Why**: Section-by-section is simpler UX
- **Reconsider**: v0.3.0 if users find it tedious

### ❌ "Accept All Remaining" Option
- **Why**: Can switch to auto mode mid-generation (future)
- **Reconsider**: v0.3.0 if requested by users

### ❌ Review History/Undo
- **Why**: Regenerate accomplishes same goal
- **Reconsider**: v0.3.0 if undo patterns emerge

### ❌ Side-by-Side Diff (regenerate)
- **Why**: Simple re-display is sufficient
- **Reconsider**: v0.3.0 for polish

---

## Dependencies

**Requires from previous sprints**:
- `ChunkedGenerator` from Sprint 5
- `SourceValidator` from Sprint 5
- `ContextManager` from Sprint 5
- Template with prompts format from Sprint 5

**Provides for future sprints**:
- `ReviewCheckpoint` system
- Enhanced source display
- Interactive generation pattern
- Partial save mechanism

---

## Acceptance Criteria

### Must Have
- ✅ Interactive checkpoints appear after each section
- ✅ All four actions work (accept, regenerate, edit, quit)
- ✅ Regenerate with feedback produces different output
- ✅ Edit in $EDITOR preserves changes
- ✅ Quit saves partial progress
- ✅ Source display shows files, sizes, token estimates
- ✅ Verbose mode shows detailed source information
- ✅ Auto mode skips all checkpoints
- ✅ All tests pass (>80% coverage)

### Nice to Have (Defer if time constrained)
- ❌ Resume from partial (save for v0.3.0)
- ❌ Colored output (plain text sufficient)
- ❌ Progress bar (section N of M is enough)

---

## Technical Approach

### TDD Red-Green-Refactor Cycle

**Example: Review Checkpoint**

1. **🔴 RED - Write Test First**:
```python
def test_checkpoint_accepts_regenerate():
    checkpoint = ReviewCheckpoint()
    section = Section(heading="Test", prompt="Test prompt")
    content = "Original content"

    # Mock user input: 'r' then feedback
    with mock_input(['r', 'Make it shorter']):
        action, feedback = checkpoint.review_section(
            section, content, sources_info
        )

    assert action == CheckpointAction.REGENERATE
    assert feedback == "Make it shorter"
```

2. **🟢 GREEN - Minimal Implementation**:
```python
def review_section(self, section, content, sources_info):
    self.display_section(section, content)
    choice = input("Choice (a/r/e/q): ").strip().lower()

    if choice == 'r':
        feedback = input("Provide feedback: ")
        return (CheckpointAction.REGENERATE, feedback)
    # ... other actions
```

3. **🔵 REFACTOR - Improve Quality**:
```python
def review_section(self, section, content, sources_info):
    self.display_section(section, content)
    self.display_options()

    while True:
        choice = self.get_validated_choice()
        if choice == 'r':
            feedback = self.get_feedback()
            return (CheckpointAction.REGENERATE, feedback)
        # ... handle other actions with validation
```

### $EDITOR Integration

**Approach**: Use subprocess to open temporary file in user's editor

**Implementation**:
```python
def edit_in_editor(self, content: str) -> str:
    """Open content in $EDITOR, return edited version."""
    import tempfile
    import subprocess
    import os

    # Get editor (fallback to nano)
    editor = os.environ.get('EDITOR', 'nano')

    # Write to temp file
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.md',
        delete=False
    ) as f:
        f.write(content)
        temp_path = f.name

    try:
        # Open in editor (blocking)
        subprocess.run([editor, temp_path], check=True)

        # Read edited content
        with open(temp_path) as f:
            return f.read()
    finally:
        # Clean up temp file
        os.unlink(temp_path)
```

**Error Handling**:
- If $EDITOR not set, use `nano` (most widely available)
- If editor fails, fall back to accept original content
- Clear message if editing was unsuccessful

### Token Estimation

**Approach**: Rough estimation (4 characters per token)

**Implementation**:
```python
def estimate_tokens(self, text: str) -> int:
    """Rough token estimate: 4 chars per token."""
    return len(text) // 4

def estimate_cost(self, tokens: int) -> float:
    """Rough cost estimate (Claude pricing)."""
    # Input: $0.00001 per token (10 tokens per cent)
    return tokens * 0.00001
```

**Why rough estimation:**
- Exact tokenization requires tiktoken or similar
- 4 chars/token is close enough for visibility
- Real token count from LLM API (post-generation)

---

## Implementation Order

### Day 1: Review Checkpoint Foundation

**Morning** (4 hours):
- 🔴 Write test: Display section with boundaries
- 🟢 Implement: `display_section()` method
- 🔵 Refactor: Formatting
- ✅ Commit

- 🔴 Write test: Get user choice (accept)
- 🟢 Implement: Basic input handling
- 🔵 Refactor: Validation
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: Regenerate action with feedback
- 🟢 Implement: Feedback collection
- 🔵 Refactor: User prompts
- ✅ Commit

- 🔴 Write test: Edit action calls $EDITOR
- 🟢 Implement: Editor integration
- Test with real editor
- ✅ Commit (checkpoint system working)

### Day 2: Source Visibility

**Morning** (4 hours):
- 🔴 Write test: Format file list (max display)
- 🟢 Implement: File list formatting
- 🔵 Refactor: String building
- ✅ Commit

- 🔴 Write test: Token estimation
- 🟢 Implement: Token and cost calculation
- Test with real sources
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: Source display output
- 🟢 Implement: Display formatting
- 🔵 Refactor: Layout
- ✅ Commit

- 🔴 Write test: Verbose mode display
- 🟢 Implement: File previews
- Test verbose output
- ✅ Commit (source visibility complete)

### Day 3: Interactive Integration

**Morning** (4 hours):
- 🔴 Write test: Regenerate with feedback flow
- 🟢 Implement: Regeneration in ChunkedGenerator
- 🔵 Refactor: Prompt enhancement
- ✅ Commit

- 🔴 Write test: Edit flow preserves changes
- 🟢 Implement: Edit integration
- Test edit → continue flow
- ✅ Commit

**Afternoon** (4 hours):
- 🔴 Write test: Quit saves partial progress
- 🟢 Implement: Partial save
- 🔵 Refactor: File format
- ✅ Commit

- Wire checkpoint into generation loop
- Test interactive flow with real template
- ✅ Commit (interactive generation working)

### Day 4: CLI Integration + Full Testing

**Morning** (4 hours):
- 🔴 Write test: CLI flags (interactive/auto/verbose)
- 🟢 Implement: Flag handling in CLI
- 🔵 Refactor: Argument validation
- ✅ Commit

- 🔴 Write test: End-to-end interactive generation
- Test full workflow manually
- ✅ Commit

**Afternoon** (4 hours):
- Manual testing: Interactive session with doc_evergreen README
- Test all actions (accept, regenerate, edit, quit)
- Document user experience findings
- 🔵 Refactor: Any UX improvements
- ✅ Final commit

**End of day**: Demo interactive mode, discuss Sprint 7

---

## Testing Requirements

### TDD Workflow Per Feature

**Example: Regenerate with Feedback**

1. **🔴 RED - Write Test First**:
```python
async def test_regenerate_with_feedback():
    generator = ChunkedGenerator(template, resolver, interactive=True)
    section = Section(heading="Test", prompt="Original prompt")

    # First generation
    content1 = await generator.generate_section(section, sources, context)

    # Regenerate with feedback
    content2 = await generator.regenerate_section(
        section, sources, context, "Make it shorter"
    )

    # Should be different
    assert content1 != content2
    assert len(content2) < len(content1)  # Shorter as requested
```

2. **🟢 GREEN - Minimal Implementation**:
```python
async def regenerate_section(self, section, sources, context, feedback):
    enhanced_prompt = f"{section.prompt}\n\nUSER FEEDBACK: {feedback}"
    return await self.generate_section_with_prompt(
        section, sources, context, enhanced_prompt
    )
```

3. **🔵 REFACTOR - Improve Quality**:
```python
async def regenerate_section(
    self,
    section: Section,
    sources_info: SourcesInfo,
    context: str,
    feedback: str
) -> str:
    """Regenerate section incorporating user feedback."""
    # Build enhanced prompt
    enhanced_prompt = self._build_feedback_prompt(
        section.prompt, feedback
    )

    # Generate with enhanced prompt
    logger.info(f"Regenerating {section.heading} with feedback")
    return await self.generate_section_with_prompt(
        section, sources_info, context, enhanced_prompt
    )
```

### Unit Tests (Write First)
- `test_checkpoint_display_section()` - Display formatting
- `test_checkpoint_get_choice()` - Input handling
- `test_checkpoint_edit_in_editor()` - Editor integration
- `test_source_display_format_list()` - File list formatting
- `test_source_display_estimate_tokens()` - Token calculation
- `test_regenerate_with_feedback()` - Feedback incorporation
- `test_partial_save_format()` - Partial file format

### Integration Tests (Write First When Possible)
- `test_interactive_generation_accept()` - Full accept flow
- `test_interactive_generation_regenerate()` - Regenerate flow
- `test_interactive_generation_quit()` - Quit and save
- `test_auto_mode_no_pauses()` - Auto mode skips checkpoints

### Manual Testing Checklist (After Automated Tests)
- [ ] Run interactive generation with test template
- [ ] Test accept → continues to next section
- [ ] Test regenerate → provides feedback → sees new output
- [ ] Test edit → opens $EDITOR → saves changes
- [ ] Test quit → saves partial progress → shows message
- [ ] Run auto mode → no pauses, completes automatically
- [ ] Run verbose mode → see detailed source info
- [ ] Quality evaluation: Is interactive control valuable?

**Test Coverage Target**: >80% for new code

**Commit Strategy**: Commit after each red-green-refactor cycle

---

## What You Learn

After this sprint ships, you discover:

1. **Interactive Control Value**
   - Do users actually use review checkpoints?
   - Which actions are most common (accept/regenerate/edit)?
   - Is it worth the interaction overhead?

2. **Regeneration with Feedback**
   - Does feedback improve output quality?
   - What types of feedback work best?
   - How often do users regenerate?

3. **Source Visibility Impact**
   - Does seeing sources help users understand output?
   - Is token estimation useful (cost awareness)?
   - What level of detail is helpful?

4. **Mode Preference**
   - Do users prefer interactive or auto mode?
   - When is each mode appropriate?
   - Should default change?

**These learnings directly inform**:
- Sprint 7: Edge cases to handle
- v0.3.0: Features to add (resume, batch review, etc.)
- Documentation: User guidance on when to use which mode

---

## Known Limitations (By Design)

1. **No resume from partial** - Must restart full generation
   - **Why acceptable**: Fast enough to regenerate (<10min)
   - **Fix in**: v0.3.0 if users quit frequently

2. **No batch review** - Every section prompts individually
   - **Why acceptable**: Tests granular control hypothesis
   - **Fix in**: v0.3.0 if too tedious

3. **No undo** - Regenerate is the "undo" mechanism
   - **Why acceptable**: Simpler UX, same outcome
   - **Fix in**: v0.3.0 if undo patterns emerge

4. **Basic editor integration** - Just opens $EDITOR
   - **Why acceptable**: Standard Unix convention works
   - **Fix in**: v0.3.0 if editor issues common

---

## Success Criteria

### User Control
- ✅ Users can accept sections easily (default action)
- ✅ Users can regenerate with meaningful feedback
- ✅ Users can edit manually mid-generation
- ✅ Users can quit and preserve progress
- ✅ Auto mode available for batch operations

### Source Visibility
- ✅ Users see which files used per section
- ✅ Users see token estimates (cost awareness)
- ✅ Verbose mode provides detailed information
- ✅ Display is clear and readable

### Code Quality
- ✅ All tests pass (>80% coverage)
- ✅ TDD cycle followed
- ✅ Clean, maintainable code
- ✅ Good error messages

### User Experience
- ✅ Interactive mode feels natural
- ✅ Actions are obvious and easy
- ✅ Feedback loop is quick
- ✅ Users feel in control

---

## Next Sprint Preview

After this sprint adds user control, Sprint 7 (optional buffer) handles **edge cases and polish**:

**The Need**: "I hit an error/edge case and the tool crashed"

**The Solution**:
- Graceful handling of empty sections
- Deep nesting support (3+ levels)
- Clear error messages for common issues
- Performance validation with large docs

**Why Optional**: Sprint 6 delivers full v0.2.0 functionality. Sprint 7 is refinement and robustness for production use.

---

## Quick Reference

**Key Files**:
- `doc_evergreen/core/review_checkpoint.py` - Interactive checkpoints
- `doc_evergreen/core/source_display.py` - Source visibility
- `doc_evergreen/core/partial_save.py` - Save progress on quit
- `doc_evergreen/doc-update.py` - CLI with interactive/auto flags

**Key Commands**:
```bash
# Interactive mode (pause for review)
doc-update --mode chunked --interactive template.json

# Auto mode (no pauses)
doc-update --mode chunked --auto template.json

# Verbose (detailed sources)
doc-update --mode chunked --verbose template.json

# Interactive + verbose
doc-update --mode chunked --interactive --verbose template.json
```

**Key Actions in Interactive Mode**:
- `a` - Accept section, continue
- `r` - Regenerate with feedback
- `e` - Edit in $EDITOR
- `q` - Quit, save progress

---

**Remember**: This sprint is about **control, not automation**. Users should feel empowered to steer output effectively.
