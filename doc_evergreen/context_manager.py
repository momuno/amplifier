"""Context manager for tracking and managing section context flow."""

import logging
from collections import deque
from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

logger = logging.getLogger(__name__)


@dataclass
class GeneratedSection:
    """A generated documentation section with summary."""

    heading: str
    content: str
    summary: str = ""


async def summarize_with_llm(content: str) -> str:
    """Generate a 3-5 sentence summary of content using LLM.

    Args:
        content: Content to summarize

    Returns:
        Concise summary (3-5 sentences)
    """
    agent = Agent(
        model=AnthropicModel("claude-sonnet-4-5-20250929"),
        system_prompt="You are a technical writer. Summarize content in 3-5 concise sentences.",
    )

    prompt = f"Summarize this content in 3-5 sentences:\n\n{content}"
    result = await agent.run(prompt)
    return result.output.strip()


class ContextManager:
    """Manages context flow between documentation sections."""

    def __init__(self, max_context_sections: int = 10, model: str | None = None):
        """Initialize context manager.

        Args:
            max_context_sections: Maximum number of sections to keep in context
            model: Optional model for summarization (defaults to Claude Sonnet 4.5)
        """
        self._sections_deque: deque[GeneratedSection] = deque(maxlen=max_context_sections)
        self.max_context_sections = max_context_sections
        self.model = model or AnthropicModel("claude-sonnet-4-5-20250929")

    @property
    def sections(self) -> list[GeneratedSection]:
        """Get sections as a list for compatibility."""

        # Return a special list subclass that supports append to the underlying deque
        class SectionsList(list):
            def __init__(self, deque_ref):
                super().__init__(deque_ref)
                self._deque = deque_ref

            def append(self, item):
                self._deque.append(item)
                # Update the list itself
                super().clear()
                super().extend(self._deque)

        return SectionsList(self._sections_deque)

    async def add_section(self, heading: str, content: str) -> None:
        """Add a section and generate its summary.

        Args:
            heading: Section heading
            content: Section content
        """
        # Create section
        section = GeneratedSection(heading=heading, content=content, summary="")
        self._sections_deque.append(section)

        # Generate summary asynchronously
        try:
            summary = await self.summarize_section(heading, content)
            section.summary = summary
        except Exception as e:
            logger.warning(f"Failed to generate summary for '{heading}': {e}")
            section.summary = ""

    def get_context_for_section(self, section_index: int) -> str:
        """Get formatted context from all previous sections.

        Args:
            section_index: Index of current section (0-based)

        Returns:
            Formatted context string with all previous sections

        Raises:
            IndexError: If section_index is out of bounds
        """
        sections_list = list(self._sections_deque)

        # section_index represents the section we're ABOUT to generate
        # So it can be equal to len(sections_list) (next section to add)
        # But not greater than that
        if section_index > len(sections_list):
            raise IndexError(f"Section index {section_index} out of bounds")

        if section_index == 0:
            return ""

        # Get all sections before the current one
        previous_sections = sections_list[:section_index]

        if not previous_sections:
            return ""

        # Format context
        lines = ["Previous Sections Context:", ""]

        for section in previous_sections:
            lines.append(f"## {section.heading}")
            if section.summary:
                lines.append(f"Summary: {section.summary}")
            lines.append("")

        return "\n".join(lines)

    async def summarize_section(self, heading: str, content: str) -> str:
        """Generate summary for a section using LLM.

        Args:
            heading: Section heading
            content: Section content

        Returns:
            3-5 sentence summary
        """
        try:
            agent = Agent(
                model=self.model,
                system_prompt="You are a technical writer. Summarize content in 3-5 concise sentences.",
            )
            prompt = f"Summarize this content in 3-5 sentences:\n\n{content}"
            result = await agent.run(prompt)
            return result.output.strip()
        except Exception as e:
            logger.warning(f"LLM summarization failed for '{heading}': {e}")
            # Fallback to first 500 characters
            if len(content) > 500:
                return content[:500] + "..."
            return content
