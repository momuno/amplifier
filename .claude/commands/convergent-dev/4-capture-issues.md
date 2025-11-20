# Capture Issues Command

**Purpose**: Systematically capture, investigate, and track issues from free-form feedback.

**Usage**: `/convergent-dev:4-capture-issues [project-name]`

**Example**: `/convergent-dev:4-capture-issues doc_evergreen`

---

## What This Does

Launches the `issue-capturer` agent to:

1. **Accept your feedback** - Tell the agent about bugs, issues, problems (free-form, casual)
2. **Parse into issues** - Agent identifies discrete, trackable issues
3. **Investigate systematically** - Reproduces issues, identifies root causes
4. **Create persistent tracking** - Markdown files that survive chat compaction
5. **Optional beads integration** - Creates beads issues for sprint workflow
6. **Summarize for next step** - Provides overview for convergence phase

---

## What You Get

**Issue Tracking Files** created in `ai_working/[project-name]/issues/`:

```
issues/
├── ISSUES_TRACKER.md           # Master list (GitHub/Jira style)
├── ISSUE-001-description.md    # Individual issue details
├── ISSUE-002-description.md
└── ...
```

**Each issue includes**:
- Status (Open | In Progress | Resolved)
- Priority (Critical | High | Medium | Low)
- Type (Bug | Enhancement | Feature)
- Description with reproduction steps
- Expected vs Actual behavior
- Root cause analysis
- Acceptance criteria
- Sprint assignment (once planned)
- Beads ID (if integrated)

---

## Integration with Workflow

**The convergent-dev cycle**:
```bash
1. /converge                       # New feature ideas → Feature scope
2. /plan-sprints                   # Feature scope + existing issues → Sprints
3. /tdd-cycle                      # Execute sprints with TDD
4. /capture-issues doc_evergreen   # After implementation: Capture feedback → issues (stored)
   └─→ (cycle repeats: back to step 1 - /converge for next feature scope)
```

**How issues flow through the cycle**:
- **After TDD implementation** - User tests, provides feedback, issues captured
- **Issues stored** in `ISSUES_TRACKER.md` for next iteration
- **Next convergence** (`/converge`) - Define new feature scope
  - Convergence agent reviews ISSUES_TRACKER.md
  - Critical issues may influence feature scope decisions
  - New features defined independently of issue backlog
- **Next sprint planning** (`/plan-sprints`) - Integrates feature scope + existing issues
  - Sprint planner reads ISSUES_TRACKER.md
  - Decides which issues fit naturally with planned features
  - Prioritizes critical issues that should be addressed first
  - Defers lower-priority issues to later versions
- **Cycle continues** - Implement → test → capture → **converge** → plan → implement...

**Outputs feed into**:
- `sprint-planner` - Reads ISSUES_TRACKER.md and integrates issues into sprint plans
- Your todo tracking - Clear, actionable items persisted across sessions

---

## When to Use

- After user testing reveals bugs
- When gathering feedback on a feature/tool
- Before planning the next iteration
- When you have multiple issues to track systematically

---

## Example Session

```
You: /capture-issues doc_evergreen

Agent: I'm ready to capture issues for doc_evergreen.
       What problems are you encountering?

You: When I run doc-update with empty context, it creates
     a README with an error message instead of failing cleanly.
     Also, the --sources flag doesn't seem to work with nested
     directories...

Agent: [Investigates, reproduces, creates tracking...]

Agent: ✅ Captured 2 issues:
       - ISSUE-001: Empty context creates confusing README (High priority, Bug)
       - ISSUE-002: --sources flag fails with nested directories (Medium priority, Bug)

       Created: ai_working/doc_evergreen/issues/ISSUES_TRACKER.md

       Next steps:
       - Use /converge to define new feature scope (if planning new features)
       - Use /plan-sprints to integrate these issues into sprint plans
       - Or address critical issues immediately with focused work
```

---

## Tips

- **Be casual** - Just describe what's not working
- **Include examples** - Commands you ran, output you got
- **Multiple issues OK** - Agent will parse and organize
- **Don't worry about structure** - Agent creates that

---

## After This

Once issue capture is complete:

**Recommended next step**: `/converge` - Define next feature scope
- Review captured issues may influence what you want to build next
- Critical issues may drive feature priorities
- Define new feature scope independently, then integrate issues during sprint planning

**Alternative paths**:
- Address critical issues immediately (focused work session)
- Review and prioritize issues in ISSUES_TRACKER.md
- Wait for more feedback before planning next iteration

**The cycle continues**: capture → **converge** → plan → implement → capture...

---

Launch the issue-capturer agent for {{project-name | default: "your project"}}:

I'll help you systematically capture and track issues. Please provide:
1. **Project name**: Which project/tool has issues?
2. **Your feedback**: What problems are you encountering? (Be as casual or detailed as you like)

I'll investigate each issue, create persistent tracking, and prepare a summary for the next workflow step.
