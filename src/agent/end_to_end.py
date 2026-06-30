"""End-to-end agent (Phase 6 — sequential integration).

Wires together pieces that, until now, only existed as independent tested
modules: Orchestrator (Phase 2) executes the task through a subagent team
(optionally LLM-backed, Phase 6), wrapped in the Phase 3 inner self-correction
loop (retry on failed verification) and Phase 4 strategy adaptation (which
execution pattern to try, learned per task class). Goal Stack and Tracer
record what happened for observability (Phase 5).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.evolution.strategy_adaptation import StrategyAdapter
from src.goals.goal_stack import GoalStack
from src.llm.client import LLMClient
from src.llm.subagent import build_llm_subagent_pool
from src.loops.self_correction import inner_loop
from src.memory.api import Memory
from src.observability.tracer import Tracer
from src.orchestrator.orchestrator import Orchestrator

EXECUTION_PATTERNS = ["sequential", "parallel", "hierarchical"]


@dataclass
class EndToEndResult:
    task: str
    succeeded: bool
    strategy: str
    attempts: int
    orchestration: dict


class EndToEndAgent:
    def __init__(
        self,
        memory: Memory | None = None,
        use_llm: bool = False,
        llm_client: LLMClient | None = None,
    ) -> None:
        self.memory = memory or Memory(db_path=":memory:")
        self.goals = GoalStack()
        self.tracer = Tracer()
        self.strategy_adapter = StrategyAdapter(EXECUTION_PATTERNS)
        self.orchestrator = Orchestrator(memory=self.memory)

        if use_llm:
            client = llm_client or LLMClient()
            for role, agent in build_llm_subagent_pool(client, self.memory).items():
                self.orchestrator.register(role, agent)

    def run(self, task: str, task_class: str = "default", max_retries: int = 2) -> EndToEndResult:
        goal = self.goals.push(task, horizon="task")
        self.tracer.record("end_to_end", "goal_pushed", {"task": task})

        strategy = self.strategy_adapter.select(task_class)
        self.tracer.record("end_to_end", "strategy_selected", {"task_class": task_class, "strategy": strategy})

        last_orchestration: dict = {}

        def attempt(attempt_number: int) -> dict:
            nonlocal last_orchestration
            last_orchestration = self.orchestrator.run(task, pattern=strategy)
            self.tracer.record(
                "orchestrator", "attempt", {"attempt": attempt_number, "verified": last_orchestration["verified"]}
            )
            return last_orchestration

        def verify(orchestration: dict) -> bool:
            return bool(orchestration["verified"])

        outcome = inner_loop(act=attempt, verify=verify, max_retries=max_retries)

        self.strategy_adapter.observe(task_class, strategy, outcome.succeeded)
        self.goals.revise(goal, active=False)
        self.tracer.record(
            "end_to_end", "completed", {"task": task, "succeeded": outcome.succeeded, "attempts": outcome.attempts}
        )

        return EndToEndResult(
            task=task,
            succeeded=outcome.succeeded,
            strategy=strategy,
            attempts=outcome.attempts,
            orchestration=last_orchestration,
        )
