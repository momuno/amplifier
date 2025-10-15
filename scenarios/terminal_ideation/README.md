# Terminal Ideation Tool

> 🚀 Explore multiple variants of an idea in parallel using Claude Code

The Terminal Ideation Tool spawns multiple Claude Code sessions in separate terminal windows, each exploring a different variant of your idea. This enables parallel exploration of different approaches, perspectives, or implementations simultaneously.

## What It Does

Given a single idea or prompt, this tool:
1. **Generates diverse variants** - Uses AI to create different exploration angles
2. **Creates isolated environments** - Each variant gets its own git worktree
3. **Spawns parallel terminals** - Opens color-coded terminal tabs with Claude Code
4. **Tracks progress** - Monitors the status of all variants via a shared status file
5. **Enables cleanup** - Removes worktrees and branches when done

## Key Features

- **Parallel Exploration**: Run 3-10 variants simultaneously
- **Visual Distinction**: Each terminal tab has a unique color and title
- **Isolated Environments**: Git worktrees prevent conflicts between variants
- **Progress Tracking**: Monitor all variants from a central location
- **Three Variant Styles**:
  - `exploratory` - Different perspectives and approaches
  - `focused` - Specific technical implementations
  - `creative` - Innovative and unconventional approaches

## Quick Start

```bash
# Explore an idea with 3 default variants
python scenarios/terminal_ideation/terminal_ideation.py "Create a web scraper for news articles"

# Generate 5 focused technical variants
python scenarios/terminal_ideation/terminal_ideation.py "Implement a caching system" --variants 5 --style focused

# Generate creative approaches without auto-execution
python scenarios/terminal_ideation/terminal_ideation.py "Design a user authentication flow" --style creative --no-auto
```

## Usage

### Basic Exploration

```bash
python terminal_ideation.py "Your idea here"
```

This will:
1. Generate 3 exploratory variants of your idea
2. Create a git worktree for each variant
3. Spawn a new terminal tab for each variant
4. Auto-execute the variant prompt in Claude Code
5. Display the session ID for tracking

### Advanced Options

```bash
python terminal_ideation.py "Your idea" \
  --variants 5 \              # Number of variants (1-10)
  --style focused \           # Variant style (exploratory/focused/creative)
  --no-auto \                 # Don't auto-execute prompts
  --base-branch develop       # Base git branch (default: main)
```

### Session Management

```bash
# List all ideation sessions
python terminal_ideation.py --list

# Check status of a specific session
python terminal_ideation.py --status abc12345

# Clean up a completed session (removes worktrees)
python terminal_ideation.py --cleanup abc12345
```

## How It Works

### 1. Variant Generation (AI)
The tool uses Claude to generate diverse variants of your idea:
- Each variant has a unique title, approach, and detailed prompt
- Variants explore meaningfully different aspects
- Color-coded for visual distinction

### 2. Worktree Creation (Code)
For each variant:
- Creates a new git branch: `ideation/variant-{id}-{timestamp}`
- Sets up an isolated worktree at `~/.amplifier/worktrees/`
- Copies environment files and installs dependencies

### 3. Terminal Spawning (Code)
Opens Windows Terminal tabs (on WSL2):
- Each tab has the variant's title and color
- Navigates to the variant's worktree
- Creates a startup script with the variant prompt
- Optionally auto-executes in Claude Code

### 4. Progress Tracking (Code)
Maintains a status file at `~/.amplifier/ideation_status/{session_id}.json`:
- Tracks each variant's status (pending/running/completed/failed)
- Records worktree locations and terminal PIDs
- Enables monitoring from the main terminal

## Example Session

```bash
$ python terminal_ideation.py "Build a CLI tool for managing todo lists"

============================================================
Terminal Ideation Tool
============================================================
Idea: Build a CLI tool for managing todo lists
Variants: 3 (exploratory)
Auto-execute: True
Base branch: main
============================================================

Generating 3 exploratory variants...
Generated 3 variants

Processing variant 1/3: Simple File-Based
Creating worktree for variant abc12345
Spawning terminal for variant abc12345

Processing variant 2/3: Database-Backed
Creating worktree for variant def67890
Spawning terminal for variant def67890

Processing variant 3/3: Cloud-Synced
Creating worktree for variant ghi13579
Spawning terminal for variant ghi13579

============================================================
✅ Session launched successfully!
Session ID: xyz99999
Variants launched: 3/3
Status tracking: ~/.amplifier/ideation_status/xyz99999.json
============================================================

🚀 Your variants are now running in separate terminals!
Each terminal tab has a different color and shows the variant title.

To check status later, run:
  python terminal_ideation.py --status xyz99999

When done, clean up with:
  python terminal_ideation.py --cleanup xyz99999
```

## Platform Support

Currently optimized for **WSL2 with Windows Terminal**. The tool detects the platform and attempts to use:
- **WSL2**: Windows Terminal (wt.exe)
- **Linux**: gnome-terminal, konsole, or xterm
- **macOS**: Terminal.app via AppleScript
- **Windows**: Windows Terminal natively

## File Structure

```
scenarios/terminal_ideation/
├── README.md                    # This file
├── HOW_TO_CREATE_YOUR_OWN.md   # Guide for adapting this tool
├── terminal_ideation.py         # Main CLI script
├── core/                        # Core modules
│   ├── variant_generator.py    # AI variant generation
│   ├── worktree_manager.py     # Git worktree operations
│   ├── terminal_spawner.py     # Terminal window management
│   ├── session_orchestrator.py # Session coordination
│   └── progress_tracker.py     # Progress tracking
└── sessions/                    # Session data storage
```

## Philosophy

This tool embodies the "code for structure, AI for intelligence" principle:
- **Code handles**: Terminal spawning, git operations, file I/O, progress tracking
- **AI handles**: Variant generation, creative exploration, prompt crafting
- **Parallel execution**: Explores multiple approaches simultaneously
- **Isolation**: Each variant is independent, preventing conflicts
- **Simplicity**: Fire-and-forget architecture with file-based coordination

## Tips

1. **Start small**: Begin with 2-3 variants to test the concept
2. **Use styles wisely**:
   - `exploratory` for initial ideation
   - `focused` for technical deep-dives
   - `creative` for out-of-the-box thinking
3. **Monitor progress**: Use `--status` to check how variants are doing
4. **Clean up**: Always use `--cleanup` to remove worktrees when done
5. **Close terminals first**: Before cleanup, manually close terminal windows

## Troubleshooting

### "Git operation failed"
- Ensure you're in a git repository
- Check that the base branch exists
- Verify you have uncommitted changes saved

### "No suitable terminal emulator found"
- On WSL2: Ensure Windows Terminal is installed
- On Linux: Install gnome-terminal, konsole, or xterm
- On macOS: Terminal.app should work by default

### "File I/O error"
- Check for cloud-synced directories (OneDrive, Dropbox)
- The tool includes retry logic for cloud sync delays

## Future Enhancements

- [ ] Web dashboard for monitoring variants
- [ ] Automatic result synthesis from all variants
- [ ] Support for custom variant templates
- [ ] Integration with other AI models
- [ ] Variant comparison and merging tools

## Related Tools

- `blog_writer` - Transforms ideas into polished blog posts
- `knowledge_synthesis` - Extracts and synthesizes knowledge from documents
- `article_illustrator` - Generates AI illustrations for articles

---

*Built with the Amplifier CLI pattern - combining code structure with AI intelligence*