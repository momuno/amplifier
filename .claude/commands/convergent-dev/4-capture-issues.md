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

**Full workflow**:
```bash
/capture-issues doc_evergreen  # Capture feedback → issues
/converge                       # Review issues → MVP scope
/plan-sprints                   # MVP → executable sprints
/tdd-cycle                      # Execute sprints with TDD
```

**Outputs feed into**:
- `convergence-architect` - Uses ISSUES_TRACKER.md to scope MVP
- `sprint-planner` - Assigns issues to sprints
- Your todo tracking - Clear, actionable items

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

       Ready for /converge to scope MVP from these issues.
```

---

## Tips

- **Be casual** - Just describe what's not working
- **Include examples** - Commands you ran, output you got
- **Multiple issues OK** - Agent will parse and organize
- **Don't worry about structure** - Agent creates that

---

Launch the issue-capturer agent for {{project-name | default: "your project"}}:

I'll help you systematically capture and track issues. Please provide:
1. **Project name**: Which project/tool has issues?
2. **Your feedback**: What problems are you encountering? (Be as casual or detailed as you like)

I'll investigate each issue, create persistent tracking, and prepare a summary for the next workflow step.
