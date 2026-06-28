"""Memory API v1 — unified facade over episodic store, semantic graph, and skill store.

Spec (docs/02_development_plan.md, section 1.4):
    memory.store(event, type="episodic", context={...})
    memory.retrieve(query, top_k=5, types=["episodic", "semantic"])
    memory.consolidate()        # episodic -> semantic
    memory.skill_extract(episode_id)  # auto-extract a skill
"""

from __future__ import annotations

from typing import Any, Literal

from src.memory.episodic import Episode, EpisodicMemory
from src.memory.semantic import SemanticGraph
from src.memory.skills import Skill, SkillStore

MemoryType = Literal["episodic", "semantic"]


class Memory:
    def __init__(self) -> None:
        self.episodic = EpisodicMemory()
        self.semantic = SemanticGraph()
        self.skills = SkillStore()

    def store(
        self,
        event: str,
        type: MemoryType = "episodic",
        context: dict[str, Any] | None = None,
    ) -> Episode:
        if type == "semantic":
            self.semantic.add_fact(event, context or {})
        return self.episodic.store(event, context)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        types: list[MemoryType] | None = None,
    ) -> dict[str, list[Any]]:
        types = types or ["episodic", "semantic"]
        result: dict[str, list[Any]] = {}
        if "episodic" in types:
            result["episodic"] = self.episodic.retrieve(query, top_k=top_k)
        if "semantic" in types:
            result["semantic"] = self.semantic.query(query, top_k=top_k)
        return result

    def consolidate(self) -> int:
        """Promote recurring episodic patterns into semantic facts. Returns count promoted."""
        promoted = 0
        seen: dict[str, int] = {}
        for episode in self.episodic.all():
            seen[episode.content] = seen.get(episode.content, 0) + 1
        for content, count in seen.items():
            if count >= 2 and not self.semantic.has_fact(content):
                self.semantic.add_fact(content, {"source": "consolidation", "frequency": count})
                promoted += 1
        return promoted

    def skill_extract(self, episode_index: int) -> Skill | None:
        episodes = self.episodic.all()
        if episode_index < 0 or episode_index >= len(episodes):
            return None
        episode = episodes[episode_index]
        plan = episode.context.get("plan")
        if not plan:
            return None
        return self.skills.extract(name=episode.content, procedure=plan)
