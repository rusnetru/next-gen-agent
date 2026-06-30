from src.evolution.strategy_adaptation import StrategyAdapter


def test_select_falls_back_to_first_strategy_without_history():
    adapter = StrategyAdapter(["react", "mcts"])
    assert adapter.select("new_task_class") == "react"


def test_observe_shifts_selection_toward_successful_strategy():
    adapter = StrategyAdapter(["react", "mcts"])
    adapter.observe("coding_task", "mcts", True)
    adapter.observe("coding_task", "mcts", True)
    adapter.observe("coding_task", "react", False)

    assert adapter.select("coding_task") == "mcts"


def test_observe_rejects_unknown_strategy():
    adapter = StrategyAdapter(["react"])
    try:
        adapter.observe("task", "unknown", True)
        assert False, "expected ValueError"
    except ValueError:
        pass
