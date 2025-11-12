"""
File discovery and gathering for doc-evergreen.

Handles finding source files via glob patterns, validating encoding,
and reading file contents. Includes LLM-guided intelligent discovery.
"""

from pathlib import Path

import pathspec

from doc_evergreen.core.doc_logger import trace_function


def find_files(patterns: list[str], base_path: Path, max_depth: int = 100) -> list[Path]:
    """
    Find files matching glob patterns or exact file paths.

    Supports both:
    - Exact file paths: "README.md", "src/main.py"
    - Glob patterns: "src/**/*.py", "*.md"
    - Mix of both: ["README.md", "src/**/*.py", "docs/guide.md"]

    Args:
        patterns: List of glob patterns or exact file paths
        base_path: Base directory to search from
        max_depth: Maximum directory depth to traverse (not used, for compatibility)

    Returns:
        List of matching file paths (absolute)
    """
    matched_files: set[Path] = set()

    for pattern in patterns:
        # First check if it's an exact file path
        exact_path = base_path / pattern
        if exact_path.is_file():
            matched_files.add(exact_path)
            continue

        # Otherwise treat as glob pattern
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                matched_files.add(file_path)

    return sorted(matched_files)


def load_gitignore(repo_path: Path) -> pathspec.PathSpec | None:
    """
    Load .gitignore patterns.

    Args:
        repo_path: Path to repository root

    Returns:
        PathSpec object or None if .gitignore doesn't exist
    """
    gitignore_path = repo_path / ".gitignore"

    if not gitignore_path.exists():
        return None

    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns = f.read().splitlines()

        # Filter out comments and empty lines
        patterns = [p for p in patterns if p.strip() and not p.strip().startswith("#")]

        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    except Exception:
        # If we can't read .gitignore, just skip it
        return None


def should_ignore(file_path: Path, repo_path: Path, gitignore: pathspec.PathSpec | None) -> bool:
    """
    Check if file should be ignored based on gitignore patterns.

    Args:
        file_path: Path to file
        repo_path: Path to repository root
        gitignore: PathSpec object from .gitignore

    Returns:
        True if file should be ignored
    """
    if gitignore is None:
        return False

    try:
        # Get relative path from repo root
        rel_path = file_path.relative_to(repo_path)
        return gitignore.match_file(str(rel_path))
    except ValueError:
        # File is not relative to repo_path
        return False


def validate_utf8(file_path: Path) -> bool:
    """
    Check if file is valid UTF-8.

    Args:
        file_path: Path to file

    Returns:
        True if file is valid UTF-8, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read()
        return True
    except (UnicodeDecodeError, FileNotFoundError):
        return False


def read_file(file_path: Path) -> str:
    """
    Read file contents as UTF-8.

    Args:
        file_path: Path to file

    Returns:
        File contents as string

    Raises:
        UnicodeDecodeError: If file is not valid UTF-8
        FileNotFoundError: If file doesn't exist
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


@trace_function
def gather_files(patterns: list[str], repo_path: Path, respect_gitignore: bool = True) -> dict[str, str]:
    """
    Gather files matching patterns/paths and read their contents.

    Supports both exact file paths and glob patterns:
    - Exact: ["README.md", "src/main.py"]
    - Patterns: ["src/**/*.py", "*.md"]
    - Mixed: ["README.md", "src/**/*.py", "docs/guide.md"]

    Args:
        patterns: List of glob patterns or exact file paths
        repo_path: Path to repository root
        respect_gitignore: If True, skip files in .gitignore

    Returns:
        Dictionary mapping file paths (relative to repo) to contents
    """
    # Find all matching files
    files = find_files(patterns, repo_path)

    # Load gitignore if needed
    gitignore = load_gitignore(repo_path) if respect_gitignore else None

    # Read files
    result: dict[str, str] = {}

    for file_path in files:
        # Skip if gitignored
        if should_ignore(file_path, repo_path, gitignore):
            continue

        # Validate UTF-8
        if not validate_utf8(file_path):
            continue

        # Read contents
        try:
            contents = read_file(file_path)
            # Store with relative path as key
            rel_path = file_path.relative_to(repo_path)
            result[str(rel_path)] = contents
        except Exception:
            # Skip files we can't read
            continue

    return result


def traverse_repo_tree(
    repo_path: Path,
    max_depth: int = 2,
    patterns: list[str] | None = None,
    include_extensions: set[str] | None = None,
    exclude_dirs: set[str] | None = None,
) -> list[Path]:
    """
    Traverse repository tree and collect relevant files.

    Can filter by either glob patterns OR file extensions:
    - If patterns provided: matches files against those patterns during traversal
    - If patterns not provided: uses extension-based filtering (default behavior)

    Args:
        repo_path: Path to repository root
        max_depth: Maximum directory depth to traverse (0 = root only, 1 = root + immediate subdirs, etc.)
        patterns: List of glob patterns to match files (e.g., ['src/**/*.py', '*.md'])
                 If provided, takes precedence over include_extensions
        include_extensions: Set of file extensions to include (e.g., {'.py', '.md', '.toml'})
                          Only used if patterns is None. If None, includes common documentation-relevant extensions
        exclude_dirs: Set of directory names to exclude (e.g., {'.git', 'node_modules'})
                     If None, uses common exclusions

    Returns:
        List of file paths found
    """
    if include_extensions is None and patterns is None:
        # Common extensions for documentation purposes (only used if no patterns)
        include_extensions = {
            ".py",
            ".md",
            ".rst",
            ".txt",
            ".toml",
            ".yaml",
            ".yml",
            ".json",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
        }

    if exclude_dirs is None:
        # Common directories to exclude
        exclude_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "dist",
            "build",
            ".eggs",
            "*.egg-info",
        }

    files: list[Path] = []

    def should_exclude_dir(dir_path: Path) -> bool:
        """Check if directory should be excluded."""
        return dir_path.name in exclude_dirs

    def matches_patterns(file_path: Path) -> bool:
        """Check if file matches any of the provided patterns."""
        if patterns is None:
            return False

        # Get relative path from repo root for pattern matching
        try:
            rel_path = file_path.relative_to(repo_path)
            rel_str = str(rel_path)

            for pattern in patterns:
                # Check if it's an exact match first
                if rel_str == pattern:
                    return True
                # Use Path.match() which properly handles ** glob patterns
                if rel_path.match(pattern):
                    return True
        except ValueError:
            pass

        return False

    def walk_tree(current_path: Path, current_depth: int) -> None:
        """Recursively walk tree up to max_depth."""
        if current_depth > max_depth:
            return

        try:
            for item in sorted(current_path.iterdir()):
                # Skip if in excluded directory names
                if item.is_dir():
                    if should_exclude_dir(item):
                        continue
                    # Recurse into subdirectory
                    walk_tree(item, current_depth + 1)
                elif item.is_file():
                    # Filter by patterns if provided, otherwise by extension
                    if patterns is not None:
                        if matches_patterns(item):
                            files.append(item)
                    elif include_extensions and item.suffix in include_extensions:
                        files.append(item)
        except PermissionError:
            # Skip directories we can't read
            pass

    # Start traversal from root at depth 0
    walk_tree(repo_path, 0)

    return sorted(files)


def peek_file(file_path: Path, max_chars: int = 500) -> str:
    """
    Read first N characters of a file for preview.

    Args:
        file_path: Path to file
        max_chars: Maximum characters to read

    Returns:
        First N characters or "[binary file]" or "[unreadable]"
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(max_chars)
            if len(content) == max_chars:
                content += "..."
            return content
    except UnicodeDecodeError:
        return "[binary file]"
    except Exception:
        return "[unreadable]"


def summarize_and_evaluate_file(file_path: Path, doc_goal: str, max_summary_chars: int = 800) -> dict:
    """
    Read a file fully, generate a summary, and evaluate its relevance to documentation goal.

    Args:
        file_path: Path to file
        doc_goal: What the documentation is about
        max_summary_chars: Maximum characters for summary

    Returns:
        Dictionary with 'summary', 'relevance_evaluation', 'relevance_score', 'error' keys
    """
    # Import here to avoid circular dependency
    from doc_evergreen.core.generator import call_llm

    try:
        # Try to read file fully
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # If file is too large (>50KB), use peek with low relevance
        if len(content) > 50000:
            peek_content = peek_file(file_path, max_chars=500)
            return {
                "summary": peek_content + "\n[Large file - showing preview only]",
                "relevance_evaluation": "File too large to fully analyze",
                "relevance_score": 3,
                "error": None,
            }

        # Generate summary and relevance evaluation using LLM
        prompt = f"""Analyze this file and provide:
1. A concise summary (max {max_summary_chars} chars) covering:
   - What this file does/contains
   - Key functionality or content
   - Technologies/frameworks used

2. Evaluate how relevant this file is to the documentation goal
3. Rate relevance on a scale of 1-10 (1=not relevant, 10=highly relevant)

Documentation Goal: {doc_goal}

File name: {file_path.name}

File content:
{content}

Respond in this EXACT format:

SUMMARY:
<your summary here>

RELEVANCE_EVALUATION:
<explain why this file is or isn't relevant to the documentation goal>

RELEVANCE_SCORE: <number 1-10>"""

        response = call_llm(prompt, max_tokens=800, temperature=0.3)

        # Parse response
        summary = ""
        evaluation = ""
        score = 5  # Default middle score

        lines = response.split("\n")
        current_section = None

        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith("SUMMARY:"):
                current_section = "summary"
                # Get text after "SUMMARY:" on same line if any
                remainder = line_stripped[8:].strip()
                if remainder:
                    summary = remainder
                continue
            elif line_stripped.startswith("RELEVANCE_EVALUATION:"):
                current_section = "evaluation"
                remainder = line_stripped[21:].strip()
                if remainder:
                    evaluation = remainder
                continue
            elif line_stripped.startswith("RELEVANCE_SCORE:"):
                current_section = None
                # Extract score
                score_text = line_stripped[16:].strip()
                try:
                    score = int(score_text)
                    # Clamp to 1-10
                    score = max(1, min(10, score))
                except ValueError:
                    score = 5
                continue

            # Accumulate content for current section
            if current_section == "summary" and line_stripped:
                if summary:
                    summary += " " + line_stripped
                else:
                    summary = line_stripped
            elif current_section == "evaluation" and line_stripped:
                if evaluation:
                    evaluation += " " + line_stripped
                else:
                    evaluation = line_stripped

        # Ensure we have at least some content
        if not summary:
            summary = "Unable to parse summary"
        if not evaluation:
            evaluation = "Unable to parse evaluation"

        return {
            "summary": summary.strip(),
            "relevance_evaluation": evaluation.strip(),
            "relevance_score": score,
            "error": None,
        }

    except UnicodeDecodeError:
        return {
            "summary": "[binary file]",
            "relevance_evaluation": "Binary file - not analyzable",
            "relevance_score": 1,
            "error": "UnicodeDecodeError",
        }
    except Exception as e:
        # Fallback to peek if LLM fails
        peek_content = peek_file(file_path, max_chars=500)
        return {
            "summary": peek_content + f"\n[Analysis failed: {str(e)[:50]}]",
            "relevance_evaluation": "Analysis failed - defaulting to low relevance",
            "relevance_score": 3,
            "error": str(e),
        }


def summarize_file_with_llm(file_path: Path, max_summary_chars: int = 1000) -> str:
    """
    Legacy function for backward compatibility. Use summarize_and_evaluate_file() for new code.

    Args:
        file_path: Path to file
        max_summary_chars: Maximum characters for summary

    Returns:
        Summary of file contents or error message
    """
    result = summarize_and_evaluate_file(
        file_path, doc_goal="general documentation", max_summary_chars=max_summary_chars
    )
    return result["summary"]


def format_files_for_llm(file_info: list[dict]) -> str:
    """
    Format file information for LLM prompt.

    Args:
        file_info: List of dicts with path, name, size, summary, relevance_score, relevance_evaluation

    Returns:
        Formatted string for prompt
    """
    if not file_info:
        return "(no files at this level)"

    # Sort by relevance score (highest first) for better context
    sorted_info = sorted(file_info, key=lambda x: x.get("relevance_score", 0), reverse=True)

    lines = []
    for info in sorted_info[:20]:  # Limit to prevent token overload
        size_kb = info["size"] / 1024
        score = info.get("relevance_score", 0)

        # Use emoji indicators for relevance level
        if score >= 8:
            relevance_indicator = "🟢"  # High relevance
        elif score >= 5:
            relevance_indicator = "🟡"  # Medium relevance
        else:
            relevance_indicator = "🔴"  # Low relevance

        lines.append(f"\n{relevance_indicator} {info['path']} ({size_kb:.1f} KB) [Relevance: {score}/10]")
        lines.append(f"   Summary: {info['summary']}")
        lines.append(f"   Why: {info.get('relevance_evaluation', 'No evaluation')}")

    if len(file_info) > 20:
        lines.append(f"\n... and {len(file_info) - 20} more files")

    return "\n".join(lines)


def peek_directory_contents(dir_path: Path) -> dict:
    """
    Peek into a directory to see what's inside (names only, no content).

    Args:
        dir_path: Path to directory

    Returns:
        Dictionary with subdirectory names and file names
    """
    try:
        items = list(dir_path.iterdir())
        subdirs = [item.name for item in items if item.is_dir()]
        files = [item.name for item in items if item.is_file()]

        return {
            "subdirs": sorted(subdirs),
            "files": sorted(files),
            "total_items": len(subdirs) + len(files),
        }
    except PermissionError:
        return {"subdirs": [], "files": [], "total_items": 0, "error": "Permission denied"}
    except Exception as e:
        return {"subdirs": [], "files": [], "total_items": 0, "error": str(e)}


def evaluate_directory_relevance(dir_path: Path, doc_goal: str, repo_path: Path) -> dict:
    """
    Evaluate directory relevance based on its contents (names only).

    Args:
        dir_path: Path to directory
        doc_goal: What the documentation is about
        repo_path: Repository root path

    Returns:
        Dictionary with relevance_evaluation, relevance_score, contents
    """
    # Import here to avoid circular dependency
    from doc_evergreen.core.generator import call_llm

    # Get directory contents
    contents = peek_directory_contents(dir_path)

    # Handle errors
    if contents.get("error"):
        return {
            "relevance_evaluation": f"Cannot access: {contents['error']}",
            "relevance_score": 1,
            "subdirs": [],
            "files": [],
            "error": contents["error"],
        }

    # If directory is empty, low relevance
    if contents["total_items"] == 0:
        return {
            "relevance_evaluation": "Empty directory",
            "relevance_score": 1,
            "subdirs": [],
            "files": [],
            "error": None,
        }

    # Get relative path for display
    try:
        rel_path = dir_path.relative_to(repo_path)
        dir_display = str(rel_path)
    except ValueError:
        dir_display = str(dir_path)

    # Create lists for display (limit to prevent token overflow)
    subdirs_display = contents["subdirs"][:20]
    files_display = contents["files"][:20]

    if len(contents["subdirs"]) > 20:
        subdirs_display.append(f"... and {len(contents['subdirs']) - 20} more")
    if len(contents["files"]) > 20:
        files_display.append(f"... and {len(contents['files']) - 20} more")

    # Build prompt for LLM
    prompt = f"""Evaluate how relevant this directory is to exploring for documentation generation.

Documentation Goal: {doc_goal}

Directory: {dir_display}

SUBDIRECTORIES in this directory:
{chr(10).join(f"  - {name}" for name in subdirs_display) if subdirs_display else "  (none)"}

FILES in this directory:
{chr(10).join(f"  - {name}" for name in files_display) if files_display else "  (none)"}

Based ONLY on these names (not file contents), evaluate:
1. How relevant is this directory to the documentation goal?
2. What kind of content might be inside based on naming patterns?
3. Should this directory be explored deeper?

Rate relevance on a scale of 1-10 (1=not relevant, 10=highly relevant)

Respond in this EXACT format:

RELEVANCE_EVALUATION:
<explain what you think is in this directory and why it is/isn't relevant>

RELEVANCE_SCORE: <number 1-10>"""

    try:
        response = call_llm(prompt, max_tokens=400, temperature=0.3)

        # Parse response
        evaluation = ""
        score = 5  # Default middle score

        lines = response.split("\n")
        current_section = None

        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith("RELEVANCE_EVALUATION:"):
                current_section = "evaluation"
                remainder = line_stripped[21:].strip()
                if remainder:
                    evaluation = remainder
                continue
            elif line_stripped.startswith("RELEVANCE_SCORE:"):
                current_section = None
                score_text = line_stripped[16:].strip()
                try:
                    score = int(score_text)
                    score = max(1, min(10, score))
                except ValueError:
                    score = 5
                continue

            if current_section == "evaluation" and line_stripped:
                if evaluation:
                    evaluation += " " + line_stripped
                else:
                    evaluation = line_stripped

        if not evaluation:
            evaluation = "Unable to parse evaluation"

        return {
            "relevance_evaluation": evaluation.strip(),
            "relevance_score": score,
            "subdirs": contents["subdirs"],
            "files": contents["files"],
            "error": None,
        }

    except Exception as e:
        # Fallback on error
        return {
            "relevance_evaluation": f"Evaluation failed: {str(e)[:50]}",
            "relevance_score": 3,
            "subdirs": contents["subdirs"],
            "files": contents["files"],
            "error": str(e),
        }


def format_dirs_for_llm(dir_info: list[dict]) -> str:
    """
    Format directory information for LLM prompt.

    Args:
        dir_info: List of dicts with path, name, relevance_score, relevance_evaluation, subdirs, files

    Returns:
        Formatted string for prompt
    """
    if not dir_info:
        return "(no subdirectories at this level)"

    # Sort by relevance score (highest first)
    sorted_info = sorted(dir_info, key=lambda x: x.get("relevance_score", 0), reverse=True)

    lines = []
    for info in sorted_info[:20]:  # Limit to prevent token overload
        score = info.get("relevance_score", 0)

        # Use emoji indicators for relevance level
        if score >= 8:
            relevance_indicator = "🟢"  # High relevance
        elif score >= 5:
            relevance_indicator = "🟡"  # Medium relevance
        else:
            relevance_indicator = "🔴"  # Low relevance

        subdir_count = len(info.get("subdirs", []))
        file_count = len(info.get("files", []))

        lines.append(
            f"\n{relevance_indicator} {info['path']} ({subdir_count} subdirs, {file_count} files) [Relevance: {score}/10]"
        )
        lines.append(f"   Why: {info.get('relevance_evaluation', 'No evaluation')}")

        # Show some example names to give context
        if info.get("files"):
            sample_files = info["files"][:3]
            lines.append(f"   Sample files: {', '.join(sample_files)}")
        if info.get("subdirs"):
            sample_dirs = info["subdirs"][:3]
            lines.append(f"   Sample subdirs: {', '.join(sample_dirs)}")

    if len(dir_info) > 20:
        lines.append(f"\n... and {len(dir_info) - 20} more directories")

    return "\n".join(lines)


def parse_relevant_files(llm_response: str) -> list[str]:
    """
    Parse file paths from LLM response.

    Args:
        llm_response: LLM's response text

    Returns:
        List of relative file paths
    """
    files = []
    in_section = False

    for line in llm_response.split("\n"):
        line = line.strip()

        if "RELEVANT_FILES:" in line:
            in_section = True
            continue
        elif any(keyword in line for keyword in ["EXPLORE_DIRECTORIES:", "REASON:"]):
            in_section = False
            continue

        if in_section and line.startswith("-"):
            # Extract path after the dash
            path = line.lstrip("- ").strip()
            if path and path.lower() != "none":
                files.append(path)

    return files


def parse_explore_directories(llm_response: str) -> list[str]:
    """
    Parse directory paths from LLM response.

    Args:
        llm_response: LLM's response text

    Returns:
        List of relative directory paths
    """
    dirs = []
    in_section = False

    for line in llm_response.split("\n"):
        line = line.strip()

        if "EXPLORE_DIRECTORIES:" in line:
            in_section = True
            continue
        elif "REASON:" in line:
            in_section = False
            continue

        if in_section and line.startswith("-"):
            # Extract path after the dash
            path = line.lstrip("- ").strip()
            if path and path.lower() != "none":
                dirs.append(path)

    return dirs


def llm_guided_discovery(about: str, repo_path: Path) -> list[str]:
    """
    Use LLM to intelligently discover relevant files through breadth-first traversal.

    At each level:
    1. Show LLM files and directories
    2. For files: peek at first ~500 chars
    3. LLM decides which files are relevant and which dirs to explore
    4. Continue until no more directories to explore

    Args:
        about: Description of what documentation is about
        repo_path: Repository root path

    Returns:
        List of relative file paths that are relevant
    """
    # Import here to avoid circular dependency
    import click

    from doc_evergreen.core.doc_logger import get_logger
    from doc_evergreen.core.generator import call_llm

    # Get logger if available
    logger = get_logger()

    # Data structures
    relevant_files: list[str] = []
    dirs_to_explore = [(repo_path, 0)]  # (dir_path, depth) tuples
    explored_dirs: set[Path] = set()

    click.echo("\n🔍 Starting LLM-guided breadth-first discovery...")
    click.echo("=" * 60)

    if logger:
        logger.logger.info("Starting LLM-guided file discovery")
        logger.logger.info(f"Documentation goal: {about}")
        logger.logger.info(f"Repository path: {repo_path}")

    # Load gitignore
    gitignore = load_gitignore(repo_path)

    # Common directories to exclude
    exclude_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".eggs",
    }

    while dirs_to_explore:
        current_dir, depth = dirs_to_explore.pop(0)  # BFS: FIFO

        if current_dir in explored_dirs:
            continue
        explored_dirs.add(current_dir)

        current_rel = str(current_dir.relative_to(repo_path)) if current_dir != repo_path else "ROOT"

        click.echo(f"\n📂 Depth {depth} | Exploring: {current_rel}")

        # Get items at this level
        try:
            items = list(current_dir.iterdir())
        except PermissionError:
            click.echo("  ⚠ Permission denied, skipping")
            continue

        files = [f for f in items if f.is_file()]
        subdirs = [d for d in items if d.is_dir()]

        # Filter out gitignored files and excluded directories
        files = [f for f in files if not should_ignore(f, repo_path, gitignore)]
        subdirs = [d for d in subdirs if d.name not in exclude_dirs]

        click.echo(f"  Found: {len(files)} files, {len(subdirs)} subdirectories")

        # Skip if nothing to process
        if not files and not subdirs:
            click.echo("  → Empty, skipping")
            continue

        # Prepare file info for LLM - generate summaries and relevance evaluations
        click.echo(f"  📝 Analyzing {len(files)} files for relevance...")
        file_info = []
        for f in files:
            try:
                rel_path = f.relative_to(repo_path)

                # Generate summary and evaluate relevance using LLM
                analysis = summarize_and_evaluate_file(f, doc_goal=about, max_summary_chars=800)

                # Log file analysis
                if logger:
                    logger.log_file_read(
                        file_path=str(rel_path),
                        reason=f"Analyzing file relevance for discovery decision at depth {depth}",
                        content_preview=f"Summary: {analysis['summary'][:300]}... | "
                        f"Relevance: {analysis['relevance_score']}/10 - {analysis['relevance_evaluation'][:200]}",
                    )

                file_info.append(
                    {
                        "path": str(rel_path),
                        "name": f.name,
                        "size": f.stat().st_size,
                        "summary": analysis["summary"],
                        "relevance_evaluation": analysis["relevance_evaluation"],
                        "relevance_score": analysis["relevance_score"],
                    }
                )
            except Exception as e:
                # Skip files we can't process
                if logger:
                    logger.log_error(
                        error_type="File Analysis Failed",
                        error_message=str(e),
                        context={"file": str(rel_path), "depth": depth},
                    )
                continue

        # Prepare directory info for LLM - evaluate relevance
        click.echo(f"  📂 Evaluating {len(subdirs)} subdirectories...")
        dir_info = []
        for d in subdirs:
            try:
                rel_path = d.relative_to(repo_path)

                # Evaluate directory relevance based on contents
                evaluation = evaluate_directory_relevance(d, doc_goal=about, repo_path=repo_path)

                # Log directory evaluation
                if logger:
                    logger.log_discovery_step(
                        depth=depth + 1,
                        directory=str(rel_path),
                        files_found=len(evaluation.get("files", [])),
                        dirs_found=len(evaluation.get("subdirs", [])),
                        selected_files=[],
                        selected_dirs=[],
                        reasoning=f"Directory relevance: {evaluation['relevance_score']}/10 - {evaluation['relevance_evaluation'][:200]}",
                    )

                dir_info.append(
                    {
                        "path": str(rel_path),
                        "name": d.name,
                        "relevance_evaluation": evaluation["relevance_evaluation"],
                        "relevance_score": evaluation["relevance_score"],
                        "subdirs": evaluation.get("subdirs", []),
                        "files": evaluation.get("files", []),
                    }
                )
            except Exception as e:
                # Skip directories we can't process
                if logger:
                    logger.log_error(
                        error_type="Directory Evaluation Failed",
                        error_message=str(e),
                        context={"directory": str(rel_path), "depth": depth},
                    )
                continue

        # Build prompt for LLM
        click.echo("  🤖 Asking LLM to make final selection...")

        # Calculate average relevance scores for context
        avg_file_score = sum(info.get("relevance_score", 0) for info in file_info) / len(file_info) if file_info else 0
        avg_dir_score = sum(info.get("relevance_score", 0) for info in dir_info) / len(dir_info) if dir_info else 0

        prompt = f"""You are making final file selection decisions for documentation generation.

Documentation Goal: {about}

Current Directory: {current_rel}
Depth Level: {depth}

FILES at this level (sorted by relevance, highest first):
{format_files_for_llm(file_info)}

SUBDIRECTORIES at this level (sorted by relevance, highest first):
{format_dirs_for_llm(dir_info)}

CONTEXT:
- Each file has been fully read, summarized, and scored for relevance (1-10 scale)
- Each directory has been peeked into (contents listed) and scored for relevance
- 🟢 Green (8-10): Highly relevant - strong candidate
- 🟡 Yellow (5-7): Moderately relevant - consider including
- 🔴 Red (1-4): Low relevance - likely skip
- Average file relevance: {avg_file_score:.1f}/10
- Average directory relevance: {avg_dir_score:.1f}/10

Task: Based on the individual relevance evaluations, decide:
1. Which files should be included in the documentation
2. Which subdirectories should be explored deeper

Guidelines for FILES:
- Prioritize files scored 7+ (highly relevant)
- Consider files scored 5-7 if they add important context
- Generally skip files scored below 5

Guidelines for DIRECTORIES:
- Explore directories scored 7+ (likely contain relevant content)
- Consider directories scored 5-7 if they might have supporting files
- Skip directories scored below 5 (unlikely to yield relevant files)

Respond EXACTLY in this format:

RELEVANT_FILES:
- path/to/file1.py
- path/to/file2.md

EXPLORE_DIRECTORIES:
- path/to/subdir1
- path/to/subdir2

REASON: <explain your selection strategy, referencing both file and directory relevance scores>

If no files are relevant, write "- NONE" under RELEVANT_FILES.
If no directories should be explored, write "- NONE" under EXPLORE_DIRECTORIES.
"""

        # Ask LLM
        try:
            response = call_llm(prompt, max_tokens=2000, temperature=0.3)

            # Log the LLM call
            if logger:
                logger.log_llm_call(
                    operation=f"Discovery decision for {current_rel} at depth {depth}",
                    prompt=prompt,
                    response=response,
                    metadata={
                        "directory": current_rel,
                        "depth": depth,
                        "files_count": len(files),
                        "subdirs_count": len(subdirs),
                    },
                )

        except Exception as e:
            # If LLM fails, fall back to including everything
            click.echo(f"  ⚠ LLM call failed: {e}, including all files")

            # Log the error
            if logger:
                logger.log_error(
                    error_type="LLM Discovery Call Failed",
                    error_message=str(e),
                    context={"directory": current_rel, "depth": depth, "fallback": "including all files"},
                )

            relevant_files.extend([str(f.relative_to(repo_path)) for f in files])
            dirs_to_explore.extend([(d, depth + 1) for d in subdirs])
            continue

        # Parse LLM response
        selected_files = parse_relevant_files(response)
        selected_dirs = parse_explore_directories(response)

        # Extract reasoning if present
        reason = ""
        if "REASON:" in response:
            reason = response.split("REASON:")[-1].strip()

        # Log the discovery step with LLM's decisions
        if logger:
            logger.log_discovery_step(
                depth=depth,
                directory=current_rel,
                files_found=len(files),
                dirs_found=len(subdirs),
                selected_files=selected_files,
                selected_dirs=selected_dirs,
                reasoning=reason,
            )

        # Show LLM's decision with relevance context
        click.echo(f"  ✓ LLM selected {len(selected_files)} files")
        if selected_files:
            # Create a lookup for relevance scores
            score_lookup = {info["path"]: info["relevance_score"] for info in file_info}
            for f in selected_files:
                score = score_lookup.get(f, 0)
                if score >= 8:
                    indicator = "🟢"
                elif score >= 5:
                    indicator = "🟡"
                else:
                    indicator = "🔴"
                click.echo(f"    {indicator} {f} [{score}/10]")

        click.echo(f"  ✓ LLM wants to explore {len(selected_dirs)} subdirectories")
        if selected_dirs:
            # Create a lookup for directory relevance scores
            dir_score_lookup = {info["path"]: info["relevance_score"] for info in dir_info}
            for d in selected_dirs:
                score = dir_score_lookup.get(d, 0)
                if score >= 8:
                    indicator = "🟢"
                elif score >= 5:
                    indicator = "🟡"
                else:
                    indicator = "🔴"
                click.echo(f"    {indicator} {d} [{score}/10]")

        # Show reasoning
        if reason:
            click.echo(f"  💭 Reason: {reason}")

        # Add selected files to collection
        relevant_files.extend(selected_files)

        # Add selected directories to exploration queue
        for dir_rel_path in selected_dirs:
            dir_full_path = repo_path / dir_rel_path
            if dir_full_path.exists() and dir_full_path.is_dir():
                dirs_to_explore.append((dir_full_path, depth + 1))

    click.echo("\n" + "=" * 60)
    click.echo(f"✅ Discovery complete! Found {len(relevant_files)} total relevant files")
    click.echo("=" * 60)

    return relevant_files


def auto_discover_files(
    topic: str,
    repo_path: Path,
    max_depth: int = 2,
    use_llm_guided: bool = False,
) -> list[str]:
    """
    Auto-discover relevant files using either tree traversal or LLM-guided discovery.

    Args:
        topic: Description of what the documentation is about
        repo_path: Path to repository root
        max_depth: Maximum directory depth for tree traversal (ignored if use_llm_guided=True)
        use_llm_guided: If True, uses LLM-guided breadth-first discovery (most intelligent)

    Returns:
        List of relative file paths
    """
    if use_llm_guided:
        # Use LLM-guided intelligent discovery (no depth limit, adaptive pruning)
        return llm_guided_discovery(topic, repo_path)

    # Use tree traversal with default extensions
    discovered_files = traverse_repo_tree(repo_path, max_depth=max_depth)

    # Load gitignore to filter
    gitignore = load_gitignore(repo_path)

    # Filter files based on gitignore
    filtered_files: list[Path] = []
    for file_path in discovered_files:
        if not should_ignore(file_path, repo_path, gitignore):
            filtered_files.append(file_path)

    # Convert to relative path strings
    relative_paths: list[str] = []
    for file_path in filtered_files:
        try:
            rel_path = file_path.relative_to(repo_path)
            relative_paths.append(str(rel_path))
        except ValueError:
            # Skip files outside repo
            continue

    return relative_paths


def estimate_file_size(patterns: list[str], repo_path: Path) -> int:
    """
    Estimate total size of files matching patterns.

    Args:
        patterns: List of glob patterns
        repo_path: Path to repository root

    Returns:
        Total size in bytes
    """
    files = find_files(patterns, repo_path)
    gitignore = load_gitignore(repo_path)

    total_size = 0
    for file_path in files:
        if should_ignore(file_path, repo_path, gitignore):
            continue

        try:
            total_size += file_path.stat().st_size
        except Exception:
            continue

    return total_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size for human readability.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.2 KB", "3.4 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
