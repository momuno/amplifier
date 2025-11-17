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

Amplifier transforms how you work with AI by making expertise reusable and composable. At its heart are three key concepts:

**Metacognitive Recipes** - These are step-by-step descriptions of how an expert thinks through a task. Instead of writing code, you describe the thinking process: "First analyze the problem, then consider alternatives, evaluate trade-offs, make a decision, and finally validate the approach." Amplifier turns these thinking patterns into executable tools.

**Tool Composition** - As you create tools, they become building blocks for more sophisticated automation. A "Research Synthesizer" might use a "Web Scraper" tool, which uses a "Content Extractor" tool. Each tool focuses on one thing, but they combine to handle complex workflows.

**Compounding Intelligence** - Every tool you create makes the next one easier to build. Your library of specialized tools grows into a personalized automation system that understands your domain, your preferences, and your way of working. The system gets smarter as you use it.

## Architecture

Amplifier is built on a modular architecture that emphasizes simplicity and extensibility:

**Core Components:**

- **Scenario System** (`scenarios/`) - Contains user-created tools organized by domain (blog writing, research, design). Each scenario is self-contained with its own prompts, logic, and documentation.

- **Agent Framework** (`.claude/agents/`) - Specialized AI agents for different tasks (architecture review, bug hunting, security analysis, design). Agents provide focused expertise and can be invoked by scenarios or used directly.

- **Workflow Orchestration** - Document-Driven Development (DDD) commands that guide feature development from planning through implementation with built-in checkpoints and rollback capabilities.

- **Development Tools** - Git worktree management for parallel development, transcript preservation across compaction events, enhanced status line for cost/time tracking, and automated context file generation.

**Key Design Principles:**

- **Ruthless Simplicity** - Minimal abstractions, start simple and grow as needed, question all complexity
- **Modular "Bricks & Studs"** - Self-contained modules with clear contracts that can be regenerated rather than patched
- **Single Source of Truth** - Configuration lives in one authoritative location (typically `pyproject.toml`)
- **Vertical Slices** - Complete end-to-end functionality before horizontal feature expansion

**Technology Stack:**

- Python 3.11+ with modern async patterns
- `uv` for fast, reliable dependency management
- Pydantic for data validation and settings
- Claude Code SDK for AI interactions
- MCP (Model Context Protocol) for service communication

## Usage Examples

### Creating a Custom Tool

```bash
# Describe what you want in natural language
/ultrathink-task Create a "Code Review Assistant" that:
1. Reads a git diff
2. Checks for common issues (security, performance, style)
3. Suggests improvements with examples
4. Prioritizes feedback by severity
```

### Using Specialized Agents

```bash
# Architecture review
Use zen-architect to design a caching layer for the API

# Security analysis
Deploy security-guardian to review authentication implementation

# Bug investigation
Have bug-hunter investigate why login fails intermittently
```

### Document-Driven Development Workflow

```bash
# Complete feature development cycle
/ddd:1-plan         # Design the feature architecture
/ddd:2-docs         # Generate and refine documentation
/ddd:3-code-plan    # Plan implementation approach
/ddd:4-code         # Implement with tests
/ddd:5-finish       # Clean up and finalize

# Each phase creates artifacts the next consumes
# You control git operations with explicit approval
```

### Parallel Development with Worktrees

```bash
# Experiment with different approaches simultaneously
make worktree feature-redis    # Try Redis for caching
make worktree feature-memcache # Try Memcache in parallel

# Compare implementations
make worktree-list             # See all active experiments

# Keep the winner
make worktree-rm feature-redis # Remove the approach you don't want
```

### Design Intelligence

```bash
# Create UI components with design system alignment
/designer create a button component with hover states and accessibility

# Establish visual direction
Use art-director to define the visual language for my dashboard

# Design system architecture
Deploy design-system-architect to plan our component library structure
```

## Development

### Building and Testing

```bash
# Install dependencies
make install

# Run all quality checks (format, lint, type-check)
make check

# Run test suite
make test

# Run specific test
uv run pytest tests/path/to/test_file.py::test_function -v

# Upgrade dependencies
make lock-upgrade

# Rebuild AI context files
make ai-context-files
```

**Adding Dependencies:**

```bash
# Navigate to project directory
cd amplifier  # or your project subdirectory

# Add runtime dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

**Testing Philosophy:**
- 60% unit tests for logic validation
- 30% integration tests for component interaction
- 10% end-to-end tests for critical user journeys
- Emphasize manual testability as a design goal

### Project Structure

```
amplifier/
├── .claude/                    # Claude Code configuration
│   ├── agents/                 # Specialized AI agents
│   ├── commands/               # Custom slash commands
│   └── tools/                  # Development utilities
├── amplifier/                  # Core Python package
│   └── __init__.py
├── scenarios/                  # User-created tools
│   ├── blog_writer/           # Example: blog writing automation
│   └── README.md              # Scenario creation guide
├── docs/                       # Documentation
│   ├── CREATE_YOUR_OWN_TOOLS.md
│   ├── WORKTREE_GUIDE.md
│   ├── THIS_IS_THE_WAY.md
│   └── design/                # Design system documentation
├── tests/                      # Test suite
│   └── terminal_bench/        # Benchmark tests
├── ai_working/                 # AI workspace
│   ├── decisions/             # Architecture decision records
│   └── DISCOVERIES.md         # Problem solutions database
├── .data/                      # Generated data (gitignored)
│   └── transcripts/           # Conversation history
├── Makefile                    # Development commands
├── pyproject.toml             # Python project configuration
└── AGENTS.md                  # AI assistant guidance
```

**Key Directories:**

- **`.claude/`** - Claude Code extensions (agents, commands, tools)
- **`scenarios/`** - Self-contained automation tools you create
- **`amplifier/`** - Core Python library code
- **`ai_working/`** - Context and decisions for AI assistants
- **`.data/`** - Runtime generated files (not version controlled)

**Philosophy:**
Each directory represents a "brick" with clear boundaries and contracts. Tools can be regenerated from their specifications rather than manually edited.

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

Using permissive AI tools in your repository requires careful attention to security considerations and careful human supervision. Even with precautions, things can still go wrong. Use Amplifier with caution and at your own risk. This is a research demonstrator in early development that may change significantly.