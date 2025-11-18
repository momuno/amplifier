"""
Sprint 3 Deliverable 2: CLI Interface

Click-based CLI for doc-evergreen documentation regeneration.
Integrates template manager, context gathering, preview, diff, and review workflow.
"""

from pathlib import Path

import click

from doc_evergreen.context import gather_context
from doc_evergreen.diff import show_diff
from doc_evergreen.file_ops import accept_changes
from doc_evergreen.file_ops import reject_changes
from doc_evergreen.preview import generate_preview
from doc_evergreen.source_resolver import resolve_sources
from doc_evergreen.source_resolver import validate_sources
from doc_evergreen.template_manager import detect_template
from doc_evergreen.template_manager import list_templates
from doc_evergreen.template_manager import load_template


@click.command("doc-update")
@click.argument("target_file", type=click.Path(), required=False)
@click.option(
    "--template",
    "-t",
    help="Exact template name (use --list-templates to see options). Auto-detects from filename if not specified.",
)
@click.option("--list-templates", "list_templates_flag", is_flag=True, help="List available templates")
@click.option("--no-review", is_flag=True, help="Skip review workflow (auto-apply changes)")
@click.option(
    "--sources",
    "-s",
    help="Comma-separated source files or patterns (overrides defaults)",
)
@click.option(
    "--exclude",
    "-e",
    help="Comma-separated exclusion patterns",
)
@click.option(
    "--add-sources",
    "-a",
    help="Additional sources to merge with defaults",
)
@click.option(
    "--show-sources",
    is_flag=True,
    help="Preview sources without generating documentation",
)
def doc_update(target_file, template, list_templates_flag, no_review, sources, exclude, add_sources, show_sources):
    """Regenerate documentation file using template and source context.

    \b
    Examples:
      # List available templates
      doc-update --list-templates

      # Auto-detect template from filename
      doc-update README.md

      # Specify exact template name
      doc-update docs/API.md --template api-reference

      # Auto-apply without review prompt
      doc-update README.md --no-review

      # Override source files
      doc-update README.md --sources "src/*.py,docs/*.md"

      # Add sources to defaults
      doc-update README.md --add-sources "config/*.yaml"

      # Exclude patterns
      doc-update README.md --exclude "test_*,*.pyc"

      # Preview sources without generating
      doc-update --show-sources
    """
    # Default template directory - check for .templates/ in current directory first
    template_dir = Path(".templates") if Path(".templates").exists() else Path(__file__).parent / "templates"

    # 1. Handle --list-templates flag
    if list_templates_flag:
        templates = list_templates(template_dir)
        for t in templates:
            click.echo(t)
        return

    # Handle --show-sources flag
    if show_sources:
        base_dir = Path.cwd()
        exclusions = exclude.split(",") if exclude else None

        # Resolve sources using source resolver (includes exclusion handling)
        resolved = resolve_sources(
            cli_sources=sources, add_sources=add_sources, base_dir=base_dir, exclusions=exclusions
        )

        # Validate sources
        validated = validate_sources(resolved)

        # Display sources with sizes
        click.echo(f"Sources for {target_file or 'documentation'}:")
        total_size = 0
        for source_path in validated:
            try:
                size = Path(source_path).stat().st_size
                total_size += size
                size_kb = size / 1024
                click.echo(f"  ✓ {source_path} ({size_kb:.1f} KB)")
            except Exception:
                click.echo(f"  ✓ {source_path}")

        # Display summary
        count = len(validated)
        if total_size > 0:
            total_kb = total_size / 1024
            click.echo(f"\nTotal: {count} sources ({total_kb:.1f} KB)")
        else:
            click.echo(f"\nTotal: {count} sources")
        return

    # 2. Require target_file if not listing templates
    if not target_file:
        raise click.UsageError("Missing argument 'TARGET_FILE'.")

    # 3. Detect or validate template
    if not template:
        template = detect_template(target_file)

    # 4. Load template
    try:
        template_content = load_template(template, template_dir=template_dir)
    except FileNotFoundError:
        available = list_templates(template_dir)
        click.echo(f"Error: Template '{template}' not found", err=True)
        if available:
            click.echo(f"Available templates: {', '.join(available)}", err=True)
        raise SystemExit(1)

    # 5. Resolve sources
    base_dir = Path.cwd()
    exclusions = exclude.split(",") if exclude else None

    # Resolve sources using source resolver (includes exclusion handling)
    resolved = resolve_sources(cli_sources=sources, add_sources=add_sources, base_dir=base_dir, exclusions=exclusions)

    # Validate sources
    validated = validate_sources(resolved)

    # Convert to Path objects for gather_context
    source_paths = [Path(s) for s in validated]

    # 6. Gather context
    context = gather_context(sources=source_paths)

    # 7. Generate preview
    preview_path = generate_preview(template_content, context, target_file, Path("."))

    # 8. Show diff if target exists, otherwise show warning
    target_path = Path(target_file)
    if target_path.exists():
        show_diff(str(target_path), str(preview_path))
    else:
        click.echo(f"Warning: {target_file} doesn't exist - this will create a new file")

    # 9. Review or auto-accept
    if no_review:
        accept_changes(target_path, preview_path)
        click.echo(f"✅ Accepted: {target_file} updated")
    else:
        if click.confirm("Accept changes?"):
            accept_changes(target_path, preview_path)
            click.echo(f"✅ Accepted: {target_file} updated")
        else:
            reject_changes(preview_path)
            click.echo(f"❌ Rejected: {target_file} unchanged")


if __name__ == "__main__":
    doc_update()
