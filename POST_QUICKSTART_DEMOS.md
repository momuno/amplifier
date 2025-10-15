# Post-Quickstart Demos: Experience Amplifier's Power

This guide provides quick (<5 minute) hands-on demos to experience Amplifier's capabilities after completing the quickstart. Each demo solves a real problem and demonstrates immediate value.

---

## Quick Demos

### Demo A: "From Scattered Notes to Knowledge Graph" ⭐ **BEST FOR RECORDING**

**What you do:**
```bash
# Drop 3-5 markdown files into a folder (your project docs, meeting notes, etc.)
make knowledge-sync
make knowledge-query Q="What patterns do we use for error handling?"
```

**What you see:**
- Multi-agent system processes your content (6 specialized agents working in parallel)
- Returns answers sourced from YOUR documentation, not generic AI knowledge
- Shows the "AI that knows your domain" capability instantly

**Why this resonates:**
- Solves real problem: "AI doesn't understand my project"
- Visible AI orchestration (multiple agents working together)
- Immediate practical value (queryable project knowledge)
- Shows compounding value (knowledge persists across sessions)

---

### Demo B: "Describe It, Build It" - Natural Language Module Generation

**What you do:**
```bash
/modular-build Build a module that reads JSON config files and validates them against a schema
```

**What you see:**
- 5-phase pipeline activates (Ask→Bootstrap→Plan→Generate→Review)
- 6 specialized agents coordinate automatically
- Complete, tested, documented module appears in minutes
- Code includes contracts, error handling, security checks

**Why this resonates:**
- "I have more ideas than time" → solved
- Shows orchestration over implementation
- Production-quality code, not toy examples
- Non-programmers could describe and get working code

---

### Demo C: "Parallel Exploration" - Try 3 Approaches Simultaneously

**What you do:**
```bash
# Create 3 parallel experiments
make worktree approach-redis
make worktree approach-sqlite
make worktree approach-inmemory

# Each worktree gets same task, different approach
# All share the knowledge base, but code stays isolated
```

**What you see:**
- Three isolated development branches created instantly
- Work on all three simultaneously with AI assistance
- Compare results, keep the winner
- All three learn from shared knowledge base

**Why this resonates:**
- Removes experimentation constraints (psychological → technical)
- "What if we tried it three different ways?" becomes normal
- Shows how Amplifier changes development workflow fundamentally
- Demonstrates shared intelligence across isolated code

---

### Demo D: "Never Lose Context" - Transcript Recovery

**What you do:**
```bash
# Have a long coding session with Claude
# Let context window get compacted (lose details)
/transcripts
# Or manually: make transcript-export
```

**What you see:**
- Full conversation history restored, including compacted parts
- Every decision, every iteration preserved
- Can search transcripts to recall "why did we choose X?"
- Shows before/after: what Claude "forgot" vs what's actually preserved

**Why this resonates:**
- Solves frustrating "AI forgot our conversation" problem
- Makes AI collaboration observable and learnable
- Enables data-driven improvement of prompts/workflows
- "You can't improve what you can't see" → now you can see

---

### Demo E: Compare/Contrast - "With vs Without Amplifier"

**What you do:**

**WITHOUT Amplifier:**
1. Ask Claude: "Build me an authentication system"
2. Watch it generate generic code
3. Ask "Use our team's patterns" → doesn't know them
4. Next session: start from scratch again

**WITH Amplifier:**
1. `/prime` (loads team philosophy, patterns, decisions)
2. Ask Claude: "Build me an authentication system"
3. Watch it reference YOUR documented patterns automatically
4. Uses zen-architect, security-guardian agents
5. Next session: remembers previous decisions via memory system

**Why this resonates:**
- Direct comparison makes value instantly obvious
- Shows all key capabilities: philosophy-as-code, agents, memory, knowledge
- Addresses "why not just use Claude directly?" question
- Demonstrates "generic AI → specialized expert" transformation

---

## Why Amplifier: The Lightbulb Moments

### "I have more ideas than time to try them."
This is the core problem Amplifier solves. Most developers are limited not by imagination but by execution capacity. Amplifier flips this: natural language orchestration, parallel exploration, and specialized agents transform the constraint from "can I build this?" to "which of these abundant possibilities matters most?"

### "Every AI session starts from zero."
Without Amplifier, you re-teach context every time. With it, philosophy loads automatically (`/prime`), the knowledge graph remembers your domain patterns, memory recalls past decisions, and transcripts preserve everything. Month 3 of development is dramatically more effective than Month 1 because the system compounds wisdom.

### "AI doesn't understand my domain."
Generic Claude becomes specialized expert through environmental design, not model improvements. Feed your documentation to knowledge synthesis (`make knowledge-sync`), and suddenly AI cites YOUR patterns, YOUR decisions, YOUR architectural choices automatically.

### "I can only try one approach at a time."
Amplifier's parallel worktrees enable "try 3 approaches simultaneously, compare results, keep winner" workflow. Experimentation becomes standard practice rather than exceptional effort. The constraint was psychological, not technical.

### "AI collaboration is a black box."
Transcripts capture full conversations before compaction. Event logs show real-time pipeline operations. Memory extraction reveals what AI learned. Agent delegation becomes visible. You can't improve what you can't see—Amplifier makes invisible processes observable and learnable.

### "AI-generated code doesn't match our standards."
Philosophy-as-code treats alignment as setup step, not ongoing persuasion. Load `CLAUDE.md`, `AGENTS.md` via `/prime` and principles like "ruthless simplicity" shape every AI action automatically. Infrastructure (ruff, pyright, zero-BS principle) ensures AI output is indistinguishable from human code at quality level.

### "Sophisticated AI environments take hours to configure."
`./amplify.sh /your/project` deploys complete AI-augmented development OS (27 specialized agents, hooks, philosophy, validation tools, knowledge synthesis) instantly in Docker. "Try this on your project" becomes frictionless.

---

## Recording Recommendation

**Record Demo A: "From Scattered Notes to Knowledge Graph"**

**Why this one:**
1. **Visually compelling** - Watch multiple agents process files in real-time
2. **Universally relatable** - Everyone has scattered project docs
3. **Immediate wow factor** - Ask question, get answer from YOUR content
4. **Shows core differentiation** - "AI that knows my domain" in 3 minutes
5. **Natural narrative arc** - Problem (scattered knowledge) → Process (synthesis) → Solution (queryable wisdom)
6. **Sets up other capabilities** - Once they see this, parallel exploration and module building make sense

**Recording flow (~3-4 minutes):**
- 0:00-0:30: Show folder with 3-5 markdown files, quickly scan one
- 0:30-2:00: Run `make knowledge-sync`, watch agent pipeline with voiceover
- 2:00-2:30: Run `make knowledge-query Q="..."`
- 2:30-3:30: Show result sourced from your docs, query 2-3 more questions
- 3:30-4:00: Explain: "This knowledge persists. Every session gets smarter."

This demo viscerally demonstrates the shift from "AI as tool" to "AI as environment" that is Amplifier's core insight.
