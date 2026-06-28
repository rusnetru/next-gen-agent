"""Procedural memory — skills auto-extracted from successful episodes. Phase 0 stub."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Skill:
    name: str
    procedure: str
    uses: int = 0
    successes: int = 0


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

    def best(self, top_k: int = 5) -> list[Skill]:
        ranked = sorted(self._skills.values(), key=lambda s: s.successes, reverse=True)
        return ranked[:top_k]
