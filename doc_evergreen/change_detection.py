"""Change detection module for doc_evergreen.

Compares new content against existing files to detect modifications.
"""

from difflib import unified_diff
from pathlib import Path


def detect_changes(existing_path: Path, new_content: str) -> tuple[bool, list[str]]:
    """Detect changes between existing file and new content.

    Args:
        existing_path: Path to existing file
        new_content: New content to compare against

    Returns:
        (has_changes, diff_lines) where:
        - has_changes: True if content differs or file is new
        - diff_lines: List of diff lines in unified diff format,
                     or ["NEW FILE"] for new files,
                     or [] for no changes
    """

    # Handle new files
    if not existing_path.exists():
        return (True, ["NEW FILE"])

    # Read existing content
    existing_content = existing_path.read_text(encoding="utf-8")

    # Handle identical content
    if existing_content == new_content:
        return (False, [])

    # Generate unified diff
    diff = unified_diff(
        existing_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=str(existing_path),
        tofile=str(existing_path),
    )
    return (True, list(diff))
