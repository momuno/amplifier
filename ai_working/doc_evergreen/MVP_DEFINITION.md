# Doc-Evergreen MVP Definition

**Status**: Converged and Ready for Implementation
**Timeline**: 2 weeks
**First Test Target**: Top-level README.md

---

## The Problem We're Solving

**The ONE Problem**: Documentation drifts from reality as code evolves, and manual updates are tedious, time-consuming, and inconsistent.

**Who Has This Problem**: Solo developers and small teams maintaining multiple documentation files across projects (API docs, architecture docs, READMEs, etc.)

**Current Solution & Why It Fails**:
- **Manual updates**: Time-consuming, inconsistent quality, easy to forget
- **Full LLM regeneration**: Unpredictable output, loses good existing content
- **Copy-paste from other docs**: Inconsistent, misses context, not scalable

**The Pain**:
- Docs become stale and untrustworthy
- Fear of regenerating docs because output quality is unpredictable
- No systematic way to keep docs in sync with code changes
- Each doc update requires significant cognitive load to gather context and ensure quality

---

## The MVP Solution

### Core Value Proposition

**"Regenerate any documentation file with confidence using templates and explicit context"**

The MVP focuses on the minimal viable loop for documentation regeneration:
1. User specifies which doc to regenerate
2. User provides template structure and source context
3. System generates doc using LLM
4. User reviews and explicitly accepts/rejects output

### Scope

**In Scope**:
- Any documentation type (README, API docs, architecture docs, guides, etc.)
- Template-based structure to ensure consistency
- Explicit context gathering (user specifies source files)
- Review and accept workflow for confidence
- Single command execution: `amplifier doc-update <doc-name>`

**Out of Scope** (Explicitly Deferred):
- Automatic change detection
- Template lifecycle management
- Intelligent source discovery
- Automated quality validation
- Version control integration
- Multiple doc formats
- Collaboration features

---

## The Three Must-Have Features

### Feature 1: Template-Based Regeneration

**What**: Single configurable template that defines doc structure

**Why Essential**: Tests the core assumption that templates can capture enough structure to generate quality output consistently

**User Experience**:
```bash
amplifier doc-update README --template readme-template.md
```

**Template Structure**:
- Sections with clear purposes (Overview, Installation, Usage, etc.)
- Placeholders for content generation
- Instructions for LLM about each section's goal
- Source attribution notes

**Success Criteria**:
- Can define a template that produces 80%+ acceptable output
- Template is reusable across similar doc types
- Clear what each section should contain

### Feature 2: Context Gathering

**What**: User explicitly specifies which source files/content to include

**Why Essential**: Tests if providing explicit context is sufficient for LLM to generate coherent, accurate docs

**User Experience**:
```bash
amplifier doc-update README \
  --sources "src/main.py,docs/architecture.md,CHANGELOG.md" \
  --context "Focus on getting started guide for new users"
```

**Capabilities**:
- Accept list of file paths
- Read and include file contents as context
- Allow optional natural language context guidance
- Show what context was gathered (for debugging)

**Success Criteria**:
- User can specify relevant sources without system guessing
- LLM has sufficient context to generate accurate content
- Generated content reflects the provided sources

### Feature 3: Review & Accept Workflow

**What**: Generate to preview file, require explicit user acceptance before overwriting

**Why Essential**: Builds confidence - user always has control and can review before committing

**User Experience**:
```bash
amplifier doc-update README --sources "..." --template "..."
# Generates: README.preview.md
# Shows diff
# Prompts: "Accept changes? (y/n/edit)"
```

**Capabilities**:
- Generate to `.preview.md` file
- Show diff between current and proposed
- Three options: Accept (overwrite), Reject (discard), Edit (open in editor)
- Never overwrite without explicit confirmation

**Success Criteria**:
- User feels safe running regeneration
- Clear visibility into what would change
- Easy to iterate if output isn't perfect

---

## First Test Case: Top-Level README

**Why README First**:
- High-value document that's often stale
- Good mix of sections (overview, installation, usage)
- Real pain point for the user
- Success here validates the approach

**What We'll Learn**:
1. Is template structure sufficient for good output?
2. Can user provide enough context without intelligent discovery?
3. Does review workflow give enough confidence to use regularly?
4. What's the actual time savings vs manual updates?

**Success Metrics**:
- README regeneration takes <5 minutes (vs 30+ manual)
- Output is 80%+ acceptable without heavy editing
- User willing to use it for 5+ more docs
- Generated README is actually useful and accurate

---

## Architecture Overview

### Components

```
doc-evergreen/
├── cli.py              # Command-line interface
├── template.py         # Template loading and parsing
├── context.py          # Source file gathering and reading
├── generator.py        # LLM-based doc generation
├── reviewer.py         # Diff and accept/reject workflow
└── templates/          # Default templates
    └── readme.md       # Default README template
```

### Data Flow

```
User Command
    ↓
Load Template (template.py)
    ↓
Gather Context (context.py)
    ↓
Generate Doc (generator.py)
    ↓
Preview & Diff (reviewer.py)
    ↓
User Decision (Accept/Reject/Edit)
    ↓
Update File (if accepted)
```

### Key Design Decisions

**1. Explicit Over Automatic**
- User specifies sources (no auto-detection)
- User specifies template (no template system)
- User accepts changes (no auto-commit)
- **Why**: Simplicity, predictability, learning what's needed

**2. File-Based Templates**
- Templates are markdown files with instructions
- Easy to create, edit, version control
- No complex template language needed
- **Why**: Ruthless simplicity, leverage existing tools

**3. Preview-First Workflow**
- Never overwrite without review
- Always show diff
- Explicit acceptance required
- **Why**: Build user trust and confidence

**4. Single Command**
- One CLI command with clear options
- No daemon, no background processing
- Synchronous execution
- **Why**: Predictable, debuggable, simple

---

## Technical Specifications

### Command Interface

```bash
amplifier doc-update <doc-path> [options]

Options:
  --template PATH       Path to template file (default: auto-detect)
  --sources FILES       Comma-separated list of source files
  --context TEXT        Additional context for generation
  --no-preview         Skip preview, generate directly
  --accept             Auto-accept changes (dangerous, skip review)
```

### Template Format

```markdown
# [SECTION: Overview]
Purpose: Brief description of what this project does
Sources: README intro, main.py docstring
---

# [SECTION: Installation]
Purpose: Step-by-step installation instructions
Sources: requirements.txt, setup.py, docs/installation.md
---

# [SECTION: Usage]
Purpose: Basic usage examples
Sources: examples/, tests/, main.py
---
```

### LLM Integration

- Use Claude Code SDK for LLM calls
- Single prompt with full context
- Structured output (markdown sections)
- Include source attribution in generation

---

## Success Criteria

**MVP is successful if:**

✅ **Functional**: Can regenerate README in <5 minutes
✅ **Quality**: Output is 80%+ acceptable without heavy editing
✅ **Useful**: User actually uses it for 5+ different docs
✅ **Confidence**: User feels safe running regeneration
✅ **Learning**: Clear understanding of what features are needed next

**MVP has failed if:**

❌ Template structure is insufficient for quality output
❌ Manual context specification is too tedious
❌ Generated content requires heavy editing (>20% changes)
❌ User doesn't trust output enough to use regularly
❌ Time savings don't justify the effort

---

## Timeline & Milestones

**Week 1: Core Implementation**
- Day 1-2: CLI scaffold and template loading
- Day 3-4: Context gathering and LLM integration
- Day 5: Review workflow and diff display

**Week 2: Testing & Refinement**
- Day 1-2: First README regeneration test
- Day 3-4: Iteration based on learnings
- Day 5: Test on 2-3 more docs, validate approach

**Delivery Date**: 2 weeks from start

---

## Risks & Mitigation

### Risk 1: LLM Output Quality Insufficient
**Mitigation**:
- Start with detailed template instructions
- Iterate on prompt engineering
- Use defensive utilities from CCSDK toolkit
- Manual review catches issues before acceptance

### Risk 2: Context Specification Too Tedious
**Mitigation**:
- Keep initial test small (README only)
- Learn what context is actually needed
- If too painful, this informs Version 2 (intelligent discovery)

### Risk 3: Template Structure Inadequate
**Mitigation**:
- Start with simple, proven structure (README sections)
- User can edit template easily (just a markdown file)
- Template is input, not output - easy to iterate

### Risk 4: Scope Creep
**Mitigation**:
- Ruthlessly defer advanced features
- Focus on 3-feature loop only
- Use DEFERRED_FEATURES.md to park ideas
- Measure against success criteria, not feature list

---

## What This MVP Will Teach Us

**Key Questions to Answer**:

1. **Template Viability**: Can a simple template structure produce quality docs?
2. **Context Sufficiency**: Is explicit context specification enough, or do we need auto-discovery?
3. **Review Necessity**: Do users need the preview workflow, or would they trust direct updates?
4. **Time Savings**: What's the actual time reduction vs manual updates?
5. **Quality Threshold**: What % acceptable output is "good enough" for adoption?
6. **Reusability**: Does same template work across different docs of same type?

**What We'll Learn for Version 2**:
- Which features from DEFERRED list are most valuable
- What pain points remain after MVP
- Where automation would provide most value
- What quality metrics actually matter

---

## Philosophy Alignment

This MVP embodies the project's core principles:

**Ruthless Simplicity**:
- 3 features only
- No complex systems
- File-based templates (not template engine)
- Manual trigger (not automatic)

**Start Minimal, Grow as Needed**:
- Test core assumption first
- Learn what's actually needed
- Don't build features we might not need

**Present-Moment Focus**:
- Solves today's pain (stale docs)
- Uses today's tools (LLM + markdown)
- No future-proofing

**Trust in Emergence**:
- Base case will be discovered through use
- Template patterns will emerge naturally
- System complexity justifies itself through need

---

## Next Steps

1. **Create implementation plan** - Break down 3 features into technical tasks
2. **Set up project structure** - Create directories and scaffolding
3. **Implement Feature 1** - Template loading and parsing
4. **Implement Feature 2** - Context gathering
5. **Implement Feature 3** - Review and accept workflow
6. **Test with README** - First real-world validation
7. **Iterate based on learnings** - Refine based on test results
8. **Document findings** - What worked, what didn't, what's next

**Ready to Build!**
