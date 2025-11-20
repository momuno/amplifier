# Feature Scope: Test Case - Basic Regeneration

**Date**: 2025-11-19
**Project**: doc_evergreen
**Status**: Feature scope defined, ready for sprint planning

---

## The ONE Problem

**Documentation drifts from reality as code evolves.**

When code changes (new features, refactored modules, updated APIs), documentation becomes stale. Developers must manually hunt down all affected docs, understand what changed, and rewrite sections to match reality. This is:
- Time-consuming (manual diffing between code and docs)
- Error-prone (easy to miss changes or introduce inconsistencies)
- Demotivating (tedious work that feels like duplication)

**Result**: Docs lag behind code, become unreliable, and eventually get ignored.

---

## The Specific User

**Solo developers or small teams maintaining 3-5+ active projects** where:
- Code evolves frequently (new features, refactoring, API changes)
- Documentation must stay accurate (READMEs, API docs, architecture guides)
- Manual sync is painful but necessary
- Time is scarce (documentation competes with development)
- Quality matters (stale docs hurt users and future maintainers)

**Current solution**: Manual regeneration
- Read source code changes
- Remember what docs reference those sources
- Open docs, find affected sections
- Rewrite sections to match reality
- Repeat for every doc, every change

**Why insufficient**:
- No systematic way to know which docs need updates
- Manual context gathering from scattered sources
- Easy to miss changes or introduce inconsistencies
- Structural drift (docs evolve format over time)
- No way to validate completeness

---

## Feature Scope Solution (5 Must-Have Features)

### 1. **Template-Based Generation**

**What**: Create `.md.template` files that lock structure with placeholder syntax.

**Why essential**: Without locked structure, each regeneration can drift format/organization. Templates ensure consistency across regenerations while allowing content to update.

**Key capabilities**:
- Placeholder syntax: `{{LLM: prompt for this section}}`
- Non-LLM sections: Static markdown preserved exactly
- Source includes: `{{INCLUDE: path/to/source.py}}`
- Clear separation: What's generated vs. what's static

**Example**:
```markdown
# Project Name

{{LLM: Write a one-sentence description based on included sources}}

## Features

{{LLM: List key features from source files}}

## Installation

```bash
pip install project-name
```

{{INCLUDE: examples/basic_usage.py}}
```

### 2. **Source Context Gathering**

**What**: Automatically read source files specified in template into LLM context.

**Why essential**: Manual context gathering (copying code, remembering what matters) is the bottleneck. Automation makes regeneration actually viable.

**Key capabilities**:
- Read files from `{{INCLUDE: path}}` directives
- Support multiple source types (Python, markdown, config files)
- Handle missing files gracefully (warn, don't fail)
- Assemble full context before LLM call

**Example flow**:
```
Template references:
- {{INCLUDE: amplifier/core.py}}
- {{INCLUDE: amplifier/cli.py}}
→ Read both files
→ Pass to LLM with template prompts
→ Generate doc sections
```

### 3. **Manual Regeneration Command**

**What**: CLI command `amplifier regen-doc <doc-path>` to regenerate on demand.

**Why essential**: Automation (watch mode, git hooks) can come later. First prove the basic flow works when manually triggered. Test case must demonstrate value before adding automation.

**Key capabilities**:
- Single command: `amplifier regen-doc amplifier/README.md`
- Uses corresponding `.md.template` file
- Gathers sources, calls LLM, writes output
- Shows progress (reading sources, calling LLM, writing)

**Example usage**:
```bash
$ amplifier regen-doc amplifier/README.md
📄 Reading template: amplifier/README.md.template
📂 Gathering sources: core.py, cli.py, config.py
🤖 Calling LLM to regenerate sections...
✅ Generated: amplifier/README.md (changed 3 sections)
```

### 4. **Structure Preservation**

**What**: Non-LLM sections (static markdown, code blocks, installation instructions) stay untouched between regenerations.

**Why essential**: Ensures docs don't randomly change format. Only content that should update (based on sources) actually updates. Everything else stays stable.

**Key capabilities**:
- Parse template into LLM vs. non-LLM sections
- Only regenerate `{{LLM: ...}}` sections
- Preserve spacing, formatting, static content exactly
- Prevent structural drift over time

**Example**:
```markdown
# Before regeneration
## Features
- Feature A (from sources)
- Feature B (from sources)

# After code adds Feature C
## Features
- Feature A (from sources)
- Feature B (from sources)
- Feature C (from sources)  ← Only this changes
```

### 5. **Change Detection**

**What**: Show diff between old and new versions, let user decide if changes are meaningful enough to keep.

**Why essential**: Not every regeneration produces meaningful updates. LLM might rephrase without adding value. User needs to see what changed and decide: "Keep update" or "Discard (no real change)".

**Key capabilities**:
- Generate new version in memory first
- Diff against current file
- Show changes in terminal (colored diff)
- Prompt: "Apply changes? [y/n]"
- Only write if user confirms

**Example**:
```bash
$ amplifier regen-doc amplifier/README.md
📄 Changes detected:

--- amplifier/README.md
+++ amplifier/README.md (regenerated)
@@ -15,7 +15,7 @@
-Supports Python 3.11+
+Supports Python 3.11-3.13

Apply changes? [y/n]: y
✅ Updated amplifier/README.md
```

---

## Success Criteria

**How we'll know the initial release succeeded:**

- [ ] **Can generate amplifier README from template + sources**
  - Template locks structure (headings, static sections)
  - Sources include core.py, cli.py, examples
  - Generated output matches expected format
  - Non-LLM sections preserved exactly

- [ ] **Can regenerate manually when sources change**
  - Command: `amplifier regen-doc amplifier/README.md`
  - Reads template, gathers sources, calls LLM
  - Completes in reasonable time (<30 seconds)
  - Shows progress feedback

- [ ] **Structure stays consistent across regenerations**
  - Same template → same structure every time
  - Only content updates, not format/organization
  - No random section reordering or heading changes

- [ ] **See diff, decide if update is meaningful**
  - Shows colored diff in terminal
  - User can accept or reject changes
  - Only writes file if user confirms
  - Prevents meaningless "rephrasing" updates

- [ ] **Friction points become visible through use**
  - Identify what's painful (template syntax? source selection? LLM prompts?)
  - Document learnings for Phase 2
  - Real usage reveals automation opportunities

---

## Test Case: amplifier/README.md

**Target document**: `amplifier/README.md`

**Why this document?**
- Real project with evolving code
- Multiple source files to include
- Mix of generated and static content
- Representative complexity (not toy example)

**Implementation steps**:
1. Create `amplifier/README.md.template` based on current README structure
2. Identify source files to include (core.py, cli.py, examples/)
3. Define LLM prompts for each generated section
4. Test regeneration flow manually
5. Validate structure preservation and change detection

**Expected sources**:
- `amplifier/core.py` - Core functionality
- `amplifier/cli.py` - CLI interface
- `examples/basic_usage.py` - Usage examples
- `pyproject.toml` - Project metadata

---

## Timeline

**Ship initial release by**: 2025-11-26 (1 week from now)

**Aggressive but achievable because**:
- Focused scope (5 features, no automation)
- Test case is real but bounded (one README)
- Manual trigger only (no watch mode, git hooks, scheduling)
- Learnings feed directly into Phase 2 planning

**What's explicitly deferred**:
- Automation (watch mode, git hooks, scheduled runs)
- Multi-doc batch processing
- Partial updates (only changed sections)
- Version control integration
- Template validation/linting
- Advanced LLM prompt engineering

---

## Version Number

**Note**: Version number (vX.Y.Z) will be determined by sprint-planner based on:
- Whether this is a breaking change (v2.0.0)
- Whether this is a new feature (v1.X.0)
- Whether this is a bugfix (v1.0.X)

This document defines WHAT to build. Sprint planning will define HOW to ship it.

---

## Next Steps

1. **Review this feature scope** - Does it solve the right problem? Are features truly must-have?
2. **Run /plan-sprints** - Break this into executable sprint plan with version number
3. **Sprint-planner will**:
   - Determine version based on scope
   - Break features into tasks
   - Estimate effort
   - Create sprint plan with deliverables

---

**Nothing is lost - everything is preserved with clear rationale and reconsider conditions.**
