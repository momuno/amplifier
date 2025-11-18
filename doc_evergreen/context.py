"""
Context gathering for doc-evergreen.

Collects content from hardcoded source files to provide context for documentation generation.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Hardcoded source files to gather context from
SOURCES = [
    "README.md",
    "amplifier/__init__.py",
    "pyproject.toml",
    "AGENTS.md",
]


def read_source_file(path: str) -> str | None:
    """
    Read a single source file.

    Args:
        path: Path to source file

    Returns:
        File content as string, or None if file doesn't exist
    """
    filepath = Path(path)

    try:
        return filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Source file not found, skipping: {path}")
        return None


def gather_context(sources: list[Path] | None = None) -> str:
    """
    Gather context from source files.

    Reads each file in the provided sources list (or SOURCES if none provided)
    and concatenates their content into a single string, with clear file separators.
    Missing files are skipped with a warning.

    Args:
        sources: Optional list of Path objects to gather context from.
                 If None, uses hardcoded SOURCES.

    Returns:
        str: Concatenated content from all available source files
    """
    # Use provided sources or fall back to defaults
    source_list = sources if sources is not None else [Path(s) for s in SOURCES]

    parts: list[str] = []

    for source in source_list:
        source_str = str(source)
        content = read_source_file(source_str)
        if content is not None:
            parts.append(f"--- {source_str} ---\n{content}\n")

    return "\n".join(parts)
