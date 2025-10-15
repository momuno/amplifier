"""
Repository traversal and tree building.

This module handles scanning the repository structure and building
the synthesis tree hierarchy.
"""

import fnmatch
from pathlib import Path

from amplifier.utils.logger import get_logger

from .hierarchy import SynthesisNode
from .hierarchy import SynthesisTree

logger = get_logger(__name__)

# Default exclusion patterns
DEFAULT_EXCLUDE = [
    "__pycache__",
    "*.pyc",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".idea",
    ".vscode",
    "*.egg-info",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "*.so",
    "*.dylib",
    "*.dll",
    ".DS_Store",
    "Thumbs.db",
    ".env",
    ".env.local",
    # Synthesis tool's own state directories
    ".repo_synthesis",
    ".repo_synthesis_state_*",
    ".repo_synthesis_temp*",
    # Common data directories
    ".data",
    "data",
    "cache",
    "tmp",
    "temp",
]


class TreeBuilder:
    """Build the repository synthesis tree."""

    def __init__(
        self,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        max_depth: int = 10,
    ):
        """
        Initialize the tree builder.

        Args:
            include_patterns: File patterns to include (e.g., ['*.py', '*.md'])
            exclude_patterns: Patterns to exclude (defaults to common ignore patterns)
            max_depth: Maximum directory depth to traverse
        """
        self.include_patterns = include_patterns or ["*"]
        self.exclude_patterns = exclude_patterns or DEFAULT_EXCLUDE
        self.max_depth = max_depth

    def build_tree(self, repo_path: Path) -> SynthesisTree:
        """
        Build the complete synthesis tree for a repository.

        Args:
            repo_path: Root path of the repository

        Returns:
            Complete synthesis tree structure
        """
        repo_path = repo_path.resolve()

        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        if not repo_path.is_dir():
            raise ValueError(f"Path is not a directory: {repo_path}")

        logger.info(f"Building synthesis tree for: {repo_path}")

        # Create root node
        root = SynthesisNode(
            path=repo_path,
            name=repo_path.name,
            type="directory",
            depth=0,
        )

        # Recursively build tree
        self._build_node(root, repo_path, depth=0)

        # Create and return tree
        tree = SynthesisTree(root=root, max_depth=self.max_depth)

        logger.info(f"Tree built: {tree.total_nodes} nodes, {tree.file_count} files, {tree.directory_count} dirs")

        return tree

    def _build_node(self, node: SynthesisNode, path: Path, depth: int) -> None:
        """Recursively build tree nodes."""
        if depth >= self.max_depth:
            logger.debug(f"Max depth {self.max_depth} reached at: {path}")
            return

        try:
            # List directory contents
            items = sorted(path.iterdir())

            for item in items:
                # Check exclusions
                if self._should_exclude(item):
                    logger.debug(f"Excluding: {item}")
                    continue

                if item.is_dir():
                    # Create directory node
                    child = SynthesisNode(
                        path=item,
                        name=item.name,
                        type="directory",
                        depth=depth + 1,
                    )
                    node.add_child(child)

                    # Recurse into directory
                    self._build_node(child, item, depth + 1)

                elif item.is_file():
                    # Check include patterns for files
                    if not self._should_include(item):
                        logger.debug(f"Skipping file: {item}")
                        continue

                    # Create file node
                    child = SynthesisNode(
                        path=item,
                        name=item.name,
                        type="file",
                        depth=depth + 1,
                    )
                    node.add_child(child)

        except PermissionError:
            logger.warning(f"Permission denied: {path}")
            node.error = "Permission denied"
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
            node.error = str(e)

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        name = path.name

        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True

            # Also check against full path for patterns like 'test/*'
            if fnmatch.fnmatch(str(path), pattern):
                return True

        return False

    def _should_include(self, path: Path) -> bool:
        """Check if file should be included."""
        if not path.is_file():
            return True  # Always include directories

        name = path.name

        # If no specific includes, include everything not excluded
        if self.include_patterns == ["*"]:
            return True

        for pattern in self.include_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True

            # Check full path
            if fnmatch.fnmatch(str(path), pattern):
                return True

        return False

    def estimate_processing_time(self, tree: SynthesisTree) -> tuple[int, int]:
        """
        Estimate processing time for the tree.

        Returns:
            Tuple of (min_minutes, max_minutes)
        """
        # Rough estimates: 2-5 seconds per file, 3-8 seconds per directory
        file_time = tree.file_count * 3.5  # Average 3.5 seconds
        dir_time = tree.directory_count * 5.5  # Average 5.5 seconds

        total_seconds = file_time + dir_time

        # Add overhead for API calls and I/O
        overhead = total_seconds * 0.2
        total_seconds += overhead

        # Convert to minutes with range
        min_minutes = int(total_seconds * 0.8 / 60)
        max_minutes = int(total_seconds * 1.2 / 60)

        return (max(1, min_minutes), max(2, max_minutes))
