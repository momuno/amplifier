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
def doc_update(target_file, template, list_templates_flag, no_review):
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
    """
    # Default template directory - check for .templates/ in current directory first
    template_dir = Path(".templates") if Path(".templates").exists() else Path(__file__).parent / "templates"

    # 1. Handle --list-templates flag
    if list_templates_flag:
        templates = list_templates(template_dir)
        for t in templates:
            click.echo(t)
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

    # 5. Gather context
    context = gather_context()

    # 6. Generate preview
    preview_path = generate_preview(template_content, context, target_file, Path("."))

    # 7. Show diff if target exists, otherwise show warning
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
