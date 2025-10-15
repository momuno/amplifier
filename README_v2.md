# Amplifier

**AI-augmented development environment that transforms how you build software.**

> [!CAUTION]
> This project is a research demonstrator in early development. Using permissive AI tools requires careful security attention and human supervision. Use at your own risk.

---

## What Is Amplifier?

Amplifier gives you instant access to 27 specialized AI agents, session-transcending memory, multi-perspective knowledge synthesis, and natural language workflows—all in a containerized environment that deploys in seconds.

Instead of starting from scratch every session, you get:
- **27 Specialized Agents** - zen-architect, bug-hunter, security-guardian, and more
- **Knowledge Graph** - Extract patterns from YOUR content, query YOUR domain expertise
- **Session Memory** - AI "remembers" decisions, preferences, patterns across sessions
- **Parallel Worktrees** - Try 3 approaches simultaneously with shared intelligence
- **Natural Language Tools** - Describe thinking processes, get working implementations

---

## 🚀 Quickstart

```bash
# 1. Clone and setup
git clone https://github.com/microsoft/amplifier.git
cd amplifier
make install

# 2. Activate environment
source .venv/bin/activate  # Linux/Mac/WSL

# 3. Try your first demo (takes ~2 minutes)
make blog-write-example
```

**That's it.** You now have a complete AI development environment.

For detailed setup including external data directories and cloud sync, see our [Full Installation Guide](docs/INSTALLATION.md).

---

## 🎯 What to Do Next: 5-Minute Demos

Try these hands-on demos to see Amplifier's power. Each shows something you couldn't easily do before—or takes hours without Amplifier.

### Demo 1: Write a Blog Post (In Your Voice)

**The Problem**: You have ideas, but writing takes hours. AI-generated content doesn't sound like you.

```bash
# Uses YOUR existing writing to learn YOUR voice
make blog-write \
  IDEA=scenarios/blog_writer/tests/sample_brain_dump.md \
  WRITINGS=scenarios/blog_writer/tests/sample_writings/
```

**What happens**: Multi-stage pipeline analyzes your writing style, drafts content matching your voice, reviews for accuracy, iterates with your feedback. Complete with state management—interrupt and resume anytime.

**The reveal**: This entire tool came from describing the thinking process in one conversation. [See how it was built →](scenarios/blog_writer/HOW_TO_CREATE_YOUR_OWN.md)

**Why it matters**: This is a 5-stage AI pipeline built from natural language. No complex code, no brittle prompts. Just describe how you think about the problem.

---

### Demo 2: Build Your Knowledge Graph

**The Problem**: Valuable knowledge scattered across files, articles, notes. Hard to query. Connections invisible.

```bash
# Extract patterns from YOUR content
make knowledge-sync

# Query what you know
make knowledge-query Q="What patterns do we use for error handling?"

# Visualize connections
make knowledge-graph-viz
```

**What happens**: 6 specialized agents analyze your content from different perspectives, extract concepts and relationships, build a queryable graph, and **preserve disagreements as valuable signal** (not forcing false consensus).

**The difference**: Open the generated `graph.html`. You'll see connections you didn't explicitly document—**emergent insights from your own knowledge**.

**Why it matters**: Your knowledge accumulates across sessions. Generic Claude becomes YOUR specialized expert by learning YOUR domain patterns, YOUR architectural decisions, YOUR preferences.

---

### Demo 3: Parallel Experimentation (3 Approaches at Once)

**The Problem**: You want to try multiple approaches but context-switching kills productivity. Serial exploration is slow.

```bash
# Create three parallel worktrees
make worktree approach-redis
make worktree approach-postgres
make worktree approach-sqlite

# Each shares the same knowledge base and memory
# Develop simultaneously, compare results, keep the winner
```

**What happens**: Git worktrees give isolated code branches that all share the central knowledge graph, memory system, and discoveries. Insights from one approach instantly available to others.

**The contrast**: Without Amplifier:
- 3 separate environments to manage
- 3 dependency sets to maintain
- 3 contexts to track
- Hours of setup

With Amplifier: **One command per approach. Shared intelligence. Parallel progress.**

**Why it matters**: Transforms "I can only focus on one thing" (psychological constraint) into "I'm running 3 experiments simultaneously" (technical capability).

---

### Demo 4: Illustrate an Article (Automatically)

**The Problem**: Finding contextually relevant images for technical content takes forever. Stock photos rarely fit.

```bash
make illustrate INPUT=your_article.md
```

**What happens**: Reads your article, identifies where images add value, generates contextually relevant prompts, creates images via AI APIs, inserts them at optimal positions with proper formatting.

**Try the comparison**:
1. Time yourself illustrating an article manually (find/create images, resize, caption, insert)
2. Run `make illustrate INPUT=article.md`
3. Compare: **Hours vs. minutes**

**Why it matters**: "Describe thinking, get tools" in action. Built by describing: "Analyze content, identify illustration points, create prompts, generate images, integrate them." That description became a production tool.

---

### Demo 5: Synthesize Repository Insights

**The Problem**: Understanding a new codebase takes days. Architectural decisions invisible. Patterns scattered.

```bash
make repo-synthesize \
  TOPIC="What enlightening experiences does this repo provide?"
```

**What happens**: Hierarchical analysis (file → directory → repository) with custom research questions, multi-agent synthesis, pattern detection. Generates comprehensive documentation revealing architectural insights and novel capabilities.

**The validation**: The `repository_synthesis_original.md` file you can read in this repo? Generated by this tool analyzing **itself**. Recursive self-application proves it works at scale.

**The artifact**: A document that would take weeks to write manually, capturing insights that live in code structure, not comments.

---

## 💡 Why Amplifier

If those demos resonated, you already get it. Here's the deeper story:

### 1. Philosophy-as-Code
Load organizational values (`CLAUDE.md`, `AGENTS.md`) via `/prime` command. They become runtime dependencies shaping every AI interaction. **Alignment is a setup step, not ongoing persuasion.**

### 2. Session-Transcending Memory
Every session extracts learnings (decisions, preferences, patterns). Future sessions retrieve relevant context automatically. **AI "remembers" your project without you re-teaching it.**

### 3. Multi-Perspective Knowledge Synthesis
6 agents extract different viewpoints, preserve disagreements, detect productive tensions. **Insights live in conflicts between perspectives, not just consensus.**

### 4. Natural Language Orchestration
`/modular-build Build a module that...` → complete, tested, secure module. **Describe what you want, get working implementations.**

### 5. Observable Collaboration
Transcripts reconstruct conversations. Event logs show pipeline activity. Memory extraction captures learnings. **You can't improve what you can't see—so everything is visible.**

### 6. Brick-and-Stud Modularity
Small modules (~150 lines) with explicit contracts enable **regenerate-from-spec instead of edit-code**. Leverage AI's strength (clean-slate generation), avoid its weakness (complex patches).

---

## 🧠 The Core Insight

**AI collaboration quality is a context problem, not a capability problem.**

Generic Claude becomes specialized expert through:
- **Domain knowledge** (what we know)
- **Conversational memory** (what we learned together)
- **Philosophical principles** (how to think)
- **Methodological patterns** (how to approach problems)

Not through better prompts or more powerful models.

**You're no longer limited by "can I build this?" but by "which of these abundant possibilities matters most?"**

---

## 📖 Using Amplifier

### Basic Usage

```bash
cd amplifier
claude  # Everything pre-configured and ready
```

### With Your Own Projects

```bash
# 1. Start Claude with both directories
claude --add-dir /path/to/your/project

# 2. Tell Claude where to work (first message)
I'm working in /path/to/your/project which doesn't have Amplifier files.
Please cd to that directory and work there.
Do NOT update any issues or PRs in the Amplifier repo.

# 3. Use Amplifier's agents on your code
"Use the zen-architect agent to design my application's caching layer"
"Deploy bug-hunter to find why my login system is failing"
```

### Development Commands

```bash
make check               # Format, lint, type-check
make test                # Run tests
make knowledge-update    # Build knowledge graph
make transcript-list     # View conversation history
make worktree NAME       # Create parallel experiment
```

---

## 🎨 Creating Your Own Tools

**You don't need to be a programmer.** Amplifier can build tools from descriptions.

### Find Ideas

Ask Amplifier to brainstorm:

```
/ultrathink-task I'm new to "metacognitive recipes" - what tools could you create
that I might find useful? Don't create them, just give me ideas.
```

This generates ideas like:
- Documentation Quality Amplifier
- Research Synthesis Quality Escalator
- Code Quality Evolution Engine
- Self-Debugging Error Recovery

### Create Your Tool

1. **Describe your goal** - What problem are you solving?
2. **Describe the thinking process** - How should the tool approach it?
3. **Let Amplifier build it** - Use `/ultrathink-task` to create
4. **Iterate to refine** - Provide feedback as you use it
5. **Share it back** - Contribute to `scenarios/`

**Example**: The blog writer was created by describing:
- Goal: Write blog posts in my style
- Process: Extract style → draft → review sources → review style → get feedback → refine

No code written by user. Just: description → Amplifier builds → feedback → refinement.

[See detailed guide →](scenarios/blog_writer/HOW_TO_CREATE_YOUR_OWN.md)

---

## 📚 More Tools to Try

Explore the [scenarios/](scenarios/) directory for more examples:

- **[tips-synthesizer](scenarios/tips_synthesizer/)** - Transform scattered tips into comprehensive guides
- **[transcribe](scenarios/transcribe/)** - Transcribe audio/video with AI-enhanced summaries
- **[web-to-md](scenarios/web_to_md/)** - Convert web pages to markdown
- **[repo-synthesizer](scenarios/repo_synthesizer/)** - Analyze codebases for insights

Each tool includes:
- `README.md` - How to use it
- `HOW_TO_CREATE_YOUR_OWN.md` - How it was built
- Working examples to try

---

## 🔮 Vision

We're building toward a future where:

1. **You describe, AI builds** - Natural language to working systems
2. **Parallel exploration** - Test 10 approaches simultaneously
3. **Knowledge compounds** - Every project makes you more effective
4. **AI handles tedious** - You focus on creative decisions

See [AMPLIFIER_VISION.md](AMPLIFIER_VISION.md) for the full vision.

---

## 📖 Documentation

- **[This Is The Way](docs/THIS_IS_THE_WAY.md)** - Best practices and strategies
- **[Worktree Guide](docs/WORKTREE_GUIDE.md)** - Parallel development workflows
- **[Modular Builder](docs/MODULAR_BUILDER_LITE.md)** - Natural language to modules
- **[Implementation Philosophy](ai_context/IMPLEMENTATION_PHILOSOPHY.md)** - How we build
- **[Agents Catalog](.claude/AGENTS_CATALOG.md)** - All 27 specialized agents

---

## 🤝 Contributing

> [!NOTE]
> Not currently accepting external contributions, but actively working toward opening this up. Feel free to fork and experiment!

Most contributions require agreeing to a Contributor License Agreement (CLA). Visit [Contributor License Agreements](https://cla.opensource.microsoft.com) for details.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).

---

## ⚠️ Current Limitations

- Knowledge extraction works best in Claude environment
- Processing time: ~10-30 seconds per document
- Memory system still in development
- **No support provided** - See [SUPPORT.md](SUPPORT.md)

> [!IMPORTANT]
> This is experimental. We break things frequently. Pin commits if you need consistency.

---

_"The best AI system isn't the smartest—it's the one that makes YOU most effective."_

---

## Legal

**Trademarks**: This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
