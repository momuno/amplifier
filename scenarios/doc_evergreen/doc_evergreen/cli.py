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

      # Create with specific sources
      doc-evergreen create --about "API docs" --output docs/API.md --sources "src/**/*.py"

      # Regenerate existing documentation
      doc-evergreen regenerate docs/API.md
    """
    # This is a Click command group - the function body is not executed
    # All functionality is in the subcommands (create, regenerate)
    return


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
    help="Files to include - supports exact paths (e.g., 'README.md') and glob patterns (e.g., 'src/**/*.py'). Can be specified multiple times. Mix both types freely. If not provided, files will be auto-discovered.",
)
@click.option(
    "--start-step",
    type=int,
    default=1,
    help="Start from a specific step (1-5) for testing. Uses existing data from previous runs. Steps: 1=Discovery, 2=Summarization, 3=Relevancy, 4=Template, 5=Generation",
)
def create(
    about: str,
    output: Path,
    sources: tuple[str, ...],
    start_step: int,
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

    \b
    Examples:
      # Create with specific sources (glob pattern)
      doc-evergreen create \\
          --about "API reference for knowledge synthesis" \\
          --output "docs/API_REFERENCE.md" \\
          --sources "src/knowledge_synthesis/**/*.py"

      # Mix exact files and patterns
      doc-evergreen create \\
          --about "Project README" \\
          --output "README.md" \\
          --sources "README.md" --sources "pyproject.toml" --sources "src/**/*.py"

      # Create with auto-discovery
      doc-evergreen create \\
          --about "Contributing guide" \\
          --output "docs/CONTRIBUTING.md"
    """
    from doc_evergreen.commands.create import execute_create

    try:
        # Convert sources tuple to list
        sources_list = list(sources) if sources else None

        execute_create(
            about=about,
            output=output,
            sources=sources_list,
            start_step=start_step,
        )
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("doc_path", type=str)
def regenerate(doc_path: str) -> None:
    """
    Regenerate documentation when source files have been updated.

    This command:
    1. Checks if the document was previously generated
    2. Compares current source file versions with those used in last generation
    3. If any source files updated, regenerates summaries and document
    4. Skips regeneration if no source files have changed

    \b
    Examples:
      # Regenerate a document
      doc-evergreen regenerate README.md

      # Regenerate document in subdirectory
      doc-evergreen regenerate docs/API.md
    """
    from doc_evergreen.commands.regenerate import execute_regenerate

    try:
        execute_regenerate(doc_path=doc_path)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
