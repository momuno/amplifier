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
