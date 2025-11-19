"""
Sprint 5: CLI Interface for Template-Based Documentation Generation

Supports both single-shot and chunked generation modes with section-level prompts.
"""

import asyncio
from pathlib import Path

import click

from doc_evergreen.chunked_generator import ChunkedGenerator
from doc_evergreen.core.template_schema import parse_template
from doc_evergreen.core.template_schema import validate_template

# Import Generator for single-shot mode (fallback to ChunkedGenerator if not available)
try:
    from doc_evergreen.single_generator import Generator
except ImportError:
    Generator = ChunkedGenerator  # type: ignore[misc,assignment]


@click.command("doc-update")
@click.argument("template_path", type=click.Path(exists=True))
@click.option(
    "--mode",
    type=click.Choice(["single", "chunked"]),
    default="single",
    help="Generation mode: single-shot or section-by-section",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Override output path from template",
)
def doc_update(template_path: str, mode: str, output: str | None):
    """Generate/update documentation from JSON template.

    \b
    Examples:
      # Generate using single-shot mode (default)
      doc-update template.json

      # Generate using chunked mode (section-by-section)
      doc-update --mode chunked template.json

      # Override output path
      doc-update --output custom.md template.json
    """
    # 1. Parse template
    try:
        template = parse_template(Path(template_path))
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    # 2. Validate template based on mode
    validation = validate_template(template, mode=mode)
    if not validation.valid:
        click.echo(f"Error: {validation.errors[0]}", err=True)
        raise click.Abort()

    # 3. Determine base_dir (parent of template file)
    base_dir = Path(template_path).parent

    # 4. Route to appropriate generator
    if mode == "chunked":
        generator = ChunkedGenerator(template, base_dir)
    else:
        # Use single-shot Generator
        generator = Generator(template, base_dir)

    # 5. Generate documentation (async)
    try:
        result = asyncio.run(generator.generate())
    except Exception as e:
        click.echo(f"Generation failed: {e}", err=True)
        raise click.Abort()

    # 6. Determine output path
    output_path = Path(output) if output else Path(template.document.output)

    # 7. Check if output exists and prompt for confirmation
    if output_path.exists() and not click.confirm(f"Overwrite {output_path}?"):
        click.echo("Aborted")
        return

    # 8. Write output
    output_path.write_text(result)
    click.echo(f"Generated: {output_path}")


if __name__ == "__main__":
    doc_update()
