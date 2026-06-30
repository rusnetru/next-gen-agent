"""Procedural Memory Store (Phase 1.3) — skills auto-extracted from episodes.

Skills are rated by usage/success and can be combined into composite skills
(Hermes-inspired self-improvement: simple validated procedures become
building blocks for more complex ones).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Skill:
    name: str
    procedure: str
    uses: int = 0
    successes: int = 0
    failures: int = 0
    composed_of: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.uses == 0:
            return 0.0
        return self.successes / self.uses


class SkillStore:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def extract(self, name: str, procedure: str) -> Skill:
        skill = self._skills.get(name)
        if skill is None:
            skill = Skill(name=name, procedure=procedure)
            self._skills[name] = skill
        skill.uses += 1
        return skill

    def record_success(self, name: str) -> None:
        skill = self._skills.get(name)
        if skill is not None:
            skill.successes += 1

    def record_failure(self, name: str) -> None:
        skill = self._skills.get(name)
        if skill is not None:
            skill.failures += 1

    def all(self) -> dict[str, Skill]:
        return dict(self._skills)

    def best(self, top_k: int = 5) -> list[Skill]:
        ranked = sorted(self._skills.values(), key=lambda s: s.success_rate, reverse=True)
        return ranked[:top_k]

    def combine(self, name_a: str, name_b: str, new_name: str) -> Skill | None:
        """Compose two existing skills into a new composite skill."""
        skill_a = self._skills.get(name_a)
        skill_b = self._skills.get(name_b)
        if skill_a is None or skill_b is None:
            return None
        composite = Skill(
            name=new_name,
            procedure=f"{skill_a.procedure} -> {skill_b.procedure}",
            composed_of=[name_a, name_b],
        )
        self._skills[new_name] = composite
        return composite
