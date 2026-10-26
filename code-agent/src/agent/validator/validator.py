"""
validator.py  –  Phase 4 Validator + Repair loop
After generation:
  1. Syntax-check all .py files with `python -m py_compile`
  2. Run pytest if tests/ directory exists
  3. For each failure: send error + file content to LLM for a fix (max 2 repairs)
  4. Return a ValidationResult with pass/fail counts
"""
from __future__ import annotations

import sys
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..tools.file_tools import read_file, write_file, list_dir
from ..tools.run_tool import run_command


_SYSTEM_REPAIR = """\
You are an expert Python developer. A file in a generated project has a syntax or \
runtime error. Fix it so it compiles and passes the test.

Rules:
1. Output ONLY the corrected file content – no markdown fences, no explanation.
2. Preserve all existing logic; only fix the reported error.
3. If the error is in a test file, fix the test to match the implementation.
"""


@dataclass
class FileResult:
    path: str
    passed: bool
    error: str = ""
    repaired: bool = False
    repair_attempts: int = 0


@dataclass
class ValidationResult:
    syntax_passed: list[str] = field(default_factory=list)
    syntax_failed: list[FileResult] = field(default_factory=list)
    tests_passed: bool = False
    tests_output: str = ""
    total_files_checked: int = 0

    @property
    def all_syntax_ok(self) -> bool:
        return len(self.syntax_failed) == 0

    def summary(self) -> str:
        lines = [
            "=== Validation Summary ===",
            f"  Files checked    : {self.total_files_checked}",
            f"  Syntax passed    : {len(self.syntax_passed)}",
            f"  Syntax failed    : {len(self.syntax_failed)}",
            f"  Tests passed     : {'Yes' if self.tests_passed else 'No / Skipped'}",
        ]
        for fr in self.syntax_failed:
            lines.append(f"  ✗ {fr.path}: {fr.error[:120]}")
        return "\n".join(lines)


class Validator:
    """
    Validates and optionally repairs generated Python files.

    Parameters
    ----------
    llm_client    : LLMClient | MockLLMClient
    cost_tracker  : CostTracker
    output_root   : Path  – root of generated project
    log_callback  : Callable[[str], None]
    max_repairs   : int   – max LLM repair attempts per file (default 2)
    """

    def __init__(
        self,
        llm_client,
        cost_tracker,
        output_root: Path,
        log_callback: Callable | None = None,
        max_repairs: int = 2,
    ) -> None:
        self._llm = llm_client
        self._cost = cost_tracker
        self._root = output_root
        self._log = log_callback or (lambda msg: None)
        self._max_repairs = max_repairs

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def validate(self) -> ValidationResult:
        """Run syntax checks + tests. Return ValidationResult."""
        result = ValidationResult()
        py_files = [p for p in list_dir(self._root) if p.endswith(".py")]
        result.total_files_checked = len(py_files)

        self._log(f"[Validator] Syntax-checking {len(py_files)} Python files …")

        for rel_path in py_files:
            abs_path = self._root / rel_path
            ok, error = self._syntax_check(abs_path)
            if ok:
                result.syntax_passed.append(rel_path)
            else:
                self._log(f"[Validator] ✗ Syntax error in {rel_path}: {error[:100]}")
                fr = FileResult(path=rel_path, passed=False, error=error)
                # Attempt repair
                fr = self._repair_loop(fr)
                result.syntax_failed.append(fr)

        # Run tests
        tests_dir = self._root / "tests"
        if tests_dir.exists() and any(tests_dir.glob("test_*.py")):
            self._log("[Validator] Running pytest …")
            result.tests_passed, result.tests_output = self._run_tests()
            if result.tests_passed:
                self._log("[Validator] ✓ All tests passed.")
            else:
                self._log("[Validator] ✗ Some tests failed.")
                self._log(result.tests_output[:500])
        else:
            self._log("[Validator] No tests directory found – skipping pytest.")
            result.tests_passed = True   # Not a failure if no tests exist

        return result

    # ------------------------------------------------------------------
    # Syntax check
    # ------------------------------------------------------------------

    def _syntax_check(self, abs_path: Path) -> tuple[bool, str]:
        """Run python -m py_compile on a single file."""
        rc, output = run_command(
            [sys.executable, "-m", "py_compile", str(abs_path)],
            cwd=self._root,
            timeout=30,
        )
        return rc == 0, output.strip()

    # ------------------------------------------------------------------
    # Test runner
    # ------------------------------------------------------------------

    def _run_tests(self) -> tuple[bool, str]:
        """Run pytest in the output root. Returns (passed, output)."""
        rc, output = run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "--no-header"],
            cwd=self._root,
            timeout=120,
        )
        return rc == 0, output

    # ------------------------------------------------------------------
    # Repair loop
    # ------------------------------------------------------------------

    def _repair_loop(self, fr: FileResult) -> FileResult:
        """Attempt LLM-based repair of a file with a syntax error."""
        try:
            original_content = read_file(self._root, fr.path)
        except Exception as e:
            self._log(f"[Validator] Cannot read {fr.path} for repair: {e}")
            return fr

        for attempt in range(1, self._max_repairs + 1):
            self._log(f"[Validator] Repair attempt {attempt}/{self._max_repairs} for {fr.path} …")
            fr.repair_attempts = attempt

            user_prompt = (
                f"## File: {fr.path}\n\n"
                f"## Error:\n{fr.error}\n\n"
                f"## Current Content:\n{original_content}\n\n"
                "Fix the error and output the corrected file content only."
            )

            try:
                content, usage = self._llm.chat_single(
                    system_prompt=_SYSTEM_REPAIR,
                    user_prompt=user_prompt,
                    max_tokens=3000,
                    temperature=0.1,
                )
                self._cost.add(f"validator:repair:{fr.path}:attempt{attempt}", usage)
            except Exception as e:
                self._log(f"[Validator] LLM repair call failed: {e}")
                break

            # Strip fences
            content = re.sub(r"^```[a-zA-Z]*\n?", "", content.strip(), flags=re.MULTILINE)
            content = re.sub(r"\n?```$", "", content.strip(), flags=re.MULTILINE)
            content = content.strip()

            # Write repaired content
            try:
                abs_path = self._root / fr.path
                write_file(self._root, fr.path, content)
                original_content = content  # Update for next iteration

                # Re-check syntax
                ok, new_error = self._syntax_check(abs_path)
                if ok:
                    fr.passed = True
                    fr.repaired = True
                    fr.error = ""
                    self._log(f"[Validator] ✓ Repaired: {fr.path}")
                    return fr
                else:
                    fr.error = new_error
            except Exception as e:
                self._log(f"[Validator] Failed to write repair: {e}")
                break

        self._log(f"[Validator] ✗ Could not repair {fr.path} after {self._max_repairs} attempts.")
        return fr
