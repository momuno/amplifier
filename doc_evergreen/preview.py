"""Preview file generation for doc_evergreen."""

from pathlib import Path

from doc_evergreen.generator import generate_doc


def generate_preview(template: str, context: str, target: str, output_dir: Path) -> Path:
    """Generate a preview of the documentation.

    Args:
        template: Template content
        context: Context for generation
        target: Target file path (used for naming preview)
        output_dir: Directory to write preview file

    Returns:
        Path to the generated preview file
    """
    # Generate content using existing generator
    content = generate_doc(template, context)

    # Create preview filename from target basename
    target_path = Path(target)
    preview_filename = f"{target_path.stem}.preview.md"
    preview_path = output_dir / preview_filename

    # Write content to preview file
    preview_path.write_text(content, encoding="utf-8")

    return preview_path
