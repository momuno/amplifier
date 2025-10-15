"""
Prompt templates for AI synthesis.

These templates guide the AI in analyzing and synthesizing repository content.
"""

from pathlib import Path


def get_file_synthesis_prompt(file_path: Path, content: str, topic: str) -> str:
    """
    Generate prompt for synthesizing a single file.

    Args:
        file_path: Path to the file
        content: File content
        topic: User's synthesis topic/question

    Returns:
        Complete prompt for file synthesis
    """
    return f"""Analyze this file and provide a synthesis focused on the topic: "{topic}"

File: {file_path.name}
Path: {file_path}

Content:
```
{content[:10000]}  # Truncate to avoid token limits
```

Please provide:
1. A brief summary of what this file does (1-2 sentences)
2. Key insights related to the topic "{topic}"
3. Any novel capabilities, patterns, or approaches relevant to the topic
4. Connections to broader concepts if applicable

Format your response as JSON:
{{
    "summary": "Brief description of the file's purpose",
    "key_insights": [
        "Insight 1 related to the topic",
        "Insight 2 related to the topic"
    ],
    "novel_capabilities": [
        "Any novel or interesting capabilities"
    ],
    "patterns": [
        "Notable patterns or approaches used"
    ],
    "relevance_to_topic": "How this file relates to '{topic}' (or 'Not directly relevant' if applicable)"
}}

Focus on extracting meaningful insights rather than listing obvious details."""


def get_directory_synthesis_prompt(dir_path: Path, child_syntheses: list[tuple[str, str]], topic: str) -> str:
    """
    Generate prompt for synthesizing a directory based on its children.

    Args:
        dir_path: Path to the directory
        child_syntheses: List of (child_name, synthesis) tuples
        topic: User's synthesis topic/question

    Returns:
        Complete prompt for directory synthesis
    """
    # Format child syntheses
    children_text = "\n\n".join(
        [
            f"### {name}\n{synthesis[:1000]}"  # Truncate each to manage tokens
            for name, synthesis in child_syntheses
        ]
    )

    return f"""Synthesize the contents of this directory based on the analyses of its contents.
Focus on the topic: "{topic}"

Directory: {dir_path.name}
Path: {dir_path}

Contents Analysis:
{children_text}

Please provide a higher-level synthesis that:
1. Identifies common themes and patterns across the files/subdirectories
2. Explains how the components work together
3. Highlights novel capabilities or approaches relevant to "{topic}"
4. Draws connections between different parts
5. Provides architectural or design insights

Format your response as JSON:
{{
    "overview": "High-level description of this directory's purpose and architecture",
    "common_themes": [
        "Theme that appears across multiple components"
    ],
    "key_insights": [
        "Important insight about how components work together"
    ],
    "novel_capabilities": [
        "Interesting or novel capabilities at this level"
    ],
    "architectural_patterns": [
        "Design patterns or architectural decisions visible"
    ],
    "integration_points": [
        "How different parts connect or communicate"
    ],
    "relevance_to_topic": "Overall relevance to '{topic}' and key findings"
}}

Synthesize at a higher level - don't just repeat details from individual files."""


def get_final_synthesis_prompt(root_synthesis: str, all_insights: list[str], topic: str) -> str:
    """
    Generate prompt for final repository-wide synthesis.

    Args:
        root_synthesis: Synthesis of the root directory
        all_insights: Collection of all key insights from the tree
        topic: User's synthesis topic/question

    Returns:
        Complete prompt for final synthesis
    """
    insights_text = "\n".join([f"- {insight}" for insight in all_insights[:50]])  # Limit to top insights

    return f"""Create a comprehensive synthesis of this entire repository focused on: "{topic}"

Root Directory Analysis:
{root_synthesis}

Key Insights from All Levels:
{insights_text}

Please provide a final synthesis that:
1. Answers the question: "{topic}"
2. Identifies the most important novel capabilities
3. Explains the overall architecture and design philosophy
4. Highlights unique or innovative approaches
5. Suggests potential applications or extensions
6. Provides actionable takeaways

Format your response as JSON:
{{
    "executive_summary": "2-3 sentence summary of findings related to '{topic}'",
    "novel_capabilities": [
        {{
            "capability": "Description of the capability",
            "significance": "Why this is important or innovative",
            "implementation": "Brief note on how it's implemented"
        }}
    ],
    "architecture_insights": [
        "Key architectural pattern or decision"
    ],
    "design_philosophy": "Overall design approach and principles",
    "unique_approaches": [
        "Innovative or unusual implementation approach"
    ],
    "potential_applications": [
        "How these patterns could be applied elsewhere"
    ],
    "key_takeaways": [
        "Most important learning or insight"
    ],
    "answer_to_topic": "Direct answer to the question '{topic}'"
}}

Focus on synthesis and insights rather than enumeration.
Prioritize novel and non-obvious findings."""
