"""Coordinate launching all variants and tracking their lifecycle."""

import logging
import uuid
from pathlib import Path
from typing import Any

from .progress_tracker import initialize_tracking
from .progress_tracker import update_variant_status
from .terminal_spawner import spawn_terminal
from .variant_generator import generate_variants_sync
from .worktree_manager import create_worktree

logger = logging.getLogger(__name__)


def orchestrate_session(
    idea: str,
    num_variants: int = 3,
    auto_execute: bool = True,
    variant_style: str = "exploratory",
    base_branch: str = "main",
) -> dict[str, Any]:
    """
    Orchestrate the creation and launching of all variants.

    Args:
        idea: Original idea to explore
        num_variants: Number of variants to create (default 3)
        auto_execute: Whether to auto-start execution (default True)
        variant_style: Style of variants - "exploratory", "focused", or "creative"
        base_branch: Git branch to base worktrees on (default "main")

    Returns:
        Dictionary with session_id, variants list, and status_file path

    Raises:
        RuntimeError: If orchestration fails
    """
    session_id = str(uuid.uuid4())[:8]
    logger.info(f"Starting ideation session {session_id} for idea: {idea[:50]}...")

    try:
        # Generate variants
        logger.info(f"Generating {num_variants} {variant_style} variants...")
        variants = generate_variants_sync(idea, num_variants, variant_style)

        if not variants:
            raise RuntimeError("Failed to generate any variants")

        logger.info(f"Generated {len(variants)} variants")

        # Process each variant
        successful_variants = []
        failed_variants = []

        for i, variant in enumerate(variants):
            logger.info(f"Processing variant {i + 1}/{len(variants)}: {variant['title']}")

            try:
                # Create worktree for this variant
                logger.info(f"Creating worktree for variant {variant['id']}")
                worktree_result = create_worktree(variant["id"], base_branch)

                variant["worktree_path"] = worktree_result["worktree_path"]
                variant["branch_name"] = worktree_result["branch_name"]

                # Spawn terminal for this variant
                logger.info(f"Spawning terminal for variant {variant['id']}")
                terminal_result = spawn_terminal(variant, worktree_result["worktree_path"], auto_execute)

                variant["tab_id"] = terminal_result["tab_id"]
                variant["pid"] = terminal_result["pid"]
                variant["launch_time"] = terminal_result["launch_time"]

                successful_variants.append(variant)
                logger.info(f"Successfully launched variant {variant['id']}")

            except Exception as e:
                logger.error(f"Failed to launch variant {variant['id']}: {e}")
                variant["error"] = str(e)
                failed_variants.append(variant)

        # Initialize progress tracking with all variants
        all_variants = successful_variants + failed_variants
        status_file = initialize_tracking(session_id, all_variants)

        # Update status for failed variants
        for variant in failed_variants:
            update_variant_status(
                status_file, variant["id"], "failed", {"error": variant.get("error", "Unknown error")}
            )

        # Update status for successful variants to running
        for variant in successful_variants:
            update_variant_status(status_file, variant["id"], "running")

        # Create session summary
        summary = {
            "session_id": session_id,
            "variants": all_variants,
            "status_file": str(status_file),
            "successful": len(successful_variants),
            "failed": len(failed_variants),
            "total": len(all_variants),
        }

        # Log summary
        logger.info(f"Session {session_id} orchestration complete:")
        logger.info(f"  - Total variants: {summary['total']}")
        logger.info(f"  - Successful launches: {summary['successful']}")
        logger.info(f"  - Failed launches: {summary['failed']}")
        logger.info(f"  - Status tracking: {status_file}")

        if successful_variants:
            logger.info("\nVariants are now running in separate terminals:")
            for v in successful_variants:
                logger.info(f"  - {v['title']} (ID: {v['id']})")
                logger.info(f"    Branch: {v['branch_name']}")
                logger.info(f"    Worktree: {v['worktree_path']}")

        return summary

    except Exception as e:
        error_msg = f"Session orchestration failed: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def cleanup_session(session_id: str, status_dir: Path | None = None) -> None:
    """
    Clean up all resources for a session.

    Args:
        session_id: Session ID to clean up
        status_dir: Directory containing status files

    Note:
        This function removes worktrees and branches but does NOT
        close terminal windows (they should be closed manually).
    """
    if status_dir is None:
        status_dir = Path.home() / ".amplifier" / "ideation_status"

    status_file = status_dir / f"{session_id}.json"

    if not status_file.exists():
        logger.warning(f"Status file not found for session {session_id}")
        return

    try:
        # Import here to avoid circular dependency
        from .progress_tracker import get_session_status
        from .worktree_manager import cleanup_worktree

        status_data = get_session_status(status_file)

        logger.info(f"Cleaning up session {session_id}")

        # Clean up each variant's worktree
        for variant in status_data.get("variants", []):
            worktree_path = variant.get("worktree")
            if worktree_path and Path(worktree_path).exists():
                try:
                    logger.info(f"Removing worktree: {worktree_path}")
                    cleanup_worktree(Path(worktree_path))
                except Exception as e:
                    logger.error(f"Failed to clean up worktree {worktree_path}: {e}")

        # Remove status file
        status_file.unlink(missing_ok=True)
        logger.info(f"Removed status file: {status_file}")

        logger.info(f"Session {session_id} cleanup complete")

    except Exception as e:
        logger.error(f"Failed to clean up session {session_id}: {e}")
