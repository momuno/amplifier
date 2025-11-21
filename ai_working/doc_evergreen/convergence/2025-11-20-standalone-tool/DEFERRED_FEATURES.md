# Deferred Features

**Version**: Post-v0.4.0 (v0.5.0+)
**Date**: 2025-11-20

---

## Philosophy

These features are valuable but NOT required for standalone tool MVP. Each is deferred with clear **reconsider conditions** - when user feedback or usage patterns indicate need.

---

## Deferred Feature List

### 1. PyPI Publishing

**What**: Publish doc-evergreen to PyPI for `pip install doc-evergreen`

**Why Deferred**:
- Git-based install (`pipx install git+https://...`) works fine
- No distribution infrastructure needed yet
- Can publish when tool matures

**Reconsider When**:
- 10+ external users requesting pip install
- Tool is stable and production-ready
- Willing to commit to version stability

**Estimated Effort**: 1-2 days (packaging, testing, publishing)

---

### 2. Advanced Template Discovery

**What**: Search parent directories for templates, global template library

**Why Deferred**:
- `.doc-evergreen/` convention is sufficient
- Additional complexity without proven need
- User can always use absolute paths

**Reconsider When**:
- Users request mono-repo support
- Common pattern emerges of shared templates
- Template reuse across projects is common

**Estimated Effort**: 3-4 hours

---

### 3. Project-Level Config File

**What**: `.doc-evergreen/config.json` for project defaults

**Why Deferred**:
- Templates already configure everything needed
- YAGNI - no proven need yet
- Adds configuration complexity

**Reconsider When**:
- Users have 5+ templates per project
- Common settings duplicated across templates
- Users request default overrides

**Estimated Effort**: 2-3 hours

---

### 4. Template Marketplace

**What**: Share templates across projects, community templates

**Why Deferred**:
- Need multiple projects using tool first
- Patterns haven't emerged yet
- Premature standardization

**Reconsider When**:
- 5+ projects documented successfully
- Common templates identified
- Users asking "where can I find templates for X?"

**Estimated Effort**: 1-2 days

---

### 5. Watch Mode / Auto-Regeneration

**What**: `doc-evergreen watch` auto-regenerates on file changes

**Why Deferred**:
- Manual regeneration workflow sufficient
- Adds complexity (file watching, debouncing)
- No user request for this yet

**Reconsider When**:
- Users report running regen frequently
- Workflow friction with manual regeneration
- Clear demand for auto-regen

**Estimated Effort**: 4-6 hours

---

### 6. CI/CD Integration Helpers

**What**: Pre-built GitHub Actions, GitLab CI templates

**Why Deferred**:
- Users can script `doc-evergreen regen` themselves
- CI/CD usage patterns not clear yet
- Tool not stable enough for CI/CD

**Reconsider When**:
- Multiple users implementing CI/CD
- Common patterns emerge
- Tool is production-stable

**Estimated Effort**: 3-4 hours

---

### 7. Multi-Project Aggregation

**What**: Document multiple projects into single output

**Why Deferred**:
- No use case identified yet
- Unclear what this would look like
- Single-project focus is clean

**Reconsider When**:
- User requests "document my mono-repo"
- Cross-project documentation need emerges
- Clear value proposition appears

**Estimated Effort**: 1-2 days

---

### 8. IDE Integration

**What**: VSCode extension, editor plugins

**Why Deferred**:
- CLI workflow works
- Premature - tool not mature enough
- Maintenance burden significant

**Reconsider When**:
- Tool is widely adopted
- Users request editor integration
- Core functionality is stable

**Estimated Effort**: 1-2 weeks

---

### 9. Git Integration

**What**: Auto-commit generated docs, PR creation

**Why Deferred**:
- Users can commit manually
- Opinionated workflow
- Not core to doc generation

**Reconsider When**:
- Users consistently forget to commit docs
- Workflow pattern emerges
- Clear automation opportunity

**Estimated Effort**: 4-6 hours

---

### 10. Single-Shot Mode (ISSUE-009)

**What**: Implement true single-shot generation (non-chunked)

**Why Deferred**:
- Chunked mode works well
- No performance issues reported
- Not needed for standalone functionality

**Reconsider When**:
- Performance issues with chunked mode
- Context management becomes problem
- Users specifically request single-shot

**Estimated Effort**: 1 day

---

### 11. Mode Clarity Documentation (ISSUE-008)

**What**: Explain chunked vs single-shot modes clearly

**Why Deferred**:
- Only chunked mode exists currently
- No confusion when there's one mode
- Becomes relevant if ISSUE-009 implemented

**Reconsider When**:
- Single-shot mode is implemented
- Users confused about mode selection

**Estimated Effort**: 2-3 hours (documentation)

---

### 12. Template Versioning

**What**: Version templates, lock projects to template versions

**Why Deferred**:
- Templates are simple enough to not need versioning
- No breaking changes anticipated
- Adds complexity without proven need

**Reconsider When**:
- Template format changes breaking old templates
- Users need to lock to specific versions
- Template evolution causes issues

**Estimated Effort**: 4-6 hours

---

### 13. Dry-Run Mode

**What**: Show what would change without applying

**Why Deferred**:
- Current diff preview + approval achieves this
- Can reject changes if not ready
- Duplication of existing workflow

**Reconsider When**:
- Users want to preview without generation cost
- Large projects where generation is expensive

**Estimated Effort**: 2-3 hours

---

### 14. Backup/Rollback

**What**: Automatic backups before overwriting, rollback capability

**Why Deferred**:
- Git provides version control (users should use it)
- Adds storage and complexity
- Not core documentation feature

**Reconsider When**:
- Users report data loss incidents
- Projects without git need safety net

**Estimated Effort**: 4-6 hours

---

### 15. Performance Optimization

**What**: Caching, parallel generation, optimized prompts

**Why Deferred**:
- Current performance acceptable
- No complaints about speed
- Premature optimization

**Reconsider When**:
- Generation takes >30s per section consistently
- Users report slow performance
- Large projects hit limits

**Estimated Effort**: 1-2 days

---

## Return to Backlog

All deferred features should be added to `MASTER_BACKLOG.md` with:
- Reconsider conditions
- Estimated effort
- Links to this document

When conditions are met, features can be pulled into future convergence cycles.

---

## Remember

**Deferral ≠ Rejection**

Every deferred feature:
- Has clear value
- Could be implemented later
- Has conditions for reconsideration
- Is preserved for future planning

**Focus wins**: Shipping 5 features well > planning 15 features poorly.
