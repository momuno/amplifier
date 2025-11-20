"""Chunked document generator with section-by-section generation.

Implements stack-based DFS traversal with upfront source validation.
"""

import logging
import time
from collections.abc import Callable
from collections.abc import Iterator
from pathlib import Path

from pydantic_ai import Agent

from doc_evergreen.context_manager import ContextManager
from doc_evergreen.core.source_validator import SourceValidationError
from doc_evergreen.core.source_validator import validate_all_sources
from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template

logger = logging.getLogger(__name__)


def traverse_dfs(sections: list[Section]) -> Iterator[Section]:
    """Traverse sections in depth-first order using explicit stack.

    Args:
        sections: List of top-level sections

    Yields:
        Section objects in DFS order
    """
    stack: list[Section] = []

    # Push sections in reverse order (so they pop in correct order)
    for section in reversed(sections):
        stack.append(section)

    while stack:
        section = stack.pop()
        yield section

        # Push children in reverse order for correct DFS traversal
        if section.sections:
            for child in reversed(section.sections):
                stack.append(child)


class ChunkedGenerator:
    """Generate documentation section-by-section with explicit prompts."""

    def __init__(self, template: Template, base_dir: Path, model: str | None = None):
        """Initialize generator with template and base directory.

        Args:
            template: Template defining document structure
            base_dir: Base directory for resolving source files
            model: Optional model name/instance for testing (defaults to Claude Sonnet 4.5)
        """
        self.template = template
        self.base_dir = base_dir
        self.model = model or "anthropic:claude-sonnet-4-5-20250929"
        self.context_manager = ContextManager(model=self.model)

        # Agent will be initialized lazily
        self._agent: Agent | None = None

    @property
    def agent(self) -> Agent:
        """Get or create the LLM agent (lazy initialization)."""
        if self._agent is None:
            self._agent = Agent(
                self.model,
                system_prompt="You are a technical documentation writer. Generate clear, accurate documentation.",
            )
        return self._agent

    async def generate(self, progress_callback: Callable[[str], None] | None = None) -> str:
        """Generate complete document section-by-section.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            Complete markdown document

        Raises:
            SourceValidationError: If source validation fails
        """
        # 1. Validate sources upfront (fail fast)
        logger.info("Validating sources...")
        validation = validate_all_sources(self.template, self.base_dir)

        if not validation.valid:
            raise SourceValidationError(f"Source validation failed: {validation.errors}")

        # 2. Initialize
        markdown_parts: list[str] = []

        # Count total sections for progress tracking
        all_sections = list(traverse_dfs(self.template.document.sections))
        total_sections = len(all_sections)

        # 3. Traverse and generate sections
        for idx, section in enumerate(all_sections, 1):
            logger.info(f"Generating: {section.heading}")

            # Get resolved sources for this section
            sources = validation.section_sources.get(section.heading, [])
            logger.info(f"  Sources: {len(sources)} files")

            # Progress: Starting section
            if progress_callback:
                source_names = [s.name for s in sources]
                source_desc = ", ".join(source_names) if source_names else "No sources"
                file_count = f"{len(sources)} file" if len(sources) == 1 else f"{len(sources)} files"

                progress_callback(f"[{idx}/{total_sections}] Generating: {section.heading}\n")
                progress_callback(f"      Sources: {source_desc} ({file_count})\n")

            # Track timing
            start_time = time.time()

            # Get context from previous sections
            section_index = len(markdown_parts)
            context = self.context_manager.get_context_for_section(section_index)

            # Generate section content
            content = await self.generate_section(section, sources, context)

            # Track in context manager
            await self.context_manager.add_section(section.heading, content)

            # Accumulate markdown
            markdown_parts.append(content)

            # Progress: Section complete
            if progress_callback:
                elapsed = time.time() - start_time
                progress_callback(f"      ✓ Complete ({elapsed:.1f}s)\n")

        # 4. Assemble complete document
        return "\n\n".join(markdown_parts)

    async def generate_section(self, section: Section, sources: list[Path], context: str) -> str:
        """Generate a single section with LLM.

        Args:
            section: Section to generate
            sources: Resolved source files for this section
            context: Context from previous sections

        Returns:
            Generated markdown content (including heading)

        Raises:
            ValueError: If section has no prompt
        """
        # Validate prompt exists
        if section.prompt is None:
            raise ValueError(
                f"Section '{section.heading}' has no prompt.\n"
                f"Fix: Add a 'prompt' field to this section in your template:\n"
                f'  "prompt": "Instructions for generating this section..."\n'
                f"See: TEMPLATES.md#writing-effective-prompts"
            )

        # Read source files
        source_content_parts = []
        for source_path in sources:
            try:
                content = source_path.read_text(encoding="utf-8")
                source_content_parts.append(f"=== {source_path.name} ===\n{content}")
            except Exception as e:
                logger.warning(f"Failed to read {source_path}: {e}")

        source_content = "\n\n".join(source_content_parts) if source_content_parts else "No source files."

        # Build user prompt
        user_prompt = f"""Generate content for this section:

## Section Prompt
{section.prompt}

## Source Materials
{source_content}

## Context from Previous Sections
{context if context else "This is the first section."}

Write in clear markdown. Include the section heading at the start."""

        # Call LLM
        content = await self._call_llm(user_prompt)

        return content

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt.

        Args:
            prompt: User prompt

        Returns:
            Generated content
        """
        result = await self.agent.run(prompt)
        return result.output
