"""
Source Resolution for doc_evergreen

Handles parsing, expanding, and resolving source file specifications:
- Parse comma-separated source specifications
- Expand glob patterns (*, **)
- Apply exclusion patterns
- Resolve final source lists with CLI/config/default priority
- Validate that sources exist
"""

import fnmatch
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Built-in default patterns when no sources are specified
DEFAULT_PATTERNS = ["**/*.py", "**/*.md", "pyproject.toml", "package.json"]


def parse_source_spec(spec: str) -> list[str]:
    """
    Parse comma-separated source specification into list of paths.

    Given: A source spec string (possibly with commas and spaces)
    When: Parsing the specification
    Then: Returns list of trimmed path strings

    Args:
        spec: Comma-separated source specification (e.g., "a.py,b.py,c.py")

    Returns:
        List of individual source paths, with whitespace trimmed
    """
    if not spec or not spec.strip():
        return []

    return [path.strip() for path in spec.split(",") if path.strip()]


def expand_glob_patterns(patterns: list[str], base_dir: Path) -> list[str]:
    """
    Expand glob patterns to actual file paths.

    Given: A list of file patterns (literals and globs)
    When: Expanding patterns relative to base_dir
    Then: Returns list of actual file paths that match

    Args:
        patterns: List of file patterns (e.g., ["*.py", "**/*.md", "specific.py"])
        base_dir: Base directory for relative pattern expansion

    Returns:
        List of absolute file paths as strings
    """
    expanded = []

    for pattern in patterns:
        pattern_path = Path(pattern)

        # Check if it's an absolute path or a literal file
        if pattern_path.is_absolute():
            # Absolute literal path - include even if doesn't exist
            # (validation happens separately)
            expanded.append(str(pattern_path))
        elif "*" not in pattern and "?" not in pattern:
            # Literal relative path (no glob characters)
            # Include even if doesn't exist (validation happens separately)
            full_path = base_dir / pattern
            expanded.append(str(full_path))
        else:
            # Glob pattern - expand it (only includes existing files)
            matches = list(base_dir.glob(pattern))
            # Only include files, not directories
            expanded.extend(str(m) for m in matches if m.is_file())

    return expanded


def apply_exclusions(files: list[str], exclusions: list[str]) -> list[str]:
    """
    Filter out files matching exclusion patterns.

    Given: A list of file paths and exclusion patterns
    When: Applying exclusions using fnmatch
    Then: Returns files that don't match any exclusion pattern

    Args:
        files: List of file paths to filter
        exclusions: List of fnmatch patterns (e.g., ["test_*.py", "*.tmp"])

    Returns:
        List of file paths that don't match any exclusion pattern
    """
    if not exclusions:
        return files

    filtered = []
    for file in files:
        filename = Path(file).name
        # Check if filename matches any exclusion pattern
        if not any(fnmatch.fnmatch(filename, pattern) for pattern in exclusions):
            filtered.append(file)

    return filtered


def validate_sources(sources: list[str]) -> list[str]:
    """
    Validate that source files exist, logging warnings for missing files.

    Given: A list of source file paths
    When: Checking if each file exists
    Then: Returns only existing files, logs warnings for missing ones

    Args:
        sources: List of source file paths to validate

    Returns:
        List of file paths that actually exist
    """
    validated = []

    for source in sources:
        source_path = Path(source)
        if source_path.exists():
            validated.append(source)
        else:
            logger.warning(f"Source file not found: {source}")

    return validated


def resolve_sources(
    cli_sources: str | None = None,
    config_sources: list[str] | None = None,
    base_dir: Path | None = None,
    add_sources: str | None = None,
) -> list[str]:
    """
    Resolve final source list from CLI, config, and defaults with priority handling.

    Priority order:
    1. CLI sources (--sources) - if specified, ONLY these are used
    2. Add sources (--add-sources) - merged WITH config sources
    3. Config sources (from config file) - used if no CLI sources
    4. Built-in defaults - used if nothing else specified

    Given: CLI sources, config sources, and/or add sources
    When: Resolving which sources to use
    Then: Returns final list of source paths respecting priority

    Args:
        cli_sources: Sources from CLI --sources argument (overrides all)
        config_sources: Sources from config file
        base_dir: Base directory for resolving relative paths
        add_sources: Sources from CLI --add-sources (merges with config)

    Returns:
        List of resolved source file paths
    """
    # Default base_dir to current directory if not specified
    if base_dir is None:
        base_dir = Path.cwd()

    # Priority 1: CLI sources override everything
    if cli_sources:
        patterns = parse_source_spec(cli_sources)
        return expand_glob_patterns(patterns, base_dir)

    # Priority 2: Add sources merge with config
    if add_sources:
        patterns = parse_source_spec(add_sources)
        if config_sources:
            patterns.extend(config_sources)
        return expand_glob_patterns(patterns, base_dir)

    # Priority 3: Config sources
    if config_sources:
        return expand_glob_patterns(config_sources, base_dir)

    # Priority 4: Built-in defaults
    return expand_glob_patterns(DEFAULT_PATTERNS, base_dir)
