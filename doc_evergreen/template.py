"""Template loading functionality for doc-evergreen"""

from pathlib import Path


def load_template(path: str) -> str:
    """Load template content from file.

    Args:
        path: Path to template file

    Returns:
        Template content as string

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    template_path = Path(path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")

    return template_path.read_text(encoding="utf-8")
