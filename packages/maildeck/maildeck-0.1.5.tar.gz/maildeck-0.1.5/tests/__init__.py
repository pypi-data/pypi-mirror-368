"""Ensure `src/` is importable when running tests via unittest discover.

This adjusts sys.path only when executed directly by test discovery.
"""

import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = root / "src"
if src.exists():
    sys.path.insert(0, str(src))
