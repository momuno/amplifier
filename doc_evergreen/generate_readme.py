#!/usr/bin/env python3
"""Main script to generate README documentation with preview workflow."""

import sys
from pathlib import Path

from doc_evergreen.context import gather_context
from doc_evergreen.diff import show_diff
from doc_evergreen.file_ops import accept_changes
from doc_evergreen.file_ops import reject_changes
from doc_evergreen.preview import generate_preview
from doc_evergreen.template import load_template


def main() -> None:
    """Generate README.md with preview and review workflow."""
    print("📝 Generating README documentation...\n")

    # Target file
    target_file = "README.md"
    target_path = Path(target_file)

    # Load template
    print("  Loading template...")
    template_path = "doc_evergreen/templates/readme-template.md"
    template = load_template(template_path)
    print(f"  ✓ Template loaded ({len(template)} characters)")

    # Gather context
    print("  Gathering context from source files...")
    context = gather_context()
    print(f"  ✓ Context gathered ({len(context)} characters)")

    # Generate preview
    print("  Generating preview with LLM...")
    preview_path = generate_preview(template, context, target_file, output_dir=Path("."))
    print(f"  ✓ Preview generated: {preview_path}")

    # Show diff if original exists
    print("\n" + "=" * 60)
    print("CHANGES")
    print("=" * 60 + "\n")

    if target_path.exists():
        show_diff(str(target_path), str(preview_path))
    else:
        print(f"Note: {target_file} doesn't exist yet - this will be a new file")
        print(f"Preview contains {len(preview_path.read_text())} characters")

    # Prompt for action
    print("\n" + "=" * 60)
    print("REVIEW")
    print("=" * 60)
    print("\nOptions:")
    print("  y - Accept changes and update", target_file)
    print("  n - Reject changes and keep original")
    print()

    while True:
        choice = input("Accept changes? (y/n): ").lower().strip()

        if choice == "y":
            accept_changes(target_path, preview_path)
            print(f"\n✅ Accepted: {target_file} updated successfully")
            break
        if choice == "n":
            reject_changes(preview_path)
            print(f"\n❌ Rejected: {target_file} unchanged, preview deleted")
            break
        print("Invalid choice. Please enter 'y' or 'n'.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
