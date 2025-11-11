"""
Create command implementation.

Handles creation of new documentation from source files.
"""

from pathlib import Path

import click

from doc_evergreen.core.discovery import auto_discover_files, format_file_size, gather_files
from doc_evergreen.core.doc_logger import close_logger, init_logger
from doc_evergreen.core.generator import (
    customize_template,
    decide_if_customization_needed,
    generate_document_with_mapping,
)
from doc_evergreen.core.history import add_doc_entry, add_version_entry, load_history
from doc_evergreen.core.source_mapping import map_sources_to_sections, save_source_map
from doc_evergreen.core.template import (
    load_builtin_template,
    save_template,
)
from doc_evergreen.core.versioning import backup_document


def find_git_root(start_path: Path) -> Path | None:
    """
    Find the git repository root by searching for .git directory.

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to git root, or None if not in a git repo
    """
    current = start_path.resolve()

    # Search up to 10 levels
    for _ in range(10):
        if (current / ".git").exists():
            return current

        parent = current.parent
        if parent == current:
            # Reached filesystem root
            break
        current = parent

    return None


def execute_create(
    about: str,
    output: Path,
    sources: list[str] | None,
    template: str | None,
    should_customize_template: bool | None,
    dry_run: bool,
) -> None:
    """
    Execute the create command.

    Args:
        about: Description of what the documentation should cover
        output: Path where the document should be saved
        sources: List of glob patterns for source files, or None for auto-discovery
        template: Specific template to use, or None for auto-selection
        should_customize_template: Whether to customize template (None=auto-decide based on whether template was specified)
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

    # Get repository root
    cwd = Path.cwd()
    git_root = find_git_root(cwd)

    if git_root is None:
        click.echo("⚠️  Warning: Not in a git repository.", err=True)
        click.echo("   Using current directory as repo root.", err=True)
        click.echo(f"   Directory: {cwd}", err=True)
        click.echo("", err=True)
        repo_path = cwd
    else:
        repo_path = git_root

        # Warn if running from subdirectory
        if cwd != git_root:
            click.echo("⚠️  Warning: Running from subdirectory of git repo.", err=True)
            click.echo(f"   Current: {cwd}", err=True)
            click.echo(f"   Git root: {git_root}", err=True)
            click.echo("   Using git root as repo path.", err=True)
            click.echo("", err=True)
            click.echo("💡 Tip: For best results, run from repository root:", err=True)
            click.echo(f"   cd {git_root}", err=True)
            click.echo('   make doc-create ABOUT="..." OUTPUT=...', err=True)
            click.echo("", err=True)

            # Ask for confirmation
            if not dry_run:
                click.confirm("Continue with git root as repo path?", abort=True, err=True)

    # Initialize logger
    log_dir = repo_path / ".doc-evergreen" / "logs"
    logger = init_logger(log_dir)
    logger.logger.info("=" * 80)
    logger.logger.info("CREATE COMMAND STARTED")
    logger.logger.info(f"About: {about}")
    logger.logger.info(f"Output: {output}")
    logger.logger.info(f"Repository path: {repo_path}")
    logger.logger.info("=" * 80)

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
        click.echo("  3. Source-to-section mapping")
        click.echo("  4. Document generation")
        click.echo("  5. Backup existing document (if exists)")
        click.echo("  6. Save to output path")
        click.echo("  7. Update history.yaml")
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

    # Determine if template should be customized
    # Three scenarios:
    # 1. Explicit --customize-template: Always customize
    # 2. Explicit --no-customize-template: Never customize
    # 3. No flag (auto-decide): Ask LLM to evaluate if customization would be beneficial

    if should_customize_template is None:
        # Auto-decide: Always ask LLM to evaluate customization need
        # (regardless of whether template was user-specified or LLM-selected)
        click.echo("Evaluating if template customization would be beneficial...")
        try:
            do_customize, reason = decide_if_customization_needed(builtin_template, about, source_files, template_name)
            if do_customize:
                click.echo(f"✓ Customization recommended: {reason}")
            else:
                click.echo(f"✓ Template sufficient as-is: {reason}")
        except Exception as e:
            click.echo(f"⚠ Could not decide on customization: {e}", err=True)
            click.echo("Defaulting to: use template directly")
            do_customize = False
    else:
        # Explicit flag provided - honor user's decision
        do_customize = should_customize_template
        if do_customize:
            click.echo(f"Customizing template '{template_name}' (explicitly requested)")
        else:
            click.echo(f"Using template '{template_name}' directly (explicitly requested)")

    # Perform customization if needed
    if do_customize:
        try:
            # Pass source files to customization for context
            customized_template = customize_template(builtin_template, about, sources=source_files, existing_doc=None)

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
    else:
        # Use template directly without customization
        customized_template = builtin_template
        template_path = None

    # Step 3: Map sources to sections
    click.echo("\n🗺️  Step 3: Mapping sources to template sections...")

    try:
        source_mapping = map_sources_to_sections(customized_template, source_files, about)
        click.echo(f"✓ Mapped {len(source_mapping)} sections")

        # Show mapping summary
        for section, sources in source_mapping.items():
            if sources:
                click.echo(f"  • {section}: {len(sources)} source(s)")

        # Save source map
        source_map_file = save_source_map(source_mapping, template_name, repo_path, metadata={"about": about})
        click.echo(f"✓ Source map saved: {source_map_file.name}")
    except Exception as e:
        raise RuntimeError(f"Source mapping failed: {e}")

    # Step 4: Generate documentation
    click.echo("\n🤖 Step 4: Generating documentation (using LLM with source mapping)...")
    click.echo("This may take 30-60 seconds...")

    try:
        generated_doc = generate_document_with_mapping(customized_template, source_files, about, source_mapping)
        click.echo("✓ Document generated successfully")
    except Exception as e:
        raise RuntimeError(f"Document generation failed: {e}")

    # Step 5: Backup existing document
    if output.exists():
        click.echo("\n💾 Step 5: Backing up existing document...")
        backup_path = backup_document(output, repo_path)
        if backup_path:
            click.echo(f"✓ Backed up to: {backup_path}")
    else:
        click.echo("\n💾 Step 5: No existing document to backup")

    # Step 6: Save generated document
    click.echo(f"\n💾 Step 6: Saving document to {output}...")

    # Ensure output directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    # Write document
    with open(output, "w", encoding="utf-8") as f:
        f.write(generated_doc)

    click.echo("✓ Document saved successfully")

    # Step 7: Update history
    click.echo("\n📋 Step 7: Updating history...")

    # Load history to check if this is a regeneration
    history = load_history(repo_path)

    # Determine relative output path
    try:
        relative_output = output.relative_to(repo_path)
    except ValueError:
        # Output is outside repo, use absolute
        relative_output = output

    doc_key = str(relative_output)

    # Get relative path for source map
    try:
        relative_source_map = source_map_file.relative_to(repo_path)
    except ValueError:
        relative_source_map = source_map_file

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
                sources=sources_for_history,
                repo_path=repo_path,
                source_map_path=str(relative_source_map),
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
            source_map_path=str(relative_source_map),
        )
        click.echo("✓ Added new document entry")

    click.echo("✓ History updated")

    # Success summary
    click.echo("\n" + "=" * 60)
    click.echo("✅ Documentation created successfully!")
    click.echo("=" * 60)
    click.echo(f"Output: {output}")
    template_desc = f"{template_name} ({'customized' if do_customize else 'built-in'})"
    click.echo(f"Template: {template_desc}")
    click.echo(f"Source mapping: {source_map_file.name}")
    click.echo(f"Sources: {len(source_files)} files")
    if is_regeneration and backup_path:
        click.echo(f"Backup: {backup_path}")
    click.echo("=" * 60)

    # Close logger
    close_logger()
