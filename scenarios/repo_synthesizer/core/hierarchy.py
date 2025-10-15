"""
Hierarchical data structures for repository synthesis.

This module defines the tree structure used to represent a repository
and track synthesis progress at each level.
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SynthesisNode:
    """A single node in the repository synthesis tree."""

    path: Path
    name: str
    type: str  # 'file' or 'directory'
    depth: int

    # Content and synthesis
    content: str | None = None  # File content or directory listing
    synthesis: str | None = None  # AI-generated synthesis
    key_insights: list[str] = field(default_factory=list)

    # Hierarchy
    parent: "SynthesisNode | None" = None
    children: list["SynthesisNode"] = field(default_factory=list)

    # Processing state
    processed: bool = False
    error: str | None = None
    processed_at: datetime | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_file(self) -> bool:
        """Check if this node represents a file."""
        return self.type == "file"

    def is_directory(self) -> bool:
        """Check if this node represents a directory."""
        return self.type == "directory"

    def add_child(self, child: "SynthesisNode") -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)

    def get_siblings(self) -> list["SynthesisNode"]:
        """Get sibling nodes at the same level."""
        if not self.parent:
            return []
        return [c for c in self.parent.children if c != self]

    def get_ancestors(self) -> list["SynthesisNode"]:
        """Get all ancestor nodes up to root."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self) -> list["SynthesisNode"]:
        """Get all descendant nodes recursively."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for serialization."""
        return {
            "path": str(self.path),
            "name": self.name,
            "type": self.type,
            "depth": self.depth,
            "content": self.content[:1000] if self.content else None,  # Truncate for storage
            "synthesis": self.synthesis,
            "key_insights": self.key_insights,
            "processed": self.processed,
            "error": self.error,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "metadata": self.metadata,
            "children_paths": [str(c.path) for c in self.children],
        }


@dataclass
class SynthesisTree:
    """The complete repository synthesis tree structure."""

    root: SynthesisNode
    max_depth: int = 10

    # Statistics
    total_nodes: int = 0
    processed_nodes: int = 0
    file_count: int = 0
    directory_count: int = 0

    # Lookup tables for fast access
    _node_map: dict[Path, SynthesisNode] = field(default_factory=dict)
    _depth_map: dict[int, list[SynthesisNode]] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize lookup tables after creation."""
        self._rebuild_indices()

    def _rebuild_indices(self) -> None:
        """Rebuild internal lookup tables."""
        self._node_map.clear()
        self._depth_map.clear()
        self.total_nodes = 0
        self.file_count = 0
        self.directory_count = 0

        # Traverse tree and build indices
        def traverse(node: SynthesisNode):
            self._node_map[node.path] = node

            if node.depth not in self._depth_map:
                self._depth_map[node.depth] = []
            self._depth_map[node.depth].append(node)

            self.total_nodes += 1
            if node.is_file():
                self.file_count += 1
            else:
                self.directory_count += 1

            for child in node.children:
                traverse(child)

        traverse(self.root)
        self.processed_nodes = sum(1 for n in self._node_map.values() if n.processed)

    def get_node(self, path: Path) -> SynthesisNode | None:
        """Get a node by its path."""
        return self._node_map.get(path)

    def get_nodes_at_depth(self, depth: int) -> list[SynthesisNode]:
        """Get all nodes at a specific depth level."""
        return self._depth_map.get(depth, [])

    def get_deepest_nodes(self) -> list[SynthesisNode]:
        """Get all nodes at the deepest level."""
        if not self._depth_map:
            return []
        max_depth = max(self._depth_map.keys())
        return self._depth_map[max_depth]

    def get_unprocessed_nodes(self) -> list[SynthesisNode]:
        """Get all unprocessed nodes."""
        return [n for n in self._node_map.values() if not n.processed]

    def get_next_batch(self) -> list[SynthesisNode]:
        """Get the next batch of nodes to process (bottom-up)."""
        # Start from deepest level and work up
        for depth in sorted(self._depth_map.keys(), reverse=True):
            nodes = self._depth_map[depth]
            unprocessed = [n for n in nodes if not n.processed]

            # Check if all children are processed for directories
            ready_nodes = []
            for node in unprocessed:
                if node.is_file() or all(c.processed for c in node.children):
                    ready_nodes.append(node)

            if ready_nodes:
                return ready_nodes

        return []

    def mark_processed(self, node: SynthesisNode) -> None:
        """Mark a node as processed and update statistics."""
        node.processed = True
        node.processed_at = datetime.now()
        self.processed_nodes += 1

    def get_progress(self) -> float:
        """Get processing progress as a percentage."""
        if self.total_nodes == 0:
            return 0.0
        return (self.processed_nodes / self.total_nodes) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert tree to dictionary for serialization."""
        return {
            "root": self.root.to_dict(),
            "max_depth": self.max_depth,
            "total_nodes": self.total_nodes,
            "processed_nodes": self.processed_nodes,
            "file_count": self.file_count,
            "directory_count": self.directory_count,
            "all_nodes": {str(p): n.to_dict() for p, n in self._node_map.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SynthesisTree":
        """Reconstruct tree from dictionary."""
        # First create all nodes
        nodes = {}
        for path_str, node_data in data["all_nodes"].items():
            path = Path(path_str)
            node = SynthesisNode(
                path=path,
                name=node_data["name"],
                type=node_data["type"],
                depth=node_data["depth"],
                content=node_data.get("content"),
                synthesis=node_data.get("synthesis"),
                key_insights=node_data.get("key_insights", []),
                processed=node_data.get("processed", False),
                error=node_data.get("error"),
                processed_at=datetime.fromisoformat(node_data["processed_at"])
                if node_data.get("processed_at")
                else None,
                metadata=node_data.get("metadata", {}),
            )
            nodes[path] = node

        # Rebuild hierarchy
        root_path = Path(data["root"]["path"])
        root = nodes[root_path]

        for path_str, node_data in data["all_nodes"].items():
            path = Path(path_str)
            node = nodes[path]

            # Reconnect children
            for child_path_str in node_data.get("children_paths", []):
                child_path = Path(child_path_str)
                if child_path in nodes:
                    node.add_child(nodes[child_path])

        # Create tree
        tree = cls(root=root, max_depth=data["max_depth"])
        tree._rebuild_indices()

        return tree
