---
description: Convergent Development workflow guide and help
---

# Convergent Development - Complete Guide

Loading convergent-dev context for comprehensive help...

@ai_context/convergent-dev/README.md
@ai_context/convergent-dev/CONVERGENCE_PROCESS.md
@ai_context/convergent-dev/SPRINT_PLANNING.md
@ai_context/convergent-dev/TDD_CYCLE.md
@ai_context/IMPLEMENTATION_PHILOSOPHY.md
@ai_context/MODULAR_DESIGN_PHILOSOPHY.md

---

## What is Convergent Development?

**Core Principle**: Move from divergent exploration to convergent execution through structured phases.

**Why it works**:
- Harnesses natural divergent thinking (exploration)
- Structured convergence to shippable scope
- Nothing is lost (deferred with conditions)
- Value-first, iterative delivery
- Test-driven implementation
- Continuous issue capture

**Philosophy Foundation**:
- Ruthless Simplicity (IMPLEMENTATION_PHILOSOPHY)
- Modular Design / Bricks & Studs (MODULAR_DESIGN_PHILOSOPHY)
- Convergent Thinking (diverge → capture → converge → defer)
- Lean/Agile Principles (iterative sprints, backlogs)

---

## Complete Workflow (4 Phases + Utility)

### Main Workflow Commands (Run in Order)

**1. `/convergent-dev:1-converge`** - From Ideas to Feature Scope

**Three scenarios supported:**
- **MVP Convergence**: Starting fresh → Define MVP scope
- **Next Feature**: Ongoing project → Find what to build next
- **Organize Backlog**: Many ideas → Structure into manageable features

Agent asks you to select scenario, then guides through:
- Explore all possibilities (DIVERGE)
- Organize ideas (CAPTURE)
- Define scope or structure (CONVERGE)
- Preserve deferred ideas (DEFER)
- **Output**: `convergence/YYYY-MM-DD-feature-name/FEATURE_SCOPE.md` + Updated backlog
- **Duration**: 30-60 minutes

**2. `/convergent-dev:2-plan-sprints`** - Feature Scope to Executable Sprints

- Read latest convergence
- Assign version number (vX.Y.Z) using SemVer
- Break into value-first sprints
- Define TDD implementation order
- **Output**: `sprints/vX.Y.Z-feature-name/SPRINT_PLAN.md`
- **Duration**: 20-30 minutes

**3. `/convergent-dev:3-tdd-cycle`** - Implement Sprint with TDD

- Write tests first (RED)
- Implement minimal code (GREEN)
- Refactor for quality (REFACTOR)
- Commit on green
- **Output**: Tested, working code
- **Duration**: Per sprint plan (2-5 days typically)

**4. `/convergent-dev:4-capture-issues`** - Capture Issues from Feedback

- Accept free-form feedback
- Systematically investigate issues
- Create persistent tracking
- **Output**: `issues/ISSUES_TRACKER.md`, `ISSUE-NNN-*.md`
- **Duration**: 15-30 minutes per session

### Utility Commands

**`/convergent-dev:0-help`** - Load all context

- Loads complete methodology documentation
- Use at session start for full context

**`/convergent-dev:status`** - Check current progress

- Shows current phase and artifacts
- Recommends next command
- Works across all projects

---

## Directory Structure (Per Project)

All workflow artifacts in `ai_working/[project-name]/`:

```
ai_working/[project-name]/
├── convergence/
│   ├── YYYY-MM-DD-feature-name/
│   │   ├── FEATURE_SCOPE.md         (What to build)
│   │   ├── DEFERRED_FEATURES.md     (What to defer)
│   │   └── CONVERGENCE_COMPLETE.md  (Summary)
│   └── MASTER_BACKLOG.md            (All deferred features)
├── sprints/
│   └── vX.Y.Z-feature-name/
│       ├── SPRINT_PLAN.md           (Overview with version)
│       └── SPRINT_N.md              (Detailed sprint plans)
└── issues/
    ├── ISSUES_TRACKER.md            (Master list)
    └── ISSUE-NNN-*.md               (Individual issues)
```

**Each command reads previous artifacts**, so you can continue from where you left off.

---

## Example Usage

### Starting a New Feature

```bash
# Load context (recommended)
/convergent-dev:0-help

# Phase 1: Converge to feature scope
/convergent-dev:1-converge

# Agent guides through: DIVERGE → CAPTURE → CONVERGE → DEFER
# Output: convergence/2025-11-18-feature-name/FEATURE_SCOPE.md

# Phase 2: Plan sprints with version
/convergent-dev:2-plan-sprints

# Agent assigns version, creates sprint plan
# Output: sprints/v0.2.0-feature-name/SPRINT_PLAN.md

# Phase 3: Implement Sprint 1
/convergent-dev:3-tdd-cycle 1

# TDD cycle: RED → GREEN → REFACTOR → Commit
# Output: Working, tested code

# Capture issues if problems arise
/convergent-dev:4-capture-issues [project-name]

# Output: issues/ISSUE-001-*.md
```

### Checking Progress Mid-Stream

```bash
# See where you are in the workflow
/convergent-dev:status

# It will tell you:
# - Current convergences and sprints
# - Open issues
# - Next recommended command
```

### Resuming After Break

```bash
# Check status
/convergent-dev:status

# Continue where you left off
/convergent-dev:3-tdd-cycle 2
```

---

## Key Concepts

### Feature Scope vs MVP

**DON'T SAY**: "MVP" for every convergence
**DO SAY**: "Feature Scope" - what to build in this release

**Why**:
- MVP = Minimum Viable Product (first version only)
- After MVP: versioned releases (v0.1.0, v0.2.0, v1.0.0)
- Convergence defines feature scope, not a new MVP

### Version Numbering (SemVer)

**Sprint-planner assigns versions** based on scope:
- **Major (v2.0.0)**: Breaking changes
- **Minor (v0.2.0)**: New features, backward compatible
- **Patch (v0.2.1)**: Bug fixes only

### Agent Responsibilities

**convergence-architect**:
- Defines WHAT to build
- Creates FEATURE_SCOPE.md
- Does NOT assign version numbers

**sprint-planner**:
- Determines version number (vX.Y.Z)
- Creates executable sprint plan
- Breaks scope into sprints

**tdd-specialist**:
- Writes tests first
- Ensures honest gatekeepers
- Guides RED-GREEN-REFACTOR

**issue-capturer**:
- Captures bugs and problems
- Creates issue tracking
- Investigates root causes

---

## Common Workflows

### Feature Development

1-converge → 2-plan-sprints → 3-tdd-cycle (each sprint) → repeat

### Bug Fixes from Issues

4-capture-issues → 1-converge (if scope change) → 2-plan-sprints → 3-tdd-cycle

### Pure Issue Tracking

4-capture-issues (multiple sessions) → prioritize in next convergence

---

## Troubleshooting

### "Where am I in the workflow?"

```bash
/convergent-dev:status
```

### "I want to start a new feature"

```bash
/convergent-dev:1-converge
```

### "I have bugs/issues to track"

```bash
/convergent-dev:4-capture-issues [project-name]
```

### "I need to plan sprints for existing convergence"

```bash
/convergent-dev:2-plan-sprints
```

---

## Philosophy Alignment

Every phase embodies:

**Ruthless Simplicity**:
- Start minimal, grow as needed
- Question every feature
- 3-5 features max per scope
- Defer thoughtfully

**Convergent Thinking**:
- Diverge freely (exploration)
- Capture systematically (organization)
- Converge ruthlessly (decision)
- Defer thoughtfully (preservation)

**Iterative Delivery**:
- Value-first sequencing
- Vertical slices
- Ship and learn
- Continuous improvement

**Test-Driven Development**:
- Tests first, always
- Honest gatekeepers
- Minimal implementation
- Refactor with protection

---

## Quick Reference Card

| Command                              | Purpose               | Output                 | Next Step                        |
| ------------------------------------ | --------------------- | ---------------------- | -------------------------------- |
| `/convergent-dev:0-help`             | Load context          | -                      | Start workflow                   |
| `/convergent-dev:status`             | Check progress        | -                      | Shows next command               |
| `/convergent-dev:1-converge`         | Ideation → Scope      | FEATURE_SCOPE.md       | `/convergent-dev:2-plan-sprints` |
| `/convergent-dev:2-plan-sprints`     | Scope → Sprints       | SPRINT_PLAN.md         | `/convergent-dev:3-tdd-cycle 1`  |
| `/convergent-dev:3-tdd-cycle [N]`    | Implement sprint      | Tested code            | Next sprint or done              |
| `/convergent-dev:4-capture-issues`   | Track issues          | ISSUES_TRACKER.md      | Include in next convergence      |

---

## Need More Help?

**Loaded Documentation**:
- Overview and philosophy now in context
- Convergence, sprint planning, and TDD guides loaded
- Implementation and modular design principles available

**Ask Specific Questions**:
- "How do I converge to feature scope?"
- "What if I have issues to track?"
- "How does version numbering work?"

**Check Phase-Specific Help**:
Each command has detailed instructions for its phase.

---

Ready to start? Run `/convergent-dev:1-converge` to begin!
