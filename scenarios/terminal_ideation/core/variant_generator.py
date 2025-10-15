"""Generate diverse exploration variants from a single idea using AI."""

import logging
import uuid
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent

logger = logging.getLogger(__name__)


class Variant(BaseModel):
    """A single exploration variant."""

    id: str
    title: str
    prompt: str
    approach: str
    color: str


class VariantSet(BaseModel):
    """Set of generated variants."""

    variants: list[Variant]


# Terminal color palette for visual distinction
TERMINAL_COLORS = [
    "#FF6B6B",  # Coral red
    "#4ECDC4",  # Turquoise
    "#45B7D1",  # Sky blue
    "#96CEB4",  # Sage green
    "#FECA57",  # Golden yellow
    "#DDA0DD",  # Plum
    "#98D8C8",  # Mint
    "#FFB6C1",  # Light pink
    "#87CEEB",  # Sky blue
    "#F0E68C",  # Khaki
]


async def generate_variants(
    idea: str, num_variants: int = 3, variant_style: str = "exploratory"
) -> list[dict[str, Any]]:
    """
    Generate diverse exploration variants from a single idea/prompt using AI.

    Args:
        idea: The original idea or prompt to explore
        num_variants: Number of variants to generate (default 3)
        variant_style: Style of variants - "exploratory", "focused", or "creative"

    Returns:
        List of variant dictionaries with id, title, prompt, approach, and color

    Raises:
        ValueError: If AI fails to generate valid variants
    """

    # Create the AI agent for variant generation
    system_prompt = f"""You are an expert at generating diverse exploration angles for ideas.
Your task is to create {num_variants} distinct variants of the given idea.

Style: {variant_style}
- exploratory: Different perspectives and approaches to explore the idea
- focused: Specific technical implementations or solutions
- creative: Innovative and unconventional approaches

For each variant, provide:
1. A concise title (max 30 chars)
2. A detailed prompt for Claude Code to execute
3. The approach/perspective being taken

Ensure each variant explores a meaningfully different aspect or approach."""

    agent = Agent("claude-3-5-sonnet-20241022", system_prompt=system_prompt, result_type=VariantSet)

    try:
        # Generate variants using AI
        result = await agent.run(f"Generate {num_variants} variants for this idea: {idea}")

        # Convert to dictionaries and assign colors
        variants = []
        for i, variant in enumerate(result.data.variants):
            variant_dict = variant.model_dump()
            variant_dict["id"] = str(uuid.uuid4())[:8]
            variant_dict["color"] = TERMINAL_COLORS[i % len(TERMINAL_COLORS)]
            variants.append(variant_dict)

        logger.info(f"Generated {len(variants)} variants for idea")
        return variants

    except Exception as e:
        logger.error(f"Failed to generate variants: {e}")

        # Provide fallback variants
        fallback_variants = []
        for i in range(num_variants):
            fallback_variants.append(
                {
                    "id": str(uuid.uuid4())[:8],
                    "title": f"Variant {i + 1}",
                    "prompt": f"Explore aspect {i + 1} of: {idea}",
                    "approach": f"Standard approach {i + 1}",
                    "color": TERMINAL_COLORS[i % len(TERMINAL_COLORS)],
                }
            )

        logger.warning(f"Using {len(fallback_variants)} fallback variants")
        return fallback_variants


def generate_variants_sync(
    idea: str, num_variants: int = 3, variant_style: str = "exploratory"
) -> list[dict[str, Any]]:
    """
    Synchronous wrapper for generate_variants.

    This is for easier integration with non-async code.
    """
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(generate_variants(idea, num_variants, variant_style))
    finally:
        loop.close()
