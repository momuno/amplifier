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


def gather_context() -> str:
    """
    Gather context from hardcoded source files.

    Reads each file in SOURCES and concatenates their content into a single string,
    with clear file separators. Missing files are skipped with a warning.

    Returns:
        str: Concatenated content from all available source files
    """
    parts: list[str] = []

    for source in SOURCES:
        content = read_source_file(source)
        if content is not None:
            parts.append(f"--- {source} ---\n{content}\n")

    return "\n".join(parts)
