"""
tests/test_generator.py
Unit tests for Generator and file tools using MockLLMClient.
"""
import sys
from pathlib import Path
import pytest

_SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_SRC))

from agent.generator import Generator
from agent.tools.file_tools import write_file, read_file, list_dir, SandboxViolation
from cost_tracker import CostTracker
from llm_client import MockLLMClient


@pytest.fixture
def output_dir(tmp_path):
    d = tmp_path / "output"
    d.mkdir()
    return d


@pytest.fixture
def mock_client():
    return MockLLMClient()


@pytest.fixture
def tracker():
    return CostTracker(model="deepseek-chat", hard_budget_usd=1.0)


@pytest.fixture
def simple_plan():
    return {
        "project_name": "TestProject",
        "description": "Test desktop app",
        "files": [
            {"path": "main.py", "purpose": "Entry point", "depends_on": []},
            {"path": "src/models.py", "purpose": "Data models", "depends_on": []},
            {"path": "requirements.txt", "purpose": "Dependencies", "depends_on": []},
            {"path": "README.md", "purpose": "Documentation", "depends_on": []},
        ],
    }


@pytest.fixture
def doc_data():
    return {
        "executive_summary": "Test project",
        "components": [{"name": "App", "description": "Main app"}],
        "tech_stack": ["Python", "Tkinter"],
        "roles": ["User"],
        "requirements": ["Run on desktop"],
        "db_schema": [],
        "assumptions": [],
    }


@pytest.fixture
def view_data():
    return {"diagrams": [], "all_classes": ["App"], "all_states": []}


# ── File Tools Tests ──────────────────────────────────────────────────────

class TestFileTools:

    def test_write_and_read(self, output_dir):
        write_file(output_dir, "test.txt", "hello world")
        content = read_file(output_dir, "test.txt")
        assert content == "hello world"

    def test_write_creates_dirs(self, output_dir):
        write_file(output_dir, "src/deep/file.py", "# code")
        assert (output_dir / "src" / "deep" / "file.py").exists()

    def test_read_nonexistent_raises(self, output_dir):
        with pytest.raises(FileNotFoundError):
            read_file(output_dir, "nonexistent.txt")

    def test_list_dir_empty(self, output_dir):
        result = list_dir(output_dir)
        assert result == []

    def test_list_dir_finds_files(self, output_dir):
        write_file(output_dir, "a.py", "")
        write_file(output_dir, "src/b.py", "")
        result = list_dir(output_dir)
        assert "a.py" in result
        assert "src/b.py" in result or "src\\b.py" in result

    def test_sandbox_violation(self, output_dir):
        with pytest.raises(SandboxViolation):
            write_file(output_dir, "../../etc/passwd", "bad")

    def test_write_overwrites_existing(self, output_dir):
        write_file(output_dir, "x.txt", "first")
        write_file(output_dir, "x.txt", "second")
        assert read_file(output_dir, "x.txt") == "second"


# ── Generator Tests ───────────────────────────────────────────────────────

class TestGenerator:

    def test_generate_all_returns_list(self, mock_client, tracker, output_dir,
                                       simple_plan, doc_data, view_data):
        gen = Generator(mock_client, tracker, output_dir, doc_data, view_data)
        result = gen.generate_all(simple_plan)
        assert isinstance(result, list)

    def test_generate_creates_files(self, mock_client, tracker, output_dir,
                                    simple_plan, doc_data, view_data):
        gen = Generator(mock_client, tracker, output_dir, doc_data, view_data)
        result = gen.generate_all(simple_plan)
        for path in result:
            assert (output_dir / path).exists(), f"File not created: {path}"

    def test_generate_respects_stop_event(self, mock_client, tracker, output_dir,
                                          simple_plan, doc_data, view_data):
        import threading
        stop = threading.Event()
        stop.set()  # Stop immediately
        gen = Generator(mock_client, tracker, output_dir, doc_data, view_data,
                        stop_event=stop)
        result = gen.generate_all(simple_plan)
        assert isinstance(result, list)
        assert len(result) == 0  # Stopped before generating

    def test_cost_tracked_after_generation(self, mock_client, tracker, output_dir,
                                            simple_plan, doc_data, view_data):
        gen = Generator(mock_client, tracker, output_dir, doc_data, view_data)
        gen.generate_all(simple_plan)
        assert tracker.total_tokens > 0

    def test_budget_exceeded_stops_early(self, mock_client, output_dir,
                                          simple_plan, doc_data, view_data):
        tiny_tracker = CostTracker(model="deepseek-chat", hard_budget_usd=0.0)
        gen = Generator(mock_client, tiny_tracker, output_dir, doc_data, view_data)
        result = gen.generate_all(simple_plan)
        # With zero budget, nothing should be generated
        assert len(result) == 0
