"""Repository Synthesizer - Extract insights from repository structure.

A hybrid code+AI tool that analyzes repositories layer-by-layer to extract
novel capabilities, interesting problems solved, and enlightening experiences.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from amplifier.ccsdk_toolkit import ToolkitLogger

from .core.orchestrator import RepoSynthesizer

logger = ToolkitLogger("repo_synthesizer")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Synthesize insights from repository structure")

    parser.add_argument(
        "--repo-path", type=Path, default=Path.cwd(), help="Path to repository to analyze (default: current directory)"
    )

    parser.add_argument("--topic", type=str, required=True, help="Synthesis topic or question to explore")

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("repository_synthesis.md"),
        help="Output path for synthesis (default: repository_synthesis.md)",
    )

    parser.add_argument("--resume", type=str, help="Resume session with given ID")

    parser.add_argument("--max-depth", type=int, default=10, help="Maximum directory depth to analyze (default: 10)")

    parser.add_argument("--include", type=str, help="Comma-separated file patterns to include (e.g., '*.py,*.md')")

    parser.add_argument(
        "--exclude", type=str, help="Comma-separated patterns to exclude (e.g., '__pycache__,node_modules')"
    )

    parser.add_argument("--no-paper-trail", action="store_true", help="Don't create paper trail of intermediate files")

    args = parser.parse_args()

    # Parse patterns
    include_patterns = args.include.split(",") if args.include else None
    exclude_patterns = args.exclude.split(",") if args.exclude else None

    # Validate repo path
    if not args.repo_path.exists():
        logger.error(f"Repository path not found: {args.repo_path}")
        sys.exit(1)

    # Create synthesizer
    synthesizer = RepoSynthesizer(
        repo_path=args.repo_path.resolve(),
        topic=args.topic,
        output_path=args.output,
        max_depth=args.max_depth,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        resume_session=args.resume,
        paper_trail=not args.no_paper_trail,
    )

    # Run synthesis
    try:
        asyncio.run(synthesizer.synthesize())
    except KeyboardInterrupt:
        logger.warning("Synthesis interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
