# Repository Synthesizer

A hierarchical synthesis tool that analyzes repositories layer-by-layer to extract novel capabilities, interesting problems solved, and enlightening experiences.

## What It Does

This tool performs deep analysis of entire repositories, processing files and directories hierarchically from the bottom up to create comprehensive insights about:

- **Novel capabilities** the codebase offers
- **Interesting problems** it solves
- **Enlightening experiences** it provides
- **Architectural insights** and design patterns
- **Unique approaches** to common problems

Unlike simple documentation generators, this tool uses AI to understand the _purpose_ and _significance_ of code, synthesizing insights at each layer of the repository hierarchy.

## How It Works

1. **Tree Building**: Scans the repository structure, building a complete hierarchy
2. **Bottom-Up Processing**: Analyzes files first, then synthesizes directory insights based on their contents
3. **Layer Synthesis**: Each directory level gets synthesized based on its children
4. **Final Synthesis**: Creates a comprehensive report answering your specific topic/question

## Installation

The tool is part of the Amplifier ecosystem. Ensure you have:

```bash
# Install dependencies
make install

# Verify ccsdk toolkit is available
python -c "import amplifier.ccsdk_toolkit"
```

## Usage

### Basic Usage

Analyze the current repository for novel capabilities:

```bash
python -m scenarios.repo_synthesizer \
  --topic "What novel, interesting, and enlightening things can be done with this codebase?"
```

### Custom Repository

Analyze a specific repository:

```bash
python -m scenarios.repo_synthesizer \
  --repo-path /path/to/repo \
  --topic "What unique architectural patterns does this use?" \
  --output architecture_analysis.md
```

### Filtered Analysis

Focus on specific file types:

```bash
python -m scenarios.repo_synthesizer \
  --topic "How does the testing strategy work?" \
  --include "*.py,*.test.ts" \
  --exclude "node_modules,dist" \
  --max-depth 5
```

### Resume Interrupted Analysis

The tool saves progress automatically:

```bash
# If interrupted, resume with the session ID shown
python -m scenarios.repo_synthesizer \
  --resume abc12345 \
  --topic "Original topic..."
```

## Example Output

The tool generates a comprehensive markdown report with:

```markdown
# Repository Synthesis: my-project

**Topic**: What novel capabilities does this offer?
**Repository**: /path/to/my-project
**Generated**: 2025-01-13T10:30:00

## Executive Summary

This repository implements a revolutionary approach to...

## Novel Capabilities

### Hybrid Code+AI Pipeline

**Significance**: Combines structured iteration with intelligent analysis
**Implementation**: Uses make commands for reliability, AI for insight

### Hierarchical Knowledge Synthesis

**Significance**: Builds understanding from bottom-up
**Implementation**: Tree traversal with layer-wise synthesis

## Architecture Insights

- Clean separation between structure (code) and intelligence (AI)
- State management for incremental progress
- Paper trail for debugging and transparency

## Unique Approaches

- Bottom-up synthesis preserves detail while building abstractions
- Defensive AI integration with retry and error handling
- Session persistence for long-running analyses

## Key Takeaways

1. Code provides structure, AI provides intelligence
2. Hierarchical processing reveals emergent patterns
3. Incremental saves enable analysis of large codebases
```

## Command Line Options

| Option             | Description              | Default                   |
| ------------------ | ------------------------ | ------------------------- |
| `--repo-path`      | Repository to analyze    | Current directory         |
| `--topic`          | Synthesis question/topic | Required                  |
| `--output`         | Output file path         | `repository_synthesis.md` |
| `--resume`         | Resume session ID        | None                      |
| `--max-depth`      | Max directory depth      | 10                        |
| `--include`        | File patterns to include | All files                 |
| `--exclude`        | Patterns to exclude      | Common ignores            |
| `--no-paper-trail` | Skip paper trail         | False                     |

## Performance Expectations

Processing time depends on repository size:

- **Small repos** (<100 files): 5-10 minutes
- **Medium repos** (100-500 files): 15-30 minutes
- **Large repos** (500-1000 files): 30-60 minutes
- **Very large repos** (1000+ files): 1-2+ hours

The tool shows progress continuously and saves state for resume capability.

## Paper Trail

By default, the tool creates a `.repo_synthesis_temp/` directory with:

- **content/**: Original file contents
- **prompts/**: AI prompts used
- **responses/**: AI responses
- **synthesis/**: Layer-by-layer synthesis results

This paper trail is kept after completion, keeping only the final report.

## Advanced Topics

### Custom Topics

The topic parameter accepts any question or analysis focus:

- "What design patterns are used and why?"
- "How could this codebase be simplified?"
- "What are the security implications of this architecture?"
- "How does this compare to conventional approaches?"
- "What can other projects learn from this?"

### Incremental Analysis

The tool saves progress after each node, allowing you to:

1. Interrupt analysis at any time (Ctrl+C)
2. Resume from where you left off
3. Adjust parameters and continue

### Integration with Knowledge Systems

The synthesis output can be fed into knowledge graphs or other analysis tools for further processing.

## Troubleshooting

### "Claude CLI not found"

Install the Claude Code SDK:

```bash
npm install -g @anthropic-ai/claude-code
```

### "Session not found"

Check available sessions:

```bash
ls .repo_synthesis_state_*/state.json
```

### Memory/Performance Issues

For very large repos:

- Use `--max-depth` to limit traversal
- Use `--include` to focus on specific files
- Consider analyzing subdirectories separately

## Philosophy

This tool embodies the "code for structure, AI for intelligence" principle:

- **Code handles**: File traversal, state management, progress tracking
- **AI handles**: Understanding meaning, finding patterns, generating insights

The hierarchical approach mirrors how humans understand complex systems - starting with details and building up to abstractions.

## Contributing

See `HOW_TO_CREATE_YOUR_OWN.md` for guidance on creating similar tools.

## Related Tools

- `knowledge_synthesis`: Extract knowledge from documents
- `blog_writer`: Generate blog posts from ideas
- `tips_synthesizer`: Synthesize tips from collections
