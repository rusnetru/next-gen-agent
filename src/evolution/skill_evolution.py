"""Skill Evolution Engine (Phase 4.1).

Builds on the Phase 1 procedural memory primitives (`Memory.skill_extract`,
`SkillStore.combine`) to automate the loop: scan successful episodes ->
extract skills -> rank by usage/success -> auto-combine skills that
repeatedly succeed back-to-back into a composite skill.
"""

from __future__ import annotations

from src.memory.api import Memory
from src.memory.skills import Skill


class SkillEvolutionEngine:
    def __init__(self, memory: Memory) -> None:
        self.memory = memory

    def extract_from_successful_episodes(self) -> list[Skill]:
        """Auto-create skills from episodes whose context marks them successful."""
        extracted: list[Skill] = []
        for index, episode in enumerate(self.memory.episodic.all()):
            if not episode.context.get("success"):
                continue
            skill = self.memory.skill_extract(index)
            if skill is not None:
                self.memory.skills.record_success(skill.name)
                extracted.append(skill)
        return extracted

    def rank(self, top_k: int = 5) -> list[Skill]:
        """Skills ranked by success rate, then by usage as a tiebreaker."""
        ranked = self.memory.skills.best(top_k=len(self.memory.skills.all()) or 1)
        ranked.sort(key=lambda s: (s.success_rate, s.uses), reverse=True)
        return ranked[:top_k]

    def auto_combine_sequential_pairs(self, min_co_occurrences: int = 2) -> list[Skill]:
        """Find skill name pairs that appear in adjacent successful episodes at
        least `min_co_occurrences` times and combine them into composite skills.
        """
        known_skills = self.memory.skills.all()
        names_in_order = [
            episode.content
            for episode in self.memory.episodic.all()
            if episode.context.get("success") and episode.content in known_skills
        ]
        pair_counts: dict[tuple[str, str], int] = {}
        for a, b in zip(names_in_order, names_in_order[1:]):
            if a == b:
                continue
            pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1

        combined: list[Skill] = []
        for (a, b), count in pair_counts.items():
            if count >= min_co_occurrences:
                composite_name = f"{a}+{b}"
                if composite_name in known_skills:
                    continue
                composite = self.memory.skills.combine(a, b, composite_name)
                if composite is not None:
                    combined.append(composite)
        return combined
