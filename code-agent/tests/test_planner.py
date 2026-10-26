"""
tests/test_planner.py
Unit tests for the Planner module using MockLLMClient.
"""
import sys
import json
from pathlib import Path
import pytest

_SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_SRC))

from agent.planner import Planner
from cost_tracker import CostTracker
from llm_client import MockLLMClient


@pytest.fixture
def mock_client():
    return MockLLMClient()


@pytest.fixture
def tracker():
    return CostTracker(model="deepseek-chat", hard_budget_usd=1.0)


@pytest.fixture
def sample_doc_data():
    return {
        "executive_summary": "Space Fractions: educational desktop game.",
        "components": [
            {"name": "Game", "description": "Core game logic"},
            {"name": "Question", "description": "Fraction question model"},
        ],
        "tech_stack": ["Python 3.10+", "Tkinter"],
        "roles": ["Student", "Admin"],
        "requirements": ["Display questions", "Track score"],
        "db_schema": [],
        "assumptions": [],
    }


@pytest.fixture
def sample_view_data():
    return {
        "diagrams": [],
        "all_classes": ["Game", "Question", "User", "Admin"],
        "all_states": ["Playing", "Paused", "GameOver"],
    }


class TestPlanner:

    def test_plan_returns_dict(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        plan = planner.plan(sample_doc_data, sample_view_data)
        assert isinstance(plan, dict)

    def test_plan_has_project_name(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        plan = planner.plan(sample_doc_data, sample_view_data)
        assert "project_name" in plan

    def test_plan_has_files(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        plan = planner.plan(sample_doc_data, sample_view_data)
        assert "files" in plan
        assert isinstance(plan["files"], list)
        assert len(plan["files"]) > 0

    def test_plan_files_have_path(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        plan = planner.plan(sample_doc_data, sample_view_data)
        for f in plan["files"]:
            assert "path" in f

    def test_plan_has_main_py(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        plan = planner.plan(sample_doc_data, sample_view_data)
        paths = [f["path"] for f in plan["files"]]
        assert "main.py" in paths

    def test_plan_has_requirements_txt(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        plan = planner.plan(sample_doc_data, sample_view_data)
        paths = [f["path"] for f in plan["files"]]
        assert any("requirements" in p for p in paths)

    def test_cost_tracked(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        planner.plan(sample_doc_data, sample_view_data)
        assert tracker.total_tokens > 0

    def test_no_web_server_files(self, mock_client, tracker, sample_doc_data, sample_view_data):
        planner = Planner(mock_client, tracker)
        plan = planner.plan(sample_doc_data, sample_view_data)
        paths = [f["path"] for f in plan["files"]]
        web_files = ["server.js", "wsgi.py", "manage.py", "package.json"]
        for wf in web_files:
            assert wf not in paths, f"Web file {wf} should not be in desktop plan"

    def test_invalid_json_fallback(self, tracker, sample_doc_data, sample_view_data):
        """Test that planner raises ValueError when LLM returns invalid JSON twice."""
        class BadClient:
            def chat_single(self, *args, **kwargs):
                return "This is not JSON at all!", {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}

        planner = Planner(BadClient(), tracker)
        with pytest.raises(ValueError, match="failed to produce valid JSON"):
            planner.plan(sample_doc_data, sample_view_data)
