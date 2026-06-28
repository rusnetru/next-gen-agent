"""Lightweight vector index for hybrid retrieval (Phase 1.1).

Uses a deterministic hashed bag-of-words embedding so retrieval works fully
offline/deterministically in tests. Swap-in point for a real embedding model
(e.g. ChromaDB's default sentence-transformer) is `embed()` — production
deployments (Fase 5) should replace this with `chromadb`'s embedding function
without changing the `VectorIndex` interface.
"""

from __future__ import annotations

import math
import re
from collections import Counter

_DIM = 256
_TOKEN_RE = re.compile(r"[a-zA-Zа-яА-Я0-9]+")


def embed(text: str) -> list[float]:
    vector = [0.0] * _DIM
    tokens = _TOKEN_RE.findall(text.lower())
    counts = Counter(tokens)
    for token, count in counts.items():
        vector[hash(token) % _DIM] += count
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class VectorIndex:
    """In-memory vector index keyed by an opaque id."""

    def __init__(self) -> None:
        self._vectors: dict[int, list[float]] = {}

    def add(self, item_id: int, text: str) -> None:
        self._vectors[item_id] = embed(text)

    def remove(self, item_id: int) -> None:
        self._vectors.pop(item_id, None)

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        query_vec = embed(query)
        scored = [(item_id, cosine_similarity(query_vec, vec)) for item_id, vec in self._vectors.items()]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [pair for pair in scored if pair[1] > 0][:top_k]
