"""
view_parser.py
Parses Architecture_View.md – extracts each PlantUML block and
returns structured metadata: diagram type, classes, relationships,
states, participants, messages, etc.
No LLM needed – pure regex + heuristics.
"""
from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any


# Map plantuml keywords to a diagram type label
DIAGRAM_TYPE_KEYWORDS: dict[str, str] = {
    "@startuml": "unknown",
    "usecase": "use_case",
    "actor": "use_case",
    "class": "class",
    "interface": "class",
    "abstract": "class",
    "object": "object",
    "state": "state",
    "activity": "activity",
    "partition": "activity",
    "sequence": "sequence",
    "participant": "sequence",
    "autonumber": "sequence",
    "collaboration": "collaboration",
    "package": "package",
    "component": "component",
    "node": "deployment",
    "artifact": "deployment",
    "database": "deployment",
    "cloud": "deployment",
    "container": "container",
}


class ArchitectureViewParser:
    """
    Parses Architecture_View.md and extracts all PlantUML diagrams.

    Output schema:
    {
      "diagrams": [
        {
          "index": int,
          "type": str,
          "raw": str,
          "classes": [ { "name": str, "attributes": [str], "methods": [str] } ],
          "relationships": [ { "from": str, "to": str, "type": str, "label": str } ],
          "states": [ { "name": str, "transitions": [str] } ],
          "participants": [ str ],
          "messages": [ str ],
          "actors": [ str ],
          "use_cases": [ str ],
          "packages": [ str ],
          "components": [ str ],
          "nodes": [ str ],
        }
      ],
      "all_classes": [ str ],
      "all_states": [ str ],
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
        self._raw = self.filepath.read_text(encoding="utf-8", errors="replace")
        diagrams = self._extract_plantuml_blocks(self._raw)
        parsed = [self._parse_block(i, block) for i, block in enumerate(diagrams)]
        all_classes = list({c["name"] for d in parsed for c in d.get("classes", [])})
        all_states = list({s["name"] for d in parsed for s in d.get("states", [])})
        self._result = {
            "diagrams": parsed,
            "all_classes": all_classes,
            "all_states": all_states,
            "source_file": str(self.filepath),
        }
        return self._result

    def to_json(self) -> str:
        if not self._result:
            self.parse()
        return json.dumps(self._result, indent=2)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _extract_plantuml_blocks(self, text: str) -> list[str]:
        """Find all @startuml...@enduml blocks (case-insensitive)."""
        pattern = re.compile(
            r"@startuml.*?@enduml", re.IGNORECASE | re.DOTALL
        )
        return pattern.findall(text)

    def _infer_type(self, block: str) -> str:
        """Heuristically infer diagram type from block content."""
        lower = block.lower()
        scores: dict[str, int] = {}

        # Strong indicator: [*] --> pattern means state diagram
        if "[*]" in block:
            scores["state"] = scores.get("state", 0) + 10

        for keyword, dtype in DIAGRAM_TYPE_KEYWORDS.items():
            count = lower.count(keyword)
            if count > 0:
                scores[dtype] = scores.get(dtype, 0) + count

        if not scores:
            return "unknown"
        return max(scores, key=lambda k: scores[k])

    def _parse_block(self, index: int, block: str) -> dict[str, Any]:
        dtype = self._infer_type(block)
        result: dict[str, Any] = {
            "index": index,
            "type": dtype,
            "raw": block,
            "classes": [],
            "relationships": [],
            "states": [],
            "participants": [],
            "messages": [],
            "actors": [],
            "use_cases": [],
            "packages": [],
            "components": [],
            "nodes": [],
        }

        lines = block.splitlines()

        if dtype in ("class", "object"):
            result["classes"] = self._parse_classes(lines)
            result["relationships"] = self._parse_relationships(lines)
        elif dtype == "state":
            result["states"] = self._parse_states(lines)
        elif dtype == "sequence":
            result["participants"] = self._parse_participants(lines)
            result["messages"] = self._parse_messages(lines)
        elif dtype == "use_case":
            result["actors"] = self._parse_actors(lines)
            result["use_cases"] = self._parse_use_cases(lines)
        elif dtype == "package":
            result["packages"] = self._parse_named(lines, "package")
            result["classes"] = self._parse_classes(lines)
        elif dtype == "component":
            result["components"] = self._parse_named(lines, "component")
        elif dtype == "deployment":
            result["nodes"] = self._parse_named(lines, "node")
        elif dtype == "activity":
            result["messages"] = self._parse_activity_actions(lines)

        return result

    # -- Class diagram --

    def _parse_classes(self, lines: list[str]) -> list[dict]:
        classes = []
        current: dict | None = None
        brace_depth = 0

        for line in lines:
            stripped = line.strip()
            # Start of class/interface/abstract
            m = re.match(
                r"^(?:class|interface|abstract\s+class|abstract)\s+"
                r'"?([A-Za-z_][A-Za-z0-9_<>]*)"?\s*(?:<<[^>]*>>)?\s*(\{)?',
                stripped,
                re.IGNORECASE,
            )
            if m:
                if current:
                    classes.append(current)
                current = {"name": m.group(1), "attributes": [], "methods": []}
                if m.group(2):  # opening brace on same line
                    brace_depth = 1
                continue

            if current:
                if "{" in stripped:
                    brace_depth += stripped.count("{")
                if "}" in stripped:
                    brace_depth -= stripped.count("}")
                    if brace_depth <= 0:
                        classes.append(current)
                        current = None
                        brace_depth = 0
                        continue

                # Attribute: + name : Type  or  - name : Type
                attr_m = re.match(r"^([+\-#~]?)\s*(\w+)\s*:\s*(.+)$", stripped)
                if attr_m and "(" not in stripped:
                    current["attributes"].append(stripped)
                    continue

                # Method: + name(args) : ReturnType
                meth_m = re.match(r"^([+\-#~]?)\s*\w+\s*\(", stripped)
                if meth_m:
                    current["methods"].append(stripped)

        if current:
            classes.append(current)

        return classes

    def _parse_relationships(self, lines: list[str]) -> list[dict]:
        """Parse lines like: ClassA --|> ClassB : label"""
        rels = []
        arrow_types = [
            (r"--\|>|<\|--", "extends"),
            (r"\.\.>|<\.\.", "uses"),
            (r"-->|<--", "association"),
            (r"--\*|\*--", "composition"),
            (r"--o|o--", "aggregation"),
            (r"\.\.\|>|<\|\.\.", "implements"),
            (r"--", "dependency"),
        ]
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("'") or stripped.startswith("@"):
                continue
            # Try each arrow type
            for arrow_pattern, rel_type in arrow_types:
                m = re.match(
                    rf'^"?([A-Za-z_][A-Za-z0-9_<> ]*)"?\s*'
                    rf"({arrow_pattern})\s*"
                    rf'"?([A-Za-z_][A-Za-z0-9_<> ]*)"?'
                    rf"(?:\s*:\s*(.+))?$",
                    stripped,
                )
                if m:
                    rels.append(
                        {
                            "from": m.group(1).strip(),
                            "to": m.group(3).strip(),
                            "type": rel_type,
                            "label": (m.group(4) or "").strip(),
                        }
                    )
                    break
        return rels

    # -- State diagram --

    def _parse_states(self, lines: list[str]) -> list[dict]:
        states: dict[str, dict] = {}
        for line in lines:
            stripped = line.strip()
            # state declaration: state "Name" as Alias
            m = re.match(r'^state\s+"?([^"{\[]+)"?\s*(?:as\s+(\w+))?', stripped, re.IGNORECASE)
            if m:
                name = (m.group(2) or m.group(1)).strip()
                states.setdefault(name, {"name": name, "transitions": []})
                continue
            # transition: StateA --> StateB : Event
            m = re.match(r"^(\w+)\s*-->\s*(\w+)(?:\s*:\s*(.+))?$", stripped)
            if m:
                src, dst, event = m.group(1), m.group(2), (m.group(3) or "").strip()
                states.setdefault(src, {"name": src, "transitions": []})
                states[src]["transitions"].append(f"{dst}: {event}" if event else dst)
        return list(states.values())

    # -- Sequence diagram --

    def _parse_participants(self, lines: list[str]) -> list[str]:
        parts = []
        for line in lines:
            stripped = line.strip()
            m = re.match(
                r"^(?:participant|actor|boundary|control|entity|database)\s+"
                r'"?([^"]+)"?(?:\s+as\s+(\w+))?',
                stripped,
                re.IGNORECASE,
            )
            if m:
                parts.append((m.group(2) or m.group(1)).strip())
        return parts

    def _parse_messages(self, lines: list[str]) -> list[str]:
        msgs = []
        for line in lines:
            stripped = line.strip()
            m = re.match(r"^(\w+)\s*(?:->+|<-+|->>|<<-)\s*(\w+)\s*:\s*(.+)$", stripped)
            if m:
                msgs.append(f"{m.group(1)} -> {m.group(2)}: {m.group(3)}")
        return msgs

    # -- Use case --

    def _parse_actors(self, lines: list[str]) -> list[str]:
        actors = []
        for line in lines:
            stripped = line.strip()
            m = re.match(r"^actor\s+\"?([^\"]+)\"?(?:\s+as\s+(\w+))?", stripped, re.IGNORECASE)
            if m:
                actors.append((m.group(2) or m.group(1)).strip())
        return actors

    def _parse_use_cases(self, lines: list[str]) -> list[str]:
        ucs = []
        for line in lines:
            stripped = line.strip()
            m = re.match(r'^usecase\s+"?([^"]+)"?(?:\s+as\s+(\w+))?', stripped, re.IGNORECASE)
            if m:
                ucs.append(m.group(1).strip())
                continue
            # parentheses notation: (Use Case Name)
            m = re.match(r"^\(([^)]+)\)", stripped)
            if m:
                ucs.append(m.group(1).strip())
        return ucs

    # -- Generic named elements --

    def _parse_named(self, lines: list[str], keyword: str) -> list[str]:
        items = []
        for line in lines:
            stripped = line.strip()
            m = re.match(
                rf'^{keyword}\s+"?([^"{{]+)"?',
                stripped,
                re.IGNORECASE,
            )
            if m:
                items.append(m.group(1).strip())
        return items

    # -- Activity diagram --

    def _parse_activity_actions(self, lines: list[str]) -> list[str]:
        actions = []
        for line in lines:
            stripped = line.strip()
            # :Action; style
            m = re.match(r"^:([^;]+);", stripped)
            if m:
                actions.append(m.group(1).strip())
        return actions
