# Amplifier

A research-stage development environment that supercharges AI coding assistants with specialized knowledge, proven workflows, and automation tools. Amplifier transforms a basic AI assistant into a force multiplier capable of delivering complex solutions with minimal hand-holding.

> **[!CAUTION]**
> This is experimental research software. Use it with caution and at your own risk. Expect rapid changes, rough edges, and no guarantees.

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for installation and setup.

## What to Do Next: 5-Minute Demos

After setup, try these hands-on experiences to see what Amplifier can do. Each takes under 5 minutes and demonstrates real capability you can use immediately.

### Demo 1: Build a Complete Tool from Natural Language

**What you'll experience:** Describe a tool in plain English, get working code with tests and documentation.

```bash
# Start Claude in your Amplifier directory
claude
```

Then:
```
/modular-build Build a tool that reads markdown files from a directory,
extracts all code blocks, and saves them as separate files organized by language
```

**What just happened:** Multiple specialized agents coordinated automatically:
- `module-intent-architect` - Understood your description and created specifications
- `contract-spec-author` - Defined formal contracts
- `zen-architect` - Designed the clean architecture
- `modular-builder` - Generated the implementation
- `test-coverage` - Added comprehensive tests
- `security-guardian` - Reviewed for vulnerabilities

**Compare without Amplifier:** You'd manually write the parser, handle edge cases, write tests, consider security implications - taking 30+ minutes minimum. With Amplifier: one sentence → working tool.

### Demo 2: Knowledge That Compounds - Query Your Project Intelligence

**What you'll experience:** Your documentation, decisions, and patterns become queryable expertise.

```bash
# First, add some content to learn from
cp your-docs/*.md .data/content/

# Extract knowledge
make knowledge-update

# Now query it like talking to someone who read all your docs
make knowledge-query Q="What error handling patterns do we use?"
make knowledge-query Q="Why did we choose FastAPI?"
```

Then start Claude and ask:
```
Build an API endpoint that follows our established patterns
```

**What just happened:** Claude automatically referenced YOUR project's patterns, YOUR decisions, YOUR style. It's not generic AI anymore - it's specialized in your codebase.

**Compare without Amplifier:** You repeatedly explain the same patterns, correct the same mistakes, watch the AI forget everything between sessions. With Amplifier: explain once, it remembers forever.

### Demo 3: Parallel Exploration - Try Three Approaches at Once

**What you'll experience:** Experiment with multiple solutions simultaneously, all learning from shared knowledge.

```bash
# Create three parallel experiments
make worktree approach-simple
make worktree approach-pydantic
make worktree approach-dataclasses

# Work in each one independently
cd ../approach-simple
claude
# Ask: "Implement data validation with clear error messages"

# Switch to another approach
cd ../approach-pydantic
claude
# Ask: "Implement data validation with Pydantic models"

# Each has isolated code but shares your knowledge base
```

**What just happened:** All three approaches learn from your shared knowledge and memory. They don't interfere with each other. You can compare results and keep the winner - or merge ideas from multiple approaches.

**Compare without Amplifier:** You'd build one approach, commit to it, discover limitations later. Sequential work means you rarely explore alternatives. With Amplifier: parallel exploration is the norm.

### Demo 4: Memory That Persists - Development That Compounds

**What you'll experience:** Amplifier remembers your preferences and decisions across sessions.

**Day 1 - Morning:**
```bash
claude
> "I prefer explicit error handling with custom exception classes"
> [Work on authentication feature]
```

**Day 1 - Afternoon (new session):**
```bash
claude
> "Build a new data validation module"
```

**What just happened:** Without you repeating yourself, Claude used custom exception classes because it remembered from your morning session. Each session makes future sessions smarter.

**Compare without Amplifier:** Every session starts from zero. You repeat yourself constantly. With Amplifier: context accumulates, work compounds.

### Demo 5: Metacognitive Recipes - Describe Thinking, Get Tools

**What you'll experience:** Describe HOW you think through a problem, get a working tool that embodies that thinking.

```bash
# Explore an existing recipe
cat scenarios/blog_writer/README.md
```

Then try creating your own:
```
/ultrathink-task I want to create a tool that:
1. First reads my existing code and extracts patterns
2. Then generates new code following those patterns
3. Then validates the new code matches the style
4. Finally suggests improvements
```

**What just happened:** You described your cognitive process - not code. Amplifier built a tool that thinks the way you described. The tool can now be reused, improved, shared.

**Compare without Amplifier:** You'd write custom scripts for pattern extraction, generation, validation - taking hours or days. With Amplifier: describe the thinking, get the tool.

### Demo 6: Fearless Refactoring with Orchestrated Agents

**What you'll experience:** Request major architectural changes and watch them happen systematically.

```
/ultrathink-task Refactor the authentication system to support multiple providers
(JWT, OAuth, API keys) through a plugin architecture. Maintain all existing
functionality and ensure tests pass.
```

**What just happened:** Amplifier orchestrated multiple specialists:
- `zen-architect` - Designed the plugin architecture
- `modular-builder` - Implemented the changes
- `test-coverage` - Verified all tests still pass
- `security-guardian` - Reviewed the security implications
- `refactor-architect` - Ensured clean migration path

**Compare without Amplifier:** Major refactoring is risky and time-consuming. You might abandon it halfway through when complexity overwhelms you. With Amplifier: ambitious refactoring becomes feasible.

## Why Amplifier?

The demos above show Amplifier in action. Here's what they demonstrate:

### The Core Problem Amplifier Solves

Modern AI assistants suffer from three fundamental limitations:
1. **Amnesia** - They forget everything between sessions
2. **Generic** - They lack expertise in YOUR domain and patterns
3. **Sequential** - They work on one thing at a time while you have many ideas

You have more ideas than time to implement them. That's the real bottleneck.

### The Amplifier Approach

**Not a better model - a better environment around the model.** Think of it like the difference between a construction worker with hand tools versus one with a full workshop, specialized equipment, and a trained team.

Amplifier provides:

- **27+ Specialized Agents** - Architecture, security, testing, debugging, knowledge synthesis experts
- **Persistent Memory** - Remembers decisions, preferences, patterns across sessions
- **Knowledge Synthesis** - Extracts and queries insights from YOUR documentation
- **Parallel Workflows** - Multiple worktrees with shared intelligence
- **Metacognitive Recipes** - Proven thinking patterns encoded as reusable tools
- **Philosophy as Code** - Load organizational principles that shape every AI interaction

### What You Gain

**Velocity:** Build in hours what took days. Ideas → working code dramatically faster.

**Exploration:** Try 10 approaches where you'd normally try 1-2. Keep the best, learn from all.

**Compounding:** Each session strengthens future sessions. Month 3 is exponentially better than month 1.

**Quality:** Infrastructure enforces best practices automatically (linting, type checking, testing, security).

**Confidence:** Tackle ambitious projects knowing specialized agents handle details while you provide vision.

### Real-World Impact

- **Parallel exploration** - Routinely try 5-10 architectural approaches simultaneously
- **Knowledge that compounds** - Extract patterns from docs, query them like a senior engineer
- **Disciplined AI behavior** - Plan-first thinking, tests, quality gates, recovery tactics
- **Tools that build tools** - Many Amplifier features were built using Amplifier itself

## What Amplifier Is Not

Be honest with yourself about expectations:

- **Not a Microsoft product** - Research demonstrator, changes rapidly
- **Not plug-and-play** - Requires CLI comfort, environment setup, API costs
- **Not stable** - Breaking changes happen as we learn and improve
- **Not free to run** - Intensive AI usage means real API costs (tracked in real-time)
- **Not for everyone** - If you want guaranteed stability, wait for v1.0

## Who Should Try Amplifier

**You'll thrive if you:**
- Have more ideas than time to implement them
- Enjoy decomposing problems and building systems
- Want to explore multiple approaches, not just one
- Are comfortable with experimental tools and rough edges
- See coding as collaborative dialog with AI

**Skip it if you:**
- Want point-and-click simplicity
- Need guaranteed stability for production work
- Prefer writing every line of code yourself
- Aren't comfortable with command-line tools

## Learn More

### Documentation

- **[AMPLIFIER_VISION.md](AMPLIFIER_VISION.md)** - Philosophy and long-term vision
- **[docs/THIS_IS_THE_WAY.md](docs/THIS_IS_THE_WAY.md)** - Battle-tested strategies from real usage
- **[ai_context/MODULAR_DESIGN_PHILOSOPHY.md](ai_context/MODULAR_DESIGN_PHILOSOPHY.md)** - Bricks and studs architecture approach
- **[docs/WORKTREE_GUIDE.md](docs/WORKTREE_GUIDE.md)** - Advanced parallel development workflows

### Explore Real Examples

The **[scenarios/](scenarios/)** directory contains real, working tools built with Amplifier. Each includes "how it was created" documentation - these are your templates:

- **blog_writer** - Analyze writing style from examples, draft matching content
- **web_to_md** - Convert web pages to organized markdown with images
- **transcribe** - Audio → segments → transcripts → synthesis with speaker detection
- **tips_synthesizer** - Extract and synthesize patterns from scattered notes

Study these to understand the "describe thinking, get tools" pattern.

### Key Features Detail

**Specialized Agents** (see `.claude/AGENTS_CATALOG.md`):
- Core: `zen-architect`, `modular-builder`, `bug-hunter`, `test-coverage`
- Analysis: `security-guardian`, `performance-optimizer`, `database-architect`
- Knowledge: `insight-synthesizer`, `knowledge-archaeologist`, `concept-extractor`
- Meta: `subagent-architect` (creates new specialized agents)

**Knowledge Base:**
```bash
make knowledge-update    # Extract from your content
make knowledge-query Q="your question"
make knowledge-graph-viz # Visualize connections
```

**Transcripts:**
```bash
make transcript-list     # See all conversations
make transcript-search TERM="auth"  # Search past work
/transcripts            # Restore full conversation in Claude
```

**Development:**
```bash
make check              # Format, lint, type-check
make test               # Run all tests
make worktree name      # Create parallel workspace
```

## Community & Next Steps

### Where We're Going

**Near term:** Multi-provider support (not locked to Claude), unified event logs, swappable orchestrators.

**Long term:** Kernel-inspired architecture - small stable core with everything else as swappable modules. Think Linux kernel for AI development environments.

See [ROADMAP.md](ROADMAP.md) for details.

### Join the Exploration

This is a collective learning journey. We're sharing openly so you can:
- Fork and build your own amplifier
- Learn from our patterns and mistakes
- Share discoveries that help everyone
- Push the boundaries of AI-assisted development

**Related Work:** See ["Superpowers: How I'm using coding agents"](https://blog.fsck.com/2025/10/09/superpowers/) for complementary approaches and community insights.

### Contributing

> [!NOTE]
> Not currently accepting external contributions (rapid iteration means things break). We plan to open this up once the architecture stabilizes. Meanwhile, fork and experiment!

For questions: GitHub Issues
For bugs: GitHub Issues
For patterns: GitHub Discussions

## The Meta-Insight

Effective AI collaboration isn't about better models - it's about better environments.

Comprehensive context (philosophy, domain knowledge, memory, methodological patterns) transforms generic AI into specialized expert. The future isn't "AI writes all code" but "humans provide vision while AI handles velocity" in an environment that accumulates wisdom and compounds capability.

**You're no longer limited by "can I build this?" but by "which of these abundant possibilities matters most?"**

---

## License & Disclaimer

MIT License - See [LICENSE](LICENSE)

This is experimental research software provided as-is with no guarantees or official support. Use at your own risk. Expect breaking changes as the project evolves.

**Platform Note:** Primary development on WSL2. macOS/Linux less tested.

See [SUPPORT.md](SUPPORT.md) for support policy (spoiler: there isn't one - this is research).

---

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.

## Contributing

Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to grant us the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com).
