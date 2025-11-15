"""
Create command implementation.

Handles creation of new documentation from source files.
"""

import json
from datetime import datetime
from pathlib import Path

import click

from doc_evergreen.core.discovery import format_file_size
from doc_evergreen.core.discovery import gather_files
from doc_evergreen.core.doc_logger import close_logger
from doc_evergreen.core.doc_logger import init_logger
from doc_evergreen.core.generator import create_customized_template
from doc_evergreen.core.generator import generate_document
from doc_evergreen.core.generator import score_file_relevancy
from doc_evergreen.core.generator import summarize_file
from doc_evergreen.core.project import backup_existing_document
from doc_evergreen.core.project import save_customized_template
from doc_evergreen.core.summaries import add_summary
from doc_evergreen.core.summaries import get_file_content_hash
from doc_evergreen.core.summaries import get_summary
from doc_evergreen.core.template import load_template_guide
from doc_evergreen.prompts import get_prompt_version


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
    start_step: int = 1,
) -> None:
    """
    Execute the create command.

    Args:
        about: Description of what the documentation should cover
        output: Path where the document should be saved
        sources: List of glob patterns for source files, or None for auto-discovery
        start_step: Step to start from (1-5). Uses existing data from previous runs.
                   Steps: 1=Discovery, 2=Summarization, 3=Relevancy, 4=Template, 5=Generation
    """
    # Validate parameters
    if not about.strip():
        raise ValueError("--about cannot be empty")

    if start_step not in range(1, 6):
        raise ValueError(f"--start-step must be between 1 and 5, got {start_step}")

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
            click.confirm("Continue with git root as repo path?", abort=True, err=True)

    # Initialize logger
    log_dir = repo_path / ".doc-evergreen" / "logs"
    logger = init_logger(log_dir)

    # Log command invocation with all arguments
    logger.log_command_invocation(
        command="create",
        args={
            "about": about,
            "output": str(output),
            "sources": sources if sources else "auto-discover",
            "repository_path": str(repo_path),
            "current_directory": str(Path.cwd()),
        },
    )

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
    if start_step > 1:
        click.echo(f"Start Step: {start_step} (skipping steps 1-{start_step - 1})")
    click.echo("=" * 60)

    # Determine project identifier from output path (used for all project data storage)
    # Use full relative path with extension to ensure uniqueness and prevent conflicts
    try:
        relative_output = output.relative_to(repo_path)
    except ValueError:
        relative_output = output

    # Convert to string with forward slashes for consistency across platforms
    doc_key = str(relative_output).replace("\\", "/")

    # Use doc_key for all project-related directories (relevancy, templates, etc.)
    # This ensures consistency and prevents conflicts between files with same name in different dirs

    # Initialize variables that may be populated by skipped steps
    source_files: dict[str, str] = {}
    file_summaries: dict[str, str] = {}
    relevancy_scores: dict[str, int] = {}
    source_file_data: list[dict] = []
    patterns: list[str] = []

    # Step 1: File Sourcing
    if start_step <= 1:
        click.echo("\n📁 Step 1: File Sourcing...")

        if not sources:
            raise ValueError("--sources is required. Auto-discovery will be implemented later.")

        # Use provided patterns/files
        patterns = list(sources)
        click.echo(f"Using provided patterns: {patterns}")

        # Gather files using glob patterns
        source_files = gather_files(patterns, repo_path)

        if not source_files:
            raise ValueError("No source files found for the specified patterns")

        # IMPORTANT: Filter out the output file from sources for CREATE operations
        # We should NEVER include the output documentation as a source when creating new docs
        try:
            output_relative = output.relative_to(repo_path)
            output_key = str(output_relative)

            if output_key in source_files:
                click.echo(f"\n⚠️  Filtering out output file from sources: {output_key}")
                click.echo("   (Output file should not be used as a source for CREATE)")
                del source_files[output_key]

        except ValueError:
            # Output is outside repo_path, can't be in source_files anyway
            pass

        # Show what was found
        click.echo(f"\nFound {len(source_files)} source files:")
        for path in list(source_files.keys())[:10]:  # Show first 10
            click.echo(f"  • {path}")
        if len(source_files) > 10:
            click.echo(f"  ... and {len(source_files) - 10} more")

        # Estimate size
        total_size = sum(len(content) for content in source_files.values())
        click.echo(f"Total size: {format_file_size(total_size)}")
    else:
        # Skip Step 1: When starting from step 2, we must have sources specified
        click.echo("\n⏩ Skipping Step 1 (File Sourcing)")
        click.echo("Loading source files from existing summaries...")

        if not sources:
            raise ValueError("--sources is required when starting from step 2")

        # Use the provided sources - these are the files we need to process
        patterns = list(sources)

        # Gather the actual file content for these sources
        source_files = gather_files(patterns, repo_path)

        if not source_files:
            raise ValueError("No source files found for the specified patterns")

        click.echo(f"Found {len(source_files)} files with existing summaries")

    # Step 2: File Summarization
    if start_step <= 2:
        click.echo("\n📝 Step 2: Summarizing source files...")
        click.echo("Generating summaries for each file (using LLM)...")
        click.echo("This may take 1-2 minutes...")

        files_to_summarize = list(source_files.keys())

        for idx, file_path in enumerate(files_to_summarize, 1):
            click.echo(f"  [{idx}/{len(files_to_summarize)}] Summarizing {file_path}...")

            # Check if we have a cached summary with matching content hash
            cached_summary = get_summary(file_path, repo_path)
            current_content_hash = get_file_content_hash(file_path, repo_path)

            if cached_summary and cached_summary.get("content_hash") == current_content_hash:
                # Content unchanged - use cached summary
                click.echo("      ✓ Using cached summary (content unchanged)")
                file_summaries[file_path] = cached_summary["summary"]
            else:
                # Content changed or no cache - generate new summary
                if cached_summary:
                    click.echo("      🔄 Content changed - regenerating summary")
                else:
                    click.echo("      🆕 No cached summary - generating new")

                file_content = source_files[file_path]
                summary, prompt_name, prompt_version = summarize_file(file_path, file_content)

                # Cache the summary with version information
                add_summary(file_path, summary, repo_path, prompt_name, prompt_version)

                file_summaries[file_path] = summary
                click.echo("      ✓ Summary generated and cached")

        click.echo(f"✓ All {len(file_summaries)} files summarized")
    else:
        # Skip Step 2: Load existing summaries
        click.echo("\n⏩ Skipping Step 2 (File Summarization)")
        click.echo("Loading existing summaries...")

        from doc_evergreen.core.summaries import get_file_summaries_dir

        summaries_dir = get_file_summaries_dir(repo_path)
        summary_files = list(summaries_dir.glob("*.json"))

        for summary_file in summary_files:
            # Load the summary data
            with open(summary_file, encoding="utf-8") as f:
                data = json.load(f)

            if "versions" in data and data["versions"]:
                file_path = data["file_path"]
                latest_version = sorted(data["versions"], key=lambda v: v["timestamp"], reverse=True)[0]
                file_summaries[file_path] = latest_version["summary"]

        click.echo(f"Loaded {len(file_summaries)} existing summaries")

    # Step 3: Score Relevancy
    if start_step <= 3:
        click.echo("\n🎯 Step 3: Scoring file relevancy...")
        click.echo("Determining which source files are relevant for this document (using LLM)...")

        from doc_evergreen.core.relevancy import add_relevancy_score
        from doc_evergreen.core.relevancy import get_relevancy_score

        for file_path in file_summaries:
            # Get the most recent summary
            summary_data = get_summary(file_path, repo_path)

            if summary_data:
                file_summary = summary_data["summary"]
                summary_timestamp = summary_data["timestamp"]

                # Check if we have a cached relevancy score for this summary
                cached_relevancy = get_relevancy_score(file_path, repo_path, doc_key)

                if (
                    cached_relevancy
                    and cached_relevancy.get("doc_description") == about
                    and cached_relevancy.get("file_summary", {}).get("version") == summary_timestamp
                ):
                    # Summary unchanged and same doc description - use cached relevancy
                    explanation = cached_relevancy["relevancy_explanation"]
                    score = cached_relevancy["relevancy_score"]
                    relevancy_timestamp = cached_relevancy["timestamp"]

                    click.echo(f"  {file_path}")
                    click.echo("    ✓ Using cached relevancy (summary unchanged)")
                    click.echo(f"    Score: {score}/10 - {explanation[:60]}...")
                else:
                    # Summary changed or no cache - re-score
                    if cached_relevancy:
                        click.echo(f"  {file_path}")
                        click.echo("    🔄 Summary changed - rescoring relevancy")
                    else:
                        click.echo(f"  {file_path}")
                        click.echo("    🆕 No cached relevancy - scoring")

                    # Score relevancy
                    explanation, score = score_file_relevancy(file_path, file_summary, about)

                    # Store relevancy score
                    prompt_name = "score_relevancy"
                    prompt_version = get_prompt_version(prompt_name)

                    relevancy_timestamp = add_relevancy_score(
                        file_path=file_path,
                        doc_description=about,
                        relevancy_explanation=explanation,
                        relevancy_score=score,
                        summary_text=file_summary,
                        summary_timestamp=summary_timestamp,
                        repo_path=repo_path,
                        project_name=doc_key,
                        prompt_name=prompt_name,
                        prompt_version=prompt_version,
                    )

                    click.echo(f"    Score: {score}/10 - {explanation[:60]}...")

                relevancy_scores[file_path] = score

                # Collect source file data for template storage
                source_file_data.append(
                    {
                        "file_path": file_path,
                        "summary": {"text": file_summary, "timestamp": summary_timestamp},
                        "relevancy": {
                            "explanation": explanation,
                            "score": score,
                            "timestamp": relevancy_timestamp,
                            "prompt": {"name": "score_relevancy", "version": get_prompt_version("score_relevancy")},
                        },
                    }
                )

        click.echo(f"✓ All {len(relevancy_scores)} files scored for relevancy")
    else:
        # Skip Step 3: Load existing relevancy scores
        click.echo("\n⏩ Skipping Step 3 (Relevancy Scoring)")
        click.echo("Loading existing relevancy scores...")

        from doc_evergreen.core.relevancy import get_project_relevancy_dir

        relevancy_dir = get_project_relevancy_dir(repo_path, doc_key)
        if not relevancy_dir.exists():
            raise ValueError(
                f"No relevancy directory found for project '{doc_key}'. "
                f"Cannot skip to step {start_step}. Run from step 1 first."
            )

        relevancy_files = list(relevancy_dir.glob("*.json"))
        if not relevancy_files:
            raise ValueError(
                f"No relevancy scores found for project '{doc_key}'. "
                f"Cannot skip to step {start_step}. Run from step 1 first."
            )

        for relevancy_file in relevancy_files:
            with open(relevancy_file, encoding="utf-8") as f:
                data = json.load(f)

            if "versions" in data and data["versions"]:
                file_path = data["file_path"]
                # Get most recent version
                latest_version = sorted(data["versions"], key=lambda v: v["timestamp"], reverse=True)[0]

                relevancy_scores[file_path] = latest_version["relevancy_score"]

                # Reconstruct source_file_data
                source_file_data.append(
                    {
                        "file_path": file_path,
                        "summary": latest_version["summary"],
                        "relevancy": {
                            "explanation": latest_version["relevancy_explanation"],
                            "score": latest_version["relevancy_score"],
                            "prompt": latest_version["prompt"],
                        },
                    }
                )

        click.echo(f"Loaded {len(relevancy_scores)} existing relevancy scores")

    # Initialize variables for Step 4
    customized_template = ""
    selected_files: dict[str, str] = {}
    template_version_identifier = ""
    doc_key = ""

    # Step 4: Template Customization
    if start_step <= 4:
        click.echo("\n🎨 Step 4: Customizing documentation template...")
        click.echo("Creating template tailored to source files and document description (using LLM)...")

        # Load the template guide
        template_guide, template_guide_version = load_template_guide()

        click.echo(f"Template guide: {template_guide_version}")
        click.echo(f"Source files analyzed: {len(source_file_data)}")
        click.echo("This may take 30-60 seconds...")

        try:
            # Create customized template with file mappings
            customized_template, selected_files, prompt_name, prompt_version = create_customized_template(
                template_guide=template_guide,
                template_guide_version=template_guide_version,
                about=about,
                source_file_data=source_file_data,
            )
            click.echo("✓ Customized template created")
            click.echo(f"  • Prompt: {prompt_name} (version {prompt_version})")
            click.echo(f"  • Selected {len(selected_files)} relevant files:")
            for file_path, reason in list(selected_files.items())[:5]:
                click.echo(f"    - {file_path}: {reason[:60]}...")
            if len(selected_files) > 5:
                click.echo(f"    ... and {len(selected_files) - 5} more")

            # Determine relative output path for project directory
            try:
                relative_output = output.relative_to(repo_path)
            except ValueError:
                relative_output = output

            doc_key = str(relative_output)

            # Define template version for metadata
            # The customized template is the actual template used, versioned by timestamp
            template_version_identifier = f"customized-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Save customized template to project directory with full metadata
            template_file_path = save_customized_template(
                doc_path=doc_key,
                template_content=customized_template,
                repo_path=repo_path,
                template_version=template_version_identifier,
                project_name=doc_key,
                selected_files=selected_files,
                doc_description=about,
                template_guide_version=template_guide_version,
                source_file_data=source_file_data,
                prompt_name=prompt_name,
                prompt_version=prompt_version,
            )
            click.echo(f"  ✓ Template saved to {template_file_path.name}")

        except Exception as e:
            raise RuntimeError(f"Template customization failed: {e}")
    else:
        # Skip Step 4: Load most recent customized template
        click.echo("\n⏩ Skipping Step 4 (Template Customization)")
        click.echo("Loading most recent customized template...")

        # Determine doc_key from output path
        try:
            relative_output = output.relative_to(repo_path)
        except ValueError:
            relative_output = output
        doc_key = str(relative_output)

        # Find most recent customized template
        project_dir = repo_path / ".doc-evergreen" / "projects" / doc_key
        templates_dir = project_dir / "4_customized_template"

        if not templates_dir.exists():
            raise ValueError(
                f"No 4_customized_template directory found for '{doc_key}'. "
                f"Cannot skip to step {start_step}. Run from step 1 first."
            )

        template_files = sorted(templates_dir.glob("customized_template_*.json"), reverse=True)
        if not template_files:
            raise ValueError(
                f"No customized templates found for '{doc_key}'. "
                f"Cannot skip to step {start_step}. Run from step 1 first."
            )

        # Load most recent template
        with open(template_files[0], encoding="utf-8") as f:
            template_data = json.load(f)

        customized_template = template_data["customized_template"]
        selected_files = template_data.get("selected_files", {})
        template_version_identifier = template_data["template_version_id"]

        click.echo(f"Loaded customized template: {template_files[0].name}")
        click.echo(f"  • Template version: {template_version_identifier}")
        click.echo(f"  • Selected {len(selected_files)} source files")

    # Step 5: Document Generation
    if start_step <= 5:
        click.echo("\n📝 Step 5: Generating final documentation...")
        click.echo("Using customized template and full source file content to create document (using LLM)...")

        click.echo(f"Document topic: {about[:80]}{'...' if len(about) > 80 else ''}")
        click.echo(f"Loading full content of {len(selected_files)} selected files...")

        # Load full content of selected source files
        source_files_content: dict[str, str] = {}
        for idx, file_path in enumerate(selected_files.keys(), 1):
            full_path = repo_path / file_path
            if full_path.exists():
                with open(full_path, encoding="utf-8") as f:
                    source_files_content[file_path] = f.read()
                click.echo(f"  [{idx}/{len(selected_files)}] Loaded: {file_path}")
            else:
                click.echo(f"  [{idx}/{len(selected_files)}] ⚠️  Warning: File not found: {file_path}", err=True)

        click.echo(f"\n✓ Loaded {len(source_files_content)} files")
        click.echo("Generating documentation with LLM...")
        click.echo("This may take 30-60 seconds...")

        try:
            # Generate document using customized template, selected files, and full source content
            generated_doc = generate_document(
                customized_template=customized_template,
                about=about,
                selected_files=selected_files,
                source_files_content=source_files_content,
            )
            click.echo("✓ Documentation generated successfully")
            click.echo(f"  • Document length: {len(generated_doc):,} characters")

        except Exception as e:
            raise RuntimeError(f"Document generation failed: {e}")
    else:
        raise ValueError(f"Invalid start_step: {start_step}. Maximum is 5.")

    # Backup existing document if it exists
    backup_timestamp = None
    if output.exists():
        click.echo("\n💾 Backing up existing document...")
        backup_timestamp = backup_existing_document(doc_key, repo_path)
        if backup_timestamp:
            click.echo(f"✓ Backed up existing document with timestamp: {backup_timestamp}")

    # Save generated document to output location
    click.echo(f"\n💾 Saving document to {output}...")

    # Ensure output directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    # Write document
    with open(output, "w", encoding="utf-8") as f:
        f.write(generated_doc)

    click.echo("✓ Document saved successfully")

    # Get the customized template version (most recent version timestamp)
    from doc_evergreen.core.project import ensure_project_dir

    project_dir = ensure_project_dir(doc_key, repo_path)
    template_metadata_path = project_dir / "4_customized_template" / "metadata.json"
    customized_template_version = None
    if template_metadata_path.exists():
        with open(template_metadata_path, encoding="utf-8") as f:
            template_data = json.load(f)
            if template_data.get("versions"):
                # Get the most recent version
                sorted_versions = sorted(template_data["versions"], key=lambda v: v.get("version", ""), reverse=True)
                customized_template_version = sorted_versions[0]["version"]

    # Get prompt version for generate_document
    generate_prompt_name = "generate_document"
    generate_prompt_version = get_prompt_version(generate_prompt_name)

    # Get content hashes for source files
    source_files_with_hashes = {}
    for file_path in source_files_content:
        content_hash = get_file_content_hash(file_path, repo_path)
        source_files_with_hashes[file_path] = content_hash if content_hash else "no-hash"

    # Save document content to project directory with versioned metadata
    from doc_evergreen.core.project import save_generated_document

    save_generated_document(
        doc_path=doc_key,
        content=generated_doc,
        repo_path=repo_path,
        project_name=doc_key,
        doc_description=about,
        source_files_content=source_files_content,
        customized_template_version=customized_template_version,
        prompt_name=generate_prompt_name,
        prompt_version=generate_prompt_version,
    )
    click.echo("✓ Content saved to project directory")

    # Success summary
    click.echo("\n" + "=" * 60)
    click.echo("✅ Documentation created successfully!")
    click.echo("=" * 60)
    click.echo(f"Output: {output}")
    click.echo(f"Template: {template_version_identifier}")
    click.echo("=" * 60)

    # Close logger
    close_logger()
