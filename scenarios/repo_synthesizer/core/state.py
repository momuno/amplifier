"""
State management for repository synthesis.

Handles checkpointing, resume capability, and progress tracking.
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Any

from amplifier.ccsdk_toolkit.defensive.file_io import read_json_with_retry
from amplifier.ccsdk_toolkit.defensive.file_io import write_json_with_retry
from amplifier.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SynthesisState:
    """State of the synthesis process."""

    # Session info
    session_id: str
    repo_path: Path
    topic: str
    started_at: datetime

    # Progress tracking
    total_nodes: int = 0
    processed_nodes: int = 0
    current_phase: str = "initialization"  # initialization, processing, finalizing

    # Output paths
    output_path: Path | None = None
    paper_trail_dir: Path | None = None

    # Configuration
    config: dict[str, Any] = field(default_factory=dict)

    # Errors and warnings
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)

    # Timing
    last_checkpoint: datetime | None = None
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "repo_path": str(self.repo_path),
            "topic": self.topic,
            "started_at": self.started_at.isoformat(),
            "total_nodes": self.total_nodes,
            "processed_nodes": self.processed_nodes,
            "current_phase": self.current_phase,
            "output_path": str(self.output_path) if self.output_path else None,
            "paper_trail_dir": str(self.paper_trail_dir) if self.paper_trail_dir else None,
            "config": self.config,
            "errors": self.errors,
            "warnings": self.warnings,
            "last_checkpoint": self.last_checkpoint.isoformat() if self.last_checkpoint else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SynthesisState":
        """Create state from dictionary."""
        return cls(
            session_id=data["session_id"],
            repo_path=Path(data["repo_path"]),
            topic=data["topic"],
            started_at=datetime.fromisoformat(data["started_at"]),
            total_nodes=data.get("total_nodes", 0),
            processed_nodes=data.get("processed_nodes", 0),
            current_phase=data.get("current_phase", "initialization"),
            output_path=Path(data["output_path"]) if data.get("output_path") else None,
            paper_trail_dir=Path(data["paper_trail_dir"]) if data.get("paper_trail_dir") else None,
            config=data.get("config", {}),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            last_checkpoint=datetime.fromisoformat(data["last_checkpoint"]) if data.get("last_checkpoint") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )


class StateManager:
    """Manage synthesis state and checkpointing."""

    def __init__(self, state_dir: Path):
        """
        Initialize state manager.

        Args:
            state_dir: Directory to store state files
        """
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.state_dir / "state.json"
        self.tree_file = self.state_dir / "tree.json"
        self.backup_dir = self.state_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.state: SynthesisState | None = None
        self.tree = None  # Will be set by orchestrator

    def save_state(self, state: SynthesisState) -> None:
        """Save current state to disk."""
        try:
            # Create backup of existing state
            if self.state_file.exists():
                backup_name = f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.backup_dir / backup_name
                self.state_file.rename(backup_path)

                # Keep only last 5 backups
                self._cleanup_old_backups()

            # Save new state
            state.last_checkpoint = datetime.now()
            write_json_with_retry(state.to_dict(), self.state_file)

            self.state = state
            logger.debug(f"State saved: {state.processed_nodes}/{state.total_nodes} nodes processed")

        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise

    def load_state(self) -> SynthesisState | None:
        """Load state from disk if it exists."""
        if not self.state_file.exists():
            return None

        try:
            data = read_json_with_retry(self.state_file)
            self.state = SynthesisState.from_dict(data)
            logger.info(f"Loaded state for session {self.state.session_id}")
            return self.state

        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None

    def save_tree(self, tree: Any) -> None:
        """Save synthesis tree to disk."""
        try:
            # Create backup
            if self.tree_file.exists():
                backup_name = f"tree_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path = self.backup_dir / backup_name
                self.tree_file.rename(backup_path)

            # Save tree
            write_json_with_retry(tree.to_dict(), self.tree_file)
            self.tree = tree

            logger.debug(f"Tree saved: {tree.processed_nodes}/{tree.total_nodes} nodes")

        except Exception as e:
            logger.error(f"Failed to save tree: {e}")
            raise

    def load_tree(self) -> Any | None:
        """Load synthesis tree from disk."""
        if not self.tree_file.exists():
            return None

        try:
            from .hierarchy import SynthesisTree

            data = read_json_with_retry(self.tree_file)
            tree = SynthesisTree.from_dict(data)
            self.tree = tree

            logger.info(f"Loaded tree: {tree.processed_nodes}/{tree.total_nodes} nodes")
            return tree

        except Exception as e:
            logger.error(f"Failed to load tree: {e}")
            return None

    def checkpoint(self, state: SynthesisState, tree: Any) -> None:
        """Save both state and tree as a checkpoint."""
        logger.debug("Creating checkpoint...")
        self.save_state(state)
        self.save_tree(tree)
        logger.info(f"Checkpoint saved: {state.processed_nodes}/{state.total_nodes} nodes")

    def can_resume(self, session_id: str) -> bool:
        """Check if a session can be resumed."""
        if not self.state_file.exists():
            return False

        try:
            data = read_json_with_retry(self.state_file)
            return data.get("session_id") == session_id and data.get("completed_at") is None

        except Exception:
            return False

    def _cleanup_old_backups(self, keep_count: int = 5) -> None:
        """Keep only the most recent backups."""
        try:
            backups = sorted(self.backup_dir.glob("*.json"))
            if len(backups) > keep_count * 2:  # Keep backups for both state and tree
                for backup in backups[: -keep_count * 2]:
                    backup.unlink()

        except Exception as e:
            logger.warning(f"Failed to cleanup backups: {e}")
