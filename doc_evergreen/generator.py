"""LLM-based documentation generator."""

import logging
import sys
import time

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a technical documentation writer. Your task is to complete markdown documentation templates by filling in placeholders using provided context.

Requirements:
- Maintain the template's markdown structure exactly
- Replace ALL placeholders with relevant content from context
- Use clear, concise technical writing
- Preserve all markdown formatting (headers, lists, code blocks)
- Return ONLY the completed markdown (no preamble/postamble)"""


def _create_agent() -> Agent:
    """Create PydanticAI agent for documentation generation."""
    return Agent(model=AnthropicModel("claude-sonnet-4-5-20250929"), system_prompt=SYSTEM_PROMPT)


def _build_user_prompt(template: str, context: str) -> str:
    """Build user prompt for LLM."""
    return f"""Complete this documentation template using the provided context.

TEMPLATE:
{template}

CONTEXT:
{context}

Return the completed markdown document."""


def _generate_with_retry(agent: Agent, user_prompt: str, max_retries: int = 3) -> str:
    """Generate documentation with retry logic."""
    for attempt in range(max_retries):
        try:
            result = agent.run_sync(user_prompt)
            output = result.output

            if not output or not output.strip():
                raise ValueError("LLM returned empty output")

            return output.strip()

        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"LLM generation failed after {max_retries} attempts: {e}")
                sys.exit(1)
            else:
                logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                time.sleep(1)

    raise RuntimeError("Unexpected retry loop exit")


def generate_doc(template: str, context: str) -> str:
    """Generate documentation by completing template with context.

    Args:
        template: Markdown template with placeholders
        context: Gathered context to use for completion

    Returns:
        Completed markdown documentation

    Raises:
        SystemExit: If LLM generation fails after retries
    """
    agent = _create_agent()
    user_prompt = _build_user_prompt(template, context)
    return _generate_with_retry(agent, user_prompt)
