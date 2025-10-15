"""Track and report progress of all variant executions via filesystem."""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def initialize_tracking(session_id: str, variants: list[dict[str, Any]], status_dir: Path | None = None) -> Path:
    """
    Initialize progress tracking for a session.

    Args:
        session_id: Unique session identifier
        variants: List of variant information dictionaries
        status_dir: Directory for status files (default ~/.amplifier/ideation_status)

    Returns:
        Path to the status JSON file

    Raises:
        IOError: If status file cannot be created
    """
    if status_dir is None:
        status_dir = Path.home() / ".amplifier" / "ideation_status"

    # Create status directory if it doesn't exist
    status_dir.mkdir(parents=True, exist_ok=True)

    # Create status file path
    status_file = status_dir / f"{session_id}.json"

    # Initialize status data
    status_data = {
        "session_id": session_id,
        "created": datetime.now().isoformat(),
        "idea": variants[0].get("prompt", "").split("\n")[0] if variants else "Unknown",
        "variants": [],
    }

    # Add each variant with initial status
    for variant in variants:
        variant_status = {
            "id": variant["id"],
            "title": variant["title"],
            "status": "pending",
            "worktree": str(variant.get("worktree_path", "")),
            "terminal_pid": variant.get("pid", 0),
            "last_update": datetime.now().isoformat(),
            "approach": variant.get("approach", ""),
            "color": variant.get("color", "#FFFFFF"),
        }
        status_data["variants"].append(variant_status)

    # Write status file with retry logic
    _write_status_with_retry(status_file, status_data)

    logger.info(f"Initialized tracking for session {session_id} at {status_file}")
    return status_file


def update_variant_status(
    status_file: Path, variant_id: str, status: str, details: dict[str, Any] | None = None
) -> None:
    """
    Update the status of a specific variant.

    Args:
        status_file: Path to the status JSON file
        variant_id: ID of the variant to update
        status: New status (pending/running/completed/failed)
        details: Additional details to merge into variant status

    Raises:
        IOError: If status file cannot be updated
    """
    try:
        # Read current status
        status_data = _read_status_with_retry(status_file)

        # Find and update the variant
        variant_found = False
        for variant in status_data["variants"]:
            if variant["id"] == variant_id:
                variant["status"] = status
                variant["last_update"] = datetime.now().isoformat()
                if details:
                    variant.update(details)
                variant_found = True
                break

        if not variant_found:
            logger.warning(f"Variant {variant_id} not found in status file")
            return

        # Write updated status
        _write_status_with_retry(status_file, status_data)

        logger.info(f"Updated variant {variant_id} status to {status}")

    except Exception as e:
        logger.error(f"Failed to update variant status: {e}")
        raise OSError(f"Could not update status file: {e}")


def get_session_status(status_file: Path) -> dict[str, Any]:
    """
    Read the current status of all variants in a session.

    Args:
        status_file: Path to the status JSON file

    Returns:
        Dictionary with session status information

    Raises:
        IOError: If status file cannot be read
    """
    try:
        return _read_status_with_retry(status_file)
    except Exception as e:
        logger.error(f"Failed to read session status: {e}")
        raise OSError(f"Could not read status file: {e}")


def get_all_sessions(status_dir: Path | None = None) -> list[dict[str, Any]]:
    """
    Get a list of all tracked sessions.

    Args:
        status_dir: Directory containing status files

    Returns:
        List of session summaries
    """
    if status_dir is None:
        status_dir = Path.home() / ".amplifier" / "ideation_status"

    if not status_dir.exists():
        return []

    sessions = []
    for status_file in status_dir.glob("*.json"):
        try:
            status_data = _read_status_with_retry(status_file)
            # Create summary
            completed = sum(1 for v in status_data["variants"] if v["status"] == "completed")
            failed = sum(1 for v in status_data["variants"] if v["status"] == "failed")
            running = sum(1 for v in status_data["variants"] if v["status"] == "running")
            total = len(status_data["variants"])

            sessions.append(
                {
                    "session_id": status_data["session_id"],
                    "created": status_data["created"],
                    "idea": status_data.get("idea", "Unknown"),
                    "total_variants": total,
                    "completed": completed,
                    "failed": failed,
                    "running": running,
                    "status_file": str(status_file),
                }
            )
        except Exception as e:
            logger.warning(f"Could not read status file {status_file}: {e}")

    # Sort by creation time (newest first)
    sessions.sort(key=lambda x: x["created"], reverse=True)
    return sessions


def _write_status_with_retry(file_path: Path, data: dict[str, Any], max_retries: int = 3) -> None:
    """
    Write status data to file with retry logic for cloud-synced directories.

    Args:
        file_path: Path to write to
        data: Data to write as JSON
        max_retries: Maximum number of retry attempts
    """
    retry_delay = 0.5

    for attempt in range(max_retries):
        try:
            # Write to temporary file first (atomic write)
            temp_file = file_path.with_suffix(".tmp")
            temp_file.write_text(json.dumps(data, indent=2))

            # Move to final location (atomic on most filesystems)
            temp_file.replace(file_path)
            return

        except OSError as e:
            if e.errno == 5 and attempt < max_retries - 1:
                # I/O error - likely cloud sync issue
                if attempt == 0:
                    logger.warning(
                        f"File I/O error writing to {file_path} - retrying. "
                        "This may be due to cloud-synced files (OneDrive, Dropbox, etc.)."
                    )
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise


def _read_status_with_retry(file_path: Path, max_retries: int = 3) -> dict[str, Any]:
    """
    Read status data from file with retry logic for cloud-synced directories.

    Args:
        file_path: Path to read from
        max_retries: Maximum number of retry attempts

    Returns:
        Parsed JSON data
    """
    retry_delay = 0.5

    for attempt in range(max_retries):
        try:
            return json.loads(file_path.read_text())
        except OSError as e:
            if e.errno == 5 and attempt < max_retries - 1:
                # I/O error - likely cloud sync issue
                if attempt == 0:
                    logger.warning(
                        f"File I/O error reading {file_path} - retrying. This may be due to cloud-synced files."
                    )
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in status file {file_path}: {e}")
            raise
