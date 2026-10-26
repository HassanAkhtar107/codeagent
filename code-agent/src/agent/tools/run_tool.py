"""
run_tool.py  –  Sandboxed subprocess runner
Runs a command inside the output directory with a timeout.
stdout + stderr are captured and returned as a string.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


DEFAULT_TIMEOUT = 60  # seconds


def run_command(
    cmd: list[str],
    cwd: Path,
    timeout: int = DEFAULT_TIMEOUT,
    env: dict | None = None,
) -> tuple[int, str]:
    """
    Run `cmd` in directory `cwd`.

    Returns
    -------
    (returncode, output)
        returncode : int  (0 = success)
        output     : str  (combined stdout + stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        combined = (result.stdout or "") + (result.stderr or "")
        return result.returncode, combined
    except subprocess.TimeoutExpired:
        return 1, f"Command timed out after {timeout}s: {' '.join(cmd)}"
    except FileNotFoundError as e:
        return 1, f"Command not found: {e}"
    except Exception as e:
        return 1, f"Unexpected error running command: {e}"
