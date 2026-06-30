"""Strategy Adaptation (Phase 4.2).

Wraps Phase 3's `StrategyRegistry` to expose adaptation as a configuration
choice, never a code rewrite: `select()` returns which registered strategy
name to use for a task class, `observe()` feeds the outcome back. The agent
never patches its own source — only the strategy *selection* adapts
(distinguishing this from self-rewriting approaches like Hyperagents).
"""

from __future__ import annotations

from src.planning.engine import StrategyRegistry


class StrategyAdapter:
    def __init__(self, available_strategies: list[str], registry: StrategyRegistry | None = None) -> None:
        if not available_strategies:
            raise ValueError("available_strategies must be non-empty")
        self.available_strategies = available_strategies
        self.registry = registry or StrategyRegistry()

    def select(self, task_class: str) -> str:
        return self.registry.best_strategy(task_class, self.available_strategies)

    def observe(self, task_class: str, strategy: str, success: bool) -> None:
        if strategy not in self.available_strategies:
            raise ValueError(f"unknown strategy: {strategy}")
        self.registry.record(task_class, strategy, success)
