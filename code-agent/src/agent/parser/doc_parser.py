"""
doc_parser.py
Parses Architecture_Documentation.md into a structured JSON dict.
Sections are detected by heading level. No LLM needed for this step.
"""
from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any


# Known section keywords mapped to canonical keys
SECTION_MAP: dict[str, str] = {
    "executive summary": "executive_summary",
    "introduction": "introduction",
    "overview": "executive_summary",
    "traceability": "traceability",
    "requirements": "requirements",
    "components": "components",
    "component": "components",
    "tech stack": "tech_stack",
    "technology stack": "tech_stack",
    "technologies": "tech_stack",
    "api": "api_specs",
    "apis": "api_specs",
    "api spec": "api_specs",
    "api specifications": "api_specs",
    "database": "db_schema",
    "db schema": "db_schema",
    "data model": "db_schema",
    "schema": "db_schema",
    "security": "security",
    "testing": "testing",
    "test": "testing",
    "deployment": "deployment",
    "docker": "deployment",
    "infrastructure": "deployment",
    "assumptions": "assumptions",
    "deviations": "assumptions",
    "constraints": "constraints",
    "roles": "roles",
    "users": "roles",
    "actors": "roles",
    "use cases": "use_cases",
    "use case": "use_cases",
    "package": "packages",
    "packages": "packages",
    "architecture": "architecture",
}


class ArchitectureDocParser:
    """
    Parses a markdown architecture document into a structured dict.
    
    The output schema:
    {
      "raw_sections": { section_key: text },
      "requirements": [ str, ... ],
      "components": [ { "name": str, "description": str } ],
      "tech_stack": [ str, ... ],
      "api_specs": [ str, ... ],
      "db_schema": [ str, ... ],
      "roles": [ str, ... ],
      "use_cases": [ str, ... ],
      "testing": { "strategy": str, "cases": [ str, ... ] },
      "assumptions": [ str, ... ],
      "executive_summary": str,
      "deployment": str,
      "security": str,
      "source_file": str,
    }
    """

    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)
        self._raw: str = ""
        self._result: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self) -> dict[str, Any]:
        """Read and parse the file. Returns structured dict."""
        self._raw = self.filepath.read_text(encoding="utf-8", errors="replace")
        sections = self._split_into_sections(self._raw)
        self._result = self._build_structure(sections)
        self._result["source_file"] = str(self.filepath)
        return self._result

    def to_json(self) -> str:
        """Return JSON string of parsed result."""
        if not self._result:
            self.parse()
        return json.dumps(self._result, indent=2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _split_into_sections(self, text: str) -> dict[str, str]:
        """
        Split markdown by headings (# / ## / ###).
        Returns dict of {heading_text_lower: body_text}.
        """
        # Match headings at any level
        pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
        matches = list(pattern.finditer(text))
        sections: dict[str, str] = {}

        for i, match in enumerate(matches):
            heading = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            key = heading.lower()
            # If duplicate heading, append content
            if key in sections:
                sections[key] += "\n\n" + body
            else:
                sections[key] = body

        # Also capture any text before the first heading
        if matches:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                sections["_preamble"] = preamble

        return sections

    def _canonical_key(self, heading: str) -> str:
        """Map a raw heading to a canonical section key."""
        heading_l = heading.lower().strip()
        for keyword, key in SECTION_MAP.items():
            if keyword in heading_l:
                return key
        return re.sub(r"\W+", "_", heading_l)

    def _build_structure(self, sections: dict[str, str]) -> dict[str, Any]:
        """Build the structured output from raw sections."""
        raw_sections: dict[str, str] = {}
        structured: dict[str, Any] = {
            "requirements": [],
            "components": [],
            "tech_stack": [],
            "api_specs": [],
            "db_schema": [],
            "roles": [],
            "use_cases": [],
            "assumptions": [],
            "testing": {"strategy": "", "cases": []},
            "executive_summary": "",
            "deployment": "",
            "security": "",
        }

        for heading, body in sections.items():
            if heading == "_preamble":
                continue
            canonical = self._canonical_key(heading)
            raw_sections[canonical] = body

            if canonical == "requirements":
                structured["requirements"] = self._extract_list_items(body)
            elif canonical == "components":
                structured["components"] = self._extract_components(body)
            elif canonical == "tech_stack":
                structured["tech_stack"] = self._extract_list_items(body)
            elif canonical == "api_specs":
                structured["api_specs"] = self._extract_list_items(body)
            elif canonical == "db_schema":
                structured["db_schema"] = self._extract_list_items(body)
            elif canonical == "roles":
                structured["roles"] = self._extract_list_items(body)
            elif canonical == "use_cases":
                structured["use_cases"] = self._extract_list_items(body)
            elif canonical == "assumptions":
                structured["assumptions"] = self._extract_list_items(body)
            elif canonical == "testing":
                structured["testing"] = self._extract_testing(body)
            elif canonical == "executive_summary":
                structured["executive_summary"] = body[:500]
            elif canonical == "deployment":
                structured["deployment"] = body[:400]
            elif canonical == "security":
                structured["security"] = body[:400]

        structured["raw_sections"] = raw_sections

        # Fallback: if no components found, try extracting from any section
        if not structured["components"]:
            for body in sections.values():
                candidates = self._extract_components(body)
                if candidates:
                    structured["components"] = candidates
                    break

        return structured

    def _extract_list_items(self, text: str) -> list[str]:
        """Extract bullet / numbered list items from markdown text."""
        items = []
        for line in text.splitlines():
            stripped = line.strip()
            # Bullet or numbered list
            m = re.match(r"^[-*+]\s+(.+)$", stripped)
            if m:
                items.append(m.group(1).strip())
                continue
            m = re.match(r"^\d+[\.\)]\s+(.+)$", stripped)
            if m:
                items.append(m.group(1).strip())
        # If no list items found, fall back to splitting by sentence
        if not items:
            sentences = re.split(r"[.\n]+", text)
            items = [s.strip() for s in sentences if len(s.strip()) > 10][:20]
        return items

    def _extract_components(self, text: str) -> list[dict[str, str]]:
        """
        Try to extract component entries with name + description.
        Handles: '**ComponentName**: description' or '## ComponentName'
        """
        components = []
        # Pattern: **Name**: description
        pattern = re.compile(r"\*\*([^*]+)\*\*\s*[:\-–]\s*(.+)")
        for m in pattern.finditer(text):
            name = m.group(1).strip()
            desc = m.group(2).strip()[:200]
            components.append({"name": name, "description": desc})

        # Pattern: Name: description (simple colon-separated)
        if not components:
            for line in text.splitlines():
                line = line.strip().lstrip("-*+").strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    name = parts[0].strip()
                    desc = parts[1].strip()[:200]
                    if 2 < len(name) < 50 and len(desc) > 5:
                        components.append({"name": name, "description": desc})

        return components[:30]  # Limit to 30 components

    def _extract_testing(self, text: str) -> dict[str, Any]:
        """Extract testing strategy and test cases from text."""
        strategy_lines = []
        cases = []
        for line in text.splitlines():
            stripped = line.strip()
            m = re.match(r"^[-*+]\s+(.+)$", stripped)
            if m:
                item = m.group(1).strip()
                # Heuristic: looks like a test case if it mentions "test", "verify", "check", "assert"
                if any(kw in item.lower() for kw in ["test", "verify", "check", "assert", "ensure", "validate"]):
                    cases.append(item)
                else:
                    strategy_lines.append(item)
            elif stripped and not stripped.startswith("#"):
                strategy_lines.append(stripped)

        return {
            "strategy": " ".join(strategy_lines[:5]),
            "cases": cases[:20],
        }
