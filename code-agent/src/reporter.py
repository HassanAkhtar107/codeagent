"""
reporter.py  –  Phase 6 Reporter
Writes GENERATION_REPORT.md into the output directory.
Summarises: files created, syntax results, test results, tokens, cost.
"""
from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any


def write_report(
    output_root: Path,
    plan: dict,
    generated_files: list[str],
    validation_result: Any,   # ValidationResult
    cost_tracker: Any,        # CostTracker
    stopped_early: bool = False,
    stop_reason: str = "",
) -> str:
    """
    Write GENERATION_REPORT.md to output_root.
    Returns the report content as a string.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_name = plan.get("project_name", "Unknown Project")
    planned_files = [f["path"] for f in plan.get("files", [])]

    missing = [p for p in planned_files if p not in generated_files]
    extra = [p for p in generated_files if p not in planned_files]

    # Build syntax section
    if validation_result:
        syntax_ok_count = len(validation_result.syntax_passed)
        syntax_fail_count = len(validation_result.syntax_failed)
        repaired = [fr for fr in validation_result.syntax_failed if fr.repaired]
        still_broken = [fr for fr in validation_result.syntax_failed if not fr.repaired]
        tests_status = "✅ Passed" if validation_result.tests_passed else "❌ Failed / Skipped"
        test_output = validation_result.tests_output[:1500] if validation_result.tests_output else "N/A"
    else:
        syntax_ok_count = syntax_fail_count = 0
        repaired = still_broken = []
        tests_status = "Not run"
        test_output = "N/A"

    # Cost section
    cost_dict = cost_tracker.to_dict()
    total_tokens = cost_dict["total_tokens"]
    total_cost = cost_dict["estimated_cost_usd"]
    hard_budget = cost_dict["hard_budget_usd"]

    lines = [
        f"# Generation Report – {project_name}",
        f"\nGenerated at: {now}",
        "",
        "---",
        "",
        "## Status",
        f"- Early stop: {'Yes – ' + stop_reason if stopped_early else 'No (completed normally)'}",
        f"- Files planned  : {len(planned_files)}",
        f"- Files generated: {len(generated_files)}",
        f"- Files missing  : {len(missing)}",
        "",
        "## Files Generated",
        "",
    ]

    for f in generated_files:
        lines.append(f"- ✅ `{f}`")
    if missing:
        lines += ["", "## Files Not Generated (planned but missing)", ""]
        for f in missing:
            lines.append(f"- ❌ `{f}`")

    lines += [
        "",
        "## Syntax Validation",
        f"- Passed : {syntax_ok_count}",
        f"- Failed : {syntax_fail_count}",
    ]

    if repaired:
        lines.append("\n### Repaired Files")
        for fr in repaired:
            lines.append(f"- ✅ `{fr.path}` (repaired after {fr.repair_attempts} attempt(s))")

    if still_broken:
        lines.append("\n### Still Broken After Repair Attempts")
        for fr in still_broken:
            lines.append(f"- ❌ `{fr.path}`: {fr.error[:200]}")

    lines += [
        "",
        "## Test Results",
        f"- Status: {tests_status}",
        "",
        "```",
        test_output,
        "```",
        "",
        "## Token Usage & Cost",
        f"- Model              : {cost_dict['model']}",
        f"- Total prompt tokens: {cost_dict['total_prompt_tokens']:,}",
        f"- Total output tokens: {cost_dict['total_completion_tokens']:,}",
        f"- Total tokens       : {total_tokens:,}",
        f"- Estimated cost     : ${total_cost:.4f} USD",
        f"- Hard budget        : ${hard_budget:.2f} USD",
        "",
        "### Per-Step Breakdown",
        "",
        "| Step | Tokens | Cost (USD) |",
        "|------|--------|------------|",
    ]

    for rec in cost_dict.get("records", []):
        lines.append(
            f"| {rec['step']} | {rec['total_tokens']:,} | ${rec['cost_usd']:.4f} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Assumptions and Deviations",
        "",
        "The following assumptions were made during generation:",
        "",
        "1. The target application is a Python Tkinter desktop application.",
        "2. Web/server technology references (REST, Node.js, microservices, Kubernetes) "
        "were adapted to desktop-equivalent Python modules.",
        "3. Database references were adapted to a local SQLite or JSON file.",
        "4. Missing or empty sections in the architecture documents were handled gracefully.",
        "5. Contradictions between the architecture documents (e.g., microservices vs desktop game) "
        "were resolved in favour of the desktop design.",
        "",
        "_See the generated README.md for setup and run instructions._",
        "",
    ]

    report = "\n".join(lines)

    # Write to disk
    report_path = output_root / "GENERATION_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    return report
