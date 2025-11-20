# Deferred Features: Test Case - Basic Regeneration

**Date**: 2025-11-19
**Convergence Session**: Test Case - Basic Regeneration
**Feature Scope**: See `FEATURE_SCOPE.md`

---

## Overview

This document captures all features discussed during the convergence session but NOT included in the feature scope. These ideas are valuable and thoughtfully deferred, not rejected. Each includes clear "Reconsider when" conditions for when they should be reconsidered.

**Total Deferred**: 21 features across 4 categories

---

## Phase 2: Automation & Triggers (After Manual Flow Works)

**Reconsider When**: Basic regeneration flow (manual trigger) proves valuable and is used for 10+ regenerations

### 1. Automatic Change Detection

**What**: Detect when source files have changed and determine if documentation needs updating.

**Why Valuable**: Eliminates "should I regenerate?" decision overhead. Proactive maintenance.

**Why Deferred**: Must prove basic regeneration works first. Manual trigger validates core value before adding automation complexity.

**Complexity**: Medium (file watching, git integration, heuristics)

**Reconsider When**:
- Manual regeneration used 10+ times successfully
- Users repeatedly ask "how do I know when to regenerate?"
- Checking "should I regenerate?" becomes tedious

---

### 2. Git Hook Integration

**What**: Automatically trigger regeneration on git events (pre-commit, post-merge, etc.)

**Why Valuable**: Docs stay in sync with code changes without manual intervention.

**Why Deferred**: Need to understand workflow integration points through manual use first. Git hooks add complexity and can slow commits.

**Complexity**: Medium (git hooks, performance, user control)

**Reconsider When**:
- Manual regeneration becomes routine part of git workflow
- Users report "I forgot to regenerate before committing" 3+ times
- Git integration patterns emerge from actual usage

---

### 3. Watch Mode

**What**: Continuously monitor source files, regenerate on changes.

**Why Valuable**: Real-time doc updates during development.

**Why Deferred**: Unclear if this workflow fits actual usage patterns. May be too aggressive (regenerate on every save?). Manual trigger proves baseline value first.

**Complexity**: Medium (file watching, debouncing, resource usage)

**Reconsider When**:
- Users manually regenerate multiple times during single dev session
- "I want docs to update as I code" explicitly requested
- Clear use cases for continuous regeneration emerge

---

### 4. Scheduled Regeneration

**What**: Cron-like scheduled regeneration (daily, weekly, on release, etc.)

**Why Valuable**: Ensures docs stay fresh even if manual trigger forgotten.

**Why Deferred**: Scheduling adds complexity without proving value. Manual trigger validates core flow first.

**Complexity**: Low (cron integration, scheduling config)

**Reconsider When**:
- Docs fall stale between releases despite manual trigger availability
- Users request "regenerate all docs weekly" explicitly
- CI/CD integration emerges as clear use case

---

## Phase 3: Multi-Document Operations (After Single-Doc Works)

**Reconsider When**: Single-document regeneration proves solid, users maintain 5+ docs

### 5. Batch Regeneration

**What**: Regenerate multiple documents in one command: `amplifier regen-doc amplifier/*.md`

**Why Valuable**: Efficient when multiple docs reference same sources.

**Why Deferred**: Must prove single-doc regeneration first. Batch operations add complexity (error handling, partial failures, progress tracking).

**Complexity**: Medium (batch processing, error handling, progress UI)

**Reconsider When**:
- Users manage 5+ template-based docs
- Manually regenerating docs one-by-one becomes tedious
- Clear patterns emerge for "regenerate all project docs"

---

### 6. Multi-Document Orchestration

**What**: Coordinate regeneration across related documents (e.g., README references API docs).

**Why Valuable**: Maintains consistency across documentation suite.

**Why Deferred**: Complex coordination logic. Need to understand cross-doc dependencies through actual usage first.

**Complexity**: High (dependency tracking, ordering, consistency validation)

**Reconsider When**:
- Users maintain documentation suites with clear cross-references
- Inconsistencies across docs become pain point
- Dependency patterns are well understood

---

### 7. Workspace-Wide Regeneration

**What**: One command to regenerate all docs in entire workspace: `amplifier regen-all`

**Why Valuable**: Ultimate convenience for "update everything."

**Why Deferred**: Requires understanding of what "all docs" means, how to discover templates, error handling for diverse docs.

**Complexity**: Medium (discovery, batch processing, configuration)

**Reconsider When**:
- Users manage 10+ docs across multiple projects
- "Regenerate everything" is frequent operation
- Clear conventions for template discovery emerge

---

## Phase 4: Advanced Features (Long-Term)

**Reconsider When**: Core functionality mature, advanced needs emerge

### 8. Partial/Selective Updates

**What**: Update only specific sections: `amplifier regen-doc README.md --section Features`

**Why Valuable**: Faster regeneration, less review overhead.

**Why Deferred**: Adds complexity to template parsing and LLM context. Full-doc regeneration validates baseline first.

**Complexity**: Medium (section targeting, context management)

**Reconsider When**:
- Full-doc regeneration takes >1 minute regularly
- Users frequently discard most changes (only 1-2 sections meaningful)
- Section-level granularity clearly valuable

---

### 9. Human Edit Preservation

**What**: Detect human edits in generated docs, preserve across regenerations.

**Why Valuable**: Allows manual fixes without losing on next regeneration.

**Why Deferred**: Complex detection logic (what's human vs. LLM?). May encourage bad pattern (manual edits instead of template fixes). Need to understand edit patterns first.

**Complexity**: High (diff analysis, merge logic, conflict resolution)

**Reconsider When**:
- Users frequently lose manual edits after regeneration
- Clear patterns emerge for "preserve this section"
- Template-based fixes prove insufficient for edge cases

---

### 10. Configuration Files

**What**: Project-wide config for regeneration defaults, LLM settings, source paths.

**Why Valuable**: Reduces command-line verbosity, shares settings across team.

**Why Deferred**: Premature without understanding what needs configuring. Manual flags validate what config is actually needed.

**Complexity**: Low (config file parsing, precedence rules)

**Reconsider When**:
- Users pass same flags repeatedly (>5 times)
- Team members need shared settings
- Clear configuration needs emerge from usage

---

### 11. Review/Approval Workflows

**What**: Multi-stage approval (generate → review → approve → commit) with audit trail.

**Why Valuable**: Quality gates, team coordination, accountability.

**Why Deferred**: Adds significant workflow complexity. Single-user manual review proves baseline first.

**Complexity**: High (workflow state, multi-user, notifications)

**Reconsider When**:
- Multiple team members regenerate same docs
- Quality control becomes necessary (approval before merge)
- Audit requirements emerge

---

### 12. Smart Structure Discovery

**What**: LLM analyzes existing docs, proposes template structure automatically.

**Why Valuable**: Reduces manual template creation effort.

**Why Deferred**: Requires deep understanding of what makes good templates. Manual template creation teaches us patterns first.

**Complexity**: High (structure analysis, LLM prompting, validation)

**Reconsider When**:
- Users have created 10+ templates manually
- Clear patterns in successful templates emerge
- Template creation is major friction point

---

### 13. LLM-Generated Templates

**What**: Ask LLM to create template from scratch: `amplifier create-template README --type project-readme`

**Why Valuable**: Ultimate convenience for template creation.

**Why Deferred**: Need to understand template best practices through manual creation first. LLM-generated templates may miss subtle requirements.

**Complexity**: Medium (template generation, validation)

**Reconsider When**:
- Manual template creation is well-understood
- Template patterns are codified
- Users explicitly request "generate template for me"

---

## Optimizations (Performance/UX)

**Reconsider When**: Core functionality works well, performance/UX becomes bottleneck

### 14. Prompt Versioning System

**What**: Version and evolve LLM prompts, track which work best.

**Why Valuable**: Improves generation quality over time.

**Why Deferred**: Need baseline prompts and usage data first. Versioning adds complexity.

**Complexity**: Medium (versioning, analytics, A/B testing)

**Reconsider When**:
- Users frequently tweak prompts for better results
- Clear improvements to prompts emerge
- Quality varies significantly across regenerations

---

### 15. Relevancy Scoring

**What**: Score each source file 1-10 for relevance to doc, include only high-scoring sources.

**Why Valuable**: Reduces context size, improves focus, lowers cost.

**Why Deferred**: Need to understand what "relevant" means through usage. Premature optimization.

**Complexity**: Medium (scoring heuristics, thresholds)

**Reconsider When**:
- Templates regularly include irrelevant sources (>30% unused)
- Context size becomes problem (hitting LLM limits)
- Cost optimization becomes priority

---

### 16. Caching/Efficiency Optimizations

**What**: Cache unchanged source content, skip sections that haven't changed, reuse context.

**Why Valuable**: Faster regeneration, lower cost.

**Why Deferred**: Premature optimization. Need to understand actual performance bottlenecks first.

**Complexity**: Medium (cache invalidation, change detection)

**Reconsider When**:
- Regeneration time >30 seconds regularly
- Cost becomes significant (>$1 per regeneration)
- Clear caching opportunities identified

---

### 17. Incremental Context Updates

**What**: Track which sources changed since last regeneration, only update relevant context.

**Why Valuable**: Efficiency for large source bases.

**Why Deferred**: Complexity without proven need. Full context gathering validates baseline first.

**Complexity**: Medium (change tracking, context diff)

**Reconsider When**:
- Source bases are large (>50 files)
- Full context gathering takes >10 seconds
- Incremental updates clearly faster

---

### 18. Progressive/Streaming Output

**What**: Show generated content as it streams from LLM, not just at completion.

**Why Valuable**: Better UX for slow generations, see progress.

**Why Deferred**: Adds UI complexity. Batch output validates baseline first.

**Complexity**: Medium (streaming, terminal UI)

**Reconsider When**:
- Regeneration regularly takes >30 seconds
- Users report feeling "is this working?" during generation
- Streaming UX clearly valuable

---

## Parking Lot (Unclear Fit)

**Reconsider When**: Specific use cases emerge through real usage

### 19. Template Marketplace

**What**: Share/discover templates created by others.

**Why Uncertain**: Unclear if templates are reusable across projects, what marketplace would look like.

**Next Step**: Understand template reusability through usage first. Are users' templates project-specific or generalizable?

**Reconsider When**:
- Users create 5+ templates and want to share
- Clear demand for "standard templates" emerges
- Reusability patterns are understood

---

### 20. Plugin/Extension System

**What**: Allow custom source readers, LLM providers, output formatters.

**Why Uncertain**: Unclear what needs extending. May be premature abstraction.

**Next Step**: Identify what users want to customize beyond core capabilities.

**Reconsider When**:
- Users request custom functionality 3+ times
- Clear extension points emerge
- Core system proves insufficient for edge cases

---

### 21. Interactive Template Creation Wizard

**What**: CLI wizard to create templates through Q&A: "What type of doc? What sections? What sources?"

**Why Uncertain**: May be more friction than manual template creation. Need to understand template creation patterns first.

**Next Step**: Observe how users create templates manually, identify pain points.

**Reconsider When**:
- Manual template creation has clear friction points
- Template patterns are codified enough to guide
- Users explicitly request "help me create template"

---

## Summary

**Phase 2 (Automation)**: 4 features - Wait for manual flow to prove valuable
**Phase 3 (Multi-Doc)**: 3 features - Wait for single-doc to mature
**Phase 4 (Advanced)**: 7 features - Long-term enhancements
**Optimizations**: 5 features - Wait for performance bottlenecks
**Parking Lot**: 3 features - Unclear fit, wait for clarity

**Total**: 21 deferred features

**Key Insight**: Every deferred feature has clear "Reconsider when" conditions. Nothing is rejected, just waiting for the right time.

---

## Next Review

**Review Trigger**: After feature scope (manual regeneration) ships and is used for 10+ regenerations

**Questions to Answer**:
- Which "Reconsider when" conditions have been met?
- What friction points emerged during real usage?
- What did we learn about the regeneration workflow?
- What should come next based on actual evidence?

---

**Philosophy**: Defer thoughtfully, not permanently. Every idea waits for its right moment.
