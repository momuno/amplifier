# doc_evergreen - Problem B: Deferred Features

**Purpose**: This document captures all features, ideas, and enhancements explored during Problem B convergence that are explicitly NOT in the MVP (Sprints 5-7). Nothing is lost - everything is preserved with clear "reconsider when" conditions.

**Philosophy**: Deferring isn't deleting. It's strategic postponement until we learn from the MVP what actually matters.

**Context**: This captures deferrals for Problem B (chunked section-by-section generation). See `DEFERRED_FEATURES.md` for Problem A deferrals.

---

## How to Use This Document

Each deferred feature includes:
- **What**: Description of the feature
- **Why Valuable**: The insight/value this would provide
- **Why Deferred**: What must be learned first from MVP
- **Reconsider When**: Specific trigger conditions for revisiting
- **Complexity**: Estimated implementation complexity (Low/Medium/High)

---

## Phase 2: Post-Order Validation & Refinement

These features add sophistication to the basic forward-only generation model.

### 1. Post-Order Validation and Updates

**What**: After generating all sections forward, validate consistency and update earlier sections based on later context

**Why Valuable**:
- Earlier sections can reference concepts defined later
- Ensures consistency across entire document
- Fixes issues discovered only after seeing full context
- More sophisticated than single-pass generation

**Example**:
```
Pass 1 (forward): Generate all sections
Pass 2 (backward): Validate and update
  - Introduction now references specific features from later sections
  - Sections are rewritten to avoid contradictions
  - Terminology is consistent throughout
```

**Why Deferred**:
- Forward-only generation is simpler (MVP test assumption)
- Need to observe what inconsistencies actually occur
- Backtracking adds state management complexity
- Must learn if single-pass quality is sufficient

**Reconsider When**:
- Users frequently edit earlier sections after seeing later ones
- Inconsistencies between sections are common (>20% of docs)
- Forward-only generation quality is insufficient
- Users request "make Introduction match Features" explicitly

**Complexity**: High (bidirectional flow, state management, update logic)

---

### 2. Sibling Consistency Checks

**What**: Validate that sibling sections don't overlap, complement each other, and cover all aspects

**Why Valuable**:
- Prevents duplicate content across sections
- Ensures no gaps in coverage
- Improves overall document quality
- Catches structural issues automatically

**Example**:
```
Siblings: "Core Features" and "Advanced Features"
Check:
  - No feature appears in both sections
  - All features are covered (no gaps)
  - Clear distinction between core/advanced
```

**Why Deferred**:
- Section prompts should handle this (user defines distinction)
- Need to observe what overlap/gap patterns occur
- Validation rules are context-dependent
- Adds complexity without proven need

**Reconsider When**:
- Overlapping content appears frequently (>10% of docs)
- Users manually check for gaps/overlaps
- Clear validation rules emerge from usage patterns
- Sibling relationships prove problematic

**Complexity**: Medium (define rules, implement checks, handle violations)

---

### 3. Tree Backtracking (Generate → Validate → Refine Loop)

**What**: Iteratively improve sections through multiple passes

**Why Valuable**:
- Higher quality through refinement
- Fixes issues discovered during generation
- Learns from mistakes in same session
- More sophisticated than one-shot

**Example**:
```
Pass 1: Generate all sections (forward)
Pass 2: Validate consistency
Pass 3: Refine sections that failed validation
Pass 4: Final validation
```

**Why Deferred**:
- Single-pass tests core assumption (is it sufficient?)
- Multi-pass adds significant complexity
- State management for iterative refinement is hard
- Must learn if quality justifies cost (time + tokens)

**Reconsider When**:
- Single-pass quality is consistently insufficient (<70% acceptable)
- Users frequently regenerate entire docs for minor fixes
- Clear patterns emerge in what needs refinement
- Quality improvement justifies additional LLM calls

**Complexity**: High (state management, convergence criteria, loop control)

---

## Phase 3: Dynamic & Adaptive Generation

These features add intelligence and flexibility to the generation process.

### 4. Dynamic Tree Growth

**What**: LLM proposes new sections during generation, user approves structure changes

**Why Valuable**:
- Adapts structure to content (not just content to structure)
- Discovers missing sections automatically
- More flexible than static templates
- AI-assisted structure design

**Example**:
```
Template defines:
  - Introduction
  - Features
  - Installation

LLM suggests during generation:
  "I notice you have complex dependencies.
   Should I add a 'Prerequisites' section before Installation?"

User approves → new section added → generation continues
```

**Why Deferred**:
- Static templates test core assumptions first
- Adds complexity (user approval, tree modification)
- Must learn if templates are sufficient
- Dynamic structure may confuse users

**Reconsider When**:
- Users frequently add sections manually after generation
- Missing sections are predictable pattern (>30% of docs)
- Template structure proves too rigid
- Users request "suggest sections" feature

**Complexity**: High (LLM section proposals, user approval UI, tree modification)

---

### 5. State Management / Resume Capability

**What**: Save progress after each section, resume from checkpoint if interrupted

**Why Valuable**:
- Handle long-running generations (10+ sections)
- Recover from interruptions (network, crashes)
- Incremental updates (regenerate only changed sections)
- Better UX for large documents

**Example**:
```
Generation interrupted at Section 5/10
$ doc-update --resume README.json
"Resuming from Section 5: Installation..."
```

**Why Deferred**:
- Full generation is fast enough for MVP (<10 min)
- Adds complexity (state serialization, resume logic)
- Must learn if generation time is problematic
- Incremental updates may not be needed

**Reconsider When**:
- Generation regularly takes >10 minutes
- Interruptions are common problem
- Users request resume capability explicitly
- Large documents (20+ sections) are frequent

**Complexity**: Medium (state serialization, checkpoint files, resume logic)

---

### 6. Advanced Forward Reference Handling

**What**: Sections can reference not-yet-generated content with placeholder resolution

**Why Valuable**:
- "See Installation section below" works naturally
- More flexible writing style
- Resolves placeholders after generation
- Sophisticated cross-referencing

**Example**:
```
Section 2 (Features):
  "To use this feature, see {{ref:installation}} below"

Section 5 (Installation):
  [generated]

Post-processing:
  Replace {{ref:installation}} with proper link/reference
```

**Why Deferred**:
- Adds complexity (placeholder syntax, resolution logic)
- Context flow handles most cases (backward references)
- Must learn if forward references are needed
- May confuse users/LLM

**Reconsider When**:
- Forward references are requested frequently
- Context flow proves insufficient for natural writing
- Clear patterns emerge in reference types
- Users manually add forward references

**Complexity**: Medium (placeholder syntax, resolution, validation)

---

## Issue-Specific Deferrals

### 7. Automatic Error Pattern Detection (ISSUE-002)

**What**: Detect when LLM generates error messages instead of actual content

**Why Valuable**:
- Catches "missing context" errors automatically
- Prevents acceptance of bad content
- Builds confidence in automation
- Reduces manual review burden

**Example**:
```
Generated content:
  "Error: Could not find information about X in provided sources"

Tool detects error pattern and warns:
  "⚠️ Section appears to contain error message. Review carefully."
```

**Why Deferred**:
- Section review handles this (user catches error content at checkpoint)
- Source validation (Feature 5) prevents most cases (ISSUE-001 fix)
- Error patterns may be hard to detect reliably
- Manual review is acceptable for MVP

**Reconsider When**:
- Users accept error content frequently (>5% of sections)
- Clear error patterns emerge that are detectable
- Source validation proves insufficient
- Automatic detection is explicitly requested

**Complexity**: Low (pattern matching) to Medium (LLM-based detection)

**Note**: Marked as DEFERRED in issue tracker - section review workflow provides manual detection.

---

## Optimizations: Performance & UX

### 8. Parallel Section Generation

**What**: Generate independent sections in parallel instead of sequentially

**Why Valuable**:
- Faster total generation time (3-5x speedup)
- Better resource utilization
- Scales to large documents
- Improved UX (less waiting)

**Example**:
```
Sequential: Section 1 (30s) → Section 2 (30s) → Section 3 (30s) = 90s total
Parallel: Sections 1, 2, 3 (30s each) = 30s total (if independent)
```

**Why Deferred**:
- Sequential is simpler for MVP
- Context flow requires ordering (later sections need earlier)
- Only some sections can be parallelized (siblings only)
- Must learn if generation time is problematic

**Reconsider When**:
- Generation time is primary complaint
- Documents have many independent siblings
- Users explicitly request faster generation
- Clear opportunities for parallelization emerge

**Complexity**: High (dependency analysis, parallel LLM calls, context management)

---

### 9. Context Summarization Options

**What**: Multiple strategies for summarizing earlier sections (full text, key points, custom)

**Why Valuable**:
- Flexibility for different use cases
- Optimize token usage vs coherence
- User control over context detail
- Performance tuning

**Options**:
```
--context-mode=full      # Full text of previous sections
--context-mode=summary   # LLM-generated summaries (default)
--context-mode=headings  # Just section headings
--context-mode=custom    # User-defined summarization prompt
```

**Why Deferred**:
- Simple summary (Feature 3) tests assumption first
- Must learn if context detail matters
- Adds complexity (multiple modes, configuration)
- Default may be sufficient

**Reconsider When**:
- Users complain about context quality
- Token usage is problematic
- Clear cases emerge where different modes needed
- Performance/quality trade-offs are explicit

**Complexity**: Medium (multiple modes, configuration, testing)

---

### 10. Smart Section Ordering

**What**: LLM suggests optimal section order based on content dependencies

**Why Valuable**:
- Improves document flow automatically
- Handles complex dependencies
- Reduces manual ordering effort
- AI-assisted structure optimization

**Example**:
```
Template order: Features → Installation → Prerequisites
LLM suggests: Prerequisites → Installation → Features
Reason: "Installation depends on Prerequisites"
```

**Why Deferred**:
- User-defined order tests assumption (is manual sufficient?)
- Adds complexity (dependency analysis, reordering)
- DFS order may be optimal for most cases
- Must learn if ordering is problematic

**Reconsider When**:
- Users frequently reorder sections manually
- Dependency issues are common (forward references)
- Clear patterns emerge in optimal ordering
- Users request "suggest order" feature

**Complexity**: Medium (dependency analysis, topological sort, user confirmation)

---

## Advanced Features: Future Vision

### 11. Multi-Document Coordination

**What**: Generate multiple related documents with consistency across them

**Why Valuable**:
- Keep README, API docs, guides consistent
- Share context across documents
- Single source of truth
- Portfolio-level documentation

**Example**:
```
Generate:
  - README.md (high-level)
  - API.md (technical details)
  - GUIDE.md (tutorials)

With consistency:
  - Same terminology
  - Consistent examples
  - Cross-references work
```

**Why Deferred**:
- Single-document generation must work first
- Cross-document coordination is complex
- Must learn patterns in multi-doc workflows
- Scope is significantly larger

**Reconsider When**:
- Users generate multiple related docs frequently
- Inconsistency across docs is common problem
- Clear patterns emerge in multi-doc relationships
- Portfolio-level tooling is requested

**Complexity**: High (cross-doc context, consistency rules, coordination)

---

### 12. Template Learning & Improvement

**What**: System learns from corrections and improves prompts/templates over time

**Why Valuable**:
- Templates evolve with usage
- Reduces manual prompt engineering
- Captures best practices automatically
- AI-assisted continuous improvement

**Example**:
```
User frequently changes:
  - "List features" → "List features with examples"

System suggests:
  "I notice you add examples frequently.
   Update template prompt to include examples by default?"
```

**Why Deferred**:
- Static templates test assumptions first
- Learning requires significant usage data
- Complexity is high (ML, feedback loops)
- Must observe patterns before automating

**Reconsider When**:
- Same manual corrections are made repeatedly (>10 times)
- Clear patterns emerge in what works/doesn't
- Users request "learn from my edits" feature
- Template quality improvement is measurable

**Complexity**: Very High (ML, feedback collection, template updates)

---

### 13. Real-Time Collaboration

**What**: Multiple users review/edit sections simultaneously during generation

**Why Valuable**:
- Team documentation workflows
- Parallel review reduces time
- Distributed expertise
- Modern collaborative UX

**Example**:
```
Section 1 generated → User A reviews
Section 2 generated → User B reviews (parallel)
Section 3 generated → Both review
```

**Why Deferred**:
- Solo workflow must work first
- Collaboration adds significant complexity
- Must learn team patterns
- Infrastructure needs (websockets, etc.)

**Reconsider When**:
- Multiple users adopt the tool
- Team coordination is pain point
- Parallel review is requested
- Collaboration infrastructure exists

**Complexity**: Very High (real-time sync, conflict resolution, UI)

---

## Summary Statistics

**Total Features Explored**: 13
**Phase 2 (Post-Order Validation)**: 3 features
**Phase 3 (Dynamic & Adaptive)**: 4 features
**Issue-Specific**: 1 feature (ISSUE-002)
**Optimizations**: 3 features
**Advanced/Future**: 2 features

**Key Insight**: We explored 13 additional features for Problem B but are building only 5 core features for MVP. This is excellent convergence - 72% of ideas thoughtfully deferred with clear reconsider conditions.

---

## Relationship to Problem A Deferrals

**Problem A deferrals** (see `DEFERRED_FEATURES.md`) focus on:
- Template lifecycle management
- Intelligent source discovery
- Automated quality validation
- Git integration
- Multi-format output

**Problem B deferrals** (this document) focus on:
- Advanced generation strategies (post-order, backtracking)
- Dynamic structure (tree growth, smart ordering)
- Performance optimizations (parallel, caching)
- Collaboration features

**Complementary**: Problem A deferrals improve input/discovery, Problem B deferrals improve generation/control.

---

## Using This Document

**During MVP Development (Sprints 5-7)**:
- Resist adding deferred features
- Reference this when tempted to expand scope
- Use as reminder of what we're learning toward
- Park new ideas here (don't implement immediately)

**After MVP Success**:
- Review "Reconsider When" conditions
- Identify which triggers have occurred
- Prioritize based on actual learnings (not speculation)
- Update this document as features are built or new ideas emerge

**When New Ideas Come Up**:
- Add to appropriate section (Phase 2/3, Optimizations, etc.)
- Include reconsider conditions (specific, measurable)
- Don't lose the insight
- Resist immediate implementation

---

## Decision Framework

**When considering a deferred feature:**

1. **Has the trigger condition occurred?**
   - If no → keep deferred
   - If yes → evaluate priority

2. **Do we have data to validate the need?**
   - If no → run experiment first
   - If yes → estimate impact

3. **What's the complexity vs value?**
   - High complexity, low value → defer longer
   - Low complexity, high value → consider for next sprint
   - High complexity, high value → break into phases

4. **Does it align with philosophy?**
   - Ruthless simplicity → favor simpler alternatives
   - Trust in emergence → build only proven needs
   - Present-moment focus → solve current pain, not hypothetical

---

## Philosophy Alignment

This deferral strategy embodies:

**Ruthless Simplicity**:
- Build 28% of explored features (5 of 18 total)
- Learn what matters through use
- Avoid premature complexity

**Trust in Emergence**:
- Features will prove their necessity
- Patterns will reveal what to build next
- Right next step becomes obvious through usage

**Present-Moment Focus**:
- Solve today's problem (lack of control in generation)
- Don't build for hypothetical futures (dynamic growth, collaboration)
- Let needs drive development (not speculation)

**Learning Stance**:
- MVP teaches what features matter
- Deferred features compete for next sprint based on data
- Data beats speculation

---

## Next Sprint Candidates (After MVP Success)

**If MVP succeeds, these are likely first candidates:**

1. **Post-Order Validation** (Phase 2)
   - Addresses consistency issues discovered in MVP
   - Moderate complexity, high value
   - Natural extension of forward generation

2. **State Management** (Phase 3)
   - If generation time proves problematic
   - Enables resume capability
   - Moderate complexity

3. **Parallel Generation** (Optimization)
   - If speed is primary complaint
   - High impact on UX
   - High complexity but clear payoff

**Priority will be determined by MVP learnings, not pre-planning.**

---

**Nothing is lost. Everything is preserved. The best features will prove themselves through use.**
