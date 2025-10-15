#!/usr/bin/env python3
"""
Test the terminal ideation tool with manual variants (no AI required).
"""

import logging

from core.session_orchestrator import orchestrate_session


# Mock the variant generator to return predefined variants
def mock_generate_variants(idea, num_variants, variant_style):
    """Return predefined sudoku solver UX variants."""

    variants = [
        {
            "id": "variant1",
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
            "id": "variant2",
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
            "id": "variant3",
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
            "id": "variant4",
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
            "id": "variant5",
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

    return variants[:num_variants]


# Monkey-patch the variant generator
import core.variant_generator

core.variant_generator.generate_variants_sync = mock_generate_variants

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Run the orchestration
if __name__ == "__main__":
    idea = "What are different front end UX approaches for a sudoku solver?"

    print("\n" + "=" * 60)
    print("Testing Terminal Ideation Tool with Manual Variants")
    print("=" * 60)
    print(f"Idea: {idea}")
    print("Variants: 5 predefined sudoku solver UX approaches")
    print("=" * 60 + "\n")

    try:
        result = orchestrate_session(idea=idea, num_variants=5, auto_execute=True, variant_style="creative")

        print("\n✅ Test launch successful!")
        print(f"Session ID: {result['session_id']}")
        print(f"Variants launched: {result['successful']}/{result['total']}")

        if result["successful"] > 0:
            print("\n🚀 The following variants are now running in separate terminals:")
            for v in result["variants"][: result["successful"]]:
                print(f"  - {v['title']}: {v['approach']}")

            print("\nCheck status with:")
            print(f"  make ideate-status SESSION={result['session_id']}")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
