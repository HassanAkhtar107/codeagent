"""
cost_tracker.py
Tracks token usage and estimated cost for a generation run.

DeepSeek pricing (as of 2025 – update MODEL_PRICES as needed):
  deepseek-chat (V3):  $0.27/1M input,  $1.10/1M output
  deepseek-reasoner:   $0.55/1M input,  $2.19/1M output

Reference: https://platform.deepseek.com/api-docs/pricing
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from threading import RLock   # RLock = reentrant; safe for nested acquire


# Price per 1 million tokens (USD)
MODEL_PRICES: dict[str, dict[str, float]] = {
    "deepseek-chat":     {"input": 0.27,  "output": 1.10},
    "deepseek-v3":       {"input": 0.27,  "output": 1.10},
    "deepseek-coder":    {"input": 0.27,  "output": 1.10},
    "deepseek-reasoner": {"input": 0.55,  "output": 2.19},
    "_default":          {"input": 0.27,  "output": 1.10},
}

DEFAULT_HARD_BUDGET_USD = 0.80


@dataclass
class CostRecord:
    step: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float


class CostTracker:
    """
    Thread-safe token / cost accumulator.

    Uses RLock (re-entrant lock) so methods that call each other
    (e.g. summary → remaining_budget) never deadlock.

    Usage
    -----
    tracker = CostTracker(model="deepseek-chat", hard_budget_usd=0.80)
    tracker.add("planner", usage_dict)
    print(tracker.summary())
    """

    def __init__(
        self,
        model: str = "deepseek-chat",
        hard_budget_usd: float = DEFAULT_HARD_BUDGET_USD,
    ) -> None:
        self.model = model
        self.hard_budget_usd = hard_budget_usd
        self._prices = MODEL_PRICES.get(model, MODEL_PRICES["_default"])
        self._lock = RLock()                # re-entrant: safe for nested calls

        # Accumulators
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.records: list[CostRecord] = []

    # ------------------------------------------------------------------

    def add(self, step: str, usage: dict[str, int]) -> None:
        """Register token usage from one LLM call."""
        pt = usage.get("prompt_tokens", 0)
        ct = usage.get("completion_tokens", 0)
        tt = usage.get("total_tokens", pt + ct)
        cost = self._calc_cost(pt, ct)

        rec = CostRecord(
            step=step,
            prompt_tokens=pt,
            completion_tokens=ct,
            total_tokens=tt,
            cost_usd=cost,
        )

        with self._lock:
            self.total_prompt_tokens += pt
            self.total_completion_tokens += ct
            self.total_tokens += tt
            self.total_cost_usd += cost
            self.records.append(rec)

    def over_budget(self) -> bool:
        """Return True if accumulated cost exceeds hard_budget_usd."""
        with self._lock:
            return self.total_cost_usd >= self.hard_budget_usd

    def remaining_budget(self) -> float:
        """Return remaining USD budget."""
        with self._lock:
            return max(0.0, self.hard_budget_usd - self.total_cost_usd)

    def summary(self) -> str:
        """Return a human-readable summary string."""
        with self._lock:
            # Inline remaining budget calc — no nested lock issue with RLock
            remaining = max(0.0, self.hard_budget_usd - self.total_cost_usd)
            lines = [
                "=== Cost & Token Summary ===",
                f"  Model            : {self.model}",
                f"  Prompt tokens    : {self.total_prompt_tokens:,}",
                f"  Completion tokens: {self.total_completion_tokens:,}",
                f"  Total tokens     : {self.total_tokens:,}",
                f"  Estimated cost   : ${self.total_cost_usd:.4f} USD",
                f"  Hard budget      : ${self.hard_budget_usd:.2f} USD",
                f"  Remaining budget : ${remaining:.4f} USD",
            ]
            if self.records:
                lines.append("\n  Step breakdown:")
                for r in self.records:
                    lines.append(
                        f"    [{r.step}] {r.total_tokens:>6} tokens  ${r.cost_usd:.4f}"
                    )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Serialisable representation for the GENERATION_REPORT."""
        with self._lock:
            return {
                "model": self.model,
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_tokens,
                "estimated_cost_usd": round(self.total_cost_usd, 6),
                "hard_budget_usd": self.hard_budget_usd,
                "records": [asdict(r) for r in self.records],
            }

    def live_status(self) -> str:
        """Short one-liner for the GUI status bar."""
        with self._lock:
            remaining = max(0.0, self.hard_budget_usd - self.total_cost_usd)
            return (
                f"Tokens: {self.total_tokens:,}  |  "
                f"Cost: ${self.total_cost_usd:.4f}  |  "
                f"Budget remaining: ${remaining:.4f}"
            )

    # ------------------------------------------------------------------

    def _calc_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price = self._prices["input"] / 1_000_000
        output_price = self._prices["output"] / 1_000_000
        return prompt_tokens * input_price + completion_tokens * output_price
