# doc_evergreen - Master Feature Backlog

**Purpose**: Consolidated backlog of ALL deferred features from all convergence sessions. This is the single source of truth for what's been explored, what's deferred, and what's been implemented.

**Philosophy**: Nothing is lost. Ideas wait here until the right "reconsider when" conditions are met.

**Last Updated**: 2025-11-18

---

## Overview

| Category | Count | Notes |
|----------|-------|-------|
| **Implemented** | 8 features | Sprints 1-4 (Problem A), Sprints 5-7 (Problem B MVP) |
| **Problem A Deferred** | 23 features | From template-system convergence |
| **Problem B Deferred** | 13 features | From chunked-generation convergence |
| **Total Backlog** | 36 features | Available for future releases |

---

## ✅ Implemented Features

### Problem A (v0.1.0 - Template System - Sprints 1-4)
- [x] Template-based document structure
- [x] Source resolution (glob patterns)
- [x] Hierarchical source inheritance
- [x] Single-shot full-document generation
- [x] Preview & accept workflow

### Problem B (v0.2.0 - Chunked Generation - Sprints 5-7)
- [x] Section-level prompts (explicit control)
- [x] Sequential DFS generation
- [x] Context flow between sections
- [x] Section review checkpoints
- [x] Source validation (ISSUE-001 fix)
- [x] Source visibility (ISSUE-003 fix)

---

## 🔄 Active Deferred Features

### Problem B - Phase 2: Post-Order Validation (After v0.2.0)

**Reconsider When**: v0.2.0 proves chunked generation works but reveals consistency issues

#### 1. Post-Order Validation and Updates
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: After generating all sections, validate consistency and update earlier sections
**Why Valuable**: Earlier sections can reference later concepts, ensures document-wide consistency
**Complexity**: High (bidirectional flow, state management)
**Reconsider When**:
- Users frequently edit earlier sections after seeing later ones
- Inconsistencies between sections are common (>20% of docs)
- Users request "make Introduction match Features" explicitly

#### 2. Sibling Consistency Checks
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Validate sibling sections don't overlap, complement each other
**Why Valuable**: Prevents duplicate content, ensures coverage
**Complexity**: Medium
**Reconsider When**:
- Overlapping content appears frequently (>10% of docs)
- Users manually check for gaps/overlaps
- Clear validation rules emerge

#### 3. Tree Backtracking (Iterative Refinement)
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Multiple passes to refine sections
**Why Valuable**: Higher quality through iterative improvement
**Complexity**: High (convergence criteria, loop control)
**Reconsider When**:
- Single-pass quality is consistently insufficient (<70% acceptable)
- Users frequently regenerate entire docs for minor fixes

---

### Problem B - Phase 3: Dynamic & Adaptive (After Phase 2)

**Reconsider When**: Phase 2 is implemented and static templates prove too rigid

#### 4. Dynamic Tree Growth
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: LLM proposes new sections during generation, user approves
**Why Valuable**: Adapts structure to content
**Complexity**: High (LLM proposals, tree modification)
**Reconsider When**:
- Users frequently add sections manually after generation (>30% of docs)
- Template structure proves too rigid

#### 5. State Management / Resume Capability
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Save progress, resume from checkpoint if interrupted
**Why Valuable**: Handle long-running generations, recover from interruptions
**Complexity**: Medium (state serialization)
**Reconsider When**:
- Generation regularly takes >10 minutes
- Interruptions are common problem

#### 6. Advanced Forward Reference Handling
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Sophisticated forward reference management
**Why Valuable**: Natural technical writing patterns
**Complexity**: Medium
**Reconsider When**:
- Basic forward reference validation proves insufficient
- Complex cross-reference needs emerge

---

### Problem B - Optimizations (Performance/UX)

**Reconsider When**: Core functionality works well, performance becomes bottleneck

#### 7. Parallel Section Generation
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Generate independent sections simultaneously
**Why Valuable**: 2-5x faster generation
**Complexity**: Medium (dependency management)
**Reconsider When**:
- Generation time >5 minutes regularly
- Clear independent sections identified

#### 8. Context Window Modes
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Adaptive context sizing (minimal/standard/comprehensive)
**Why Valuable**: Balance between quality and cost
**Complexity**: Low
**Reconsider When**:
- Token costs become significant
- Context strategies show clear trade-offs

#### 9. Smart Section Ordering
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Optimal generation order based on dependencies
**Why Valuable**: Better context flow
**Complexity**: Medium (dependency analysis)
**Reconsider When**:
- Template order proves suboptimal frequently
- Dependency patterns are clear

---

### Problem B - Advanced Features

**Reconsider When**: All Phase 2 and Phase 3 features implemented, need next evolution

#### 10. Multi-Document Coordination
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Generate multiple related documents with consistency
**Why Valuable**: Documentation suites with cross-references
**Complexity**: High (cross-doc coordination)
**Reconsider When**:
- Users maintain 5+ related docs
- Cross-doc consistency is manual

#### 11. Template Learning from Generated Content
**Origin**: Problem B convergence (2025-11-18-chunked-generation)
**What**: Improve templates based on what works
**Why Valuable**: Templates evolve with usage
**Complexity**: High (ML/pattern recognition)
**Reconsider When**:
- Clear patterns in successful vs unsuccessful generations
- Template refinement is manual and tedious

---

### Problem A - Version 2 (High Priority)

**Reconsider When**: Template system (v0.1.0) is in active use

#### 12. Automatic Change Detection
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Detect when source files changed, determine if docs need updating
**Why Valuable**: Proactive doc maintenance
**Complexity**: Medium (git hooks, heuristics)
**Reconsider When**:
- MVP used for 10+ docs
- Manually checking "should I regenerate?" becomes tedious

#### 13. Template Lifecycle Management
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Create, evolve, and manage templates over time
**Why Valuable**: Templates improve through use
**Complexity**: Medium (versioning, analytics)
**Reconsider When**:
- User has created 3+ templates manually
- Template editing becomes frequent

#### 14. Intelligent Source Discovery
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Auto-identify relevant source files
**Why Valuable**: Eliminates manual source specification
**Complexity**: High (code analysis, dependency tracking)
**Reconsider When**:
- User has regenerated 10+ docs with manual sources
- Manual source specification is primary pain point

#### 15. Automated Quality Validation
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Check generated doc quality against criteria
**Why Valuable**: Catches issues before user review
**Complexity**: Medium (define criteria, implement checks)
**Reconsider When**:
- 5+ successful regenerations show common quality patterns
- User checks same things repeatedly

#### 16. Git Integration
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Version control integration for doc history
**Why Valuable**: See evolution, rollback if needed
**Complexity**: Low (git commands, commit messages)
**Reconsider When**:
- User has regenerated same doc 3+ times
- Rollback becomes necessary

#### 17. Template Variants & Specialization
**Origin**: Problem A convergence (2025-11-18-problem-a-template-system)
**What**: Multiple templates for different doc types
**Why Valuable**: Specialization improves quality
**Complexity**: Medium (template library, selection)
**Reconsider When**:
- Single template proves insufficient
- User creates 3+ different templates

---

### Problem A - Future Enhancements (Medium Priority)

**Reconsider When**: Version 2 features are implemented, need next capabilities

#### 18-36. (23 total features from Problem A)
See `convergence/2025-11-18-problem-a-template-system/DEFERRED_FEATURES.md` for complete list including:
- Meta-templates & template generation
- Cross-file relationship tracking
- Selective section regeneration
- Multi-format output
- AI-curated source selection
- Incremental context updates
- Collaboration features
- Doc health dashboard
- Background processing
- Rich preview UI
- Undo/redo support
- Caching & reuse
- Template marketplace (parking lot)
- Hooks & extensions (parking lot)
- LLM learning (parking lot)
- Doc publishing integration (parking lot)
- Testing & validation framework (parking lot)

---

## 📊 Backlog Statistics

### By Phase
- **v0.1.0 (Implemented)**: 5 features (Problem A)
- **v0.2.0 (Implemented)**: 6 features (Problem B)
- **Phase 2 (Problem B)**: 3 features
- **Phase 3 (Problem B)**: 3 features
- **Optimizations (Problem B)**: 3 features
- **Advanced (Problem B)**: 2 features
- **Version 2 (Problem A)**: 6 features
- **Future (Problem A)**: 17 features

### By Complexity
- **Low**: ~5 features
- **Medium**: ~15 features
- **High**: ~16 features

### By Origin
- **Problem A** (Template System): 23 deferred features
- **Problem B** (Chunked Generation): 13 deferred features

---

## 🎯 Prioritization Framework

Features move from backlog to active development when:

1. **"Reconsider When" conditions are met** (data-driven triggers)
2. **User pain is validated** (multiple requests, clear patterns)
3. **MVP learning is complete** (we understand the problem space)
4. **Complexity is justified** (value > implementation cost)

### Current Priority Queue (After v0.2.0)

**Next Up (Phase 2 - Problem B)**:
1. Post-order validation (if consistency issues emerge)
2. Sibling checks (if overlap/gaps are common)
3. Tree backtracking (if single-pass quality insufficient)

**Watching (Problem A)**:
- Automatic change detection
- Template lifecycle management
- Intelligent source discovery

**Parking Lot**:
- Everything else waits for trigger conditions

---

## 📝 Using This Backlog

### When MVP Completes
1. Review "Reconsider When" conditions
2. Check which triggers have occurred
3. Prioritize based on actual learnings
4. Move features to active sprint planning

### When New Ideas Arise
1. Add to this document under appropriate origin/phase
2. Include "Reconsider When" conditions
3. Assign complexity estimate
4. Don't immediately implement (defer thoughtfully)

### When Planning Next Release
1. Check all "Reconsider When" conditions
2. Validate with user data (not speculation)
3. Select 3-5 features for next convergence
4. Create new convergence session

---

## 🔗 Related Documents

- **Problem A Details**: `convergence/2025-11-18-problem-a-template-system/DEFERRED_FEATURES.md`
- **Problem B Details**: `convergence/2025-11-18-chunked-generation/DEFERRED_FEATURES.md`
- **Issues Tracker**: `issues/ISSUES_TRACKER.md`
- **Sprint Plans**: `sprints/` (once created)

---

## Philosophy Alignment

This backlog embodies:

**Ruthless Simplicity**:
- Implemented 11 features out of 49 explored (22%)
- 78% thoughtfully deferred with clear conditions

**Trust in Emergence**:
- Features prove necessity through use
- Data beats speculation

**Present-Moment Focus**:
- Solve current problems (documentation control)
- Let needs drive development

**Learning Stance**:
- MVPs teach what matters
- Deferred features wait for validation
- Every release informs the next

---

**Last Review**: 2025-11-18
**Next Review**: After Sprints 5-7 complete (v0.2.0 release)
**Review Trigger**: When any "Reconsider When" condition is met
