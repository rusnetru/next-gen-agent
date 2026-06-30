"""LLM-backed subagents — replace the Phase 2 deterministic stubs with real
model calls while keeping the exact same `Subagent.act(task, context) -> str`
contract, so `Orchestrator` needs zero changes to use them.
"""

from __future__ import annotations

from src.llm.client import LLMClient
from src.memory.api import Memory
from src.orchestrator.communication import SharedContext
from src.orchestrator.subagents import MemoryCurator, Planner, Subagent

_SYSTEM_PROMPTS = {
    "researcher": (
        "You are the Researcher subagent in a multi-agent system. Investigate the "
        "given task and report concise, factual findings. Be brief."
    ),
    "executor": (
        "You are the Executor subagent in a multi-agent system. Carry out the given "
        "task and report what was done, as if it were executed. Be brief."
    ),
}


class LLMSubagent(Subagent):
    """Generic LLM-driven subagent for a given role/context_key/system prompt."""

    def __init__(self, role: str, client: LLMClient, context_key: str) -> None:
        self.role = role
        self.client = client
        self.context_key = context_key

    def act(self, task: str, context: SharedContext) -> str:
        system_prompt = _SYSTEM_PROMPTS.get(self.role, f"You are the {self.role} subagent.")
        result = self.client.complete(system_prompt, task)
        context.set(self.context_key, result)
        return result


class LLMVerifier(Subagent):
    """LLM-driven Verifier: judges whether prior subagent output satisfies the task."""

    role = "verifier"

    _SYSTEM_PROMPT = (
        "You are the Verifier subagent. You are given the original task and what "
        "other subagents produced. Reply with exactly one word: PASS if the work "
        "satisfies the task, or FAIL otherwise."
    )

    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def act(self, task: str, context: SharedContext) -> str:
        evidence = "\n".join(context.history()) or "(no prior output)"
        user_message = f"Task: {task}\n\nWork so far:\n{evidence}"
        verdict = self.client.complete(self._SYSTEM_PROMPT, user_message)
        passed = "PASS" in verdict.upper()
        context.set("verified", passed)
        return f"verified: {'ok' if passed else 'failed'} ({verdict.strip()})"


def build_llm_subagent_pool(client: LLMClient, memory: Memory) -> dict[str, Subagent]:
    """Researcher/Executor/Verifier go through the LLM; Planner/MemoryCurator stay
    deterministic — decomposition and memory bookkeeping don't need a model call.
    """
    return {
        "researcher": LLMSubagent("researcher", client, context_key="research"),
        "executor": LLMSubagent("executor", client, context_key="execution_result"),
        "verifier": LLMVerifier(client),
        "planner": Planner(),
        "memory_curator": MemoryCurator(memory),
    }
