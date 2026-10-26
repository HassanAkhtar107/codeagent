"""
file_tools.py  –  File I/O tool layer
Sandboxed to the output directory: all paths are resolved
relative to the output_root and checked against it.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


class SandboxViolation(Exception):
    """Raised when a path escapes the output sandbox."""


def _safe_path(output_root: Path, relative_path: str) -> Path:
    """
    Resolve relative_path inside output_root.
    Raises SandboxViolation if the resolved path is outside output_root.
    """
    full = (output_root / relative_path).resolve()
    try:
        full.relative_to(output_root.resolve())
    except ValueError:
        raise SandboxViolation(
            f"Path '{relative_path}' resolves outside the output directory."
        )
    return full


def write_file(output_root: Path, relative_path: str, content: str) -> str:
    """
    Write `content` to `output_root / relative_path`.
    Creates parent directories as needed.
    Returns the absolute path of the written file.
    """
    dest = _safe_path(output_root, relative_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return str(dest)


def read_file(output_root: Path, relative_path: str) -> str:
    """
    Read and return the content of `output_root / relative_path`.
    Raises FileNotFoundError if the file does not exist.
    """
    src = _safe_path(output_root, relative_path)
    if not src.exists():
        raise FileNotFoundError(f"File not found: {relative_path}")
    return src.read_text(encoding="utf-8", errors="replace")


def list_dir(output_root: Path, relative_path: str = ".") -> list[str]:
    """
    List files recursively under `output_root / relative_path`.
    Returns paths relative to output_root.
    """
    target = _safe_path(output_root, relative_path)
    if not target.exists():
        return []
    result = []
    for p in sorted(target.rglob("*")):
        if p.is_file():
            result.append(str(p.relative_to(output_root)))
    return result
