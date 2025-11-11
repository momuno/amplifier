"""
Regenerate command implementation.

Handles regeneration of documents from saved configuration.
"""

from pathlib import Path

import click

from doc_evergreen.core.discovery import gather_files
from doc_evergreen.core.generator import generate_document_with_mapping
from doc_evergreen.core.history import add_version_entry, get_doc_config, load_history
from doc_evergreen.core.source_mapping import load_source_map, map_sources_to_sections, save_source_map
from doc_evergreen.core.template import load_builtin_template, load_template_from_path
from doc_evergreen.core.versioning import backup_document


def regenerate_single_document(
    doc_key: str,
    doc_config: dict,
    repo_path: Path,
    dry_run: bool,
) -> None:
    """
    Regenerate a single document from its configuration.

    Args:
        doc_key: Document key in history
        doc_config: Document configuration from history
        repo_path: Repository root path
        dry_run: If True, show what would be done without writing files
    """
    click.echo(f"\n📄 Regenerating: {doc_key}")
    click.echo("-" * 60)

    # Extract configuration
    output_path = repo_path / doc_config["path"]
    sources = doc_config.get("sources", [])
    about = doc_config.get("about", "")
    template_info = doc_config.get("template_used", {})
    template_name = template_info.get("name")
    template_path = template_info.get("path")

    if not template_name:
        click.echo("⚠ No template information in history, skipping", err=True)
        return

    click.echo(f"About: {about}")
    click.echo(f"Output: {output_path}")
    click.echo(f"Sources: {sources}")
    click.echo(f"Template: {template_name}")

    if dry_run:
        click.echo("\n[DRY RUN] Would regenerate this document")
        return

    # Step 1: Gather source files
    click.echo("\n📁 Step 1: Gathering source files...")
    try:
        source_files = gather_files(sources, repo_path)
    except Exception as e:
        click.echo(f"⚠ Failed to gather source files: {e}", err=True)
        return

    if not source_files:
        click.echo(f"⚠ No source files found for patterns: {sources}", err=True)
        return

    click.echo(f"Found {len(source_files)} source files")

    # Step 2: Load template
    click.echo("\n📝 Step 2: Loading template...")
    try:
        if template_path:
            # Try to load customized template
            try:
                template_content = load_template_from_path(template_path, repo_path)
                click.echo(f"Loaded customized template from {template_path}")
            except FileNotFoundError:
                # Fall back to built-in
                click.echo(f"Customized template not found, using built-in: {template_name}")
                template_content = load_builtin_template(template_name)
        else:
            # Load built-in
            template_content = load_builtin_template(template_name)
            click.echo(f"Loaded built-in template: {template_name}")

        # Never use existing output to influence new generation (circular reference problem)

    except Exception as e:
        click.echo(f"⚠ Failed to load template: {e}", err=True)
        return

    # Step 3: Load or create source mapping
    click.echo("\n🗺️  Step 3: Loading/creating source mapping...")

    source_map_path_str = doc_config.get("source_map_path")
    source_mapping = None
    source_map_file = None

    if source_map_path_str:
        # Try to load existing source map
        try:
            source_map_path = repo_path / source_map_path_str
            source_mapping = load_source_map(source_map_path)
            click.echo(f"✓ Loaded source map from {source_map_path_str}")
        except FileNotFoundError:
            click.echo(f"⚠ Source map not found: {source_map_path_str}")
            source_mapping = None

    if source_mapping is None:
        # Create new source mapping
        click.echo("Creating new source mapping...")
        try:
            source_mapping = map_sources_to_sections(template_content, source_files, about)
            click.echo(f"✓ Mapped {len(source_mapping)} sections")

            # Save the new mapping
            source_map_file = save_source_map(source_mapping, template_name, repo_path, metadata={"about": about})
            click.echo(f"✓ Source map saved: {source_map_file.name}")
        except Exception as e:
            click.echo(f"⚠ Failed to create source mapping: {e}", err=True)
            return

    # Step 4: Generate document
    click.echo("\n🤖 Step 4: Generating documentation (using LLM with source mapping)...")
    click.echo("This may take 30-60 seconds...")

    try:
        generated_doc = generate_document_with_mapping(template_content, source_files, about, source_mapping)
        click.echo("✓ Document generated successfully")
    except Exception as e:
        click.echo(f"⚠ Failed to generate document: {e}", err=True)
        return

    # Step 5: Backup existing document
    if output_path.exists():
        click.echo("\n💾 Step 5: Backing up existing document...")
        backup_path = backup_document(output_path, repo_path)
        if backup_path:
            click.echo(f"✓ Backed up to: {backup_path}")
    else:
        click.echo("\n💾 Step 5: No existing document to backup")
        backup_path = None

    # Step 6: Save generated document
    click.echo(f"\n💾 Step 6: Saving document to {output_path}...")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write document
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generated_doc)

    click.echo("✓ Document saved successfully")

    # Step 7: Update history
    click.echo("\n📋 Step 7: Updating history...")

    # Get relative path for source map if we created a new one
    source_map_path_for_history = ""
    if source_map_file:
        try:
            relative_source_map = source_map_file.relative_to(repo_path)
            source_map_path_for_history = str(relative_source_map)
        except ValueError:
            source_map_path_for_history = str(source_map_file)
    elif source_map_path_str:
        # Use existing source map path
        source_map_path_for_history = source_map_path_str

    if backup_path:
        try:
            relative_backup = backup_path.relative_to(repo_path)
        except ValueError:
            relative_backup = backup_path

        add_version_entry(
            doc_path=doc_key,
            backup_path=str(relative_backup),
            template_name=template_name,
            template_path=template_path or "",
            sources=sources,
            repo_path=repo_path,
            source_map_path=source_map_path_for_history,
        )

    click.echo("✓ History updated")

    click.echo(f"\n✅ Successfully regenerated: {doc_key}")


def execute_regenerate(
    doc_path: Path | None,
    regenerate_all: bool,
    dry_run: bool,
) -> None:
    """
    Execute the regenerate command.

    Args:
        doc_path: Path to specific document to regenerate, or None if --all
        regenerate_all: If True, regenerate all configured documents
        dry_run: If True, show what would be done without writing files
    """
    # Get repository root
    repo_path = Path.cwd()

    # Display header
    click.echo("=" * 60)
    click.echo("doc-evergreen regenerate command")
    click.echo("=" * 60)

    if regenerate_all:
        click.echo("Mode: Regenerate all configured documents")
    else:
        click.echo(f"Mode: Regenerate single document: {doc_path}")

    click.echo(f"Dry run: {dry_run}")
    click.echo("=" * 60)

    # Load history
    click.echo("\n📋 Loading configuration from history...")
    try:
        history = load_history(repo_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load history: {e}")

    docs = history.get("docs", {})

    if not docs:
        click.echo("⚠ No documents configured in history.yaml", err=True)
        click.echo("Use 'doc-evergreen create' to create your first document")
        return

    if regenerate_all:
        # Regenerate all documents
        doc_keys = list(docs.keys())
        click.echo(f"Found {len(doc_keys)} configured documents")

        if dry_run:
            click.echo("\n[DRY RUN] Would regenerate the following documents:")
            for key in doc_keys:
                click.echo(f"  • {key}")
            return

        # Regenerate each document
        success_count = 0
        fail_count = 0

        for doc_key in doc_keys:
            doc_config = docs[doc_key]
            try:
                regenerate_single_document(doc_key, doc_config, repo_path, dry_run)
                success_count += 1
            except Exception as e:
                click.echo(f"\n⚠ Error regenerating {doc_key}: {e}", err=True)
                fail_count += 1
                continue

        # Summary
        click.echo("\n" + "=" * 60)
        click.echo("📊 Regeneration Summary")
        click.echo("=" * 60)
        click.echo(f"✅ Successful: {success_count}")
        if fail_count > 0:
            click.echo(f"⚠ Failed: {fail_count}")
        click.echo("=" * 60)

    else:
        # Regenerate single document
        if not doc_path:
            raise ValueError("Must specify document path or use --all flag")

        # Normalize path to match history keys
        try:
            relative_path = doc_path.relative_to(repo_path)
        except ValueError:
            relative_path = doc_path

        doc_key = str(relative_path)

        # Get document configuration
        doc_config = get_doc_config(doc_key, repo_path)

        if not doc_config:
            click.echo(f"⚠ Document not found in history: {doc_key}", err=True)
            click.echo("\nConfigured documents:")
            for key in docs.keys():
                click.echo(f"  • {key}")
            return

        if dry_run:
            click.echo(f"\n[DRY RUN] Would regenerate: {doc_key}")
            click.echo(f"About: {doc_config.get('about', 'N/A')}")
            click.echo(f"Sources: {doc_config.get('sources', [])}")
            return

        # Regenerate the document
        regenerate_single_document(doc_key, doc_config, repo_path, dry_run)
