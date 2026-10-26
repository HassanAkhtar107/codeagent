"""
main.py  –  Entry point for Code Agent
Launches the GUI. When packaged with PyInstaller, this is the script
PyInstaller uses as the entry point.
"""
import sys
from pathlib import Path

# Ensure src/ is on the path so all imports resolve correctly
_HERE = Path(__file__).parent
_SRC = _HERE / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from gui import launch

if __name__ == "__main__":
    launch()
