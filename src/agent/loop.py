"""Phase 0 agent loop: perceive -> retrieve -> plan -> act -> observe -> store."""

from __future__ import annotations

from pathlib import Path

from src.memory.api import Memory


class Agent:
    def __init__(self, db_path: str | Path = "memory.db") -> None:
        self.memory = Memory(db_path=db_path)

    def step(self, perception: str) -> str:
        related = self.memory.retrieve(perception)["episodic"]
        plan = self._plan(perception, related)
        result = self._act(plan)
        self.memory.store(perception, type="episodic", context={"plan": plan, "result": result})
        return result

    def _plan(self, perception: str, related: list) -> str:
        return f"respond to: {perception}"

    def _act(self, plan: str) -> str:
        return f"[stub action] {plan}"
