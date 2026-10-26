"""
conftest.py  –  pytest root configuration for code-agent tests
Adds src/ to sys.path so all imports resolve correctly.
"""
import sys
from pathlib import Path

# Add the src directory to path
_SRC = Path(__file__).parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
