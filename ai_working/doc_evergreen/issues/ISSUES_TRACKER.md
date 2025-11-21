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

### ISSUE-010: Makefile `regen-doc` Missing OUTPUT Parameter
- **Status**: Open
- **Priority**: Medium
- **Type**: Bug (Missing Feature)
- **Component**: Makefile
- **Assigned to**: Next polish/UX sprint
- **Created**: 2025-11-20
- **Sprint**: TBD (UX Polish)

Makefile `regen-doc` target doesn't expose the `--output` CLI option that the underlying command supports. Usage message also doesn't mention OUTPUT parameter, creating discoverability issues and incomplete feature parity between Makefile wrapper and CLI.

[Full details →](./ISSUE-010-makefile-missing-output-param.md)

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

### ISSUE-004: CLI help text unclear about output file location
- **Status**: ✅ Resolved
- **Priority**: Medium
- **Type**: Enhancement (UX)
- **Component**: CLI
- **Resolved in**: Sprint 8 Day 4 (v0.3.0)
- **Created**: 2025-11-19
- **Resolved**: 2025-11-20

**Resolution**: Created new `regen-doc` command with comprehensive help text including Quick Start guide, detailed workflow explanation, and examples. Help text now clearly explains template structure and output path behavior.

[Full details →](./ISSUE-004-cli-help-text-unclear.md)

---

### ISSUE-005: No example templates or documentation about template creation
- **Status**: ✅ Resolved
- **Priority**: High
- **Type**: Enhancement (Documentation)
- **Component**: Documentation, Examples
- **Resolved in**: Sprint 8 Day 3 & Sprint 10 Day 1 (v0.3.0)
- **Created**: 2025-11-19
- **Resolved**: 2025-11-20

**Resolution**: Created 5 example templates (2 learning examples + 3 production templates) and comprehensive documentation (TEMPLATES.md, USER_GUIDE.md, BEST_PRACTICES.md totaling 1,260+ lines). All acceptance criteria met.

[Full details →](./ISSUE-005-no-example-templates.md)

---

### ISSUE-006: Unclear whether sources belong in template vs CLI argument
- **Status**: ✅ Resolved
- **Priority**: High
- **Type**: Bug / Documentation
- **Component**: Template System, Documentation
- **Resolved in**: Sprint 9 Day 2 (v0.3.0)
- **Created**: 2025-11-19
- **Resolved**: 2025-11-20

**Resolution**: Expanded TEMPLATES.md with 280+ lines of source specification documentation covering glob patterns, resolution behavior, common patterns, and troubleshooting. Enhanced error messages to show actionable fixes. Clarified that sources are per-section in templates (no global CLI flag in v0.3.0).

[Full details →](./ISSUE-006-sources-template-vs-cli.md)

---

### ISSUE-007: No progress or activity feedback during generation
- **Status**: ✅ Resolved
- **Priority**: High
- **Type**: Enhancement (UX)
- **Component**: CLI, ChunkedGenerator
- **Resolved in**: Sprint 9 Day 1 (v0.3.0)
- **Created**: 2025-11-19
- **Resolved**: 2025-11-20

**Resolution**: Implemented complete progress feedback system with progress callbacks, timing tracking, section progress display ([1/N]), source file display, and completion markers. Integrated into CLI with real-time output. 9 tests validate functionality.

[Full details →](./ISSUE-007-no-progress-feedback.md)

---

### ISSUE-011: Add project_root Support for Standalone Tool Usage
- **Status**: ✅ Resolved (Superseded)
- **Priority**: N/A
- **Type**: Feature
- **Component**: Architecture
- **Resolved in**: Sprints 11-12 (v0.4.0)
- **Created**: 2025-11-20
- **Resolved**: 2025-11-20

**Resolution**: Superseded by convention-based cwd approach (Sprints 11-12). Instead of adding `project_root` field, implemented simpler solution: run from project root (cwd = project), templates in `.doc-evergreen/`, zero configuration. Dramatically simpler than original proposal. See MIGRATION_v0.3_to_v0.4.md.

[Full details →](./ISSUE-011-project-root-support.md)

---

**Last Updated**: 2025-11-21
**Total Issues**: 11 (3 open [1 deferred], 0 in progress, 8 resolved)
