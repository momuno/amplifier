# ISSUE-006: Unclear Whether Sources Belong in Template vs CLI Argument

**Status:** Open
**Priority:** High
**Type:** Bug / Documentation
**Created:** 2025-11-19
**Updated:** 2025-11-19

---

## Description

Users are confused about how to specify source files for documentation generation. The template schema has a `sources` field per section, and the CLI has a `--sources` flag, but it's unclear:
- Which method to use
- If both can be used together
- Which takes precedence
- What happens when sources are missing

## User Feedback

> "is the template supposed to already specify source files or do i pass it at command line"

**Triggering error:**
```
python3 doc_evergreen/doc-update.py --output custom.md example_template.json
Generation failed: Section 'Introduction' has no sources (no files found)
Aborted!
```

## Reproduction Steps

1. Create a template without `sources` fields in sections:
   ```json
   {
     "document": {
       "sections": [
         {"heading": "Overview", "prompt": "Explain..."}
       ]
     }
   }
   ```
2. Run: `doc-update template.json` (without `--sources` flag)
3. Observe error: "Section 'Overview' has no sources"
4. Question: Should I add sources to template or use `--sources` flag?

**Frequency:** Always (when sources not specified correctly)

## Expected Behavior

**Clear documentation explaining:**

1. **Template sources (per-section):**
   - Specify different sources for each section
   - Most flexible approach
   - Example: Overview uses README, API docs use source code

2. **CLI sources (global):**
   - Apply same sources to all sections
   - Quick for simple cases
   - Example: `--sources "src/*.py,docs/*.md"`

3. **Precedence:**
   - Template sources are section-specific
   - CLI sources supplement or override (document which)
   - Or: CLI sources only used if section has no sources

4. **Clear error messages:**
   - "Section 'Overview' has no sources. Add 'sources' field to template or use --sources flag"
   - Link to documentation about source specification

## Actual Behavior

- Error message: "Section 'Introduction' has no sources (no files found)"
- Doesn't explain how to fix
- Doesn't clarify template vs CLI sources
- No documentation about source precedence
- Users must experiment or read code

## Root Cause

**Location:**
- Template schema: `doc_evergreen/core/template_schema.py` (Section dataclass)
- CLI: `doc_evergreen/cli.py` (--sources option)
- Source resolution: `doc_evergreen/source_resolver.py`

**Technical Explanation:**

The codebase supports both approaches:

1. **Template sources:**
   ```python
   @dataclass
   class Section:
       heading: str
       sources: list[str] = field(default_factory=list)  # Per-section
   ```

2. **CLI sources:**
   ```python
   @click.option("--sources", help="Source files/patterns (comma-separated)")
   ```

However:
- No documentation explains which to use when
- No clear precedence rules
- Error messages don't guide users
- Template validation doesn't check for missing sources upfront

## Impact Analysis

**Severity:** High - Confuses users about fundamental tool usage

**User Impact:**
- Trial and error to figure out source specification
- Unclear which approach is "correct"
- Wasted time debugging error messages
- Reduced confidence in tool

**Workaround:**
1. Add `sources` field to every section in template
2. Or use `--sources` flag at CLI (if that works globally)
3. Experiment to find what works

## Acceptance Criteria

To consider this issue resolved:

- [ ] **Documentation created** explaining:
  - [ ] When to use template sources (per-section customization)
  - [ ] When to use CLI sources (apply to all sections)
  - [ ] Precedence rules if both specified
  - [ ] Examples of both approaches
- [ ] **Error message improved:**
  - [ ] "Section 'X' has no sources. Add 'sources': [...] to section in template, or use --sources flag"
  - [ ] Link to documentation
- [ ] **Help text updated:**
  - [ ] `--sources` help explains it applies to all sections
  - [ ] Mentions template sources as alternative
- [ ] **Template validation** enhanced:
  - [ ] Warn if sections missing sources and no CLI sources provided
  - [ ] Clear validation messages before generation starts

## Related Issues

- Related to: ISSUE-001 - Empty sources should fail early with clear message
- Related to: ISSUE-005 - Example templates should show both approaches
- Related to: ISSUE-003 - Better source feedback would help

## Technical Notes

**Proposed Solution:**

**1. Update error message in source validation:**
```python
# In source_validator.py or chunked_generator.py
if not section.sources:
    raise ValueError(
        f"Section '{section.heading}' has no sources.\n"
        f"Fix: Add 'sources': [\"path/to/file.py\"] to section in template,\n"
        f"     or use --sources flag: doc-update --sources 'src/*.py' template.json\n"
        f"See: TEMPLATES.md for examples"
    )
```

**2. Create TEMPLATES.md documenting both approaches:**

```markdown
## Source Specification

### Option 1: Per-Section Sources (Template)
Best when sections need different sources:

```json
{
  "sections": [
    {
      "heading": "API Reference",
      "sources": ["src/api/*.py"]
    },
    {
      "heading": "Installation",
      "sources": ["setup.py", "requirements.txt"]
    }
  ]
}
```

### Option 2: Global Sources (CLI)
Best when all sections use same sources:

```bash
doc-update --sources "src/*.py,docs/*.md" template.json
```

### Precedence
- Template sources are always used if specified
- CLI sources apply to sections WITHOUT sources
- CLI sources DON'T override template sources
```

**3. Update CLI help text:**
```python
@click.option(
    "--sources",
    help="Source files/patterns (comma-separated). Applies to sections without sources in template."
)
```

**Implementation Complexity:** Medium - Requires error message updates, documentation, and validation changes

**Estimated Effort:** 4-5 hours (including documentation and testing)

## Testing Notes

**Test Cases Needed:**
- [ ] Template with sources, no CLI sources → uses template sources
- [ ] Template without sources, CLI sources → uses CLI sources
- [ ] Template with some sources, CLI sources → template takes precedence, CLI fills gaps
- [ ] Template without sources, no CLI sources → clear error before generation
- [ ] Verify error message is helpful and actionable

**Regression Risk:** Low - Improving messages and docs, core logic unchanged

## Sprint Assignment

**Assigned to:** TBD (High Priority - Usability)
**Rationale:** Fundamental confusion about tool usage, moderate effort, high impact

## Comments / Updates

### 2025-11-19
Issue captured from user feedback. User encountered error and didn't know whether to fix in template or via CLI flag. This is a critical usability issue affecting tool comprehension.

---

## RESOLUTION

**Resolved in**: Sprint 9 Day 2 (v0.3.0)
**Commit**: 665fad5 - "feat(doc_evergreen): Sprint 9 Day 2 - source documentation and enhanced error messages"
**Date**: 2025-11-20

**What was done**:

**Comprehensive Source Documentation** (TEMPLATES.md expanded by 280+ lines):
1. **Understanding Sources** section - Explains per-section source specification clearly
2. **Glob Pattern Support** - Complete reference table with examples
3. **Source Resolution** - Explains relative path resolution with examples
4. **Common Source Patterns** - 4 real-world patterns (README, API, Module, Installation)
5. **Choosing Good Sources** - DO/DON'T lists with rationale
6. **Source File Limits** - Performance guidelines
7. **Troubleshooting Sources** - 3 common issues with specific solutions

**Enhanced Error Messages**:
1. source_validator.py - "No sources found" error now shows:
   - Which patterns failed to match
   - 3 possible causes
   - Actionable fixes with examples
   - Link to documentation: `TEMPLATES.md#source-resolution`

**Documentation clarifies**:
- Sources are per-section (template), not global
- No CLI --sources flag in regen-doc (removed in v0.3.0)
- Resolution is relative to template location
- Examples for every common use case

**Issue fully resolved** - Source specification is now thoroughly documented with examples and clear error messages.
