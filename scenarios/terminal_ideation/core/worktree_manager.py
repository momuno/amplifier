"""Manage git worktrees for isolated variant execution."""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def create_worktree(
    variant_id: str, base_branch: str = "main", worktree_base_dir: Path | None = None
) -> dict[str, Any]:
    """
    Create a git worktree for isolated variant execution.

    Args:
        variant_id: Unique identifier for the variant
        base_branch: Branch to create worktree from (default "main")
        worktree_base_dir: Base directory for worktrees (default ~/.amplifier/worktrees)

    Returns:
        Dictionary with worktree_path, branch_name, and created status

    Raises:
        RuntimeError: If git operations fail
    """
    if worktree_base_dir is None:
        worktree_base_dir = Path.home() / ".amplifier" / "worktrees"

    # Create base directory if it doesn't exist
    worktree_base_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique branch name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = f"ideation/variant-{variant_id}-{timestamp}"
    worktree_path = worktree_base_dir / branch_name.replace("/", "_")

    try:
        # Get the repository root
        repo_root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        )
        repo_root = repo_root_result.stdout.strip()

        # Check if worktree already exists
        list_result = subprocess.run(
            ["git", "worktree", "list"], cwd=repo_root, capture_output=True, text=True, check=True
        )

        if str(worktree_path) in list_result.stdout:
            logger.warning(f"Worktree already exists at {worktree_path}")
            return {"worktree_path": worktree_path, "branch_name": branch_name, "created": False}

        # Create new branch and worktree
        logger.info(f"Creating worktree at {worktree_path} with branch {branch_name}")

        # Create the worktree with new branch
        subprocess.run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_branch],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )

        # Copy .env file if it exists
        env_file = Path(repo_root) / ".env"
        if env_file.exists():
            target_env = worktree_path / ".env"
            target_env.write_text(env_file.read_text())
            logger.info("Copied .env file to worktree")

        # Install dependencies in the worktree
        if (worktree_path / "pyproject.toml").exists():
            logger.info("Installing dependencies in worktree")
            subprocess.run(
                ["uv", "sync"],
                cwd=worktree_path,
                capture_output=True,
                text=True,
                check=False,  # Don't fail if dependencies can't be installed
            )

        logger.info(f"Successfully created worktree at {worktree_path}")
        return {"worktree_path": worktree_path, "branch_name": branch_name, "created": True}

    except subprocess.CalledProcessError as e:
        error_msg = f"Git operation failed: {e.stderr if e.stderr else str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Failed to create worktree: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def cleanup_worktree(worktree_path: Path, delete_branch: bool = True) -> None:
    """
    Remove a git worktree and optionally delete its branch.

    Args:
        worktree_path: Path to the worktree to remove
        delete_branch: Whether to delete the associated branch (default True)

    Raises:
        RuntimeError: If cleanup fails
    """
    try:
        # Get the repository root
        repo_root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        )
        repo_root = repo_root_result.stdout.strip()

        # Get branch name before removing worktree
        branch_name = None
        if delete_branch:
            list_result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"], cwd=repo_root, capture_output=True, text=True, check=True
            )

            # Parse worktree list to find branch
            lines = list_result.stdout.strip().split("\n")
            for i, line in enumerate(lines):
                if line.startswith("worktree") and str(worktree_path) in line:
                    # Branch info is typically on the next line
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if lines[j].startswith("branch"):
                            branch_name = lines[j].split()[-1]
                            break

        # Remove the worktree
        logger.info(f"Removing worktree at {worktree_path}")
        subprocess.run(
            ["git", "worktree", "remove", str(worktree_path), "--force"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )

        # Delete the branch if requested
        if delete_branch and branch_name:
            logger.info(f"Deleting branch {branch_name}")
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,  # Don't fail if branch doesn't exist
            )

        logger.info(f"Successfully cleaned up worktree at {worktree_path}")

    except subprocess.CalledProcessError as e:
        error_msg = f"Cleanup failed: {e.stderr if e.stderr else str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Failed to cleanup worktree: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def list_worktrees() -> list[dict[str, str]]:
    """
    List all git worktrees in the current repository.

    Returns:
        List of dictionaries with worktree information
    """
    try:
        result = subprocess.run(["git", "worktree", "list", "--porcelain"], capture_output=True, text=True, check=True)

        worktrees = []
        current = {}
        for line in result.stdout.strip().split("\n"):
            if line.startswith("worktree"):
                if current:
                    worktrees.append(current)
                current = {"path": line.split(maxsplit=1)[1]}
            elif line.startswith("HEAD"):
                current["head"] = line.split(maxsplit=1)[1]
            elif line.startswith("branch"):
                current["branch"] = line.split(maxsplit=1)[1]
            elif line.startswith("detached"):
                current["detached"] = True

        if current:
            worktrees.append(current)

        return worktrees

    except subprocess.CalledProcessError:
        return []
