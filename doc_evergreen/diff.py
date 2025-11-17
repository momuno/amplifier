"""Diff display module for doc_evergreen Sprint 2.

Provides unified diff output between original and preview versions.
"""

import difflib
from pathlib import Path


def show_diff(original_path: str, preview_path: str) -> None:
    """Display unified diff between two files.

    Args:
        original_path: Path to original file
        preview_path: Path to preview file

    Prints:
        - Unified diff output with +/- markers
        - Line number ranges with @@ markers
        - Summary with added/removed line counts
        - "Files are identical" message if no changes
    """
    # Read files
    original_content = Path(original_path).read_text()
    preview_content = Path(preview_path).read_text()

    # Split into lines
    original_lines = original_content.splitlines(keepends=True)
    preview_lines = preview_content.splitlines(keepends=True)

    # Generate unified diff
    diff = list(
        difflib.unified_diff(
            original_lines,
            preview_lines,
            fromfile=original_path,
            tofile=preview_path,
            lineterm="",
        )
    )

    # Check if files are identical
    if not diff:
        print("Files are identical")
        return

    # Track counts
    added = 0
    removed = 0

    # Print diff with simple colorization
    for line in diff:
        if line.startswith("+++") or line.startswith("---"):
            # Skip file headers
            continue
        if line.startswith("+"):
            print(f"\033[32m{line}\033[0m")  # Green
            added += 1
        elif line.startswith("-"):
            print(f"\033[31m{line}\033[0m")  # Red
            removed += 1
        elif line.startswith("@@"):
            print(f"\033[34m{line}\033[0m")  # Blue
        else:
            print(line)

    # Print summary
    print(f"\n{added} lines added, {removed} lines removed")
