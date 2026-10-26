"""
generator.py  –  Phase 3 Generator module
Agent loop: for each file in the plan:
  1. Build a focused prompt (only relevant JSON slices + interfaces of
     already-generated files)
  2. Ask LLM to produce the file content
  3. Write to disk via the tools layer
  4. Update the "generated summary" context
"""
from __future__ import annotations

import json
import re
import threading
from pathlib import Path
from typing import Any, Callable

from ..tools.file_tools import write_file, list_dir


# System prompt for file generation
_SYSTEM_GENERATE = """\
You are an expert Python developer. Generate the content of the requested file \
for a Python Tkinter DESKTOP application. 

Rules:
1. Output ONLY the file content – no markdown fences, no explanation text.
2. Use Python 3.10+ features where helpful. Add docstrings and inline comments.
3. The application is a desktop GUI (Tkinter). Do NOT generate web server code.
4. If generating a Python file, include proper imports and make it runnable.
5. If generating JSON data, output only valid JSON.
6. If generating requirements.txt, list only pip-installable packages (one per line).
7. If generating README.md, use standard markdown.
8. For test files, use pytest style (no unittest subclassing needed).
"""

_SYSTEM_README = """\
You are a technical writer. Generate a README.md for a Python Tkinter desktop application. \
Include: project description, prerequisites, installation, how to run, how to run tests, \
and an "Assumptions and Deviations" section. Use standard markdown.
Output ONLY the README content – no explanation.
"""

_SYSTEM_REQUIREMENTS = """\
Generate a requirements.txt for a Python Tkinter desktop application.
List only external pip packages (not stdlib modules). One package per line.
If no external packages are needed, output a comment line: # No external dependencies
Output ONLY the requirements.txt content.
"""


class Generator:
    """
    Generates project files one at a time using the LLM.

    Parameters
    ----------
    llm_client       : LLMClient | MockLLMClient
    cost_tracker     : CostTracker
    output_root      : Path – directory where files are written
    doc_data         : dict – parsed architecture doc
    view_data        : dict – parsed architecture view
    stop_event       : threading.Event – checked before each file
    log_callback     : Callable[[str], None]
    """

    def __init__(
        self,
        llm_client,
        cost_tracker,
        output_root: Path,
        doc_data: dict,
        view_data: dict,
        stop_event: threading.Event | None = None,
        log_callback: Callable | None = None,
    ) -> None:
        self._llm = llm_client
        self._cost = cost_tracker
        self._root = output_root
        self._doc = doc_data
        self._view = view_data
        self._stop = stop_event
        self._log = log_callback or (lambda msg: None)

        # Tracks interfaces of files already generated: {path: short_summary}
        self._generated_interfaces: dict[str, str] = {}
        self._generated_paths: list[str] = []

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def generate_all(self, plan: dict[str, Any]) -> list[str]:
        """
        Generate every file in the plan.

        Returns list of successfully written file paths (relative to output_root).
        """
        files = plan.get("files", [])
        project_name = plan.get("project_name", "Project")
        description = plan.get("description", "")

        self._log(f"[Generator] Starting generation of {len(files)} files …")

        for i, file_entry in enumerate(files, 1):
            if self._stop and self._stop.is_set():
                self._log("[Generator] Stop requested. Halting generation.")
                break
            if self._cost.over_budget():
                self._log("[Generator] Budget exceeded. Stopping generation.")
                break

            path = file_entry.get("path", "")
            purpose = file_entry.get("purpose", "")
            depends_on = file_entry.get("depends_on", [])

            self._log(f"[Generator] ({i}/{len(files)}) Generating: {path}")

            try:
                content = self._generate_file(
                    path=path,
                    purpose=purpose,
                    depends_on=depends_on,
                    project_name=project_name,
                    description=description,
                )
                abs_path = write_file(self._root, path, content)
                self._generated_paths.append(path)
                self._generated_interfaces[path] = self._extract_interface(path, content)
                self._log(f"[Generator] ✓ Written: {path}")
            except Exception as e:
                self._log(f"[Generator] ✗ Failed to generate {path}: {e}")

        return self._generated_paths

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _generate_file(
        self,
        path: str,
        purpose: str,
        depends_on: list[str],
        project_name: str,
        description: str,
    ) -> str:
        """Call LLM to generate content for one file."""
        system_prompt = self._pick_system_prompt(path)
        user_prompt = self._build_user_prompt(
            path, purpose, depends_on, project_name, description
        )

        content, usage = self._llm.chat_single(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=3000,
            temperature=0.2,
        )
        self._cost.add(f"generator:{path}", usage)

        # Strip accidental markdown fences
        content = self._strip_fences(content, path)
        return content

    def _pick_system_prompt(self, path: str) -> str:
        """Choose the right system prompt based on file type."""
        low = path.lower()
        if low.endswith("readme.md"):
            return _SYSTEM_README
        if low.endswith("requirements.txt"):
            return _SYSTEM_REQUIREMENTS
        return _SYSTEM_GENERATE

    def _build_user_prompt(
        self,
        path: str,
        purpose: str,
        depends_on: list[str],
        project_name: str,
        description: str,
    ) -> str:
        """Build the focused user prompt for one file."""
        # Relevant slices from parsed architecture
        components = self._doc.get("components", [])[:10]
        tech_stack = self._doc.get("tech_stack", [])[:8]
        all_classes = self._view.get("all_classes", [])[:15]
        all_states = self._view.get("all_states", [])[:8]
        roles = self._doc.get("roles", [])[:5]
        requirements = self._doc.get("requirements", [])[:8]
        db_schema = self._doc.get("db_schema", [])[:5]
        assumptions = self._doc.get("assumptions", [])[:5]

        # Interfaces of dependencies
        dep_interfaces = {}
        for dep in depends_on:
            if dep in self._generated_interfaces:
                dep_interfaces[dep] = self._generated_interfaces[dep]

        prompt_parts = [
            f"# Project: {project_name}",
            f"Description: {description}",
            f"\n## File to generate: `{path}`",
            f"Purpose: {purpose}",
        ]

        if dep_interfaces:
            prompt_parts.append("\n## Interfaces of dependencies (already generated):")
            for dep_path, iface in dep_interfaces.items():
                prompt_parts.append(f"\n### {dep_path}\n{iface}")

        prompt_parts += [
            f"\n## Architecture Components\n{json.dumps(components, indent=2)}",
            f"\n## Tech Stack\n{json.dumps(tech_stack, indent=2)}",
            f"\n## Roles\n{json.dumps(roles, indent=2)}",
            f"\n## Key Requirements\n{json.dumps(requirements, indent=2)}",
            f"\n## Classes from Diagrams\n{json.dumps(all_classes, indent=2)}",
            f"\n## Game/App States\n{json.dumps(all_states, indent=2)}",
        ]

        if db_schema:
            prompt_parts.append(f"\n## Data Schema\n{json.dumps(db_schema, indent=2)}")
        if assumptions:
            prompt_parts.append(f"\n## Assumptions\n{json.dumps(assumptions, indent=2)}")

        # Already generated summary (to avoid re-generating identical code)
        if self._generated_paths:
            prompt_parts.append(
                f"\n## Already generated files (do not re-generate them):\n"
                + "\n".join(f"  - {p}" for p in self._generated_paths[-20:])
            )

        prompt_parts.append(f"\nGenerate the content for `{path}` now.")
        return "\n".join(prompt_parts)

    def _extract_interface(self, path: str, content: str) -> str:
        """
        Extract a short interface summary from generated content.
        For Python: extracts class/function signatures.
        For JSON/text: returns first 300 chars.
        """
        if not path.endswith(".py"):
            return content[:300]

        lines = content.splitlines()
        interface_lines = []
        for line in lines:
            stripped = line.strip()
            # Capture class defs, function defs, and top-level constants
            if re.match(r"^(class |def |async def |[A-Z_]+\s*=)", stripped):
                interface_lines.append(line)
            elif stripped.startswith('"""') and interface_lines:
                interface_lines.append(line)
        return "\n".join(interface_lines[:40])

    def _strip_fences(self, content: str, path: str) -> str:
        """Remove markdown code fences from LLM output."""
        # Remove ```python, ```json, ``` etc.
        cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", content.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```$", "", cleaned.strip(), flags=re.MULTILINE)
        return cleaned.strip()
