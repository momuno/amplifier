"""Document generation service integrating with doc-evergreen."""

from __future__ import annotations

import asyncio
import io
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

from doc_evergreen.commands.create import execute_create

from doc_studio.api.sse import sse_manager
from doc_studio.models.events import ProgressEvent
from doc_studio.models.state import GenerationJob
from doc_studio.models.state import JobStatus
from doc_studio.models.state import Template


class GenerationService:
    """Service for document generation with real-time progress updates."""

    def __init__(self, workspace_path: str) -> None:
        """Initialize generation service.

        Args:
            workspace_path: Path to workspace directory
        """
        self.workspace_path = Path(workspace_path)

    async def generate_document(self, template: Template, output_path: str, job_id: str) -> GenerationJob:
        """Generate a document from a template.

        Args:
            template: Template to use for generation
            output_path: Path to write generated document
            job_id: Unique job identifier for SSE events

        Returns:
            GenerationJob with final status
        """
        job = GenerationJob(
            id=job_id,
            template_name=template.name,
            status=JobStatus.RUNNING,
            progress=0.0,
            result_path=output_path,
            started_at=datetime.now(),
        )

        resource_id = f"job:{job_id}"

        try:
            # Send initial progress event
            await sse_manager.send_progress(
                resource_id,
                ProgressEvent(
                    job_id=job_id,
                    stage="initialization",
                    progress=0.0,
                    message="Starting document generation",
                ),
            )

            # Stage 1: Collect source files (20%)
            await self._collect_sources(template, resource_id, job_id)
            job.progress = 0.2

            # Stage 2: Process sections (60%)
            await self._process_sections(template, resource_id, job_id)
            job.progress = 0.8

            # Stage 3: Write output (20%)
            await self._write_output(template, output_path, resource_id, job_id)
            job.progress = 1.0

            # Mark as complete
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()

            await sse_manager.send_progress(
                resource_id,
                ProgressEvent(
                    job_id=job_id,
                    stage="complete",
                    progress=1.0,
                    message=f"Document generated successfully: {output_path}",
                ),
            )

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now()

            await sse_manager.send_progress(
                resource_id,
                ProgressEvent(
                    job_id=job_id,
                    stage="error",
                    progress=job.progress,
                    message=f"Generation failed: {e}",
                ),
            )

        return job

    async def _collect_sources(self, template: Template, resource_id: str, job_id: str) -> None:
        """Collect and validate source files.

        Args:
            template: Template with source files
            resource_id: Resource ID for SSE events
            job_id: Job identifier
        """
        await sse_manager.send_progress(
            resource_id,
            ProgressEvent(
                job_id=job_id,
                stage="collecting",
                progress=0.05,
                message="Collecting source files...",
            ),
        )

        # Simulate collection work
        await asyncio.sleep(0.5)

        total_files = sum(len(section.source_files) for section in template.sections)

        await sse_manager.send_progress(
            resource_id,
            ProgressEvent(
                job_id=job_id,
                stage="collecting",
                progress=0.2,
                message=f"Found {total_files} source files across {len(template.sections)} sections",
            ),
        )

    async def _process_sections(self, template: Template, resource_id: str, job_id: str) -> None:
        """Process template sections.

        Args:
            template: Template to process
            resource_id: Resource ID for SSE events
            job_id: Job identifier
        """
        total_sections = len(template.sections)

        for i, section in enumerate(template.sections):
            progress = 0.2 + (i / total_sections) * 0.6

            await sse_manager.send_progress(
                resource_id,
                ProgressEvent(
                    job_id=job_id,
                    stage="processing",
                    progress=progress,
                    message=f"Processing section: {section.title}",
                ),
            )

            # Simulate processing work
            await asyncio.sleep(0.5)

    async def _write_output(self, template: Template, output_path: str, resource_id: str, job_id: str) -> None:
        """Write generated document to file using doc-evergreen.

        Args:
            template: Template used for generation
            output_path: Path to write output
            resource_id: Resource ID for SSE events
            job_id: Job identifier
        """
        await sse_manager.send_progress(
            resource_id,
            ProgressEvent(
                job_id=job_id,
                stage="generating",
                progress=0.85,
                message="Generating document with doc-evergreen...",
            ),
        )

        # Prepare parameters for doc-evergreen
        output_file = self.workspace_path / output_path

        # Collect all source files from template sections
        all_sources = []
        for section in template.sections:
            all_sources.extend(section.source_files)

        # Remove duplicates while preserving order
        unique_sources = list(dict.fromkeys(all_sources))

        # Build "about" description from template
        about = template.description or f"Documentation for {template.name}"

        # Use template name if it exists in doc-evergreen, otherwise use 'default'
        template_name = template.name if template.name in ["default", "api", "guide", "technical"] else None

        try:
            # Capture stdout to send as progress updates
            stdout_capture = io.StringIO()

            # Run doc-evergreen generation in thread pool (it's synchronous)
            await asyncio.to_thread(
                self._run_doc_evergreen_with_capture,
                about=about,
                output=output_file,
                sources=unique_sources if unique_sources else None,
                template=template_name,
                stdout_capture=stdout_capture,
            )

            # Send captured output as progress
            output_lines = stdout_capture.getvalue().strip().split("\n")
            for line in output_lines[-5:]:  # Send last 5 lines as summary
                if line.strip():
                    await sse_manager.send_progress(
                        resource_id,
                        ProgressEvent(
                            job_id=job_id,
                            stage="generating",
                            progress=0.95,
                            message=line.strip(),
                        ),
                    )

            await sse_manager.send_progress(
                resource_id,
                ProgressEvent(
                    job_id=job_id,
                    stage="complete",
                    progress=1.0,
                    message=f"Document generated successfully: {output_path}",
                ),
            )

        except Exception as e:
            # If doc-evergreen fails, provide helpful error message
            error_msg = f"doc-evergreen generation failed: {str(e)}"
            await sse_manager.send_progress(
                resource_id,
                ProgressEvent(
                    job_id=job_id,
                    stage="error",
                    progress=0.85,
                    message=error_msg,
                ),
            )
            raise RuntimeError(error_msg)

    def _run_doc_evergreen_with_capture(
        self,
        about: str,
        output: Path,
        sources: list[str] | None,
        template: str | None,
        stdout_capture: io.StringIO,
    ) -> None:
        """Run doc-evergreen with stdout capture.

        Args:
            about: Description for documentation
            output: Output file path
            sources: Source file patterns
            template: Template name
            stdout_capture: StringIO to capture stdout
        """
        import os

        # Change to workspace directory before running doc-evergreen
        # This avoids interactive prompts about subdirectory execution
        original_cwd = Path.cwd()
        try:
            os.chdir(self.workspace_path)
            with redirect_stdout(stdout_capture):
                execute_create(
                    about=about,
                    output=output,
                    sources=sources,
                    template=template,
                    should_customize_template=None,  # Let doc-evergreen decide
                    dry_run=False,
                )
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
