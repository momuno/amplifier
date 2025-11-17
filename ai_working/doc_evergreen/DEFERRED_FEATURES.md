# Doc-Evergreen: Deferred Features

**Purpose**: This document captures all features, ideas, and enhancements explored during the convergence session that are explicitly NOT in the MVP. Nothing is lost - everything is preserved with clear "reconsider when" conditions.

**Philosophy**: Deferring isn't deleting. It's strategic postponement until we learn from the MVP what actually matters.

---

## How to Use This Document

Each deferred feature includes:
- **What**: Description of the feature
- **Why Valuable**: The insight/value this would provide
- **Why Deferred**: What must be learned first
- **Reconsider When**: Specific trigger conditions for revisiting

---

## Version 2: High-Priority Post-MVP

These features directly address known pain points but require MVP learnings first.

### 1. Automatic Change Detection

**What**: System automatically detects when source files have changed and determines if docs need updating

**Why Valuable**:
- Eliminates manual decision of "does this doc need regenerating?"
- Proactive rather than reactive doc maintenance
- Catches drift before it becomes problematic

**Why Deferred**:
- Need to understand what constitutes "valuable enough" changes
- Must learn what granularity matters (syntax vs logic vs structure)
- Requires baseline understanding of doc-to-source relationships

**Reconsider When**:
- MVP used successfully for 10+ docs
- Clear patterns emerge about what changes trigger regeneration
- User manually checking "should I regenerate?" becomes tedious

**Implementation Notes**:
- Git hooks to detect changes
- Heuristics for change significance
- User configurable thresholds
- Notification system for recommended updates

---

### 2. Template Lifecycle Management

**What**: System for creating, evolving, and managing templates over time

**Why Valuable**:
- Templates improve through use
- Capture learned patterns
- Reduce manual template editing
- Support template variants for different contexts

**Why Deferred**:
- Need to understand what makes a "good" template first
- Must observe how templates naturally evolve through use
- Template pain points must be experienced to solve correctly

**Reconsider When**:
- User has created 3+ templates manually
- Clear patterns emerge in template structure
- Template editing becomes frequent/tedious
- Quality varies significantly across templates

**Implementation Notes**:
- Template versioning system
- Template analytics (what sections work well)
- Template suggestions from usage patterns
- Template composition (reusable sections)

---

### 3. Intelligent Source Discovery

**What**: System automatically identifies relevant source files for doc generation

**Why Valuable**:
- Eliminates tedious manual source specification
- Discovers non-obvious relevant sources
- Maintains source list as project evolves
- Reduces cognitive load on user

**Why Deferred**:
- Need to learn what sources are actually needed
- Must understand patterns in source-to-doc relationships
- Manual specification teaches what "relevant" means

**Reconsider When**:
- User has regenerated 10+ docs with manual sources
- Clear patterns in which sources are needed for which docs
- Manual source specification becomes primary pain point
- Source lists become long/complex

**Implementation Notes**:
- Code analysis for relationships
- Import/dependency tracking
- Semantic similarity for relevance
- User can override/customize suggestions

---

### 4. Automated Quality Validation

**What**: System automatically checks generated doc quality against criteria

**Why Valuable**:
- Catches issues before user review
- Builds confidence in automation
- Provides objective quality metrics
- Enables unattended regeneration

**Why Deferred**:
- Need to understand what "quality" means for docs
- Must observe what issues actually occur
- Quality criteria are context-dependent

**Reconsider When**:
- 5+ successful regenerations show common quality patterns
- Clear criteria emerge (completeness, accuracy, consistency)
- User spends time checking same things repeatedly
- Quality issues are predictable enough to automate

**Implementation Notes**:
- Completeness checks (all sections present)
- Accuracy checks (code examples work)
- Consistency checks (terminology, formatting)
- Source attribution validation

---

### 5. Git Integration

**What**: Version control integration for doc history and rollback

**Why Valuable**:
- See history of doc evolution
- Rollback if regeneration goes wrong
- Compare versions easily
- Track what changed and why

**Why Deferred**:
- Need to establish regeneration works reliably first
- Must understand what version history is actually useful
- Preview/accept workflow provides safety for now

**Reconsider When**:
- User has regenerated same doc 3+ times
- Need to compare across multiple regenerations
- Rollback becomes necessary (regeneration went wrong)
- History of "why this changed" becomes valuable

**Implementation Notes**:
- Automatic git commits on acceptance
- Structured commit messages with metadata
- Easy diff viewing
- Revert/restore commands

---

### 6. Template Variants & Specialization

**What**: Multiple template variants for different doc types and contexts

**Why Valuable**:
- Different docs have different needs
- Specialization improves quality
- Supports team/project conventions
- Enables experimentation

**Why Deferred**:
- Need baseline template that works first
- Must understand how templates naturally diverge
- Single template tests core assumptions

**Reconsider When**:
- Single template proves insufficient for multiple doc types
- User creates 3+ different templates manually
- Clear categories of docs emerge
- Template customization becomes frequent

**Implementation Notes**:
- Template library/registry
- Template selection heuristics
- Template inheritance/composition
- Per-project template overrides

---

## Future Enhancements: Medium Priority

These add significant value but aren't immediately necessary.

### 7. Meta-Templates & Template Generation

**What**: Templates for creating templates (the recursive layer)

**Why Valuable**:
- Bootstrap new templates faster
- Capture template creation patterns
- Reduce template creation effort
- Enable non-experts to create templates

**Why Deferred**:
- Recursive complexity needs justification
- Must understand template patterns first
- Single layer of templates may be sufficient

**Reconsider When**:
- User has created 5+ templates manually
- Clear patterns in template structure emerge
- Template creation becomes bottleneck
- Template quality varies significantly

---

### 8. Cross-File Relationship Tracking

**What**: Understand and track relationships between docs and sources

**Why Valuable**:
- Detect when change in File A affects docs about File B
- Map dependencies across codebase
- Smarter change detection
- Better source discovery

**Why Deferred**:
- Complex feature requiring significant infrastructure
- Benefit unclear without usage data
- Manual source specification works for now

**Reconsider When**:
- Multi-file impacts become common problem
- Missing relevant sources happens frequently
- User maintains relationship maps manually
- Source discovery is clearly insufficient

---

### 9. Selective Section Regeneration

**What**: Regenerate specific sections while keeping others frozen

**Why Valuable**:
- Preserve manually edited sections
- Surgical updates for efficiency
- Fine-grained control
- Reduce regeneration time

**Why Deferred**:
- Full regeneration tests core assumption first
- Adds complexity to workflow
- Preview/accept provides control for now

**Reconsider When**:
- Users regularly reject full regeneration due to one section
- Manual edits need preservation across regenerations
- Regeneration time becomes problematic
- Section-level control requested explicitly

---

### 10. Multi-Format Output

**What**: Generate same content in multiple formats (HTML, PDF, etc.)

**Why Valuable**:
- Different consumption contexts
- Single source, multiple outputs
- Consistency across formats
- Broader applicability

**Why Deferred**:
- Markdown-only tests core functionality
- Format conversion can be separate step
- Unclear which formats are needed

**Reconsider When**:
- User manually converts markdown to other formats
- Multiple format needs are expressed
- 5+ docs need non-markdown versions
- Format-specific features are required

---

### 11. AI-Curated Source Selection

**What**: LLM helps identify and rank relevant sources for doc generation

**Why Valuable**:
- Smarter than rule-based discovery
- Adapts to project specifics
- Explains relevance reasoning
- Learns from user corrections

**Why Deferred**:
- Adds LLM cost/complexity
- Static heuristics may be sufficient
- Need baseline for comparison

**Reconsider When**:
- Rule-based discovery proves insufficient
- Source selection becomes primary pain point
- User feedback on sources is consistently needed
- Context gathering needs intelligence

---

### 12. Incremental Context Updates

**What**: Only reanalyze sources that changed since last generation

**Why Valuable**:
- Performance optimization
- Reduces LLM token usage
- Faster regeneration
- Better for large projects

**Why Deferred**:
- Premature optimization
- Full regeneration tests assumptions first
- Performance not yet a bottleneck

**Reconsider When**:
- Regeneration takes >30 seconds regularly
- Token costs become significant
- Working with large codebases (100+ files)
- Performance explicitly requested

---

### 13. Collaboration Features

**What**: Multiple users working on docs, review workflows, approval processes

**Why Valuable**:
- Team documentation workflows
- Quality gates before publication
- Shared templates and standards
- Distributed maintenance

**Why Deferred**:
- Solo user workflow comes first
- Collaboration complexity is significant
- Team patterns must be observed

**Reconsider When**:
- Multiple users adopt the tool
- Team coordination becomes pain point
- Review/approval workflows needed
- Shared templates requested

---

### 14. Doc Health Dashboard

**What**: Overview showing status of all docs (stale, healthy, needs review)

**Why Valuable**:
- Visibility into doc ecosystem
- Prioritization of updates
- Track improvement over time
- Identify problematic docs

**Why Deferred**:
- Need multiple docs in system first
- Status criteria must be established
- Single-doc focus for MVP

**Reconsider When**:
- Managing 10+ docs with the tool
- Unclear which docs need attention
- Manual tracking becomes tedious
- Portfolio view is requested

---

## Optimizations: Performance & UX

These improve experience but aren't core functionality.

### 15. Background Processing

**What**: Regenerate docs in background, notify when complete

**Why Valuable**:
- Don't block user workflow
- Handle long-running generations
- Batch processing efficiency
- Better UX for large docs

**Why Deferred**:
- Synchronous execution is simpler
- Generation speed unknown
- Adds complexity for uncertain benefit

**Reconsider When**:
- Generation regularly takes >1 minute
- User wants to continue working during generation
- Batch regeneration becomes common
- Async explicitly requested

---

### 16. Rich Preview UI

**What**: Web-based preview with side-by-side diff, syntax highlighting, etc.

**Why Valuable**:
- Better review experience
- Easier to spot changes
- More context visible
- Professional appearance

**Why Deferred**:
- Terminal diff is sufficient for MVP
- Adds complexity (web server, etc.)
- UX improvements come after core functionality

**Reconsider When**:
- Users struggle with terminal diff
- Review workflow is primary friction
- Large diffs are hard to parse
- UI explicitly requested

---

### 17. Undo/Redo Support

**What**: Easy revert of accepted changes, try different regenerations

**Why Valuable**:
- Safety net for experimentation
- Quick iteration on options
- Reduce fear of acceptance
- Support exploratory workflow

**Why Deferred**:
- Preview/reject provides safety for MVP
- Git integration provides undo later
- Adds state management complexity

**Reconsider When**:
- Users hesitant to accept due to no undo
- Experimentation with options becomes common
- "Try this, try that" workflow emerges
- Requested explicitly after bad regeneration

---

### 18. Caching & Reuse

**What**: Cache analysis results, reuse across regenerations

**Why Valuable**:
- Performance improvement
- Reduce redundant LLM calls
- Lower token costs
- Faster iteration

**Why Deferred**:
- Premature optimization
- Cache invalidation complexity
- Cost/benefit unclear

**Reconsider When**:
- Same sources analyzed repeatedly
- Regeneration cost becomes significant
- Performance explicitly problematic
- Clear reuse patterns emerge

---

## Parking Lot: Interesting But Uncertain

Ideas that came up but need more exploration before even deferring to a version.

### 19. Template Marketplace

**What**: Share/discover templates created by others

**Why Uncertain**:
- Unclear if templates are reusable across projects
- Community size unknown
- Discoverability and trust issues
- May over-engineer template system

**Reconsider When**:
- Active user community exists
- Template sharing requested organically
- Clear value in others' templates demonstrated

---

### 20. Hooks & Extensions

**What**: Plugin system for custom pre/post processing

**Why Uncertain**:
- Unclear what customization is needed
- May add unnecessary complexity
- Core functionality may be sufficient

**Reconsider When**:
- Users hacking around limitations consistently
- Clear extension patterns emerge
- 3+ projects need same custom behavior

---

### 21. LLM Learning & Improvement

**What**: System learns from corrections and improves over time

**Why Uncertain**:
- Technically complex (fine-tuning, etc.)
- Benefit unclear vs prompt engineering
- May be solving wrong problem

**Reconsider When**:
- Same corrections made repeatedly
- Clear patterns in user edits
- Prompt engineering hits limits
- ML expertise available

---

### 22. Doc Publishing Integration

**What**: Generate and publish to doc sites (ReadTheDocs, etc.)

**Why Uncertain**:
- May be separate concern
- Publishing tools already exist
- Unclear integration value

**Reconsider When**:
- Users manually publish generated docs
- Publishing workflow is friction
- Integration clearly valuable

---

### 23. Testing & Validation Framework

**What**: Test generated docs (code examples work, links valid, etc.)

**Why Uncertain**:
- Scope may be too large
- Existing tools may suffice
- Quality validation strategy unclear

**Reconsider When**:
- Generated docs have broken examples
- Quality issues are consistent
- Manual testing becomes bottleneck
- Automated testing clearly needed

---

## Summary Statistics

**Total Features Explored**: 23
**Version 2 (High Priority)**: 6 features
**Future Enhancements (Medium Priority)**: 8 features
**Optimizations (Performance/UX)**: 4 features
**Parking Lot (Uncertain)**: 5+ ideas

**Key Insight**: We explored 23 features but are building only 3 for MVP. This is excellent convergence - 87% of ideas thoughtfully deferred with clear reconsider conditions.

---

## Using This Document

**During MVP Development**:
- Resist adding deferred features
- Reference this when tempted to expand scope
- Use as reminder of what we're learning toward

**After MVP Success**:
- Review "Reconsider When" conditions
- Identify which triggers have occurred
- Prioritize based on actual learnings
- Update this document as features are built or new ideas emerge

**When Ideas Come Up**:
- Add to appropriate section
- Include reconsider conditions
- Don't lose the insight
- Resist immediate implementation

---

## Philosophy Alignment

This deferral strategy embodies:

**Ruthless Simplicity**:
- Build 13% of explored features
- Learn what matters through use
- Avoid premature complexity

**Trust in Emergence**:
- Features will prove their necessity
- Patterns will reveal what to build next
- The right next step becomes obvious

**Present-Moment Focus**:
- Solve today's problem (stale docs)
- Don't build for hypothetical futures
- Let needs drive development

**Learning Stance**:
- MVP teaches what matters
- Deferred features compete for next sprint
- Data beats speculation

---

**Nothing is lost. Everything is preserved. The best features will prove themselves through use.**
