"""Working memory — bounded context window (Phase 0.3)."""

from __future__ import annotations

from collections import deque


class WorkingMemory:
    """Holds the most recent N items in scope for the current context window.

    Eviction is FIFO once `capacity` is exceeded, mirroring how a bounded
    LLM context window drops the oldest turns first.
    """

    def __init__(self, capacity: int = 20) -> None:
        self.capacity = capacity
        self._items: deque[str] = deque(maxlen=capacity)

    def add(self, item: str) -> None:
        self._items.append(item)

    def as_list(self) -> list[str]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
