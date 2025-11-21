# ISSUE-004: CLI help text unclear about output file location

**Status**: ✅ RESOLVED
**Priority**: Medium
**Type**: Enhancement (UX)
**Component**: CLI (`doc_evergreen/cli.py`)
**Created**: 2025-11-19
**Resolved**: 2025-11-20
**Resolved in**: Sprint 8 Day 4 (v0.3.0)
**Resolution Commit**: 0f3a127

---

## Description

First-time users of the `doc-update` CLI don't understand where output files will be created. The `--output` option help text says "Override output path from template" but this assumes the user knows:
1. That templates have an `output` field
2. Where the default output location comes from
3. What "from template" means in this context

This creates confusion during first use and requires users to either read source code or experiment to understand the behavior.

---

## User Feedback

> "It's not clear from the --help option that I can specify what file I am creating (the output location). Is that all defined in the template.json?"

---

## Reproduction Steps

1. Run: `.venv/bin/python3 doc_evergreen/doc-update.py --help`
2. Read the `--output` option description
3. Observe: No clear explanation of default behavior

**Current help output:**
```
Options:
  --output PATH  Override output path from template
```

---

## Expected Behavior

The help text should clearly communicate:
1. **Default behavior**: Output location comes from template's `"output"` field
2. **Override behavior**: `--output` lets you specify a different location
3. **Context**: What "from template" means

**Proposed improved help text:**
```python
help="Output file path (default: uses 'output' field from template)"
```

Or alternatively:
```python
help="Output file path (overrides template's 'output' field if specified)"
```

---

## Actual Behavior

Current implementation (cli.py:32-34):
```python
@click.option(
    "--output",
    type=click.Path(),
    help="Override output path from template",
)
```

The word "Override" implies a default exists but doesn't explain WHERE that default comes from.

---

## Root Cause

**Location**: `doc_evergreen/cli.py:34`

The help text was written with assumption that users understand template structure. The full command docstring (lines 40-48) DOES include helpful examples:

```python
"""Generate/update documentation from JSON template.

\b
Examples:
  # Generate using single-shot mode (default)
  doc-update template.json

  # Generate using chunked mode (section-by-section)
  doc-update --mode chunked template.json

  # Override output path
  doc-update --output custom.md template.json
"""
```

However, these examples only appear when viewing the full help (`--help`), not in the brief option descriptions.

---

## Proposed Solution

**Option 1: Improve help text (minimal change)**
```python
@click.option(
    "--output",
    type=click.Path(),
    help="Output file path (default: uses 'output' field from template)",
)
```

**Option 2: More explicit**
```python
@click.option(
    "--output",
    type=click.Path(),
    help="Override output path specified in template.json 'output' field",
)
```

**Option 3: Add to option help AND improve examples**
Keep the improved help text AND enhance the docstring examples to show the template structure.

---

## Acceptance Criteria

- [ ] Updated help text clearly explains default behavior
- [ ] First-time users can understand output location without reading docs
- [ ] Help text mentions template's `output` field
- [ ] Consider adding example showing template structure in help
- [ ] Verify with `doc-update --help` that text is clear

---

## Affected Files

- `doc_evergreen/cli.py` (line 34: help text)
- Potentially: Documentation files if they need updating

---

## Testing Notes

**To verify fix:**
1. Update help text in cli.py
2. Run: `.venv/bin/python3 doc_evergreen/doc-update.py --help`
3. Confirm help text is clearer for first-time users
4. Ask someone unfamiliar with the tool to read it

---

## Sprint Assignment

TBD (to be assigned during sprint planning)

---

## Related Issues

None yet

---

## Notes

- This is a UX improvement, not a bug - the functionality works correctly
- The full command docstring is actually quite helpful, but users need to see `--help` to benefit
- Could also consider improving the README with template structure examples
- Low implementation cost (just update help string)
- High impact for first-time user experience

---

## RESOLUTION

**Resolved in**: Sprint 8 Day 4 (v0.3.0)
**Commit**: 0f3a127 - "feat(doc_evergreen): complete Sprint 8 Day 4 - integration testing and polish"
**Date**: 2025-11-20

**What was done**:
1. Created new `regen-doc` command replacing `doc-update` with comprehensive help text
2. Added Quick Start guide to main CLI help
3. Added detailed workflow explanation to regen-doc help
4. Included examples for all common use cases
5. Explained both Sprint 5 and Sprint 8 template formats

**Help text improvements**:
```python
@click.group()
def cli():
    """doc_evergreen - AI-powered documentation generation from templates.

    Generate and maintain documentation by defining templates with sections,
    prompts, and source files. The system regenerates docs as your code evolves.

    Quick Start:
      1. Create a template (see examples/ directory)
      2. Run: regen-doc your-template.json
      3. Review changes and approve

    Documentation: See TEMPLATES.md for template creation guide
    """
```

**Issue fully resolved** - CLI help is now comprehensive and clear for first-time users.
