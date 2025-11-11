"""
Create command implementation.

Handles creation of new documentation from source files.
"""

from pathlib import Path

import click

from doc_evergreen.core.discovery import auto_discover_files, format_file_size, gather_files
from doc_evergreen.core.generator import customize_template, generate_document
from doc_evergreen.core.history import add_doc_entry, add_version_entry, load_history
from doc_evergreen.core.template import (
    load_builtin_template,
    save_template,
)
from doc_evergreen.core.versioning import backup_document


def execute_create(
    about: str,
    output: Path,
    sources: list[str] | None,
    template: str | None,
    dry_run: bool,
) -> None:
    """
    Execute the create command.

    Args:
        about: Description of what the documentation should cover
        output: Path where the document should be saved
        sources: List of glob patterns for source files, or None for auto-discovery
        template: Specific template to use, or None for auto-selection
        dry_run: If True, show what would be done without writing files
    """
    # Validate parameters
    if not about.strip():
        raise ValueError("--about cannot be empty")

    # Ensure output has a valid extension
    if not output.suffix:
        raise ValueError(f"Output path must include filename with extension: {output}")

    if output.suffix not in [".md", ".txt", ".rst"]:
        click.echo(
            f"Warning: Output file has unusual extension '{output.suffix}'. "
            "Typically documentation uses .md (markdown)",
            err=True,
        )

    # Get repository root (current directory)
    repo_path = Path.cwd()

    # Display header
    click.echo("=" * 60)
    click.echo("doc-evergreen create command")
    click.echo("=" * 60)
    click.echo(f"About: {about}")
    click.echo(f"Output: {output}")
    click.echo(f"Sources: {sources if sources else 'auto-discover'}")
    click.echo(f"Template: {template if template else 'auto-select'}")
    click.echo(f"Dry run: {dry_run}")
    click.echo("=" * 60)

    # Step 1: File discovery
    click.echo("\n📁 Step 1: Discovering source files...")

    # Track what sources were used for history
    sources_for_history: list[str] = []

    if sources:
        # Use provided patterns
        patterns = list(sources)
        sources_for_history = patterns
        click.echo(f"Using provided patterns: {patterns}")
        # Gather files using glob patterns
        source_files = gather_files(patterns, repo_path)
    else:
        # Auto-discover using LLM-guided intelligent discovery
        # Returns actual file paths, not patterns
        click.echo("Using LLM to intelligently discover relevant files...")
        file_paths = auto_discover_files(about, repo_path, use_llm_guided=True)
        sources_for_history = file_paths  # Store discovered paths
        click.echo(f"\n✓ LLM discovered {len(file_paths)} relevant files")

        # Show all files
        for path in file_paths:
            click.echo(f"  • {path}")

        # Gather files directly from discovered paths
        source_files = gather_files(file_paths, repo_path)

    if not source_files:
        raise ValueError("No source files found for the specified topic/patterns")

    # Show what was found
    click.echo(f"\nFound {len(source_files)} source files:")
    for path in list(source_files.keys()):
        click.echo(f"  • {path}")

    # Estimate size
    total_size = sum(len(content) for content in source_files.values())
    click.echo(f"Total size: {format_file_size(total_size)}")

    if dry_run:
        click.echo("\n[DRY RUN] Would proceed with:")
        click.echo("  2. Template selection/customization")
        click.echo("  3. Document generation")
        click.echo("  4. Backup existing document (if exists)")
        click.echo("  5. Save to output path")
        click.echo("  6. Update history.yaml")
        return

    # Step 2: Template selection and customization
    click.echo("\n📝 Step 2: Preparing template...")

    if template:
        # Use explicitly specified template
        template_name = template
        click.echo(f"Using specified template: {template_name}")
    else:
        # Use LLM to intelligently select or create appropriate template
        from doc_evergreen.core.template import select_template_with_llm

        click.echo("Using LLM to select appropriate template...")
        template_name = select_template_with_llm(about, repo_path)
        click.echo(f"Selected template: {template_name}")

    # Load built-in template
    builtin_template = load_builtin_template(template_name)

    # Customize template for this project
    click.echo("Customizing template for your project (using LLM)...")
    try:
        # Never use existing output to influence new generation (circular reference problem)
        customized_template = customize_template(builtin_template, about, existing_doc=None)

        # Save customized template
        template_path = save_template(
            customized_template,
            template_name,
            repo_path,
            metadata={"derived_from": template_name, "customizations": ["Customized for project context"]},
        )
        click.echo(f"Saved customized template: {template_path}")

    except Exception as e:
        click.echo(f"⚠ Template customization failed: {e}", err=True)
        click.echo("Using built-in template without customization")
        customized_template = builtin_template
        template_path = None

    # Step 3: Generate documentation
    click.echo("\n🤖 Step 3: Generating documentation (using LLM)...")
    click.echo("This may take 30-60 seconds...")

    try:
        generated_doc = generate_document(customized_template, source_files, about)
        click.echo("✓ Document generated successfully")
    except Exception as e:
        raise RuntimeError(f"Document generation failed: {e}")

    # Step 4: Backup existing document
    if output.exists():
        click.echo("\n💾 Step 4: Backing up existing document...")
        backup_path = backup_document(output, repo_path)
        if backup_path:
            click.echo(f"✓ Backed up to: {backup_path}")
    else:
        click.echo("\n💾 Step 4: No existing document to backup")

    # Step 5: Save generated document
    click.echo(f"\n💾 Step 5: Saving document to {output}...")

    # Ensure output directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    # Write document
    with open(output, "w", encoding="utf-8") as f:
        f.write(generated_doc)

    click.echo("✓ Document saved successfully")

    # Step 6: Update history
    click.echo("\n📋 Step 6: Updating history...")

    # Load history to check if this is a regeneration
    history = load_history(repo_path)

    # Determine relative output path
    try:
        relative_output = output.relative_to(repo_path)
    except ValueError:
        # Output is outside repo, use absolute
        relative_output = output

    doc_key = str(relative_output)

    # Check if this is a regeneration
    is_regeneration = doc_key in history.get("docs", {})

    if is_regeneration:
        # Add version entry (internally saves history)
        if backup_path:
            try:
                relative_backup = backup_path.relative_to(repo_path)
            except ValueError:
                relative_backup = backup_path

            add_version_entry(
                doc_path=doc_key,
                backup_path=str(relative_backup),
                template_name=template_name,
                template_path=str(template_path.relative_to(repo_path)) if template_path else "",
                repo_path=repo_path,
            )
            click.echo("✓ Added version entry for regeneration")
    else:
        # Add new doc entry (internally saves history)
        add_doc_entry(
            doc_path=doc_key,
            about=about,
            template_name=template_name,
            template_path=str(template_path.relative_to(repo_path)) if template_path else "",
            sources=sources_for_history,
            repo_path=repo_path,
        )
        click.echo("✓ Added new document entry")

    click.echo("✓ History updated")

    # Success summary
    click.echo("\n" + "=" * 60)
    click.echo("✅ Documentation created successfully!")
    click.echo("=" * 60)
    click.echo(f"Output: {output}")
    click.echo(f"Template: {template_name} (customized)")
    click.echo(f"Sources: {len(source_files)} files")
    if is_regeneration and backup_path:
        click.echo(f"Backup: {backup_path}")
    click.echo("=" * 60)
