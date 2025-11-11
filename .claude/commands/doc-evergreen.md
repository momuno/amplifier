---
description: Generate or regenerate documentation using doc-evergreen tool
category: documentation
allowed-tools: Bash, Read, Glob, AskUserQuestion
---

# doc-evergreen - Documentation Generation Tool

@scenarios/doc_evergreen/AI_ASSISTANT_WORKFLOW.md

---

## Your Task

Help the user use the doc-evergreen tool effectively by:

1. **Reading the AI_ASSISTANT_WORKFLOW.md** (already loaded above) to understand:
   - How the tool works (LLM-guided file discovery)
   - Prerequisites (working directory, API key)
   - Available commands (create, regenerate)
   - Best practices

2. **Understanding what the user wants**:
   - Do they want to **create** new documentation?
   - Do they want to **regenerate** existing documentation?
   - Are they asking for help understanding the tool?

3. **Following the workflow guide** to:
   - Ask the right clarifying questions
   - Gather necessary information (about, output path)
   - Run the appropriate `make doc-create` or `make doc-regenerate` command
   - Explain what's happening and what to expect

---

## Quick Reference

**Creating new documentation**:
```bash
make doc-create ABOUT="description" OUTPUT=path
```

**Regenerating existing documentation**:
```bash
make doc-regenerate DOC=path  # Single doc
make doc-regenerate ALL=true  # All docs
```

**Key Points**:
- Uses LLM-guided discovery by default (finds relevant files intelligently)
- Creates `.doc-evergreen/` directory at repository root
- Takes 30-60 seconds per document
- Shows full LLM reasoning for transparency

---

## Additional Guidance

$ARGUMENTS
