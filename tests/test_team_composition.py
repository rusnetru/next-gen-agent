from src.evolution.team_composition import TeamCompositionLearner


def test_best_team_returns_none_without_history():
    learner = TeamCompositionLearner()
    assert learner.best_team("unseen") is None


def test_best_team_picks_highest_success_rate_composition():
    learner = TeamCompositionLearner()
    learner.record("research_task", ["researcher", "verifier"], True)
    learner.record("research_task", ["researcher", "verifier"], True)
    learner.record("research_task", ["researcher", "executor"], False)

    assert learner.best_team("research_task") == ["researcher", "verifier"]


def test_record_persists_fact_in_semantic_graph():
    learner = TeamCompositionLearner()
    learner.record("research_task", ["researcher", "verifier"], True)

    assert learner.semantic.has_fact("team[research_task] = researcher+verifier")
