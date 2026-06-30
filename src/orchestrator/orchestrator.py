"""Orchestrator Agent (Phase 2.1 / 2.3): decomposition, dynamic team selection,
sequential/parallel/hierarchical execution, result assembly + verification.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from src.memory.api import Memory
from src.orchestrator.communication import SharedContext
from src.orchestrator.subagents import Executor, MemoryCurator, Planner, Researcher, Subagent, Verifier

Pattern = Literal["sequential", "parallel", "hierarchical"]

_ROUTING_KEYWORDS: dict[str, tuple[str, ...]] = {
    "researcher": ("research", "find", "investigate", "search"),
    "verifier": ("verify", "check", "validate"),
}


class Orchestrator:
    """Builds an ad-hoc subagent team per task instead of a fixed pipeline.

    The agent pool is a registry (`self.pool`), so callers can add/remove
    subagent types at runtime (`register`/`unregister`) — topology is not
    fixed at construction time.
    """

    def __init__(self, memory: Memory | None = None) -> None:
        self.memory = memory or Memory(db_path=":memory:")
        self.pool: dict[str, Subagent] = {
            "researcher": Researcher(),
            "executor": Executor(),
            "verifier": Verifier(),
            "planner": Planner(),
            "memory_curator": MemoryCurator(self.memory),
        }

    def register(self, role: str, agent: Subagent) -> None:
        self.pool[role] = agent

    def unregister(self, role: str) -> None:
        self.pool.pop(role, None)

    def decompose(self, task: str) -> list[str]:
        planner: Planner = self.pool["planner"]  # type: ignore[assignment]
        return planner.decompose(task)

    def route(self, subtask: str) -> str:
        """Dynamic topology: pick the agent role best suited to a subtask."""
        lowered = subtask.lower()
        for role, keywords in _ROUTING_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return role
        return "executor"

    def run(self, task: str, pattern: Pattern = "sequential") -> dict:
        context = SharedContext(task=task)
        subtasks = self.decompose(task)

        if pattern == "sequential":
            self._run_sequential(subtasks, context)
        elif pattern == "parallel":
            self._run_parallel(subtasks, context)
        elif pattern == "hierarchical":
            self._run_hierarchical(subtasks, context)
        else:
            raise ValueError(f"unknown execution pattern: {pattern}")

        verdict = self.pool["verifier"].act(task, context)
        context.post("verifier", verdict)
        curation = self.pool["memory_curator"].act(task, context)
        context.post("memory_curator", curation)

        return {
            "task": task,
            "subtasks": subtasks,
            "verified": context.get("verified", False),
            "transcript": context.history(),
        }

    def _run_sequential(self, subtasks: list[str], context: SharedContext) -> None:
        for subtask in subtasks:
            self._dispatch(subtask, context)

    def _run_parallel(self, subtasks: list[str], context: SharedContext) -> None:
        with ThreadPoolExecutor(max_workers=max(1, len(subtasks))) as pool:
            list(pool.map(lambda st: self._dispatch(st, context), subtasks))

    def _run_hierarchical(self, subtasks: list[str], context: SharedContext) -> None:
        for subtask in subtasks:
            nested = self.decompose(subtask)
            if len(nested) > 1:
                self._run_sequential(nested, context)
            else:
                self._dispatch(subtask, context)

    def _dispatch(self, subtask: str, context: SharedContext) -> None:
        role = self.route(subtask)
        agent = self.pool[role]
        result = agent.act(subtask, context)
        context.post(role, result)
