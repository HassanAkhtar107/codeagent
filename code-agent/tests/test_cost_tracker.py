"""
tests/test_cost_tracker.py
Unit tests for the CostTracker module.
"""
import sys
from pathlib import Path
import pytest

_SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_SRC))

from cost_tracker import CostTracker, DEFAULT_HARD_BUDGET_USD


class TestCostTracker:

    def test_initial_state(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=0.80)
        assert ct.total_tokens == 0
        assert ct.total_cost_usd == 0.0
        assert not ct.over_budget()

    def test_add_usage(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=1.0)
        ct.add("step1", {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300})
        assert ct.total_prompt_tokens == 100
        assert ct.total_completion_tokens == 200
        assert ct.total_tokens == 300
        assert ct.total_cost_usd > 0

    def test_multiple_adds_accumulate(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=1.0)
        ct.add("s1", {"prompt_tokens": 100, "completion_tokens": 100, "total_tokens": 200})
        ct.add("s2", {"prompt_tokens": 200, "completion_tokens": 200, "total_tokens": 400})
        assert ct.total_tokens == 600
        assert len(ct.records) == 2

    def test_over_budget_false_initially(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=0.80)
        ct.add("s1", {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20})
        assert not ct.over_budget()

    def test_over_budget_triggers(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=0.000001)
        ct.add("s1", {"prompt_tokens": 10000, "completion_tokens": 10000, "total_tokens": 20000})
        assert ct.over_budget()

    def test_remaining_budget(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=1.0)
        assert ct.remaining_budget() == pytest.approx(1.0)
        ct.add("s1", {"prompt_tokens": 1000, "completion_tokens": 1000, "total_tokens": 2000})
        assert ct.remaining_budget() < 1.0

    def test_summary_contains_keywords(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=0.80)
        ct.add("plan", {"prompt_tokens": 500, "completion_tokens": 300, "total_tokens": 800})
        s = ct.summary()
        assert "Estimated cost" in s
        assert "Total tokens" in s
        assert "plan" in s

    def test_to_dict(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=0.80)
        ct.add("gen", {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150})
        d = ct.to_dict()
        assert d["model"] == "deepseek-chat"
        assert d["total_tokens"] == 150
        assert "estimated_cost_usd" in d
        assert len(d["records"]) == 1

    def test_live_status_string(self):
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=0.80)
        status = ct.live_status()
        assert "Tokens:" in status
        assert "Cost:" in status

    def test_thread_safety(self):
        """Rudimentary thread-safety check."""
        import threading
        ct = CostTracker(model="deepseek-chat", hard_budget_usd=100.0)
        errors = []

        def add_tokens():
            try:
                for _ in range(10):
                    ct.add("thread", {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15})
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_tokens) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert ct.total_tokens == 5 * 10 * 15
