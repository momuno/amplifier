# doc_evergreen - AI Working Directory

This directory contains all planning, convergence, sprint, and issue tracking for the doc_evergreen project.

## Directory Structure

```
ai_working/doc_evergreen/
├── convergence/              # Feature scope definitions from convergence sessions
│   ├── YYYY-MM-DD-feature-name/
│   │   ├── FEATURE_SCOPE.md
│   │   ├── DEFERRED_FEATURES.md
│   │   └── CONVERGENCE_COMPLETE.md
│   └── MASTER_BACKLOG.md    # Consolidated backlog from all convergences
├── sprints/                  # Sprint plans and execution tracking
│   └── vX.Y.Z-feature-name/
│       ├── SPRINT_PLAN.md
│       └── SPRINT_N.md
├── issues/                   # Issue tracking
│   ├── ISSUES_TRACKER.md
│   └── ISSUE-NNN-*.md
└── README.md                 # This file
```

---

## Workflow Overview

### 1. Convergence (Define Feature Scope)

**Tool**: `/converge` or convergence-architect agent

**Input**:
- User ideas and goals
- Current code state
- Issue tracker
- Previous convergence sessions

**Process**: DIVERGE → CAPTURE → CONVERGE → DEFER

**Output** (in `convergence/YYYY-MM-DD-feature-name/`):
- `FEATURE_SCOPE.md` - What to build (NOT "MVP_DEFINITION")
- `DEFERRED_FEATURES.md` - What to defer
- `CONVERGENCE_COMPLETE.md` - Summary
- Updates `MASTER_BACKLOG.md`

**Example**:
```bash
$ /converge "I want to explore chunked generation"
# ... convergence session ...
# Creates: convergence/2025-11-18-chunked-generation/
```

---

### 2. Sprint Planning (Determine Version & Plan)

**Tool**: `/plan-sprints` or sprint-planner agent

**Input**:
- `convergence/[latest]/FEATURE_SCOPE.md` (what to build)
- `issues/ISSUES_TRACKER.md` (issues to address)
- Current code state (git, existing versions)
- Previous sprint history

**Process**:
- Analyze scope (breaking change? new feature? bugfix?)
- Assign version number using SemVer
- Break into executable sprints
- Estimate effort

**Output** (in `sprints/vX.Y.Z-feature-name/`):
- `SPRINT_PLAN.md` with version number
- Individual `SPRINT_N.md` files
- Links back to convergence session

**Example**:
```bash
$ /plan-sprints
# Reads: convergence/2025-11-18-chunked-generation/FEATURE_SCOPE.md
# Creates: sprints/v0.2.0-chunked-generation/
#   - SPRINT_PLAN.md (version v0.2.0)
#   - SPRINT_5.md, SPRINT_6.md, SPRINT_7.md
```

---

### 3. Execution (Implement Sprints)

**Tool**: `/tdd-cycle` or tdd-specialist agent

**Input**:
- `sprints/vX.Y.Z-feature-name/SPRINT_N.md`

**Process**:
- Write tests first (red)
- Implement features (green)
- Refactor (refactor)

**Output**:
- Code changes
- Tests
- Documentation

---

### 4. Issue Tracking (Capture Problems)

**Tool**: `/capture-issues` or issue-capturer agent

**Input**:
- User feedback about bugs/issues
- Current code behavior

**Process**:
- Investigate and reproduce
- Create issue tracking files

**Output** (in `issues/`):
- `ISSUES_TRACKER.md` - Master list
- `ISSUE-NNN-description.md` - Individual issues

---

## Key Concepts

### Feature Scope vs MVP

**DON'T SAY**: "MVP_DEFINITION" for every convergence
**DO SAY**: "FEATURE_SCOPE" - defines what to build in next release

**Why**:
- MVP = Minimum Viable Product (the FIRST version only)
- After MVP, you have **releases** or **versions** (v0.1.0, v0.2.0, v1.0.0)
- Convergence defines **feature scope** for next release, not a new "MVP"

### Version Numbering (SemVer)

**Sprint-planner assigns versions** based on scope:

```
v0.1.0 = Initial release (Problem A - Template System)
v0.2.0 = New features (Problem B - Chunked Generation)
v0.3.0 = More features (Phase 2 - Post-order validation)
v1.0.0 = First stable release (user decides when ready)
v2.0.0 = Breaking changes
```

**Rules**:
- **Major** (v2.0.0): Breaking changes to existing functionality
- **Minor** (v0.2.0): New features, backward compatible
- **Patch** (v0.2.1): Bug fixes only

### Agent Responsibilities

**Convergence-Architect**:
- Defines WHAT to build
- Creates FEATURE_SCOPE.md
- Does NOT assign version numbers
- Does NOT create sprint plans

**Sprint-Planner**:
- Determines version number (vX.Y.Z)
- Creates executable sprint plan
- Breaks scope into sprints
- Estimates effort

**TDD-Specialist**:
- Implements sprints
- Writes tests first
- Delivers working code

**Issue-Capturer**:
- Captures bugs and problems
- Creates issue tracking
- Investigates root causes

---

## File Naming Conventions

### Convergence Directories
```
YYYY-MM-DD-descriptive-name/
```

Examples:
- `2025-11-18-chunked-generation/`
- `2025-12-01-dynamic-expansion/`

### Convergence Files (consistent names)
- `FEATURE_SCOPE.md` (what to build)
- `DEFERRED_FEATURES.md` (what to defer)
- `CONVERGENCE_COMPLETE.md` (summary)

### Sprint Directories
```
vX.Y.Z-feature-name/
```

Examples:
- `v0.1.0-template-system/`
- `v0.2.0-chunked-generation/`

### Sprint Files
- `SPRINT_PLAN.md` (overall plan with version)
- `SPRINT_N.md` (individual sprint details)

---

## Master Backlog

**Location**: `convergence/MASTER_BACKLOG.md`

**Purpose**: Single source of truth for ALL deferred features from ALL convergence sessions

**Organized by**:
- Origin (which convergence generated this idea)
- Phase (when to reconsider)
- Status (New, Under Consideration, Implemented)
- Complexity (Low/Medium/High)

**Use cases**:
- Review after each release to see what triggers have been met
- Add new ideas without losing them
- Prioritize next convergence based on data

---

## Current State

### Implemented
- **v0.1.0** (Problem A - Template System): Sprints 1-4
  - Template-based structure
  - Source resolution
  - Single-shot generation
  - Preview & accept workflow

- **v0.2.0** (Problem B - Chunked Generation): Sprints 5-7 (IN PROGRESS)
  - Section-level prompts
  - Sequential DFS generation
  - Context flow between sections
  - Section review checkpoints
  - Source validation (fixes ISSUE-001, ISSUE-003)

### Active Issues
- See `issues/ISSUES_TRACKER.md`

### Deferred Features
- 36 features in backlog
- See `convergence/MASTER_BACKLOG.md`

---

## Philosophy

This structure embodies:

**Ruthless Simplicity**:
- Clear separation of concerns (convergence → planning → execution)
- Minimal files, maximum clarity
- No duplication of information

**Trust in Emergence**:
- Features prove themselves through use
- Data-driven prioritization
- Deferred doesn't mean deleted

**Present-Moment Focus**:
- Solve current problems
- Let needs drive development
- MVP/release scope stays focused (3-5 features)

**Learning Stance**:
- Every release teaches what matters next
- Backlog evolves with understanding
- Nothing is lost, everything is preserved

---

## Quick Reference

### Find Feature Scope for Current Work
```bash
ls -t convergence/*/FEATURE_SCOPE.md | head -1
```

### Find Current Sprint Plan
```bash
ls -t sprints/*/SPRINT_PLAN.md | head -1
```

### Check Active Issues
```bash
cat issues/ISSUES_TRACKER.md
```

### Review Backlog
```bash
cat convergence/MASTER_BACKLOG.md
```

---

## Related Documentation

- **Project Root**: `../../doc_evergreen/` (actual code)
- **Decisions**: `../decisions/` (if exists - architectural decisions)
- **Main Project Docs**: See project root README

---

**Last Updated**: 2025-11-18
**Current Version**: v0.2.0 (in development)
**Next Review**: After Sprint 7 complete
