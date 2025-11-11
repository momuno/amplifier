"""
File discovery and gathering for doc-evergreen.

Handles finding source files via glob patterns, validating encoding,
and reading file contents. Includes LLM-guided intelligent discovery.
"""

from pathlib import Path

import pathspec


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


def format_files_for_llm(file_info: list[dict]) -> str:
    """
    Format file information for LLM prompt.

    Args:
        file_info: List of dicts with path, name, size, preview

    Returns:
        Formatted string for prompt
    """
    if not file_info:
        return "(no files at this level)"

    lines = []
    for info in file_info[:20]:  # Limit to prevent token overload
        size_kb = info["size"] / 1024
        lines.append(f"\n{info['path']} ({size_kb:.1f} KB)")
        lines.append(f"Preview: {info['preview'][:200]}")

    if len(file_info) > 20:
        lines.append(f"\n... and {len(file_info) - 20} more files")

    return "\n".join(lines)


def format_dirs_for_llm(dir_info: list[dict]) -> str:
    """
    Format directory information for LLM prompt.

    Args:
        dir_info: List of dicts with path, name, file_count

    Returns:
        Formatted string for prompt
    """
    if not dir_info:
        return "(no subdirectories at this level)"

    lines = []
    for info in dir_info[:30]:  # Show more dirs since they're smaller
        lines.append(f"- {info['path']} ({info['file_count']} files)")

    if len(dir_info) > 30:
        lines.append(f"... and {len(dir_info) - 30} more directories")

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

        # Prepare file info for LLM
        file_info = []
        for f in files:
            try:
                rel_path = f.relative_to(repo_path)
                content_peek = peek_file(f, max_chars=500)

                # Log file peek
                if logger:
                    logger.log_file_read(
                        file_path=str(rel_path),
                        reason=f"Peeking file for LLM discovery decision at depth {depth}",
                        content_preview=content_peek,
                    )

                file_info.append(
                    {
                        "path": str(rel_path),
                        "name": f.name,
                        "size": f.stat().st_size,
                        "preview": content_peek,
                    }
                )
            except Exception:
                continue

        # Prepare directory info for LLM
        dir_info = []
        for d in subdirs:
            try:
                rel_path = d.relative_to(repo_path)
                # Count files in directory (shallow)
                try:
                    file_count = len([item for item in d.iterdir() if item.is_file()])
                except Exception:
                    file_count = 0
                dir_info.append({"path": str(rel_path), "name": d.name, "file_count": file_count})
            except Exception:
                continue

        # Build prompt for LLM
        click.echo("  🤖 Asking LLM to decide relevance...")

        prompt = f"""You are helping discover relevant files for documentation generation.

Documentation Goal: {about}

Current Directory: {current_rel}
Depth Level: {depth}

FILES at this level:
{format_files_for_llm(file_info)}

SUBDIRECTORIES at this level:
{format_dirs_for_llm(dir_info)}

Task: Decide which files are relevant to the documentation goal and which subdirectories should be explored deeper.

Respond EXACTLY in this format:

RELEVANT_FILES:
- path/to/file1.py
- path/to/file2.md

EXPLORE_DIRECTORIES:
- path/to/subdir1
- path/to/subdir2

REASON: <brief explanation of your decisions>

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

        # Show LLM's decision
        click.echo(f"  ✓ LLM selected {len(selected_files)} files")
        if selected_files:
            for f in selected_files:
                click.echo(f"    • {f}")

        click.echo(f"  ✓ LLM wants to explore {len(selected_dirs)} subdirectories")
        if selected_dirs:
            for d in selected_dirs:
                click.echo(f"    → {d}")

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
