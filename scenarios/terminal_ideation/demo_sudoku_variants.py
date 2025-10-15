#!/usr/bin/env python3
"""
Demo the terminal ideation tool with predefined sudoku solver UX variants.
This bypasses AI generation to show the terminal spawning functionality.
"""

import logging
import uuid

from core.progress_tracker import initialize_tracking
from core.progress_tracker import update_variant_status
from core.terminal_spawner import spawn_terminal

# Import the necessary components
from core.worktree_manager import create_worktree

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Predefined sudoku solver UX variants
SUDOKU_VARIANTS = [
    {
        "id": str(uuid.uuid4())[:8],
        "title": "Minimalist Grid",
        "prompt": """Create a minimalist sudoku solver with a clean, distraction-free interface:
- Simple 9x9 grid with thin borders
- Monochrome color scheme (black, white, gray)
- Subtle hover effects
- Number input via keyboard only
- Small solve button at bottom
- No animations, pure functionality
Build this using HTML/CSS/JavaScript with focus on simplicity.""",
        "approach": "Minimalist design focusing on pure functionality",
        "color": "#FF6B6B",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "title": "Gamified Experience",
        "prompt": """Create a gamified sudoku solver with engaging visual feedback:
- Animated number placement with particle effects
- Progress bar showing completion percentage
- Achievement badges for solving patterns
- Timer with high score tracking
- Sound effects for valid/invalid moves
- Colorful, playful design with gradients
Build this with React and CSS animations for smooth interactions.""",
        "approach": "Game-like interface with rewards and feedback",
        "color": "#4ECDC4",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "title": "AI Assistant Mode",
        "prompt": """Create an AI-assisted sudoku solver with smart hints:
- Split screen: puzzle on left, AI assistant chat on right
- AI provides hints in natural language
- Step-by-step solving explanations
- Difficulty adjustment based on user performance
- Voice input option for numbers
- Dark mode with neon accents
Build this with a modern framework and integrate AI hint generation.""",
        "approach": "AI-powered assistant providing intelligent guidance",
        "color": "#45B7D1",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "title": "3D Interactive",
        "prompt": """Create a 3D rotating sudoku cube interface:
- Sudoku grid on a rotating 3D cube
- Gesture controls for rotation
- Each face shows different puzzle views
- Depth effects and shadows
- Smooth transitions between cells
- Futuristic holographic appearance
Build this using Three.js or similar 3D library.""",
        "approach": "3D visualization with innovative navigation",
        "color": "#96CEB4",
    },
    {
        "id": str(uuid.uuid4())[:8],
        "title": "Accessibility First",
        "prompt": """Create a fully accessible sudoku solver:
- High contrast mode toggle
- Large, clear fonts with size adjustment
- Screen reader optimized markup
- Keyboard-only navigation with visual focus indicators
- Color blind friendly palette options
- Voice commands for number entry
- Tutorial mode with step-by-step instructions
Build this following WCAG 2.1 AAA standards.""",
        "approach": "Maximum accessibility for all users",
        "color": "#FECA57",
    },
]


def demo_sudoku_ideation():
    """Demo the terminal ideation tool with sudoku solver variants."""

    session_id = str(uuid.uuid4())[:8]
    print("\n" + "=" * 60)
    print("🚀 Terminal Ideation Tool Demo - Sudoku Solver UX")
    print("=" * 60)
    print(f"Session ID: {session_id}")
    print("Launching 5 different UX approaches for a sudoku solver...")
    print("=" * 60 + "\n")

    successful_variants = []
    failed_variants = []

    # Process each variant
    for i, variant in enumerate(SUDOKU_VARIANTS):
        print(f"Processing variant {i + 1}/5: {variant['title']}")

        try:
            # Create worktree for this variant
            print(f"  Creating worktree for variant {variant['id']}...")
            worktree_result = create_worktree(variant["id"])

            variant["worktree_path"] = worktree_result["worktree_path"]
            variant["branch_name"] = worktree_result["branch_name"]

            # Spawn terminal for this variant
            print(f"  Spawning terminal with {variant['color']} tab...")
            terminal_result = spawn_terminal(
                variant,
                worktree_result["worktree_path"],
                auto_execute=True,  # Auto-execute the prompt in Claude Code
            )

            variant["tab_id"] = terminal_result["tab_id"]
            variant["pid"] = terminal_result["pid"]
            variant["launch_time"] = terminal_result["launch_time"]

            successful_variants.append(variant)
            print(f"  ✅ Successfully launched: {variant['title']}")

        except Exception as e:
            print(f"  ❌ Failed to launch: {e}")
            variant["error"] = str(e)
            failed_variants.append(variant)

    # Initialize progress tracking
    all_variants = successful_variants + failed_variants
    status_file = initialize_tracking(session_id, all_variants)

    # Update statuses
    for variant in failed_variants:
        update_variant_status(status_file, variant["id"], "failed")

    for variant in successful_variants:
        update_variant_status(status_file, variant["id"], "running")

    # Print summary
    print("\n" + "=" * 60)
    print("✅ Demo Launch Complete!")
    print(f"Session ID: {session_id}")
    print(f"Successful launches: {len(successful_variants)}/5")
    print(f"Status file: {status_file}")
    print("=" * 60)

    if successful_variants:
        print("\n🎨 The following sudoku solver UX variants are now open:")
        for v in successful_variants:
            print(f"  {v['color']} {v['title']}: {v['approach']}")

        print("\n📝 Claude Code is auto-executing the prompt in each terminal!")
        print("The prompts are saved in .claude_prompt.txt files in each worktree")

        print("\n📊 Check status with:")
        print(f"  make ideate-status SESSION={session_id}")

        print("\n🧹 Clean up when done with:")
        print(f"  make ideate-cleanup SESSION={session_id}")


if __name__ == "__main__":
    try:
        demo_sudoku_ideation()
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
