"""
tests/test_pipeline.py
Integration test for the full pipeline using MockLLMClient.
No API calls are made.
"""
import sys
import threading
from pathlib import Path
import pytest

_SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(_SRC))

from pipeline import create_pipeline
from llm_client import MockLLMClient

SAMPLES = Path(__file__).parent.parent / "samples"


@pytest.fixture
def sample_files():
    """Return paths only if sample files exist."""
    doc = SAMPLES / "Architecture_Documentation.md"
    view = SAMPLES / "Architecture_View.md"
    if not doc.exists() or not view.exists():
        pytest.skip("Sample files not available")
    return doc, view


class TestPipelineWithMock:

    def test_full_run_succeeds(self, tmp_path, sample_files):
        doc, view = sample_files
        output = tmp_path / "generated"
        logs = []
        stop = threading.Event()

        pipeline = create_pipeline(
            api_key="mock-key",
            model="deepseek-chat",
            doc_path=doc,
            view_path=view,
            output_dir=output,
            cache_dir=None,
            hard_budget_usd=1.0,
            log_callback=lambda msg: logs.append(msg),
            stop_event=stop,
            llm_client=MockLLMClient(),
        )

        result = pipeline.run()
        assert result.get("success") is True

    def test_report_written(self, tmp_path, sample_files):
        doc, view = sample_files
        output = tmp_path / "generated"
        stop = threading.Event()

        pipeline = create_pipeline(
            api_key="mock-key",
            model="deepseek-chat",
            doc_path=doc,
            view_path=view,
            output_dir=output,
            cache_dir=None,
            hard_budget_usd=1.0,
            log_callback=lambda msg: None,
            stop_event=stop,
            llm_client=MockLLMClient(),
        )
        pipeline.run()
        report = output / "GENERATION_REPORT.md"
        assert report.exists(), "GENERATION_REPORT.md was not written"

    def test_stop_event_halts_generation(self, tmp_path, sample_files):
        doc, view = sample_files
        output = tmp_path / "generated"
        stop = threading.Event()
        stop.set()  # Pre-set stop

        pipeline = create_pipeline(
            api_key="mock-key",
            model="deepseek-chat",
            doc_path=doc,
            view_path=view,
            output_dir=output,
            cache_dir=None,
            hard_budget_usd=1.0,
            log_callback=lambda msg: None,
            stop_event=stop,
            llm_client=MockLLMClient(),
        )
        result = pipeline.run()
        # Should not crash even when stopped immediately
        assert "success" in result or "error" in result

    def test_cost_tracked(self, tmp_path, sample_files):
        doc, view = sample_files
        output = tmp_path / "generated"
        stop = threading.Event()

        pipeline = create_pipeline(
            api_key="mock-key",
            model="deepseek-chat",
            doc_path=doc,
            view_path=view,
            output_dir=output,
            cache_dir=None,
            hard_budget_usd=1.0,
            log_callback=lambda msg: None,
            stop_event=stop,
            llm_client=MockLLMClient(),
        )
        pipeline.run()
        assert pipeline.cost_tracker.total_tokens > 0
