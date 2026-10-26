"""
tests/test_validator.py
Unit tests for the Validator using MockLLMClient and temporary files.
"""
import sys
import textwrap
from pathlib import Path
import pytest

_SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_SRC))

from agent.validator import Validator
from agent.tools.file_tools import write_file
from cost_tracker import CostTracker
from llm_client import MockLLMClient


@pytest.fixture
def output_dir(tmp_path):
    d = tmp_path / "project"
    d.mkdir()
    return d


@pytest.fixture
def tracker():
    return CostTracker(model="deepseek-chat", hard_budget_usd=1.0)


@pytest.fixture
def mock_client():
    return MockLLMClient()


class TestValidatorSyntaxCheck:

    def test_valid_python_file_passes(self, output_dir, tracker, mock_client):
        write_file(output_dir, "good.py", "def foo():\n    return 42\n")
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        assert "good.py" in result.syntax_passed

    def test_invalid_python_file_fails(self, output_dir, tracker, mock_client):
        write_file(output_dir, "bad.py", "def foo(\n    broken syntax\n")
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        failed_paths = [fr.path for fr in result.syntax_failed]
        assert "bad.py" in failed_paths

    def test_multiple_valid_files_all_pass(self, output_dir, tracker, mock_client):
        for name in ["a.py", "b.py", "c.py"]:
            write_file(output_dir, name, f"# {name}\npass\n")
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        assert result.syntax_failed == []
        assert len(result.syntax_passed) == 3

    def test_no_python_files(self, output_dir, tracker, mock_client):
        write_file(output_dir, "data.json", '{"key": "value"}')
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        assert result.total_files_checked == 0
        assert result.syntax_passed == []
        assert result.syntax_failed == []


class TestValidatorTests:

    def test_no_tests_dir_skips_pytest(self, output_dir, tracker, mock_client):
        write_file(output_dir, "main.py", "# main\npass\n")
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        # tests_passed defaults to True when no tests exist
        assert result.tests_passed is True

    def test_passing_test_detected(self, output_dir, tracker, mock_client):
        write_file(output_dir, "src/__init__.py", "")
        write_file(output_dir, "src/calc.py", "def add(a, b): return a + b\n")
        write_file(
            output_dir, "tests/test_calc.py",
            "import sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))\n"
            "from calc import add\n"
            "def test_add(): assert add(2, 3) == 5\n"
        )
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        assert result.tests_passed is True

    def test_failing_test_detected(self, output_dir, tracker, mock_client):
        write_file(
            output_dir, "tests/test_fail.py",
            "def test_always_fails():\n    assert False, 'This test always fails'\n"
        )
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        assert result.tests_passed is False


class TestValidatorRepair:

    def test_repair_fixes_simple_syntax(self, output_dir, tracker):
        """MockLLMClient returns valid Python for repair → file should be marked repaired."""
        write_file(output_dir, "broken.py", "def oops(\n    bad syntax here\n")

        class FixingClient:
            def chat_single(self, *args, **kwargs):
                return "def oops():\n    pass\n", {
                    "prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70
                }

        v = Validator(FixingClient(), tracker, output_dir, max_repairs=1)
        result = v.validate()
        repaired = [fr for fr in result.syntax_failed if fr.repaired]
        assert len(repaired) == 1
        assert repaired[0].path == "broken.py"

    def test_max_repairs_respected(self, output_dir, tracker):
        """Client that always returns invalid code → max_repairs respected."""
        write_file(output_dir, "unfixable.py", "def (:\n    pass")

        class BadFixClient:
            def chat_single(self, *args, **kwargs):
                return "still broken (:\n", {
                    "prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15
                }

        v = Validator(BadFixClient(), tracker, output_dir, max_repairs=2)
        result = v.validate()
        failed = [fr for fr in result.syntax_failed if not fr.repaired]
        assert len(failed) == 1
        assert failed[0].repair_attempts == 2


class TestValidationResult:

    def test_all_syntax_ok_property(self, output_dir, tracker, mock_client):
        write_file(output_dir, "ok.py", "pass\n")
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        assert result.all_syntax_ok is True

    def test_summary_contains_counts(self, output_dir, tracker, mock_client):
        write_file(output_dir, "fine.py", "x = 1\n")
        v = Validator(mock_client, tracker, output_dir)
        result = v.validate()
        summary = result.summary()
        assert "Files checked" in summary
        assert "Syntax passed" in summary
