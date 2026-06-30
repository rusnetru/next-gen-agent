"""Team Composition Learning (Phase 4.3).

Tracks which combinations of subagent roles succeed for which task classes,
persisting the history as facts in the Phase 1 semantic graph so it survives
consolidation and is queryable alongside other long-term knowledge.
"""

from __future__ import annotations

from src.memory.semantic import SemanticGraph


def _team_fact(task_class: str, team: tuple[str, ...]) -> str:
    return f"team[{task_class}] = {'+'.join(sorted(team))}"


class TeamCompositionLearner:
    def __init__(self, semantic: SemanticGraph | None = None) -> None:
        self.semantic = semantic or SemanticGraph()
        self._history: dict[str, list[tuple[tuple[str, ...], bool]]] = {}

    def record(self, task_class: str, team: list[str], success: bool) -> None:
        key = tuple(sorted(team))
        self._history.setdefault(task_class, []).append((key, success))
        fact = _team_fact(task_class, key)
        if not self.semantic.has_fact(fact):
            self.semantic.add_fact(fact, {"task_class": task_class, "team": list(key), "uses": 0, "successes": 0})
        node = self.semantic._graph.nodes[fact]
        node["uses"] = node.get("uses", 0) + 1
        node["successes"] = node.get("successes", 0) + (1 if success else 0)

    def best_team(self, task_class: str) -> list[str] | None:
        """Highest success-rate team composition observed for this task class."""
        records = self._history.get(task_class, [])
        if not records:
            return None
        stats: dict[tuple[str, ...], list[int]] = {}
        for team, success in records:
            uses_successes = stats.setdefault(team, [0, 0])
            uses_successes[0] += 1
            uses_successes[1] += 1 if success else 0
        best_team = max(stats.items(), key=lambda kv: kv[1][1] / kv[1][0])
        return list(best_team[0])
