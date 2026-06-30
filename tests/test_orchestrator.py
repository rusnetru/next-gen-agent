from src.memory.api import Memory
from src.orchestrator.communication import SharedContext
from src.orchestrator.orchestrator import Orchestrator
from src.orchestrator.subagents import Executor, Planner, Researcher, Verifier


def make_orchestrator() -> Orchestrator:
    return Orchestrator(memory=Memory(db_path=":memory:"))


def test_decompose_splits_on_and():
    planner = Planner()
    assert planner.decompose("research topic A and execute task B") == [
        "research topic A",
        "execute task B",
    ]


def test_route_picks_researcher_for_research_keywords():
    orch = make_orchestrator()
    assert orch.route("research the competitor landscape") == "researcher"


def test_route_picks_verifier_for_verify_keywords():
    orch = make_orchestrator()
    assert orch.route("verify the deployment") == "verifier"


def test_route_defaults_to_executor():
    orch = make_orchestrator()
    assert orch.route("ship the release") == "executor"


def test_run_sequential_produces_verified_result():
    orch = make_orchestrator()
    result = orch.run("research market trends and execute the report", pattern="sequential")
    assert result["verified"] is True
    assert len(result["subtasks"]) == 2
    assert any("researcher" in line for line in result["transcript"])
    assert any("executor" in line for line in result["transcript"])


def test_run_parallel_executes_all_subtasks():
    orch = make_orchestrator()
    result = orch.run("research X and verify Y and execute Z", pattern="parallel")
    assert result["verified"] is True
    assert len(result["subtasks"]) == 3


def test_run_hierarchical_handles_nested_decomposition():
    orch = make_orchestrator()
    result = orch.run("plan the launch", pattern="hierarchical")
    assert result["verified"] is True


def test_unknown_pattern_raises():
    orch = make_orchestrator()
    try:
        orch.run("do something", pattern="bogus")  # type: ignore[arg-type]
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_dynamic_topology_register_and_unregister():
    orch = make_orchestrator()

    class Translator(Executor):
        role = "translator"

    orch.register("translator", Translator())
    assert "translator" in orch.pool

    orch.unregister("translator")
    assert "translator" not in orch.pool


def test_memory_curator_stores_episode_after_run():
    memory = Memory(db_path=":memory:")
    orch = Orchestrator(memory=memory)
    orch.run("execute the deploy script")
    episodes = memory.episodic.all()
    assert any("execute the deploy script" in e.content for e in episodes)


def test_shared_context_communication_layer():
    context = SharedContext(task="demo")
    context.post("researcher", "found something")
    context.set("key", "value")
    assert context.get("key") == "value"
    assert context.history() == ["researcher: found something"]
