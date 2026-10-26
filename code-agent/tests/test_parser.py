"""
tests/test_parser.py
Phase 1 unit tests for ArchitectureDocParser and ArchitectureViewParser.
Uses sample files from samples/ directory.
"""
import sys
import json
from pathlib import Path
import pytest

# Ensure src is importable
_SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_SRC))

from agent.parser.doc_parser import ArchitectureDocParser
from agent.parser.view_parser import ArchitectureViewParser

SAMPLES = Path(__file__).parent.parent / "samples"
DOC_FILE = SAMPLES / "Architecture_Documentation.md"
VIEW_FILE = SAMPLES / "Architecture_View.md"


# ── Doc Parser Tests ──────────────────────────────────────────────────────

class TestArchitectureDocParser:

    @pytest.fixture(autouse=True)
    def parser(self, tmp_path):
        """Use the real sample file if available, else a minimal stub."""
        if DOC_FILE.exists():
            self._parser = ArchitectureDocParser(DOC_FILE)
        else:
            stub = tmp_path / "doc.md"
            stub.write_text(
                "# Executive Summary\nA game.\n\n"
                "## Components\n**Game**: core logic\n**User**: player\n\n"
                "## Requirements\n- Display questions\n- Track score\n\n"
                "## Tech Stack\n- Python\n- Tkinter\n\n"
                "## Testing\n- Test scoring\n- Verify state transitions\n",
                encoding="utf-8",
            )
            self._parser = ArchitectureDocParser(stub)
        self._result = self._parser.parse()

    def test_parse_returns_dict(self):
        assert isinstance(self._result, dict)

    def test_has_required_keys(self):
        for key in ("requirements", "components", "tech_stack", "executive_summary"):
            assert key in self._result, f"Missing key: {key}"

    def test_requirements_is_list(self):
        assert isinstance(self._result["requirements"], list)

    def test_components_is_list(self):
        assert isinstance(self._result["components"], list)

    def test_tech_stack_is_list(self):
        assert isinstance(self._result["tech_stack"], list)

    def test_source_file_set(self):
        assert "source_file" in self._result

    def test_to_json_valid(self):
        j = self._parser.to_json()
        parsed = json.loads(j)
        assert isinstance(parsed, dict)

    def test_components_have_name(self):
        for c in self._result["components"]:
            assert "name" in c

    def test_testing_structure(self):
        t = self._result.get("testing", {})
        assert isinstance(t, dict)
        assert "strategy" in t
        assert "cases" in t


class TestDocParserEdgeCases:
    """Test parser robustness with malformed / minimal input."""

    def test_empty_file(self, tmp_path):
        empty = tmp_path / "empty.md"
        empty.write_text("", encoding="utf-8")
        parser = ArchitectureDocParser(empty)
        result = parser.parse()
        assert isinstance(result, dict)
        assert result["requirements"] == []
        assert result["components"] == []

    def test_no_sections(self, tmp_path):
        plain = tmp_path / "plain.md"
        plain.write_text("Just some text with no headings.", encoding="utf-8")
        parser = ArchitectureDocParser(plain)
        result = parser.parse()
        assert isinstance(result, dict)

    def test_missing_components_section(self, tmp_path):
        md = tmp_path / "missing.md"
        md.write_text("# Requirements\n- Req 1\n- Req 2\n", encoding="utf-8")
        parser = ArchitectureDocParser(md)
        result = parser.parse()
        assert isinstance(result["components"], list)  # empty is fine


# ── View Parser Tests ─────────────────────────────────────────────────────

class TestArchitectureViewParser:

    @pytest.fixture(autouse=True)
    def parser(self, tmp_path):
        if VIEW_FILE.exists():
            self._parser = ArchitectureViewParser(VIEW_FILE)
        else:
            stub = tmp_path / "view.md"
            stub.write_text(
                "# View\n"
                "```plantuml\n@startuml\nclass Game {\n  - state: str\n  + start(): void\n}\n"
                "class User {\n  - score: int\n}\nGame --> User\n@enduml\n```\n\n"
                "```plantuml\n@startuml\n[*] --> Playing\nPlaying --> Paused\nPaused --> Playing\n@enduml\n```\n",
                encoding="utf-8",
            )
            self._parser = ArchitectureViewParser(stub)
        self._result = self._parser.parse()

    def test_parse_returns_dict(self):
        assert isinstance(self._result, dict)

    def test_has_diagrams_key(self):
        assert "diagrams" in self._result

    def test_diagrams_is_list(self):
        assert isinstance(self._result["diagrams"], list)

    def test_at_least_one_diagram(self):
        assert len(self._result["diagrams"]) >= 1

    def test_all_classes_extracted(self):
        assert isinstance(self._result.get("all_classes"), list)

    def test_all_states_extracted(self):
        assert isinstance(self._result.get("all_states"), list)

    def test_source_file_set(self):
        assert self._result.get("source_file")

    def test_diagram_has_type(self):
        for diag in self._result["diagrams"]:
            assert "type" in diag

    def test_diagram_has_index(self):
        for diag in self._result["diagrams"]:
            assert "index" in diag

    def test_to_json_valid(self):
        j = self._parser.to_json()
        parsed = json.loads(j)
        assert "diagrams" in parsed


class TestViewParserEdgeCases:

    def test_no_plantuml_blocks(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("# No diagrams here\n", encoding="utf-8")
        parser = ArchitectureViewParser(f)
        result = parser.parse()
        assert result["diagrams"] == []

    def test_class_diagram_parsing(self, tmp_path):
        f = tmp_path / "class.md"
        f.write_text(
            "@startuml\n"
            "class Foo {\n  + bar(): str\n  - baz: int\n}\n"
            "class Baz {}\n"
            "Foo --> Baz\n"
            "@enduml\n",
            encoding="utf-8",
        )
        parser = ArchitectureViewParser(f)
        result = parser.parse()
        assert len(result["diagrams"]) == 1
        diag = result["diagrams"][0]
        assert diag["type"] == "class"
        names = [c["name"] for c in diag["classes"]]
        assert "Foo" in names

    def test_state_diagram_parsing(self, tmp_path):
        f = tmp_path / "state.md"
        f.write_text(
            "@startuml\n"
            "[*] --> Idle\n"
            "Idle --> Running\n"
            "Running --> Done\n"
            "@enduml\n",
            encoding="utf-8",
        )
        parser = ArchitectureViewParser(f)
        result = parser.parse()
        diag = result["diagrams"][0]
        assert diag["type"] == "state"
        state_names = [s["name"] for s in diag["states"]]
        assert "Idle" in state_names or "Running" in state_names
