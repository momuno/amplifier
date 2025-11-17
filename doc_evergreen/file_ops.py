"""File operations for doc_evergreen Sprint 2 review workflow."""

import shutil
from pathlib import Path


def accept_changes(original: Path, preview: Path) -> None:
    """Accept changes by replacing original with preview.

    Args:
        original: Path to original file
        preview: Path to preview file

    The preview file is copied to original (preserving metadata)
    and then the preview is deleted.
    """
    shutil.copy2(preview, original)
    preview.unlink()


def reject_changes(preview: Path) -> None:
    """Reject changes by deleting preview file.

    Args:
        preview: Path to preview file

    The original file is left unchanged. Silently succeeds
    if preview doesn't exist.
    """
    preview.unlink(missing_ok=True)
