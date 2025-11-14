"""Prompt templates for LLM calls with versioning support."""

from pathlib import Path
from typing import overload

import json


@overload
def load_prompt(name: str, return_version: bool = False) -> str: ...


@overload
def load_prompt(name: str, return_version: bool = True) -> tuple[str, str]: ...


def load_prompt(name: str, return_version: bool = False) -> str | tuple[str, str]:
    """
    Load the most recent version of a prompt template from file.

    Args:
        name: Name of the prompt file (without extension)
        return_version: If True, return tuple of (prompt, version)

    Returns:
        Prompt template content as string (most recent version)
        OR tuple of (prompt, version) if return_version=True

    Raises:
        FileNotFoundError: If prompt file doesn't exist
        ValueError: If prompt file is invalid or has no versions
    """
    prompts_dir = Path(__file__).parent
    prompt_file = prompts_dir / f"{name}.json"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_file}")

    with open(prompt_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "versions" not in data:
        raise ValueError(f"Invalid prompt file format: {prompt_file}")

    versions = data["versions"]
    if not versions or not isinstance(versions, list):
        raise ValueError(f"No versions found in prompt file: {prompt_file}")

    # Sort by version (timestamp) descending and get most recent
    sorted_versions = sorted(versions, key=lambda v: v["version"], reverse=True)
    most_recent = sorted_versions[0]

    if return_version:
        return (most_recent["prompt"], most_recent["version"])
    return most_recent["prompt"]


def get_prompt_version(name: str) -> str:
    """
    Get the version identifier of the most recent prompt.

    Args:
        name: Name of the prompt file (without extension)

    Returns:
        Version string (timestamp) of the most recent prompt version

    Raises:
        FileNotFoundError: If prompt file doesn't exist
        ValueError: If prompt file is invalid or has no versions
    """
    prompts_dir = Path(__file__).parent
    prompt_file = prompts_dir / f"{name}.json"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_file}")

    with open(prompt_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or "versions" not in data:
        raise ValueError(f"Invalid prompt file format: {prompt_file}")

    versions = data["versions"]
    if not versions or not isinstance(versions, list):
        raise ValueError(f"No versions found in prompt file: {prompt_file}")

    # Sort by version (timestamp) descending and get most recent
    sorted_versions = sorted(versions, key=lambda v: v["version"], reverse=True)

    return sorted_versions[0]["version"]
