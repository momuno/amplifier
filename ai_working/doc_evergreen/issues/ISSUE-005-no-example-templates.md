# ISSUE-005: No Example Templates or Documentation About Template Creation

**Status:** Open
**Priority:** High
**Type:** Enhancement (Documentation)
**Created:** 2025-11-19
**Updated:** 2025-11-19

---

## Description

Users attempting to use doc_evergreen for the first time don't know where to find example templates or how to create their own. There are no example templates in the repository and no documentation explaining the template structure or creation process.

## User Feedback

> "where is the template.json i'm supposed to pass in. does one not exist yet?"

## Reproduction Steps

1. Clone/download the doc_evergreen project
2. Try to run `doc-update` command
3. Realize you need a template.json file
4. Search for example templates in the repository
5. Find none exist

**Frequency:** Always (affects all first-time users)

## Expected Behavior

The project should provide:
1. **Example templates directory**: `doc_evergreen/examples/` or `doc_evergreen/templates/examples/`
2. **Multiple example templates**:
   - Simple example (1-2 sections)
   - Complex example (nested sections)
   - Real-world example (documenting doc_evergreen itself)
3. **Template documentation**:
   - JSON structure explanation
   - Field descriptions (`heading`, `prompt`, `sources`, `output`)
   - When to use chunked vs single-shot mode
   - How to specify sources (per-section vs CLI)
4. **README section**: "Getting Started" with template examples

## Actual Behavior

- No example templates exist in the repository
- No templates directory
- README doesn't explain template structure
- Users must guess or read source code to understand format
- Only way to learn is trial and error

## Root Cause

**Location:** Repository structure / Documentation gap

**Technical Explanation:**

The project has:
- ✅ Template parsing (`template_schema.py`)
- ✅ Template validation (`validate_template()`)
- ❌ No example templates
- ❌ No documentation about template creation

This is a documentation and onboarding gap, not a code issue.

## Impact Analysis

**Severity:** High - Blocks first-time users from using the tool

**User Impact:**
- Cannot use tool without creating template from scratch
- Must read source code to understand structure
- Trial and error leads to frustration
- Reduces tool adoption

**Workaround:**
1. Read `template_schema.py` to understand structure
2. Create template manually based on dataclass definitions
3. Experiment until template works

## Acceptance Criteria

To consider this issue resolved:

- [ ] Create `doc_evergreen/examples/` directory
- [ ] Example 1: `simple-example.json` - 2 sections, basic prompts
- [ ] Example 2: `nested-example.json` - Nested sections demonstrating hierarchy
- [ ] Example 3: `doc-evergreen-self.json` - Documents doc_evergreen itself
- [ ] Create `TEMPLATES.md` documentation explaining:
  - [ ] JSON structure with annotated examples
  - [ ] All fields and their purposes
  - [ ] How sources work (per-section field)
  - [ ] How output path works
  - [ ] Mode selection guidance
- [ ] Update README with "Quick Start" section referencing examples
- [ ] Add template validation examples (what fails and why)

## Related Issues

- Related to: ISSUE-004 - Help text could reference example templates
- Related to: ISSUE-006 - Template docs should explain sources field
- Related to: ISSUE-008 - Template docs should explain when to use each mode

## Technical Notes

**Proposed Solution:**

**1. Create examples directory:**
```
doc_evergreen/
├── examples/
│   ├── README.md                    # Overview of examples
│   ├── simple-example.json          # Basic 2-section template
│   ├── nested-sections.json         # Demonstrates section hierarchy
│   └── doc-evergreen-guide.json     # Real-world self-documentation
```

**2. Simple example template:**
```json
{
  "document": {
    "title": "Simple Documentation Example",
    "output": "SIMPLE_EXAMPLE.md",
    "sections": [
      {
        "heading": "Overview",
        "prompt": "Explain what this project does and why it exists.",
        "sources": ["src/main.py", "README.md"]
      },
      {
        "heading": "Installation",
        "prompt": "Provide installation instructions.",
        "sources": ["setup.py", "requirements.txt"]
      }
    ]
  }
}
```

**3. Create TEMPLATES.md documentation**

**Implementation Complexity:** Low - Creating examples and docs

**Estimated Effort:** 3-4 hours

## Testing Notes

**Test Cases Needed:**
- [ ] Verify each example template is valid (passes validation)
- [ ] Run each example template successfully
- [ ] Confirm generated output is reasonable quality
- [ ] Test that new users can follow documentation to create their own

**Regression Risk:** None - Adding examples doesn't change existing code

## Sprint Assignment

**Assigned to:** TBD (High Priority - Onboarding)
**Rationale:** Blocks first-time users, low implementation effort, high impact on adoption

## Comments / Updates

### 2025-11-19
Issue captured from user feedback. User couldn't find any templates to use as examples or reference. This is a critical onboarding gap that makes the tool difficult to adopt.

---

## RESOLUTION

**Resolved in**: Sprint 8 Day 3 & Sprint 10 Day 1 (v0.3.0)
**Commits**:
- 36ece9a - Sprint 8 Day 3: Example templates and comprehensive documentation
- 11f3ebc - Sprint 10 Day 1: Real-world template examples
**Date**: 2025-11-20

**What was created**:

**Example Templates** (Sprint 8):
1. `examples/simple.json` - Basic 2-section template for learning
2. `examples/nested.json` - Hierarchical structure demonstration

**Production Templates** (Sprint 10):
3. `templates/amplifier_readme.json` - Multi-component library (9 sections, PRIMARY test case)
4. `templates/cli_tool_guide.json` - CLI tool documentation (10 sections)
5. `templates/self_documenting.json` - Self-documentation example (9 sections)

**Documentation** (Sprint 8):
- Created comprehensive `TEMPLATES.md` (400+ lines) explaining:
  - Template structure with complete examples
  - All field references
  - How to create templates step-by-step
  - Source specification (expanded in Sprint 9 with 280+ lines)
  - Best practices

**Additional Documentation** (Sprint 10):
- `USER_GUIDE.md` (520 lines) - References all examples
- `BEST_PRACTICES.md` (340 lines) - Template design patterns

**All acceptance criteria met** - Users now have 5 example templates, comprehensive documentation, and step-by-step guides.
