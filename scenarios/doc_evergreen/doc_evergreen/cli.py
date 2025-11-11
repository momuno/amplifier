"""
doc-evergreen CLI

Automatic documentation generation and maintenance tool.
"""

import sys
from pathlib import Path

import click


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """
    doc-evergreen - Automatic documentation generation and maintenance.

    Generate and maintain documentation from source code and configuration files.
    Uses LLM intelligence for discovery and generation with deterministic execution
    for automation.

    \b
    Examples:
      # Create new documentation
      doc-evergreen create --about "API reference" --output docs/API.md

      # Regenerate from saved configuration
      doc-evergreen regenerate README.md

      # Regenerate all configured documents
      doc-evergreen regenerate --all
    """
    # This is a Click command group - the function body is not executed
    # All functionality is in the subcommands (create, regenerate)
    return None


@cli.command()
@click.option(
    "--about",
    required=True,
    help="Description of what the documentation should cover (e.g., 'API reference for knowledge synthesis')",
)
@click.option(
    "--output",
    required=True,
    type=click.Path(path_type=Path),
    help="Full path where the document should be saved (e.g., 'docs/API_REFERENCE.md')",
)
@click.option(
    "--sources",
    multiple=True,
    help="Glob patterns for files to include (e.g., 'src/**/*.py'). Can be specified multiple times. If not provided, files will be auto-discovered.",
)
@click.option(
    "--template",
    help="Specific template to use (e.g., 'readme', 'api-reference'). If not provided, template will be auto-selected based on --about.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be generated without writing files",
)
def create(
    about: str,
    output: Path,
    sources: tuple[str, ...],
    template: str | None,
    dry_run: bool,
) -> None:
    """
    Create new documentation from scratch.

    This command generates documentation by:
    1. Discovering or using specified source files
    2. Selecting or creating an appropriate template
    3. Generating the documentation via LLM
    4. Saving the result and configuration for future regeneration

    \b
    Required Parameters:
      --about   What the documentation should cover
      --output  Where to save the generated document

    \b
    Optional Parameters:
      --sources    Files to include (auto-discovered if not provided)
      --template   Template to use (auto-selected if not provided)
      --dry-run    Preview without writing files

    \b
    Examples:
      # Create with specific sources
      doc-evergreen create \\
          --about "API reference for knowledge synthesis" \\
          --output "docs/API_REFERENCE.md" \\
          --sources "src/knowledge_synthesis/**/*.py"

      # Create with auto-discovery
      doc-evergreen create \\
          --about "Contributing guide" \\
          --output "docs/CONTRIBUTING.md"

      # Preview without writing
      doc-evergreen create \\
          --about "User guide" \\
          --output "docs/USER_GUIDE.md" \\
          --dry-run
    """
    from doc_evergreen.commands.create import execute_create

    try:
        # Convert sources tuple to list
        sources_list = list(sources) if sources else None

        execute_create(
            about=about,
            output=output,
            sources=sources_list,
            template=template,
            dry_run=dry_run,
        )
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("doc_path", required=False, type=click.Path(path_type=Path))
@click.option(
    "--all",
    "regenerate_all",
    is_flag=True,
    help="Regenerate all configured documents",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be regenerated without writing files",
)
def regenerate(
    doc_path: Path | None,
    regenerate_all: bool,
    dry_run: bool,
) -> None:
    """
    Regenerate documentation from saved configuration.

    This command uses the configuration saved in .doc-evergreen/history.yaml
    to regenerate documents without needing to specify parameters again.

    \b
    Usage:
      doc-evergreen regenerate <doc-path>    # Regenerate single document
      doc-evergreen regenerate --all         # Regenerate all documents

    \b
    Examples:
      # Regenerate single document
      doc-evergreen regenerate README.md

      # Regenerate all configured documents
      doc-evergreen regenerate --all

      # Preview what would be regenerated
      doc-evergreen regenerate --all --dry-run
    """
    from doc_evergreen.commands.regenerate import execute_regenerate

    # Validate arguments
    if not doc_path and not regenerate_all:
        click.echo("Error: Must specify either <doc-path> or --all flag", err=True)
        click.echo("\nUsage:")
        click.echo("  doc-evergreen regenerate <doc-path>")
        click.echo("  doc-evergreen regenerate --all")
        sys.exit(1)

    if doc_path and regenerate_all:
        click.echo("Error: Cannot specify both <doc-path> and --all flag", err=True)
        click.echo("\nUsage:")
        click.echo("  doc-evergreen regenerate <doc-path>")
        click.echo("  doc-evergreen regenerate --all")
        sys.exit(1)

    try:
        execute_regenerate(
            doc_path=doc_path,
            regenerate_all=regenerate_all,
            dry_run=dry_run,
        )
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
