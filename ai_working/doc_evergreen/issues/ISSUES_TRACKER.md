# Issues Tracker - doc_evergreen

## Open Issues

### ISSUE-002: Misleading Success Message When Generated Content Contains Errors
- **Status**: Open (Deferred)
- **Priority**: Medium
- **Type**: Enhancement
- **Component**: CLI (`doc_evergreen/cli.py`)
- **Assigned to**: Deferred (v0.2.0)
- **Created**: 2025-11-18
- **Deferred**: Handled by section review workflow in v0.2.0

Displays "✅ Accepted: README.md updated" even when generated content contains LLM error messages instead of actual documentation, creating false confidence. Deferred because section-by-section review in chunked mode provides alternative solution.

[Full details →](./ISSUE-002-misleading-success-message.md)

---

### ISSUE-004: CLI help text unclear about output file location
- **Status**: Open
- **Priority**: Medium
- **Type**: Enhancement (UX)
- **Component**: CLI (`doc_evergreen/cli.py`)
- **Assigned to**: TBD
- **Created**: 2025-11-19
- **Sprint**: TBD

First-time users don't understand where output files will be created when running `doc-update`. The `--output` help text says "Override output path from template" but doesn't explain that templates contain an `output` field or where the default location is.

[Full details →](./ISSUE-004-cli-help-text-unclear.md)

---

### ISSUE-005: No example templates or documentation about template creation
- **Status**: Open
- **Priority**: High
- **Type**: Enhancement (Documentation)
- **Component**: Documentation, Examples
- **Assigned to**: TBD
- **Created**: 2025-11-19
- **Sprint**: TBD (High Priority - Onboarding)

Users attempting to use doc_evergreen don't know where to find example templates or how to create their own. No example templates exist in the repository and no documentation explains template structure or creation process.

[Full details →](./ISSUE-005-no-example-templates.md)

---

### ISSUE-006: Unclear whether sources belong in template vs CLI argument
- **Status**: Open
- **Priority**: High
- **Type**: Bug / Documentation
- **Component**: CLI, Template System, Documentation
- **Assigned to**: TBD
- **Created**: 2025-11-19
- **Sprint**: TBD (High Priority - Usability)

Users are confused about how to specify source files - template has `sources` field per section, CLI has `--sources` flag. Not documented which to use, precedence rules, or what happens when sources are missing.

[Full details →](./ISSUE-006-sources-template-vs-cli.md)

---

### ISSUE-007: No progress or activity feedback during generation
- **Status**: Open
- **Priority**: High
- **Type**: Enhancement (UX)
- **Component**: CLI (`doc_evergreen/cli.py`)
- **Assigned to**: TBD
- **Created**: 2025-11-19
- **Sprint**: TBD (High Priority - UX)

CLI provides no output during generation. Users see blank terminal and don't know if tool is working, hung, or crashed. Especially problematic for long-running multi-section generations.

[Full details →](./ISSUE-007-no-progress-feedback.md)

---

### ISSUE-008: Unclear what "chunked" vs "single-shot" modes do
- **Status**: Open
- **Priority**: Medium
- **Type**: Enhancement (Documentation)
- **Component**: CLI, Documentation
- **Assigned to**: TBD
- **Created**: 2025-11-19
- **Sprint**: TBD (Documentation - After ISSUE-009)

CLI offers two modes but doesn't explain what each does, when to use them, or how they differ. Users must guess or experiment to understand functionality.

[Full details →](./ISSUE-008-modes-unclear.md)

---

### ISSUE-009: Single-shot mode not implemented - both modes use chunked generator
- **Status**: Open
- **Priority**: High
- **Type**: Bug (Missing Feature)
- **Component**: Generation (`single_generator.py` missing)
- **Assigned to**: TBD
- **Created**: 2025-11-19
- **Sprint**: TBD (Feature Implementation)

CLI advertises two generation modes but single-shot mode isn't implemented. Both modes fall back to `ChunkedGenerator`, making `--mode` option misleading and non-functional.

[Full details →](./ISSUE-009-single-shot-not-implemented.md)

---

## In Progress

(No issues currently in progress)

---

## Resolved

### ISSUE-001: Tool Proceeds with Empty Context Instead of Failing Early
- **Status**: Resolved
- **Priority**: High
- **Type**: Bug
- **Component**: CLI / Source Validation
- **Resolved in**: Sprint 5 (v0.2.0)
- **Created**: 2025-11-18
- **Resolved**: 2025-11-19

**Resolution**: Implemented comprehensive source validation system in Sprint 5. The new `validate_all_sources()` function validates all sources upfront before generation starts, checks for empty source lists per section, and displays validation reports. Tool now fails early with clear error messages when source patterns don't match any files, preventing LLM calls with empty context.

[Full details →](./ISSUE-001-empty-context-handling.md)

---

### ISSUE-003: No User Feedback When Source Globs Match Zero Files
- **Status**: Resolved
- **Priority**: Medium
- **Type**: Enhancement
- **Component**: CLI / Source Validation
- **Resolved in**: Sprint 5/6 (v0.2.0)
- **Created**: 2025-11-18
- **Resolved**: 2025-11-19

**Resolution**: Addressed through Sprint 5 validation reporting (shows resolved file paths per section before generation) and Sprint 6 interactive visibility (section-by-section progress with source display). Users now have clear visibility into which sources are being used through upfront validation reports, per-section logging, and optional interactive checkpoints.

[Full details →](./ISSUE-003-no-source-validation-feedback.md)

---

**Last Updated**: 2025-11-19
**Total Issues**: 9 (7 open [1 deferred], 0 in progress, 2 resolved)
