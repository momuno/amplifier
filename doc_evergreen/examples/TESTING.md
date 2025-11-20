# Manual Testing Guide for Example Templates

This document describes how to manually test the example templates.

## Prerequisites

Ensure you have:
- Python 3.11+ installed
- Dependencies installed: `make install` or `uv sync`
- Working directory at project root

## Test Cases

### 1. Simple Template (`simple.json`)

**Purpose**: Verify basic 2-section template works correctly

**Command**:
```bash
regen-doc doc_evergreen/examples/simple.json
```

**Expected behavior**:
1. Parses template successfully
2. Generates content for "Overview" section using README.md sources
3. Generates content for "Installation" section using README.md and pyproject.toml
4. Shows unified diff comparing to SIMPLE_EXAMPLE.md (or "NEW FILE" if doesn't exist)
5. Prompts for approval: "Apply these changes?"
6. On approval (y), creates SIMPLE_EXAMPLE.md in project root
7. Shows success message: "✓ File written: SIMPLE_EXAMPLE.md"

**Manual checks**:
- [ ] Generated file has 2 sections with correct headings
- [ ] Content is relevant to the project based on sources
- [ ] Output path is correct (SIMPLE_EXAMPLE.md in project root)
- [ ] File can be regenerated (subsequent runs show diff)

### 2. Nested Template (`nested.json`)

**Purpose**: Verify hierarchical sections work correctly

**Command**:
```bash
regen-doc doc_evergreen/examples/nested.json
```

**Expected behavior**:
1. Parses template with nested sections
2. Generates parent section "Getting Started" with subsections:
   - Installation (child)
   - Configuration (child)
3. Generates parent section "Usage" with subsections:
   - Basic Usage (child)
   - Advanced Usage (child)
4. Shows diff for ADVANCED_EXAMPLE.md
5. Prompts for approval
6. Creates file on approval

**Manual checks**:
- [ ] Generated file has proper heading hierarchy (# parent, ## child)
- [ ] Parent sections include intro content plus subsections
- [ ] Subsections are properly nested and formatted
- [ ] All 4 subsections appear in correct order

### 3. Production Template (`amplifier_readme.json`)

**Purpose**: Verify complex real-world template with 9 sections

**Command**:
```bash
regen-doc doc_evergreen/templates/amplifier_readme.json
```

**Expected behavior**:
1. Parses template with 9 sections
2. Generates content for each section using multiple sources
3. Shows diff comparing to existing amplifier/README.md
4. Takes longer due to 9 sections (progress feedback would be nice - Sprint 9!)
5. Prompts for approval
6. Updates amplifier/README.md on approval

**Manual checks**:
- [ ] All 9 sections present: Introduction, Architecture, Installation, Usage Example, Module Design Principles, Testing, Data Storage, Future Enhancements, Module Documentation
- [ ] Architecture section lists all major modules found in sources
- [ ] Code examples in Usage Example section are valid Python
- [ ] Links in Module Documentation section are correct
- [ ] Content is consistent with existing README (structure preserved)

## Additional Testing

### Auto-Approve Flag

Test that `--auto-approve` skips the confirmation prompt:

```bash
regen-doc --auto-approve doc_evergreen/examples/simple.json
```

**Expected**: File is written immediately without "Apply these changes?" prompt

### Output Override

Test that `--output` overrides the template's output path:

```bash
regen-doc --output /tmp/test-output.md doc_evergreen/examples/simple.json
```

**Expected**: File is written to `/tmp/test-output.md` instead of `SIMPLE_EXAMPLE.md`

### Error Handling

Test error cases:

```bash
# Non-existent template
regen-doc does-not-exist.json
# Expected: Error message, exit code 1

# Invalid JSON
echo '{invalid json' > /tmp/bad.json
regen-doc /tmp/bad.json
# Expected: JSON parsing error, exit code 1

# Template with missing sources
# (create test template with non-existent source files)
# Expected: Warning or error about missing sources
```

## Validation Checklist

After testing all templates, verify:

- [ ] JSON syntax is valid (validated with `python3 -m json.tool`)
- [ ] Templates parse successfully
- [ ] Content generation completes without errors
- [ ] Change detection works (shows diff correctly)
- [ ] Approval workflow functions properly
- [ ] Files are written to correct locations
- [ ] Generated content quality is acceptable
- [ ] Subsequent regenerations show appropriate diffs
- [ ] Error handling is graceful

## Status

**JSON Validation**: ✅ All templates have valid JSON syntax
- simple.json: ✓
- nested.json: ✓
- amplifier_readme.json: ✓

**Full Integration Testing**: ⏳ Pending (scheduled for Day 4 of Sprint 8)

## Notes

- Simple template uses 2 real source files from the project
- Nested template demonstrates 2-level hierarchy (parent → child)
- Production template (amplifier_readme.json) is THE primary test case for v0.3.0
- All templates follow the schema defined in `doc_evergreen/core/template_schema.py`
- Templates are designed to be self-documenting examples for users
