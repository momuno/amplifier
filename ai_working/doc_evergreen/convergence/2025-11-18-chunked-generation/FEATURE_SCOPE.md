# doc_evergreen - Problem B MVP Definition

**Chunked Section-by-Section Generation with User Control**

**Status**: Converged and Ready for Sprint Planning
**Timeline**: 2-3 weeks (Sprints 5-7)
**Builds On**: Sprints 1-4 (Problem A - Template-based Single-shot Generation)

---

## Context: Two Problems, Two MVPs

### Problem A (COMPLETED - Sprints 1-4)
**"Stale documentation needs reliable regeneration"**
- ✅ Template-based structure
- ✅ Source resolution (glob patterns, hierarchical)
- ✅ Single-shot full-document generation
- ✅ Review & accept workflow

### Problem B (THIS MVP - Sprints 5-7)
**"Single-shot generation lacks control and predictability"**
- Section-by-section generation (chunked)
- Explicit prompts per section (strong guardrails)
- Context flow between sections
- Source validation and visibility
- Optional review checkpoints

---

## The ONE Problem

**Problem Statement:**
"Full-document single-shot generation lacks user control and guardrails, making output unpredictable and difficult to steer toward user's actual needs"

**Current State (After Sprints 1-4):**
- Template defines structure (section hierarchy)
- Tool gathers all sources once
- Single LLM call generates entire document
- User reviews complete output
- **Pain**: No control over individual section content
- **Pain**: Unpredictable output from large prompts
- **Pain**: Must regenerate entire document to fix one section
- **Pain**: Unknown which sources affected which sections (ISSUE-003)
- **Pain**: Tool continues with empty context (ISSUE-001)

**Desired State (Problem B MVP):**
- Users define explicit prompts for each section
- Generate document section-by-section
- Context flows from earlier to later sections
- User sees which sources are used per section
- Optional checkpoints to review/steer at each stage
- Tool fails early if sources are missing

---

## The Specific User

**Who:**
- Solo developers maintaining 5+ projects with living documentation
- Technical writers managing complex technical docs
- Teams needing predictable, steerable documentation generation

**Current Pain (Problem B Specific):**
- **Lack of control**: Can't specify what each section should contain
- **All-or-nothing**: Can't steer individual sections
- **Unpredictable**: Large prompts produce variable quality
- **Source mystery**: No visibility into which sources affected which sections (ISSUE-003)
- **Silent failures**: Tool continues with empty sources, generates error messages (ISSUE-001)

**What They Need:**
- Strong input guardrails (explicit prompts per section)
- Ability to catch and fix problems at section boundaries
- Visibility into source resolution per section
- Confidence that sources exist before generation starts
- Context flow so sections reference each other appropriately

---

## Current Solution & Why It Fails

**Current Approach (Sprints 1-4 - Problem A):**
1. User defines template structure (sections hierarchy)
2. Tool gathers all sources once
3. Single LLM call generates entire document
4. Review & accept workflow

**Why This Is Insufficient for Problem B:**
- **Lack of control**: No way to specify what each section should contain
- **All-or-nothing**: Can't steer individual sections
- **Unpredictable**: Large prompts produce variable quality
- **Source visibility**: No way to know which sources affected which sections
- **Silent failures**: Tool continues with empty sources (ISSUE-001)
- **Context opacity**: Unclear how sections relate to each other

---

## MVP Solution: Chunked Section-by-Section Generation

### Architecture Overview

```
Template with Section Prompts
         ↓
   Source Validation (fail early)
         ↓
Section 1: Generate [show sources]
         ↓
  [Optional Review Checkpoint]
         ↓
Section 2: Generate with Section 1 context [show sources]
         ↓
  [Optional Review Checkpoint]
         ↓
Section 3: Generate with Sections 1-2 context [show sources]
         ↓
  [Optional Review Checkpoint]
         ↓
   Complete Document
         ↓
  Final Review & Accept (existing Sprint 4 workflow)
```

---

## Must-Have Features (5)

### Feature 1: Template with Section-Level Prompts

**What:**
- Extend JSON template format to include explicit prompts per section
- Each section specifies: `heading`, `prompt`, `sources` (optional)
- Hierarchical source inheritance from Sprints 1-4

**Example Template:**
```json
{
  "document": {
    "title": "My Project README",
    "output": "README.md",
    "sections": [
      {
        "heading": "Introduction",
        "prompt": "Provide high-level overview of project purpose and main goals. Keep it concise (2-3 paragraphs).",
        "sources": ["README.md", "pyproject.toml"]
      },
      {
        "heading": "Features",
        "prompt": "List key features as bullet points. Reference concepts from Introduction section. Be specific about capabilities.",
        "sources": ["src/**/*.py"],
        "sections": [
          {
            "heading": "Core Features",
            "prompt": "Focus on must-have capabilities. Include code examples.",
            "sources": ["src/core/**/*.py"]
          }
        ]
      },
      {
        "heading": "Installation",
        "prompt": "Step-by-step install guide. Assume user has read Features section.",
        "sources": ["pyproject.toml", "README.md"]
      }
    ]
  }
}
```

**Why Essential:**
- Gives users "strong guardrail input" they need
- Explicit control over what each section should contain
- Clear expectations for LLM per section
- Enables section-specific source specification

**Technical:**
- Reuse Sprint 1-4 template parser
- Add `prompt` field to section schema (required)
- Validate prompt existence before generation
- Support nested sections (hierarchical prompts)

**Success Criteria:**
- Template parser accepts `prompt` field
- Validation fails if section lacks prompt
- Prompts are passed to LLM correctly

---

### Feature 2: Sequential Section Generation

**What:**
- Generate document section-by-section in DFS (depth-first) order
- Each section generation is a separate LLM call
- Smaller, focused prompts per section
- No post-order validation or backtracking (MVP simplification)

**DFS Traversal Example:**
```
Introduction (generate heading + content)
Features (generate heading + content)
  ├── Core Features (generate heading + content)
  └── Advanced Features (generate heading + content)
Installation (generate heading + content)
```

**Why Essential:**
- Breaks large unpredictable generation into manageable chunks
- Smaller prompts = more predictable output
- User can reason about one section at a time
- Explicit forward-only flow (simpler than bidirectional)

**Technical:**
- DFS tree traversal (recursive or stack-based)
- Generate at each node (section heading + content)
- No backtracking or update passes (defer to v2)
- Single-pass generation only

**Success Criteria:**
- Sections generated in correct DFS order
- Each section receives appropriate context
- Complete document assembled correctly

---

### Feature 3: Context Flow Between Sections

**What:**
- Later sections receive summaries of earlier sections as context
- Section prompts can reference what's been generated
- Maintains document coherence across chunks
- Context includes: section headings + key points + relationships

**Context Building Example:**
```
Section 1 (Introduction):
  Prompt: "High-level overview..."
  Context: [just sources]
  Output: "This project provides X, Y, Z..."

Section 2 (Features):
  Prompt: "List features, reference concepts from Introduction..."
  Context: [sources + summary of Introduction]
  Summary: "Introduction established: X, Y, Z"
  Output: "Building on X, our features include..."

Section 3 (Installation):
  Prompt: "Step-by-step install, assume user read Features..."
  Context: [sources + summaries of Introduction + Features]
  Summary: "Introduction: X, Y, Z. Features: A, B, C"
  Output: "To use features A, B, C, first install..."
```

**Why Essential:**
- Avoids disjointed sections
- Later sections can reference earlier content appropriately
- Creates natural flow despite chunked generation
- Enables "assume user read X" style prompts

**Technical:**
- Pass summaries (not full text) of previous sections
- Include section headings + key points (3-5 sentences max)
- Limit context size to prevent token overflow
- Build context incrementally (append each section)

**Success Criteria:**
- Later sections demonstrate awareness of earlier content
- Cross-references are appropriate and accurate
- Document reads coherently end-to-end

---

### Feature 4: Section Review Checkpoints (Optional)

**What:**
- After each section generation, optionally pause for review
- User can: accept, regenerate with feedback, edit, or quit
- Flexible control level via CLI flags
- Two modes: interactive (pause) vs auto (no pause)

**CLI Flags:**
```bash
# Interactive mode (pause for review after each section)
doc-update --interactive template.json

# Auto mode (generate all sections without pausing)
doc-update --auto template.json
doc-update template.json  # auto is default
```

**Review Flow (Interactive Mode):**
```
Generating section: Introduction
  Using sources: README.md, pyproject.toml
  [progress...]
  ✅ Generated 234 words

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Introduction

doc_evergreen is a tool for maintaining living documentation...
[full section content]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Options:
  [a] Accept and continue to next section
  [r] Regenerate with feedback
  [e] Edit manually in $EDITOR
  [q] Quit (save progress so far)

Choice: _
```

**User Actions:**
- **Accept**: Continue to next section (most common)
- **Regenerate**: User provides feedback, retry section with modified prompt
- **Edit**: Open section in $EDITOR, save changes, continue
- **Quit**: Save progress to date, exit cleanly

**Why Essential:**
- Ultimate "guardrail" - user can steer at each step
- Catch bad sections before continuing
- Prevents need to regenerate entire document
- Builds confidence through control

**Technical:**
- Simple CLI prompt after each section (using `input()`)
- Accept: continue to next section (default)
- Regenerate: take user feedback, retry section with modified prompt
- Edit: `subprocess.run(["$EDITOR", temp_file])`, read changes
- Quit: save partial document to `.partial.md`, exit cleanly

**Success Criteria:**
- Review checkpoint appears after each section (interactive mode)
- All four actions work correctly
- Auto mode skips checkpoints (for CI/batch)
- Partial progress is saved on quit

---

### Feature 5: Source Validation & Visibility

**What:**
- **Validate sources before generation** (fail early)
- **Show which sources are used** for each section
- **Clear error when sources are empty**
- Prevents ISSUE-001 and addresses ISSUE-003

**Before Generation (Validation Phase):**
```bash
$ doc-update template.json

📋 Validating template sources...

Section: Introduction
  Sources: ["README.md", "pyproject.toml"]
  ✅ Found: README.md (2.3 KB)
  ✅ Found: pyproject.toml (1.1 KB)

Section: Features
  Sources: ["src/**/*.py"]
  ✅ Found 12 files: src/core/generator.py, src/core/template.py, ...

Section: Installation
  Sources: ["setup.py"]
  ❌ ERROR: No files found matching "setup.py"

❌ Validation failed: Section 'Installation' has no sources
Aborting: Cannot generate with missing sources.
```

**During Generation (Progress Display):**
```bash
Generating section: Introduction
  Using sources: README.md, pyproject.toml
  Tokens: 2,450 (sources) + 150 (prompt) = 2,600 total
  [calling LLM...]
  ✅ Generated 234 words in 8.3s

Generating section: Features
  Using sources: 12 Python files from src/ (8.7 KB total)
  Context: Summary of Introduction (3 sentences)
  Tokens: 8,900 (sources) + 150 (prompt) + 100 (context) = 9,150 total
  [calling LLM...]
  ✅ Generated 456 words in 12.1s
```

**Why Essential:**
- **Fixes ISSUE-001**: Prevents tool from continuing with empty context
- **Addresses ISSUE-003**: Shows which sources affect each section
- **Builds confidence**: User knows sources exist before generation starts
- **Debugging aid**: Clear visibility into source resolution
- **Performance transparency**: Shows token usage per section

**Technical:**
- Validate all section sources before starting generation (upfront check)
- Display resolved file paths at section level (list up to 5, then "and N more")
- Fail with clear error if any section has zero sources
- Show source list when generating each section (during progress)
- Optionally show token counts (via `--verbose` flag)

**Success Criteria:**
- Tool fails fast if any section lacks sources
- User sees clear list of files used per section
- Error message explains how to fix missing sources
- Token usage is visible (helpful for cost estimation)

---

## Success Criteria

**The MVP succeeds if:**

1. ✅ Template with section-level prompts parses and validates correctly
2. ✅ Each section generates sequentially with appropriate sources
3. ✅ Later sections receive context from earlier sections
4. ✅ Source validation prevents empty context errors (ISSUE-001 fixed)
5. ✅ User sees which sources are used per section (ISSUE-003 addressed)
6. ✅ Interactive mode lets user review/steer at checkpoints
7. ✅ Output is more coherent and steerable than single-shot generation
8. ✅ User feels more control over output quality

**Test Case (Complete):**

```json
{
  "document": {
    "title": "doc_evergreen README",
    "output": "README.md",
    "sections": [
      {
        "heading": "Overview",
        "prompt": "High-level overview of doc_evergreen purpose (2-3 paragraphs). Emphasize living documentation that stays current.",
        "sources": ["doc_evergreen/doc-update.py", "doc_evergreen/README.md"]
      },
      {
        "heading": "Features",
        "prompt": "List key features as bullet points. Reference concepts from Overview. Focus on: template-based generation, source resolution, review workflow, chunked generation.",
        "sources": ["doc_evergreen/**/*.py"]
      },
      {
        "heading": "Getting Started",
        "prompt": "Quick start guide assuming user read Features. Include: install, basic template, first run.",
        "sources": ["doc_evergreen/doc-update.py", "pyproject.toml"],
        "sections": [
          {
            "heading": "Installation",
            "prompt": "Installation steps only. Reference package info from parent sources.",
            "sources": []  # inherits from parent
          },
          {
            "heading": "First Template",
            "prompt": "Show minimal working template example. Explain each field.",
            "sources": ["doc_evergreen/examples/*.json"]
          }
        ]
      }
    ]
  }
}
```

**Expected Behavior:**
1. **Validation Phase:**
   - Validate all sources upfront
   - Show file counts per section
   - Inherit sources correctly (Installation from parent)
   - Fail if any section has zero sources

2. **Generation Phase:**
   - Generate Overview using doc-update.py + README.md
   - Generate Features using all Python files + Overview summary
   - Generate Getting Started intro using specified files + previous sections
   - Generate Installation (nested) using inherited sources + parent context
   - Generate First Template using example JSONs + all previous context

3. **Interactive Phase (if `--interactive`):**
   - Pause after each section for review
   - Show generated content
   - Allow accept/regenerate/edit/quit

4. **Output:**
   - Produce coherent README with natural flow
   - Cross-references are appropriate ("As mentioned in Overview...")
   - Sections reference each other meaningfully

**If sources missing:** Fail with clear error before attempting generation

---

## Technical Architecture

### Component Changes

**From Sprints 1-4 (Reusing):**
- `template.py`: Template parser (extend with section-level prompts)
- `source_resolver.py`: Source resolution system (glob patterns, hierarchical inheritance)
- JSON schema validation
- Review & accept workflow

**New for Problem B MVP:**
- `chunked_generator.py`: Section-by-section generation logic (DFS traversal)
- `context_manager.py`: Track and pass section summaries
- `source_validator.py`: Validate sources before generation (upfront check)
- `review_checkpoint.py`: Interactive section review (optional)

### Data Flow

```
1. Parse Template (template.py)
   - Load JSON
   - Validate schema (including section prompts)
   - Build section tree
   ↓
2. Validate All Sources (source_validator.py - NEW)
   - Resolve sources for each section
   - Check if any section has zero sources
   - Fail early if missing sources
   ↓ (abort if validation fails)
3. Initialize Context (context_manager.py - NEW)
   - Start with empty context
   - Prepare to accumulate section summaries
   ↓
4. For each section in DFS order (chunked_generator.py - NEW):
   a. Show sources for this section (source_validator.py)
   b. Generate section with (sources + context) (LLM call)
   c. [Optional] Review checkpoint (review_checkpoint.py)
   d. Add summary to context (context_manager.py)
   ↓
5. Assemble complete document (chunked_generator.py)
   - Concatenate all sections
   - Format as markdown
   ↓
6. Final Review & Accept (existing Sprint 4 workflow)
   - Show diff
   - Accept/reject/edit
```

### File Structure

```
doc_evergreen/
├── doc-update.py              # CLI entry (extend for --interactive)
├── core/
│   ├── __init__.py
│   ├── template.py            # Template parser (add section prompt schema)
│   ├── source_resolver.py     # Source resolution (reuse from Sprints 1-4)
│   ├── generator.py           # Generator interface (single-shot - existing)
│   ├── chunked_generator.py   # NEW: Section-by-section generation
│   ├── context_manager.py     # NEW: Context flow between sections
│   ├── source_validator.py    # NEW: Validate sources before generation
│   ├── review_checkpoint.py   # NEW: Interactive section review
│   └── review.py              # Review workflow (existing - extend for section checkpoints)
├── templates/
│   └── readme-chunked.json    # Example template with section prompts
└── tests/
    ├── test_chunked_generator.py
    ├── test_context_manager.py
    ├── test_source_validator.py
    └── test_review_checkpoint.py
```

---

## Implementation Phases

### Week 1: Core Infrastructure (Sprint 5)

**Goals:**
- Extend template format for section-level prompts
- Implement sequential DFS generation (no backtracking)
- Add source validation (ISSUE-001 fix)
- Basic context flow between sections

**Deliverables:**
1. Updated template schema with section `prompt` field (required)
2. `ChunkedGenerator` with DFS traversal (forward-only)
3. `SourceValidator` that checks sources upfront (fail early)
4. Basic `ContextManager` (pass section summaries)
5. Basic source visibility (show files per section)
6. Generate document section-by-section (no review checkpoints yet)

**Test:**
- Generate README with 3 sections
- Verify context flows from section 1 → 2 → 3
- Verify tool fails if sources are missing
- Verify sources are shown per section

**Success Metrics:**
- Template parser accepts `prompt` field
- DFS traversal generates sections in correct order
- Context summaries are passed to later sections
- Source validation fails early with clear error
- Source lists are visible during generation

---

### Week 2: Polish & Testing (Sprint 6)

**Goals:**
- Add section review checkpoints (interactive mode)
- Improve source visibility (ISSUE-003 complete)
- Test with real templates (doc_evergreen's own README)
- Documentation for chunked generation

**Deliverables:**
1. `ReviewCheckpoint` component (accept/regenerate/edit/quit)
2. `--interactive` and `--auto` CLI flags
3. Section review checkpoint UI (simple CLI prompts)
4. Enhanced source display (file counts, sizes, token estimates)
5. User documentation for chunked generation workflow
6. Test with doc_evergreen's own README (dogfooding)

**Test:**
- Interactive generation with section steering
- Regenerate a section with feedback
- Edit a section manually mid-generation
- Quit and resume from checkpoint

**Success Metrics:**
- Review checkpoints appear after each section (interactive mode)
- All four user actions work (accept/regenerate/edit/quit)
- Auto mode skips checkpoints (for CI/batch)
- User can steer output at each section
- Documentation is clear and complete

---

### Week 3: Refinement & Buffer (Sprint 7 - if needed)

**Goals:**
- Handle edge cases (empty sections, deeply nested hierarchies)
- Improve error messages
- User testing with real projects
- Performance optimization (if needed)

**Deliverables:**
1. Edge case handling (0-source sections, empty prompts, deep nesting)
2. Clear error messages for common issues
3. User testing with 2-3 real projects (not just doc_evergreen)
4. Performance profiling (token usage, timing)
5. Optimization if needed (caching, batching)

**Test:**
- Complex multi-level docs (3+ levels of nesting)
- Edge cases (missing prompts, circular references)
- Large documents (10+ sections)
- Performance under realistic load

**Success Metrics:**
- No crashes on edge cases
- Error messages are clear and actionable
- Performance is acceptable (<30s per section)
- User testing validates workflow

---

## Dependencies & Requirements

### Builds On (Sprints 1-4):
- Template parsing infrastructure (`template.py`)
- Source resolution system (`source_resolver.py`)
- Hierarchical source inheritance
- JSON template format
- Review & accept workflow (`review.py`)

### External Dependencies:
- PydanticAI (LLM calls)
- Claude/GPT API (text generation)
- Python 3.11+ (pathlib, asyncio)

### New Dependencies (if any):
- Potentially prompt optimization library (for context summarization)
- Or use LLM itself to generate summaries (self-referential)

---

## What's Explicitly Deferred (v2 - Future Sprints)

**These features are valuable but NOT in MVP:**

### Deferred to Version 2 (Phase 2):

1. **Post-order validation and updates**
   - Generate all sections first, then validate consistency
   - Update earlier sections based on later context
   - Requires backtracking logic
   - **Why deferred**: MVP is forward-only (simpler)
   - **Reconsider when**: Inconsistencies are common across sections

2. **Sibling consistency checks**
   - Ensure sibling sections don't overlap
   - Validate that all aspects are covered
   - Cross-section validation rules
   - **Why deferred**: Section prompts handle this (user responsibility)
   - **Reconsider when**: Overlaps/gaps occur frequently

3. **Tree backtracking** (generate → validate → refine loop)
   - Iteratively improve sections
   - Complex state management
   - **Why deferred**: Single-pass is simpler for MVP
   - **Reconsider when**: One-shot quality is insufficient

### Deferred to Version 3 (Phase 3):

4. **Dynamic tree growth**
   - LLM proposes new sections
   - User approves structure changes
   - Template evolution during generation
   - **Why deferred**: Static templates test core assumptions first
   - **Reconsider when**: Users manually add sections frequently

5. **State management / resume capability**
   - Save progress after each section
   - Resume from checkpoint if interrupted
   - Version control for incremental updates
   - **Why deferred**: Generate full doc is fast enough for MVP
   - **Reconsider when**: Generation takes >10 minutes

6. **Advanced forward reference handling**
   - Sections referencing not-yet-generated content
   - Placeholder resolution
   - Multi-pass generation
   - **Why deferred**: Adds significant complexity
   - **Reconsider when**: Forward references are common pattern

### Issue-Specific:

7. **Error pattern detection (ISSUE-002)**
   - Detect when LLM generates error messages instead of content
   - **Why deferred**: Section review handles this (user catches it)
   - **Reconsider when**: Users accept error content frequently

**Rationale:** MVP focuses on core chunked generation with user control. Advanced features can build on this foundation after learning what matters.

---

## Risks & Mitigations

### Risk 1: Context Overflow
**Problem:** Passing summaries of all previous sections may exceed token limits

**Mitigation:**
- Keep summaries concise (key points only, 3-5 sentences max)
- Limit context to N most recent sections (e.g., last 3)
- Monitor token usage per section (show in progress)
- Truncate context if needed (warn user)

---

### Risk 2: Section Coherence
**Problem:** Chunked generation may produce disjointed sections

**Mitigation:**
- Explicitly pass section summaries as context
- Design prompts to reference earlier sections
- Test with real documents (doc_evergreen README)
- Iterate on context strategy based on output quality
- Use LLM to generate section summaries (self-referential)

---

### Risk 3: Interactive Mode UX
**Problem:** Review checkpoints may feel tedious for many sections

**Mitigation:**
- Make `--auto` mode the default (no checkpoints)
- Keep review UI simple (single-key choices)
- Allow batching (review every N sections - future)
- Provide quick "accept all remaining" option (future)

---

### Risk 4: Source Validation Complexity
**Problem:** Validating sources for deeply nested sections may be slow

**Mitigation:**
- Cache resolved sources (don't re-glob for each section)
- Show progress during validation ("Validating 5/12 sections...")
- Fail fast on first missing source (don't validate all)
- Parallelize source resolution (future optimization)

---

### Risk 5: Prompt Engineering Burden
**Problem:** Users must write good prompts for each section

**Mitigation:**
- Provide example templates with well-designed prompts
- Include prompt guidelines in documentation
- Show prompt effectiveness in examples
- Consider prompt suggestions in future (LLM-assisted)

---

## Metrics for Success

### Quantitative:
- **Section generation time**: <30s per section (acceptable)
- **Context passing overhead**: <5s per section
- **Source validation time**: <10s total (upfront)
- **User review time**: ~1min per section (interactive mode)
- **Total time**: <10min for 10-section doc (vs 30+ manual)

### Qualitative:
- User reports feeling more control over output
- Fewer full-document regenerations needed
- Higher satisfaction with section quality
- Easier to steer output toward needs
- More confidence in generated content

### Bug Fixes:
- ✅ ISSUE-001 resolved (no more empty context errors)
- ✅ ISSUE-003 resolved (source visibility clear)
- ⏸️ ISSUE-002 deferred (section review handles this)

---

## Timeline

**Total: 2-3 weeks**

**Week 1 (Sprint 5):** Core infrastructure (template prompts, DFS generation, source validation, context flow)
**Week 2 (Sprint 6):** Polish & testing (review checkpoints, source visibility, dogfooding)
**Week 3 (Sprint 7):** Buffer for refinement (edge cases, error messages, user testing)

**Ready to start:** After user confirms MVP definition

---

## Next Actions

1. **Review & approve** this MVP definition
2. **Break into executable sprints** using `/plan-sprints` or manual sprint planning
3. **Update issue tracker:**
   - Assign ISSUE-001 to Sprint 5 (source validation)
   - Assign ISSUE-003 to Sprint 5 (source visibility)
   - Update ISSUE-002 (defer - section review handles it)
4. **Begin Sprint 5** (Week 1 - core infrastructure)

---

## Document History

- **2025-01-18**: Initial MVP definition (Problem B - Chunked Generation)
- **Builds on:** Sprints 1-4 (Problem A - Template-based Single-shot)
- **References:**
  - ISSUE-001 (empty context) - FIXED in this MVP
  - ISSUE-003 (source visibility) - ADDRESSED in this MVP
  - ISSUE-002 (error messages) - DEFERRED (section review handles)

---

## Philosophy Alignment

This MVP embodies the project's core principles:

**Ruthless Simplicity:**
- 5 features only (section prompts, sequential generation, context flow, source validation, review checkpoints)
- Forward-only generation (no backtracking)
- Manual section specification (no auto-discovery)
- Simple CLI (no web UI)

**Start Minimal, Grow as Needed:**
- Test section-by-section approach first
- Learn what control points matter
- Don't build features we might not need (dynamic growth, backtracking)

**Present-Moment Focus:**
- Solves today's pain (unpredictable single-shot generation)
- Uses today's tools (LLM + JSON templates)
- No future-proofing (state management, resume capability)

**Trust in Emergence:**
- Section patterns will emerge through use
- Quality standards will be discovered through testing
- Right features will prove themselves through need

**User Control & Confidence:**
- Explicit prompts give users strong input guardrails
- Review checkpoints give users strong output control
- Source validation builds confidence (fail early)
- Visibility builds trust (show what's happening)

---

**This is the MVP for Problem B. Nothing more, nothing less. Every feature serves the core goal: giving users control and predictability in section-by-section documentation generation.**
