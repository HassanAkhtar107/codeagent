"""
planner.py  –  Phase 3 Planner module
Asks the LLM to produce a JSON project plan:
  { project_name, description, folder_structure, files: [{path, purpose, depends_on}] }

Validates JSON strictly. Retries once on failure.
Applies "desktop-first" enforcement: strips web/server file paths
and replaces them with desktop Tkinter equivalents.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable


SYSTEM_PROMPT = """\
You are an expert software architect. Your job is to create a project plan for a \
DESKTOP application (Python + Tkinter). The generated project must be a runnable \
desktop GUI application, NOT a web app or server.

Rules:
1. Output ONLY valid JSON – no markdown fences, no explanation text.
2. The plan must list every file needed for a complete, runnable project.
3. Include: main.py (entry point), src/ modules, data/ files, tests/ directory,
   requirements.txt, README.md, and optionally a Dockerfile.
4. If the architecture mentions web tech (REST, Express, Node, Docker, Kubernetes),
   adapt them to desktop equivalents (e.g. a local SQLite DB instead of a server DB,
   Python classes instead of microservices).
5. Do NOT include server-side files like wsgi.py, server.js, package.json, etc.

Output JSON schema (EXACTLY):
{
  "project_name": "string",
  "description": "string",
  "folder_structure": ["dir1/", "dir2/", ...],
  "files": [
    {
      "path": "relative/path/to/file.py",
      "purpose": "one-sentence description",
      "depends_on": ["other/file.py", ...]
    }
  ]
}
"""

# Web-tech red flags that should trigger substitution
WEB_PATH_PATTERNS = [
    r"server\.js", r"app\.js", r"wsgi\.py", r"asgi\.py", r"manage\.py",
    r"package\.json", r"node_modules", r"\.env", r"docker-compose",
    r"routes/", r"controllers/", r"middleware/", r"views\.py",
    r"serializers\.py", r"urls\.py",
]
WEB_PATTERN_RE = re.compile("|".join(WEB_PATH_PATTERNS), re.IGNORECASE)


class Planner:
    """
    Produces and validates the project plan JSON from parsed architecture data.

    Parameters
    ----------
    llm_client : LLMClient | MockLLMClient
        The LLM backend to use.
    cost_tracker : CostTracker
        Accumulates tokens/cost for this call.
    log_callback : Callable[[str], None] | None
        Optional function for log output.
    """

    def __init__(self, llm_client, cost_tracker, log_callback: Callable | None = None) -> None:
        self._llm = llm_client
        self._cost = cost_tracker
        self._log = log_callback or (lambda msg: None)

    # ------------------------------------------------------------------

    def plan(self, doc_data: dict, view_data: dict) -> dict[str, Any]:
        """
        Generate the project plan.

        Returns the validated plan dict.
        Raises ValueError if the LLM cannot produce valid JSON after 2 attempts.
        """
        prompt = self._build_prompt(doc_data, view_data)
        self._log("[Planner] Requesting project plan from LLM …")

        last_error: str = ""
        for attempt in range(1, 3):          # Max 2 attempts
            content, usage = self._llm.chat_single(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=prompt,
                max_tokens=2048,
                temperature=0.1,
            )
            self._cost.add(f"planner:attempt{attempt}", usage)

            plan, error = self._parse_plan_json(content)
            if plan is not None:
                plan = self._enforce_desktop(plan)
                self._log(
                    f"[Planner] Plan validated. {len(plan.get('files', []))} files planned."
                )
                return plan

            last_error = error
            self._log(f"[Planner] JSON parse failed (attempt {attempt}): {error}. Retrying …")

        raise ValueError(f"Planner failed to produce valid JSON after 2 attempts: {last_error}")

    # ------------------------------------------------------------------

    def _build_prompt(self, doc_data: dict, view_data: dict) -> str:
        """Construct a concise prompt with only the essential architecture slices."""
        summary = doc_data.get("executive_summary", "")[:400]
        components = doc_data.get("components", [])[:15]
        tech_stack = doc_data.get("tech_stack", [])[:10]
        roles = doc_data.get("roles", [])[:5]
        requirements = doc_data.get("requirements", [])[:10]
        all_classes = view_data.get("all_classes", [])[:20]
        all_states = view_data.get("all_states", [])[:10]

        return (
            f"## Project Summary\n{summary}\n\n"
            f"## Components\n{json.dumps(components, indent=2)}\n\n"
            f"## Tech Stack (adapt web items to desktop)\n{json.dumps(tech_stack, indent=2)}\n\n"
            f"## Roles / Actors\n{json.dumps(roles, indent=2)}\n\n"
            f"## Key Requirements\n{json.dumps(requirements, indent=2)}\n\n"
            f"## Classes from Diagrams\n{json.dumps(all_classes, indent=2)}\n\n"
            f"## States from Diagrams\n{json.dumps(all_states, indent=2)}\n\n"
            "Generate a complete project plan JSON for a Python Tkinter desktop application."
        )

    def _parse_plan_json(self, content: str) -> tuple[dict | None, str]:
        """
        Try to extract and validate JSON from LLM output.
        Returns (plan_dict, "") on success, (None, error_msg) on failure.
        """
        # Strip markdown fences if present
        cleaned = re.sub(r"```(?:json)?", "", content).strip()
        # Try to find a JSON object
        m = re.search(r"\{[\s\S]+\}", cleaned)
        if not m:
            return None, "No JSON object found in response."
        candidate = m.group(0)

        try:
            plan = json.loads(candidate)
        except json.JSONDecodeError as e:
            return None, f"JSONDecodeError: {e}"

        # Validate required keys
        required = {"project_name", "files"}
        missing = required - plan.keys()
        if missing:
            return None, f"Missing required keys: {missing}"

        if not isinstance(plan.get("files"), list) or not plan["files"]:
            return None, "files must be a non-empty list."

        for f in plan["files"]:
            if not isinstance(f, dict) or "path" not in f:
                return None, "Each file entry must be a dict with at least 'path'."

        return plan, ""

    def _enforce_desktop(self, plan: dict) -> dict:
        """
        Remove web-server files and ensure the plan has essential desktop files.
        """
        original_files = plan.get("files", [])
        desktop_files = []
        removed = []

        for f in original_files:
            path = f.get("path", "")
            if WEB_PATTERN_RE.search(path):
                removed.append(path)
            else:
                desktop_files.append(f)

        if removed:
            self._log(
                f"[Planner] Removed web-specific files: {removed}"
            )

        # Ensure main.py exists
        has_main = any(f["path"] == "main.py" for f in desktop_files)
        if not has_main:
            desktop_files.insert(
                0,
                {
                    "path": "main.py",
                    "purpose": "Entry point – launches the Tkinter application",
                    "depends_on": [],
                },
            )

        # Ensure requirements.txt
        has_req = any("requirements" in f["path"] for f in desktop_files)
        if not has_req:
            desktop_files.append(
                {"path": "requirements.txt", "purpose": "Python dependencies", "depends_on": []}
            )

        # Ensure README.md
        has_readme = any("readme" in f["path"].lower() for f in desktop_files)
        if not has_readme:
            desktop_files.append(
                {"path": "README.md", "purpose": "Setup and run instructions", "depends_on": []}
            )

        plan["files"] = desktop_files
        return plan
