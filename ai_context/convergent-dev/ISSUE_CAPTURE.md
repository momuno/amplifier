# Workflow: Issue Capture (Issue-Capturer)

**Purpose**: Systematically capture, investigate, and track issues from free-form user feedback, creating persistent documentation that feeds into sprint planning.

**Agent**: `issue-capturer`
**Command**: `/convergent-dev:4-capture-issues [project-name]`
**Duration**: 15-45 minutes (depending on issue count)
**Output**: Persistent markdown issue tracking files

---

## When to Use This Workflow

✅ **Use when:**
- After user testing reveals bugs or issues
- Gathering feedback on implemented features
- Before planning the next iteration/sprint
- Multiple issues need systematic tracking
- Post-sprint cleanup agent identifies minor issues
- Completing the convergent-dev cycle

❌ **Don't use when:**
- Single trivial issue (just fix it directly)
- Issues already well-documented elsewhere
- Still in exploratory/prototyping phase

---

## The Issue Capture Process

### Overview: Five Modes

The issue-capturer operates in five sequential modes:

1. **CAPTURE** - Parse free-form feedback into discrete issues
2. **INVESTIGATE** - Understand root causes (delegates to bug-hunter for complex cases)
3. **DOCUMENT** - Create persistent markdown tracking
4. **INTEGRATE** - (Optional) Create beads issues for workflow integration
5. **SUMMARIZE** - Provide overview for convergence/sprint planning

---

### Mode 1: CAPTURE (Parse Feedback)

**Goal**: Transform free-form feedback into discrete, trackable issues without loss.

**What Happens**:
- Agent reads all feedback carefully
- Parses into discrete issues (ISSUE-001, ISSUE-002, etc.)
- Separates symptoms from root causes
- Performs initial categorization

**Initial Categorization**:
- **Type**: Bug | Enhancement | Feature
- **Priority**: Critical | High | Medium | Low
- **Affected component/area**

**Example**:
```
User feedback: "The CLI crashes on empty input, output format is inconsistent,
and it's slow on large files"

Parsed issues:
- ISSUE-001: CLI crashes on empty input (Bug, High priority)
- ISSUE-002: Output format inconsistent (Bug, Medium priority)
- ISSUE-003: Slow performance on large files (Enhancement, Medium priority)
```

---

### Mode 2: INVESTIGATE (Root Cause Analysis)

**Goal**: Understand each issue deeply through systematic investigation.

**What Happens**:
- Agent attempts to reproduce each issue
- Identifies root causes
- For complex issues: Delegates to `bug-hunter` agent
- Documents investigation findings

**Investigation Includes**:
- Reproduction steps
- Expected vs. actual behavior
- Root cause analysis
- Affected files/components
- Potential solutions

**Bug-Hunter Integration**:
```
For complex debugging:
1. issue-capturer identifies issue needs deep investigation
2. Delegates to bug-hunter agent
3. bug-hunter performs hypothesis-driven debugging
4. Returns findings to issue-capturer
5. issue-capturer incorporates into issue documentation
```

**Example Investigation**:
```markdown
**Reproduction Steps:**
1. Run `doc-update --context-dir ./empty`
2. Observe CLI crashes with stack trace

**Root Cause:**
Context gathering module doesn't handle empty directories.
Missing validation in `src/context/gather.py` line 42.

**Expected Behavior:**
Should display clear error message: "No context files found in ./empty"
```

---

### Mode 3: DOCUMENT (Persistent Tracking)

**Goal**: Create markdown files following consistent format for long-term tracking.

**Files Created**:

**1. `ISSUES_TRACKER.md`** (Master list):
```markdown
# Issues Tracker - [Project Name]

## Open Issues

### ISSUE-001: CLI crashes on empty input
- **Status**: Open
- **Priority**: High
- **Type**: Bug
- **Assigned to**: Unassigned
- **Created**: 2025-01-19
- **Sprint**: TBD

[Full details →](./ISSUE-001-cli-crash-empty-input.md)

---

## In Progress

(Issues currently being worked on)

---

## Resolved

(Completed issues with resolution notes)
```

**2. Individual Issue Files** (`ISSUE-00X-description.md`):
```markdown
# ISSUE-001: CLI crashes on empty input

**Status**: Open
**Priority**: High
**Type**: Bug
**Created**: 2025-01-19
**Updated**: 2025-01-19

## Description

The CLI crashes with a stack trace when run with an empty context directory
instead of displaying a clear error message.

## Reproduction Steps

1. Create empty directory: `mkdir empty-context`
2. Run: `doc-update --context-dir ./empty-context`
3. Observe crash

## Expected Behavior

Should display: "No context files found in ./empty-context"

## Actual Behavior

```
Traceback (most recent call last):
  File "src/context/gather.py", line 42
  ...
```

## Root Cause

Context gathering module (`src/context/gather.py` line 42) doesn't validate
for empty directories before attempting to process files.

## Acceptance Criteria

- [ ] Empty directory displays clear error message
- [ ] No stack trace visible to user
- [ ] Exit code 1 (error) returned
- [ ] Test added for empty directory case

## Affected Files

- `src/context/gather.py`
- `tests/test_context_gather.py` (needs new test)

## Sprint Assignment

TBD (to be assigned during sprint planning)

## Beads ID

(Optional: bd-123 if integrated with beads workflow)
```

**Format Benefits**:
- Survives chat compaction (persistent markdown)
- Human-readable (not just for tools)
- Integrates with sprint planning
- Optional beads integration for workflow tracking

---

### Mode 4: INTEGRATE (Optional Beads Integration)

**Goal**: Create beads issues for workflow integration.

**When to Use**:
- Project uses beads for issue tracking
- Want sprint workflow integration
- Need cross-repository issue tracking

**What Happens**:
1. For each captured issue, create corresponding beads issue
2. Link beads ID back to markdown file
3. Sync status between markdown and beads
4. Enable sprint assignment through beads

**Integration Pattern**:
```bash
# issue-capturer creates markdown
ISSUE-001 → ai_working/project/issues/ISSUE-001-description.md

# Also creates beads issue
bd create --title "CLI crashes on empty input" \
  --type bug --priority high \
  --description "See ai_working/project/issues/ISSUE-001-description.md"

# Links them bidirectionally
ISSUE-001 ← beads:bd-123
```

---

### Mode 5: SUMMARIZE (Prepare for Next Phase)

**Goal**: Provide actionable overview for convergence or sprint planning.

**Summary Includes**:
- Total issues captured
- Breakdown by priority
- Breakdown by type
- Critical issues requiring immediate attention
- Recommended next steps

**Example Summary**:
```
✅ Issue Capture Complete

Captured 5 issues for doc_evergreen:
- 2 High priority bugs
- 2 Medium priority enhancements
- 1 Low priority feature request

Critical Issues (recommend addressing before next sprint):
- ISSUE-001: CLI crashes on empty input (High, Bug)
- ISSUE-004: Data loss on interrupt (High, Bug)

Next Steps:
1. Address critical issues immediately, OR
2. Use /converge to define new feature scope (captures all issues to planning)
3. Use /plan-sprints to integrate issues into sprint plans

All issues tracked in: ai_working/doc_evergreen/issues/ISSUES_TRACKER.md
```

---

## Outputs Created

### Directory Structure

```
ai_working/[project]/issues/
├── ISSUES_TRACKER.md           # Master list (GitHub/Jira style)
├── ISSUE-001-description.md    # Individual issue details
├── ISSUE-002-description.md
├── ISSUE-003-description.md
└── ...
```

### Key Files

**1. `ISSUES_TRACKER.md`**:
- Master list of all issues
- Organized by status (Open | In Progress | Resolved)
- Quick overview with links to details
- Updated continuously as issues progress

**2. Individual Issue Files**:
- Full investigation details
- Reproduction steps
- Root cause analysis
- Acceptance criteria
- Sprint assignment
- Resolution notes (when closed)

---

## Integration with Convergent-Dev Workflow

### The Complete Cycle

```
1. /converge                      → Feature scope defined
2. /plan-sprints                  → Sprints planned (with existing issues)
3. /tdd-cycle                     → Implementation with TDD
4. /capture-issues [project]      → Testing feedback captured
   └─→ Issues stored in ISSUES_TRACKER.md
   └─→ (cycle repeats: issues feed into next /plan-sprints)
```

### How Issues Flow

**After Implementation**:
1. User tests implemented features
2. Discovers bugs, performance issues, improvements
3. Provides feedback (free-form is fine)
4. Post-task-cleanup agent may identify minor issues
5. issue-capturer captures everything systematically

**Issues Are Stored**:
- Persistent markdown files survive chat compaction
- ISSUES_TRACKER.md is single source of truth
- Ready for next planning cycle

**Next Convergence**:
- Focuses on new feature scope exploration
- Doesn't get distracted by existing issues
- Backlog for new ideas remains separate from bug tracking

**Next Sprint Planning**:
- sprint-planner reads ISSUES_TRACKER.md
- Evaluates which issues to integrate with feature scope work
- Decides: fix now, defer to later, or bundle with feature work
- Assigns issues to appropriate sprints

**Example Integration**:
```
Sprint 5 Plan includes:
- New feature: Export functionality (from feature scope)
- ISSUE-001: CLI crash on empty input (High priority bug)
- ISSUE-003: Slow on large files (fits naturally with export work)

Deferred:
- ISSUE-002: Output format (low priority, addressed in Sprint 6)
```

---

## Agent Coordination

### Primary Agent: issue-capturer

**Responsibilities**:
- Parse feedback into discrete issues
- Orchestrate investigation process
- Create and maintain markdown files
- Integrate with beads (optional)
- Summarize for next workflow phase

### Delegated Agent: bug-hunter

**When Used**: Complex issues requiring deep investigation

**Delegation Pattern**:
```
issue-capturer: "ISSUE-003 is complex, need deep debugging"
  ↓
bug-hunter: Performs hypothesis-driven debugging
  - Reproduces issue systematically
  - Tests hypotheses
  - Identifies root cause
  - Suggests fixes
  ↓
issue-capturer: Incorporates findings into documentation
```

**Example**:
```
ISSUE-003: Memory leak in long-running process

issue-capturer identifies: "This requires profiling and debugging"
Delegates to bug-hunter

bug-hunter investigates:
- Profiles memory usage over time
- Identifies leaked objects
- Traces to source in caching module
- Suggests fix: implement cache eviction

issue-capturer documents:
- Root cause from bug-hunter
- Affected files
- Proposed solution
- Acceptance criteria
```

---

## Real-World Example: doc_evergreen

### Starting Context

After Sprint 4 completion, user tests the tool and provides feedback:

```
User: "I've been testing doc-update and found a few issues:
1. It crashes when I point it at an empty directory
2. The output markdown has inconsistent spacing
3. It's really slow on my large codebase (50+ files)
Also, it would be nice if I could specify output format."
```

### CAPTURE Phase

```
issue-capturer parses feedback:

ISSUE-001: CLI crashes on empty directory (Bug, High)
ISSUE-002: Inconsistent spacing in output (Bug, Medium)
ISSUE-003: Slow performance on large codebases (Enhancement, Medium)
ISSUE-004: Output format configuration (Feature, Low)
```

### INVESTIGATE Phase

```
For ISSUE-001 (straightforward):
- Reproduces crash
- Identifies missing validation
- Documents fix approach

For ISSUE-003 (complex):
- Delegates to bug-hunter
- bug-hunter profiles execution
- Identifies sequential processing bottleneck
- Suggests parallel processing solution
```

### DOCUMENT Phase

```
Creates files:
- ai_working/doc_evergreen/issues/ISSUES_TRACKER.md
- ai_working/doc_evergreen/issues/ISSUE-001-empty-dir-crash.md
- ai_working/doc_evergreen/issues/ISSUE-002-spacing-inconsistent.md
- ai_working/doc_evergreen/issues/ISSUE-003-slow-large-files.md
- ai_working/doc_evergreen/issues/ISSUE-004-format-config.md
```

### SUMMARIZE Phase

```
✅ Captured 4 issues for doc_evergreen:
- 1 High priority bug (ISSUE-001)
- 1 Medium priority bug (ISSUE-002)
- 1 Medium priority enhancement (ISSUE-003)
- 1 Low priority feature (ISSUE-004)

Recommend:
1. Fix ISSUE-001 immediately (crashes are critical)
2. Integrate ISSUE-002, ISSUE-003 into next sprint planning
3. Defer ISSUE-004 to backlog (low priority feature)

Next: Use /converge for new features OR /plan-sprints to plan fixes
```

---

## Tips for Effective Issue Capture

### Providing Feedback

✅ **Do**:
- Be casual and natural (agent parses free-form text)
- Include specific examples (commands, inputs, outputs)
- Mention multiple issues at once (agent separates them)
- Describe what you expected vs. what happened
- Include error messages if available

❌ **Don't**:
- Try to pre-categorize or format
- Worry about being too detailed
- Self-censor "minor" issues
- Create your own issue IDs

### During Investigation

✅ **Do**:
- Answer clarifying questions from agent
- Provide additional context if requested
- Confirm reproduction steps
- Verify root cause analysis makes sense

❌ **Don't**:
- Rush the investigation
- Skip reproduction verification
- Assume agent knows your context

### After Capture

✅ **Do**:
- Review ISSUES_TRACKER.md for accuracy
- Confirm priority assessments
- Note any critical issues for immediate attention
- Use issues in sprint planning

❌ **Don't**:
- Ignore captured issues
- Let them drift without status updates
- Forget to integrate with sprint planning

---

## Common Scenarios

### Scenario 1: Multiple Bugs After Testing

**User**: "Just finished testing Sprint 4. Found 3 bugs and have some improvement ideas."

**Process**:
1. `/capture-issues doc_evergreen`
2. Describe bugs and ideas naturally
3. Agent captures and investigates each
4. Creates persistent tracking
5. Summarizes for next planning

**Outcome**: 3 bugs + 2 enhancements documented, ready for Sprint 5 planning.

---

### Scenario 2: Critical Issue During Development

**User**: "The tool is crashing on production data!"

**Process**:
1. `/capture-issues doc_evergreen` (captures as high priority)
2. Agent delegates to bug-hunter for urgent investigation
3. Root cause identified quickly
4. Issue documented with fix approach
5. Can address immediately or in next sprint

**Outcome**: Critical bug tracked with investigation complete.

---

### Scenario 3: Post-Sprint Cleanup Findings

**Context**: post-task-cleanup agent runs after Sprint 4, identifies minor issues

**Process**:
1. Cleanup agent notes: inconsistent naming, unused imports, type errors
2. `/capture-issues doc_evergreen`
3. Captures cleanup findings as low-priority enhancements
4. Documents systematically
5. Integrates into Sprint 5 planning

**Outcome**: Technical debt tracked alongside feature work.

---

## Success Criteria

Issue capture is successful when:

✅ All feedback parsed into discrete issues
✅ Each issue has clear reproduction steps
✅ Root causes identified (or investigation path documented)
✅ Persistent markdown files created
✅ Issues ready for sprint planning integration
✅ Critical issues flagged for immediate attention
✅ Summary provided for next workflow phase

---

## Integration with Other Workflows

**Before this workflow**:
- Used `/converge` for feature scope
- Used `/plan-sprints` for sprint breakdown
- Used `/tdd-cycle` for implementation
- User testing revealed issues

**During this workflow**:
- Capture feedback systematically
- Investigate issues thoroughly
- Document persistently
- Integrate with beads (optional)
- Summarize for planning

**After this workflow**:
- Issues tracked in ISSUES_TRACKER.md
- Ready for next `/converge` (new features) or `/plan-sprints` (integrate issues)
- Critical issues can be addressed immediately
- Cycle repeats with next convergence

**Complete chain**:
```
Idea → [/converge] → Feature Scope → [/plan-sprints] → Sprints → [/tdd-cycle] → Code → [/capture-issues] → (cycle repeats)
```

---

## Command Usage

### Basic Usage

```bash
/convergent-dev:4-capture-issues [project-name]
```

**Example**:
```bash
/convergent-dev:4-capture-issues doc_evergreen
```

**What happens**:
1. Launches issue-capturer agent
2. Agent asks for feedback
3. You describe issues (free-form)
4. Agent captures, investigates, documents
5. Creates ISSUES_TRACKER.md and individual issue files
6. Provides summary for next steps

---

## Philosophy Alignment

This workflow embodies the project's core principles:

**Ruthless Simplicity**:
- Direct feedback capture (no complex forms)
- Markdown files (simple, persistent)
- Clear investigation process

**Systematic Approach**:
- Five-mode process ensures thoroughness
- No issues lost through chat compaction
- Delegated investigation when needed

**Integration with Workflow**:
- Feeds naturally into sprint planning
- Separates bug tracking from feature exploration
- Enables continuous improvement

**Trust in Tools**:
- Delegates complex debugging to bug-hunter
- Uses beads when appropriate
- Leverages markdown for persistence

---

**Ready to capture issues? Run `/convergent-dev:4-capture-issues [project-name]`**
