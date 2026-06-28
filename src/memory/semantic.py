"""Semantic memory — graph of consolidated facts. Phase 0 stub backed by NetworkX."""

from __future__ import annotations

from typing import Any

import networkx as nx


class SemanticGraph:
    def __init__(self) -> None:
        self._graph = nx.DiGraph()

    def add_fact(self, fact: str, metadata: dict[str, Any] | None = None) -> None:
        self._graph.add_node(fact, **(metadata or {}))

    def has_fact(self, fact: str) -> bool:
        return self._graph.has_node(fact)

    def query(self, query: str, top_k: int = 5) -> list[str]:
        matches = [n for n in self._graph.nodes if query.lower() in n.lower()]
        return matches[:top_k]

    def link(self, fact_a: str, fact_b: str, relation: str) -> None:
        self._graph.add_edge(fact_a, fact_b, relation=relation)
