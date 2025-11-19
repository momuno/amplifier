#!/usr/bin/env python3
"""
Wrapper script to run doc-update CLI.
Usage: python doc-update.py [OPTIONS] [TARGET_FILE]
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import doc_evergreen
sys.path.insert(0, str(Path(__file__).parent.parent))

from doc_evergreen.cli import doc_update

if __name__ == "__main__":
    doc_update()
