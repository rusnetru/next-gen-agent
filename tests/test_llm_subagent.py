from src.llm.subagent import LLMSubagent, LLMVerifier, build_llm_subagent_pool
from src.memory.api import Memory
from src.orchestrator.communication import SharedContext


class FakeLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def complete(self, system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
        self.calls.append((system_prompt, user_message))
        return self._responses.pop(0)


def test_llm_subagent_calls_client_and_sets_context():
    client = FakeLLMClient(["researched findings"])
    agent = LLMSubagent("researcher", client, context_key="research")
    context = SharedContext(task="investigate X")

    result = agent.act("investigate X", context)

    assert result == "researched findings"
    assert context.get("research") == "researched findings"
    assert client.calls[0][1] == "investigate X"


def test_llm_verifier_marks_pass():
    client = FakeLLMClient(["PASS"])
    verifier = LLMVerifier(client)
    context = SharedContext(task="t")
    context.set("execution_result", "done")

    result = verifier.act("t", context)

    assert context.get("verified") is True
    assert "ok" in result


def test_llm_verifier_marks_fail():
    client = FakeLLMClient(["FAIL - incomplete"])
    verifier = LLMVerifier(client)
    context = SharedContext(task="t")

    verifier.act("t", context)

    assert context.get("verified") is False


def test_build_llm_subagent_pool_has_all_roles():
    client = FakeLLMClient([])
    memory = Memory(db_path=":memory:")
    pool = build_llm_subagent_pool(client, memory)

    assert set(pool.keys()) == {"researcher", "executor", "verifier", "planner", "memory_curator"}
