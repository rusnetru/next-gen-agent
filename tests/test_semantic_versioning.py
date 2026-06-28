from src.memory.semantic import SemanticGraph


def test_update_fact_supersedes_without_deleting_old():
    graph = SemanticGraph()
    graph.add_fact("user prefers tea")
    graph.update_fact("user prefers tea", "user prefers coffee")

    assert graph.has_fact("user prefers tea")
    assert graph.has_fact("user prefers coffee")
    assert graph.history("user prefers coffee") == ["user prefers coffee", "user prefers tea"]
