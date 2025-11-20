# Sprint 8: Template-Based Regeneration Core

**Duration:** 4 days
**Goal:** Build template-based regeneration workflow with diff preview
**Value Delivered:** Users can regenerate docs from templates and preview changes before applying

---

## Why This Sprint?

This establishes the new regeneration workflow that addresses the core gap in v0.2.0: users couldn't easily update documentation as code changed. By building on the existing template structure (no new syntax needed), we maintain simplicity while adding powerful regeneration capabilities.

---

## Deliverables

### 1. New `regen-doc` Command (~150 lines + ~100 lines tests)

**What it does:**
- New CLI command that replaces `doc-update`
- Reads existing JSON templates
- Generates new documentation content
- Compares with existing documentation
- Shows diff for user approval
- Applies changes or exits

**Why this sprint:**
- Foundation for entire regeneration workflow
- Builds on existing template schema (no schema changes needed)
- Resolves **ISSUE-004** (CLI help text) by creating new clear help text

**Key decisions:**
- Use existing `Template`, `Document`, `Section` schema classes
- Use `ChunkedGenerator` (existing, reliable)
- Simple unified diff initially (sufficient, no library needed)
- Interactive approval workflow (y/n prompt)

**Implementation notes:**
```python
# Leverages existing schema:
from doc_evergreen.core.template_schema import parse_template, Template
from doc_evergreen.chunked_generator import ChunkedGenerator

# New command structure:
@click.command()
@click.argument("template_path", type=click.Path(exists=True))
@click.option("--auto-approve", is_flag=True, help="Apply changes without approval")
@click.option("--output", type=click.Path(), help="Override template output path")
def regen_doc(template_path: str, auto_approve: bool, output: str | None):
    """Regenerate documentation from template with change preview.

    Examples:
      regen-doc template.json          # Preview changes, ask approval
      regen-doc --auto-approve t.json  # Apply automatically
    """
    pass
```

### 2. Change Detection Module (~100 lines + ~80 lines tests)

**What it does:**
- Compares new content against existing file
- Identifies what changed (added, removed, modified lines)
- Generates unified diff format
- Handles missing files gracefully

**Why this sprint:**
- Core capability for preview workflow
- Reusable for future diff improvements
- Simple implementation (Python's `difflib` sufficient)

**Implementation notes:**
```python
from difflib import unified_diff
from pathlib import Path

def detect_changes(
    existing_path: Path,
    new_content: str
) -> tuple[bool, list[str]]:
    """Detect changes between existing file and new content.

    Returns:
        (has_changes, diff_lines)
    """
    if not existing_path.exists():
        return (True, ["NEW FILE"])

    existing = existing_path.read_text()
    if existing == new_content:
        return (False, [])

    diff = unified_diff(
        existing.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=str(existing_path),
        tofile=str(existing_path),
    )
    return (True, list(diff))
```

### 3. Primary Test Case + Example Templates (~200 lines JSON + docs)

**What it does:**
- Provides PRIMARY test case: `templates/amplifier_readme.json`
- Uses existing `amplifier/README.md` as real-world validation target
- Includes 2 additional example templates for reference
- Resolves **ISSUE-005** (no example templates)

**Why this sprint:**
- Essential for onboarding new users
- Validates template schema works with real project
- Reference for users creating their own templates
- **Test case used throughout all v0.3.0 sprints for validation**

**PRIMARY TEST CASE:**

**Test Case 1: `templates/amplifier_readme.json`** (Real-world regeneration target)
```json
{
  "document": {
    "title": "Amplifier - README",
    "output": "amplifier/README.md",
    "sections": [
      {
        "heading": "Introduction",
        "prompt": "Write a brief introduction to the Amplifier Memory System...",
        "sources": ["amplifier/README.md", "ai_context/MODULAR_DESIGN_PHILOSOPHY.md"]
      },
      {
        "heading": "Architecture",
        "prompt": "Describe the overall architecture of the Amplifier system...",
        "sources": [
          "amplifier/README.md",
          "amplifier/memory/README.md",
          "amplifier/extraction/README.md",
          "amplifier/search/README.md",
          "amplifier/validation/README.md",
          "amplifier/knowledge_synthesis/README.md",
          "amplifier/content_loader/README.md",
          "amplifier/config/README.md",
          "amplifier/ccsdk_toolkit/README.md",
          "amplifier/knowledge_integration/README.md",
          "amplifier/knowledge_mining/README.md"
        ]
      },
      // ... 7 more sections covering installation, usage, testing, etc.
    ]
  }
}
```

**Note:** This template already exists at `doc_evergreen/templates/amplifier_readme.json` and will be the primary validation test throughout v0.3.0.

**ADDITIONAL EXAMPLE TEMPLATES:**

**Example 1: `examples/simple.json`** (Basic 2-section template)
```json
{
  "document": {
    "title": "Simple Project Documentation",
    "output": "SIMPLE_EXAMPLE.md",
    "sections": [
      {
        "heading": "Overview",
        "prompt": "Explain what this project does, its purpose, and main features.",
        "sources": ["README.md", "src/main.py"]
      },
      {
        "heading": "Installation",
        "prompt": "Provide clear installation instructions with examples.",
        "sources": ["setup.py", "requirements.txt"]
      }
    ]
  }
}
```

**Example 2: `examples/nested.json`** (Nested sections)
```json
{
  "document": {
    "title": "Advanced Documentation Example",
    "output": "ADVANCED_EXAMPLE.md",
    "sections": [
      {
        "heading": "Getting Started",
        "prompt": "Introduction to the project",
        "sources": ["README.md"],
        "sections": [
          {
            "heading": "Installation",
            "prompt": "How to install",
            "sources": ["setup.py"]
          },
          {
            "heading": "Configuration",
            "prompt": "Configuration options",
            "sources": ["config.py"]
          }
        ]
      }
    ]
  }
}
```

### 4. Basic Template Documentation (~150 lines markdown)

**What it does:**
- Creates `TEMPLATES.md` explaining template structure
- Documents all fields (heading, prompt, sources, sections)
- Shows how sources work (per-section specification)
- Partially resolves **ISSUE-006** (template vs CLI sources)

**Why this sprint:**
- Users need to understand template structure
- Reduces confusion about how to create templates
- Reference documentation for field meanings

**Structure:**
```markdown
# Template Guide

## Template Structure
(Explain JSON structure with existing schema)

## Fields Reference
- heading: Section title
- prompt: What to generate for this section
- sources: List of file patterns for this section
- sections: Nested subsections

## Creating Templates
(Step-by-step guide)

## Examples
(Reference to examples directory)
```

---

## What Gets Punted (Deliberately Excluded)

- **Advanced diff libraries** - Python's `difflib` sufficient for MVP
- **Fancy diff UI** - Simple text diff in terminal works
- **Template validation beyond existing** - Current validation adequate
- **Section-level regeneration** - Full doc regen only (simpler)
- **Custom placeholder syntax** - Use existing JSON structure
- **Single-shot mode** (Issue #009) - Chunked mode sufficient

---

## Dependencies

**Requires from previous sprints:**
- Existing template schema (already exists in v0.2.0)
- ChunkedGenerator (already exists in v0.2.0)
- Source validation (already exists in v0.2.0)

**Provides for future sprints:**
- Working regen-doc command
- Change detection mechanism
- Example templates
- Template documentation

---

## Acceptance Criteria

### Must Have
- ✅ `regen-doc template.json` generates new content
- ✅ Shows clear diff of what changed
- ✅ Prompts for approval (y/n)
- ✅ Applies changes on approval
- ✅ Handles missing files gracefully
- ✅ **PRIMARY: `templates/amplifier_readme.json` works correctly (THE test case)**
- ✅ 2 additional example templates work correctly
- ✅ Basic template documentation exists
- ✅ Better CLI help text (resolves Issue #004)

### Nice to Have (Defer if time constrained)
- ❌ Colored diff output
- ❌ Word-level diff (vs line-level)
- ❌ Statistics (X lines added, Y removed)

---

## Testing Requirements

**TDD Approach:**

Follow red-green-refactor for all features:

1. **🔴 RED - Write Failing Tests:**
   ```python
   def test_regen_detects_changes():
       # Test that SHOULD pass but doesn't yet
       result = detect_changes(existing_path, new_content)
       assert result.has_changes == True
   ```

2. **🟢 GREEN - Minimal Implementation:**
   ```python
   def detect_changes(existing_path, new_content):
       # Simplest code to make test pass
       if not existing_path.exists():
           return ChangeResult(has_changes=True)
       return ChangeResult(has_changes=existing != new_content)
   ```

3. **🔵 REFACTOR - Improve Quality:**
   - Clean up code structure
   - Extract functions
   - Improve naming
   - Run tests to ensure still passing

**Unit Tests (Write First):**
- Change detection identifies modifications correctly
- Change detection handles missing files
- Diff generation produces valid unified diff format
- Template parsing works with examples
- CLI argument parsing correct

**Integration Tests (Write First):**
- Full workflow: template → generate → diff → approve → apply
- Example templates generate valid documentation
- Handles both new files and updates

**Manual Testing (After Automated Tests Pass):**
- [ ] **PRIMARY TEST:** Run `regen-doc templates/amplifier_readme.json` and verify:
  - Generates content for all 9 sections
  - Clear output showing progress
  - Readable diff comparing to existing amplifier/README.md
  - Approval prompt works
  - File gets updated on approval
  - Preserves overall structure and quality
- [ ] Run `regen-doc examples/simple.json` and verify basic workflow
- [ ] Run `regen-doc examples/nested.json` and verify nested sections work

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## What You Learn

After this sprint, you'll discover:
1. **How often users need to regenerate** → Motivates Sprint 9 iteration
2. **What diff format is most helpful** → Could improve in future
3. **What prompts generate best docs** → Improves example templates
4. **Where users get confused** → Guides Sprint 9 UX improvements

---

## Success Metrics

**Quantitative:**
- All 3 example templates generate valid docs
- Change detection accuracy: 100% (identifies all changes)
- Test coverage: >80%

**Qualitative:**
- User can run example without reading docs
- Diff output is clear and understandable
- Approval workflow feels natural

---

## Implementation Order (TDD Daily Workflow)

**Day 1: Change Detection + Tests**
- 🔴 Write failing tests for change detection
- 🟢 Implement change detection (minimal)
- 🔵 Refactor for quality
- ✅ Commit with all tests green

**Day 2: regen-doc Command + Tests**
- 🔴 Write failing tests for CLI command
- 🟢 Implement basic command structure
- 🟢 Integrate with change detection
- 🟢 Add approval workflow
- ✅ Commit with all tests green

**Day 3: Example Templates + Template Docs**
- Create 3 example templates
- Test each template manually
- Write TEMPLATES.md documentation
- ✅ Commit working examples

**Day 4: Integration Testing + Polish**
- 🔴 Write integration tests
- 🟢 Test end-to-end workflows
- 🔵 Fix any issues discovered
- Update help text (resolve Issue #004)
- ✅ Final testing and sprint review

---

## Known Limitations (By Design)

1. **Line-level diff only** - No word-level highlighting (acceptable for MVP)
2. **Terminal-only UI** - No fancy diff viewer (simpler, works everywhere)
3. **Full doc regeneration** - Can't update individual sections (simpler workflow)
4. **Manual approval required** - No auto-apply by default (safer for users)

---

## Next Sprint Preview

After Sprint 8 ships, users will want:
- Better progress feedback during generation (Sprint 9)
- Iterative refinement workflow (Sprint 9)
- Clearer source gathering documentation (Sprint 9)
