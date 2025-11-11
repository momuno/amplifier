"""File tree utilities for doc-studio."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from doc_studio.models import FileNode
from doc_studio.models import FileType


def should_ignore(path: Path, ignore_patterns: list[str]) -> bool:
    """Check if a path should be ignored based on patterns.

    Args:
        path: Path to check
        ignore_patterns: List of glob patterns to ignore

    Returns:
        True if path should be ignored
    """
    path_str = str(path)
    name = path.name

    for pattern in ignore_patterns:
        # Match against both full path and just the name
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(name, pattern):
            return True
        # Also check if any parent directory matches
        if fnmatch.fnmatch(f"*/{name}", pattern) or fnmatch.fnmatch(f"*/{name}/*", pattern):
            return True

    return False


def load_gitignore_patterns(workspace: Path) -> list[str]:
    """Load ignore patterns from .gitignore file.

    Args:
        workspace: Workspace directory path

    Returns:
        List of ignore patterns
    """
    patterns = [
        # Default ignore patterns
        ".git",
        ".git/*",
        "__pycache__",
        "*.pyc",
        ".venv",
        "venv",
        "node_modules",
        ".DS_Store",
        "*.egg-info",
    ]

    gitignore_path = workspace / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    patterns.append(line)

    return patterns


def build_file_tree(
    workspace: Path,
    included_files: set[str] | None = None,
    max_depth: int = 10,
) -> FileNode:
    """Build a file tree structure from a workspace directory.

    Args:
        workspace: Root workspace directory
        included_files: Set of file paths that are included in template
        max_depth: Maximum depth to traverse

    Returns:
        FileNode representing the root of the tree
    """
    if included_files is None:
        included_files = set()

    # Load ignore patterns
    ignore_patterns = load_gitignore_patterns(workspace)

    def build_node(path: Path, depth: int = 0) -> FileNode | None:
        """Recursively build file tree nodes.

        Args:
            path: Path to build node for
            depth: Current depth in tree

        Returns:
            FileNode or None if should be ignored
        """
        # Check depth limit
        if depth > max_depth:
            return None

        # Check if should be ignored
        relative_path = path.relative_to(workspace)
        if should_ignore(relative_path, ignore_patterns):
            return None

        # Determine if this path is included in template
        path_str = str(relative_path)
        is_included = path_str in included_files

        if path.is_file():
            return FileNode(
                path=path_str,
                name=path.name,
                type=FileType.FILE,
                is_included=is_included,
            )

        # It's a directory
        children = []
        try:
            for child_path in sorted(path.iterdir()):
                child_node = build_node(child_path, depth + 1)
                if child_node is not None:
                    children.append(child_node)
        except PermissionError:
            # Skip directories we can't read
            pass

        return FileNode(
            path=path_str if path != workspace else ".",
            name=path.name if path != workspace else workspace.name,
            type=FileType.DIRECTORY,
            children=children,
            is_included=is_included,
        )

    root_node = build_node(workspace)
    if root_node is None:
        # Fallback to empty root
        return FileNode(
            path=".",
            name=workspace.name,
            type=FileType.DIRECTORY,
            children=[],
        )

    return root_node
