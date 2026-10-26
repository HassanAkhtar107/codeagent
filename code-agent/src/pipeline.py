"""
pipeline.py  –  Top-level agent pipeline orchestrator
Connects parser → planner → generator → validator → reporter
Designed to run in a background thread.
"""
from __future__ import annotations

import threading
from pathlib import Path
from typing import Callable, Any

from agent.parser import ArchitectureDocParser, ArchitectureViewParser
from agent.planner import Planner
from agent.generator import Generator
from agent.validator import Validator
from cost_tracker import CostTracker
from llm_client import LLMClient
from reporter import write_report


class Pipeline:
    """
    Orchestrates the full code-generation pipeline.

    Parameters
    ----------
    api_key          : str
    model            : str
    doc_path         : Path
    view_path        : Path
    output_dir       : Path
    cache_dir        : Path | None
    hard_budget_usd  : float
    log_callback     : Callable[[str], None]
    cost_callback    : Callable[[str], None]  – called with live_status() string
    stop_event       : threading.Event
    llm_client       : optional pre-built client (for testing with mock)
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        doc_path: Path,
        view_path: Path,
        output_dir: Path,
        cache_dir: Path | None,
        hard_budget_usd: float,
        log_callback: Callable[[str], None],
        cost_callback: Callable[[str], None] | None = None,
        stop_event: threading.Event | None = None,
        llm_client=None,
    ) -> None:
        self._log = log_callback
        self._cost_cb = cost_callback or (lambda s: None)
        self._stop = stop_event or threading.Event()

        # Store paths directly
        self._doc_path: Path = doc_path
        self._view_path: Path = view_path
        self.output_dir: Path = output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        self.cost_tracker = CostTracker(model=model, hard_budget_usd=hard_budget_usd)

        if llm_client is not None:
            self._llm = llm_client
        else:
            self._llm = LLMClient(
                api_key=api_key,
                model=model,
                cache_dir=cache_dir,
                stop_event=self._stop,
                log_callback=self._log,
            )

    # ------------------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """
        Execute the pipeline end-to-end.
        Returns a summary dict with keys: success, report, error.
        """
        self._log("=" * 60)
        self._log("Code Agent – Starting pipeline")
        self._log("=" * 60)

        plan: dict = {}
        generated: list[str] = []
        validation_result = None
        stopped_early = False
        stop_reason = ""
        report = ""

        try:
            # ── Phase 1: Parse ─────────────────────────────────────────
            self._check_stop()
            self._log("\n── Phase 1: Parsing architecture documents …")
            doc_parser = ArchitectureDocParser(self._doc_path)
            doc_data = doc_parser.parse()
            self._log(
                f"   Doc parsed: {len(doc_data.get('components', []))} components, "
                f"{len(doc_data.get('requirements', []))} requirements."
            )

            view_parser = ArchitectureViewParser(self._view_path)
            view_data = view_parser.parse()
            self._log(
                f"   View parsed: {len(view_data.get('diagrams', []))} diagrams, "
                f"{len(view_data.get('all_classes', []))} classes."
            )

            # ── Phase 2: Plan ──────────────────────────────────────────
            self._check_stop()
            self._log("\n── Phase 2: Generating project plan …")
            planner = Planner(self._llm, self.cost_tracker, self._log)
            plan = planner.plan(doc_data, view_data)
            self._cost_cb(self.cost_tracker.live_status())
            self._log(f"   Plan ready: {len(plan.get('files', []))} files.")

            # ── Phase 3: Generate ──────────────────────────────────────
            self._check_stop()
            self._log("\n── Phase 3: Generating project files …")
            generator = Generator(
                llm_client=self._llm,
                cost_tracker=self.cost_tracker,
                output_root=self.output_dir,
                doc_data=doc_data,
                view_data=view_data,
                stop_event=self._stop,
                log_callback=self._log,
            )
            generated = generator.generate_all(plan)
            self._cost_cb(self.cost_tracker.live_status())

            if self._stop.is_set():
                stopped_early = True
                stop_reason = "User requested stop."
                self._log("\n   Generation stopped early by user.")
            elif self.cost_tracker.over_budget():
                stopped_early = True
                stop_reason = f"Hard budget ${self.cost_tracker.hard_budget_usd:.2f} exceeded."
                self._log(f"\n   Budget exceeded – stopping.")

            # ── Phase 4: Validate ──────────────────────────────────────
            if not stopped_early:
                self._check_stop()
                self._log("\n── Phase 4: Validating generated files …")
                validator = Validator(
                    llm_client=self._llm,
                    cost_tracker=self.cost_tracker,
                    output_root=self.output_dir,
                    log_callback=self._log,
                )
                validation_result = validator.validate()
                self._cost_cb(self.cost_tracker.live_status())
                self._log(validation_result.summary())

        except RuntimeError as e:
            if "stopped by user" in str(e).lower():
                stopped_early = True
                stop_reason = "User requested stop."
                self._log("\n[Pipeline] Stopped by user request.")
            else:
                self._log(f"\n[Pipeline] Runtime error: {e}")
                # Still write report for partial results
                report = self._write_final_report(
                    plan, generated, validation_result,
                    stopped_early=True, stop_reason=str(e)
                )
                return {"success": False, "error": str(e), "report": report}

        except Exception as e:
            self._log(f"\n[Pipeline] Fatal error: {e}")
            report = self._write_final_report(
                plan, generated, validation_result,
                stopped_early=True, stop_reason=str(e)
            )
            return {"success": False, "error": str(e), "report": report}

        # ── Phase 5: Report ────────────────────────────────────────────
        report = self._write_final_report(
            plan, generated, validation_result,
            stopped_early=stopped_early, stop_reason=stop_reason
        )

        self._log("\n" + self.cost_tracker.summary())
        self._log("\n" + "=" * 60)
        self._log("Code Agent – Pipeline complete.")
        self._log("=" * 60)

        return {
            "success": True,
            "error": "",
            "report": report,
            "stopped_early": stopped_early,
        }

    def _write_final_report(
        self,
        plan: dict,
        generated: list,
        validation_result,
        stopped_early: bool,
        stop_reason: str,
    ) -> str:
        self._log("\n── Phase 5: Writing generation report …")
        try:
            report = write_report(
                output_root=self.output_dir,
                plan=plan,
                generated_files=generated,
                validation_result=validation_result,
                cost_tracker=self.cost_tracker,
                stopped_early=stopped_early,
                stop_reason=stop_reason,
            )
            self._log(f"   Report: {self.output_dir / 'GENERATION_REPORT.md'}")
            return report
        except Exception as e:
            self._log(f"   Failed to write report: {e}")
            return ""

    def _check_stop(self) -> None:
        if self._stop.is_set():
            raise RuntimeError("Generation stopped by user.")


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def create_pipeline(
    api_key: str,
    model: str,
    doc_path,
    view_path,
    output_dir,
    cache_dir,
    hard_budget_usd: float,
    log_callback: Callable,
    cost_callback: Callable | None = None,
    stop_event: threading.Event | None = None,
    llm_client=None,
) -> Pipeline:
    """Factory that wires up a Pipeline with the correct paths."""
    return Pipeline(
        api_key=api_key,
        model=model,
        doc_path=Path(doc_path),
        view_path=Path(view_path),
        output_dir=Path(output_dir),
        cache_dir=Path(cache_dir) if cache_dir else None,
        hard_budget_usd=hard_budget_usd,
        log_callback=log_callback,
        cost_callback=cost_callback,
        stop_event=stop_event or threading.Event(),
        llm_client=llm_client,
    )
