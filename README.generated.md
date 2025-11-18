# Amplifier: Metacognitive AI Development

> _"Automate complex workflows by describing how you think through them."_

> [!CAUTION]
> This project is a research demonstrator. It is in early development and may change significantly. Using permissive AI tools in your repository requires careful attention to security considerations and careful human supervision, and even then things can still go wrong. Use it with caution, and at your own risk. See [Disclaimer](#disclaimer).

## Overview

Amplifier is a coordinated and accelerated development system that turns your expertise into reusable AI tools without requiring code. Describe the step-by-step thinking process for handling a task—a "metacognitive recipe"—and Amplifier builds a tool that executes it reliably. As you create more tools, they combine and build on each other, transforming individual solutions into a compounding automation system.

## 🚀 QuickStart

### Prerequisites

<details>
<summary>Click to expand prerequisite instructions</summary>

1. Check if prerequisites are already met.

   - ```bash
     python3 --version  # Need 3.11+
     ```
   - ```bash
     uv --version       # Need any version
     ```
   - ```bash
     node --version     # Need any version
     ```
   - ```bash
     pnpm --version     # Need any version
     ```
   - ```bash
     git --version      # Need any version
     ```

2. Install what is missing.

   **Mac**

   ```bash
   brew install python3 node git pnpm uv
   ```

   **Ubuntu/Debian/WSL**

   ```bash
   # System packages
   sudo apt update && sudo apt install -y python3 python3-pip nodejs npm git

   # pnpm
   npm install -g pnpm
   pnpm setup && source ~/.bashrc

   # uv (Python package manager)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   **Windows**

   1. Install [WSL2](https://learn.microsoft.com/windows/wsl/install)
   2. Run Ubuntu commands above inside WSL

   **Manual Downloads**

   - [Python](https://python.org/downloads) (3.11 or newer)
   - [Node.js](https://nodejs.org) (any recent version)
   - [pnpm](https://pnpm.io/installation) (package manager)
   - [Git](https://git-scm.com) (any version)
   - [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)

> **Platform Note**: Development and testing has primarily been done in Windows WSL2. macOS and Linux should work but have received less testing. Your mileage may vary.

</details>

### Setup

```bash
# Clone Amplifier repository
git clone https://github.com/microsoft/amplifier.git amplifier
cd amplifier

# Install dependencies
make install

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac/WSL
# .venv\Scripts\Activate.ps1  # Windows PowerShell
```

### Get Started

```bash
# Start Claude Code
claude
```

**Create your first tool in 5 steps:**

1. **Identify a task** you want to automate (e.g., "weekly learning digest")

   Need ideas? Try This:

   ```
   /ultrathink-task I'm new to "metacognitive recipes". What are some useful
   tools I could create with Amplifier that show how recipes can self-evaluate
   and improve via feedback loops? Just brainstorm ideas, don't build them yet.
   ```

2. **Describe the thinking process** - How would an expert handle it step-by-step?

   Need help? Try This:

   ```
   /ultrathink-task This is my idea: <your idea here>. Can you help me describe the
   thinking process to handle it step-by-step?
   ```

   Example of a metacognitive recipe:

   ```markdown
   I want to create a tool called "Research Synthesizer". Goal: help me research a topic by finding sources, extracting key themes, then asking me to choose which themes to explore in depth, and finally producing a summarized report.

   Steps:

   1. Do a preliminary web research on the topic and collect notes.
   2. Extract the broad themes from the notes.
   3. Present me the list of themes and highlight the top 2-3 you recommend focusing on (with reasons).
   4. Allow me to refine or add to that theme list.
   5. Do in-depth research on the refined list of themes.
   6. Draft a report based on the deep research, ensuring the report stays within my requested length and style.
   7. Offer the draft for my review and incorporate any feedback.
   ```

3. **Generate with `/ultrathink-task`** - Let Amplifier build the tool

   ```
   /ultrathink-task <your metacognitive recipe here>
   ```

4. **Refine through feedback** - "Make connections more insightful"

   ```
   Let's see how it works. Run <your generated tool>.
   ```

   Then:

   - Observe and note issues.
   - Provide feedback in context.
   - Iterate until satisfied.

**Learn more** with [Create Your Own Tools](docs/CREATE_YOUR_OWN_TOOLS.md) - Deep dive into the process.

## Core Concepts

Amplifier is built on the principle that **expertise can be captured as thinking processes**. Instead of writing code, you describe how you mentally approach a task—the questions you ask, the criteria you use, the order of operations. Amplifier translates these "metacognitive recipes" into executable tools.

**Key concepts:**

- **Metacognitive Recipes**: Step-by-step descriptions of expert thinking processes that guide task execution
- **Tool Composition**: Tools build on each other—new tools can use existing tools as building blocks
- **Compounding Automation**: As your tool library grows, complex workflows become easier to create
- **Human-in-the-Loop**: Tools can request human feedback at decision points, combining AI capabilities with human judgment
- **Context Persistence**: Project-specific guidance stored in AGENTS.md preserves context across sessions

The system is designed for **iterative refinement**: create a basic tool, use it, observe issues, provide feedback, and improve. Each iteration makes the tool more reliable and aligned with your needs.

## Architecture

Amplifier follows a **modular, "bricks and studs" architecture** optimized for AI-assisted development:

**Core Components:**

- **Claude Code Integration**: Primary interface using Claude's AI capabilities with specialized agents
- **Specialized Agents** (`.claude/agents/`): Domain experts for development, design, knowledge synthesis, and meta-operations
- **Scenario System** (`scenarios/`): Maturity progression from experiments to production-ready tools
- **Document-Driven Development** (`/ddd:*` commands): Workflow that ensures docs and code stay synchronized
- **Git Worktrees**: Parallel development branches with isolated environments
- **MCP Servers**: External tool integration (DeepWiki for repo documentation, Context7 for library docs)

**Design Philosophy:**

- **Ruthless Simplicity**: Minimal abstractions, KISS principle, avoid future-proofing
- **Single Source of Truth**: Configuration lives in one authoritative location (`pyproject.toml`)
- **Incremental Processing**: Save progress continuously, enable interruption without data loss
- **Modular Bricks**: Self-contained components with clear contracts that can be regenerated
- **Zero-BS Principle**: No stubs or placeholders—every function must work or not exist

**Data Flow:**

1. User describes thinking process (metacognitive recipe)
2. Amplifier creates/refines tool using specialized agents
3. Tool executes with human feedback loops at decision points
4. Results saved incrementally with fixed filenames
5. Context preserved in AGENTS.md and decision records

The architecture emphasizes **composability** (tools building on tools), **observability** (transcripts and decision records), and **maintainability** (simple, direct implementations over complex abstractions).

## Usage Examples

### Create a Custom Research Tool

```bash
# Start Claude Code
claude
```

Tell Claude:

```
/ultrathink-task Create a "Tech Trend Analyzer" that:
1. Searches for recent articles on a technology topic
2. Extracts key claims and supporting evidence
3. Identifies emerging patterns and contradictions
4. Asks me which patterns to investigate deeper
5. Produces a summary report with my chosen focus areas
```

### Use Document-Driven Development

```bash
# Design a new feature
/ddd:1-plan Create a user authentication system with JWT tokens

# Generate/update documentation
/ddd:2-docs

# Review docs, iterate until approved, then plan implementation
/ddd:3-code-plan

# Implement and test
/ddd:4-code

# Finalize and clean up
/ddd:5-finish
```

### Explore with Parallel Worktrees

```bash
# Try two authentication approaches simultaneously
make worktree feature-jwt
make worktree feature-oauth

# Work in each branch independently
cd .worktrees/feature-jwt
# ... develop JWT approach

cd .worktrees/feature-oauth
# ... develop OAuth approach

# Compare and choose winner
make worktree-list
make worktree-rm feature-jwt
```

### Use Specialized Design Agents

```bash
# Start Claude Code
claude
```

Tell Claude:

```
Use the component-designer agent to create a responsive navigation menu
with mobile hamburger menu, accessibility features, and smooth transitions.
```

Or:

```
Deploy the art-director agent to establish a visual design system
for my SaaS dashboard including color palette, typography scale,
and spacing system.
```

### Restore Context After Compaction

```bash
# Claude Code auto-saves transcripts before compaction
# Restore full conversation history anytime
claude
```

In Claude:

```
/transcripts
```

## Development

### Building and Testing

```bash
# Install all dependencies
make install

# Run all quality checks (format, lint, type-check)
make check

# Run test suite
make test

# Run specific test
uv run pytest tests/path/to/test_file.py::TestClass::test_function -v

# Add new dependency (from project directory)
uv add package-name

# Add development dependency
uv add --dev package-name

# Upgrade dependency lock
make lock-upgrade

# Rebuild AI context files
make ai-context-files
```

**After making code changes, always:**

1. Run `make check` to catch syntax/linting/type errors
2. Start the affected service to catch runtime errors
3. Test basic functionality
4. Stop the service to free up ports

### Project Structure

```
amplifier/
├── .claude/                  # Claude Code configuration
│   ├── agents/              # Specialized AI agents
│   ├── commands/            # Custom slash commands
│   └── tools/               # Tool definitions and utilities
├── amplifier/               # Core Python package
│   └── __init__.py         # Package initialization
├── scenarios/               # User-created tools (experimental → production)
│   ├── README.md           # Philosophy and maturity model
│   └── blog_writer/        # Example mature tool
├── docs/                    # Documentation
│   ├── CREATE_YOUR_OWN_TOOLS.md
│   ├── document_driven_development/
│   ├── design/             # Design intelligence docs
│   ├── WORKTREE_GUIDE.md
│   └── WORKSPACE_PATTERN.md
├── tests/                   # Test suite
│   └── terminal_bench/     # Benchmarking framework
├── ai_working/              # AI workspace
│   ├── decisions/          # Architecture decision records
│   └── DISCOVERIES.md      # Problem/solution knowledge base
├── .data/                   # Runtime data (git-ignored)
│   └── transcripts/        # Conversation history exports
├── pyproject.toml          # Python project config (single source of truth)
├── ruff.toml               # Code formatter/linter config
├── Makefile                # Development commands
└── AGENTS.md               # AI assistant guidance
```

**Key directories:**

- **`.claude/`**: All Claude Code customization—agents, commands, tools
- **`scenarios/`**: Your custom tools progress from experiments to production-ready
- **`amplifier/`**: Core reusable Python package
- **`ai_working/`**: Preserves context across sessions (decisions, discoveries)
- **`.data/`**: Runtime data excluded from version control

**Configuration hierarchy:**

- `pyproject.toml` - Primary config (dependencies, tool settings)
- `ruff.toml` - Formatting/linting rules
- `.vscode/settings.json` - IDE settings that reference project config
- `AGENTS.md` - AI behavioral guidance

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## License

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general). Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.

## Disclaimer

> [!IMPORTANT]
> **This is an experimental system. _We break things frequently_.**

- Not accepting contributions yet (but we plan to!)
- No stability guarantees
- Pin commits if you need consistency
- This is a learning resource, not production software
- **No support provided** - See [SUPPORT.md](SUPPORT.md)

**Use this project at your own risk.** Amplifier is a research demonstrator in early development. Using permissive AI tools in your repository requires careful attention to security considerations and human supervision. Even with precautions, unexpected issues can occur.