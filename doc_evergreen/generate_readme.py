#!/usr/bin/env python3
"""Main script to generate README documentation."""

import sys
from pathlib import Path

from doc_evergreen.context import gather_context
from doc_evergreen.generator import generate_doc
from doc_evergreen.template import load_template


def main() -> None:
    """Generate README.md from template and codebase context."""
    print("📝 Generating README documentation...")

    # Load template
    print("  Loading template...")
    template_path = "doc_evergreen/templates/readme-template.md"
    template = load_template(template_path)
    print(f"  ✓ Template loaded ({len(template)} characters)")

    # Gather context
    print("  Gathering context from source files...")
    context = gather_context()
    print(f"  ✓ Context gathered ({len(context)} characters)")

    # Generate documentation
    print("  Generating documentation with LLM...")
    generated = generate_doc(template, context)
    print(f"  ✓ Documentation generated ({len(generated)} characters)")

    # Write output
    output_path = Path("README.generated.md")
    output_path.write_text(generated, encoding="utf-8")
    print(f"\n✓ Generated: {output_path}")
    print("\nNext steps:")
    print("  1. Review README.generated.md")
    print("  2. Compare with current README.md")
    print("  3. Evaluate quality (80%+ acceptable?)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
