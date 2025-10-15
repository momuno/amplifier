#!/usr/bin/env python3
"""
Terminal Ideation Tool - Explore ideas in parallel with Claude Code.

This tool spawns multiple Claude Code sessions in separate terminals,
each exploring a different variant of your idea in parallel.
"""

import argparse
import logging
import sys
from pathlib import Path

from core.progress_tracker import get_all_sessions
from core.progress_tracker import get_session_status
from core.session_orchestrator import cleanup_session
from core.session_orchestrator import orchestrate_session

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the terminal ideation tool."""
    parser = argparse.ArgumentParser(
        description="Explore ideas in parallel with Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Explore an idea with 3 default variants
  %(prog)s "Create a web scraper for news articles"

  # Generate 5 focused technical variants
  %(prog)s "Implement a caching system" --variants 5 --style focused

  # Generate creative approaches without auto-execution
  %(prog)s "Design a user authentication flow" --style creative --no-auto

  # List all sessions
  %(prog)s --list

  # Check status of a specific session
  %(prog)s --status abc12345

  # Clean up a completed session
  %(prog)s --cleanup abc12345
        """,
    )

    # Main idea argument (optional for list/status/cleanup operations)
    parser.add_argument("idea", nargs="?", help="The idea or prompt to explore in parallel")

    # Variant configuration
    parser.add_argument("-n", "--variants", type=int, default=3, help="Number of variants to generate (default: 3)")

    parser.add_argument(
        "-s",
        "--style",
        choices=["exploratory", "focused", "creative"],
        default="exploratory",
        help="Style of variants to generate (default: exploratory)",
    )

    # Execution options
    parser.add_argument("--no-auto", action="store_true", help="Don't auto-execute prompts in Claude Code")

    parser.add_argument("-b", "--base-branch", default="main", help="Git branch to base worktrees on (default: main)")

    # Session management
    parser.add_argument("--list", action="store_true", help="List all ideation sessions")

    parser.add_argument("--status", metavar="SESSION_ID", help="Show status of a specific session")

    parser.add_argument("--cleanup", metavar="SESSION_ID", help="Clean up a completed session (removes worktrees)")

    # Other options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Handle session management operations
    if args.list:
        list_sessions()
        return 0

    if args.status:
        show_session_status(args.status)
        return 0

    if args.cleanup:
        cleanup_session_interactive(args.cleanup)
        return 0

    # For main operation, idea is required
    if not args.idea:
        parser.error("An idea is required (unless using --list, --status, or --cleanup)")

    # Validate variant count
    if args.variants < 1 or args.variants > 10:
        parser.error("Number of variants must be between 1 and 10")

    # Run the main orchestration
    try:
        logger.info("=" * 60)
        logger.info("Terminal Ideation Tool")
        logger.info("=" * 60)
        logger.info(f"Idea: {args.idea}")
        logger.info(f"Variants: {args.variants} ({args.style})")
        logger.info(f"Auto-execute: {not args.no_auto}")
        logger.info(f"Base branch: {args.base_branch}")
        logger.info("=" * 60)

        result = orchestrate_session(
            idea=args.idea,
            num_variants=args.variants,
            auto_execute=not args.no_auto,
            variant_style=args.style,
            base_branch=args.base_branch,
        )

        print("\n" + "=" * 60)
        print("✅ Session launched successfully!")
        print(f"Session ID: {result['session_id']}")
        print(f"Variants launched: {result['successful']}/{result['total']}")
        print(f"Status tracking: {result['status_file']}")
        print("=" * 60)

        if result["successful"] > 0:
            print("\n🚀 Your variants are now running in separate terminals!")
            print("Each terminal tab has a different color and shows the variant title.")
            print("\nTo check status later, run:")
            print(f"  python terminal_ideation.py --status {result['session_id']}")
            print("\nWhen done, clean up with:")
            print(f"  python terminal_ideation.py --cleanup {result['session_id']}")

        return 0

    except Exception as e:
        logger.error(f"Failed to launch ideation session: {e}")
        return 1


def list_sessions():
    """List all ideation sessions."""
    sessions = get_all_sessions()

    if not sessions:
        print("No ideation sessions found.")
        return

    print("\n" + "=" * 80)
    print("Ideation Sessions")
    print("=" * 80)

    for session in sessions:
        print(f"\nSession ID: {session['session_id']}")
        print(f"  Created: {session['created']}")
        print(f"  Idea: {session['idea'][:60]}...")
        print(f"  Variants: {session['total_variants']} total")
        print(
            f"  Status: ✅ {session['completed']} completed, "
            f"🚀 {session['running']} running, "
            f"❌ {session['failed']} failed"
        )


def show_session_status(session_id: str):
    """Show detailed status of a specific session."""
    status_dir = Path.home() / ".amplifier" / "ideation_status"
    status_file = status_dir / f"{session_id}.json"

    if not status_file.exists():
        print(f"Session {session_id} not found.")
        return

    try:
        status_data = get_session_status(status_file)

        print("\n" + "=" * 80)
        print(f"Session {session_id} Status")
        print("=" * 80)
        print(f"Created: {status_data['created']}")
        print(f"Idea: {status_data.get('idea', 'Unknown')}")
        print("\nVariants:")

        for variant in status_data["variants"]:
            status_emoji = {"pending": "⏳", "running": "🚀", "completed": "✅", "failed": "❌"}.get(
                variant["status"], "❓"
            )

            print(f"\n  {status_emoji} {variant['title']} (ID: {variant['id']})")
            print(f"     Status: {variant['status']}")
            print(f"     Approach: {variant['approach']}")
            print(f"     Last update: {variant['last_update']}")
            if variant.get("worktree"):
                print(f"     Worktree: {variant['worktree']}")

    except Exception as e:
        print(f"Error reading session status: {e}")


def cleanup_session_interactive(session_id: str):
    """Interactively clean up a session."""
    status_dir = Path.home() / ".amplifier" / "ideation_status"
    status_file = status_dir / f"{session_id}.json"

    if not status_file.exists():
        print(f"Session {session_id} not found.")
        return

    # Show session status first
    show_session_status(session_id)

    print("\n" + "=" * 80)
    print("⚠️  WARNING: This will remove all worktrees and branches for this session.")
    print("Make sure to close all terminal windows for this session first.")
    print("=" * 80)

    response = input("\nProceed with cleanup? (y/N): ")
    if response.lower() != "y":
        print("Cleanup cancelled.")
        return

    try:
        cleanup_session(session_id)
        print(f"✅ Session {session_id} cleaned up successfully.")
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")


if __name__ == "__main__":
    sys.exit(main())
