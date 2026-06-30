"""Subagent Communication Layer (Phase 2.4).

A SharedContext is the team's shared working memory for one orchestration
run: subagents read/write keyed results and append to a transcript so later
agents (and the Verifier) can see what earlier agents produced. The same
shape doubles as the payload exchanged with external A2A-compatible peers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    sender: str
    content: str


@dataclass
class SharedContext:
    task: str
    data: dict[str, Any] = field(default_factory=dict)
    transcript: list[Message] = field(default_factory=list)

    def post(self, sender: str, content: str) -> None:
        self.transcript.append(Message(sender=sender, content=content))

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def history(self) -> list[str]:
        return [f"{m.sender}: {m.content}" for m in self.transcript]
